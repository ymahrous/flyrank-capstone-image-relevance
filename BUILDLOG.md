## Phase 0 - Walking Skeleton
- No AI tools used for skeleton setup.
- **Pillow Nightmare:** Encountered persistent `AttributeError: module 'PIL' has no attribute 'PngImagePlugin'`. Tried multiple reinstalls. Root cause: dropping PIL entirely and using `genai.Image.from_bytes()` is much cleaner for backend APIs anyway.
- **Neon DB SSL:** Chose Neon as the $0 Postgres provider. `asyncpg` crashes if `?sslmode=require` is left in the URL string. Fixed by parsing the URL in `app/db.py` and passing a native Python `ssl.create_default_context()` to `connect_args`.

## Phase 1 - Design & Corpus
- No AI tools used for schema design.
- **Key Decision:** Enforced a `Literal["animal", "landscape", "food", "object", "building"]` category enum in Pydantic. This controlled vocabulary is what allows the Phase 3 mismatch guard to do hard subject vetoes without fuzzy string matching.
- Curated a 50-image Unsplash manifest. Deliberately included ambiguous images to guarantee low-confidence flagging triggers.
- Built the `eval_set.json` *before* the AI pipeline so threshold tuning has ground truth immediately.

## Phase 2 - Vision Pipeline
- AI used: ChatGPT to help draft the initial regex for stripping ```json markdown blocks from Gemini responses.
- **Where AI was wrong:** The AI suggested deep dictionary diving into `response.candidates[0].content.parts[0].text`, which threw `AttributeError`s on malformed responses. Changed to the safer `response.text` accessor wrapped in a generic `try/except`.
- **Gemini Model Hell:** Free tier models are highly region/account dependent. Started with `gemini-pro-vision` (404), tried `gemini-1.5-flash` (PIL issues), finally landed on `gemini-2.5-flash-image` for vision and `gemini-3.6-flash` for text after Google repeatedly returned 404s and forced upgrade errors.
- Implemented a 2-second sleep between vision calls to respect free-tier RPM limits.

## Phase 3 - Matching Engine & Guard
- No AI tools used for the guard logic; deliberately built the 3-signal system (Subject Veto -> Similarity Threshold -> Confidence Floor) based on the capstone rubric requirements.
- Used a simple `SYNONYM_MAP` dictionary to handle scientific names (e.g., "Vulpes vulpes" -> "red fox") instead of wasting API calls on LLM-based normalization.