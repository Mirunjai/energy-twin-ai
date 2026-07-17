import numpy as np
import logging
from models.schemas import SimulationContext, MonteCarloResults

logger = logging.getLogger("energy_twin.backend.monte_carlo")

class MonteCarloEngine:
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations

    def run(self, context: SimulationContext) -> None:
        logger.info(f"Starting Monte Carlo simulation with N={self.iterations} iterations")

        if not context.geo_response or not context.graph_snapshot:
            logger.warning("Monte Carlo engine lacks geo_response or graph_snapshot. Aborting.")
            return

        # 1. Extract dynamic risk from the upstream Geo Agent
        risk_prob = context.geo_response.metrics.posterior_probability

        # 2. Baseline parameters (Hardcoded for hackathon prototype; ideally fetched from graph nodes)
        baseline_imports_mbd = 5.0  # Million barrels per day transiting the targeted corridor
        spr_total_capacity_mb = 45.0 # Total national reserve (yielding ~9.5 days of standard cover)
        standard_cover_days = 9.5

        # 3. Stochastic Arrays Generation
        # Did the disruption manifest? (Coin flip weighted by Bayesian posterior)
        disruption_events = np.random.binomial(1, risk_prob, self.iterations)

        # If disrupted, what fraction of capacity is lost? 
        # A Beta(2, 5) distribution skews towards partial blockades (20-30% loss) rather than total closure
        severity_drops = np.random.beta(a=2.0, b=5.0, size=self.iterations)

        # 4. Calculate Vectorized Shortfalls
        daily_shortfalls_mbd = baseline_imports_mbd * severity_drops * disruption_events

        # 5. Calculate SPR Exhaustion Trajectory
        # Avoid division by zero: if shortfall is minimal, SPR remains at baseline standard cover
        spr_days = np.where(
            daily_shortfalls_mbd > 0.1,
            spr_total_capacity_mb / daily_shortfalls_mbd,
            standard_cover_days
        )
        
        # Cap the output at the physical maximum reserve capacity
        spr_days = np.clip(spr_days, 0.0, standard_cover_days)

        # 6. Extract Statistics for the UI
        mean_days = np.mean(spr_days)
        p5_days = np.percentile(spr_days, 5)   # Worst-case scenario
        p95_days = np.percentile(spr_days, 95) # Best-case scenario
        mean_shortfall = np.mean(daily_shortfalls_mbd)

        # 7. Enrich the Shared Context
        context.monte_carlo_results = MonteCarloResults(
            iterations=self.iterations,
            spr_days_remaining_mean=round(float(mean_days), 2),
            spr_days_remaining_p5=round(float(p5_days), 2),
            spr_days_remaining_p95=round(float(p95_days), 2),
            expected_shortfall_mbd=round(float(mean_shortfall), 2),
            confidence_interval_str=f"{round(float(p5_days), 1)} to {round(float(p95_days), 1)} days"
        )

        logger.info(
            "Monte Carlo complete", 
            extra={"95_ci_spr_cover": context.monte_carlo_results.confidence_interval_str}
        )