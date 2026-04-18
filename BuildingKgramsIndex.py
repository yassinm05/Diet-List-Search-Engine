import json
from collections import defaultdict, Counter

def BuildGram(Text, k):
    Text = "$" + Text + "$"
    
    unique_grams = set()
    
    for i in range(len(Text) - k + 1):
        
        current_gram = Text[i:i+k]
        
        unique_grams.add(current_gram)

    
    return list(unique_grams)

def K_Gram_Indexing(k, input_file="inverted_index.json", output_file="k_gram_index.json"):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            inverted_index = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return
        
    
    k_gram_index = defaultdict(list)

    
    vocabulary_words = inverted_index.keys()

    for word in vocabulary_words:
        grams = BuildGram(word, k)
        
        for bg in grams:
            k_gram_index[bg].append(word)

    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(k_gram_index, f, indent=4)

if __name__ == "__main__":
    K_Gram_Indexing(k=2)
