"""Monotonic agent trajectory tracking for Structural Promotion O₀→O₂.

An AgentTrajectory enforces monotonic winding — every cycle adds information,
never re-treads. The Frobenius ratio tracks structural health: what fraction
of action cycles are verified closed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

from .contracts import DualToolResult


@dataclass
class AgentCycle:
    """A single winding of the THINK→ACT→OBSERVE→UPDATE loop.

    Attributes:
        winding: Monotonically increasing cycle number (Ω_z invariant).
        timestamp: ISO-8601 timestamp of the cycle.
        action_name: The action tool invoked this cycle.
        action_input: Input parameters for the action.
        dual_result: The Frobenius-closed dual verification result.
        update_note: Observation / world-model update from this cycle.
        done: Whether this cycle terminated the agent (terminal action).
        conclusion: Final conclusion text, populated only if done=True.
        frobenius_closed: Shorthand for dual_result.frobenius_closed.
    """

    winding: int
    timestamp: str
    action_name: str
    action_input: dict[str, Any]
    dual_result: Optional[DualToolResult] = None
    update_note: str = ""
    done: bool = False
    conclusion: str = ""

    @property
    def frobenius_closed(self) -> bool:
        return self.dual_result is not None and self.dual_result.frobenius_closed


class AgentTrajectory:
    """A monotonic sequence of agent cycles (Ω_z topological protection).

    The trajectory enforces:
      - Monotonic winding numbers (no re-treading).
      - Frobenius ratio tracking (structural health metric).
      - Structural health score combining ratio and closure count.

    Attributes:
        cycles: List of completed agent cycles.
    """

    def __init__(self) -> None:
        self.cycles: list[AgentCycle] = []

    def add_cycle(
        self,
        action_name: str,
        action_input: dict[str, Any],
        dual_result: Optional[DualToolResult] = None,
        update_note: str = "",
        done: bool = False,
        conclusion: str = "",
    ) -> AgentCycle:
        """Add a new cycle, enforcing monotonic winding.

        Args:
            action_name: Name of the action tool called.
            action_input: Input to the action tool.
            dual_result: Frobenius-closed dual verification result.
            update_note: Observation / update note.
            done: Whether this is a terminal cycle.
            conclusion: Final conclusion if terminal.

        Returns:
            The newly created AgentCycle.

        Raises:
            ValueError: If the winding number would not be monotonic.
        """
        winding = len(self.cycles)
        if winding > 0 and self.cycles[-1].winding >= winding:
            raise ValueError(
                f"Monotonic winding violated: cycle {winding} follows "
                f"cycle {self.cycles[-1].winding}. Ω_z protection enforced."
            )

        cycle = AgentCycle(
            winding=winding,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            action_name=action_name,
            action_input=action_input,
            dual_result=dual_result,
            update_note=update_note,
            done=done,
            conclusion=conclusion,
        )
        self.cycles.append(cycle)
        return cycle

    @property
    def frobenius_ratio(self) -> float:
        """Fraction of cycles that were Frobenius-closed."""
        if not self.cycles:
            return 0.0
        closed = sum(1 for c in self.cycles if c.frobenius_closed)
        return closed / len(self.cycles)

    def structural_health(self) -> dict[str, Any]:
        """Compute structural health metrics.

        Returns:
            Dict with frobenius_ratio, total_cycles, closed_cycles,
            open_cycles, and a health_score (0.0-1.0).
        """
        total = len(self.cycles)
        closed = sum(1 for c in self.cycles if c.frobenius_closed)
        open_cycles = total - closed
        ratio = self.frobenius_ratio

        # Health score: Frobenius ratio weighted by completion status
        health_score = ratio * (1.0 - 0.1 * (open_cycles / max(total, 1)))

        return {
            "frobenius_ratio": ratio,
            "total_cycles": total,
            "closed_cycles": closed,
            "open_cycles": open_cycles,
            "health_score": round(health_score, 4),
        }
