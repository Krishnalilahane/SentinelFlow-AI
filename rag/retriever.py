from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import chromadb
from sentence_transformers import SentenceTransformer


VECTOR_STORE_DIR = BASE_DIR / "rag" / "vector_store"

COLLECTION_NAME = "sentinelflow_policy_knowledge"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class PolicyRetriever:
    def __init__(self) -> None:
        if not VECTOR_STORE_DIR.exists():
            raise FileNotFoundError(
                f"Vector store not found at {VECTOR_STORE_DIR}. "
                "Run python rag\\ingest.py first."
            )

        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
        self.collection = self.client.get_collection(name=COLLECTION_NAME)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if top_k < 1:
            top_k = 1

        if top_k > 10:
            top_k = 10

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        ).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted_results = []

        for document, metadata, distance in zip(documents, metadatas, distances):
            relevance_score = 1 / (1 + float(distance))

            formatted_results.append(
                {
                    "source_file": metadata.get("source_file"),
                    "policy_name": metadata.get("policy_name"),
                    "chunk_text": document,
                    "relevance_score": round(relevance_score, 4),
                }
            )

        return formatted_results


def main() -> None:
    retriever = PolicyRetriever()

    query = "new device login and suspicious transaction"
    results = retriever.search(query=query, top_k=3)

    print(f"Query: {query}")
    print(f"Results returned: {len(results)}")
    print("-" * 80)

    for index, result in enumerate(results, start=1):
        print(f"Result {index}")
        print(f"Policy: {result['policy_name']}")
        print(f"Source: {result['source_file']}")
        print(f"Score: {result['relevance_score']}")
        print(result["chunk_text"])
        print("-" * 80)


if __name__ == "__main__":
    main()