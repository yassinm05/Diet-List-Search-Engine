import json
import jellyfish

def phonetic_candidates(query_word, index_file="metaphone_index.json"):
    query_word = query_word.lower().strip()
    
    
    typo_code = jellyfish.metaphone(query_word)
    print(f"Typo: '{query_word}' -> Phonetic Code: [{typo_code}]")
    
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            metaphone_index = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {index_file}. Run the build script first.")
        return []

    
    candidates = metaphone_index.get(typo_code, [])
    
    return candidates

if __name__ == "__main__":
    test_typo = "seeliak" 
    
    print("Searching phonetic index...\n" + "-"*30)
    matches = phonetic_candidates(test_typo)
    
    if matches:
        print(f"Success! Found {len(matches)} dictionary matches for that sound:")
        print(matches)
    else:
        print("No phonetic matches found in the dictionary.")