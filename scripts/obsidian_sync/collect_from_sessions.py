#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

TZ_CN = timezone(timedelta(hours=8))


def safe(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]+", "_", s).strip("_")[:80] or "msg"


def parse_ts_from_text(text: str):
    m = re.search(r'"timestamp"\s*:\s*"([^"]+)"', text)
    if not m:
        return datetime.now(TZ_CN)
    raw = m.group(1)
    # Example: Wed 2026-03-11 09:01 GMT+8
    try:
        return datetime.strptime(raw, "%a %Y-%m-%d %H:%M GMT+8").replace(tzinfo=TZ_CN)
    except Exception:
        return datetime.now(TZ_CN)


def parse_message_id(text: str):
    m = re.search(r"\[message_id:\s*([^\]]+)\]", text)
    if m:
        return m.group(1).strip()
    return None


def extract_sender(text: str):
    m = re.search(r"\n([^\n:]{1,50}):\s", text)
    return m.group(1).strip() if m else "unknown"


def extract_payload_text(text: str):
    # keep only the useful conversation tail when available
    marker = re.search(r"\[message_id:[^\]]+\]\n", text)
    if marker:
        tail = text[marker.end():].strip()
        return tail
    return text.strip()


def ingest_one(repo: Path, board: str, chat_id: str, sender: str, text: str, ts: datetime, message_id: str):
    day = ts.strftime("%Y-%m-%d")
    hhmmss = ts.strftime("%H%M%S")
    out_dir = repo / board / "inbox" / day
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{hhmmss}_{safe(message_id)}.md"
    if out.exists():
        return None

    frontmatter = (
        "---\n"
        "source: feishu-session-log\n"
        f"chat_id: {chat_id}\n"
        f"channel: {board}\n"
        f"sender: {sender}\n"
        f"ts: {ts.isoformat()}\n"
        f"message_id: {message_id}\n"
        f"tags: [feishu, {board}, raw]\n"
        "---\n\n"
    )
    out.write_text(frontmatter + text + "\n", encoding="utf-8")
    return out


def main():
    script_dir = Path(__file__).resolve().parent

    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--mapping", required=True)
    p.add_argument("--sessions-index", default="/home/ubuntu/.openclaw/agents/main/sessions/sessions.json")
    p.add_argument("--state", default=str(script_dir / ".collect_state.json"))
    args = p.parse_args()

    repo = Path(args.repo)
    mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    sessions_index = json.loads(Path(args.sessions_index).read_text(encoding="utf-8"))

    state_path = Path(args.state)
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    created = []

    for chat_id, board in mapping.items():
        session_key = f"agent:main:feishu:group:{chat_id}"
        entry = sessions_index.get(session_key)
        if not entry:
            continue
        session_file = entry.get("sessionFile")
        if not session_file:
            continue

        fpath = Path(session_file)
        if not fpath.exists():
            continue

        offset = int(state.get(session_file, 0))
        with fpath.open("r", encoding="utf-8") as f:
            f.seek(offset)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message") or {}
                if msg.get("role") != "user":
                    continue
                content = msg.get("content") or []
                text = "\n".join([c.get("text", "") for c in content if c.get("type") == "text"]).strip()
                if not text:
                    continue
                message_id = parse_message_id(text) or obj.get("id")
                sender = extract_sender(text)
                ts = parse_ts_from_text(text)
                payload = extract_payload_text(text)
                out = ingest_one(repo, board, chat_id, sender, payload, ts, message_id)
                if out:
                    created.append(str(out))
            state[session_file] = f.tell()

    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"created": len(created), "files": created}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
