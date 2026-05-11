from __future__ import annotations
from typing import List, Dict, Any


def chunk_document(
    text: str,
    tokenizer,
    max_tokens: int = 400,
    stride: int = 200,
) -> List[Dict[str, Any]]:
    
    if not text or not text.strip():
        return []

    # ── 1. Tokenise the entire document (no special tokens so we count content only)
    token_ids: List[int] = tokenizer.encode(text, add_special_tokens=False)
    total_tokens = len(token_ids)

    if total_tokens == 0:
        return []

    chunks: List[Dict[str, Any]] = []
    start = 0

    while start < total_tokens:
        end = min(start + max_tokens, total_tokens)

        # ── 2. Decode this window back to a readable string
        chunk_tokens = token_ids[start:end]
        chunk_text: str = tokenizer.decode(chunk_tokens, skip_special_tokens=True)

        chunks.append(
            {
                "text": chunk_text.strip(),
                "chunk_index": len(chunks),
                "start_token": start,
                "end_token": end,
                "token_count": end - start,
            }
        )

        # ── 3. If we just processed the final tokens, stop
        if end == total_tokens:
            break

        # ── 4. Advance by stride (not by max_tokens) to create overlap
        start += stride

    return chunks


def chunk_corpus(
    corpus: List[Dict[str, Any]],
    tokenizer,
    max_tokens: int = 400,
    stride: int = 200,
    title_prefix: bool = True,
) -> List[Dict[str, Any]]:
    
    all_chunks: List[Dict[str, Any]] = []

    for doc in corpus:
        doc_id    = doc["DocID"]
        title     = doc.get("Title", "")
        url       = doc.get("URL", "")
        raw_text  = doc.get("Text", "")

        # Optionally prepend title for richer chunk context
        full_text = f"{title}\n\n{raw_text}" if title_prefix else raw_text

        doc_chunks = chunk_document(full_text, tokenizer, max_tokens, stride)

        for chunk in doc_chunks:
            chunk.update(
                {
                    "doc_id"     : doc_id,
                    "doc_title"  : title,
                    "doc_url"    : url,
                    # Unique ID used as the ChromaDB primary key
                    "chunk_id"   : f"doc{doc_id}_chunk{chunk['chunk_index']}",
                }
            )
            all_chunks.append(chunk)

    return all_chunks


# ── Quick sanity-check (run this file directly to test chunking) ───────────────
if __name__ == "__main__":
    import json, sys
    from sentence_transformers import SentenceTransformer

    SCRAPPED_PATH = "scientific_diets.json"
    MODEL_NAME    = "BAAI/bge-small-en-v1.5"
    MAX_TOKENS    = 400
    STRIDE        = 200

    print(f"Loading model '{MODEL_NAME}' for tokenizer …")
    model     = SentenceTransformer(MODEL_NAME)
    tokenizer = model.tokenizer

    print(f"Loading corpus from '{SCRAPPED_PATH}' …")
    with open(SCRAPPED_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    chunks = chunk_corpus(corpus, tokenizer, MAX_TOKENS, STRIDE)

    # ── Stats
    total_docs   = len(corpus)
    total_chunks = len(chunks)
    avg_chunks   = total_chunks / total_docs if total_docs else 0
    token_counts = [c["token_count"] for c in chunks]
    avg_tokens   = sum(token_counts) / len(token_counts) if token_counts else 0

    print("\n──────────── Chunking Statistics ────────────")
    print(f"  Documents     : {total_docs}")
    print(f"  Total chunks  : {total_chunks}")
    print(f"  Avg chunks/doc: {avg_chunks:.1f}")
    print(f"  Avg tokens/chunk: {avg_tokens:.1f}")
    print(f"  Min tokens/chunk: {min(token_counts)}")
    print(f"  Max tokens/chunk: {max(token_counts)}")
    print("─────────────────────────────────────────────")

    # Show a sample chunk
    sample = chunks[5] if len(chunks) > 5 else chunks[0]
    print(f"\nSample chunk [{sample['chunk_id']}]:")
    print(f"  Doc     : {sample['doc_title']}")
    print(f"  Tokens  : {sample['start_token']} → {sample['end_token']}")
    print(f"  Preview : {sample['text'][:200]} …")
