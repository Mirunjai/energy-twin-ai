def bayesian_update(prior: float, p_e_given_h: float, p_e_given_not_h: float) -> dict:
    """
    Executes a standard Bayesian probability update using odds form.
    """
    # Safeguard against division by zero in likelihood ratio
    likelihood_ratio = p_e_given_h / p_e_given_not_h if p_e_given_not_h > 0 else float('inf')
    
    # 1. Convert prior probability to prior odds
    prior_odds = prior / (1.0 - prior) if prior < 1.0 else float('inf')
    
    # 2. Compute posterior odds directly (Core Fix)
    if prior_odds == float('inf') or likelihood_ratio == float('inf'):
        posterior_odds = float('inf')
    else:
        posterior_odds = prior_odds * likelihood_ratio
        
    # 3. Convert posterior odds back to probability
    posterior = posterior_odds / (1.0 + posterior_odds) if posterior_odds != float('inf') else 1.0
    
    delta = posterior - prior
    
    # Renamed from confidence to impact_score to reflect statistical reality
    impact_score = min(abs(delta) * 2, 1.0)
    
    return {
        "prior_probability": round(prior, 4),
        "prior_odds": round(prior_odds, 4) if prior_odds != float('inf') else "inf",
        "likelihood_ratio": round(likelihood_ratio, 4) if likelihood_ratio != float('inf') else "inf",
        "posterior_probability": round(posterior, 4),
        "posterior_odds": round(posterior_odds, 4) if posterior_odds != float('inf') else "inf",
        "risk_delta": round(delta, 4),
        "impact_score": round(impact_score, 4)
    }