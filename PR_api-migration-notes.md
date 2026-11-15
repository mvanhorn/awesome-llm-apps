Title: Add api-migration-notes skill: migration notes that cover every breaking API change

## Summary

Adds `agent_skills/api-migration-notes/`: given two OpenAPI 3.x JSON documents, produce consumer migration notes that name every breaking change. A stdlib differ classifies the spec. Notes then say who is affected, what breaks, what to change, and show before/after request or response examples. A checker fails until every breaking id is covered.

Listings: root README skills list, `agent_skills/README.md` table, and `agent_skills/registry.json`.

## What the scripts do vs what the agent writes

Scripts (Python 3.11 standard library only; no network):

- `scripts/oas_diff.py` loads two OpenAPI 3.x JSON documents, resolves local `$ref`s with cycle protection and size caps (`max_ref_depth` 32, `max_nodes` 50000, `max_refs` 2000, `max_file_bytes` 2e6), and emits stable change records with ids and JSON pointers. Breaking: removed path/operation, removed or renamed response field, request field newly required, type/format/enum narrowing, parameter location change, auth scheme change, status code removal. Additive: new optional field, new endpoint, enum widening. Deprecations are recorded separately.
- `scripts/check_notes.py` parses notes Markdown. Each change section is a `##` heading that names the id as `[BRK-003]` or `<!-- change: BRK-003 -->`. Breaking sections must include Before and After labels plus at least two fenced examples. Exit 0 = covered; 1 = uncovered/unknown/missing examples; 2 = usage or input error.

The agent reads the differ JSON, writes the consumer-facing notes (who is affected, what to change, before/after examples), runs the checker, and fills gaps until exit 0.

## Coverage guarantee (checker)

The checker is the coverage gate. A first draft that omitted `BRK-016` (removed status 400 from `GET /orders`) failed with `uncovered: BRK-016` and exit 1. The completed notes passed `16/16 breaking changes covered, 0 unknown ids, 0 missing examples` (exit 0). Unknown ids and sections without before/after examples also fail.

JSON Pointers encode path keys (`/health` → `/paths/~1health`).

## Evals

Commands from `.github/workflows/skill-evals.yml`, recorded in `logs/` on the demo branch:

- [x] `for t in agent_skills/evals/*/test_*.py; do python3 "$t"; done`
  - `api-migration-notes/test_api_migration_notes.py`: 44/44 (classifications, `$ref` / allOf, cycles, caps, enum narrowing vs widening, required-ness, checker pass/missing/unknown/missing-examples, YAML rejection)
  - `commit-archaeologist/test_archaeologist.py`: 28/28
  - `dependency-doctor/test_dep_doctor.py`: 69/69
  - `first-reader/test_first_reader.py`: all script tests passed (47 assertions)
  - `project-graveyard/test_graveyard.py`: 16/16
  - `scope-creep-detector/test_scope_creep.py`: 15/15
  - `tools/test_registry_lint.py`: 7/7
- [x] `python3 agent_skills/evals/tools/skill_lint.py agent_skills/api-migration-notes --strict` — 0 error(s), 0 warning(s). Same `--strict` loop over all 8 skill directories: each PASS.
- [x] `python3 agent_skills/evals/tools/skill_scanner.py agent_skills` — 0 CRITICAL, 0 WARN, 8 INFO (none on this skill)
- [x] `python3 agent_skills/evals/tools/run_trigger_evals.py` — 8 skills all clear; `api-migration-notes` 4 positives clear 5 near-misses (weakest 1.79 vs strongest 0.71)
- [x] `python3 agent_skills/evals/tools/registry_lint.py --check` — PASS — 0 error(s), 0 warning(s)

## Not covered

- YAML input is not parsed. The differ exits 2 and tells the caller to convert with `yq -o=json spec.yaml > spec.json`.
- Remote `$ref`s (http/https) are not fetched.
- Tier-3 behavioral evals (`evals.json`) are on-demand and were not run.

## Demo

![demo](https://raw.githubusercontent.com/mvanhorn/pr-demo-assets/main/osc-bulk-1115b/api-migration-notes/preview.gif)

Full recording (MP4): https://raw.githubusercontent.com/mvanhorn/pr-demo-assets/main/osc-bulk-1115b/api-migration-notes/out.mp4
