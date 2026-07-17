"""Supply-chain network graph setup."""

import networkx as nx


def build_supply_chain_graph() -> nx.DiGraph:
    """Create a baseline directed graph of source, chokepoint, and destination nodes."""
    graph = nx.DiGraph()
    graph.add_edge("Persian Gulf", "Strait of Hormuz", capacity=18.0)
    graph.add_edge("Strait of Hormuz", "Indian Refineries", capacity=15.0)
    graph.add_edge("Russian Ports", "Indian Refineries", capacity=4.0)
    return graph
