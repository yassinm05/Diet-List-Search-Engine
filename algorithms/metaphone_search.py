import json
import jellyfish
from pathlib import Path

DEFAULT_INDEX_FILE = Path(__file__).resolve().parents[1] / "indexs" / "metaphone_index.json"


def phonetic_candidates(query_word, index_file=DEFAULT_INDEX_FILE):
    query_word = query_word.lower().strip()

    typo_code = jellyfish.metaphone(query_word)
    print(f"Typo: '{query_word}' -> Phonetic Code: [{typo_code}]")

    index_path = Path(index_file)
    try:
        with index_path.open('r', encoding='utf-8') as f:
            metaphone_index = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {index_path}. Run the build script first.")
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