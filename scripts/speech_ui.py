import tkinter as tk
from tkinter import scrolledtext
import threading

from speech_controller import run_speech_to_text


def update_status(msg):
    status_label.config(text=f"Status: {msg}")


def run_stt():
    try:
        update_status("Recording...")

        
        text = run_speech_to_text()

        transcript_box.delete("1.0", tk.END)
        transcript_box.insert(tk.END, text)

        update_status("Done")

    except Exception as e:
        update_status(f"Error: {e}")
        print(f"[DEBUG ERROR] {e}")


def start_stt():
    threading.Thread(target=run_stt, daemon=True).start()


root = tk.Tk()
root.title("Speech to Text")

record_button = tk.Button(root, text="Start Recording", command=start_stt)
record_button.pack(pady=10)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack()

transcript_box = scrolledtext.ScrolledText(root, width=60, height=15)
transcript_box.pack(padx=10, pady=10)

root.mainloop()