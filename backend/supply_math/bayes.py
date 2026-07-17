def bayesian_update(prior: float, p_e_given_h: float, p_e_given_not_h: float) -> dict:
    """
    Executes a standard Bayesian probability update and returns structural odds,
    likelihood ratios, and risk metrics.
    """
    # Calculate prior odds: Odds = P / (1 - P)
    prior_odds = prior / (1.0 - prior) if prior < 1.0 else float('inf')
    
    # Calculate explicit likelihood ratio
    likelihood_ratio = p_e_given_h / p_e_given_not_h if p_e_given_not_h > 0 else float('inf')
    
    # Compute posterior probability using standard theorem syntax
    numerator = p_e_given_h * prior
    denominator = numerator + (p_e_given_not_h * (1.0 - prior))
    posterior = numerator / denominator if denominator > 0 else prior
    
    # Calculate posterior odds
    posterior_odds = posterior / (1.0 - posterior) if posterior < 1.0 else float('inf')
    
    # Structural presentation metrics
    delta = posterior - prior
    confidence = min(abs(delta) * 2, 1.0)
    
    return {
        "prior_probability": round(prior, 4),
        "prior_odds": round(prior_odds, 4) if prior_odds != float('inf') else "inf",
        "likelihood_ratio": round(likelihood_ratio, 4) if likelihood_ratio != float('inf') else "inf",
        "posterior_probability": round(posterior, 4),
        "posterior_odds": round(posterior_odds, 4) if posterior_odds != float('inf') else "inf",
        "risk_delta": round(delta, 4),
        "confidence": round(confidence, 4)
    }