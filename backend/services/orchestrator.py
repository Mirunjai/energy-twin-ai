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

    def process_disruption(self, signal: DisruptionSignal) -> SimulationContext:
        """
        Main pipeline orchestrating the agents, evaluating consensus, 
        and running downstream simulations.
        """
        context = SimulationContext(
            signal=signal,
            metadata={"analysis_version": "1.2.0", "scenario_name": f"{signal.corridor}_crisis"}
        )
        
        # 1. Agent 1: Geopolitical & Bayesian Assessment
        # (Assuming geo_agent.run populates context.geo_response, 
        # or we simulate the run_analysis dict behavior here)
        self.geo_agent.run(context)
        geo_result = {
            "posterior_probability": context.geo_response.metrics.posterior_probability,
            "supplier_id": context.geo_response.normalized.supplier_id,
            "corridor_id": context.geo_response.normalized.corridor_id
        }
        
        # 2. Agent 2: Commodity & Logistics (Lanchester + AIS/Market)
        comm_result = self.comm_agent.evaluate_corridor_capacity(
            geo_payload=geo_result, 
            escort_level="low" # Can be dynamically pulled from active intelligence
        )
        
        # 3. Agent Disagreement Logic
        geo_prob = geo_result.get("posterior_probability", 0.5)
        geo_confidence = "LOW" if geo_prob < 0.40 else "HIGH"
        logistics_attrition = "HIGH" if comm_result.get("is_critical") else "LOW"
        
        escalation_flag = None
        disagreement_reasoning = None
        
        if geo_confidence == "LOW" and logistics_attrition == "HIGH":
            escalation_flag = "ESCALATE TO HUMAN ANALYST"
            disagreement_reasoning = (
                "Agent disagreement detected\n\n"
                f"Bayesian confidence:\n{geo_confidence} ({(geo_prob * 100):.1f}%)\n\n"
                f"Shipping attrition:\n{logistics_attrition} (Critical in {comm_result.get('days_to_critical', 'N/A')} days)\n\n"
                "Recommendation:\nEscalate to analyst"
            )
            logger.warning(escalation_flag)
        elif geo_confidence == "HIGH" and logistics_attrition == "HIGH":
            escalation_flag = "CONSENSUS ALIGNED: CRITICAL"
        else:
            escalation_flag = "CONSENSUS ALIGNED: STABLE"

        # Attach agent coordination results to context metadata
        context.metadata["agent_analysis"] = {
            "geo": geo_result,
            "comm": comm_result,
            "escalation_status": escalation_flag,
            "disagreement_context": disagreement_reasoning
        }
        
        # 4. Graph Snapshot Setup
        context.graph_snapshot = self.canonical_graph.snapshot()
        context.graph_snapshot.update_corridor_risk(
            corridor_id=geo_result["corridor_id"], 
            posterior_probability=geo_prob
        )
        
        # 5. Monte Carlo Engine
        self.mc_engine.run(context)
        
        # 6. Optimization Engine
        raw_routes = context.graph_snapshot.get_optimal_reroutes(
            source=geo_result["supplier_id"],
            target="reliance_jamnagar",
            top_k=3
        )
        context.procurement_alternatives = raw_routes 
        
        # Explicit teardown
        context.graph_snapshot = None 

        return context