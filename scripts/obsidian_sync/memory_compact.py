#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

TZ_CN = timezone(timedelta(hours=8))

SECTION_KIND = {
    "关键结论": "decision",
    "待办事项": "todo",
    "风险与提醒": "risk",
    "摘要": "fact",
}

TOPIC_RULES = [
    ("Memory 压缩格式修复", ["memory", "compact", "流水账", "主题", "卡片", "atomic"]),
    ("OpenClaw vs ZeroClaw 选型", ["openclaw", "zeroclaw", "切换", "可用性", "优劣"]),
    ("Page-Agent 项目", ["page-agent", "page agent"]),
    ("知识库同步自动化", ["定时", "凌晨", "自动创建", "同步", "pipeline", "run_pipeline", "heartbeat"]),
    ("知识库重刷与回填", ["全量", "重刷", "历史", "刷一遍", "delta", "knowledge"]),
]

STOPWORDS = {
    "胡锦晖", "为什么", "现在", "这个", "那个", "我们", "你", "我", "需要", "然后", "如果", "已经", "继续", "今天", "昨天", "可以",
    "回复", "确认", "流程", "方案", "默认", "输出", "问题", "处理", "修复", "记录", "项目", "对话", "内容", "消息", "建议",
}


def normalize(line: str):
    x = re.sub(r"\s+", " ", line).strip()
    x = re.sub(r"\[.*?\]\(.*?\)", "", x).strip()
    return x


def clean_line_for_output(line: str):
    x = normalize(line)
    x = x.strip('"\'[] ')
    x = re.sub(r"^[-:：\s]+", "", x)
    return x


def good_line(body: str):
    bad = [
        "replying to",
        "message_id",
        "[interactive card]",
        "```",
        "agent:main",
        "http://127.0.0.1",
        "主要参与者",
        "关键词：",
        "当日消息已完成自动归档",
        "原始记录路径",
        "参考 `",
        "你回 a/b/c",
        "先按流程确认一个关键点",
        "我先给你",
        "你回我一句",
        "下一步只需要你确认",
        "只确认最后一个点",
    ]
    low = body.lower()
    if any(b in low for b in bad):
        return False
    if body.count("[") + body.count("]") > 4:
        return False
    if len(body) > 180:
        return False
    return True


def extract_from_daily(path: Path):
    text = path.read_text(encoding="utf-8")
    current_section = ""
    items = []
    for raw in text.splitlines():
        ln = raw.strip()
        if ln.startswith("## "):
            current_section = ln[3:].strip()
            continue
        if not ln.startswith("- "):
            continue
        body = clean_line_for_output(ln[2:])
        if len(body) < 8 or not good_line(body):
            continue
        kind = SECTION_KIND.get(current_section, "fact")
        items.append((kind, body))
    return items


