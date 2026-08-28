import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import os
import sys

# Import the processing logic from your other file
from processor import run_batch

# --- FIX FOR WINDOWS VENV TKINTER BUG ---
# Only apply this fix if running from Python directly, NOT when packaged as an .exe
if sys.platform == 'win32' and not getattr(sys, 'frozen', False):
    os.environ['TCL_LIBRARY'] = os.path.join(sys.base_prefix, 'tcl', 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(sys.base_prefix, 'tcl', 'tk8.6')
def select_input_folder():
    folder_path = filedialog.askdirectory(title="Select Snapchat Memories Folder")
    if folder_path:
        input_path_var.set(folder_path)

def select_output_folder():
    folder_path = filedialog.askdirectory(title="Select Where to Save Combined Files")
    if folder_path:
        output_path_var.set(folder_path)

def safe_log_update(message):
    # Tkinter isn't thread-safe. root.after forces the main GUI thread to update the text box safely.
    root.after(0, append_to_log, message)

def append_to_log(message):
    log_box.config(state="normal") # Enable editing
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)            # Auto-scroll to bottom
    log_box.config(state="disabled") # Disable editing

def process_thread_target(input_dir, output_dir):
    try:
        # Run the heavy processing
        run_batch(input_dir, output_dir, safe_log_update)
    except Exception as e:
        safe_log_update(f"Critical error: {e}")
    finally:
        # Re-enable the start button when done
        root.after(0, lambda: start_btn.config(state="normal", text="Start Processing"))

def start_processing():
    input_dir = input_path_var.get()
    output_dir = output_path_var.get()
    
    if not input_dir or not output_dir:
        safe_log_update("Error: Please select both folders first.")
        return
        
    # Disable the button to prevent clicking it twice
    start_btn.config(state="disabled", text="Processing... Please wait.")
    
    # Clear the log box
    log_box.config(state="normal")
    log_box.delete(1.0, tk.END)
    log_box.config(state="disabled")
    
    safe_log_update(f"Reading from: {input_dir}")
    safe_log_update(f"Saving to: {output_dir}\n")
    
    # Spawn a background thread so the GUI doesn't freeze
    # daemon=True means if the user closes the app, this thread stops instantly
    thread = threading.Thread(target=process_thread_target, args=(input_dir, output_dir), daemon=True)
    thread.start()

# --- Main Window Setup ---
root = tk.Tk()
root.title("Snapchat-Taikuri 67")
root.geometry("600x500")
root.config(padx=20, pady=20)

input_path_var = tk.StringVar()
output_path_var = tk.StringVar()

# --- UI Elements ---
tk.Label(root, text="Mistä kansiosta haluat ladata tiedostot?").pack(anchor="w")
tk.Button(root, text="Selaa", command=select_input_folder).pack(anchor="w", pady=2)
tk.Label(root, textvariable=input_path_var, fg="blue").pack(anchor="w", pady=(0, 10))

tk.Label(root, text="Mihin kansioon haluat ladata tiedostot?").pack(anchor="w")
tk.Button(root, text="Selaa", command=select_output_folder).pack(anchor="w", pady=2)
tk.Label(root, textvariable=output_path_var, fg="blue").pack(anchor="w", pady=(0, 15))

start_btn = tk.Button(root, text="Seesam aukene! (Aloita prosessointi)", command=start_processing, bg="green", fg="white", font=("Arial", 11, "bold"))
start_btn.pack(fill="x", pady=5)

# Log/Console window
tk.Label(root, text="Activity Log:").pack(anchor="w", pady=(10, 0))
log_box = scrolledtext.ScrolledText(root, height=12, state="disabled", bg="#f4f4f4")
log_box.pack(fill="both", expand=True)

# Run the app
root.mainloop()