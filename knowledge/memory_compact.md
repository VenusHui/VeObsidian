# Memory Compact

- updated_at: 2026-03-11T23:40:00+08:00
- budget_tokens: 3000
- used_tokens_est: 180
- source_day: 2026-03-11

## Atomic Memories
- [decision] 采集范围为 AI 与 finance 两个 Feishu 群的全部消息，先落 raw inbox。
- [decision] 每天 02:00（Asia/Shanghai）执行流水线：采集 → daily 总结 → memory compact → git push。
- [decision] 知识库远程仓库使用 git@github.com:VenusHui/VeObsidian.git。
- [constraint] 长期记忆采用 compact 预算控制，不向会话注入全文，优先检索 topK 相关记忆。
- [constraint] 原始消息保留在 inbox，仅作为追溯依据，不作为长期上下文直接注入。
- [fact] chat_id 映射：oc_f0e3cd308ffd2fea779bd59e79fa68a0 -> ai；oc_805962c00638505d51d8c12f157a7d97 -> finance。
- [fact] 主入口脚本：scripts/obsidian_sync/run_pipeline.sh。
- [todo] V3 将 memory 条目升级为结构化字段：事实/决策/待办/负责人/截止日期/置信度。
