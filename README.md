# 🔍 Information Retrieval Search Engine

**Author:** Yassin Mahmoud & Mohamed Mahmoud
**Domain:** Scientific Diets & Globally Adaptive Nutritional Search  

---

## 1. Project Overview

This project is a comprehensive Information Retrieval (IR) system designed to accurately search and retrieve scientific diet and nutritional documents. The system implements multiple retrieval paradigms:

**Tolerant Retrieval Pipeline:** Handles real-world user queries—which often include typographical errors or phonetic guesses of complex medical terms—the system implements a robust pipeline with multiple linguistic and mathematical algorithms to gracefully autocorrect queries and retrieve relevant documents.

**Advanced Retrieval Capabilities:** Goes beyond keyword matching by integrating:
- **Neural Semantic Search** - Uses transformer-based embeddings and vector similarity to find semantically related documents
- **LLM-Based Query Expansion** - Leverages large language models to automatically expand user queries with synonyms and related terms
- **Evaluation Framework** - Includes comprehensive IR metrics (Precision, Recall, MRR) to assess retrieval effectiveness

## 1.1 Project Structure

The codebase is organized into focused folders:

* **GUI Entry Point:** `app_gui.py`
* **Controllers:** `src/core/search_controller.py`
* **Tolerance Retrieval Algorithms:** `src/ToleranceRet/algorithms/` (edit distance, Jaccard, k-grams, metaphone search)
* **Index Builders:** `src/ToleranceRet/builders/` (data scraper and index builders)
* **Advanced Retrieval:** `src/AdvancedRet/` (semantic search and query expansion)
* **Evaluation Framework:** `evaluation/` (metrics calculation and ablation studies)
* **Index Files:** `data/indexs/` (`inverted_index.json`, `k_gram_index.json`, `metaphone_index.json`)
* **Vector Database:** `data/chroma_db/` (ChromaDB persistent storage for semantic search)
* **Source Dataset:** `data/scientific_diets.json`

## 2. Phase 1: Data Acquisition & Storage

The foundation of the search engine was built by dynamically harvesting text data from the web.

* **Web Scraping:** Utilizing the Python `BeautifulSoup` library, the system scraped the "List of Diets" page from Wikipedia, specifically targeting sections dedicated to medical, scientific, and weight-control diets to ensure high-quality data.
* **Data Structuring:** The raw HTML paragraphs were cleaned of citation brackets and structural artifacts. The resulting documents were packaged into a structured format (`scientific_diets.json`), where each entry contains a unique **DocID**, **Title**, **URL**, and the raw **Text** of the article.

## 3. Phase 2: Core Indexing Engine

To enable rapid searching, the raw text was transformed into an optimized dictionary.

* **Text Preprocessing:** All document text underwent a strict normalization pipeline. This included converting text to lowercase, stripping out all punctuation, and filtering out non-informative stop-words (e.g., "the", "and", "is").
* **Inverted Index Construction:** The preprocessed tokens were mapped to the documents in which they appear. The resulting `indexs/inverted_index.json` maps each unique vocabulary word to a sub-dictionary containing the **DocID** and its corresponding **Term Frequency (TF)**.

## 4. Phase 3: Tolerant Retrieval Data Structures

To facilitate typo correction and phonetic matching without scanning the entire database at search time, two specialized dictionaries were constructed from the main vocabulary:

* **K-Gram Index (`indexs/k_gram_index.json`):** Every word in the primary inverted index was broken down into overlapping bigrams (k=2) with boundary markers (e.g., `$p`, `pr`, `ro`). This index maps each 2-character chunk to the list of vocabulary words that contain it.
* **Phonetic Index (`indexs/metaphone_index.json`):** Utilizing the `jellyfish` library, every vocabulary word was translated into its standardized phonetic consonant code (representing how the word sounds). This index groups words with entirely different spellings under identical phonetic keys.

## 5. Phase 4: Search Algorithms & Optimization

The system utilizes several algorithms to process user queries, employing a highly optimized "funnel" approach to maintain computational speed.

