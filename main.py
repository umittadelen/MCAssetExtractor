
import os
import json
import sys
import subprocess

# Auto-install tkinter if not present
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    print("tkinter not found. Attempting to install...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tk'])
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

import shutil
import threading

USER = os.getlogin()
INDEXES_DIR = fr"C:\\Users\\{USER}\\AppData\\Roaming\\.minecraft\\assets\\indexes"
OBJECTS_DIR = fr"C:\\Users\\{USER}\\AppData\\Roaming\\.minecraft\\assets\\objects"

def get_index_files():
    return [f for f in os.listdir(INDEXES_DIR) if f.endswith('.json')]


def extract_files(index_file, save_dir, progress_callback=None, done_callback=None):
    with open(os.path.join(INDEXES_DIR, index_file), encoding='utf-8') as f:
        data = json.load(f)
    objects = data.get('objects', {})
    output_dir = os.path.join(save_dir, 'output')
    total = len(objects)
    for i, (name, info) in enumerate(objects.items(), 1):
        h = info['hash']
        src = os.path.join(OBJECTS_DIR, h[:2], h)
        dst = os.path.join(output_dir, name.replace('/', os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            shutil.copy2(src, dst)
        except Exception:
            pass
        if progress_callback:
            progress_callback(i, total)
    if done_callback:
        done_callback(total, output_dir)


def run_gui():
    root = tk.Tk()
    root.title("MC Asset Extractor")
    root.geometry("370x220")

    tk.Label(root, text="Index JSON:").pack(pady=5)
    index_var = tk.StringVar()
    index_files = get_index_files()
    dropdown = tk.OptionMenu(root, index_var, *index_files)
    dropdown.pack(pady=2)
    if index_files:
        index_var.set(index_files[0])

    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)
    progress_label = tk.Label(root, text="")
    progress_label.pack()

    def update_progress(current, total):
        progress["maximum"] = total
        progress["value"] = current
        progress_label.config(text=f"{current}/{total} files extracted")
        root.update_idletasks()

    def on_done(total, output_dir):
        progress_label.config(text=f"Done! {total} files extracted.")
        messagebox.showinfo("Done", f"Extracted {total} files to {output_dir}.")

    def on_extract():
        idx = index_var.get()
        if not idx:
            messagebox.showwarning("Select file", "Choose an index JSON file.")
            return
        outdir = filedialog.askdirectory(title="Select output folder")
        if outdir:
            progress["value"] = 0
            progress_label.config(text="Starting...")
            t = threading.Thread(target=extract_files, args=(idx, outdir, update_progress, on_done), daemon=True)
            t.start()

    tk.Button(root, text="Extract", command=on_extract, width=15).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
