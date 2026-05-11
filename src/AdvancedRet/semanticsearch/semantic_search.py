from __future__ import annotations

from typing import List, Dict, Any, Literal
from pathlib import Path
import os

import chromadb
from sentence_transformers import SentenceTransformer


MODEL_NAME      = "BAAI/bge-small-en-v1.5"
PROJECT_ROOT    = Path(__file__).resolve().parents[3]  # Navigate to project root
CHROMA_DB_PATH  = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "diet_documents"

# BGE instruction prefix — used only at query time, not during indexing
BGE_QUERY_PREFIX = "Represent this sentence for searching relevant passages: "



_model:      SentenceTransformer | None = None
_collection: chromadb.Collection | None = None


def _load_resources() -> tuple[SentenceTransformer, chromadb.Collection]:
    """Lazy-load the model and ChromaDB collection (once per process)."""
    global _model, _collection

    if _model is None:
        print(f"[SemanticSearch] Loading model '{MODEL_NAME}' …", flush=True)
        _model = SentenceTransformer(MODEL_NAME)

    if _collection is None:
        if not CHROMA_DB_PATH.exists():
            raise FileNotFoundError(
                f"ChromaDB not found at '{CHROMA_DB_PATH}'. "
                f"Run phase1_build_index.py first."
            )
        client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        _collection = client.get_collection(COLLECTION_NAME)

    return _model, _collection



def semantic_search(
    query: str,
    top_k_chunks: int = 20,
    top_k_docs:   int = 5,
    pooling: Literal["max", "avg"] = "max",
    score_threshold: float = 0.0,
) -> List[Dict[str, Any]]:
    
    if not query or not query.strip():
        return []

    model, collection = _load_resources()

    
    query_text = BGE_QUERY_PREFIX + query.strip()
    query_vec  = model.encode(
        query_text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).tolist()

    
    # n_results capped at total collection size to avoid errors on small indexes
    n_results = min(top_k_chunks, collection.count())

    raw = collection.query(
        query_embeddings=[query_vec],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # raw["distances"][0] → cosine *distances* (lower = more similar)
    # Convert: cosine_similarity = 1 − cosine_distance
    chunk_scores  = [1.0 - d for d in raw["distances"][0]]
    chunk_docs    = raw["documents"][0]
    chunk_metas   = raw["metadatas"][0]

   
    doc_score_lists : Dict[int, List[float]] = {}
    doc_best_chunk  : Dict[int, str]         = {}
    doc_metadata    : Dict[int, Dict]        = {}

    for score, text, meta in zip(chunk_scores, chunk_docs, chunk_metas):
        doc_id = meta["doc_id"]

        if doc_id not in doc_score_lists:
            doc_score_lists[doc_id] = []
            doc_best_chunk[doc_id]  = text
            doc_metadata[doc_id]    = meta

        doc_score_lists[doc_id].append(score)

        # Track the best-scoring chunk for snippet display
        if score > max(doc_score_lists[doc_id][:-1], default=0):
            doc_best_chunk[doc_id] = text

    # Apply pooling
    doc_final_scores: Dict[int, float] = {}
    for doc_id, scores in doc_score_lists.items():
        if pooling == "max":
            doc_final_scores[doc_id] = max(scores)
        else:  # avg
            doc_final_scores[doc_id] = sum(scores) / len(scores)

    
    ranked = sorted(doc_final_scores.items(), key=lambda x: x[1], reverse=True)

    results: List[Dict[str, Any]] = []
    for doc_id, score in ranked:
        if score < score_threshold:
            continue
        if len(results) >= top_k_docs:
            break

        meta = doc_metadata[doc_id]
        results.append(
            {
                "doc_id"     : doc_id,
                "title"      : meta["doc_title"],
                "url"        : meta["doc_url"],
                "score"      : round(score, 4),
                "best_chunk" : doc_best_chunk[doc_id],
                "chunk_count": len(doc_score_lists[doc_id]),
            }
        )

    return results



def search_for_tkinter(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Thin wrapper with the same signature expected by your Tkinter search handler.
    Returns a list of result dicts with 'title', 'url', 'score', 'snippet'.
    """
    raw_results = semantic_search(query, top_k_chunks=top_k * 4, top_k_docs=top_k)

    # Rename 'best_chunk' → 'snippet' for UI convenience
    return [
        {
            "doc_id" : r["doc_id"],
            "title"  : r["title"],
            "url"    : r["url"],
            "score"  : r["score"],
            "snippet": r["best_chunk"][:300] + "…" if len(r["best_chunk"]) > 300 else r["best_chunk"],
        }
        for r in raw_results
    ]



if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "low sodium diet for blood pressure"
    print(f"\n🔍 Query: \"{query}\"\n")

    results = semantic_search(query, top_k_chunks=20, top_k_docs=5)

    if not results:
        print("No results found.")
    else:
        print(f"{'Rank':<5} {'Score':<8} {'DocID':<7} {'Title'}")
        print("─" * 70)
        for rank, r in enumerate(results, 1):
            print(f"{rank:<5} {r['score']:<8.4f} {r['doc_id']:<7} {r['title']}")
            print(f"      Snippet: {r['best_chunk'][:120].strip()} …")
            print()
