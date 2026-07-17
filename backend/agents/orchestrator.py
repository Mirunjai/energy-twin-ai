"""Scenario routing logic across specialist agents."""

from typing import Any

from backend.agents.comm_agent import solve_lanchester_attrition
from backend.agents.geo_agent import bayesian_threat_update
from backend.agents.spr_agent import SPRTracker
from backend.simulations.monte_carlo import run_monte_carlo_spr_drawdown


async def run_orchestration(scenario_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Route input to the relevant modeling stubs and return unified agent output."""
    if scenario_type == "chokepoint_disruption":
        threat = bayesian_threat_update(
            prior_threat=float(payload.get("prior_threat", 0.5)),
            evidence_factor=float(payload.get("evidence_factor", 1.0)),
        )
        attrition = solve_lanchester_attrition(
            attacker_strength=float(payload.get("attacker_strength", 10)),
            defender_strength=float(payload.get("defender_strength", 12)),
            attacker_effectiveness=float(payload.get("attacker_effectiveness", 0.7)),
            defender_effectiveness=float(payload.get("defender_effectiveness", 0.8)),
        )
        tracker = SPRTracker(
            starting_reserve_mmbbl=float(payload.get("reserve_mmbbl", 740.0)),
            drawdown_mmbbl_per_day=float(payload.get("drawdown_mmbbl_per_day", 1.0)),
        )
        simulations = run_monte_carlo_spr_drawdown(
            iterations=int(payload.get("iterations", 100)),
            initial_reserve=tracker.starting_reserve_mmbbl,
            daily_drawdown=tracker.drawdown_mmbbl_per_day,
        )
        return {
            "threat_posterior": threat,
            "attrition": attrition,
            "spr_days_remaining": tracker.days_remaining(),
            "spr_drawdown_simulations": simulations,
        }

    return {"status": "unsupported_scenario", "scenario_type": scenario_type}
