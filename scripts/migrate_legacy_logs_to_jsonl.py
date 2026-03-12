#!/usr/bin/env python3
"""Aggregate legacy markdown message logs into monthly JSONL files.

Input (legacy, local-only):
  <scope>/inbox/YYYY-MM-DD/*.md
  <scope>/daily/YYYY-MM-DD.md

Output:
  local_logs/<scope>/messages-YYYY-MM.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

SCOPES = ("ai", "finance", "shared")
DATE_DIR_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
INBOX_FILE_RE = re.compile(r"^(\d{6})_(.+)\.md$")


@dataclass
class Record:
    scope: str
    yyyy_mm: str
    payload: dict
    source: Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def build_record_for_inbox(scope: str, day_dir: str, file: Path) -> Record | None:
    if not DATE_DIR_RE.match(day_dir):
        return None

    m = INBOX_FILE_RE.match(file.name)
    if not m:
        return None

    hhmmss, msg_id = m.group(1), m.group(2)
    yyyy, mm, dd = day_dir.split("-")
    ts = f"{yyyy}-{mm}-{dd}T{hhmmss[0:2]}:{hhmmss[2:4]}:{hhmmss[4:6]}"

    payload = {
        "ts": ts,
        "scope": scope,
        "source_type": "legacy_inbox_md",
        "message_id": msg_id,
        "text": read_text(file),
        "source_path": str(file),
    }

    return Record(scope=scope, yyyy_mm=f"{yyyy}-{mm}", payload=payload, source=file)


def build_record_for_daily(scope: str, file: Path) -> Record | None:
    # file: <scope>/daily/YYYY-MM-DD.md
    day = file.stem
    if not DATE_DIR_RE.match(day):
        return None
    yyyy, mm, dd = day.split("-")

    payload = {
        "ts": f"{yyyy}-{mm}-{dd}",
        "scope": scope,
        "source_type": "legacy_daily_md",
        "message_id": None,
        "text": read_text(file),
        "source_path": str(file),
    }

    return Record(scope=scope, yyyy_mm=f"{yyyy}-{mm}", payload=payload, source=file)


def collect_records(root: Path) -> list[Record]:
    records: list[Record] = []

    for scope in SCOPES:
        scope_dir = root / scope
        if not scope_dir.exists():
            continue

        inbox_dir = scope_dir / "inbox"
        if inbox_dir.exists():
            for day_dir in sorted(p for p in inbox_dir.iterdir() if p.is_dir()):
                for f in sorted(day_dir.glob("*.md")):
                    rec = build_record_for_inbox(scope, day_dir.name, f)
                    if rec:
                        records.append(rec)

        daily_dir = scope_dir / "daily"
        if daily_dir.exists():
            for f in sorted(daily_dir.glob("*.md")):
                rec = build_record_for_daily(scope, f)
                if rec:
                    records.append(rec)

    return records


def append_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fw:
        for row in rows:
            fw.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy md logs to local monthly JSONL")
    parser.add_argument("--root", default=".", help="repo root")
    parser.add_argument("--out-root", default="local_logs", help="output logs root")
    parser.add_argument("--apply", action="store_true", help="write output files")
    parser.add_argument("--delete-source", action="store_true", help="delete source md after successful write (requires --apply)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_root = (root / args.out_root).resolve()

    records = collect_records(root)
    if not records:
        print("No legacy markdown logs found.")
        return 0

    buckets: dict[tuple[str, str], list[Record]] = {}
    for r in records:
        buckets.setdefault((r.scope, r.yyyy_mm), []).append(r)

    print(f"Found records: {len(records)}")
    for (scope, yyyy_mm), rows in sorted(buckets.items()):
        out_file = out_root / scope / f"messages-{yyyy_mm}.jsonl"
        print(f"  - {scope} {yyyy_mm}: {len(rows)} -> {out_file}")

    if not args.apply:
        print("\nDry run. Add --apply to write JSONL.")
        return 0

    for (scope, yyyy_mm), rows in sorted(buckets.items()):
        out_file = out_root / scope / f"messages-{yyyy_mm}.jsonl"
        append_jsonl(out_file, [r.payload for r in rows])

    if args.delete_source:
        if not args.apply:
            raise SystemExit("--delete-source requires --apply")
        for r in records:
            r.source.unlink(missing_ok=True)
        print("Deleted legacy source markdown files.")

    print("Migration complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
