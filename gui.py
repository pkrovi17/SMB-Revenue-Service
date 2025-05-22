import tkinter as tk
from tkinter import filedialog
import subprocess
import threading

# Colors
BG_COLOR = "#1e1e1e"
FG_COLOR = "#f5c147"
BTN_COLOR = "#2d2d2d"
BTN_HOVER = "#3a3a3a"
FONT = ("Segoe UI", 11)

# Run the processing logic and exit
def run_and_exit(path_or_url):
    show_processing_screen()
    subprocess.run(['python', 'extract.py', path_or_url])
    root.quit()

def select_file():
    filepath = filedialog.askopenfilename(
        title="Select File",
        filetypes=[("Spreadsheet files", "*.xlsx *.xls *.csv"), ("All files", "*.*")]
    )
    if filepath:
        threading.Thread(target=run_and_exit, args=(filepath,)).start()

def submit_google_sheet():
    url = url_entry.get().strip()
    if "docs.google.com" in url:
        threading.Thread(target=run_and_exit, args=(url,)).start()

def on_hover(e):
    e.widget['bg'] = BTN_HOVER

def off_hover(e):
    e.widget['bg'] = BTN_COLOR

def show_processing_screen():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="Processing...", font=("Segoe UI", 16, "bold"),
             bg=BG_COLOR, fg=FG_COLOR).pack(expand=True)

# --- GUI Setup ---
root = tk.Tk()
root.title("🧾 Financial Sheet Processor")
root.configure(bg=BG_COLOR)
root.geometry("500x280")
root.resizable(False, False)

# Title
tk.Label(root, text="Convert Financial Sheets to JSON", font=("Segoe UI", 14, "bold"),
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)

# File Button
file_btn = tk.Button(root, text="📂 Select Excel/CSV File", font=FONT,
                     bg=BTN_COLOR, fg=FG_COLOR, relief="flat", command=select_file)
file_btn.pack(pady=10, ipadx=10, ipady=5)
file_btn.bind("<Enter>", on_hover)
file_btn.bind("<Leave>", off_hover)

# Google Sheets Input
tk.Label(root, text="Or paste Google Sheets URL:", font=FONT,
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=(20, 5))

url_entry = tk.Entry(root, font=FONT, bg="#2b2b2b", fg=FG_COLOR,
                     insertbackground=FG_COLOR, relief="flat", width=50)
url_entry.pack(ipady=5)

url_btn = tk.Button(root, text="🌐 Process Google Sheet", font=FONT,
                    bg=BTN_COLOR, fg=FG_COLOR, relief="flat", command=submit_google_sheet)
url_btn.pack(pady=10, ipadx=10, ipady=5)
url_btn.bind("<Enter>", on_hover)
url_btn.bind("<Leave>", off_hover)

# Footer
tk.Label(root, text="Powered by Ollama & LLaMA 3", font=("Segoe UI", 9),
         bg=BG_COLOR, fg="#888888").pack(side="bottom", pady=10)

root.mainloop()
