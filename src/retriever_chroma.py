from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from src.config import CONFIG


CHROMA_DIR = Path(
    CONFIG["paths"].get(
        "chroma_store",
        "data/vector_store/chroma_db",
    )
)

COLLECTION_NAME = CONFIG["retrieval"].get(
    "collection_name",
    "pizza_menu",
)


def chunk_to_document(chunk):
    return " ".join([
        chunk.get("id", ""),
        chunk.get("type", ""),
        chunk.get("category", ""),
        chunk.get("name", ""),
        chunk.get("text", ""),
    ])


def get_embedding_model_name(model_name=None):
    if model_name is None:
        model_name = CONFIG["retrieval"]["embedding_model"]

    return model_name


def build_chroma_collection(
    chunks,
    persist_dir=CHROMA_DIR,
    collection_name=COLLECTION_NAME,
    model_name=None,
):
    model_name = get_embedding_model_name(model_name)

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name=model_name,
        device=CONFIG["retrieval"].get("embedding_device", "cpu"),
        normalize_embeddings=CONFIG["retrieval"].get("normalize_embeddings", True),
    )

    persist_dir = Path(persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(persist_dir))

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={
            "hnsw:space": CONFIG["retrieval"].get(
                "chroma_distance_metric",
                "cosine",
            )
        },
    )

    ids = [chunk["id"] for chunk in chunks]

    documents = [
        chunk_to_document(chunk)
        for chunk in chunks
    ]

    metadatas = [
        {
            "type": chunk.get("type", ""),
            "category": chunk.get("category", ""),
            "name": chunk.get("name", ""),
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return collection


def get_chroma_collection(
    persist_dir=CHROMA_DIR,
    collection_name=COLLECTION_NAME,
    model_name=None,
):
    model_name = get_embedding_model_name(model_name)

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name=model_name,
        device=CONFIG["retrieval"].get("embedding_device", "cpu"),
        normalize_embeddings=CONFIG["retrieval"].get(
            "normalize_embeddings",
            True,
        ),
    )

    client = chromadb.PersistentClient(path=str(persist_dir))

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
    )

    return collection


def retrieve_with_chroma(
    query,
    chunks,
    top_k=None,
    persist_dir=CHROMA_DIR,
    collection_name=COLLECTION_NAME,
    model_name=None,
):
    if top_k is None:
        top_k = CONFIG["retrieval"].get("top_k", 3)

    similarity_threshold = CONFIG["retrieval"].get(
        "similarity_threshold",
        0.0,
    )

    collection = get_chroma_collection(
        persist_dir=persist_dir,
        collection_name=collection_name,
        model_name=model_name,
    )

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["distances"],
    )

    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunk_lookup = {
        chunk["id"]: chunk
        for chunk in chunks
    }

    retrieved_chunks = []

    for chunk_id, distance in zip(ids, distances):
        similarity = 1 - distance

        if similarity < similarity_threshold:
            continue

        if chunk_id in chunk_lookup:
            chunk = dict(chunk_lookup[chunk_id])
            chunk["retrieval_distance"] = distance
            chunk["retrieval_similarity"] = similarity
            retrieved_chunks.append(chunk)

    return retrieved_chunks