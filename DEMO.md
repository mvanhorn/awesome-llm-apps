# Page Watch demo

Recorded from a real run of the Page Watch agent in this repository. The terminal replay uses the exact lines in `commands.log`. Judgments in this capture are recorded sample fixtures (`judge_mode=sample`, `Source: sample`). This is not a live Gemini run.

The replay label on every frame is "Animated replay of real captured command output", with a second line "Recorded sample judgments — no Gemini calls".

## What the 24 s recording shows

1. **0.0–2.2 s** — `python3 --version`, `python3 -m compileall always_on_agents/page_watch_agent`, local `python3 -m http.server 8765` serving the three fixture pages, and `curl` of `pricing.html` returning HTTP 200. No pytest output.
2. **2.2–4.4 s** — first `--fetch` against v1 pages. All three pages report `Baseline captured.` `Judge mode: sample`.
3. **4.4–5.2 s** — `cp pages_v2/*.html pages/` (price $29→$49, rate limit 100→60, docs footer/timestamp only, new arbitration clause).
4. **5.2–8.6 s** (~3.4 s hold, large type, two columns) — second `--fetch` material brief. Pricing: `$29` → `$49` and rate limit `100` → `60`, with before/after quotes, pre-filter verdicts, and `Source: sample`. Docs: `No material change.` Terms: binding arbitration clause with before/after quotes and `Pre-filter: likely_material (keyword:arbitration)`.
5. **8.6–12.0 s** (~3.4 s, full frame) — rendered HTML brief of that same second fetch at 1920×1080, with the banner `Recorded sample judgments — judge_mode=sample — no Gemini calls`.
6. **12.0–15.4 s** (~3.4 s) — fallback label example: with no API key, `judge_hunks(..., sample=False)` prints `hunk source = prefilter_fallback` and `Source: prefilter_fallback (Gemini did not judge this hunk)`.
7. **15.4–24.0 s** — scheduler on port 8766. `GET /health` returns `{"status":"ok"}`. Dry-run flags: `dry_run = True`, `delivery.sent = False`, `delivery.status = dry_run`, `judge_mode = sample`. `POST /page-watch/trigger` with `{"dry_run": true, "live": false}` ends on `nothing sent: True`.

## Media

- `out.mp4`: 1920×1080, 30 fps, 720 frames, 24.0 s, H.264 yuv420p.
- `preview.gif`: 960×540, 8 fps, 192 frames, 24.0 s, 0.35 MB.

See `logs/ffprobe.txt` for the probe output.

## Not run

No `GOOGLE_API_KEY` or `GEMINI_API_KEY` was present. Live Gemini judgments were not called. Sample-mode recorded judgments were used for `--sample`, `--fetch` (`PAGE_WATCH_LIVE_MODEL=false`), and the scheduler dry-run.
