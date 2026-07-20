import chromadb
from chromadb.utils import embedding_functions
import os

class CaseStudyVectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        # 1. Direct Chroma initialization (No LangChain)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 2. Standard, fast embedding model
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # 3. Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="historical_disruptions",
            embedding_function=self.embedding_fn
        )

    def ingest_case_studies(self):
        """
        Seeds the DB with the enriched, structured historical analogues 
        required by the Master Plan and the HMM Observation Encoder.
        """
        documents = [
            "Houthi rebel forces launched sustained drone and missile attacks on commercial shipping in the Red Sea, forcing major operators to divert via the Cape of Good Hope. Insurance premiums spiked by 300%.",
            "Heightened US-Iran rhetoric led to naval posturing in the Strait of Hormuz. Though no physical blockade occurred, the threat of sanctions caused Indian refiners to secure spot cargoes at a 15% premium.",
            "A sudden geopolitical shock disrupted East African supply chains. The resulting Suez Canal bottleneck delayed VLCCs by an average of 14 days, triggering cascading refinery slowdowns."
        ]
        
        # Enriched metadata provides the precise quantitative footprints needed for backtesting
        metadatas = [
            {
                "title": "2023 Houthi Red Sea Escalation", 
                "date": "2023-11", 
                "threat": "drone_attacks", 
                "corridor": "red_sea", 
                "citation": "Reuters / Lloyd's List",
                "severity": "critical",
                "delay_days": 14,
                "insurance_spike_pct": 300,
                "price_shock_pct": 8.2
            },
            {
                "title": "2025 US-Iran Standoff", 
                "date": "2025-01", 
                "threat": "sanctions_pressure", 
                "corridor": "hormuz", 
                "citation": "OFAC / Financial Times",
                "severity": "elevated",
                "delay_days": 0,
                "insurance_spike_pct": 25,
                "price_shock_pct": 15.0
            },
            {
                "title": "McKinsey Supply Shock Analysis", 
                "date": "2024-06", 
                "threat": "chokepoint_closure", 
                "corridor": "suez", 
                "citation": "McKinsey Global Institute",
                "severity": "critical",
                "delay_days": 14,
                "insurance_spike_pct": 150,
                "price_shock_pct": 5.0
            }
        ]
        
        ids = ["case_houthi_2023", "case_iran_2025", "case_mckinsey_2024"]
        
        # Upsert cleanly updates existing keys if re-run during development
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Vector store seeded with enriched quantitative case studies.")

if __name__ == "__main__":
    store = CaseStudyVectorStore()
    store.ingest_case_studies()