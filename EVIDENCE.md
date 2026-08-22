# Evidence Log

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
- [x] Database tables created successfully on Neon
  ```
  Connecting to: ep-xxxxx.aws.neon.tech/neondb...
  Creating database tables...
  Done!
  ```
- [x] Corpus downloads deterministically (50 images in data/images/)
- [x] Eval set committed at `app/eval/eval_set.json`

## Phase 2 - Image Understanding Pipeline
- [x] All 50 images seeded into `images` table
- [x] Vision model produces structured output validated against schema
  **PROOF:** [PASTE a screenshot of 3-4 rows from your `image_metadata` table in Neon here]
- [x] At least one low-confidence image is flagged, not guessed
  **PROOF:** [PASTE a screenshot of your `images` table where status = 'flagged']
- [x] Vision and embedding costs are tracked per call
  **PROOF:** [PASTE a screenshot of your `cost_log` table showing 50+ vision rows and 50+ embedding rows]

## Phase 3 - Matching Engine & Mismatch Guard
- [x] Image and post embeddings are stored
- [x] Fox post ranks fox first; guard refuses the wolf
  **PROOF:** [PASTE the JSON output from GET /matching/posts/{fox_id}/images showing the wolf being rejected here]
- [x] No-match post returns "no confident match" with reasons
  **PROOF:** [PASTE the JSON output from GET /matching/posts/{quantum_id}/images here]