import json
import os
import networkx as nx
import logging

logger = logging.getLogger("energy_twin.backend.graph_loader")

def load_supply_network(filepath: str = "data/supply_network.json") -> nx.DiGraph:
    G = nx.DiGraph()
    
    if not os.path.exists(filepath):
        logger.error(f"Network dataset not found at {filepath}")
        raise FileNotFoundError(f"Missing canonical graph dataset: {filepath}")
        
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    node_ids = set()
    
    # 1. Non-destructive node validation and insertion
    for node in data.get("nodes", []):
        if "id" not in node or "type" not in node:
            raise ValueError(f"Node missing required attributes 'id' or 'type': {node}")
            
        node_id = node["id"]
        if node_id in node_ids:
            raise ValueError(f"Duplicate node ID found in dataset: {node_id}")
            
        node_ids.add(node_id)
        attributes = {k: v for k, v in node.items() if k != "id"}
        G.add_node(node_id, **attributes)
        
    # 2. Non-destructive edge validation and insertion
    for edge in data.get("edges", []):
        if "source" not in edge or "target" not in edge:
            raise ValueError(f"Edge missing 'source' or 'target': {edge}")
            
        source = edge["source"]
        target = edge["target"]
        
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"Edge references invalid or orphaned node: {source} -> {target}")
            
        attributes = {k: v for k, v in edge.items() if k not in ("source", "target")}
        G.add_edge(source, target, **attributes)
        
    logger.info(
        "Loaded and validated canonical supply network",
        extra={"nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
    )
    return G