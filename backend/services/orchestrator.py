import logging
from agents.geo_agent import GeopoliticalAgent
from simulations.monte_carlo import MonteCarloEngine
from graph.network_graph import SupplyChainGraph
from models.schemas import DisruptionSignal, SimulationContext

logger = logging.getLogger("energy_twin.backend.orchestrator")

class CrisisOrchestrator:
    def __init__(self, geo_agent: GeopoliticalAgent, mc_engine: MonteCarloEngine, canonical_graph: SupplyChainGraph):
        self.geo_agent = geo_agent
        self.mc_engine = mc_engine
        self.canonical_graph = canonical_graph
        logger.info("Crisis Orchestrator initialized.")

    def process_disruption(self, signal: DisruptionSignal) -> SimulationContext:
        context = SimulationContext(
            signal=signal,
            metadata={"analysis_version": "1.1.0", "scenario_name": f"{signal.corridor}_crisis"}
        )
        
        # 1. Geopolitical Agent (Bayesian updates are handled internally here)
        self.geo_agent.run(context)
        
        # 2. Graph Snapshot Setup
        context.graph_snapshot = self.canonical_graph.snapshot()
        context.graph_snapshot.update_corridor_risk(
            corridor_id=context.geo_response.normalized.corridor_id, 
            posterior_probability=context.geo_response.metrics.posterior_probability
        )
        
        # 3. Monte Carlo Engine
        self.mc_engine.run(context)
        
        # 4. Optimization Engine (Directly mapping outputs to the new Pydantic model)
        raw_routes = context.graph_snapshot.get_optimal_reroutes(
            source=context.geo_response.normalized.supplier_id,
            target="reliance_jamnagar",
            top_k=3
        )
        context.procurement_alternatives = raw_routes 
        
        # Explicit teardown
        context.graph_snapshot = None 

        return context