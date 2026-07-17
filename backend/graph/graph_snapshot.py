import networkx as nx
import logging
from typing import List, Dict, Any

logger = logging.getLogger("energy_twin.backend.graph_snapshot")

class GraphSnapshot:
    def __init__(self, G: nx.DiGraph):
        self.G = G

    def update_corridor_risk(self, corridor_id: str, posterior_probability: float):
        """
        Injects the dynamic geopolitical posterior into the snapshot using a 
        bounded composite risk model to prevent compounding inflation.
        """
        if corridor_id not in self.G:
            logger.warning(f"Target corridor '{corridor_id}' not found in snapshot topology.")
            return
            
        self.G.nodes[corridor_id]["current_risk_prob"] = posterior_probability
        
        # Risk Model Constants (α for structural base, β for dynamic injection)
        alpha = 1.0
        beta = 0.5 
        
        for u, v, data in self.G.edges(data=True):
            if u == corridor_id or v == corridor_id:
                base = data.get("base_risk_weight", 0.0)
                data["dynamic_risk_weight"] = (alpha * base) + (beta * posterior_probability)
                
        logger.info(
            f"Snapshot updated: Injected dynamic risk ({posterior_probability}) into '{corridor_id}' edges"
        )

    def get_optimal_reroutes(self, source: str, target: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Calculates alternatives by generating a dynamic composite score for routing 
        that balances risk, distance, and transit time.
        """
        # Dynamically compute composite score across all edges
        for u, v, data in self.G.edges(data=True):
            risk = data.get("dynamic_risk_weight", data.get("base_risk_weight", 0.0))
            distance = data.get("distance_nm", 1.0)
            
            # Composite optimization function (arbitrary weights for demo balancing)
            data["composite_score"] = (risk * 1000) + (distance * 0.1)

        try:
            path_generator = nx.shortest_simple_paths(self.G, source, target, weight="composite_score")
            
            routes = []
            for i, path in enumerate(path_generator):
                if i >= top_k:
                    break
                    
                total_risk = sum(self.G[u][v].get("dynamic_risk_weight", self.G[u][v].get("base_risk_weight", 0.0)) for u, v in zip(path[:-1], path[1:]))
                total_distance = sum(self.G[u][v].get("distance_nm", 0) for u, v in zip(path[:-1], path[1:]))
                
                routes.append({
                    "path_nodes": path,
                    "cumulative_risk": round(total_risk, 4),
                    "total_distance_nm": total_distance
                })
                
            return routes
            
        except nx.NetworkXNoPath:
            logger.warning(f"Network isolated: No path exists between {source} and {target}")
            return []