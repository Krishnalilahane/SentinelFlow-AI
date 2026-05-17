from rag.retriever import PolicyRetriever


class PolicyService:
    def __init__(self) -> None:
        self.retriever = PolicyRetriever()

    def search_policies(self, query: str, top_k: int = 3) -> list[dict]:
        return self.retriever.search(query=query, top_k=top_k)