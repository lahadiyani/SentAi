import requests
import urllib.parse
from collections import Counter

sentiment_counter = Counter({'positif': 0, 'negatif': 0, 'netral': 0})

def analyze_sentiment(comment, prompt):
    if "oke" in comment.lower():
        return "netral"
    
    encoded_prompt = urllib.parse.quote(prompt)
    encoded_comment = urllib.parse.quote(comment)
    url = f"https://text.pollinations.ai/{encoded_prompt} {encoded_comment}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            result = response.text.strip().lower()
            if "positif" in result:
                sentiment = "positif"
            elif "negatif" in result:
                sentiment = "negatif"
            else:
                sentiment = "netral"
            sentiment_counter[sentiment] += 1
            return sentiment
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Terjadi kesalahan: {e}"
