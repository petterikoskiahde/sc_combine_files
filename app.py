import os
import sys
import threading

if sys.platform == "win32" and not getattr(sys, "frozen", False):
    os.environ["TCL_LIBRARY"] = os.path.join(sys.base_prefix, "tcl", "tcl8.6")
    os.environ["TK_LIBRARY"] = os.path.join(sys.base_prefix, "tcl", "tk8.6")

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import processor


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Snapchat Taikuri")
        self.root.geometry("520x280")
        self.root.resizable(False, False)

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()

        # Event flag to signal the thread to stop
        self.cancel_event = threading.Event()

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Input Folder:").grid(
            row=0, column=0, sticky=tk.W, pady=4
        )
        ttk.Entry(frame, textvariable=self.input_dir, width=42).grid(
            row=0, column=1, padx=6, pady=4
        )
        ttk.Button(frame, text="Browse...", command=self._browse_input).grid(
            row=0, column=2, pady=4
        )

        ttk.Label(frame, text="Output Folder:").grid(
            row=1, column=0, sticky=tk.W, pady=4
        )
        ttk.Entry(frame, textvariable=self.output_dir, width=42).grid(
            row=1, column=1, padx=6, pady=4
        )
        ttk.Button(frame, text="Browse...", command=self._browse_output).grid(
            row=1, column=2, pady=4
        )

        self.progress_bar = ttk.Progressbar(
            frame, orient="horizontal", mode="determinate", length=480
        )
        self.progress_bar.grid(row=2, column=0, columnspan=3, pady=(20, 5))

        self.percent_label = ttk.Label(frame, text="0%", font=("Helvetica", 11, "bold"))
        self.percent_label.grid(row=3, column=0, columnspan=3)

        self.status_label = ttk.Label(
            frame, text="Ready", foreground="gray", wraplength=480
        )
        self.status_label.grid(row=4, column=0, columnspan=3, pady=4)

        # Button frame to hold both Start and Stop buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))

        self.start_btn = ttk.Button(
            btn_frame, text="Start Combining", command=self._start_processing
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            btn_frame, text="Stop", command=self._stop_processing, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def _browse_input(self):
        path = filedialog.askdirectory(title="Select Snapchat Memories Input Folder")
        if path:
            self.input_dir.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_dir.set(path)

    def _update_progress(self, current, total, message):
        def _apply():
            if total > 0:
                pct = int((current / total) * 100)
                self.progress_bar["value"] = pct
                self.percent_label.config(text=f"{pct}% ({current}/{total})")
            else:
                self.progress_bar["value"] = 0
                self.percent_label.config(text="0%")
            self.status_label.config(text=message)

        self.root.after(0, _apply)

    def _stop_processing(self):
        # Tell the thread to stop and disable the stop button so they can't spam it
        self.cancel_event.set()
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Stopping after current file finishes...")

    def _start_processing(self):
        inp = self.input_dir.get().strip()
        out = self.output_dir.get().strip()

        if not inp or not os.path.isdir(inp):
            messagebox.showerror("Error", "Please select a valid Input folder.")
            return
        if not out or not os.path.isdir(out):
            messagebox.showerror("Error", "Please select a valid Output folder.")
            return

        if os.path.abspath(inp) == os.path.abspath(out):
            messagebox.showerror(
                "Error",
                "Input and Output folders cannot be the exact same.\nPlease select a different Output folder.",
            )
            return

        # Reset the cancel event and toggle button states
        self.cancel_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.progress_bar["value"] = 0
        self.percent_label.config(text="0%")

        def worker():
            # Pass the cancel event to the processor
            processor.run_batch(inp, out, self._update_progress, self.cancel_event)

            # Re-enable Start button and disable Stop button when completely finished
            def reset_buttons():
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)

            self.root.after(0, reset_buttons)

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
