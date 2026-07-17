"""Monte Carlo stubs for SPR drawdown modeling."""

import numpy as np
from scipy.stats import norm


def run_monte_carlo_spr_drawdown(
    iterations: int,
    initial_reserve: float,
    daily_drawdown: float,
) -> dict[str, float]:
    """Run a simple stochastic drawdown loop and summarize remaining days."""
    sampled_days = []
    for _ in range(max(iterations, 1)):
        noise = norm.rvs(loc=0.0, scale=0.05)
        adjusted_drawdown = max(daily_drawdown * (1 + noise), 0.01)
        sampled_days.append(max(initial_reserve / adjusted_drawdown, 0.0))

    return {
        "mean_days": float(np.mean(sampled_days)),
        "p10_days": float(np.percentile(sampled_days, 10)),
        "p90_days": float(np.percentile(sampled_days, 90)),
    }
