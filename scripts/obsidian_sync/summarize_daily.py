#!/usr/bin/env python3
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

TZ_CN = timezone(timedelta(hours=8))
STOPWORDS = set("的 了 是 在 和 就 都 而 及 与 着 或 一个 我们 你们 他们 这个 那个".split())


def read_md_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            text = parts[2]
    return text.strip()


def split_lines(text: str):
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def extract_keywords(lines, topk=10):
    words = []
    for line in lines:
        for w in re.findall(r"[A-Za-z]{3,}|[\u4e00-\u9fff]{2,}", line):
            if w in STOPWORDS:
                continue
            words.append(w.lower())
    c = Counter(words)
    return [k for k, _ in c.most_common(topk)]


def extract_todos(lines):
    keys = ["TODO", "待办", "需要", "请", "明天", "跟进", "安排", "修复"]
    out = []
    for line in lines:
        if any(k.lower() in line.lower() for k in keys):
            out.append(line)
    return out[:20]


def extract_decisions(lines):
    keys = ["决定", "定在", "按这个", "方案", "确认", "同意", "落地"]
    out = []
    for line in lines:
        if any(k in line for k in keys):
            out.append(line)
    return out[:20]


def summarize_board(repo: Path, board: str, day: str):
    inbox = repo / board / "inbox" / day
    files = sorted(inbox.glob("*.md")) if inbox.exists() else []
    if not files:
        return None

    all_lines = []
    senders = Counter()
    for f in files:
        body = read_md_body(f)
        lines = split_lines(body)
        all_lines.extend(lines)
        m = re.search(r"^([^:]{1,40}):", body)
        if m:
            senders[m.group(1)] += 1

    keywords = extract_keywords(all_lines)
    todos = extract_todos(all_lines)
    decisions = extract_decisions(all_lines)

    out_dir = repo / board / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{day}.md"

    summary = [
        f"# {board.upper()} Daily - {day}",
        "",
        f"- 消息数量：{len(files)}",
        f"- 主要参与者：{', '.join([f'{k}({v})' for k, v in senders.most_common(8)]) or '无'}",
        f"- 关键词：{', '.join(keywords) or '无'}",
        "",
        "## 摘要",
        "- 当日消息已完成自动归档，详见 inbox 原文。",
        "",
        "## 关键结论",
    ]
    if decisions:
        summary += [f"- {x}" for x in decisions[:8]]
    else:
        summary += ["- 暂无明确决策语句。"]

    summary += ["", "## 待办事项"]
    if todos:
        summary += [f"- {x}" for x in todos[:10]]
    else:
        summary += ["- 暂无显式待办。"]

    summary += ["", "## 风险与提醒", "- 如需更高质量摘要，可在此基础上接入 LLM 精炼。", "", "## 原始记录路径", f"- `{board}/inbox/{day}/`"]

    out.write_text("\n".join(summary) + "\n", encoding="utf-8")
    return out


def summarize_shared(repo: Path, day: str, boards):
    available = [b for b in boards if (repo / b / "daily" / f"{day}.md").exists()]
    if not available:
        return None

    out_dir = repo / "shared" / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{day}.md"
    lines = [f"# Shared Daily - {day}", "", "## 跨群联动要点"]
    for b in available:
        lines.append(f"- 参考 `{b}/daily/{day}.md`")
    lines += ["", "## 建议", "- 次日优先处理待办交集和阻塞项。"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--day", help="YYYY-MM-DD, default yesterday (Asia/Shanghai)")
    p.add_argument("--boards", default="ai,finance,quant")
    args = p.parse_args()

    now = datetime.now(TZ_CN)
    day = args.day or (now - timedelta(days=1)).strftime("%Y-%m-%d")
    boards = [x.strip() for x in args.boards.split(",") if x.strip()]
    repo = Path(args.repo)

    outs = []
    for b in boards:
        out = summarize_board(repo, b, day)
        if out:
            outs.append(str(out))
    shared_out = summarize_shared(repo, day, boards)
    if shared_out:
        outs.append(str(shared_out))
    print("\n".join(outs))


if __name__ == "__main__":
    main()
