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
    
    # Header Label
    ttk.Label(frame, text=description, font=("Helvetica", 12, "bold")).pack(pady=15)
    
    search_frame = ttk.Frame(frame)
    search_frame.pack(pady=5)
    
    # Search Entry
    entry = ttk.Entry(search_frame, width=40, font=("Helvetica", 12))
    entry.pack(side=tk.LEFT, padx=10)
    
    # Stylish Text Box (Dark mode with Monospaced font for aligned columns)
    result_box = tk.Text(frame, height=15, width=70, font=("Consolas", 11), 
                         bg="#282c34", fg="#abb2bf", insertbackground="white", 
                         relief=tk.FLAT, padx=10, pady=10)
                         
    # Search Button
    btn = ttk.Button(search_frame, text="Search", 
                     command=lambda: handle_search(entry, result_box, search_type))
    btn.pack(side=tk.LEFT)
    
    result_box.pack(pady=15)
    return frame

def main():
    root = tk.Tk()
    root.title("Information Retrieval Search Engine")
    root.geometry("650x550") # Expanded slightly to fit padding nicely
    
    # --- STYLING ---
    style = ttk.Style()
    
    # 'clam' is a cleaner base theme than the default Windows/Mac look
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    bg_color = "#f4f6f9" # Light slate/gray
    root.configure(bg=bg_color)
    
    # Apply colors to frames and labels
    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, foreground="#2c3e50")
    
    # Style the notebook (tabs)
    style.configure("TNotebook", background=bg_color, borderwidth=0)
    style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[10, 5], background="#e1e8ed", foreground="#7f8c8d")
    style.map("TNotebook.Tab", 
              background=[("selected", "#ffffff")], 
              foreground=[("selected", "#2980b9")]) # Blue text on active tab
              
    # Style the Search button
    style.configure("TButton", font=("Helvetica", 10, "bold"), background="#3498db", foreground="white", padding=5)
    style.map("TButton", background=[("active", "#2980b9")]) # Darker blue when clicked
    
    # --- GUI SETUP ---
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=15, pady=15)
    
    create_tab(notebook, "Exact Match", "exact", "Standard Inverted Index Search")
    create_tab(notebook, "Spelling", "spelling", "Tolerant Retrieval: k-grams + Edit Distance")
    create_tab(notebook, "Phonetic", "phonetic", "Tolerant Retrieval: Metaphone Matching")
    create_tab(notebook, "Smart Search", "smart", "Combined Engine: Exact Fallback to Tolerant Algorithms")
    create_tab(notebook, "Jaccard", "jaccard", "Tolerant Retrieval: Jaccard Coefficient Scoring")
    
    root.mainloop()

if __name__ == "__main__":
    main()