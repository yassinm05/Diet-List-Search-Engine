from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import List, Dict, Any


import chromadb
from sentence_transformers import SentenceTransformer

from chunker import chunk_corpus


PROJECT_ROOT    = Path(__file__).resolve().parents[3]
SCRAPPED_JSON   = PROJECT_ROOT / "data" / "scientific_diets.json"
CHROMA_DB_PATH  = PROJECT_ROOT / "data" / "chroma_db"  # folder where ChromaDB persists data
COLLECTION_NAME = "diet_documents"


MODEL_NAME  = "BAAI/bge-small-en-v1.5"
MAX_TOKENS  = 400    # chunk window  (tokens)
STRIDE      = 200    # sliding step  (50 % overlap)
BATCH_SIZE  = 64     # embedding batch — increase if you have a GPU



def load_corpus(path) -> List[Dict[str, Any]]:
    """Load and validate the scrapped JSON corpus."""
    corpus_path = Path(path) if not isinstance(path, Path) else path
    if not corpus_path.exists():
        sys.exit(f"[ERROR] Corpus file not found: {corpus_path}")

    with corpus_path.open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    # Accept both a plain list and {"documents": [...]} wrapper
    if isinstance(corpus, dict) and "documents" in corpus:
        corpus = corpus["documents"]

    required_keys = {"DocID", "Title", "URL", "Text"}
    for i, doc in enumerate(corpus):
        missing = required_keys - set(doc.keys())
        if missing:
            sys.exit(f"[ERROR] Document #{i} is missing keys: {missing}")

    print(f"[✓] Loaded {len(corpus)} documents from '{corpus_path}'")
    return corpus


def build_index(
    corpus_path = SCRAPPED_JSON,
    rebuild: bool = False,
) -> None:
    

    
    corpus = load_corpus(corpus_path)

    
    print(f"[*] Loading embedding model '{MODEL_NAME}' …")
    t0    = time.time()
    model = SentenceTransformer(MODEL_NAME)
    print(f"[✓] Model loaded in {time.time() - t0:.1f}s")

    
    print(f"[*] Chunking corpus  (window={MAX_TOKENS}, stride={STRIDE}) …")
    t0     = time.time()
    chunks = chunk_corpus(corpus, model.tokenizer, MAX_TOKENS, STRIDE)
    print(
        f"[✓] {len(chunks)} chunks created from {len(corpus)} docs "
        f"in {time.time() - t0:.1f}s  "
        f"(avg {len(chunks)/len(corpus):.1f} chunks/doc)"
    )

    
    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

    if rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"[*] Dropped existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass  # collection didn't exist yet

    # cosine space → distances returned as (1 - cosine_similarity)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    existing_count = collection.count()
    if existing_count > 0 and not rebuild:
        print(
            f"[!] Collection already has {existing_count} entries. "
            f"Use --rebuild to recreate it. Exiting."
        )
        return

   
    texts     = [c["text"]      for c in chunks]
    ids       = [c["chunk_id"]  for c in chunks]
    metadatas = [
        {
            "doc_id"     : c["doc_id"],       # int → stored as int
            "doc_title"  : c["doc_title"],
            "doc_url"    : c["doc_url"],
            "chunk_index": c["chunk_index"],
            "start_token": c["start_token"],
            "end_token"  : c["end_token"],
            "token_count": c["token_count"],
        }
        for c in chunks
    ]

    print(f"[*] Embedding {len(texts)} chunks (batch_size={BATCH_SIZE}) …")
    t0 = time.time()

    
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,   # unit-norm → cosine sim = dot product
        convert_to_numpy=True,
    ).tolist()

    elapsed = time.time() - t0
    print(f"[✓] Embedding done in {elapsed:.1f}s  ({len(texts)/elapsed:.0f} chunks/s)")

    # ── 6. Add to ChromaDB (in batches to avoid memory spikes) ───────────────
    CHROMA_BATCH = 512  # ChromaDB recommends ≤5461 per call
    print(f"[*] Writing to ChromaDB …")
    t0 = time.time()

    for i in range(0, len(chunks), CHROMA_BATCH):
        collection.add(
            ids        = ids[i : i + CHROMA_BATCH],
            embeddings = embeddings[i : i + CHROMA_BATCH],
            documents  = texts[i : i + CHROMA_BATCH],
            metadatas  = metadatas[i : i + CHROMA_BATCH],
        )

    print(f"[✓] ChromaDB write done in {time.time() - t0:.1f}s")

   
    final_count = collection.count()
    print("\n══════════════ INDEX SUMMARY ══════════════")
    print(f"  Collection  : {COLLECTION_NAME}")
    print(f"  Stored at   : {CHROMA_DB_PATH.resolve()}")
    print(f"  Documents   : {len(corpus)}")
    print(f"  Chunks      : {final_count}")
    print(f"  Model       : {MODEL_NAME}")
    print(f"  Chunk size  : {MAX_TOKENS} tokens  |  Stride: {STRIDE} tokens")
    print(f"  Overlap     : {MAX_TOKENS - STRIDE} tokens  ({(MAX_TOKENS-STRIDE)/MAX_TOKENS*100:.0f}%)")
    print("═══════════════════════════════════════════\n")
    print("[✓] Phase 1 complete — index is ready for semantic search.\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build ChromaDB semantic index")
    parser.add_argument("--json",    default=str(SCRAPPED_JSON), help="Path to scientific_diets.json")
    parser.add_argument("--rebuild", action="store_true",   help="Drop and recreate index")
    args = parser.parse_args()

    build_index(corpus_path=args.json, rebuild=args.rebuild)
