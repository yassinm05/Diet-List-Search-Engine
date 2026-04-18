import json
import re
from collections import defaultdict, Counter

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
    "of", "with", "by", "as", "is", "are", "was", "were", "be", "been", 
    "it", "this", "that", "these", "those", "from", "which", "can", "not"
}

def PreProcessText(text):
    text = text.lower()
    words = re.findall(r'\b[a-z0-9]+\b', text)

    filtered_words = [word for word in words if word not in STOP_WORDS]
    return filtered_words

def BuildInvertedIndex(input_file = "scientific_diets.json", output_file = "inverted_index.json"):
    try:
       with open(input_file, 'r', encoding='utf-8') as f:
           documents = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
    
    inverted_index = defaultdict(dict)

    for doc in documents:
        doc_id = doc['DocID']
        text = doc['Text']

        tokens = PreProcessText(text)

        term_frequencies = Counter(tokens)
        
        for term, freq in term_frequencies.items():
            inverted_index[term][doc_id] = freq

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(inverted_index, f, indent=4)


if __name__ == "__main__":
    BuildInvertedIndex()

   
       