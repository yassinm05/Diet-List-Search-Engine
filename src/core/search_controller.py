import json
from collections import defaultdict
from pathlib import Path

from src.ToleranceRet.algorithms import edit_distance as E
from src.ToleranceRet.algorithms import jaccard as J
from src.ToleranceRet.algorithms import kgrams as K
from src.ToleranceRet.algorithms import metaphone_search as M
from src.ToleranceRet.builders import inverted_index_builder as B
from src.AdvancedRet.semanticsearch.semantic_search import semantic_search
from src.AdvancedRet.queryexpansion.queryexpansion import expand_query_with_llm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_FILE = PROJECT_ROOT /"data" / "indexs" / "inverted_index.json"
DOCS_FILE = PROJECT_ROOT / "data" / "scientific_diets.json"

# 1. Initialize empty dictionaries so the app survives missing files
index_db = {}
doc_map = {}

try:
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        index_db = json.load(f)
    with DOCS_FILE.open("r", encoding="utf-8") as f:
        doc_map = {str(d["DocID"]): d["Title"] for d in json.load(f)}
except FileNotFoundError as e:
    print(f"WARNING: Missing main database file! {e}")


# 2. Helper Functions
def aggregate_docs(term_doc_dicts):
    """Combines document scores from multiple words."""
    if not term_doc_dicts: return []
    
    combined_scores = defaultdict(int)
    for doc_dict in term_doc_dicts:
        for doc_id, score in doc_dict.items():
            combined_scores[doc_id] += score
            
    # Sort by the combined score in descending order
    return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

def format_results(query_str, docs_list, corrected_from=None):
    """Formats the array of documents into a clean string."""
    if not docs_list:
        return f"No documents found for '{query_str}'."
    
    output = ""
    if corrected_from:
        output += f"Typo detected in: '{corrected_from}'.\n"
        output += f"Showing results for corrected query: '{query_str}'\n"
    else:
        output += f"Showing exact matches for: '{query_str}'\n"
        
    output += "-" * 50 + "\n"
    for doc_id, score in docs_list:
        title = doc_map.get(str(doc_id), "Unknown Document")
        output += f"Score: {score:4} | DocID: {doc_id:2} | Title: {title}\n"
    return output


# 3. Master Search Engine
def _process_search(query, get_best_match_func, prefix=""):
    """
    Master function that handles tokenizing, multi-word dictionary lookups, 
    document aggregation, and formatting.
    """
    tokens = B.PreProcessText(query)
    if not tokens: return "Please enter a valid search term."
    
    corrected_tokens = []
    term_doc_dicts = []
    was_corrected = False

    for token in tokens:
        if token in index_db:
            # Exact match found, no correction needed
            corrected_tokens.append(token)
            term_doc_dicts.append(index_db[token])
        else:
            # Word not found; apply the specific algorithm passed via get_best_match_func
            best_match = get_best_match_func(token) if get_best_match_func else None
            
            if best_match:
                corrected_tokens.append(best_match)
                term_doc_dicts.append(index_db.get(best_match, {}))
                was_corrected = True
            else:
                corrected_tokens.append(token) # Keep original if no suggestion

    docs = aggregate_docs(term_doc_dicts)
    original_query = " ".join(tokens)
    final_query = " ".join(corrected_tokens)
    
    # Handle the case where exact search yields no results
    if not docs and not get_best_match_func:
        return f"None of the words in '{original_query}' were found. Try the other tabs!"
        
    return prefix + format_results(final_query, docs, corrected_from=(original_query if was_corrected else None))


# 4. Main Search Flows 
def run_exact_search(query):
    # Pass 'None' for the match function since we don't want to correct typos here
    return _process_search(query, None)

def run_spelling_search(query):
    def get_match(token):
        candidates = K.k_grams(token)
        return min(candidates, key=lambda c: E.Edit_distance(token, c)) if candidates else None
        
    return _process_search(query, get_match)

def run_phonetic_search(query):
    def get_match(token):
        candidates = M.phonetic_candidates(token)
        return min(candidates, key=lambda c: E.Edit_distance(token, c)) if candidates else None
        
    return _process_search(query, get_match)

def run_smart_search(query):
    def get_match(token):
        candidates = set()
        candidates.update(K.k_grams(token) or [])
        candidates.update(M.phonetic_candidates(token) or [])
        return min(list(candidates), key=lambda c: E.Edit_distance(token, c)) if candidates else None
        
    return _process_search(query, get_match, prefix="SMART SEARCH ACTIVATED\n")

def run_jaccard_search(query):
    def get_match(token):
        candidates = K.k_grams(token)
        # Note the max() here because Jaccard looks for highest similarity, not lowest distance
        return max(candidates, key=lambda c: J.jaccard_similarity(token, c)) if candidates else None
        
    return _process_search(query, get_match)

def format_semantic_results(query_str, results_list, original_query=None):
    """Special formatter for Semantic Search that includes text snippets."""
    if not results_list:
        return f"No semantic matches found for '{query_str}'."
    
    output = ""
    if original_query:
        output += f"Original Query: '{original_query}'\n"
        output += f"Expanded Query: '{query_str}'\n"
    else:
        output += f"Showing semantic matches for: '{query_str}'\n"
        
    output += "-" * 70 + "\n"
    for r in results_list:
        # Clean up the snippet to fit nicely in the text box
        clean_snippet = r.get('best_chunk', '').replace('\n', ' ').strip()
        short_snippet = clean_snippet[:100] + "..." if len(clean_snippet) > 100 else clean_snippet
        
        output += f"Score: {r['score']:.4f} | DocID: {r['doc_id']:2} | Title: {r['title']}\n"
        output += f"  Snippet: {short_snippet}\n\n"
    
    return output

def run_semantic_search(query):
    # Calls your ChromaDB search
    raw_results = semantic_search(query, top_k_chunks=20, top_k_docs=5)
    return format_semantic_results(query, raw_results)

def run_expansion_search(query):
    # 1. Expand with Gemini
    expanded_query = expand_query_with_llm(query)
    # 2. Search with the new expanded query
    raw_results = semantic_search(expanded_query, top_k_chunks=20, top_k_docs=5)
    # 3. Format and show both the original and new queries
    return format_semantic_results(expanded_query, raw_results, original_query=query)