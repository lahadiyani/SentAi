from google_play_scraper import reviews

def fetch_google_play_comments(app_package, limit=100):
    """Mengambil komentar dari Google Play Store berdasarkan package name."""
    try:
        result, _ = reviews(
            app_package,
            lang='id',  # Bisa ganti sesuai kebutuhan ('en' untuk Inggris)
            country='id',
            count=limit
        )
        return [r['content'] for r in result]  # Ambil hanya isi komentarnya
    except Exception as e:
        print(f"Error mengambil komentar: {e}")
        return []
