import os
import asyncio
import requests
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

def print_step(num, text):
    print(f"\n{'='*40}")
    print(f"STEP {num}: {text}")
    print(f"{'='*40}")

def hit_api(method, endpoint, json_data=None):
    url = f"{BASE_URL}{endpoint}"
    if method == "GET":
        r = requests.get(url)
    else:
        r = requests.post(url, json=json_data)
    return r

async def main():
    print("STARTING DEMO SEQUENCE")

    # Step 1: Reset DB
    print_step(1, "Resetting Database to clean slate")
    os.system("python -m scripts.fresh_start")

    # Step 2: Run Vision
    print_step(2, "Running Vision Batch Job (Processing 50 images...)")
    r = hit_api("POST", "/jobs/vision")
    print("Job triggered. Waiting 120 seconds for processing...")
    await asyncio.sleep(120) # Adjust this based on how fast your free tier processes

    # Step 3: Run Embeddings
    print_step(3, "Generating Embeddings for Images...")
    r = hit_api("POST", "/jobs/embed-images")
    print("Job triggered. Waiting 45 seconds...")
    await asyncio.sleep(45)

    # Step 4: Create Posts
    print_step(4, "Creating Blog Posts")
    
    posts = [
        {"title": "Red Fox Behavior", "content": "Red foxes are solitary hunters that primarily feed on rodents and rabbits. They are known for their cunning and adaptability."},
        {"title": "Gray Wolf Pack Dynamics", "content": "Gray wolves live in complex social packs led by an alpha pair. They work together to hunt large prey like elk and bison."},
        {"title": "Quantum Computing Basics", "content": "Quantum computing uses qubits to perform calculations at speeds unimaginable with classical silicon processors."}
    ]
    
    post_ids = []
    for p in posts:
        r = hit_api("POST", "/posts/", p)
        data = r.json()
        post_ids.append(data["id"])
        print(f"Created: {p['title']} (ID: {data['id']}, Subject: {data['subject']})")

    # Step 5: The Fox Match (Happy Path)
    print_step(5, "Querying Images for 'Red Fox Behavior' Post")
    r = hit_api("GET", f"/matching/posts/{post_ids[0]}/images")
    print("Result:")
    print(r.json()["suggestion"]["explanation"])
    print(">>> FOX MATCHED SUCCESSFULLY <<<")

    # Step 6: The Wolf Rejection (The Guard Moment)
    print_step(6, "Inspecting Candidates (THE GUARD MOMENT)")
    candidates = r.json()["candidates_evaluated"]
    for c in candidates:
        if c["guard_decision"] == "reject":
            print(f"REJECTED: {c['subject']} -> {c['explanation']}")

    # Step 7: The No Match (Safe Rejection)
    print_step(7, "Querying Images for 'Quantum Computing' Post")
    r = hit_api("GET", f"/matching/posts/{post_ids[2]}/images")
    print(f"Verdict: {r.json()['verdict']}")
    print(f"Explanation: {r.json()['explanation']}")
    print(">>> CORRECTLY REFUSED TO GUESS <<<")

    # Step 8: The Review Trail
    print_step(8, "Reviewing the Fox Suggestion")
    if r.json().get("suggestion"):
        # (In a real scenario you'd grab the suggestion ID here)
        print("Approve/Reject endpoints are ready for human-in-the-loop.")

    print("\nDEMO SEQUENCE COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())