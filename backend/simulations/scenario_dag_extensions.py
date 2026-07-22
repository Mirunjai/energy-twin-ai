


def compute_power_sector_stress(capacity_shortfall_pct: float) -> dict:

	PETROLEUM_TO_POWER_ELASTICITY = 0.35

	stress_multiplier = 1.0 + (PETROLEUM_TO_POWER_ELASTICITY * capacity_shortfall_pct)

	return {
        "power_sector_stress_multiplier": round(stress_multiplier, 4),
        "label": "DIRECTIONAL_ESTIMATE",
        "basis": "IEA petroleum-to-thermal elasticity"
    }


def compute_gdp_impact_estimate_pct(power_stress_multiplier: float) -> dict:
    """Compute GDP impact using cross-economy elasticity and petroleum share of energy demand.

    
    """
   
    
    """
    DAG Node 3: Power sector stress → GDP drag.
    
    IMF estimates India loses ~0.7% GDP per 10% sustained energy cost shock.
    That is -0.07% GDP per 1% of power stress above baseline.
    Source: IMF World Economic Outlook 2024 (directional estimate).
    """
    IMF_ENERGY_TO_GDP_ELASTICITY = -0.07
    excess_stress = power_stress_multiplier - 1.0  # how much above normal (e.g. 1.105 - 1.0 = 0.105)
    gdp_impact_pct = IMF_ENERGY_TO_GDP_ELASTICITY * excess_stress * 100  # convert to percentage points
    return {
        "gdp_impact_estimate_pct": round(gdp_impact_pct, 4),
        "label": "DIRECTIONAL_ESTIMATE",
        "basis": "IMF energy-to-GDP elasticity"
    }
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
	pct = float(capacity_shortfall_pct)
	pct = max(min(pct,1.0),0.0)

	# Simple linear relationships calibrated to produce e.g. 0.3 -> (1.15, -0.4)


	power_sector_stress_multiplier = compute_power_sector_stress(pct)
	gdp_result = compute_gdp_impact_estimate_pct(power_sector_stress_multiplier["power_sector_stress_multiplier"])

	return {
		"power_sector_stress": power_sector_stress_multiplier,
		"gdp_trajectory": gdp_result
	}


# Expected Output Shape (Directional/Elasticity multipliers):
# {
#   "power_sector_stress_multiplier": 1.15,
#   "gdp_impact_estimate_pct": -0.4
# }

if __name__ == "__main__":
    for shortfall in [0.0, 0.1, 0.3, 0.5, 1.0]:
        result = estimate_macro_impacts(shortfall)
        print(f"\nShortfall: {shortfall*100:.0f}%")
        print(f"  Power Stress: {result['power_sector_stress']['power_sector_stress_multiplier']}x")
        print(f"  GDP Impact:   {result['gdp_trajectory']['gdp_impact_estimate_pct']}%")