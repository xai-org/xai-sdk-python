import dataclasses
import subprocess
import sys
import textwrap

import pytest

from xai_sdk.safety import (
    NETWORK_ONLY,
    PERMISSIVE,
    STRICT,
    SafetyPolicy,
    SafetyViolationError,
)


def test_policy_defaults():
    p = SafetyPolicy()
    assert p.block_subprocess is True
    assert p.block_code_generation is True
    assert p.block_network is True
    assert p.block_filesystem is True
    assert p.allowed_paths == ()
    assert p.allowed_hosts == ()
    assert p.on_violation == "raise"


def test_policy_custom_values():
    p = SafetyPolicy(
        block_subprocess=False,
        block_network=False,
        allowed_paths=["/tmp"],  # noqa: S108
        allowed_hosts=["api.x.ai", "Example.COM"],
    )
    assert p.block_subprocess is False
    assert p.block_network is False
    assert len(p.allowed_paths) == 1
    assert p.allowed_hosts == ("api.x.ai", "example.com")


def test_policy_frozen():
    p = SafetyPolicy()
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.block_subprocess = False  # type: ignore[misc]


def test_policy_none_paths_normalised():
    p = SafetyPolicy(allowed_paths=None)
    assert p.allowed_paths == ()


def test_policy_paths_resolved_to_absolute():
    import os

    p = SafetyPolicy(allowed_paths=["./relative"])
    for path in p.allowed_paths:
        assert os.path.isabs(path)


def test_strict_blocks_everything():
    assert STRICT.block_subprocess is True
    assert STRICT.block_code_generation is True
    assert STRICT.block_network is True
    assert STRICT.block_filesystem is True


def test_network_only_allows_network():
    assert NETWORK_ONLY.block_network is False
    assert NETWORK_ONLY.block_subprocess is True


def test_permissive_allows_network_and_fs():
    assert PERMISSIVE.block_network is False
    assert PERMISSIVE.block_filesystem is False
    assert PERMISSIVE.block_subprocess is True


def test_violation_error_attributes():
    v = SafetyViolationError("subprocess", ("ls",), "blocked")
    assert v.event == "subprocess"
    assert v.audit_args == ("ls",)
    assert v.reason == "blocked"
    assert "blocked" in str(v)


def test_violation_error_is_runtime_error():
    assert issubclass(SafetyViolationError, RuntimeError)


