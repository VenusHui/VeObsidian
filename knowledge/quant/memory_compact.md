# Memory Compact

- updated_at: 2026-03-19T02:24:39.436191+08:00
- budget_tokens: 3000
- used_tokens_est: 230
- source_day: 2026-03-18

## Atomic Memories
- [decision] 我先给你 3 个实现方案（含取舍），你拍板后我就按选定方案落地：
- [todo] \- 数据来源先用你现有 txt 并按方案 2 的方式做“轻预处理”
- [todo] 我已经修复并推送了 ✅
- [todo] 还是有问题，你本地运行npm run build查看并修复吧
- [todo] 我做了这部分修复：
- [fact] 方案 1（推荐）：请求时动态过滤（参数直传）
- [fact] 方案 2：预生成静态池文件（你提到的 txt 思路）
- [fact] 方案 3：数据库维表驱动（长期最优）
- [fact] 短期采用 方案 1 \+ 方案 2 混合：
- [fact] \- 接口层面按方案 1（参数驱动，前后端联动）
- [fact] \- 请求来时根据参数做集合并/差
- [fact] \- 需要维护池更新机制（防止过期）
- [fact] A,就放在主库里，后面有需要再分库
- [fact] 如需更高质量摘要，可在此基础上接入 LLM 精炼。
- [fact] `quant/inbox/2026-03-18/`
