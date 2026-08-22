# Build Log

## Phase 0 - Walking Skeleton
- No AI tools used for skeleton setup.
- **Pillow Nightmare:** Encountered persistent `AttributeError: module 'PIL' has no attribute 'PngImagePlugin'`. Tried multiple reinstalls, assumed it was a pathing issue. Eventually realized dropping PIL entirely and using `genai.Image.from_bytes()` is much cleaner for backend APIs anyway. Removed Pillow from requirements.
- **Neon DB SSL:** Chose Neon as the $0 Postgres provider. `asyncpg` crashes if `?sslmode=require` is left in the URL string. Fixed by parsing the URL in `app/db.py` and passing a native Python `ssl.create_default_context()` to `connect_args`.

## Phase 1 - Design & Corpus
- No AI tools used for schema design.
- **Key Decision:** Enforced a `Literal["animal", "landscape", "food", "object", "building"]` category enum in Pydantic. This controlled vocabulary is what allows the Phase 3 mismatch guard to do hard subject vetoes (e.g., fox vs wolf) without fuzzy string matching.
- Curated a 50-image Unsplash manifest. Deliberately included 2-3 visually ambiguous images to guarantee the low-confidence flagging requirement (Probe 1) triggers during Phase 2.
- Built the `eval_set.json` *before* building the AI pipeline so threshold tuning in Phase 3 has ground truth data immediately.

## Phase 2 - Vision Pipeline
- AI used: ChatGPT to help draft the initial regex for stripping ```json markdown blocks from Gemini responses.
- **Where AI was wrong:** The AI suggested deep dictionary diving into `response.candidates[0].content.parts[0].text`, which threw `AttributeError`s on malformed responses. Changed to the safer `response.text` accessor wrapped in a generic `try/except` that logs the raw string on failure.
- **Gemini Model Hell:** Free tier models are highly region/account dependent. Started with `gemini-pro-vision` (404), tried `gemini-1.5-flash`, finally landed on `gemini-2.5-flash-image` for vision and `gemini-3.6-flash` for text after Google repeatedly returned 404s and forced upgrade 403 errors. Lesson: Always use `genai.list_models()` first.
- Implemented a 2-second sleep between vision calls to respect free-tier RPM limits.

## Phase 3 - Matching Engine & Guard
- No AI tools used for the guard logic; deliberately built the 3-signal system (Subject Veto -> Similarity Threshold -> Confidence Floor) based on the capstone rubric requirements.
- Used a simple `SYNONYM_MAP` dictionary to handle scientific names (e.g., "Vulpes vulpes" -> "red fox") instead of wasting API calls on LLM-based normalization.
- Handled the "No Confident Match" edge case by checking if *any* candidate passes the guard, returning a global rejection with aggregated reasons if none do.

## Phase 4 - Tests & Eval
- AI used: Claude to scaffold the boilerplate for `pytest` async fixtures, but manually wrote all test logic.
- **Where AI was wrong:** AI suggested mocking `AsyncSession` which required complex `unittest.mock.AsyncMock` patches. I simplified the tests by testing the `guard_service` logic as pure functions (no DB needed) and using FastAPI's `TestClient` for API tests.
- Built the eval runner to calculate Top-1 Precision. Had to handle the mapping between eval set slugs and actual DB Post IDs via title fuzzy matching.