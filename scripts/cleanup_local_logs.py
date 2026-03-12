#!/usr/bin/env python3
"""Cleanup local raw message logs by month with a buffer period.

Convention:
  local_logs/<scope>/messages-YYYY-MM.jsonl

Example (buffer_months=1):
  - run in 2026-03 -> delete 2026-01 and older
  - keep 2026-02 as buffer, keep current month 2026-03
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

PATTERN = re.compile(r"^messages-(\d{4})-(\d{2})\.jsonl$")


@dataclass
class LogFile:
    path: Path
    year: int
    month: int


def month_start(d: date) -> date:
    return date(d.year, d.month, 1)


def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    return date(y, m, 1)


def discover_logs(root: Path) -> list[LogFile]:
    results: list[LogFile] = []
    if not root.exists():
        return results

    for p in root.rglob("messages-*.jsonl"):
        m = PATTERN.match(p.name)
        if not m:
            continue
        year, month = int(m.group(1)), int(m.group(2))
        if month < 1 or month > 12:
            continue
        results.append(LogFile(path=p, year=year, month=month))

    return sorted(results, key=lambda x: (x.year, x.month, str(x.path)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean local message logs with month buffer")
    parser.add_argument("--root", default="local_logs", help="local logs root (default: local_logs)")
    parser.add_argument(
        "--buffer-months",
        type=int,
        default=1,
        help="how many whole previous months to keep as buffer (default: 1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="preview deletions only (default: true)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually delete matched files",
    )

    args = parser.parse_args()

    dry_run = args.dry_run and not args.apply
    root = Path(args.root)

    if args.buffer_months < 0:
        raise SystemExit("--buffer-months must be >= 0")

    now = date.today()
    current_month = month_start(now)
    # Files older than this are removed.
    # buffer=1 in Mar => cutoff=Feb-01 => Jan and older removed.
    cutoff = add_months(current_month, -args.buffer_months)

    logs = discover_logs(root)
    if not logs:
        print(f"No matching logs found under: {root}")
        return 0

    to_delete: list[Path] = []
    for item in logs:
        file_month = date(item.year, item.month, 1)
        if file_month < cutoff:
            to_delete.append(item.path)

    print(f"Root: {root}")
    print(f"Today: {now.isoformat()}")
    print(f"Buffer months: {args.buffer_months}")
    print(f"Delete files with month < {cutoff.isoformat()}")
    print(f"Matched files: {len(logs)}")
    print(f"Delete count: {len(to_delete)}")

    for p in to_delete:
        print(f"  - {p}")

    if dry_run:
        print("\nDry run mode. No files deleted. Use --apply to execute.")
        return 0

    for p in to_delete:
        p.unlink(missing_ok=True)

    # Remove empty directories under root
    for d in sorted(root.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()

    print("\nCleanup complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
