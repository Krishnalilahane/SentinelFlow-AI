from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


POLICY_DIR = BASE_DIR / "rag" / "policy_documents"
VECTOR_STORE_DIR = BASE_DIR / "rag" / "vector_store"

COLLECTION_NAME = "sentinelflow_policy_knowledge"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_policy_documents() -> list[dict]:
    documents = []

    markdown_files = sorted(POLICY_DIR.glob("*.md"))

    if not markdown_files:
        raise FileNotFoundError(f"No markdown policy files found in: {POLICY_DIR}")

    for file_path in markdown_files:
        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        documents.append(
            {
                "source_file": file_path.name,
                "policy_name": file_path.stem.replace("_", " ").title(),
                "content": content,
            }
        )

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n- ", "\n\n", "\n", ". ", " "],
    )

    chunks = []

    for document in documents:
        split_texts = splitter.split_text(document["content"])

        for index, chunk_text in enumerate(split_texts):
            clean_chunk = chunk_text.strip()

            if not clean_chunk:
                continue

            chunks.append(
                {
                    "id": f"{document['source_file']}::chunk_{index}",
                    "text": clean_chunk,
                    "metadata": {
                        "source_file": document["source_file"],
                        "policy_name": document["policy_name"],
                        "chunk_index": index,
                    },
                }
            )

    return chunks


def create_vector_store(chunks: list[dict]) -> None:
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [chunk["id"] for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True,
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print("Vector store ingestion completed successfully.")
    print(f"Collection name: {COLLECTION_NAME}")
    print(f"Chunks stored or updated: {len(chunks)}")
    print(f"Vector store path: {VECTOR_STORE_DIR}")


def main() -> None:
    documents = load_policy_documents()
    chunks = chunk_documents(documents)

    print(f"Policy documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")

    create_vector_store(chunks)


if __name__ == "__main__":
    main()