import networkx as nx
import logging
from graph.graph_loader import load_supply_network
from graph.graph_snapshot import GraphSnapshot

logger = logging.getLogger("energy_twin.backend.network_graph")

class SupplyChainGraph:
    def __init__(self, data_path: str = "data/supply_network.json"):
        # The immutable canonical structure loaded directly into memory
        self._canonical_G = load_supply_network(data_path)
        logger.info("Canonical supply network loaded and locked. Ready for snapshotting.")

    def snapshot(self) -> GraphSnapshot:
        """
        Returns a mutable, isolated deep copy of the graph for a single simulation run.
        """
        return GraphSnapshot(self._canonical_G.copy())