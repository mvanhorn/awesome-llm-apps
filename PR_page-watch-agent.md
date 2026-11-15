Title: Add Page Watch always-on agent: brief me when the pages I depend on change in ways that matter

## Summary

Page Watch is an always-on briefing agent for a short list of pages you depend on: vendor pricing, API rate-limit docs, terms of service, status and changelog pages. It fetches those pages on a schedule, compares them to the last snapshot, and reports only material changes — with the exact old vs new text, an impact tag, and the deterministic pre-filter verdict next to the model classification. Cosmetic chrome (timestamps, cache-busters, CSRF tokens, promo banners, nav) is stripped or classified as not material.

It belongs with the other always-on agents: a job that should run in the background and only interrupt you when something you rely on actually changed.

## How it works

- `watch.py` loads a YAML or JSON watch list (url, name, optional CSS selector or text anchors, optional keywords). It fetches with a timeout, size cap, and polite User-Agent, normalizes readable text, stores snapshots under a directory keyed by URL hash, and diffs at paragraph level with hunk ids that stay stable when unchanged paragraphs are reordered.
- A deterministic pre-filter always runs first (keyword hits such as price / limit / deprecat, and numeric changes such as prices or quotas). Its verdict is shown next to the model verdict so the brief is checkable.
- `judge.py` classifies each hunk as `material` or `cosmetic`, writes a one-sentence summary, quotes before/after exactly, and tags impact (pricing, limits, legal, deprecation, availability, other). Fetching a watch list uses Gemini as the default judge whenever `GOOGLE_API_KEY` or `GEMINI_API_KEY` is set. `--sample` is the offline path: recorded fixture judgments, no network, no model. If Gemini cannot judge a hunk, the brief still renders and marks it `source=prefilter_fallback`.
- `delivery.py` renders a text + HTML brief grouped by page. Nothing is sent unless `dry_run=false` and Gmail or a webhook is configured.
- `agent.py` exposes `root_agent` for questions such as "what changed on the pricing page this week?". `scheduler_api.py` exposes `/page-watch/dry-run`, `/page-watch/trigger`, and `/page-watch/pubsub`.

## Safety defaults

- Scheduler `dry_run` defaults to true. Delivery is not attempted until the request sets `"dry_run": false`.
- Even then, Gmail or webhook configuration must be present; otherwise the API returns `skipped_no_delivery` and sends nothing.
- Watch list and snapshot paths come from server environment (`PAGE_WATCH_WATCHLIST`, `PAGE_WATCH_SNAPSHOT_DIR`), not from request payloads.
- Fetches use a dedicated User-Agent, a 15s timeout, and a 1.5 MB size cap.
- `--sample` never calls the model. `PAGE_WATCH_LIVE_MODEL=false` keeps recorded judgments while fetching.

## Testing

Commands run from the repository root, Python 3.12.3:

- `python3 -m pytest always_on_agents/page_watch_agent/tests/unit -q` — 25 passed, 1 warning
- `python3 -m pytest always_on_agents/release_radar_agent/tests/unit -q` — 16 passed, 1 warning
- `(cd always_on_agents && python3 -m pytest always_on_hn_briefing_agent/tests/unit -q)` — 9 passed
- `python3 -m compileall always_on_agents/page_watch_agent` — exit 0
- `python3 watch.py --sample` — pricing and terms material with before/after quotes; docs no material change; `Judge mode: sample`; `Source: sample`
- two `--fetch` runs against local fixture pages with `PAGE_WATCH_LIVE_MODEL=false` (baseline, then v2) — same brief shape; `judge_mode=sample`
- a no-key `judge_hunks(..., sample=False)` call printed `Source: prefilter_fallback (Gemini did not judge this hunk)`
- `GET /page-watch/dry-run` — `dry_run = True`, `delivery.sent = False`, `delivery.status = dry_run`, `judge_mode = sample`
- `POST /page-watch/trigger` with `{"dry_run": true, "live": false}` — `nothing sent: True`

There is no repository Python lint/format config for apps, so no extra linter was run on these files.

## Remaining proof gaps

- Live Gemini judgments were not exercised in the demo. `GOOGLE_API_KEY` / `GEMINI_API_KEY` were unset, so this capture used recorded sample judgments (`source=sample`) plus a no-key fallback label (`source=prefilter_fallback`). A `--fetch` with a key and `source=gemini` in the brief was not recorded.
- Gmail and webhook sending were not exercised beyond the skip/dry-run guards (network was patched in tests; the scheduler demo kept `dry_run` true).

## Demo

![demo](https://raw.githubusercontent.com/mvanhorn/awesome-llm-apps/demo/page-watch-agent/preview.gif)

Full recording (MP4): https://raw.githubusercontent.com/mvanhorn/awesome-llm-apps/demo/page-watch-agent/out.mp4
