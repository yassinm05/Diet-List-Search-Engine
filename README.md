# 🔍 Information Retrieval Search Engine

**Author:** Yassin Mahmoud  
**Domain:** Scientific Diets & Globally Adaptive Nutritional Search  

---

## 1. Project Overview

This project is a custom-built Information Retrieval (IR) system designed to accurately search and retrieve scientific diet and nutritional documents. To handle real-world user queries—which often include typographical errors or phonetic guesses of complex medical terms—the system implements a robust Tolerant Retrieval pipeline. It utilizes multiple linguistic and mathematical algorithms to gracefully autocorrect queries and retrieve relevant documents.

## 1.1 Project Structure

The codebase is organized into focused folders:

* **GUI Entry Point:** `app_gui.py`
* **Controllers:** `controllers/search_controller.py`
* **Algorithms:** `algorithms/` (edit distance, Jaccard, k-grams, metaphone search)
* **Builders:** `builders/` (data scraper and index builders)
* **Index Files:** `indexs/` (`inverted_index.json`, `k_gram_index.json`, `metaphone_index.json`)
* **Source Dataset:** `scientific_diets.json`

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

## 6. Phase 5: Application Architecture & User Interface

The system was designed with a strict Separation of Concerns. The business logic and algorithm routing are isolated within `controllers/search_controller.py`, which feeds formatted data to a lightweight Tkinter Graphical User Interface (GUI).

The GUI is divided into five functional tabs to demonstrate the different retrieval strategies:

* **Exact Match:** The baseline engine. It cleans the user's query and searches the primary inverted index. It requires perfect spelling; a single typo results in a failed search.
* **Spelling (K-Grams):** Designed for typographical errors (fat-finger mistakes). It breaks the typo into bigrams, retrieves a shortlist of candidates from the k-gram index, and uses Edit Distance to autocorrect the query before retrieving documents.
* **Phonetic (Metaphone):** Designed for phonetic errors where the user does not know how to spell the word. It translates the query into a consonant code, looks it up in the Metaphone dictionary, resolves ties with Edit Distance, and retrieves the documents.
* **Jaccard Similarity:** An alternative spelling corrector. It utilizes the k-gram index to pool candidates, but mathematically scores and selects the winner using the Jaccard Intersection over Union formula rather than Edit Distance operations.
* **Smart Search:** The ultimate, "Google-style" approach. It attempts an Exact Match first. If that fails, it simultaneously queries both the k-gram filter and the phonetic index, pooling all potential candidates into one massive set. It then runs Edit Distance across the entire pool to find the absolute best correction, completely abstracting the complexity away from the user.

---

## 7. Standardized System Output

Regardless of the search method or tab selected by the user, the final step of the retrieval pipeline is standardized across the entire application. Once the engine finalizes the exact match or determines the best spelling/phonetic correction, it queries the main inverted index and outputs the results in a clean, readable format. For every successfully matched document, each tab returns:

> * **Score:** The relevance ranking based on Term Frequency (TF).
> * **DocID:** The unique identifier for the document in the database.
> * **Title:** The name of the scientific diet or article.

*(Results are always displayed in descending order, ensuring the most mathematically relevant documents appear at the top).*
