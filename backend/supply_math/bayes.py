def _validate_probability(name: str, value: float):
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} probability must be between 0.0 and 1.0.")

def bayesian_update(prior: float, p_e_given_h: float, p_e_given_not_h: float) -> dict:
    """
    Executes a standard Bayesian probability update using odds form.
    Returns a plain dictionary to remain agnostic of the web/API layer.
    """
    _validate_probability("prior", prior)
    _validate_probability("p_e_given_h", p_e_given_h)
    _validate_probability("p_e_given_not_h", p_e_given_not_h)

    likelihood_ratio = p_e_given_h / p_e_given_not_h if p_e_given_not_h > 0 else float('inf')
    prior_odds = prior / (1.0 - prior) if prior < 1.0 else float('inf')
    
    if prior_odds == float('inf') or likelihood_ratio == float('inf'):
        posterior_odds = float('inf')
    else:
        posterior_odds = prior_odds * likelihood_ratio
        
    posterior = posterior_odds / (1.0 + posterior_odds) if posterior_odds != float('inf') else 1.0
    delta = posterior - prior
    impact_score = min(abs(delta) * 2, 1.0)
    
    return {
        "prior_probability": round(prior, 4),
        "prior_odds": round(prior_odds, 4) if prior_odds != float('inf') else float('inf'),
        "likelihood_ratio": round(likelihood_ratio, 4) if likelihood_ratio != float('inf') else float('inf'),
        "posterior_probability": round(posterior, 4),
        "posterior_odds": round(posterior_odds, 4) if posterior_odds != float('inf') else float('inf'),
        "risk_delta": round(delta, 4),
        "impact_score": round(impact_score, 4)
    }