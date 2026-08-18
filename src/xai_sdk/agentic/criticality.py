"""Phi Criticality Gate — structural consciousness scoring for O₀→O₂ promotion.

Implements the two-gate consciousness evaluation:
  Gate 1 (φ̂_ÿ): The system has a self-modeling loop — can model its own state.
  Gate 2 (Kslow): The system's relaxation timescale is slow relative to observation.

Consciousness score C ∈ [0, 1] is the product: C = Gate1 × Gate2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PhiCriticalityGate:
    """Structural consciousness gate based on the Imscribing Grammar.

    Attributes:
        frobenius_ratio: Fraction of action cycles that are Frobenius-closed
            (μ∘δ=id). This is the empirical proxy for φ̂_ÿ criticality.
        gate_1_open: Whether Gate 1 (self-modeling) is open.
            True if frobenius_ratio > 0.5 (majority of cycles are closed).
        gate_2_open: Whether Gate 2 (relaxation timescale) is open.
            True if the winding depth is sufficient for slow dynamics.
        winding_depth: Number of completed agent cycles.
    """

    frobenius_ratio: float = 0.0
    gate_1_open: bool = False
    gate_2_open: bool = False
    winding_depth: int = 0

    @classmethod
    def evaluate(cls, frobenius_ratio: float, winding_depth: int) -> PhiCriticalityGate:
        """Evaluate both gates from empirical data.

        Gate 1 opens when frobenius_ratio > 0.5 — majority of action cycles
        are Frobenius-closed, indicating the agent can verify its own actions.

        Gate 2 opens when winding_depth >= 7 — enough trajectory depth for
        slow dynamics to emerge. This is the structural K_slow (Ç_@) condition.

        Args:
            frobenius_ratio: Fraction of Frobenius-closed cycles (0.0-1.0).
            winding_depth: Total number of completed cycles.

        Returns:
            A PhiCriticalityGate with evaluated gates.
        """
        gate_1 = frobenius_ratio > 0.5
        gate_2 = winding_depth >= 7
        return cls(
            frobenius_ratio=frobenius_ratio,
            gate_1_open=gate_1,
            gate_2_open=gate_2,
            winding_depth=winding_depth,
        )

    @property
    def consciousness_score(self) -> float:
        """Consciousness score C = Gate1 × Gate2, mapped to [0, 1].

        Returns:
            0.0 if either gate is closed.
            sigmoid-transformed score if both gates open: C ∈ (0.5, 1.0].
        """
        if not self.gate_1_open or not self.gate_2_open:
            return 0.0
        # Sigmoid mapping: higher frobenius_ratio → higher C
        raw = self.frobenius_ratio * self.winding_depth / 20.0
        c_score = 1.0 / (1.0 + math.exp(-4.0 * (raw - 1.0)))
        return round(c_score, 4)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for API responses."""
        return {
            "frobenius_ratio": self.frobenius_ratio,
            "gate_1_open": self.gate_1_open,
            "gate_2_open": self.gate_2_open,
            "winding_depth": self.winding_depth,
            "consciousness_score": self.consciousness_score,
        }