def dedupe(items):
    seen = set()
    out = []
    for k, t in items:
        key = re.sub(r"[^\w\u4e00-\u9fff]+", "", t.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append((k, t))
    return out


def guess_topic(text: str):
    low = text.lower()
    for topic, keys in TOPIC_RULES:
        if any(k in low for k in keys):
            return topic

    tokens = re.findall(r"[A-Za-z0-9_\-\u4e00-\u9fff]{2,}", text)
    tokens = [t for t in tokens if t not in STOPWORDS and not t.isdigit()]
    if tokens:
        return f"{tokens[0]} 相关"
    return "其他事项"


def load_existing_cards(compact_path: Path):
    if not compact_path.exists():
        return {}
    text = compact_path.read_text(encoding="utf-8")
    cards = {}
    current = None
    for raw in text.splitlines():
        ln = raw.strip()
        if ln.startswith("### 主题："):
            current = ln.replace("### 主题：", "", 1).strip()
            cards[current] = {"decision": [], "todo": [], "risk": [], "fact": []}
        elif current and ln.startswith("- 结论："):
            v = ln.replace("- 结论：", "", 1).strip()
            if v and v != "（暂无）":
                cards[current]["decision"].append(v)
        elif current and ln.startswith("- 后续动作："):
            v = ln.replace("- 后续动作：", "", 1).strip()
            if v and v != "（暂无）":
                cards[current]["todo"].append(v)
        elif current and ln.startswith("- 风险："):
            v = ln.replace("- 风险：", "", 1).strip()
            if v and v != "（暂无）":
                cards[current]["risk"].append(v)
        elif current and ln.startswith("- 补充："):
            v = ln.replace("- 补充：", "", 1).strip()
            if v:
                cards[current]["fact"].append(v)
    return cards


def merge_to_topic_cards(existing_cards, new_items):
    cards = defaultdict(lambda: {"decision": [], "todo": [], "risk": [], "fact": []})

    for t, payload in existing_cards.items():
        for k, lines in payload.items():
            cards[t][k].extend(lines)

    for kind, line in new_items:
        topic = guess_topic(line)
        cards[topic][kind].append(line)

    for topic in list(cards.keys()):
        for k in cards[topic].keys():
            deduped = []
            seen = set()
            for line in cards[topic][k]:
                key = re.sub(r"[^\w\u4e00-\u9fff]+", "", line.lower())
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(line)
            cards[topic][k] = deduped

    return cards


def pick_best(lines):
    if not lines:
        return "（暂无）"
    return lines[0]


def estimate_tokens(s: str):
    return max(1, len(s) // 2)


def topic_score(payload):
    return len(payload["decision"]) * 4 + len(payload["todo"]) * 3 + len(payload["risk"]) * 3 + len(payload["fact"]) * 1


def render_cards(day: str, cards: dict, max_tokens: int):
    ordered = sorted(cards.items(), key=lambda kv: topic_score(kv[1]), reverse=True)

    header = [
        "# Memory Compact",
        "",
        f"- updated_at: {datetime.now(TZ_CN).isoformat()}",
        f"- source_day: {day}",
        f"- style: 主题 -> 结论 -> 后续动作",
        "",
    ]

    body = []
    used = estimate_tokens("\n".join(header))
    kept_topics = 0
    for topic, payload in ordered:
        decision = pick_best(payload["decision"] or payload["fact"])
        todo = pick_best(payload["todo"])
        risk = pick_best(payload["risk"])
        extra = []
        for line in payload["decision"][1:2] + payload["todo"][1:2] + payload["fact"][:1]:
            if line not in {decision, todo, risk}:
                extra.append(line)

        card_lines = [
            f"### 主题：{topic}",
            f"- 结论：{decision}",
            f"- 后续动作：{todo}",
            f"- 风险：{risk}",
        ]
        if extra:
            card_lines.append(f"- 补充：{'; '.join(extra)}")
        card_lines.append("")

        block = "\n".join(card_lines)
        tk = estimate_tokens(block)
        if used + tk > max_tokens:
            continue
        body.extend(card_lines)
        used += tk
        kept_topics += 1

    return header + body, used, kept_topics


def write_scope(scope_dir: Path, day: str, new_items, max_tokens: int):
    scope_dir.mkdir(parents=True, exist_ok=True)
    compact_path = scope_dir / "memory_compact.md"

    # 按日重建：只保留 source_day 的主题卡，避免跨天累积成“流水帐”。
    cards = merge_to_topic_cards({}, dedupe(new_items))
    rendered, used, kept_topics = render_cards(day, cards, max_tokens)
    compact_path.write_text("\n".join(rendered).rstrip() + "\n", encoding="utf-8")

    delta_path = scope_dir / "delta" / f"{day}.md"
    delta_path.parent.mkdir(parents=True, exist_ok=True)
    grouped = defaultdict(list)
    for kind, line in dedupe(new_items):
        grouped[guess_topic(line)].append((kind, line))

    delta_lines = [f"# Memory Delta - {day}", "", "# 新增主题卡"]
    for topic, items in grouped.items():
        delta_lines.append(f"\n## 主题：{topic}")
        dec = [x for k, x in items if k in ("decision", "fact")]
        todo = [x for k, x in items if k == "todo"]
        risk = [x for k, x in items if k == "risk"]
        delta_lines.append(f"- 结论：{pick_best(dec)}")
        delta_lines.append(f"- 后续动作：{pick_best(todo)}")
        delta_lines.append(f"- 风险：{pick_best(risk)}")

    delta_path.write_text("\n".join(delta_lines).rstrip() + "\n", encoding="utf-8")

    manifest = {
        "day": day,
        "new_items": len(new_items),
        "kept_topics": kept_topics,
        "used_tokens_est": used,
        "max_tokens": max_tokens,
        "style": "topic-card",
    }
    (scope_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--day", help="YYYY-MM-DD, default yesterday")
    p.add_argument("--max-tokens", type=int, default=3000)
    p.add_argument("--boards", default="ai,finance,quant")
    args = p.parse_args()

    repo = Path(args.repo)
    now = datetime.now(TZ_CN)
    day = args.day or (now - timedelta(days=1)).strftime("%Y-%m-%d")
    boards = [b.strip() for b in args.boards.split(",") if b.strip()]

    knowledge_root = repo / "knowledge"
    knowledge_root.mkdir(parents=True, exist_ok=True)

    results = {}
    shared_items = []
    active_boards = []
    for b in boards:
        path = repo / b / "daily" / f"{day}.md"
        if not path.exists():
            continue
        board_items = dedupe(extract_from_daily(path))
        if not board_items:
            continue
        active_boards.append(b)
        shared_items.extend(board_items)
        results[b] = write_scope(knowledge_root / b, day, board_items, args.max_tokens)

    shared_items = dedupe(shared_items)
    if shared_items:
        results["shared"] = write_scope(knowledge_root / "shared", day, shared_items, args.max_tokens)

    print(json.dumps({"day": day, "active_boards": active_boards, "scopes": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
