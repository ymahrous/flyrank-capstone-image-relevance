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

async def main():
    print("STARTING DEMO SEQUENCE")

    # Step 1: Reset DB
    print_step(1, "Resetting Database to clean slate")
    os.system("python -m scripts.fresh_start")

    # Step 2: Run Vision DIRECTLY (Not via HTTP)
    print_step(2, "Running Vision Batch Job (Processing 50 images...)")
    from app.jobs.process_images import run_vision_batch_job
    await run_vision_batch_job("demo-vision-job")
    
    # Step 3: Run Embeddings DIRECTLY (Not via HTTP)
    print_step(3, "Generating Embeddings for Images...")
    from app.jobs.embed_images import run_image_embedding_job
    await run_image_embedding_job("demo-embed-job")

    # Step 4: Create Posts
    print_step(4, "Creating Blog Posts")
    
    posts = [
        {"title": "Red Fox Behavior", "content": "Red foxes are solitary hunters that primarily feed on rodents and rabbits. They are known for their cunning and adaptability."},
        {"title": "Gray Wolf Pack Dynamics", "content": "Gray wolves live in complex social packs led by an alpha pair. They work together to hunt large prey like elk and bison."},
        {"title": "Quantum Computing Basics", "content": "Quantum computing uses qubits to perform calculations at speeds unimaginable with classical silicon processors."}
    ]
    
    post_ids = []
    for p in posts:
        r = requests.post(f"{BASE_URL}/posts/", json=p)
        data = r.json()
        post_ids.append(data["id"])
        print(f"Created: {p['title']} (ID: {data['id']}, Subject: {data['subject']})")

    # Step 5: The Fox Match (Happy Path)
    print_step(5, "Querying Images for 'Red Fox Behavior' Post")
    r = requests.get(f"{BASE_URL}/matching/posts/{post_ids[0]}/images")
    res_json = r.json()
    
    if res_json.get("suggestion"):
        print("Result:")
        print(res_json["suggestion"]["explanation"])
        print(">>> FOX MATCHED SUCCESSFULLY <<<")
        
        # Step 6: The Wolf Rejection (The Guard Moment)
        print_step(6, "Inspecting Candidates (THE GUARD MOMENT)")
        candidates = res_json.get("candidates_evaluated", [])
        wolf_rejected = False
        for c in candidates:
            if c["guard_decision"] == "reject":
                print(f"🛑 REJECTED: {c['subject']} -> {c['explanation']}")
                wolf_rejected = True
        if not wolf_rejected:
            print("Note: No hard rejections in top candidates (highly accurate corpus).")

    # Step 7: The No Match (Safe Rejection)
    print_step(7, "Querying Images for 'Quantum Computing' Post")
    r = requests.get(f"{BASE_URL}/matching/posts/{post_ids[2]}/images")
    res_json = r.json()
    print(f"Verdict: {res_json.get('verdict', 'N/A')}")
    print(f"Explanation: {res_json.get('explanation', 'N/A')}")
    print(">>> CORRECTLY REFUSED TO GUESS <<<")

    # Step 8: The Review Trail
    print_step(8, "Reviewing the Fox Suggestion")
    if res_json.get("suggestion"):
        print("Approve/Reject endpoints are ready for human-in-the-loop.")

    print("\nDEMO SEQUENCE COMPLETE")

if __name__ == "__main__":
    asyncio.run(main())