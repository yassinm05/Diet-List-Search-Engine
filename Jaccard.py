def get_bigrams(word):
    word = "$" + word + "$"
    return set(word[i:i+2] for i in range(len(word)-1))

def jaccard_similarity(word1, word2):
    set1 = get_bigrams(word1)
    set2 = get_bigrams(word2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union != 0 else 0.0