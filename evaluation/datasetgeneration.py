import json
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import os

# 1. Configuration
load_dotenv()
API_KEY = os.getenv("IRProjectGeminiKey")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def create_evaluation_dataset(input_file, output_file):
    # Load your scrapped documents
    with open(input_file, 'r', encoding='utf-8') as f:
        docs = json.load(f)

    # Prepare the massive context string for the LLM
    # We include DocID, Title, and Text so Gemini has the full picture
    context_parts = []
    for d in docs:
        context_parts.append(f"DocID: {d['DocID']}\nTitle: {d['Title']}\nText: {d['Text']}\n{'-'*20}")
    
    full_context = "\n".join(context_parts)

    # The Master Prompt
    prompt = f"""
    You are an Information Retrieval specialist. Below are 25 Wikipedia documents about diets.
    
    YOUR TASK:
    Generate a dataset of exactly 100 search queries based on these documents.
    
    QUERY CATEGORIES (25 queries each):
    1. Lexical: Keyword-heavy, using exact terms from titles and intros.
    2. Semantic: Natural language questions describing concepts without using the diet's name.
    3. Deep-Link: Specific facts found in the middle/bottom of long documents.
    4. Tolerant: Queries with intentional typos or phonetic misspellings (e.g., 'Keto' -> 'Keyto').

    FOR EACH QUERY:
    Identify ALL relevant documents from the 25 provided. Assign a Relevance Score:
    3: The primary/best document for this query.
    2: Highly relevant (contains a significant section about this).
    1: Tangentially relevant (mentions it briefly).

    OUTPUT FORMAT:
    Return ONLY a JSON list of objects:
    [
      {{
        "Query": "text here",
        "Type": "Lexical/Semantic/Deep-Link/Tolerant",
        "Matches": [
          {{"DocID": 1, "Score": 3}},
          {{"DocID": 2, "Score": 1}}
        ]
      }}
    ]

    DOCUMENTS:
    {full_context}
    """

    print("Sending request to Gemini... (This may take 60-90 seconds)")
    try:
        # We use a higher temperature (0.7) for query variety
        response = model.generate_content(prompt)
        
        # Clean the output to ensure it's valid JSON
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        
        generated_data = json.loads(raw_text)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(generated_data, f, indent=4)
            
        print(f"Success! Generated {len(generated_data)} queries in {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        # If the output was too long and truncated, the JSON load will fail.
        # In that case, we suggest splitting the prompt into 2 batches of 50.

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    input_file = project_root / "data" / "scientific_diets.json"
    output_file = Path(__file__).resolve().parent / "gold_standard.json"
    create_evaluation_dataset(str(input_file), str(output_file))