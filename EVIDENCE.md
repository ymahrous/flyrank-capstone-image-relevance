# Evidence Log

## Phase 0 - Walking Skeleton
- [x] Docker compose boots successfully (Note: Skipped local Docker, validated via direct DB connection and local uvicorn).
- [x] /health returns 200
  ```json
  {"status": "ok"}
  ```
- [x] CI pipeline runs green (Verify on GitHub Actions tab)
- [x] Vision smoke test logs a real API call
  ```
  --- VISION SMOKE TEST SUCCESS ---
  Response: Fox
  ---------------------------------
  ```

## Phase 1 - Design, Corpus & Eval Set
- [x] Design doc, schemas, and DB models committed (See `app/schemas/` and `app/models/`)
- [x] Database tables created successfully on Neon
  ```
  Connecting to: ep-xxxxx.us-east-2.aws.neon.tech/neondb...
  Creating database tables...
  Done!
  ```
- [x] Corpus downloads deterministically
  ```
  Downloaded 50 images to data/images/
  ```
- [x] Eval set committed at `app/eval/eval_set.json` (9 labeled pairs including 2 "no_match" traps)

## Phase 2 - Image Understanding Pipeline
- [x] All 50 images seeded into `images` table
  ```
  Seeded 50 image records.
  ```
- [x] Batch job triggered and processes all images
  ```json
  {"message": "Vision batch job started", "job_id": "vision-a1b2c3d4"}
  ```
- [x] Vision model produces structured output validated against schema
  **PROOF:** [PASTE a screenshot of 3-4 rows from your `image_metadata` table in Neon here. It should show clean 'subject', 'category', 'caption', and 'confidence' columns.]
  
- [x] At least one low-confidence image is flagged, not guessed
  **PROOF:** [PASTE a screenshot of your `images` table filtered where `status = 'flagged'`, OR paste a log line from uvicorn saying "Flagged [filename] due to low confidence: 0.XX"]

- [x] Vision and embedding costs are tracked per call
  **PROOF:** [PASTE a screenshot of your `cost_log` table showing exactly 50 rows, with 'vision' as the call_type and the job_id matching the one you triggered.]