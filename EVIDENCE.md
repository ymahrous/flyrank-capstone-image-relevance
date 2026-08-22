# Evidence Log
*One pasted proof per Definition-of-Done checkbox.*

## Phase 0 - Walking Skeleton
- [x] /health returns 200
  ```json
  {"status": "ok"}
  ```
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
  Connecting to: ep-xxxxx.aws.neon.tech/neondb...
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
- [x] Vision model produces structured output validated against schema
  **PROOF:** [PASTE a screenshot of 3-4 rows from your `image_metadata` table in Neon here. Should show clean 'subject', 'category', 'caption', and 'confidence' columns.]
  
- [x] At least one low-confidence image is flagged, not guessed
  **PROOF:** [PASTE a screenshot of your `images` table filtered where `status = 'flagged'`, OR paste a log line from uvicorn saying "Flagged [filename] due to low confidence: 0.XX"]

- [x] Vision and embedding costs are tracked per call
  **PROOF:** [PASTE a screenshot of your `cost_log` table showing 50+ rows, with 'vision' and 'embedding' as the call_types]

## Phase 3 - Matching Engine & Mismatch Guard
- [x] Image and post embeddings are stored; posts return ranked image suggestions
- [x] The mismatch guard rejects incorrect recommendations (fox post vs wolf image)
  **PROOF:** [PASTE the JSON output from GET /matching/posts/{fox_id}/images. MUST show a candidate with `"guard_decision": "reject"` and `"reason_code": "category_mismatch"`]
- [x] When no image clears the bar, the system answers "no confident match"
  **PROOF:** [PASTE the JSON output from GET /matching/posts/{quantum_id}/images. MUST show `"verdict": "no_confident_match"`]

## Phase 4 - Production Layer, Tests & Eval
- [x] Review workflow (approve / reject) exists
  **PROOF:** [PASTE a curl transcript showing POST /suggestions/1/approve returning 200]
- [x] Automated tests cover schema validation, mismatch rejection, and matching accuracy
  **PROOF:** [PASTE the terminal output of `pytest -v` showing all tests passed]
- [x] A small labeled evaluation dataset measures top-1 precision
  **PROOF:** [PASTE the terminal output of `python -m app.eval.run_eval` showing the final percentage]

## Phase 5 - Demo Prep & Hardening
- [x] Database can be wiped and re-seeded cleanly for demos
  **PROOF:** [PASTE the terminal output of `python -m scripts.fresh_start` showing "Database wiped clean." and "Re-seeded 50 image records."]
- [x] Automated demo sequence runs end-to-end without manual intervention
  **PROOF:** [PASTE the final terminal output of `python -m scripts.run_demo` showing the "STARTING FLYRANK DEMO SEQUENCE", the Wolf Rejection step, the Quantum No-Match step, and the "DEMO SEQUENCE COMPLETE" messages.]