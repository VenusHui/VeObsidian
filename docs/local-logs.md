# Local Raw Message Logs (Local-only)

## Goal

- Keep GitHub repo clean: only compact knowledge.
- Store raw messages locally for traceability and re-compaction.

## Path & Naming

Use monthly JSONL files by scope:

- `local_logs/ai/messages-YYYY-MM.jsonl`
- `local_logs/finance/messages-YYYY-MM.jsonl`
- `local_logs/shared/messages-YYYY-MM.jsonl`

One line = one JSON object.

## Suggested JSON fields

```json
{
  "ts": "2026-03-12T16:34:00+08:00",
  "scope": "ai",
  "channel": "feishu",
  "chat_id": "chat:xxx",
  "message_id": "om_xxx",
  "role": "user",
  "sender": "胡锦晖",
  "text": "...",
  "meta": {}
}
```

## One-time Migration from legacy Markdown

If old files still exist (like `<scope>/inbox/YYYY-MM-DD/*.md`), run:

```bash
python3 scripts/migrate_legacy_logs_to_jsonl.py          # dry-run
python3 scripts/migrate_legacy_logs_to_jsonl.py --apply  # write JSONL
# optional: delete old markdown after successful migration
python3 scripts/migrate_legacy_logs_to_jsonl.py --apply --delete-source
```

## Cleanup Policy

Use a one-month buffer (default):

- March run: delete January and older
- Keep February as buffer
- Keep current month always

Script:

```bash
python3 scripts/cleanup_local_logs.py --buffer-months 1 --dry-run
python3 scripts/cleanup_local_logs.py --buffer-months 1 --apply
```
