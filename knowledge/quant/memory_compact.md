# Memory Compact

- scope: quant
- standard: Done / Learned / Next / Risks
- source_window: latest 7 delta files

## Done Snapshot
- 方案 1（我推荐）：轻量自研回测引擎（贴合你现有架构）
- 方案 2：接入 Backtrader 作为底层引擎
- 你现在需要做两步确认生效：
- 我先给你一个极简改造方案，确认后我马上落代码并推送：
- 你回我一句“确认”，我就直接改并推到 dev/v1.1.0。
- QUANT 无新增已完成事项。
- 如果你同意，我现在就直接改这两块并给你一轮 curl 对比结果。
- 我先给你一个简版设计（确认后我就直接改）：
- 只确认最后一个点：
- 从你们刚才的验收信息看，目前只能确认回测任务在跑、进度在更新，还不能直接证明“每笔交易记录和结果明细”已经入库（那需要看库表/接口或直接查一次 DB）。

## Reusable Patterns
- 再确认一个约束：第一版策略代码的来源你希望是
- 方案A（推荐）：异步软触发 + 后台硬删除
- 方案B：同步删除接口（不推荐）
- 方案C：软删除（只标记）

## Next Priorities
- C) 先A，后续再考虑B（更安全也更快落地）
- A) 同步执行（请求发起后直接等待结果，简单）
- 缺点：需要自己维护撮合与指标计算代码。
- schemas/backtest.py：回测请求/响应结构
- 按照dev/**触发吧，另外帮我检查一下我的GitHub actions配置是否有问题，有的话一并帮我修复了
- 如果你同意，我可以直接改一版：
- 你直接帮我操作修复，然后重新提交
- 我又做了一轮兜底修复并已推送：
- data_processor.py：修复 numpy 2.x 下 np.trapz 不可用问题（改兼容 np.trapezoid）
- 你现在需要做两步确认生效：

## Active Risks
- body: 太好了，这样后续就顺了。\n那我后面就按这个分支直接推送推进；你现在可以先看这次 dev/v1.1.0 的 Actions 跑结果，如果有任何失败日志我来直接定位并修复。
- body: 已直接帮你修复并推送了 ✅\n这次我处理了两处根因：\n1. 网络抖动导致 AKShare 分时接口断连\n- 在 fetch_minute_data 增加了重试机制（默认最多重试 2 次，带退避等待）\n- 避免 RemoteDisconnected 一次失败就直接打穿流程\n2. 无数据时 datetime 列不存在导致 500\n- 在 get_minute_data 里对空结果做了兜底：\n- 返回带标准列的空 DataFrame（含 datetime）\n- 空数据时不再访问 result_df\\[\datetime\\\]，避免 KeyError: 'datetime'\n已提交并推送到 dev/v1.1.0：\n- commit: 0e3be16\n- message: fix: handle empty minute data and retry akshare requests\n你现在可以再触发一次回测验证；按这个修复，之前那种 500（获取分钟数据失败: 'datetime'）应该不会再出现了。
- body: 已帮你修复并提交 ✅\n- 已对报错的 10 个 Python 文件执行 Black 格式化\n- 已提交到分支 dev/v1.1.0\n- 提交哈希：516e8e2\n- 已推送到远端：origin/dev/v1.1.0\n你现在可以直接去看这次 Actions，理论上这个 black --check . 报错会消失。
- 优点：慢删除不阻塞请求、体验稳定、可观察
- 你要的话我可以直接给你做一版“最小性能修复包”（后端2处+前端1处），先把页面卡顿明显降下来。
