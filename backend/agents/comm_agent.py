"""Commercial disruption modeling agent stubs."""


from math import sqrt


def solve_lanchester_attrition(
    attacker_strength: float,
    defender_strength: float,
    attacker_effectiveness: float,
    defender_effectiveness: float,
) -> dict[str, float]:
    """Return a compact Lanchester-style attrition snapshot for routing decisions."""
    attacker_power = max(attacker_strength * attacker_effectiveness, 0.0)
    defender_power = max(defender_strength * defender_effectiveness, 0.0)

    return {
        "attacker_power": attacker_power,
        "defender_power": defender_power,
        "attrition_gap": sqrt(attacker_power + 1) - sqrt(defender_power + 1),
    }