* **K-Gram Candidate Filtering:** When a misspelled word is searched, it is broken into bigrams. The system queries the K-gram index to return only the **top 10 candidate words** that share the highest number of bigrams with the typo.
* **Edit Distance (Levenshtein):** Instead of running computationally expensive matrix math against the entire dictionary, the Edit Distance algorithm is selectively applied *only* to the top 10 candidates retrieved by the K-gram filter. It calculates the minimum number of insertions, deletions, or substitutions required to fix the typo, definitively selecting the candidate with the lowest cost.
* **Phonetic Matching:** The user's query is converted into a phonetic code using the Metaphone algorithm. The system instantly retrieves all dictionary words that share that exact sound. If multiple words sound identical, Edit Distance is used as a tie-breaker.
* **Jaccard Similarity:** As an alternative mathematical scoring model, this algorithm calculates the Intersection over Union (IoU) between the bigram set of the typo and the bigram sets of the dictionary candidates, selecting the correction with the highest similarity coefficient.

## 6. Phase 5: Advanced Semantic Search

To move beyond lexical matching and capture semantic meaning, the system now integrates AI-powered neural retrieval:

* **Semantic Vector Embeddings:** Using the BGE (BAAI General Embedding) small model (`BAAI/bge-small-en-v1.5`), all documents are transformed into dense vector embeddings that capture contextual meaning. This allows the system to understand that "ketogenic" and "low-carbohydrate" are semantically similar, even without exact word matches.
* **Vector Database Storage:** Embeddings are efficiently stored and indexed in ChromaDB, a vector database purpose-built for semantic search. This enables sub-millisecond similarity searches across the entire corpus.
* **Query-Document Similarity:** User queries are encoded using the same embedding model (with special query prefixes for optimal retrieval), then compared against all document embeddings using cosine similarity. Documents with the highest semantic similarity scores are returned, regardless of spelling or exact terminology.
* **Chunk-Level Retrieval:** For better relevance, documents are split into semantic chunks, and the system returns the most relevant chunk from each matched document. This provides more granular and contextually appropriate results.

### 6.1 BGE Query Prefix

The system uses a special prefix when encoding user queries: `"Represent this sentence for searching relevant passages: "`. This prefix tells the BGE model that the text is a search query (not a document), which optimizes the embedding for retrieval tasks. This improves matching accuracy because the model understands the intent behind the query.

### 6.2 Max Pooling for Document Scoring

Since documents are split into multiple chunks, multiple chunks from the same document may be retrieved in the search results. **Max pooling** aggregates these chunk-level scores back to the document level by taking the **highest similarity score** among all chunks from that document. This ensures that if even one part of a document is highly relevant to the query, the entire document ranks highly—which aligns with how users expect search engines to work.

## 7. Phase 6: Query Expansion with LLM

To further enhance search capabilities and discover relevant documents that the user may not have thought to query directly, the system integrates Large Language Model (LLM) based query expansion:

* **Gemini-Powered Expansion:** Using Google's Gemini 2.5 Flash model, the system generates 3-4 semantically related keywords and medical synonyms for any user query. For example, searching for "keto" expands to include "ketogenic", "low-carb", "fat-metabolism", etc.
* **Ablation Study Framework:** The expansion step is optional and can be toggled on or off, allowing for evaluation of how query expansion impacts retrieval performance.
* **Graceful Degradation:** If the LLM API is unavailable or rate-limited, the system gracefully falls back to the original query without interrupting the search experience.
* **Integration with Semantic Search:** Expanded queries are fed directly into the semantic search pipeline, significantly broadening the document retrieval scope.

## 8. Phase 7: Application Architecture & User Interface

The system was designed with a strict Separation of Concerns. The business logic and algorithm routing are isolated within `src/core/search_controller.py`, which feeds formatted data to a lightweight Tkinter Graphical User Interface (GUI).

The GUI is divided into seven functional tabs to demonstrate the different retrieval strategies:

