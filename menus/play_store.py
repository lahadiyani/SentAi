import tkinter as tk
from tkinter import ttk, messagebox
from libs.ui import start_process, stop_process

def open_playstore_menu(parent):
    """
    parent: Tk instance dari main menu
    """
    # Sembunyikan window utama
    parent.withdraw()
    
    # Buat window baru (Toplevel)
    playstore_win = tk.Toplevel(parent)
    playstore_win.title("Playstore Menu - Analisis Sentimen")
    playstore_win.geometry("400x450")
    playstore_win.iconbitmap('assets/icon.ico')
    playstore_win.resizable(True, True)

    content_frame = tk.Frame(playstore_win, padx=20, pady=20)
    content_frame.pack(fill="both", expand=True)
    content_frame.grid_columnconfigure(0, weight=1)

    # Input link Google Play
    link_label = tk.Label(content_frame, text="Masukkan Link Aplikasi:")
    link_label.grid(row=0, column=0, sticky="w", pady=5)
    link_entry = ttk.Entry(content_frame, width=40)
    link_entry.grid(row=1, column=0, pady=5, ipadx=10, ipady=3, sticky="ew")

    # Input jumlah komentar
    count_label = tk.Label(content_frame, text="Jumlah Komentar:")
    count_label.grid(row=2, column=0, sticky="w", pady=5)
    count_entry = ttk.Entry(content_frame, width=10)
    count_entry.grid(row=3, column=0, pady=5, ipadx=10, ipady=3, sticky="ew")

    # Fungsi untuk memulai proses dengan input link
    def start_with_link():
        link = link_entry.get().strip()
        count = count_entry.get().strip()
        
        if not link:
            messagebox.showerror("Error", "Link aplikasi tidak boleh kosong!")
            return
        if not count.isdigit() or int(count) <= 0:
            messagebox.showerror("Error", "Jumlah komentar harus berupa angka positif!")
            return
        
        # Memulai proses dengan data dari link
        start_process(link=link, count=int(count))

    # Tombol Mulai dengan CSV
    start_button = ttk.Button(content_frame, text="Mulai dengan CSV", command=start_process)
    start_button.grid(row=4, column=0, pady=10, ipadx=10, ipady=5, sticky="ew")

    # Tombol Mulai dengan Link Google Play
    start_link_button = ttk.Button(content_frame, text="Mulai dengan Link", command=start_with_link)
    start_link_button.grid(row=5, column=0, pady=10, ipadx=10, ipady=5, sticky="ew")

    # Tombol Hentikan Proses
    stop_button = ttk.Button(content_frame, text="Hentikan Proses", command=stop_process)
    stop_button.grid(row=6, column=0, pady=10, ipadx=10, ipady=5, sticky="ew")

    # Status
    status_label = tk.Label(content_frame, text="Status: Menunggu.", anchor="w", font=("Arial", 12))
    status_label.grid(row=7, column=0, pady=10, sticky="ew")

    # Fungsi untuk kembali ke menu utama
    def back_to_main_menu():
        # Tutup window Playstore
        playstore_win.destroy()
        # Tampilkan kembali root
        parent.deiconify()

    # Tombol Kembali ke Menu Utama
    back_button = ttk.Button(content_frame, text="Kembali ke Menu Utama", command=back_to_main_menu)
    back_button.grid(row=8, column=0, pady=10, ipadx=10, ipady=5, sticky="ew")
