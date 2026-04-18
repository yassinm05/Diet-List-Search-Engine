import json
import Building_II as B
import Kgrams as K
import EditDistance as E
import MetaphoneSearch as M
import Jaccard as J

# 1. Initialize empty dictionaries so the app survives missing files
index_db = {}
doc_map = {}

try:
    with open("inverted_index.json", "r", encoding="utf-8") as f: 
        index_db = json.load(f)
    with open("scientific_diets.json", "r", encoding="utf-8") as f: 
        doc_map = {str(d["DocID"]): d["Title"] for d in json.load(f)}
except FileNotFoundError as e:
    print(f"WARNING: Missing main database file! {e}")


# 2. Helper Functions
def get_exact_docs(term):
    """Retrieves and sorts the documents for a correctly spelled term."""
    if term not in index_db: return []
    results = index_db[term]
    return sorted(results.items(), key=lambda x: x[1], reverse=True)

def format_results(term, docs_list, corrected_from=None):
    """Formats the array of documents into a clean string."""
    if not docs_list:
        return f"No documents found containing the word '{term}'."
    
    output = ""
    if corrected_from:
        output += f"Typo detected: '{corrected_from}'.\n"
        output += f"Showing results for corrected word: '{term}'\n"
    else:
        output += f"Showing exact matches for: '{term}'\n"
        
    output += "-" * 50 + "\n"
    for doc_id, score in docs_list:
        title = doc_map.get(str(doc_id), "Unknown Document")
        output += f"Score: {score:2} | DocID: {doc_id:2} | Title: {title}\n"
    return output


# 3. Main Search Flows
def run_exact_search(query):
    tokens = B.PreProcessText(query)
    if not tokens: return "Please enter a valid search term."
    
    target_word = tokens[0]
    docs = get_exact_docs(target_word)
    
    if not docs:
        return f"'{target_word}' not found in the dictionary. Try the other tabs!"
    return format_results(target_word, docs)

def run_spelling_search(query):
    tokens = B.PreProcessText(query)
    if not tokens: return "Please enter a valid search term."
    
    target_word = tokens[0]
    
    if target_word in index_db:
        return f"'{target_word}' is already spelled correctly!\n\n" + format_results(target_word, get_exact_docs(target_word))
        
    # Ask the Kgrams module for candidates
    candidates = K.k_grams(target_word)
    if not candidates: 
        return f"Could not find any spelling suggestions for '{target_word}'."
    
    best_match = min(candidates, key=lambda c: E.Edit_distance(target_word, c))
    docs = get_exact_docs(best_match)
    
    return format_results(best_match, docs, corrected_from=target_word)

def run_phonetic_search(query):
    tokens = B.PreProcessText(query)
    if not tokens: return "Please enter a valid search term."
    
    target_word = tokens[0]
    
    if target_word in index_db:
        return f"'{target_word}' is already spelled correctly!\n\n" + format_results(target_word, get_exact_docs(target_word))
        
    # Ask the MetaphoneSearch module for candidates
    candidates = M.phonetic_candidates(target_word)
    
    if not candidates: 
        return f"Could not find phonetic matches sounding like '{target_word}'."
    
    best_match = min(candidates, key=lambda c: E.Edit_distance(target_word, c))
    docs = get_exact_docs(best_match)
    
    return format_results(best_match, docs, corrected_from=target_word)

def run_smart_search(query):
    tokens = B.PreProcessText(query)
    if not tokens: return "Please enter a valid search term."
    
    target_word = tokens[0]
    
    # 1. Exact Match Check
    if target_word in index_db:
        return f"Exact Match Found!\n\n" + format_results(target_word, get_exact_docs(target_word))
        
    # 2. Pool Candidates from both modules
    candidates = set()
    candidates.update(K.k_grams(target_word))
    candidates.update(M.phonetic_candidates(target_word))
    
    if not candidates:
        return f"No matches found using any algorithm for '{target_word}'."
        
    # 3. Find the best match from the combined pool
    best_match = min(list(candidates), key=lambda c: E.Edit_distance(target_word, c))
    docs = get_exact_docs(best_match)
    
    return "SMART SEARCH ACTIVATED\n" + format_results(best_match, docs, corrected_from=target_word)

def run_jaccard_search(query):
    tokens = B.PreProcessText(query)
    if not tokens: return "Please enter a valid search term."
    
    target_word = tokens[0]
    
    if target_word in index_db:
        return f"'{target_word}' is already spelled correctly!\n\n" + format_results(target_word, get_exact_docs(target_word))
        
    candidates = K.k_grams(target_word)
    if not candidates: 
        return f"Could not find any spelling suggestions for '{target_word}'."
    
    best_match = max(candidates, key=lambda c: J.jaccard_similarity(target_word, c))
    docs = get_exact_docs(best_match)
    
    return format_results(best_match, docs, corrected_from=target_word)