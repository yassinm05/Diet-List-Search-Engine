import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_FILE = PROJECT_ROOT / "indexs" / "inverted_index.json"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "indexs" / "k_gram_index.json"

def BuildGram(Text, k):
    Text = "$" + Text + "$"
    
    unique_grams = set()
    
    for i in range(len(Text) - k + 1):
        
        current_gram = Text[i:i+k]
        
        unique_grams.add(current_gram)

    
    return list(unique_grams)

def K_Gram_Indexing(k, input_file=DEFAULT_INPUT_FILE, output_file=DEFAULT_OUTPUT_FILE):
    input_path = Path(input_file)
    output_path = Path(output_file)

    try:
        with input_path.open('r', encoding='utf-8') as f:
            inverted_index = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        return
        
    
    k_gram_index = defaultdict(list)

    
    vocabulary_words = inverted_index.keys()

    for word in vocabulary_words:
        grams = BuildGram(word, k)
        
        for bg in grams:
            k_gram_index[bg].append(word)

    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(k_gram_index, f, indent=4)

if __name__ == "__main__":
    K_Gram_Indexing(k=2)
