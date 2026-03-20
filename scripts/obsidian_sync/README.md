# Obsidian Git Sync（方案B）

## 1) 初始化服务器仓库
```bash
bash scripts/obsidian_sync/init_repo.sh /home/ubuntu/.openclaw/workspace/obsidian-kb-server
```

## 2) 配置 chat_id 映射
编辑 `scripts/obsidian_sync/channels.json`：
```json
{
  "oc_f0e3cd308ffd2fea779bd59e79fa68a0": "ai",
  "oc_805962c00638505d51d8c12f157a7d97": "finance",
  "oc_4ae8526f72727cbd410fbc40a5d6aea2": "quant"
}
```

## 3) 实时采集（从 OpenClaw session 日志抓取全部消息）
```bash
python3 scripts/obsidian_sync/collect_from_sessions.py \
  --repo /home/ubuntu/.openclaw/workspace/obsidian-kb-server \
  --mapping scripts/obsidian_sync/channels.json
```

说明：
- 按 session 增量偏移读取，不会重复导入
- 默认状态文件：`scripts/obsidian_sync/.collect_state.json`

## 4) 每日知识沉淀（按天生成 daily）
```bash
# 默认汇总“昨天”
python3 scripts/obsidian_sync/summarize_daily.py \
  --repo /home/ubuntu/.openclaw/workspace/obsidian-kb-server

# 指定日期
python3 scripts/obsidian_sync/summarize_daily.py \
  --repo /home/ubuntu/.openclaw/workspace/obsidian-kb-server \
  --day 2026-03-11
```

输出：
- `ai/daily/YYYY-MM-DD.md`
- `finance/daily/YYYY-MM-DD.md`
- `quant/daily/YYYY-MM-DD.md`
- `shared/daily/YYYY-MM-DD.md`

## 5) 记忆压缩（Memory Compact）
```bash
python3 scripts/obsidian_sync/memory_compact.py \
  --repo /home/ubuntu/.openclaw/workspace/obsidian-kb-server \
  --day 2026-03-11 \
  --max-tokens 3000
```

输出（分群 + 全局）：
- `knowledge/ai/memory_compact.md`
- `knowledge/finance/memory_compact.md`
- `knowledge/quant/memory_compact.md`
- `knowledge/shared/memory_compact.md`
- 各自对应 `delta/YYYY-MM-DD.md` 与 `manifest.json`

按 query 检索压缩记忆：
```bash
python3 scripts/obsidian_sync/retrieve_compact.py \
  --repo /home/ubuntu/.openclaw/workspace/obsidian-kb-server \
  --scope ai \
  --query "cron 定时 同步" \
  --topk 8
```

## 6) 一键流水线（采集 + 汇总 + 压缩 + push）
```bash
# 默认处理昨天
bash scripts/obsidian_sync/run_pipeline.sh

# 指定日期
bash scripts/obsidian_sync/run_pipeline.sh 2026-03-11
```

## 7) 定时任务（服务器）
```cron
0 2 * * * /home/ubuntu/.openclaw/workspace/obsidian-kb-server/scripts/obsidian_sync/run_pipeline.sh
```

## 7) 本地电脑同步
1. `git clone <你的私有仓库地址>`
2. Obsidian 打开该目录
3. 定时 `git pull` 或手动拉取

## 8) 建议
- `inbox/` 只做原始归档，不手工改
- 结构化知识主看 `daily/` 与 `shared/daily/`
