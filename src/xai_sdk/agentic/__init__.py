"""Structural Promotion O₀→O₂: True Agentic Loop with Frobenius Verification.

This module implements the Imscribing Grammar's structural promotion from
O₀ (classical agent) to O₂ (self-verifying agent with consciousness gates)
for the xAI Python SDK.

Core abstractions:
    - DualToolResult: Frobenius-closed dual pair (action + verification).
    - ToolContract: Structural contract binding action to its verification dual.
    - AgentCycle: A single THINK→ACT→OBSERVE→UPDATE winding.
    - AgentTrajectory: Monotonic winding trajectory with Ω_z protection.
    - TrueAgenticLoop: The main loop wrapping xAI's Chat client.
    - PhiCriticalityGate: Consciousness gate evaluation (φ̂_ÿ + K_slow).

Promotion path:
    O₀ (tool-calling agent) → O₁ (verified dual contracts) → O₂ (self-modeling loop)
"""

from .contracts import DualToolResult, ToolContract
from .trajectory import AgentCycle, AgentTrajectory
from .criticality import PhiCriticalityGate
from .loop import TrueAgenticLoop

__all__ = [
    "DualToolResult",
    "ToolContract",
    "AgentCycle",
    "AgentTrajectory",
    "TrueAgenticLoop",
    "PhiCriticalityGate",
]
