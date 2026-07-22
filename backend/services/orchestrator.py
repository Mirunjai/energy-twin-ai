import logging
# 1. Fixed Imports: Pull the Retriever and the new consolidated RAG Agent
from rag.retriever import EvidenceRetriever
from agents.rag_agent import RAGIntelligenceAgent, ObservationEncoder
from agents.geo_agent import GeopoliticalAgent
from agents.comm_agent import CommodityLogisticsAgent 
from simulations.monte_carlo import MonteCarloEngine
from graph.network_graph import SupplyChainGraph
from models.schemas import DisruptionSignal, SimulationContext, ProcurementAlternative

# --- NEW IMPORTS FOR PHASE 1 WIRING ---
from simulations.scenario_dag_extensions import estimate_macro_impacts
from optimization.procurement_lp import optimize_procurement
from agents.spr_agent import SPRTracker

logger = logging.getLogger("energy_twin.backend.orchestrator")

class CrisisOrchestrator:
    # 2. Fixed Init: Removed the dead hmm_agent argument
    def __init__(
        self, 
        geo_agent: GeopoliticalAgent, 
        comm_agent: CommodityLogisticsAgent, 
        mc_engine: MonteCarloEngine, 
        canonical_graph: SupplyChainGraph
    ):
        self.geo_agent = geo_agent
        self.comm_agent = comm_agent
        self.mc_engine = mc_engine
        self.canonical_graph = canonical_graph
        
        # Initialize Agent 3 (Consolidated RAG + HMM)
        self.retriever = EvidenceRetriever()
        self.rag_agent = RAGIntelligenceAgent()
        
        # Initialize the fixed SPR agent
        self.spr_agent = SPRTracker()
        
        # Auto-seed vector store if empty
        try:
            if self.retriever.store.collection.count() == 0:
                self.retriever.store.ingest_case_studies()
                logger.info("Vector store auto-seeded with 3 historical case studies (Houthi 2023, Iran 2025, McKinsey).")
        except Exception as e:
            logger.warning(f"Vector store seeding attempted but encountered issue: {e}. Retriever may return empty results.")
        
        logger.info("Crisis Orchestrator initialized.")

    def _calculate_confidence_band(self, probability: float) -> str:
        if probability < 0.20: return "VERY LOW"
        if probability < 0.40: return "LOW"
        if probability < 0.60: return "MEDIUM"
        if probability < 0.80: return "HIGH"
        return "VERY HIGH"

    def _calculate_system_confidence(self, geo_band: str, logistics_band: str, evidence_count: int, data_freshness: float = 1.0) -> float:
        evidence_factor = min(evidence_count * 0.1, 0.4)
        freshness_factor = data_freshness * 0.4
        
        agents_agree = (geo_band in ["HIGH", "VERY HIGH"] and logistics_band == "CRITICAL") or \
                       (geo_band in ["VERY LOW", "LOW"] and logistics_band == "STABLE")
        agreement_bonus = 0.2 if agents_agree else 0.0
        
        return round(min(evidence_factor + freshness_factor + agreement_bonus, 1.0), 2)

    def process_disruption(self, signal: DisruptionSignal) -> SimulationContext:
        context = SimulationContext(
            signal=signal,
            metadata={"analysis_version": "1.7.0", "scenario_name": f"{signal.corridor}_crisis"}
        )
        
        # 1. Pipeline Execution: Geo Agent
        self.geo_agent.run(context)
        geo_prob = context.geo_response.metrics.posterior_probability
        
        # 3. Fixed Retrieval: Call the retriever explicitly
        event_description = signal.headline  # Use the actual schema field
        evidence_cards = self.retriever.retrieve_analogues(event_description)
        
        # --- BUG 4 FIX START ---
        # Reconcile the incoming EventType enum with the JSON threat profile keys
        threat_mapping = {
            "kinetic_incident": "drone_attacks",
            "sanctions_announcement": "sanctions_pressure",
            "hostile_statement": "naval_blockade",
            "insurance_premium_spike": "naval_blockade"
        }
        
        # Safely map the event type, falling back to "default" if not found
        mapped_threat = threat_mapping.get(signal.event_type.value, "default")

        geo_result = {
            "posterior_probability": geo_prob,
            "threat_type": mapped_threat,   # <-- Pass the mapped threat type to Agent 2
            "supplier_id": context.geo_response.normalized.supplier_id,
            "corridor_id": context.geo_response.normalized.corridor_id,
            "model_confidence": getattr(context.geo_response.metrics, 'confidence', 0.8),
            "evidence": evidence_cards
        }
        # --- BUG 4 FIX END ---
        
        active_escort_strength = 0.35 
        
        # 3. Pipeline Execution: Comm Agent 
        comm_result = self.comm_agent.evaluate_corridor_capacity(
            geo_payload=geo_result, 
            escort_strength=active_escort_strength
        )

        # --- SCENARIO DAG WIRING START ---
        # Compute shortfall safely (falling back to 100.0 if max_capacity isn't explicitly defined as an attribute)
        max_cap = getattr(self.comm_agent, "max_capacity", comm_result.get("initial_capacity", 100.0))
        final_cap = comm_result.get("final_capacity", 0.0)
        
        capacity_shortfall_pct = (max_cap - final_cap) / max_cap if max_cap > 0 else 1.0
        macro_impacts = estimate_macro_impacts(capacity_shortfall_pct)
        # --- SCENARIO DAG WIRING END ---
        
        # 4. HMM Integration: Encode Observation
        current_observation = ObservationEncoder.encode(geo_result, comm_result, evidence_cards)
        observation_history = [current_observation] 
        
        # 4. Fixed HMM Decoding: Call it on the new rag_agent
        inferred_states, path_confidence = self.rag_agent.decode_corridor_sequence(observation_history)
        current_state = inferred_states[-1] if inferred_states else "NORMAL"
        
        # 5. Establish Confidence Bands
        geo_band = self._calculate_confidence_band(geo_prob)
        logistics_band = "CRITICAL" if comm_result.get("is_critical") else "STABLE"
        
        evidence_count = len(evidence_cards) if isinstance(evidence_cards, list) else 1
        system_confidence = self._calculate_system_confidence(
            geo_band=geo_band, 
            logistics_band=logistics_band, 
            evidence_count=evidence_count, 
            data_freshness=1.0 
        )
        
        # 6. Disagreement Logic & Escalation Routing
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

        # 7. Structured Reasoning Trail
        math_context = comm_result.get("mathematical_context", {})
        
        reasoning_trail = {
            "bayesian_evidence": {
                "posterior": geo_prob,
                "confidence_band": geo_band,
                "extracted_signals": evidence_cards
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
        
        # 8. Package results directly for Sprint 5's Digital Twin UI mapping
        context.metadata["agent_analysis"] = {
            "current_hidden_state": current_state,
            "historical_state_trajectory": inferred_states,
            "viterbi_confidence": path_confidence,
            "evidence_cards": evidence_cards,
            "geo": geo_result,
            "comm": comm_result,
            "macro_impacts": macro_impacts,  # <-- Added the DAG macro impacts here
            "escalation_status": escalation_flag,
            "reasoning_trail": reasoning_trail
        }
        
        # 9. Graph Snapshot Setup
        context.graph_snapshot = self.canonical_graph.snapshot()
        context.graph_snapshot.update_corridor_risk(
            corridor_id=geo_result["corridor_id"], 
            posterior_probability=geo_prob
        )
        
        # 10. Monte Carlo Engine
        self.mc_engine.run(context)
        
        # --- NEW SPR WIRING ---
        shortfall_mbd = context.monte_carlo_results.expected_shortfall_mbd
        
        # Run the newly fixed calculation
        spr_readout = self.spr_agent.calculate_replenishment_window(
            daily_shortfall_mmbbl=shortfall_mbd
        )
        
        # Attach it to the agent_analysis dictionary so the UI can display it
        context.metadata["agent_analysis"]["spr_readout"] = spr_readout
        # ----------------------
        
        # 11. Optimization Engine
        snapshot = context.graph_snapshot
        
        # We need to construct a dict with "nodes" and "edges" for the LP module
        if hasattr(snapshot, "to_dict"):
            graph_dict = snapshot.to_dict()
        else:
            # GraphSnapshot likely wraps a NetworkX graph (usually .graph, .G, or .network)
            nx_graph = getattr(snapshot, 'graph', getattr(snapshot, 'G', getattr(snapshot, 'network', None)))
            
            if nx_graph is None:
                # If we still can't find it, log the available attributes so we can see exactly what is inside
                logger.error(f"GraphSnapshot attributes: {dir(snapshot)}")
                raise RuntimeError(f"Could not find the NetworkX graph inside GraphSnapshot. Available attributes: {dir(snapshot)}")
                
            # Unpack the NetworkX graph into the exact dictionary shape the LP expects
            graph_dict = {
                "nodes": [{"id": n, **d} for n, d in nx_graph.nodes(data=True)],
                "edges": [{"source": u, "target": v, **d} for u, v, d in nx_graph.edges(data=True)]
            }

        raw_routes = optimize_procurement(
            graph_data=graph_dict,
            disrupted_corridor=geo_result["corridor_id"],
            risk_posterior=geo_prob
        )
        # Convert raw dictionaries to Pydantic models (falling back securely if LP returns dicts or objects)
        context.procurement_alternatives = [
            ProcurementAlternative(**route) if isinstance(route, dict) else route 
            for route in raw_routes
        ]
        # --- PROCUREMENT LP WIRING END ---
        
        # Explicit teardown
        context.graph_snapshot = None 

        return context