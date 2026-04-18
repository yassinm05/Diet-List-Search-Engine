import tkinter as tk
from tkinter import ttk
import Search_controller as sc

def handle_search(entry_widget, result_box, search_type):
    query = entry_widget.get().strip()
    if not query:
        return
        
    result_box.delete(1.0, tk.END) 
    
    # Delegate all the hard work to the controller
    if search_type == "exact":
        results = sc.run_exact_search(query)
    elif search_type == "spelling":
        results = sc.run_spelling_search(query)
    elif search_type == "phonetic":
        results = sc.run_phonetic_search(query)
    elif search_type == "smart":
        results = sc.run_smart_search(query)
    elif search_type == "jaccard":
        results = sc.run_jaccard_search(query)
        
    result_box.insert(tk.END, results)

def create_tab(notebook, title, search_type, description):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=title)
    
    ttk.Label(frame, text=description, font=("Arial", 12)).pack(pady=10)
    
    search_frame = ttk.Frame(frame)
    search_frame.pack(pady=5)
    
    entry = ttk.Entry(search_frame, width=40, font=("Arial", 12))
    entry.pack(side=tk.LEFT, padx=5)
    
    result_box = tk.Text(frame, height=15, width=60, font=("Arial", 11))
    
    btn = ttk.Button(search_frame, text="Search", 
                     command=lambda: handle_search(entry, result_box, search_type))
    btn.pack(side=tk.LEFT)
    
    result_box.pack(pady=15)
    return frame

def main():
    root = tk.Tk()
    root.title("Information Retrieval Search Engine")
    root.geometry("600x500")
    
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=10, pady=10)
    
    create_tab(notebook, "Exact Match", "exact", "Standard Inverted Index Search")
    create_tab(notebook, "Spelling (k-grams)", "spelling", "Tolerant Retrieval: k-grams + Edit Distance")
    create_tab(notebook, "Phonetic (Metaphone)", "phonetic", "Tolerant Retrieval: Metaphone Matching")
    create_tab(notebook, "Smart Search", "smart", "Combined Engine: Exact Fallback to Tolerant Algorithms")
    create_tab(notebook, "Jaccard Similarity", "jaccard", "Tolerant Retrieval: Jaccard Coefficient Scoring")
    
    root.mainloop()

if __name__ == "__main__":
    main()