import csv
import chardet
from tkinter import messagebox

def detect_encoding(file_path, sample_size=2048):
    """Mendeteksi encoding file dengan membaca sebagian isi file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    confidence = result['confidence']
    print(f"[DEBUG] Detected encoding: {encoding}, confidence: {confidence}")
    if not encoding:
        encoding = 'utf-8'
    return encoding

def detect_delimiter(file_path, encoding):
    """Mendeteksi delimiter yang digunakan dalam CSV (, atau ;)"""
    with open(file_path, 'r', encoding=encoding, errors='replace') as file:
        first_line = file.readline()
        if ";" in first_line and "," not in first_line:
            return ";"
        return ","

def find_comment_column(headers):
    """Cari kolom yang kemungkinan berisi komentar."""
    candidates = ['content', 'comment', 'komentar', 'review', 'text', 'message', 'body']
    for col in candidates:
        if col in headers:
            return col
    # Kalau tidak ada yang cocok, ambil kolom kedua atau pertama
    return headers[1] if len(headers) > 1 else headers[0]

def load_comments(input_file):
    """Membaca file CSV dengan beberapa fallback encoding jika gagal."""
    try:
        # 1. Deteksi encoding dengan chardet
        detected_encoding = detect_encoding(input_file)
        encodings_to_try = [
            detected_encoding,
            'utf-8-sig',    # fallback 1
            'iso-8859-1',   # fallback 2
        ]

        data = []
        delimiter = None
        used_encoding = None

        for enc in encodings_to_try:
            try:
                print(f"[DEBUG] Mencoba encoding: {enc}")
                with open(input_file, 'r', encoding=enc, errors='replace') as f:
                    # Deteksi delimiter dengan encoding yang sedang dicoba
                    delim = detect_delimiter(input_file, enc)
                    f.seek(0)  # Kembalikan pointer ke awal file
                    csv_reader = csv.reader(f, delimiter=delim)
                    data = list(csv_reader)
                # Jika berhasil dibaca tanpa error, set delimiter & encoding
                delimiter = delim
                used_encoding = enc
                break
            except UnicodeDecodeError as e:
                print(f"[DEBUG] Gagal decode dengan {enc}: {e}")
                continue

        # Jika semua encoding di atas gagal, coba terakhir dengan ignore
        if not data:
            try:
                print("[DEBUG] Mencoba encoding: utf-8 + ignore")
                with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                    delim = detect_delimiter(input_file, 'utf-8')
                    f.seek(0)
                    csv_reader = csv.reader(f, delimiter=delim)
                    data = list(csv_reader)
                delimiter = delim
                used_encoding = 'utf-8 (ignore)'
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file dengan berbagai encoding: {e}")
                return []

        print(f"[DEBUG] Encoding final yang digunakan: {used_encoding}")
        print(f"[DEBUG] Delimiter final yang digunakan: {delimiter}")

        # 2. Validasi data
        if not data:
            messagebox.showerror("Error", "File CSV kosong.")
            return []

        headers = data[0]
        print(f"[DEBUG] Header CSV: {headers}")

        if len(data) < 2:
            messagebox.showerror("Error", "Tidak ada data di dalam file CSV.")
            return []

        # 3. Cari kolom komentar
        comment_col = find_comment_column(headers)
        print(f"[DEBUG] Kolom komentar terdeteksi: {comment_col}")

        try:
            col_index = headers.index(comment_col)
        except ValueError:
            messagebox.showerror("Error", f"Kolom '{comment_col}' tidak ditemukan di header.")
            return []

        # 4. Ambil data dari kolom yang dipilih
        comments = [row[col_index].strip()
                    for row in data[1:]
                    if len(row) > col_index and row[col_index].strip()]

        print(f"[DEBUG] Total komentar ditemukan: {len(comments)}")

        if not comments:
            messagebox.showerror("Error", "Tidak ada komentar ditemukan dalam file.")
            return []

        return comments

    except Exception as e:
        messagebox.showerror("Error", f"Gagal membaca file: {e}")
        return []

def save_progress(output_file, comments):
    """Menyimpan hasil analisis sentimen ke dalam file CSV."""
    try:
        with open(output_file, mode='w', encoding='utf-8', newline='') as output_csv:
            fieldnames = ['comment', 'sentiment']
            writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
            writer.writeheader()
            for comment, sentiment in comments:
                writer.writerow({'comment': comment, 'sentiment': sentiment})
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan progres: {e}")
        return False
