# Demo: api-migration-notes

Animated replay of real captured command output from `commands.log`. Every on-screen line is an exact excerpt of that log. Key beats are held large; the film ends on the checker pass.

## Spec pair

The demo uses the in-repo Orders pair (Apache-2.0, same license as this repository):

- `agent_skills/evals/api-migration-notes/fixtures/orders-v1.json` (OpenAPI 3.0.3, version 1.0.0)
- `agent_skills/evals/api-migration-notes/fixtures/orders-v2.json` (OpenAPI 3.0.3, version 2.0.0)

## Frames (24 s, 1920×1080, 30 fps)

| Time | What is on screen |
|---|---|
| 0.0–3.5 s | `oas_diff.py` on the Orders pair, then the differ `"summary"`: breaking 16, additive 3, deprecation 1, `exit 0` |
| 3.5–6.5 s | Classified records `BRK-001` (`removed_path` `/health`) and `BRK-016` (`status_code_removed` GET `/orders` 400) |
| 6.5–12.5 s | `check_notes.py` on the incomplete draft. `FAIL: … uncovered: BRK-016`, `covered 15/16`, `exit 1`. Held large (~6 s) |
| 12.5–18.0 s | Completed notes section `## [BRK-016] Removed status 400 from GET /orders` with Before/After examples |
| 18.0–24.0 s | `check_notes.py` on the completed notes. `PASS: 16/16 breaking changes covered, 0 unknown ids, 0 missing examples`, `exit 0`. Held large (~6 s) as the **final frame** |

Label on every frame: `Animated replay of real captured command output`.

## Commands

Working directory: repository root. Full stdout and exit codes are in `commands.log`.

```bash
python3 agent_skills/api-migration-notes/scripts/oas_diff.py \
  agent_skills/evals/api-migration-notes/fixtures/orders-v1.json \
  agent_skills/evals/api-migration-notes/fixtures/orders-v2.json
# exit 0 — 16 breaking, 3 additive, 1 deprecation

python3 agent_skills/api-migration-notes/scripts/check_notes.py \
  /tmp/api-mig-demo/draft.md /tmp/api-mig-demo/changes.json
# exit 1 — FAIL uncovered: BRK-016

python3 agent_skills/api-migration-notes/scripts/check_notes.py \
  /tmp/api-mig-demo/notes.md /tmp/api-mig-demo/changes.json
# exit 0 — PASS: 16/16 breaking changes covered, 0 unknown ids, 0 missing examples
```

YAML specs are not accepted (exit 2). Convert with `yq -o=json spec.yaml > spec.json` first.

## Media

- `out.mp4`: 1920×1080, 30 fps, 720 frames, 24.00 s, H.264 yuv420p
- `preview.gif`: 1280×720, 12 fps, 288 frames, 24.00 s, 259 496 bytes (≤5 MB; last ~6 s is the PASS hold)
