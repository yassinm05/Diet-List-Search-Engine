import json
from collections import defaultdict
from pathlib import Path

import jellyfish

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_FILE = PROJECT_ROOT / "indexs" / "inverted_index.json"
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "indexs" / "metaphone_index.json"


def Build_Metaphone_Index(input_file=DEFAULT_INPUT_FILE, output_file=DEFAULT_OUTPUT_FILE):
    input_path = Path(input_file)
    output_path = Path(output_file)

    print(f"Loading vocabulary from {input_path}...")

    try:
        with input_path.open("r", encoding="utf-8") as f:
            inverted_index = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}.")
        return

    vocabulary = list(inverted_index.keys())
    print(f"Generating phonetic codes for {len(vocabulary)} words...")

    metaphone_index = defaultdict(list)

    for word in vocabulary:
        phonetic_code = jellyfish.metaphone(word)
        if phonetic_code:
            metaphone_index[phonetic_code].append(word)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(metaphone_index, f, indent=4)

    print(f"Successfully saved Phonetic Index to {output_path}")
    print(f"Total unique phonetic sounds generated: {len(metaphone_index)}")


if __name__ == "__main__":
    Build_Metaphone_Index()
