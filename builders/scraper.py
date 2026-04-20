import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_FILE = PROJECT_ROOT / "scientific_diets.json"

def scrape_scientific_diets(max_documents=50, output_file=DEFAULT_OUTPUT_FILE):
    base_url = "https://en.wikipedia.org"
    list_url = f"{base_url}/wiki/List_of_diets"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching master list from {list_url}...")
    response = requests.get(list_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    diet_links = []
    seen_urls = set()
    
    # THE FIX: We target the specific HTML IDs for the scientific sections
    target_ids = ['Diets_followed_for_medical_reasons', 'Calorie_and_weight_control_diets']
    
    for section_id in target_ids:
        # 1. Find the invisible span tag that holds the ID
        heading_span = soup.find(id=section_id)
        
        if heading_span:
            # 2. Get the actual <h2> heading tag that wraps the span
            heading_tag = heading_span.parent
            
            # 3. Find the bulleted list (<ul>) that comes immediately AFTER this heading
            ul_tag = heading_tag.find_next_sibling('ul')
            
            if ul_tag:
                # 4. Grab all the links, but ONLY from inside this specific list
                links_in_section = ul_tag.find_all('a', href=True)
                
                for link in links_in_section:
                    href = link['href']
                    title = link.get('title', link.text).strip()
                    
                    if href.startswith('/wiki/') and ':' not in href and '#' not in href:
                        full_url = base_url + href
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            diet_links.append({'title': title, 'url': full_url})
                            
    print(f"Found {len(diet_links)} scientific diet pages. Scraping up to {max_documents}...")
    
    documents = []
    doc_id_counter = 1
    
    for diet in diet_links[:max_documents]:
        print(f"[{doc_id_counter}/{max_documents}] Scraping: {diet['title']}")
        
        try:
            page_response = requests.get(diet['url'], headers=headers)
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            
            paragraphs = page_soup.find_all('p')
            full_text = " ".join([p.text.strip() for p in paragraphs if p.text.strip() != ""])
            clean_text = re.sub(r'\[\d+\]', '', full_text)
            
            if len(clean_text) > 100: 
                documents.append({
                    "DocID": doc_id_counter,
                    "Title": diet['title'],
                    "URL": diet['url'],
                    "Text": clean_text
                })
                doc_id_counter += 1
                
        except Exception as e:
            print(f"Error scraping {diet['title']}: {e}")
            
        time.sleep(1)
        
    # We'll save it as scientific_diets.json this time
    output_path = Path(output_file)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(documents, f, indent=4, ensure_ascii=False)

    print(f"\nScraping complete! Saved {len(documents)} documents to {output_path}")

if __name__ == "__main__":
    scrape_scientific_diets(max_documents=50)