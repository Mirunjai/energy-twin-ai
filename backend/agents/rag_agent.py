"""Retrieval and state-estimation boilerplate."""

import chromadb
import numpy as np
from hmmlearn.hmm import GaussianHMM


def create_hmm_model(n_components: int = 2) -> GaussianHMM:
    """Initialize a default Hidden Markov Model for scenario state inference."""
    return GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=100)


def create_chroma_client(path: str = ".chroma") -> chromadb.PersistentClient:
    """Create a local persistent ChromaDB client for agent memory."""
    return chromadb.PersistentClient(path=path)


def warm_start_hmm(model: GaussianHMM) -> GaussianHMM:
    """Fit with placeholder samples so local development can run immediately."""
    seed_data = np.array([[0.1], [0.3], [0.8], [0.6], [0.2]])
    model.fit(seed_data)
    return model
