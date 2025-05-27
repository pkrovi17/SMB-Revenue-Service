
import tkinter as tk
from tkinter import filedialog
import subprocess
import threading
import webbrowser

# Theme
BG_COLOR = "#1e1e1e"
FG_COLOR = "#f5c147"
BTN_COLOR = "#2d2d2d"
BTN_HOVER = "#3a3a3a"
FONT = ("Segoe UI", 11)



def extract_and_launch(path_or_url, mode):
    show_processing_screen()
    subprocess.run(['python', 'extract3.py', path_or_url, mode])
    threading.Thread(target=launch_dashboard).start()

def launch_dashboard():
    subprocess.Popen(['python', 'dashboard3.py'])
    root.after(1000, show_dashboard_link)

def show_dashboard_link():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="✅ Dashboard Ready!", font=("Segoe UI", 16, "bold"),
             bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)

    link = tk.Label(root, text="👉 Open Dashboard", font=("Segoe UI", 12, "underline"),
                    bg=BG_COLOR, fg=FG_COLOR, cursor="hand2")
    link.pack()
    link.bind("<Button-1>", lambda e: webbrowser.open("http://127.0.0.1:8050"))

    tk.Label(root, text="Leave this window open while using the dashboard.",
             bg=BG_COLOR, fg="#cccccc", font=FONT).pack(pady=10)

    tk.Button(root, text="Exit", font=FONT,
              bg=BTN_COLOR, fg=FG_COLOR, relief="flat", command=root.quit).pack(pady=20)

def select_file():
    filepath = filedialog.askopenfilename(
        title="Select Spreadsheet",
        filetypes=[("Spreadsheet files", "*.xlsx *.xls *.csv"), ("All files", "*.*")]
    )
    if filepath:
        threading.Thread(target=extract_and_launch, args=(filepath, selected_mode.get())).start()

def submit_google_sheet():
    url = url_entry.get().strip()
    if "docs.google.com" in url:
        threading.Thread(target=extract_and_launch, args=(url, selected_mode.get())).start()

def on_hover(e):
    e.widget['bg'] = BTN_HOVER

def off_hover(e):
    e.widget['bg'] = BTN_COLOR

def show_processing_screen():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="Processing with LLaMA 3...", font=("Segoe UI", 16, "bold"),
             bg=BG_COLOR, fg=FG_COLOR).pack(expand=True)

# --- GUI Setup ---
root = tk.Tk()
root.title("Financial Dashboard Generator")
root.configure(bg=BG_COLOR)
root.geometry("500x380")
root.resizable(False, False)
selected_mode = tk.StringVar(value="summary")

tk.Label(root, text="📈 Convert Financial Sheets to Dashboards", font=("Segoe UI", 14, "bold"),
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)

# Radio Buttons for Mode
tk.Label(root, text="Select Analysis Mode:", font=FONT,
         bg=BG_COLOR, fg=FG_COLOR).pack()
modes = [("📊 Summary (Annual Report)", "summary"), ("📈 Forecast (Time Series)", "forecast")]
for label, val in modes:
    rb = tk.Radiobutton(root, text=label, variable=selected_mode, value=val, bg=BG_COLOR,
                        fg=FG_COLOR, selectcolor=BG_COLOR, font=FONT, activebackground=BG_COLOR)
    rb.pack(anchor="w", padx=50)

file_btn = tk.Button(root, text="📂 Select Excel/CSV File", font=FONT,
                     bg=BTN_COLOR, fg=FG_COLOR, relief="flat", command=select_file)
file_btn.pack(pady=10, ipadx=10, ipady=5)
file_btn.bind("<Enter>", on_hover)
file_btn.bind("<Leave>", off_hover)

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

tk.Label(root, text="Powered by Ollama, LLaMA 3 & Plotly Dash", font=("Segoe UI", 9),
         bg=BG_COLOR, fg="#888888").pack(side="bottom", pady=10)

root.mainloop()
