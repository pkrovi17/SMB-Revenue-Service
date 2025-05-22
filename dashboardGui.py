import tkinter as tk
import subprocess
import threading

# Theme Colors
BG_COLOR = "#1e1e1e"
FG_COLOR = "#f5c147"
BTN_COLOR = "#2d2d2d"
BTN_HOVER = "#3a3a3a"
FONT = ("Segoe UI", 11)

def run_dashboard():
    show_loading_screen()
    subprocess.run(['python', 'dashboard.py'])
    root.quit()

def on_hover(e):
    e.widget['bg'] = BTN_HOVER

def off_hover(e):
    e.widget['bg'] = BTN_COLOR

def show_loading_screen():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="Launching Dashboard...", font=("Segoe UI", 16, "bold"),
             bg=BG_COLOR, fg=FG_COLOR).pack(expand=True)

# --- GUI Setup ---
root = tk.Tk()
root.title("Dashboard Launcher")
root.configure(bg=BG_COLOR)
root.geometry("500x200")
root.resizable(False, False)

tk.Label(root, text="📊 View Financial Dashboards", font=("Segoe UI", 14, "bold"),
         bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)

launch_btn = tk.Button(root, text="📊 Launch Dashboard", font=FONT,
                       bg=BTN_COLOR, fg=FG_COLOR, relief="flat", command=lambda: threading.Thread(target=run_dashboard).start())
launch_btn.pack(pady=20, ipadx=10, ipady=5)
launch_btn.bind("<Enter>", on_hover)
launch_btn.bind("<Leave>", off_hover)

tk.Label(root, text="Powered by Ollama & Plotly Dash", font=("Segoe UI", 9),
         bg=BG_COLOR, fg="#888888").pack(side="bottom", pady=10)

root.mainloop()
