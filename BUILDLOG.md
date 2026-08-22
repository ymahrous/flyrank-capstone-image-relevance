# Build Log

## Phase 0 - Walking Skeleton
- No AI tools used for skeleton setup.
- **Pillow Nightmare:** Encountered a persistent `AttributeError: module 'PIL' has no attribute 'PngImagePlugin'`. Attempted multiple reinstalls and cache purges, assuming it was a virtual environment corruption. Root cause was actually an unnecessary dependency. Solution: Dropped PIL entirely and used `genai.Image.from_bytes()`. This is cleaner for backend APIs anyway as it avoids managing heavy image file processing in memory.
- **Neon DB SSL:** Chose Neon as the $0 Postgres provider. `asyncpg` crashes if `?sslmode=require` is left in the URL string. Fixed by parsing the URL in `app/db.py` to strip the query parameters, and passing a native Python `ssl.create_default_context()` to `connect_args`.

## Phase 1 - Design & Corpus
- No AI tools used for schema design.
- **Key Decision:** Enforced a `Literal["animal", "landscape", "food", "object", "building"]` category enum in Pydantic. This controlled vocabulary is what allows the Phase 3 mismatch guard to execute hard subject vetoes (e.g., fox vs. wolf) without relying on fragile fuzzy string matching.
- Curated a 50-image Unsplash manifest. Deliberately included 2-3 visually ambiguous/low-quality images to guarantee the low-confidence flagging requirement (Probe 1) triggers during Phase 2, rather than hoping the AI naturally outputs a low score.
- Built the `eval_set.json` *before* building the AI pipeline. This de-risks Phase 3 because threshold tuning has ground-truth data immediately available.

## Phase 2 - Vision Pipeline
- AI used: ChatGPT to help draft the initial regex for stripping ```json markdown blocks from Gemini responses.
- **Where AI was wrong:** The AI suggested deep dictionary diving into `response.candidates[0].content.parts[0].text`, which threw `AttributeError`s on malformed responses. I changed it to the safer `response.text` accessor wrapped in a generic `try/except` that logs the raw string on failure.
- **Gemini Model Hell:** Free tier models are highly region/account dependent. Started with `gemini-pro-vision` (404), and after several forced upgrade errors, landed on `gemini-2.5-flash-image` for vision and `gemini-2.5-flash` for text extraction to remain within the free tier constraints. Lesson learned: Always query `genai.list_models()` first instead of trusting documentation for free-tier availability. 
- Implemented a 2-second sleep between vision calls to respect free-tier RPM limits, preventing 429 rate-limit errors from killing the batch job.

## Phase 3 - Matching Engine & Guard
- No AI tools used for the guard logic; deliberately built the 3-signal system (Subject Veto -> Similarity Threshold -> Confidence Floor) based on the capstone rubric requirements.
- Used a simple `SYNONYM_MAP` dictionary to handle scientific names (e.g., "Vulpes vulpes" -> "red fox") instead of wasting API calls on LLM-based normalization.
- Handled the "No Confident Match" edge case by checking if *any* candidate passes the guard, returning a global rejection with aggregated reasons if none do.
- Used `gemini-embedding-001` for vector generation to align with account permissions.

## Phase 4 - Tests & Eval
- AI used: Claude to scaffold the boilerplate for `pytest` async fixtures.
- **Where AI was wrong:** AI suggested mocking `AsyncSession` which required complex `unittest.mock.AsyncMock` patches. I simplified the tests by testing the `guard_service` logic as pure functions (no DB needed) and using FastAPI's `TestClient` for API boundary tests. Much more deterministic.
- Built the eval runner to calculate Top-1 Precision. Had to handle the mapping between eval set slugs and actual DB Post IDs. Enhanced the script to auto-generate missing posts and their embeddings on the fly so the eval can be run cleanly on a fresh database without manual curl commands.

## Phase 5 - Demo Prep & Hardening
- No AI tools used for demo scripting.
- **Nuke and Seed:** Built `fresh_start.py` to truncate all tables and re-seed the 50 images. Critical for ensuring the evaluator (or a fresh clone) never sees messy, duplicated test data from development.
- **Automated Demo Runner:** Created `run_demo.py` to script the exact 6-minute demo sequence (reset -> vision -> embed -> post -> query). Proves the system is deterministic and reproducible, not just a fragile series of manual curl commands.
- **The "Wolf Moment":** Rehearsed the exact JSON payload where the guard triggers a `category_mismatch` on a semantically similar wolf image. The structured reason codes (`"expected red fox, detected gray wolf"`) make the demo land perfectly without needing to explain code.