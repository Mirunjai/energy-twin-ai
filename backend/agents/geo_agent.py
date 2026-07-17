from datetime import datetime, timezone
from typing import Dict, Any
from supply_math.bayes import bayesian_update
from models.enums import EventType

class GeopoliticalAgent:
    def __init__(self):
        self.corridor_priors: Dict[str, float] = {
            "strait_of_hormuz": 0.05,
            "suez_canal": 0.03,
            "red_sea_bab_el_mandab": 0.08,
            "us_canada": 0.01
        }
        
        self.likelihoods: Dict[EventType, Dict[str, float]] = {
            EventType.hostile_statement: {"p_e_given_h": 0.65, "p_e_given_not_h": 0.15},
            EventType.sanctions_announcement: {"p_e_given_h": 0.80, "p_e_given_not_h": 0.05},
            EventType.insurance_premium_spike: {"p_e_given_h": 0.90, "p_e_given_not_h": 0.10},
            EventType.kinetic_incident: {"p_e_given_h": 0.95, "p_e_given_not_h": 0.02}
        }
        
        self.explanations: Dict[EventType, str] = {
            EventType.hostile_statement: "Hostile rhetoric indicates growing geopolitical friction, forcing a minor upward reassessment of corridor vulnerability.",
            EventType.sanctions_announcement: "Sanctions announcements economically isolate transit lines, structurally shifting procurement baselines.",
            EventType.insurance_premium_spike: "Commercial insurance premium spikes indicate rapid real-world risk pricing by maritime underwriters.",
            EventType.kinetic_incident: "Kinetic incidents historically exhibit maximum structural threat levels, forcing rapid escalation queues."
        }

    # Added raw_text parameter to preserve the signal for downstream NLP agents
    def analyze_signal(self, corridor: str, supplier: str, event_type: EventType, raw_text: str) -> Dict[str, Any]:
        normalized_corridor = corridor.lower().strip().replace(" ", "_")
        normalized_supplier = supplier.strip().title()
        
        prior = self.corridor_priors.get(normalized_corridor, 0.05)
        profile = self.likelihoods.get(event_type, {"p_e_given_h": 0.50, "p_e_given_not_h": 0.50})
        
        bayes_metrics = bayesian_update(
            prior=prior,
            p_e_given_h=profile["p_e_given_h"],
            p_e_given_not_h=profile["p_e_given_not_h"]
        )
        
        # Direct lookup. If the math engine contract breaks, the API will throw a clean 500.
        post_prob = bayes_metrics["posterior_probability"]
        
        if post_prob <= 0.25:
            severity = "LOW"
        elif post_prob <= 0.50:
            severity = "MODERATE"
        elif post_prob <= 0.75:
            severity = "HIGH"
        else:
            severity = "CRITICAL"
            
        return {
            "corridor": normalized_corridor,
            "supplier": normalized_supplier,
            "event_processed": event_type.value,
            "raw_signal": raw_text, 
            **bayes_metrics,
            "threat_severity": severity,
            "reason": self.explanations.get(event_type, "Unclassified anomaly flagged within target zone."),
            "agent_signature": "Agent-1_Geopolitical_Risk_Core",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }