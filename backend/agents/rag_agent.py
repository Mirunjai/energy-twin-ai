# backend/agents/rag_agent.py
import numpy as np
import logging
from rag.retriever import EvidenceRetriever

logger = logging.getLogger("energy_twin.backend.rag_agent")

class Observation:
    def __init__(self, bayes_posterior, ais_diversion, insurance_spike, price_volatility, rag_score):
        self.bayes_posterior = float(bayes_posterior)
        self.ais_diversion = float(ais_diversion)
        self.insurance_spike = bool(insurance_spike)
        self.price_volatility = float(price_volatility)
        self.rag_score = float(rag_score)

class ObservationEncoder:
    @staticmethod
    def encode(geo_result, comm_result, rag_cards):
        top_rag_score = rag_cards[0]["similarity_score"] if rag_cards else 0.0
        logistics = comm_result.get("logistics_signals", {})
        return Observation(
            bayes_posterior=geo_result.get("posterior_probability", 0.0),
            ais_diversion=logistics.get("ais_diversion_rate", 0.0),
            insurance_spike=logistics.get("insurance_premium_spike", False),
            price_volatility=logistics.get("brent_wti_spread_volatility", 0.0),
            rag_score=top_rag_score
        )

class RAGIntelligenceAgent:  # Formerly HMMAgent
    def __init__(self):
        self.states = ["NORMAL", "MONITORING", "ELEVATED", "CRITICAL"]
        self.n_states = len(self.states)
        self.A = np.array([
            [0.85, 0.15, 0.00, 0.00],
            [0.10, 0.70, 0.20, 0.00],
            [0.00, 0.15, 0.65, 0.20],
            [0.00, 0.00, 0.30, 0.70]
        ])
        self.pi = np.array([0.70, 0.20, 0.10, 0.00])

    def _calculate_emission_log_probs(self, obs: Observation):
        log_emissions = np.zeros(self.n_states)
        for i, state in enumerate(self.states):
            score = 0.0
            if state == "NORMAL":
                score += (1.0 - obs.bayes_posterior) * 3 + (1.0 - obs.ais_diversion) * 2 - (3 if obs.insurance_spike else 0)
            elif state == "MONITORING":
                score += obs.bayes_posterior * 1.5 + obs.price_volatility * 1.5
            elif state == "ELEVATED":
                score += obs.bayes_posterior * 3 + obs.ais_diversion * 2 + (2 if obs.insurance_spike else 0) + obs.rag_score * 2
            elif state == "CRITICAL":
                score += obs.bayes_posterior * 5 + obs.ais_diversion * 4 + (4 if obs.insurance_spike else 0) + obs.rag_score * 3
            log_emissions[i] = np.log(max(1e-6, score + 1.0))
        return log_emissions

    def decode_corridor_sequence(self, observation_history):
        T = len(observation_history)
        if T == 0: return [], 0.0
        viterbi_matrix = np.zeros((self.n_states, T))
        backpointers = np.zeros((self.n_states, T), dtype=int)
        
        log_b = self._calculate_emission_log_probs(observation_history[0])
        for s in range(self.n_states):
            viterbi_matrix[s, 0] = np.log(max(1e-6, self.pi[s])) + log_b[s]
            
        for t in range(1, T):
            log_b = self._calculate_emission_log_probs(observation_history[t])
            for s in range(self.n_states):
                log_transitions = viterbi_matrix[:, t - 1] + np.log(max(1e-6, self.A[:, s]))
                backpointers[s, t] = np.argmax(log_transitions)
                viterbi_matrix[s, t] = log_transitions[backpointers[s, t]] + log_b[s]
                
        best_path = np.zeros(T, dtype=int)
        best_path[T - 1] = np.argmax(viterbi_matrix[:, T - 1])
        path_p = viterbi_matrix[best_path[T - 1], T - 1]
        
        for t in range(T - 2, -1, -1):
            best_path[t] = backpointers[best_path[t + 1], t + 1]
            
        return [self.states[idx] for idx in best_path], float(np.exp(path_p))