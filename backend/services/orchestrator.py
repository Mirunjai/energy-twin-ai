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

    def process_disruption(self, signal: DisruptionSignal) -> SimulationContext:
        """
        Main pipeline orchestrating the agents, evaluating consensus, 
        and running downstream simulations.
        """
        context = SimulationContext(
            signal=signal,
            metadata={"analysis_version": "1.3.0", "scenario_name": f"{signal.corridor}_crisis"}
        )
        
        # 1. Execute Agents
        self.geo_agent.run(context)
        
        # Map context response to the expected geo_result payload shape
        geo_prob = context.geo_response.metrics.posterior_probability
        geo_result = {
            "posterior_probability": geo_prob,
            "supplier_id": context.geo_response.normalized.supplier_id,
            "corridor_id": context.geo_response.normalized.corridor_id,
            "model_confidence": getattr(context.geo_response.metrics, 'confidence', 0.8),
            "evidence": getattr(context.geo_response, 'extracted_signals', [
                "Sanctions pressure elevated",
                "AIS diversions initiated"
            ])
        }
        
        # Dynamically determine escort strength based on geopolitical context
        # In a real scenario, this is passed from the RAG/Intel agent
        active_escort_strength = 0.35 
        
        comm_result = self.comm_agent.evaluate_corridor_capacity(
            geo_payload=geo_result, 
            escort_strength=active_escort_strength
        )
        
        # 2. Establish Confidence Bands
        geo_band = self._calculate_confidence_band(geo_prob)
        
        final_cap = comm_result.get("final_capacity", 100)
        logistics_band = "CRITICAL" if comm_result.get("is_critical") else "STABLE"
        
        # Compute overall system confidence (mocked heuristic for structure)
        system_confidence = round((geo_result.get("model_confidence", 0.8) * 0.6) + 0.35, 2)
        
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
        # Using .get() for nested dictionaries to prevent KeyErrors if the schema shifts
        math_context = comm_result.get("mathematical_context", {})
        
        reasoning_trail = {
            "bayesian_evidence": {
                "posterior": geo_prob,
                "confidence_band": geo_band,
                "extracted_signals": geo_result.get("evidence")
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