import networkx as nx
import logging
from typing import List, Dict, Any
from config.settings import settings

logger = logging.getLogger("energy_twin.backend.graph_snapshot")

class GraphSnapshot:
    def __init__(self, G: nx.DiGraph):
        self.G = G

    def update_corridor_risk(self, corridor_id: str, posterior_probability: float):
        if corridor_id not in self.G:
            logger.warning(f"Target corridor '{corridor_id}' not found in snapshot topology.")
            return
            
        self.G.nodes[corridor_id]["current_risk_prob"] = posterior_probability
        
        alpha = settings.graph_weights.get("alpha", 1.0)
        beta = settings.graph_weights.get("beta", 0.5)
        
        for u, v, data in self.G.edges(data=True):
            if u == corridor_id or v == corridor_id:
                base = data.get("base_risk_weight", 0.0)
                data["dynamic_risk_weight"] = (alpha * base) + (beta * posterior_probability)

    def reset_dynamic_state(self):
        """
        Note: Currently unused as snapshots are discarded per-request.
        Retained for future Monte Carlo batching or persistent scenario reuse.
        """
        for node, data in self.G.nodes(data=True):
            data.pop("current_risk_prob", None)
        for u, v, data in self.G.edges(data=True):
            data.pop("dynamic_risk_weight", None)

    def get_optimal_reroutes(self, source: str, target: str, top_k: int = 3) -> List[Dict[str, Any]]:
        risk_weight = settings.graph_weights.get("risk", 1000.0)
        distance_weight = settings.graph_weights.get("distance", 0.1)

        def edge_cost(u, v, data):
            risk = data.get("dynamic_risk_weight", data.get("base_risk_weight", 0.0))
            distance = data.get("distance_nm", 1.0)
            return (risk * risk_weight) + (distance * distance_weight)

        try:
            path_generator = nx.shortest_simple_paths(self.G, source, target, weight=edge_cost)
            
            routes = []
            for i, path in enumerate(path_generator):
                if i >= top_k:
                    break
                    
                total_risk = sum(self.G[u][v].get("dynamic_risk_weight", self.G[u][v].get("base_risk_weight", 0.0)) for u, v in zip(path[:-1], path[1:]))
                total_distance = sum(self.G[u][v].get("distance_nm", 0) for u, v in zip(path[:-1], path[1:]))
                
                # Raw numerical output only
                estimated_cost = total_distance * 1500.0
                
                routes.append({
                    "path_nodes": path,
                    "cumulative_risk": round(total_risk, 4),
                    "total_distance_nm": total_distance,
                    "estimated_cost_delta_per_day": estimated_cost
                })
                
            return routes
            
        except nx.NetworkXNoPath:
            logger.warning(f"Network isolated: No path exists between {source} and {target}")
            return []