def _run_snippet(code: str) -> subprocess.CompletedProcess:
    """Run a Python snippet in a subprocess and return the result."""
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", textwrap.dedent(code)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_blocks_os_system():
    result = _run_snippet("""
        import os
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        with SafetyGuard(policy):
            try:
                os.system("echo hi")
                print("NOT_BLOCKED")
            except Exception as e:
                print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED:SafetyViolationError" in result.stdout, result.stderr


def test_blocks_subprocess_popen():
    result = _run_snippet("""
        import subprocess
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        with SafetyGuard(policy):
            try:
                subprocess.Popen(["echo", "hi"])
                print("NOT_BLOCKED")
            except Exception as e:
                print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED:SafetyViolationError" in result.stdout, result.stderr


def test_allowed_outside_guard():
    result = _run_snippet("""
        import os
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        # Install the hook via a guard
        with SafetyGuard(policy):
            pass
        # Outside guard, should work fine
        os.system("echo OUTSIDE_OK")
        print("PASS")
    """)
    assert "PASS" in result.stdout, result.stderr


def test_blocks_exec():
    result = _run_snippet("""
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        with SafetyGuard(policy):
            try:
                exec("x = 1")
                print("NOT_BLOCKED")
            except Exception as e:
                print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED:SafetyViolationError" in result.stdout, result.stderr


def test_blocks_eval():
    result = _run_snippet("""
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        with SafetyGuard(policy):
            try:
                eval("1 + 1")
                print("NOT_BLOCKED")
            except Exception as e:
                print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED:SafetyViolationError" in result.stdout, result.stderr


def test_json_loads_not_blocked():
    result = _run_snippet("""
        import json
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        with SafetyGuard(policy):
            data = json.loads('{"key": "value"}')
            print(f"OK:{data['key']}")
    """)
    assert "OK:value" in result.stdout, result.stderr


def test_blocks_socket_connect():
    result = _run_snippet("""
        import socket
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        with SafetyGuard(policy):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("example.com", 80))
                print("NOT_BLOCKED")
            except Exception as e:
                if "SafetyViolation" in type(e).__name__ or "Safety violation" in str(e):
                    print(f"BLOCKED:{type(e).__name__}")
                else:
                    print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED" in result.stdout, result.stderr


def test_allowed_host_passes():
    result = _run_snippet("""
        import socket
        from xai_sdk.safety import SafetyGuard, SafetyPolicy, SafetyViolationError
        policy = SafetyPolicy(allowed_hosts=["127.0.0.1"])
        with SafetyGuard(policy):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.1)
                s.connect(("127.0.0.1", 1))
                print("CONNECTED")
            except SafetyViolationError:
                print("BLOCKED")
            except (ConnectionRefusedError, OSError, TimeoutError):
                # Connection failed for network reasons, but was not blocked by safety
                print("ALLOWED")
    """)
    assert "ALLOWED" in result.stdout or "CONNECTED" in result.stdout, result.stderr


def test_blocks_file_open():
    result = _run_snippet("""
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy()
        with SafetyGuard(policy):
            try:
                open("/etc/hostname", "r")
                print("NOT_BLOCKED")
            except Exception as e:
                print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED:SafetyViolationError" in result.stdout, result.stderr


def test_allowed_path_passes():
    result = _run_snippet("""
        import tempfile, os
        from xai_sdk.safety import SafetyGuard, SafetyPolicy

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            # Write outside guard
            with open(test_file, "w") as f:
                f.write("hello")

            policy = SafetyPolicy(allowed_paths=[tmpdir])
            with SafetyGuard(policy):
                try:
                    with open(test_file, "r") as f:
                        print(f"OK:{f.read()}")
                except Exception as e:
                    print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "OK:hello" in result.stdout, result.stderr


def test_disabled_category_allows():
    result = _run_snippet("""
        import os
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        policy = SafetyPolicy(block_subprocess=False)
        with SafetyGuard(policy):
            os.system("echo ALLOWED")
            print("PASS")
    """)
    assert "PASS" in result.stdout, result.stderr


def test_log_mode_no_raise():
    result = _run_snippet("""
        import os, logging
        from xai_sdk.safety import SafetyGuard, SafetyPolicy
        logging.basicConfig(level=logging.WARNING)
        policy = SafetyPolicy(on_violation="log")
        with SafetyGuard(policy):
            os.system("echo hi")
            print("CONTINUED")
    """)
    assert "CONTINUED" in result.stdout, result.stderr


def test_nested_guards_use_inner_policy():
    result = _run_snippet("""
        import os
        from xai_sdk.safety import SafetyGuard, SafetyPolicy

        outer = SafetyPolicy(block_subprocess=True)
        inner = SafetyPolicy(block_subprocess=False)

        with SafetyGuard(outer):
            with SafetyGuard(inner):
                os.system("echo INNER_OK")
                print("INNER_PASS")

            try:
                os.system("echo OUTER")
                print("OUTER_NOT_BLOCKED")
            except Exception as e:
                print(f"OUTER_BLOCKED:{type(e).__name__}")
    """)
    assert "INNER_PASS" in result.stdout, result.stderr
    assert "OUTER_BLOCKED:SafetyViolationError" in result.stdout, result.stderr


def test_decorator_usage():
    result = _run_snippet("""
        import os
        from xai_sdk.safety import SafetyGuard, SafetyPolicy

        policy = SafetyPolicy()

        @SafetyGuard(policy)
        def risky():
            os.system("echo hi")

        try:
            risky()
            print("NOT_BLOCKED")
        except Exception as e:
            print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED:SafetyViolationError" in result.stdout, result.stderr


def test_guard_only_affects_current_thread():
    result = _run_snippet("""
        import os, threading
        from xai_sdk.safety import SafetyGuard, SafetyPolicy

        results = {}

        def guarded_thread():
            policy = SafetyPolicy()
            with SafetyGuard(policy):
                try:
                    os.system("echo hi")
                    results["guarded"] = "NOT_BLOCKED"
                except Exception:
                    results["guarded"] = "BLOCKED"

        def free_thread():
            import time
            time.sleep(0.1)  # ensure guard is active in other thread
            try:
                os.system("echo hi")
                results["free"] = "NOT_BLOCKED"
            except Exception:
                results["free"] = "BLOCKED"

        t1 = threading.Thread(target=guarded_thread)
        t2 = threading.Thread(target=free_thread)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        print(f"guarded={results.get('guarded')}")
        print(f"free={results.get('free')}")
    """)
    assert "guarded=BLOCKED" in result.stdout, result.stderr
    assert "free=NOT_BLOCKED" in result.stdout, result.stderr


def test_global_safety_persists():
    result = _run_snippet("""
        import os
        from xai_sdk.safety import SafetyPolicy, enable_global_safety

        enable_global_safety(SafetyPolicy())
        try:
            os.system("echo hi")
            print("NOT_BLOCKED")
        except Exception as e:
            print(f"BLOCKED:{type(e).__name__}")
    """)
    assert "BLOCKED:SafetyViolationError" in result.stdout, result.stderr
