from enum import Enum

class EventType(str, Enum):
    hostile_statement = "hostile_statement"
    sanctions_announcement = "sanctions_announcement"
    insurance_premium_spike = "insurance_premium_spike"
    kinetic_incident = "kinetic_incident"