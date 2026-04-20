import json
from collections import Counter
from pathlib import Path

from builders import kgram_index_builder as K

DEFAULT_INDEX_FILE = Path(__file__).resolve().parents[1] / "indexs" / "k_gram_index.json"

def k_grams(query, input_file=DEFAULT_INDEX_FILE):
    query = query.lower()

    query_grams = K.BuildGram(query, k=2)
    index_path = Path(input_file)

    with index_path.open('r', encoding='utf-8') as f:
        k_gram_index = json.load(f)

    all_candidate_words = []

    for gram in query_grams:
        if gram in k_gram_index.keys():
            all_candidate_words.extend(k_gram_index[gram])

    candidate_counts = Counter(all_candidate_words)

    top_10_candidates = []
    for word, count in candidate_counts.most_common(10):
        top_10_candidates.append(word)

    return top_10_candidates

if __name__ == "__main__":
    test_word = "protien" 
    best_matches = k_grams(test_word)
    print(f"Top candidates for '{test_word}':")
    print(best_matches)
