# Build Log

## Phase 0 - Walking Skeleton
- No AI tools used for skeleton setup.
- Handled `PIL` (Pillow) import conflicts by dropping the library entirely and relying on Gemini's native `Image.from_bytes()` for vision tasks. This keeps the container lighter and avoids local dependency hell.
- Chose Neon DB as the $0 Postgres provider. Required custom SSL context handling in SQLAlchemy because `asyncpg` does not natively parse `?sslmode=require` from URL strings.

## Phase 1 - Design & Corpus
- No AI tools used for schema design.
- **Key decision:** Enforced a `Literal["animal", "landscape", "food", "object", "building"]` category enum in Pydantic. This controlled vocabulary is what allows the Phase 3 mismatch guard to do hard subject vetoes (e.g., fox vs wolf) without fuzzy string matching.
- Curated a 50-image Unsplash manifest. Deliberately included 2-3 visually ambiguous images to guarantee the low-confidence flagging requirement (Probe 1) triggers during Phase 2.
- Built the `eval_set.json` *before* building the AI pipeline so threshold tuning in Phase 3 has ground truth data immediately.

## Phase 2 - Vision Pipeline
- AI used: Gemini 1.5 Flash (via `gemini-pro-vision` model name for free tier compatibility) to write the initial JSON-stripping regex.
- **Where AI was wrong:** The AI suggested using `response.candidates[0].content.parts[0].text`, which threw `AttributeError`s on malformed responses. I changed it to use the safer `response.text` accessor and wrapped the whole thing in a generic `try/except` that logs the raw string on failure.
- Implemented a 2-second sleep between vision calls. The Gemini free tier has an aggressive Requests-Per-Minute (RPM) limit. Without this throttle, the batch job would hit 429 rate limits and trigger unnecessary retry backoffs.
- Schema validation catches Gemini's habit of wrapping JSON responses in ```json ... ``` markdown blocks.