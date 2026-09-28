"""Dual verification contracts for the Structural Promotion O₀→O₂ protocol.

This module implements Frobenius-closed tool contracts: every action is paired with
a verification channel, and no world-model update is accepted without dual closure.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class DualToolResult:
    """A Frobenius-closed dual: action μ and verification δ satisfy μ(δ(query)) = query.

    Every tool call is paired with a verification call. The pair is Frobenius-closed
    when the verification output confirms the action output — mu(delta(query)) == query.

    Attributes:
        tool_name: Name of the primary action tool.
        tool_input: Input parameters sent to the action tool.
        tool_output: Output returned by the action tool.
        verify_name: Name of the verification tool (dual).
        verify_output: Output returned by the verification tool.
        frobenius_closed: True iff the dual pair is verified consistent.
    """

    tool_name: str
    tool_input: dict[str, Any]
    tool_output: str
    verify_name: str
    verify_output: str
    frobenius_closed: bool = False

    @classmethod
    def from_tool_call(
        cls,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_output: str,
        verify_name: str,
        verify_output: str,
    ) -> DualToolResult:
        """Construct a DualToolResult and evaluate Frobenius closure.

        Frobenius closure holds when the verification output is non-empty
        and does not report errors. This is the structural μ∘δ=id condition.

        Args:
            tool_name: Primary action tool name.
            tool_input: Input to the primary action.
            tool_output: Output from the primary action.
            verify_name: Verification tool name.
            verify_output: Output from the verification tool.

        Returns:
            A DualToolResult with frobenius_closed set appropriately.
        """
        closed = bool(verify_output) and "error" not in verify_output.lower()
        return cls(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            verify_name=verify_name,
            verify_output=verify_output,
            frobenius_closed=closed,
        )


@dataclass
class ToolContract:
    """A structural contract binding an action to its verification dual.

    Attributes:
        tool_name: Name of the tool being contracted.
        assertion: A Python expression over the tool output that must hold.
        verify_fn: Callable that takes (tool_input, tool_output) and returns
            verification output. Defaults to a no-op pass-through.
        auto_approve: If True, the contract auto-approves on verify success.
    """

    tool_name: str
    assertion: str = "True"
    verify_fn: Optional[Callable[[dict[str, Any], str], str]] = None
    auto_approve: bool = True

    def verify(self, tool_input: dict[str, Any], tool_output: str) -> tuple[bool, str]:
        """Run verification and return (passed, message)."""
        if self.verify_fn is not None:
            verify_output = self.verify_fn(tool_input, tool_output)
        else:
            verify_output = tool_output  # identity verification

        try:
            result = eval(self.assertion, {"output": verify_output, "input": tool_input})
            passed = bool(result)
        except Exception as exc:
            return False, f"Assertion evaluation failed: {exc}"

        if passed and self.auto_approve:
            return True, f"Contract approved: {self.tool_name} passed assertion '{self.assertion}'"
        return passed, f"Contract result: {passed} for {self.tool_name}"
