import json
from collections import defaultdict
from pathlib import Path

from algorithms import edit_distance as E
from algorithms import jaccard as J
from algorithms import kgrams as K
from algorithms import metaphone_search as M
from builders import inverted_index_builder as B

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = PROJECT_ROOT / "indexs" / "inverted_index.json"
DOCS_FILE = PROJECT_ROOT / "scientific_diets.json"

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