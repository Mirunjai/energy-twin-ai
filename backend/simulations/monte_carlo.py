import numpy as np
import logging
import time
from models.schemas import SimulationContext, MonteCarloResults
from models.enums import EventType

logger = logging.getLogger("energy_twin.backend.monte_carlo")

class MonteCarloEngine:
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations
        
        # (alpha, beta) parameters tuned to geopolitical severity
        self.severity_distributions = {
            EventType.hostile_statement: (2.0, 5.0),       # High noise, low actual capacity loss
            EventType.sanctions_announcement: (4.0, 3.0),  # Moderate-to-high capacity loss
            EventType.insurance_premium_spike: (3.0, 4.0), # Moderate friction
            EventType.kinetic_incident: (5.0, 2.0)         # Severe physical disruption
        }

    def run(self, context: SimulationContext) -> None:
        logger.info(f"Starting Monte Carlo simulation with N={self.iterations} iterations")

        if not context.geo_response or not context.graph_snapshot:
            logger.warning("Monte Carlo engine lacks geo_response or graph_snapshot. Aborting.")
            return

        # 1. Initialize Reproducible RNG Context
        seed = context.metadata.get("simulation_seed", int(time.time()))
        context.metadata["simulation_seed"] = seed
        rng = np.random.default_rng(seed)

        # 2. Extract Agent Posteriors
        risk_prob = context.geo_response.metrics.posterior_probability
        event_str = context.geo_response.normalized.event_processed
        
        try:
            event_type = EventType(event_str)
        except ValueError:
            event_type = EventType.hostile_statement # Safe fallback

        # 3. Dynamic Baseline Extraction from Snapshot
        corridor_id = context.geo_response.normalized.corridor_id
        baseline_imports_mbd = 0.0
        
        for u, v, data in context.graph_snapshot.G.edges(data=True):
            if u == corridor_id or v == corridor_id:
                baseline_imports_mbd += data.get("capacity_mbd", 0.0)
                
        if baseline_imports_mbd == 0.0:
            logger.warning(f"Corridor {corridor_id} has 0 capacity in graph. Defaulting to 5.0 MBD.")
            baseline_imports_mbd = 5.0

        spr_total_capacity_mb = 45.0 # Total national reserve buffer
        standard_cover_days = 9.5

        # 4. Stochastic Arrays Generation
        disruption_events = rng.binomial(1, risk_prob, self.iterations)
        
        a, b = self.severity_distributions.get(event_type, (2.0, 5.0))
        severity_drops = rng.beta(a=a, b=b, size=self.iterations)

        # 5. Vectorized Shortfall Calculation
        daily_shortfalls_mbd = baseline_imports_mbd * severity_drops * disruption_events

        # 6. Calculate SPR Exhaustion Trajectory (Handling zero-shortfall securely)
        spr_days = np.where(
            daily_shortfalls_mbd > 0.1,
            spr_total_capacity_mb / daily_shortfalls_mbd,
            standard_cover_days
        )
        spr_days = np.clip(spr_days, 0.0, standard_cover_days)

        # 7. Extract Rich Statistics
        context.monte_carlo_results = MonteCarloResults(
            iterations=self.iterations,
            simulation_seed=seed,
            spr_days_remaining_mean=round(float(np.mean(spr_days)), 2),
            spr_days_remaining_median=round(float(np.median(spr_days)), 2),
            spr_days_remaining_std_dev=round(float(np.std(spr_days)), 2),
            spr_days_remaining_p5=round(float(np.percentile(spr_days, 5)), 2),
            spr_days_remaining_p50=round(float(np.percentile(spr_days, 50)), 2),
            spr_days_remaining_p95=round(float(np.percentile(spr_days, 95)), 2),
            expected_shortfall_mbd=round(float(np.mean(daily_shortfalls_mbd)), 2),
            max_shortfall_mbd=round(float(np.max(daily_shortfalls_mbd)), 2),
            confidence_interval_str=f"{round(float(np.percentile(spr_days, 5)), 1)} to {round(float(np.percentile(spr_days, 95)), 1)} days"
        )

        logger.info(
            "Monte Carlo complete", 
            extra={
                "seed": seed, 
                "95_ci_spr_cover": context.monte_carlo_results.confidence_interval_str
            }
        )