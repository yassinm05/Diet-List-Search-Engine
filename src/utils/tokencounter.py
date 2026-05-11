import json
from pathlib import Path
import tiktoken

def analyze_corpus(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Using 'cl100k_base' which is common for modern LLMs
    encoding = tiktoken.get_encoding("cl100k_base")
    
    stats = []
    total_tokens = 0
    
    print(f"{'DocID':<6} | {'Title':<25} | {'Tokens':<10}")
    print("-" * 45)
    
    for doc in data:
        text = doc.get("Text", "")
        tokens = len(encoding.encode(text))
        stats.append(tokens)
        total_tokens += tokens
        print(f"{doc['DocID']:<6} | {doc['Title'][:25]:<25} | {tokens:<10}")
    
    avg = sum(stats) / len(stats)
    print("-" * 45)
    print(f"Total Documents: {len(data)}")
    print(f"Total Tokens:    {total_tokens}")
    print(f"Average Tokens:  {avg:.2f}")
    print(f"Max Tokens:      {max(stats)}")
    
    return stats

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    corpus_file = project_root / "data" / "scientific_diets.json"
    analyze_corpus(str(corpus_file))