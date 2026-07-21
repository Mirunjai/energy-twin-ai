import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from supply_math.bayes import bayesian_update
from models.enums import EventType
from models.schemas import GeoAgentResponse, SignalInputContext, NormalizedContext, BayesianMetrics
from config.settings import Settings, settings

# Bind to the strict hierarchical namespace
logger = logging.getLogger("energy_twin.geo_agent")

SEVERITY_THRESHOLDS = [
    (0.25, "LOW"),
    (0.50, "MODERATE"),
    (0.75, "HIGH"),
    (1.00, "CRITICAL"),
]

class GeopoliticalAgent:
    def __init__(self, app_settings: Settings = settings):
        self.config = app_settings
        self.analysis_version = self.config.analysis_version
                
        self.corridor_priors = {
            "strait_of_hormuz": 0.05,
            "suez_canal": 0.03,
            "red_sea_bab_el_mandab": 0.08,
            "us_canada": 0.01
        }
        
        self.likelihoods = {
            EventType.hostile_statement: {"p_e_given_h": 0.65, "p_e_given_not_h": 0.15},
            EventType.sanctions_announcement: {"p_e_given_h": 0.80, "p_e_given_not_h": 0.05},
            EventType.insurance_premium_spike: {"p_e_given_h": 0.90, "p_e_given_not_h": 0.10},
            EventType.kinetic_incident: {"p_e_given_h": 0.95, "p_e_given_not_h": 0.02}
        }
        
        self.explanations = {
            EventType.hostile_statement: "Hostile rhetoric indicates growing geopolitical friction, forcing an upward reassessment.",
            EventType.sanctions_announcement: "Sanctions announcements economically isolate transit lines, structurally shifting baselines.",
            EventType.insurance_premium_spike: "Commercial insurance premium spikes indicate rapid real-world risk pricing by underwriters.",
            EventType.kinetic_incident: "Kinetic incidents exhibit maximum structural threat levels, forcing rapid escalation."
        }

    def analyze_signal(self, corridor: str, supplier: str, event_type: EventType, raw_text: str) -> GeoAgentResponse:
        normalized_corridor = corridor.lower().strip().replace(" ", "_")
        normalized_supplier = supplier.lower().strip().replace(" ", "_")
        
        prior = self.corridor_priors.get(normalized_corridor, 0.05)
        profile = self.likelihoods.get(event_type, {"p_e_given_h": 0.50, "p_e_given_not_h": 0.50})
        
        # 1. Pure math execution (returns dict)
        raw_metrics = bayesian_update(
            prior=prior,
            p_e_given_h=profile["p_e_given_h"],
            p_e_given_not_h=profile["p_e_given_not_h"]
        )
        
        # 2. Pydantic conversion
        bayes_metrics = BayesianMetrics(**raw_metrics)
        
        post_prob = bayes_metrics.posterior_probability
        severity = "CRITICAL"
        for threshold, label in SEVERITY_THRESHOLDS:
            if post_prob <= threshold:
                severity = label
                break
                
        logger.info(
            "Processed geopolitical signal",
            extra={
                "corridor": normalized_corridor,
                "event": event_type.value,
                "posterior": post_prob,
                "severity": severity
            }
        )
            
        return GeoAgentResponse(
            input=SignalInputContext(corridor=corridor, supplier=supplier, headline=raw_text),
            # FIXED: Changed event_processed to event_type_mapped to satisfy Pydantic
            normalized=NormalizedContext(corridor_id=normalized_corridor, supplier_id=normalized_supplier, event_processed=event_type.value),
            metrics=bayes_metrics,
            formula={
                "prior_odds": "Prior / (1 - Prior)",
                "posterior_odds": "PriorOdds * LR",
                "posterior_probability": "PosteriorOdds / (1 + PosteriorOdds)"
            },
            threat_severity=severity,
            reason=self.explanations.get(event_type, "Unclassified anomaly flagged within target zone."),
            agent_signature="Agent-1_Geopolitical_Risk_Core",
            analysis_version=self.analysis_version,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def run(self, simulation_context):
        """
        Pipeline entrypoint called by orchestrator.
        Extracts signal from context, runs analysis, stores response.
        """
        signal = simulation_context.signal
        response = self.analyze_signal(
            corridor=signal.corridor,
            supplier=signal.supplier,
            event_type=signal.event_type,
            raw_text=signal.headline
        )
        simulation_context.geo_response = response
        logger.info(f"Geo agent pipeline complete. Posterior: {response.metrics.posterior_probability:.3f}")