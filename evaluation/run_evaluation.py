import json
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Import your new semantic search
from src.AdvancedRet.semanticsearch.semantic_search import semantic_search

# TODO: Later, import your old legacy search here to compare!
# from controllers.search_controller import legacy_search

def calculate_metrics(retrieved_ids, relevant_ids, k=5):
    """Calculates Precision@K, Recall@K, and Reciprocal Rank."""
    # Only look at the Top K retrieved documents
    top_k_retrieved = retrieved_ids[:k]
    
    # Find the intersection (True Positives)
    true_positives = [doc_id for doc_id in top_k_retrieved if doc_id in relevant_ids]
    
    # 1. Precision @ K
    precision = len(true_positives) / k if k > 0 else 0.0
    
    # 2. Recall @ K
    recall = len(true_positives) / len(relevant_ids) if len(relevant_ids) > 0 else 0.0
    
    # 3. Reciprocal Rank (RR)
    rr = 0.0
    for rank, doc_id in enumerate(top_k_retrieved, start=1):
        if doc_id in relevant_ids:
            rr = 1.0 / rank
            break # We only care about the FIRST correct answer for MRR
            
    return precision, recall, rr

def run_ablation_study(gold_standard_path):
    with open(gold_standard_path, 'r', encoding='utf-8') as f:
        queries = json.load(f)

    total_queries = len(queries)
    print(f"Starting Evaluation on {total_queries} queries...\n")

    # Tracking totals for Semantic Search
    sem_total_p, sem_total_r, sem_total_rr = 0, 0, 0

    for idx, q_data in enumerate(queries):
        query_text = q_data["Query"]
        # Extract just the DocIDs from your Matches list
        relevant_ids = [match["DocID"] for match in q_data["Matches"]] 

        # --- 1. RUN SEMANTIC SEARCH ---
        # Get top 5 results
        sem_results = semantic_search(query_text, top_k_chunks=20, top_k_docs=5)
        sem_retrieved_ids = [res["doc_id"] for res in sem_results]
        
        # Calculate metrics for this query
        p, r, rr = calculate_metrics(sem_retrieved_ids, relevant_ids, k=5)
        sem_total_p += p
        sem_total_r += r
        sem_total_rr += rr
        
        # Print progress every 10 queries
        if (idx + 1) % 10 == 0:
            print(f"Evaluated {idx + 1}/{total_queries} queries...")

    # Calculate final averages
    print("\n" + "="*40)
    print("FINAL RESULTS: SEMANTIC SEARCH (K=5)")
    print("="*40)
    print(f"Mean Precision@5: {sem_total_p / total_queries:.4f}")
    print(f"Mean Recall@5:    {sem_total_r / total_queries:.4f}")
    print(f"Mean MRR:         {sem_total_rr / total_queries:.4f}")
    print("="*40)

if __name__ == "__main__":
    # Ensure this path points to your gold_standard.json
    gold_standard_path = Path(__file__).resolve().parent / "gold_standard.json"
    run_ablation_study(str(gold_standard_path))