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

## Retention suggestion

- Keep local raw logs for 30–90 days, then archive or delete.
- Repo remains clean: only compacted knowledge + scripts/docs.
