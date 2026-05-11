import json
import csv
import re
from src.core import search_controller as sc

def calculate_metrics(retrieved_ids, relevant_ids, k=5):
    """Calculates Precision, Recall, and MRR for the top K results."""
    top_k = retrieved_ids[:k]
    true_positives = [doc_id for doc_id in top_k if doc_id in relevant_ids]
    
    precision = len(true_positives) / k if k > 0 else 0.0
    recall = len(true_positives) / len(relevant_ids) if len(relevant_ids) > 0 else 0.0
    
    rr = 0.0
    for rank, doc_id in enumerate(top_k, start=1):
        if doc_id in relevant_ids:
            rr = 1.0 / rank
            break
            
    return precision, recall, rr

def extract_ids_from_text(result_text):
    """Finds all the 'DocID: X' numbers inside your UI text output."""
    # This looks for "DocID: 12" or "DocID:  5" and pulls out the number
    matches = re.findall(r'DocID:\s*(\d+)', result_text)
    return [int(m) for m in matches]

def main():
    print("Loading Gold Standard...")
    try:
        with open("evaluation/gold_standard.json", 'r', encoding='utf-8') as f:
            queries = json.load(f)
    except FileNotFoundError:
        print("Error: Please make sure 'gold_standard.json' is in an 'evaluation' folder!")
        return

    # Map the algorithms you want to test
    engines = {
        "1_K-Grams": sc.run_spelling_search,
        "2_Metaphone": sc.run_phonetic_search,
        "3_Jaccard": sc.run_jaccard_search,
        "4_SmartSearch": sc.run_smart_search,
        "5_Semantic": sc.run_semantic_search,
        "6_Semantic_Expansion": sc.run_expansion_search
    }

    results_data = []
    total_q = len(queries)

    print(f"Starting Ablation Study for {total_q} queries. This might take a minute...\n")

    for engine_name, search_func in engines.items():
        print(f"Testing Engine: {engine_name}...")
        sum_p, sum_r, sum_rr = 0, 0, 0
        
        for q in queries:
            query_text = q["Query"]
            # Get the correct IDs from the gold standard
            relevant_ids = [match["DocID"] for match in q["Matches"]]
            
            try:
                # 1. Run the search (gets your formatted text)
                result_text = search_func(query_text)
                
                # 2. Extract the DocIDs from the text
                retrieved_ids = extract_ids_from_text(result_text)
                
                # 3. Grade it
                p, r, rr = calculate_metrics(retrieved_ids, relevant_ids, k=5)
                sum_p += p
                sum_r += r
                sum_rr += rr
            except Exception as e:
                # If an engine crashes on a word, score it as 0
                pass
                
        # Save average scores
        results_data.append({
            "Engine": engine_name,
            "Precision@5": round(sum_p / total_q, 4),
            "Recall@5": round(sum_r / total_q, 4),
            "MRR": round(sum_rr / total_q, 4)
        })

    # --- SAVE TO CSV ---
    csv_file = "Ablation_Report.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Engine", "Precision@5", "Recall@5", "MRR"])
        writer.writeheader()
        writer.writerows(results_data)
        
    print("\n" + "="*50)
    print("✅ DONE! Open 'Ablation_Report.csv' in Excel.")
    print("="*50)

if __name__ == "__main__":
    main()