# Memory Compact

- updated_at: 2026-03-13T02:00:01.944461+08:00
- budget_tokens: 3000
- used_tokens_est: 187
- source_day: 2026-03-12

## Atomic Memories
- [decision] 再确认一个约束：第一版策略代码的来源你希望是
- [decision] C\) 先A，后续再考虑B（更安全也更快落地）"]
- [todo] 按照dev/**触发吧，另外帮我检查一下我的GitHub actions配置是否有问题，有的话一并帮我修复了
- [fact] 方案 1（我推荐）：轻量自研回测引擎（贴合你现有架构）
- [fact] 方案 2：接入 Backtrader 作为底层引擎
- [fact] A\) 同步执行（请求发起后直接等待结果，简单）
- [fact] \- 缺点：需要自己维护撮合与指标计算代码。
- [fact] \- schemas/backtest.py：回测请求/响应结构
- [fact] 如需更高质量摘要，可在此基础上接入 LLM 精炼。
- [fact] `quant/inbox/2026-03-12/`
