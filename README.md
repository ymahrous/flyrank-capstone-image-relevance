# FlyRank Capstone: AI Image Understanding & Content Matching Engine

## Evaluation Metrics
**Top-1 Precision:** Measured via `python -m app.eval.run_eval` against a 9-pair labeled dataset.

## The Mission
A backend system that looks at an image library, understands what's actually in each image, and matches the right image to the right blog post based on meaning, not filenames. 

The core production feature is **the mismatch guard**. It combines extracted tags, semantic similarity thresholds, and confidence scores to refuse bad matches with a human-readable explanation. Good suggestions when confident, safe rejection when uncertain.

## Architecture
The system uses a layered architecture (HTTP -> Services -> Repositories) with parallel embedding streams that meet at a ranking step. Everything passes through the Mismatch Guard before being presented to a human.

```text
Images -> [Batch Job] -> Vision Model -> {tags, caption, confidence} -> DB
                                           \-> embed(caption) -> image_vectors

Posts  -> [Text Extract] -> {subject, category} -> DB
                             \-> embed(text)   -> post_vectors

GET /posts/:id/images
  -> Cosine Similarity Ranking (image_vectors x post_vector)
  -> Mismatch Guard (Subject Veto + Threshold + Confidence)
     |-> SUGGEST (with explanation)
     |-> REJECT (e.g., "Subject mismatch: expected fox, detected wolf")
     |-> NO_CONFIDENT_MATCH (e.g., "Similarity below threshold")
  -> Review API (Approve / Reject)
```

## Tech Stack ($0 Constraint)
- **Framework:** Python + FastAPI
- **Database:** PostgreSQL (Hosted on Neon free tier)
- **Vision Model:** `gemini-2.5-flash-image` (Free tier)
- **Text/Extraction Model:** `gemini-2.5-flash` (Free tier)
- **Embeddings:** `gemini-embedding-001` (Free tier)
- **Validation:** Pydantic v2

## Setup & Running

### Prerequisites
- Python 3.11+
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- A local postgres database

### 1. Clone and Install
```bash
git clone https://github.com/ymahrous/flyrank-capstone-image-relevance.git
cd flyrank-capstone-image-relevance
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and DATABASE_URL
```

### 3. Initialize Database & Seed
```bash
python -m scripts.init_db
python -m scripts.migrate_add_vectors
python -m scripts.download_corpus
python -m scripts.seed_db
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload
```

### 5. Execute the Pipeline
1. **Process Images:** `curl -X POST http://localhost:8000/jobs/vision`
2. **Embed Images:** `curl -X POST http://localhost:8000/jobs/embed-images`
3. **Create a Post:** 
   ```bash
   curl -X POST http://localhost:8000/posts/ -H "Content-Type: application/json" -d '{"title": "Red Fox Behavior", "content": "Red foxes are cunning solitary hunters."}'
   ```
4. **Get Suggestions:** `curl http://localhost:8000/matching/posts/1/images`

### 6. Automated Demo & Eval
To reset the database and run the full pipeline automatically:
```bash
python -m scripts.run_demo
```

To calculate the Top-1 Precision metric:
```bash
python -m app.eval.run_eval
```

## Running Tests
```bash
# Run deterministic unit tests (Guard & API validation)
pytest -v
```

## Limitations & Honest Assumptions
- **Scale:** Brute-force cosine similarity is used instead of `pgvector` indexes. This is perfectly fine for the bounded 50-image scope, but would need vector indexing (e.g., HNSW) for 10,000+ images.
- **Subject Extraction:** Post subjects are extracted via LLM. If the LLM hallucinates a highly obscure synonym not in our `SYNONYM_MAP`, the hard subject veto might falsely reject a good image.
- **Throttling:** Vision jobs sleep for 2 seconds between calls to respect the free-tier RPM limit. This makes the batch job take ~2 minutes for 50 images.
- **Embeddings:** Image embeddings are generated from the *text caption*, not the raw image pixels. This saves costs and complexity, but relies on the vision model's caption being highly accurate.

## Project Structure
```
.
├── app/
│   ├── api/          # HTTP boundary (FastAPI routers)
│   ├── services/     # Business logic (Vision, Embeddings, Guard)
│   ├── repositories/ # Database access layer
│   ├── jobs/         # Background batch workers
│   ├── schemas/      # Pydantic models (Strict validation)
│   ├── models/       # SQLAlchemy ORM models
│   ├── eval/         # Evaluation dataset & runner
│   └── db.py         # Async engine & session
├── scripts/          # DB init, corpus download, demo runner
├── tests/            # Pytest unit tests
├── data/             # Image corpus & manifest
├── capstone.yaml     # Automated evaluator config
└── requirements.txt
```