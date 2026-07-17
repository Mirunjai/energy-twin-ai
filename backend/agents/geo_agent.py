"""Geospatial threat reasoning agent stubs."""

from scipy.stats import beta


def bayesian_threat_update(prior_threat: float, evidence_factor: float) -> float:
    """Update threat belief with a lightweight Bayesian-style posterior estimate."""
    alpha = max(prior_threat, 0.01) * 10
    beta_param = max(1 - prior_threat, 0.01) * 10
    posterior_mean = beta(alpha + evidence_factor, beta_param + 1).mean()
    return float(min(max(posterior_mean, 0.0), 1.0))
