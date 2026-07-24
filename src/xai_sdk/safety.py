import functools
import os
import sys
import threading
import warnings
from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional, Sequence, TypeVar, Union

_MIN_ADDRESS_PARTS = 2

T = TypeVar("T")


class SafetyViolationError(RuntimeError):
    """Raised when a blocked operation is attempted inside a SafetyGuard."""

    def __init__(self, event: str, args: tuple, reason: str):
        """Initialize with the audit event name, its arguments, and a human-readable reason."""
        self.event = event
        self.audit_args = args
        self.reason = reason
        super().__init__(f"Safety violation: {reason} (audit event: {event})")


def _normalize_paths(paths: Union[Sequence[str], None]) -> tuple[str, ...]:
    if not paths:
        return ()
    return tuple(os.path.realpath(p) for p in paths)


def _normalize_hosts(hosts: Union[Sequence[str], None]) -> tuple[str, ...]:
    if not hosts:
        return ()
    return tuple(h.lower() for h in hosts)


@dataclass(frozen=True)
class SafetyPolicy:
    """Configuration for which operations to block inside a SafetyGuard.

    Args:
        block_subprocess: Block subprocess/process execution (subprocess.Popen,
            os.system, os.exec*, os.spawn, os.fork).
        block_code_generation: Block dynamic code generation (exec, compile).
        block_network: Block network connections (socket.connect, socket.getaddrinfo).
        block_filesystem: Block filesystem writes (open with write mode, os.rename,
            os.remove, os.mkdir, etc.). Read-only opens to allowed_paths are permitted.
        allowed_paths: Filesystem paths where operations are permitted when
            block_filesystem is True. Resolved to absolute paths.
        allowed_hosts: Network hosts where connections are permitted when
            block_network is True.
        on_violation: ``"raise"`` to throw SafetyViolationError, ``"log"`` to warn only.
    """

    block_subprocess: bool = True
    block_code_generation: bool = True
    block_network: bool = True
    block_filesystem: bool = True
    allowed_paths: tuple[str, ...] = ()
    allowed_hosts: tuple[str, ...] = ()
    on_violation: Literal["raise", "log"] = "raise"

    def __init__(
        self,
        *,
        block_subprocess: bool = True,
        block_code_generation: bool = True,
        block_network: bool = True,
        block_filesystem: bool = True,
        allowed_paths: Union[Sequence[str], None] = None,
        allowed_hosts: Union[Sequence[str], None] = None,
        on_violation: Literal["raise", "log"] = "raise",
    ):
        """Create a new safety policy with the given blocking rules and allowlists."""
        object.__setattr__(self, "block_subprocess", block_subprocess)
        object.__setattr__(self, "block_code_generation", block_code_generation)
        object.__setattr__(self, "block_network", block_network)
        object.__setattr__(self, "block_filesystem", block_filesystem)
        object.__setattr__(self, "allowed_paths", _normalize_paths(allowed_paths))
        object.__setattr__(self, "allowed_hosts", _normalize_hosts(allowed_hosts))
        object.__setattr__(self, "on_violation", on_violation)


