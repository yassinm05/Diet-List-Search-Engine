import json
import jellyfish
from collections import defaultdict

def Build_Metaphone_Index(input_file="inverted_index.json", output_file="metaphone_index.json"):
    print(f"Loading vocabulary from {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            inverted_index = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}.")
        return

    
    vocabulary = list(inverted_index.keys())
    print(f"Generating phonetic codes for {len(vocabulary)} words...")

    
    metaphone_index = defaultdict(list)

    for word in vocabulary:
        # 1. Generate the Metaphone code using the library
        phonetic_code = jellyfish.metaphone(word)
        
        # 2. Add the word to the index under its phonetic code
        if phonetic_code:
            metaphone_index[phonetic_code].append(word)

    # Save the phonetic index to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metaphone_index, f, indent=4)
        
    print(f"Successfully saved Phonetic Index to {output_file}")
    print(f"Total unique phonetic sounds generated: {len(metaphone_index)}")

if __name__ == "__main__":
    Build_Metaphone_Index()