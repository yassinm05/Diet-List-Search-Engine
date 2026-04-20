import json
import re
from collections import Counter, defaultdict
from pathlib import Path

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
    "of", "with", "by", "as", "is", "are", "was", "were", "be", "been", 
    "it", "this", "that", "these", "those", "from", "which", "can", "not"
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_FILE = PROJECT_ROOT / "scientific_diets.json"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "indexs" / "inverted_index.json"

def PreProcessText(text):
    text = text.lower()
    words = re.findall(r'\b[a-z0-9]+\b', text)

    filtered_words = [word for word in words if word not in STOP_WORDS]
    return filtered_words

def BuildInvertedIndex(input_file=DEFAULT_SOURCE_FILE, output_file=DEFAULT_OUTPUT_FILE):
    input_path = Path(input_file)
    output_path = Path(output_file)

    try:
        with input_path.open('r', encoding='utf-8') as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        return

    inverted_index = defaultdict(dict)

    for doc in documents:
        doc_id = doc['DocID']
        text = doc['Text']

        tokens = PreProcessText(text)

        term_frequencies = Counter(tokens)

        for term, freq in term_frequencies.items():
            inverted_index[term][doc_id] = freq

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(inverted_index, f, indent=4)


if __name__ == "__main__":
    BuildInvertedIndex()

   
       