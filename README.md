# Obsidian Knowledge Base

This repo keeps **compact knowledge only** for sync and Obsidian reading.

## Tracked in Git

- `knowledge/ai/memory_compact.md`
- `knowledge/ai/manifest.json`
- `knowledge/finance/memory_compact.md`
- `knowledge/finance/manifest.json`
- `knowledge/shared/memory_compact.md`
- `knowledge/shared/manifest.json`

## Local-only (ignored)

Raw message records are kept locally and never pushed:

- `local_logs/<scope>/messages-YYYY-MM.jsonl` (recommended)
- optional local staging/output folders: `ai/`, `finance/`, `shared/`, `knowledge/*/delta/`

## Retention & Cleanup

- Default policy: keep **1-month buffer**.
  - Example: run in March → clean January and older, keep February as buffer.
- Cleanup script:
  - `python3 scripts/cleanup_local_logs.py --buffer-months 1 --dry-run`
  - `python3 scripts/cleanup_local_logs.py --buffer-months 1 --apply`

See `docs/local-logs.md` for full local log spec.
