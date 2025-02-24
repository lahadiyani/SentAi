import tkinter as tk
from tkinter import ttk
from menus.play_store import open_playstore_menu

root = tk.Tk()
root.title("SentAI - Analisis Sentimen")
root.geometry("400x400")
root.minsize(400, 400)
root.resizable(True, True)
root.iconbitmap('assets/icon.ico')

header_frame = tk.Frame(root)
header_frame.pack(fill="x", pady=10)
tk.Label(header_frame, text="Halo, Selamat Datang!", font=("Arial", 14)).pack()

content_frame = tk.Frame(root, padx=20, pady=20)
content_frame.pack(fill="both", expand=True)
content_frame.grid_columnconfigure(0, weight=1)

tk.Label(content_frame, text="Pilih Menu:").grid(row=0, column=0, sticky="w", pady=5)

# Panggil fungsi open_playstore_menu(root) dengan command
ttk.Button(content_frame, text="Playstore Menu", command=lambda: open_playstore_menu(root)).grid(row=1, column=0, pady=5, sticky="ew")

root.mainloop()
