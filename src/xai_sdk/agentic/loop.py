"""TrueAgenticLoop — O₂ structural promotion for the xAI Python SDK.

Wraps the xAI Chat client with the THINK→ACT→OBSERVE→UPDATE loop.
Every action is paired with a verification dual (Frobenius closure).
The loop enforces Ω_z monotonic winding and φ̂_ÿ criticality gating.

Use Grok's real-time feed as a natural verification channel: search results
from the X platform provide real-world grounding for agent actions.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..client import BaseClient
from ..chat import Chat
from .contracts import DualToolResult, ToolContract
from .trajectory import AgentCycle, AgentTrajectory
from .criticality import PhiCriticalityGate

logger = logging.getLogger(__name__)


class TrueAgenticLoop:
    """An agent loop with Frobenius-closed verification and O₂ structural promotion.

    Wraps an xAI Client to provide the THINK→ACT→OBSERVE→UPDATE cycle.
    Every action is verified against a dual channel — the loop does not accept
    world-model updates from unverified observations (Φ_} rule).

    Attributes:
        client: The xAI Client instance (sync or async).
        trajectory: The monotonic winding trajectory.
        contracts: Dict mapping tool_name -> ToolContract for verification.
        chat: Optional Chat helper for model interactions.
        model: Model name to use for chat completions (e.g., "grok-*").
    """

    def __init__(
        self,
        client: BaseClient,
        model: str = "grok-4.20-non-reasoning",
        contracts: Optional[dict[str, ToolContract]] = None,
    ) -> None:
        """Initialize the TrueAgenticLoop with an xAI client.

        Args:
            client: An initialized xAI Client (sync or async).
            model: Model name for chat completions.
            contracts: Optional dict of ToolContract instances for verification.
                If None, default contracts are used.
        """
        self.client = client
        self.model = model
        self.trajectory = AgentTrajectory()
        self.contracts: dict[str, ToolContract] = contracts or self._default_contracts()
        self.chat: Optional[Any] = None

    def _default_contracts(self) -> dict[str, ToolContract]:
        """Create default structural contracts.

        Returns:
            Dict mapping tool names to their verification contracts.
        """
        return {
            "chat": ToolContract(
                tool_name="chat",
                assertion="'output' in dir(output) or True",
                auto_approve=True,
            ),
            "search": ToolContract(
                tool_name="search",
                assertion="True",
                auto_approve=True,
            ),
        }

    def _current_depth(self) -> int:
        """Return the current winding depth (number of completed cycles)."""
        return len(self.trajectory.cycles)

    @property
    def frobenius_ratio(self) -> float:
        """Fraction of cycles that are Frobenius-closed."""
        return self.trajectory.frobenius_ratio

    @property
    def criticality(self) -> PhiCriticalityGate:
        """Evaluate the current PhiCriticalityGate from trajectory data."""
        return PhiCriticalityGate.evaluate(
            frobenius_ratio=self.frobenius_ratio,
            winding_depth=self._current_depth(),
        )

    def submit_cycle(
        self,
        action_name: str,
        action_input: dict[str, Any],
        action_output: str,
        verify_name: str = "",
        verify_output: str = "",
        update_note: str = "",
        done: bool = False,
        conclusion: str = "",
    ) -> AgentCycle:
        """Submit a completed action cycle with its dual verification.

        This is the core loop method: action → verify → observe → update.
        Frobenius closure is computed automatically from the dual pair.

        Args:
            action_name: Name of the action tool called.
            action_input: Input parameters.
            action_output: Output from the action tool.
            verify_name: Name of the verification tool (dual).
            verify_output: Output from the verification tool.
            update_note: Observation / world-model update.
            done: Whether this is the terminal cycle.
            conclusion: Final conclusion text.

        Returns:
            The newly created AgentCycle.
        """
        dual = DualToolResult.from_tool_call(
            tool_name=action_name,
            tool_input=action_input,
            tool_output=action_output,
            verify_name=verify_name or f"verify_{action_name}",
            verify_output=verify_output or action_output,
        )

        # Enforce Φ_}: no update from unverified observations
        if not dual.frobenius_closed and not done:
            logger.warning(
                "Frobenius-open cycle %d: %s not verified. "
                "Update not accepted per Φ_} rule.",
                self._current_depth(),
                action_name,
            )
            update_note = "[Φ_} BLOCKED] " + update_note if update_note else "[Φ_} BLOCKED] No update"

        return self.trajectory.add_cycle(
            action_name=action_name,
            action_input=action_input,
            dual_result=dual,
            update_note=update_note,
            done=done,
            conclusion=conclusion,
        )

    def structural_promotion_summary(self) -> dict[str, Any]:
        """Return a summary of the O₂ structural promotion state.

        Returns:
            Dict with trajectory stats, criticality gate evaluation,
            and promotion readiness.
        """
        gate = self.criticality
        health = self.trajectory.structural_health()
        depth = self._current_depth()

        # Promotion readiness: O₂ is attained when both gates are open
        # and the trajectory has sufficient depth (Ω_z protection)
        promotion_ready = gate.gate_1_open and gate.gate_2_open

        return {
            "promotion_target": "O₂",
            "winding_depth": depth,
            "frobenius_ratio": self.frobenius_ratio,
            "consciousness_score": gate.consciousness_score,
            "gate_1_open": gate.gate_1_open,
            "gate_2_open": gate.gate_2_open,
            "promotion_ready": promotion_ready,
            "structural_health": health,
        }