class _AuditInterceptor:
    """Singleton that manages the PEP 578 audit hook and per-thread policy state."""

    _instance: Optional["_AuditInterceptor"] = None
    _install_lock = threading.Lock()

    def __init__(self) -> None:
        self._local = threading.local()
        self._handlers: dict[str, Callable[[SafetyPolicy, tuple], None]] = {
            "subprocess.Popen": self._check_subprocess,
            "os.system": self._check_subprocess,
            "os.exec": self._check_subprocess,
            "os.spawn": self._check_subprocess,
            "os.fork": self._check_subprocess,
            "os.kill": self._check_subprocess,
            "os.startfile": self._check_subprocess,
            "ctypes.dlopen": self._check_subprocess,
            "webbrowser.open": self._check_subprocess,
            "exec": self._check_code_gen,
            "compile": self._check_code_gen,
            "socket.connect": self._check_network,
            "socket.bind": self._check_network,
            "socket.sendmsg": self._check_network,
            "socket.sendto": self._check_network,
            "socket.getaddrinfo": self._check_network_addrinfo,
            "open": self._check_filesystem,
            "os.rename": self._check_filesystem_dual,
            "os.remove": self._check_filesystem_path,
            "os.unlink": self._check_filesystem_path,
            "os.mkdir": self._check_filesystem_path,
            "os.rmdir": self._check_filesystem_path,
            "os.truncate": self._check_filesystem_path,
            "os.chmod": self._check_filesystem_path,
            "os.chown": self._check_filesystem_path,
            "os.link": self._check_filesystem_dual,
            "os.symlink": self._check_filesystem_dual,
            "shutil.rmtree": self._check_filesystem_path,
            "shutil.copyfile": self._check_filesystem_dual,
        }

    @classmethod
    def get_instance(cls) -> "_AuditInterceptor":
        """Return the singleton interceptor, installing the audit hook on first call."""
        if cls._instance is None:
            with cls._install_lock:
                if cls._instance is None:
                    instance = cls()
                    sys.addaudithook(instance._hook)
                    cls._instance = instance
        return cls._instance

    def activate(self, policy: SafetyPolicy) -> None:
        """Push a policy onto this thread's enforcement stack."""
        if not hasattr(self._local, "policy_stack"):
            self._local.policy_stack = []
        self._local.policy_stack.append(policy)

    def deactivate(self) -> None:
        """Pop the most recent policy from this thread's enforcement stack."""
        stack = getattr(self._local, "policy_stack", None)
        if stack:
            stack.pop()

    @property
    def _active_policy(self) -> Optional[SafetyPolicy]:
        stack = getattr(self._local, "policy_stack", None)
        return stack[-1] if stack else None

    def _hook(self, event: str, args: tuple) -> None:
        policy = self._active_policy
        if policy is None:
            return
        handler = self._handlers.get(event)
        if handler is not None:
            handler(policy, args)

    def _raise_or_log(self, policy: SafetyPolicy, event: str, args: tuple, reason: str) -> None:
        violation = SafetyViolationError(event, args, reason)
        if policy.on_violation == "raise":
            raise violation
        warnings.warn(str(violation), UserWarning, stacklevel=4)

    def _check_subprocess(self, policy: SafetyPolicy, args: tuple) -> None:
        if policy.block_subprocess:
            self._raise_or_log(policy, "subprocess", args, "Process execution is blocked")

    def _check_code_gen(self, policy: SafetyPolicy, args: tuple) -> None:
        if policy.block_code_generation:
            self._raise_or_log(policy, "code_generation", args, "Dynamic code generation is blocked")

    def _check_network(self, policy: SafetyPolicy, args: tuple) -> None:
        if not policy.block_network:
            return
        host = self._extract_host_from_address(args)
        if host and policy.allowed_hosts and host.lower() in policy.allowed_hosts:
            return
        self._raise_or_log(policy, "network", args, f"Network connection blocked (host: {host!r})")

    def _check_network_addrinfo(self, policy: SafetyPolicy, args: tuple) -> None:
        if not policy.block_network:
            return
        host = args[0] if args else None
        if isinstance(host, str) and policy.allowed_hosts and host.lower() in policy.allowed_hosts:
            return
        self._raise_or_log(policy, "network", args, f"DNS resolution blocked (host: {host!r})")

    def _extract_host_from_address(self, args: tuple) -> Optional[str]:
        if len(args) < _MIN_ADDRESS_PARTS:
            return None
        address = args[1]
        if isinstance(address, tuple) and len(address) >= _MIN_ADDRESS_PARTS:
            return str(address[0])
        return None

    def _is_path_allowed(self, policy: SafetyPolicy, path: Any) -> bool:
        if not isinstance(path, str | bytes):
            return False
        if isinstance(path, bytes):
            path = os.fsdecode(path)
        real_path = os.path.realpath(path)
        for allowed in policy.allowed_paths:
            try:
                if os.path.commonpath([real_path, allowed]) == allowed:
                    return True
            except ValueError:
                continue
        return False

    def _check_filesystem(self, policy: SafetyPolicy, args: tuple) -> None:
        if not policy.block_filesystem:
            return
        if not args:
            return
        path = args[0]
        if not isinstance(path, str | bytes):
            return
        if policy.allowed_paths and self._is_path_allowed(policy, path):
            return
        self._raise_or_log(policy, "filesystem", args, f"File access blocked: {path!r}")

    def _check_filesystem_path(self, policy: SafetyPolicy, args: tuple) -> None:
        if not policy.block_filesystem:
            return
        if not args:
            return
        path = args[0]
        if policy.allowed_paths and self._is_path_allowed(policy, path):
            return
        self._raise_or_log(policy, "filesystem", args, f"Filesystem operation blocked: {path!r}")

    def _check_filesystem_dual(self, policy: SafetyPolicy, args: tuple) -> None:
        if not policy.block_filesystem:
            return
        src = args[0] if args else None
        dst = args[1] if len(args) > 1 else None
        if policy.allowed_paths:
            src_ok = src is not None and self._is_path_allowed(policy, src)
            dst_ok = dst is not None and self._is_path_allowed(policy, dst)
            if src_ok and dst_ok:
                return
        self._raise_or_log(policy, "filesystem", args, f"Filesystem operation blocked: {src!r} -> {dst!r}")


class SafetyGuard:
    """Context manager and decorator that enforces a SafetyPolicy via PEP 578 audit hooks.

    The audit hook is installed lazily on first use and persists for the process
    lifetime (per PEP 578). Enforcement is scoped to the current thread and
    active only while the guard is entered.

    Can be used as a context manager::

        with SafetyGuard(policy):
            # dangerous operations blocked here
            ...

    Or as a decorator::

        @SafetyGuard(policy)
        def handle_tool_calls(tool_calls):
            ...
    """

    def __init__(self, policy: SafetyPolicy):
        """Create a guard bound to the given policy."""
        self._policy = policy
        self._interceptor = _AuditInterceptor.get_instance()

    def __enter__(self) -> "SafetyGuard":
        """Activate enforcement for the current thread."""
        self._interceptor.activate(self._policy)
        return self

    def __exit__(self, *exc_info: Any) -> None:
        """Deactivate enforcement for the current thread."""
        self._interceptor.deactivate()

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Wrap *func* so it runs inside this guard."""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with self:
                return func(*args, **kwargs)

        return wrapper


def enable_global_safety(policy: SafetyPolicy) -> None:
    """Enable safety enforcement globally for the current thread.

    Unlike SafetyGuard, this activation is permanent for the thread — there is
    no corresponding disable. Use this for always-on protection.
    """
    interceptor = _AuditInterceptor.get_instance()
    interceptor.activate(policy)


STRICT = SafetyPolicy(
    block_subprocess=True,
    block_code_generation=True,
    block_network=True,
    block_filesystem=True,
)

NETWORK_ONLY = SafetyPolicy(
    block_subprocess=True,
    block_code_generation=True,
    block_network=False,
    block_filesystem=True,
)

PERMISSIVE = SafetyPolicy(
    block_subprocess=True,
    block_code_generation=True,
    block_network=False,
    block_filesystem=False,
)
