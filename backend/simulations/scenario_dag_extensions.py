# Input parameters:
def estimate_macro_impacts(capacity_shortfall_pct: float) -> dict:
	"""Estimate simple macro impacts from a capacity shortfall percentage.

	Args:
		capacity_shortfall_pct: shortfall expressed as a proportion (e.g. 0.2 for 20%).

	Returns:
		dict with keys:
		  - power_sector_stress_multiplier: multiplicative stress on power sector (float)
		  - gdp_impact_estimate_pct: estimated % impact on GDP (float, negative for contraction)
	"""
	if capacity_shortfall_pct is None:
		raise ValueError("capacity_shortfall_pct must be provided")
	try:
		pct = float(capacity_shortfall_pct)
	except (TypeError, ValueError):
		raise ValueError("capacity_shortfall_pct must be numeric")

	# Keep inputs in a reasonable range
	pct = max(min(pct, 1.0), -1.0)

	# Simple linear relationships calibrated to produce e.g. 0.3 -> (1.15, -0.4)
	stress_coef = 0.5
	gdp_coef = -1.3333333333333333

	power_sector_stress_multiplier = 1.0 + stress_coef * pct
	gdp_impact_estimate_pct = gdp_coef * pct

	return {
		"power_sector_stress_multiplier": power_sector_stress_multiplier,
		"gdp_impact_estimate_pct": gdp_impact_estimate_pct,
	}


# Expected Output Shape (Directional/Elasticity multipliers):
# {
#   "power_sector_stress_multiplier": 1.15,
#   "gdp_impact_estimate_pct": -0.4
# }
