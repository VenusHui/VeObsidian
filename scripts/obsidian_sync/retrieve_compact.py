#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def score(line: str, query: str):
    q = [x for x in re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", query.lower()) if len(x) > 1]
    s = line.lower()
    return sum(1 for t in q if t in s)


def parse_cards(text: str):
    cards = []
    current = []
    for raw in text.splitlines():
        ln = raw.rstrip()
        if ln.startswith("### 主题："):
            if current:
                cards.append("\n".join(current))
            current = [ln]
        elif current and ln.startswith("- "):
            current.append(ln)
        elif current and not ln.strip():
            current.append(ln)
    if current:
        cards.append("\n".join(current))
    return cards


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--query", required=True)
    p.add_argument("--scope", default="shared", help="ai|finance|quant|shared")
    p.add_argument("--topk", type=int, default=8)
    args = p.parse_args()

    path = Path(args.repo) / "knowledge" / args.scope / "memory_compact.md"
    if not path.exists():
        print(f"(memory_compact.md not found for scope={args.scope})")
        return

    cards = parse_cards(path.read_text(encoding="utf-8"))
    ranked = sorted(cards, key=lambda x: score(x, args.query), reverse=True)
    out = [x for x in ranked if score(x, args.query) > 0][: args.topk]
    if not out:
        out = ranked[: min(args.topk, len(ranked))]
    print("\n\n".join(out))


if __name__ == "__main__":
    main()
