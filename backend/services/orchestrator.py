import logging
from agents.geo_agent import GeopoliticalAgent
from agents.comm_agent import CommodityAgent
from simulations.monte_carlo import MonteCarloEngine
from graph.network_graph import SupplyChainGraph
from models.schemas import DisruptionSignal, SimulationContext

logger = logging.getLogger("energy_twin.backend.orchestrator")

class CrisisOrchestrator:
    def __init__(
        self, 
        geo_agent: GeopoliticalAgent, 
        comm_agent: CommodityAgent, 
        mc_engine: MonteCarloEngine, 
        canonical_graph: SupplyChainGraph
    ):
        self.geo_agent = geo_agent
        self.comm_agent = comm_agent
        self.mc_engine = mc_engine
        self.canonical_graph = canonical_graph
        logger.info("Crisis Orchestrator initialized.")

    def _calculate_confidence_band(self, probability: float) -> str:
        if probability < 0.20: return "VERY LOW"
        if probability < 0.40: return "LOW"
        if probability < 0.60: return "MEDIUM"
        if probability < 0.80: return "HIGH"
        return "VERY HIGH"

    def _calculate_system_confidence(self, geo_band: str, logistics_band: str, evidence_count: int, data_freshness: float = 1.0) -> float:
        """
        Derives confidence from observable quantities rather than heuristics.
        - data_freshness: 1.0 (live) to 0.0 (stale)
        - evidence_count: Number of distinct intelligence sources
        - agreement: Do Agent 1 and Agent 2 align?
        """
        # 1. Base factor from evidence volume (max 0.4)
        evidence_factor = min(evidence_count * 0.1, 0.4)
        
        # 2. Base factor from data freshness (max 0.4)
        freshness_factor = data_freshness * 0.4
        
        # 3. Agreement bonus (max 0.2)
        agents_agree = (geo_band in ["HIGH", "VERY HIGH"] and logistics_band == "CRITICAL") or \
                       (geo_band in ["VERY LOW", "LOW"] and logistics_band == "STABLE")
        agreement_bonus = 0.2 if agents_agree else 0.0
        
        return round(min(evidence_factor + freshness_factor + agreement_bonus, 1.0), 2)

    def process_disruption(self, signal: DisruptionSignal) -> SimulationContext:
        """
        Main pipeline orchestrating the agents, evaluating consensus, 
        and running downstream simulations.
        """
        context = SimulationContext(
            signal=signal,
            metadata={"analysis_version": "1.4.0", "scenario_name": f"{signal.corridor}_crisis"}
        )
        
        # 1. Execute Agents
        self.geo_agent.run(context)
        
        geo_prob = context.geo_response.metrics.posterior_probability
        
        # Extract evidence list to use for confidence scoring later
        extracted_evidence = getattr(context.geo_response, 'extracted_signals', [
            "Sanctions pressure elevated",
            "AIS diversions initiated"
        ])
        
        geo_result = {
            "posterior_probability": geo_prob,
            "supplier_id": context.geo_response.normalized.supplier_id,
            "corridor_id": context.geo_response.normalized.corridor_id,
            "model_confidence": getattr(context.geo_response.metrics, 'confidence', 0.8),
            "evidence": extracted_evidence
        }
        
        # Dynamically determine escort strength (mocked for now, normally from RAG/Intel)
        active_escort_strength = 0.35 
        
        comm_result = self.comm_agent.evaluate_corridor_capacity(
            geo_payload=geo_result, 
            escort_strength=active_escort_strength
        )
        
        # 2. Establish Confidence Bands
        geo_band = self._calculate_confidence_band(geo_prob)
        
        final_cap = comm_result.get("final_capacity", 100)
        logistics_band = "CRITICAL" if comm_result.get("is_critical") else "STABLE"
        
        # Compute overall system confidence using the observable metrics method
        evidence_count = len(extracted_evidence)
        # Using a default freshness of 1.0, though you could map this to signal.metadata.get("freshness", 1.0)
        system_confidence = self._calculate_system_confidence(
            geo_band=geo_band, 
            logistics_band=logistics_band, 
            evidence_count=evidence_count, 
            data_freshness=1.0 
        )
        
        # 3. Disagreement Logic & Escalation Routing
        escalation_flag = "MONITORING"
        
        if geo_band in ["VERY LOW", "LOW"] and logistics_band == "CRITICAL":
            escalation_flag = "ESCALATE TO HUMAN ANALYST"
            disagreement_type = "LATENT VULNERABILITY DETECTED"
            logger.warning(f"{escalation_flag} - {disagreement_type}")
            
        elif geo_band in ["HIGH", "VERY HIGH"] and logistics_band == "STABLE":
            escalation_flag = "ESCALATE TO HUMAN ANALYST"
            disagreement_type = "RESILIENT CORRIDOR: FALSE ALARM OVERRIDE"
            logger.warning(f"{escalation_flag} - {disagreement_type}")
            
        elif geo_band in ["HIGH", "VERY HIGH"] and logistics_band == "CRITICAL":
            escalation_flag = "CONSENSUS ALIGNED: INITIATE REROUTE PROTOCOLS"
            disagreement_type = "NONE"
            
        else:
            disagreement_type = "NONE"

        # 4. Structured Reasoning Trail
        math_context = comm_result.get("mathematical_context", {})
        
        reasoning_trail = {
            "bayesian_evidence": {
                "posterior": geo_prob,
                "confidence_band": geo_band,
                "extracted_signals": extracted_evidence
            },
            "lanchester_evidence": {
                "days_to_critical": comm_result.get("days_to_critical"),
                "escort_strength_applied": active_escort_strength,
                "projected_final_capacity": final_cap,
                "adaptation_rate": math_context.get("recovery_coefficient", 0.0)
            },
            "market_evidence": comm_result.get("logistics_signals", []),
            "disagreement_context": disagreement_type,
            "overall_system_confidence": system_confidence
        }
        
        # Attach to context metadata
        context.metadata["agent_analysis"] = {
            "geo": geo_result,
            "comm": comm_result,
            "escalation_status": escalation_flag,
            "reasoning_trail": reasoning_trail
        }
        
        # 5. Graph Snapshot Setup
        context.graph_snapshot = self.canonical_graph.snapshot()
        context.graph_snapshot.update_corridor_risk(
            corridor_id=geo_result["corridor_id"], 
            posterior_probability=geo_prob
        )
        
        # 6. Monte Carlo Engine
        self.mc_engine.run(context)
        
        # 7. Optimization Engine
        raw_routes = context.graph_snapshot.get_optimal_reroutes(
            source=geo_result["supplier_id"],
            target="reliance_jamnagar",
            top_k=3
        )
        context.procurement_alternatives = raw_routes 
        
        # Explicit teardown
        context.graph_snapshot = None 

        return context