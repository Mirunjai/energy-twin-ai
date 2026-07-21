from rag.vector_store import CaseStudyVectorStore

class EvidenceRetriever:
    def __init__(self):
        self.store = CaseStudyVectorStore()

    def retrieve_analogues(self, query_text, n_results=1):
        """
        Retrieves historical analogues and formats them as Evidence Cards.
        """
        results = self.store.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        evidence_cards = []
        
        # Guard clause if DB is empty
        if not results['documents'] or not results['documents'][0]:
            return evidence_cards

        # Unpack Chroma's output structure
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] # Lower distance = higher similarity
        
        for doc, meta, dist in zip(documents, metadatas, distances):
            # Convert L2 distance to a mock similarity score (0.0 to 1.0)
            similarity = max(0.0, 1.0 - (dist / 2.0)) 
            
            card = {
                "title": meta.get("title", "Historical Analogue"),
                "similarity_score": round(similarity, 2),
                "summary": doc,
                "citation": meta.get("citation", "Unknown Source"),
                "metadata": {
                    "corridor": meta.get("corridor"),
                    "threat": meta.get("threat")
                }
            }
            evidence_cards.append(card)
            
        return evidence_cards