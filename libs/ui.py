import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading
import time
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from libs.sentiment_analysis import analyze_sentiment, sentiment_counter
from libs.file_handler import load_comments, save_progress, detect_encoding
from libs.google_play_handler import fetch_google_play_comments  # Import fitur Google Play

# Setup logging
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/app.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

processed_comments = []
is_processing = False
global_output_file = None  # Path file output

def extract_google_play_id(link):
    match = re.search(r"id=([a-zA-Z0-9._-]+)", link)
    return match.group(1) if match else None

def process_comments(comments, output_file, prompt, delay, progress_var, result_label, top_window, text_box, chart, chart_canvas):
    global is_processing, processed_comments
    is_processing = True
    total_comments = len(comments)
    logging.info(f"Mulai memproses {total_comments} komentar...")
    
    for idx, comment in enumerate(comments, start=1):
        if not is_processing:
            logging.info("Proses dihentikan oleh user.")
            break

        # Analisis sentimen untuk setiap komentar
        sentiment = analyze_sentiment(comment, prompt)
        processed_comments.append((comment, sentiment))
        logging.debug(f"Komentar: {comment} | Sentimen: {sentiment}")

        # Perbarui text box (gunakan after untuk update secara thread-safe)
        text_box.after(0, lambda c=comment, s=sentiment: update_text_box(text_box, c, s))

        # Perbarui progress bar dan label
        progress = (idx / total_comments) * 100
        progress_var.set(progress)
        result_label.config(text=f"Sentimen Diproses: {idx} / {total_comments}")

        # Perbarui grafik
        update_chart(chart, chart_canvas)

        top_window.update_idletasks()
        time.sleep(delay)

    # Setelah selesai, simpan hasil
    if save_progress(output_file, processed_comments):
        messagebox.showinfo("Info", f"Progres berhasil disimpan ke '{output_file}'.")
        logging.info(f"Progres berhasil disimpan ke '{output_file}'.")
    else:
        messagebox.showerror("Error", "Gagal menyimpan progres.")
        logging.error("Gagal menyimpan progres saat menyelesaikan proses.")

    is_processing = False
    top_window.destroy()

def update_text_box(text_box, comment, sentiment):
    text_box.config(state=tk.NORMAL)
    text_box.insert(tk.END, f"Komentar: '{comment}' => Sentimen: {sentiment}\n")
    text_box.yview(tk.END)
    text_box.config(state=tk.DISABLED)

def update_chart(chart, canvas):
    chart.clear()
    labels = ['Positif', 'Negatif', 'Netral']
    sizes = [sentiment_counter['positif'], sentiment_counter['negatif'], sentiment_counter['netral']]
    chart.bar(labels, sizes, color=['green', 'red', 'blue'])
    chart.set_title('Distribusi Sentimen')
    chart.set_ylabel('Jumlah Komentar')
    chart.set_ylim(0, max(sizes) + 1)
    canvas.draw()

def start_process(link=None, count=100):
    global processed_comments, is_processing, global_output_file
    processed_comments = []

    def start_analysis(comments):
        global global_output_file
        output_file = filedialog.asksaveasfilename(title="Simpan file output CSV", defaultextension=".csv")
        if not output_file:
            logging.warning("User tidak memilih file output.")
            return

        global_output_file = output_file
        logging.info(f"Output file disimpan: {global_output_file}")

        prompt = "Analisa emosi yang terkandung dalam komentar berikut. Tentukan apakah komentar tersebut menunjukkan emosi negatif, positif, atau netral. Jawab dengan tepat hanya dengan satu kata: 'negatif', 'positif', atau 'netral'. Perhatikan kata-kata yang menyiratkan perasaan seperti marah, kecewa, bahagia, atau pujian. Contoh: jika komentar mengandung kata-kata kasar atau menyatakan kekecewaan, jawab 'negatif'; jika berisi pujian atau ungkapan bahagia, jawab 'positif'; dan jika komentar tidak menunjukkan emosi yang kuat, jawab 'netral'."

        top_window = tk.Toplevel()
        top_window.title("Monitoring Proses")
        top_window.geometry("600x500")

        progress_var = tk.DoubleVar()
        ttk.Progressbar(top_window, variable=progress_var, maximum=100, length=300).pack(pady=10, padx=20)

        result_label = tk.Label(top_window, text="Sentimen Diproses: 0 / 0", anchor="w")
        result_label.pack(pady=10, padx=20)

        text_box = tk.Text(top_window, height=10, width=70, wrap=tk.WORD)
        text_box.pack(pady=10, padx=20, fill="both", expand=True)
        text_box.config(state=tk.DISABLED)

        fig, chart = plt.subplots(figsize=(6, 3))
        chart_canvas = FigureCanvasTkAgg(fig, master=top_window)
        chart_canvas.get_tk_widget().pack(pady=10, padx=20, fill="both", expand=True)

        threading.Thread(target=process_comments, args=(
            comments, output_file, prompt, 1, progress_var, result_label, top_window, text_box, chart, chart_canvas
        )).start()

    # Jika diberikan link, ekstrak App ID dan ambil komentar
    if link:
        app_id = extract_google_play_id(link)
        if not app_id:
            messagebox.showerror("Error", "URL tidak valid! Harap masukkan link Google Play yang benar.")
            return
        logging.info(f"Mengambil komentar dari Google Play untuk App ID: {app_id}")
        comments = fetch_google_play_comments(app_id, limit=count)
        if not comments:
            messagebox.showerror("Error", "Gagal mengambil komentar dari Google Play.")
            return
        start_analysis(comments)
    else:
        # Jika tidak ada link, gunakan pilihan manual
        choice = messagebox.askquestion("Pilih Metode Input", 
                                        "Gunakan Google Play Store untuk mengambil komentar? (Yes = Google Play, No = CSV)")
        if choice == 'yes':
            app_url = simpledialog.askstring("Input", "Masukkan Link Aplikasi Google Play:")
            app_id = extract_google_play_id(app_url)
            if not app_id:
                messagebox.showerror("Error", "URL tidak valid! Masukkan link yang benar.")
                return
            comments = fetch_google_play_comments(app_id, limit=100)
        else:
            input_file = filedialog.askopenfilename(title="Pilih file CSV input")
            if not input_file:
                logging.warning("User tidak memilih file input.")
                return
            comments = load_comments(input_file)

        start_analysis(comments)

def stop_process():
    global is_processing, global_output_file
    is_processing = False
    logging.info("User menekan tombol Hentikan Proses.")

    if global_output_file and processed_comments:
        if save_progress(global_output_file, processed_comments):
            messagebox.showinfo("Info", f"Progres berhasil disimpan ke '{global_output_file}'.")
            logging.info(f"Progres berhasil disimpan ke '{global_output_file}'.")
        else:
            messagebox.showerror("Error", "Gagal menyimpan progres.")
            logging.error("Gagal menyimpan progres saat menghentikan proses.")

    messagebox.showinfo("Info", "Proses dihentikan. Program akan keluar.")
    logging.info("Program dihentikan oleh user.")
    sys.exit()
