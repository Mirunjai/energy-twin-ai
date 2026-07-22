import numpy as np
import logging
import time
from models.schemas import SimulationContext, MonteCarloResults
from simulations.scenario_profiles import SEVERITY_DISTRIBUTIONS

logger = logging.getLogger("energy_twin.backend.monte_carlo")

class MonteCarloEngine:
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations

    def run(self, context: SimulationContext) -> None:
        logger.info(f"Starting Monte Carlo simulation with N={self.iterations} iterations")

        if not context.geo_response or not context.graph_snapshot:
            logger.warning("Monte Carlo engine lacks geo_response or graph_snapshot. Aborting.")
            return

        seed = context.metadata.get("simulation_seed", int(time.time()))
        context.metadata["simulation_seed"] = seed
        rng = np.random.default_rng(seed)

        risk_prob = context.geo_response.metrics.posterior_probability
        
        # 1. Direct, strongly-typed enum fetch from the initial signal
        event_type = context.signal.event_type

        corridor_id = context.geo_response.normalized.corridor_id
        baseline_imports_mbd = 0.0
        
        for u, v, data in context.graph_snapshot.G.edges(data=True):
            if u == corridor_id or v == corridor_id:
                baseline_imports_mbd += data.get("capacity_mbd", 0.0)
                
        if baseline_imports_mbd == 0.0:
            logger.warning(f"Corridor {corridor_id} has 0 capacity in graph. Defaulting to 5.0 MBD.")
            baseline_imports_mbd = 5.0

        spr_total_capacity_mb = 45.0 
        standard_cover_days = 9.5

        disruption_events = rng.binomial(1, risk_prob, self.iterations)
        
        # Pulling from the isolated scenario profile
        a, b = SEVERITY_DISTRIBUTIONS.get(event_type, (2.0, 5.0))
        severity_drops = rng.beta(a=a, b=b, size=self.iterations)

        daily_shortfalls_mbd = baseline_imports_mbd * severity_drops * disruption_events

        spr_days = np.where(
            daily_shortfalls_mbd > 0.1,
            spr_total_capacity_mb / np.maximum(daily_shortfalls_mbd, 1e-9),
            standard_cover_days
        )
        spr_days = np.clip(spr_days, 0.0, standard_cover_days)

        # 2. Optimized statistical caching
        mean_days = float(np.mean(spr_days))
        median_days = float(np.median(spr_days))
        std_dev_days = float(np.std(spr_days))
        p5_days = float(np.percentile(spr_days, 5))
        p50_days = float(np.percentile(spr_days, 50))
        p95_days = float(np.percentile(spr_days, 95))
        mean_shortfall = float(np.mean(daily_shortfalls_mbd))
        max_shortfall = float(np.max(daily_shortfalls_mbd))

        # 3. Lightweight UI Histogram Generation (20 bins)
        counts, bins = np.histogram(spr_days, bins=20)

        context.monte_carlo_results = MonteCarloResults(
            iterations=self.iterations,
            simulation_seed=seed,
            spr_days_remaining_mean=round(mean_days, 2),
            spr_days_remaining_median=round(median_days, 2),
            spr_days_remaining_std_dev=round(std_dev_days, 2),
            spr_days_remaining_p5=round(p5_days, 2),
            spr_days_remaining_p50=round(p50_days, 2),
            spr_days_remaining_p95=round(p95_days, 2),
            expected_shortfall_mbd=round(mean_shortfall, 2),
            max_shortfall_mbd=round(max_shortfall, 2),
            confidence_interval_str=f"{round(p5_days, 1)} to {round(p95_days, 1)} days",
            histogram_bins=[round(float(b), 2) for b in bins],
            histogram_counts=[int(c) for c in counts]
        )

        logger.info(
            "Monte Carlo complete", 
            extra={
                "seed": seed, 
                "95_ci_spr_cover": context.monte_carlo_results.confidence_interval_str
            }
        )