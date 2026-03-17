# Memory Compact

- updated_at: 2026-03-18T02:00:01.986943+08:00
- budget_tokens: 3000
- used_tokens_est: 344
- source_day: 2026-03-17

## Atomic Memories
- [decision] 你这个“历史任务可删除 \+ 级联清理 \+ 慢操作处理”我给你一版可落地方案（先设计，确认后我就实现）：
- [decision] \- 二次确认弹窗：提示“会删除明细、回合、曲线，不可恢复”
- [decision] 5\) 与“重启恢复策略C”一起落地
- [todo] 你要的话我可以直接给你做一版“最小性能修复包”（后端2处\+前端1处），先把页面卡顿明显降下来。"]
- [fact] \- backtest\_jobs 中关联结果（可选，见方案）
- [fact] 2\) 删除策略（推荐方案）
- [fact] 方案A（推荐）：异步软触发 \+ 后台硬删除
- [fact] 方案B：同步删除接口（不推荐）
- [fact] 方案C：软删除（只标记）
- [fact] 优点：慢删除不阻塞请求、体验稳定、可观察
- [fact] \- error 写入：服务重启中断，请手动重试
- [fact] 3. 写入统一错误信息：服务重启中断，请手动重试
- [fact] \- error=服务重启中断，请手动重试
- [fact] \- 但列表响应 schema 实际只需要轻量字段（状态/进度/时间）
- [fact] \- overview/trades/rounds/snapshots/strategy\-config 同时请求
- [fact] 4. 详情改懒加载（进入对应 tab 再请求 trades/rounds/snapshots）
- [fact] 如需更高质量摘要，可在此基础上接入 LLM 精炼。
- [fact] `quant/inbox/2026-03-17/`