* **Exact Match:** The baseline engine. It cleans the user's query and searches the primary inverted index. It requires perfect spelling; a single typo results in a failed search.
* **Spelling (K-Grams):** Designed for typographical errors (fat-finger mistakes). It breaks the typo into bigrams, retrieves a shortlist of candidates from the k-gram index, and uses Edit Distance to autocorrect the query before retrieving documents.
* **Phonetic (Metaphone):** Designed for phonetic errors where the user does not know how to spell the word. It translates the query into a consonant code, looks it up in the Metaphone dictionary, resolves ties with Edit Distance, and retrieves the documents.
* **Jaccard Similarity:** An alternative spelling corrector. It utilizes the k-gram index to pool candidates, but mathematically scores and selects the winner using the Jaccard Intersection over Union formula rather than Edit Distance operations.
* **Smart Search:** The ultimate, "Google-style" approach. It attempts an Exact Match first. If that fails, it simultaneously queries both the k-gram filter and the phonetic index, pooling all potential candidates into one massive set. It then runs Edit Distance across the entire pool to find the absolute best correction, completely abstracting the complexity away from the user.
* **Semantic Search:** AI-powered contextual search. Uses pre-computed document embeddings and ChromaDB to find semantically similar documents. This tab demonstrates neural retrieval without relying on keyword matching.
* **Query Expansion:** The ultimate advanced engine. Combines LLM-based query expansion with semantic search. First, the user query is expanded using Gemini to generate synonyms and related terms. The expanded query is then fed into the semantic search pipeline for maximum coverage and relevance.

---

## 9. Standardized System Output

Regardless of the search method or tab selected by the user, the final step of the retrieval pipeline is standardized across the entire application. Once the engine finalizes the exact match or determines the best spelling/phonetic correction, it queries the main inverted index and outputs the results in a clean, readable format. For every successfully matched document, each tab returns:

> * **Score:** The relevance ranking based on Term Frequency (TF) for traditional methods, or cosine similarity score for semantic methods.
> * **DocID:** The unique identifier for the document in the database.
> * **Title:** The name of the scientific diet or article.

*(Results are always displayed in descending order, ensuring the most mathematically relevant documents appear at the top).*

---

## 10. Evaluation Framework

To assess the effectiveness of the search engine, an evaluation framework has been implemented:

* **Gold Standard Dataset:** Manually curated query-document relevance judgments are stored in `evaluation/gold_standard.json`, mapping each query to its relevant documents.
* **Evaluation Metrics:** The framework computes three standard IR metrics:
  - **Precision@K:** The proportion of retrieved documents that are relevant, measured at a cutoff of K results (typically K=5).
  - **Recall@K:** The proportion of all relevant documents that appear in the top K results.
  - **Mean Reciprocal Rank (MRR):** The average of the reciprocal ranks of the first relevant document for each query.
* **Ablation Study Support:** The evaluation framework can toggle different features (e.g., query expansion on/off) to measure their individual contribution to retrieval performance.
* **Semantic Search Evaluation:** The `evaluation/run_evaluation.py` script specifically evaluates semantic search performance against the gold standard.

---

## 11. Dependencies

The project requires the following Python packages:

**Core Dependencies:**
* `beautifulsoup4>=4.14.3` - Web scraping for data acquisition
* `jellyfish>=1.1.3` - Fuzzy string matching and Metaphone phonetic encoding
* `requests>=2.33.1` - HTTP requests for web scraping

**Advanced Retrieval Dependencies:**
* `sentence-transformers` - BAAI BGE embedding model for semantic search
* `chromadb` - Vector database for efficient semantic similarity search
* `google-generativeai` - Google Gemini API for LLM-based query expansion
* `python-dotenv` - Environment variable management for API keys

**Python Version:** Requires Python 3.12 or higher

---

## 12. Setup & Configuration

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Environment Configuration
For query expansion to work, create a `.env` file in the project root with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Initialize Data & Indices
Run the builders to generate the inverted index and other search indices:
```bash
python src/ToleranceRet/builders/inverted_index_builder.py
python src/ToleranceRet/builders/kgram_index_builder.py
python src/ToleranceRet/builders/metaphone_index_builder.py
```

### 4. Build Vector Embeddings (for Semantic Search)
```bash
python src/AdvancedRet/semanticsearch/build_index.py
```

### 5. Launch the GUI
```bash
python app_gui.py
```

---

## 13. Running Evaluations

To evaluate semantic search performance:
```bash
python evaluation/run_evaluation.py
```

This generates Mean Precision@5, Recall@5, and MRR metrics comparing the semantic search engine against the gold standard dataset.
