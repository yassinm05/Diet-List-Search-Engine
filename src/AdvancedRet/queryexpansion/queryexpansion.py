import os
import sys
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))


env_path = project_root / ".env"

from src.AdvancedRet.semanticsearch import semantic_search as semantic_search_module
# Ensure API key is loaded
load_dotenv(env_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the fast, lightweight model for real-time expansion
expansion_model = genai.GenerativeModel('gemini-2.5-flash')

def expand_query_with_llm(original_query: str) -> str:
    """
    Takes a short user query and returns an expanded string 
    containing the original query plus 3-4 highly relevant medical/diet synonyms.
    """
    if not original_query or not original_query.strip():
        return original_query

    prompt = f"""
    You are an invisible search assistant for a medical and diet database.
    The user typed this search query: "{original_query}"
    
    Provide exactly 3 to 4 related keywords, medical terms, or synonyms that would help find relevant Wikipedia articles. 
    
    RULES:
    1. Return ONLY a single line of space-separated words.
    2. Do NOT use commas.
    3. Do NOT provide any explanations or markdown.
    """

    try:
        response = expansion_model.generate_content(prompt)
        # Clean the output (strip whitespace and newlines)
        expanded_terms = response.text.strip()
        
        # Combine original query with the new terms
        final_query = f"{original_query} {expanded_terms}"
        return final_query
        
    except Exception as e:
        print(f"[Warning] Query expansion failed: {e}")
        # If the API fails (e.g., rate limit), gracefully degrade to the original query
        return original_query

def execute_master_search(query: str, use_expansion: bool = False, top_k: int = 5):
    """
    The master entry point for the search engine.
    Controls the ablation study toggles.
    """
    print(f"\n--- New Search ---")
    print(f"User Query: '{query}'")
    
    # 1. Check if Expansion is toggled ON
    if use_expansion:
        search_query = expand_query_with_llm(query)
        print(f"LLM Expanded Query: '{search_query}'")
    else:
        search_query = query
        
    # 2. Execute the Semantic Search
    # (We use search_query here, but we'll return the results to the UI normally)
    raw_results = semantic_search_module.semantic_search(search_query, top_k_chunks=top_k * 4, top_k_docs=top_k)
    
    # 3. Format for Tkinter UI
    formatted_results = [
        {
            "doc_id" : r["doc_id"],
            "title"  : r["title"],
            "url"    : r["url"],
            "score"  : r["score"],
            "snippet": r["best_chunk"][:300] + "…" if len(r["best_chunk"]) > 300 else r["best_chunk"],
        }
        for r in raw_results
    ]
    
    return formatted_results
# --- Quick Test ---
if __name__ == "__main__":
    test_query = "keto"
    print(f"Original: {test_query}")
    print(f"Expanded: {expand_query_with_llm(test_query)}")
    # Expected output something like: "keto ketogenic low-carb fat ketosis"