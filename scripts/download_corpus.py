import os
import json
import requests
import time

CORPUS_DIR = "data/images"
MANIFEST_PATH = "data/manifest.json"

def download_corpus():
    os.makedirs(CORPUS_DIR, exist_ok=True)
    
    with open(MANIFEST_PATH, "r") as f:
        images = json.load(f)

    headers = {"User-Agent": "Mozilla/5.0"}
    
    for img in images:
        filename = f"{img['id']}.jpg"
        filepath = os.path.join(CORPUS_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"Skipping {filename}, already exists.")
            continue
            
        print(f"Downloading {filename}...")
        try:
            r = requests.get(img["url"], headers=headers, timeout=15)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(r.content)
            time.sleep(0.5) # Be polite to Unsplash
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            
    print("Corpus download complete.")

if __name__ == "__main__":
    download_corpus()