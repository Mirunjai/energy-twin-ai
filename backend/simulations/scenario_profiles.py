from models.enums import EventType

# (alpha, beta) parameters tuned to geopolitical severity profiles
SEVERITY_DISTRIBUTIONS = {
    EventType.hostile_statement: (2.0, 5.0),       # High noise, low actual capacity loss
    EventType.sanctions_announcement: (4.0, 3.0),  # Moderate-to-high capacity loss
    EventType.insurance_premium_spike: (3.0, 4.0), # Moderate friction
    EventType.kinetic_incident: (5.0, 2.0)         # Severe physical disruption
}