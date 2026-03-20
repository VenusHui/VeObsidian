#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def safe(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s)
    return s.strip("_")[:80] or "msg"


def parse_ts(ts: str) -> dt.datetime:
    # support ISO8601; fallback to now
    try:
        return dt.datetime.fromisoformat(ts)
    except Exception:
        return dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="Obsidian repo path")
    p.add_argument("--mapping", required=True, help="chat_id to board JSON mapping")
    p.add_argument("--input", required=True, help="message JSON file")
    p.add_argument("--push", action="store_true", help="git push after commit")
    args = p.parse_args()

    repo = Path(args.repo)
    mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    msg = json.loads(Path(args.input).read_text(encoding="utf-8"))

    chat_id = msg.get("chat_id", "unknown_chat")
    board = mapping.get(chat_id, "shared")
    sender = msg.get("sender", "unknown")
    text = msg.get("text", "")
    ts_raw = msg.get("ts", dt.datetime.now().isoformat())
    message_id = msg.get("message_id", "no_message_id")

    ts = parse_ts(ts_raw)
    day = ts.strftime("%Y-%m-%d")
    t = ts.strftime("%H%M%S")

    out_dir = repo / board / "inbox" / day
    out_dir.mkdir(parents=True, exist_ok=True)

    fname = f"{t}_{safe(message_id)}.md"
    out = out_dir / fname

    frontmatter = (
        "---\n"
        "source: feishu\n"
        f"chat_id: {chat_id}\n"
        f"channel: {board}\n"
        f"sender: {sender}\n"
        f"ts: {ts.isoformat()}\n"
        f"message_id: {message_id}\n"
        f"tags: [feishu, {board}]\n"
        "---\n\n"
    )

    out.write_text(frontmatter + text + "\n", encoding="utf-8")

    run(["git", "add", str(out.relative_to(repo))], cwd=repo)
    run(["git", "commit", "-m", f"ingest({board}): {message_id}"] , cwd=repo)

    if args.push:
        run(["git", "push"], cwd=repo)

    print(str(out))


if __name__ == "__main__":
    main()
