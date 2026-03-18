# Memory Compact

- scope: quant
- standard: Done / Learned / Next / Risks
- update_policy: skip empty day files

## Done Snapshot
- 胡锦晖: [Replying to: 完全同意，先做纯代码是最稳的。下一个关键选择：回测执行方式你要哪种优先？
- 再确认一个约束：第一版策略代码的来源你希望是
- 方案 1（我推荐）：轻量自研回测引擎（贴合你现有架构）
- 方案 2：接入 Backtrader 作为底层引擎
- A\) 同步执行（请求发起后直接等待结果，简单）
- 缺点：需要自己维护撮合与指标计算代码。
- 你现在需要做两步确认生效：
- 如果你同意，我可以直接改一版：
- 我先给你一个极简改造方案，确认后我马上落代码并推送：
- 你回我一句“确认”，我就直接改并推到 dev/v1.1.0。

## Reusable Patterns
- 胡锦晖: [Replying to: 完美，这样第一版风险最低、迭代最快。基于你选的方向（纯代码、先同步后异步、先内置策略模板），我给你 3 个实现方案：
- \) 删除策略（推荐方案）
- 方案A（推荐）：异步软触发 + 后台硬删除
- 方案B：同步删除接口（不推荐）
- 方案C：软删除（只标记）

## Next Priorities
- 胡锦晖: [Replying to: 你这个起点其实很好：工程能力强 + 有交易想法，比“只会因子名词”更容易落地。你不用先啃一堆高深量化理论，先走一条“规则化想法 → 可回测 → 小资金验证”的工程路线就行。
- 胡锦晖: [Replying to: 很好，你这个基础已经能直接进入“可落地回测”阶段了。先确认一个关键点：第一版回测你更想优先支持哪类策略表达？
- C\) 先A，后续再考虑B（更安全也更快落地）
- 按照dev/**触发吧，另外帮我检查一下我的GitHub actions配置是否有问题，有的话一并帮我修复了
- 我现在一次有效的回测都做不出来了，你在实现之后需要多做一些测试
- 如果你同意，我下一步就按你刚说的方向直接做两件事：
- 你选一个，我按这个做完整设计并落地。
- 下一步我只确认一件事：
- 胡锦晖: 我现在一次有效的回测都做不出来了，你在实现之后需要多做一些测试
- 我希望你能通过curl或者其他发请求的方式，帮我测试回测模块的可用性

## Active Risks
- body: 太好了，这样后续就顺了。\n那我后面就按这个分支直接推送推进；你现在可以先看这次 dev/v1.1.0 的 Actions 跑结果，如果有任何失败日志我来直接定位并修复。
- [message_id: om_x100b540243aed508b216c833283a2eb] 胡锦晖: [Replying to: 太好了，这样后续就顺了。 那我后面就按这个分支直接推送推进；你现在可以先看这次 dev/v1.1.0 的 Actions 跑结果，如果有任何失败日志我来直接定位并修复。 Github Actions失败了，报错如下： Run # 代码格式检查（失败时应直接失败） # 代码格式检查（失败时应直接失败） black --check . shell: /usr/bin/bash -e {0} env: DOCKER_REGISTRY: ghcr.io IMAGE_PREFIX: VenusHui/vewealth pythonLocation: /opt/hostedtoolcache/Python/3.12.12/x64 PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib/pkgconfig Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64 Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64 Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.12.12/x64 LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.12.12/x64/lib would reformat /home/runner/work/VeWealth/VeWealth/backend/app/core/logger.py would reformat /home/runner/work/VeWealth/VeWealth/backend/app/models/backtest.py would reformat /home/runner/work/VeWealth/VeWealth/backend/app/routers/backtest.py would reformat /home/runner/work/VeWealth/VeWealth/backend/app/services/backtest/registry.py would reformat /home/runner/work/VeWealth/VeWealth/backend/app/services/backtest/metrics.py would reformat /home/runner/work/VeWealth/VeWealth/backend/app/services/backtest/engine.py would reformat /home/runner/work/VeWealth/VeWealth/backend/app/services/backtest/service.py would reformat /home/runner/work/VeWealth/VeWealth/backend/migration/db/v1/migrate_add_password.py would reformat /home/runner/work/VeWealth/VeWealth/backend/setup_database.py would reformat /home/runner/work/VeWealth/VeWealth/backend/app/services/stock_service.py Oh no! 💥 💔 💥 10 files would be reformatted, 35 files would be left unchanged. Error: Process completed with exit code 1.
- body: 已直接帮你修复并推送了 ✅\n这次我处理了两处根因：\n1. 网络抖动导致 AKShare 分时接口断连\n- 在 fetch\\_minute\\_data 增加了重试机制（默认最多重试 2 次，带退避等待）\n- 避免 RemoteDisconnected 一次失败就直接打穿流程\n2. 无数据时 datetime 列不存在导致 500\n- 在 get\\_minute\\_data 里对空结果做了兜底：\n- 返回带标准列的空 DataFrame（含 datetime）\n- 空数据时不再访问 result\\_df\\[\datetime\\\]，避免 KeyError: 'datetime'\n已提交并推送到 dev/v1.1.0：\n- commit: 0e3be16\n- message: fix: handle empty minute data and retry akshare requests\n你现在可以再触发一次回测验证；按这个修复，之前那种 500（获取分钟数据失败: 'datetime'）应该不会再出现了。
- [message_id: om_x100b5403216aa0ecc2aca6d015185c8] 胡锦晖: [Replying to: 已直接帮你修复并推送了 ✅ 这次我处理了两处根因： 1. 网络抖动导致 AKShare 分时接口断连 - 在 fetch\_minute\_data 增加了重试机制（默认最多重试 2 次，带退避等待） - 避免 RemoteDisconnected 一次失败就直接打穿流程 2. 无数据时 datetime 列不存在导致 500 - 在 get\_minute\_data 里对空结果做了兜底： - 返回带标准列的空 DataFrame（含 datetime） - 空数据时不再访问 result\_df\[datetime\]，避免 KeyError: 'datetime' 已提交并推送到 dev/v1.1.0： - commit: 0e3be16 - message: fix: handle empty minute data and retry akshare requests 你现在可以再触发一次回测验证；按这个修复，之前那种 500（获取分钟数据失败: 'datetime'）应该不会再出现了。 获取股票 000001 分时数据失败: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) 获取分钟数据失败: 'datetime' INFO: 211.95.108.226:2056 - POST /api/backtest/run HTTP/1.1 500 Internal Server Error INFO: 127.0.0.1:53154 - GET /health HTTP/1.1 200 OK INFO: 220.196.160.124:47682 - GET /api/stock/cyq?symbol=002364&adjust= HTTP/1.1 200 OK INFO: 220.196.160.95:26704 - GET /api/watchlist HTTP/1.1 401 Unauthorized INFO: 127.0.0.1:45896 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:35832 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:60702 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:60258 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:60462 - GET /health HTTP/1.1 200 OK INFO: 180.101.245.248:26656 - GET /api/backtest/run HTTP/1.1 405 Method Not Allowed INFO: 127.0.0.1:53566 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:48942 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:35230 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:37818 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:39566 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:38826 - GET /health HTTP/1.1 200 OK INFO: 127.0.0.1:46178 - GET /health HTTP/1.1 200 OK 获取股票 002364 分时数据失败: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) 2026-03-13 02:22:51 | ERROR | vewealth.data_processor:fit_gaussian_mixture:171 | GMM拟合失败: module 'numpy' has no attribute 'trapz' Traceback (most recent call last): File /app/app/utils/data_processor.py, line 129, in fit_gaussian_mixture density_integral = np.trapz(densities, price_range) ^^^^^^^^ File /usr/local/lib/python3.12/site-packages/numpy/__init__.py, line 792, in __getattr__ raise AttributeError(fmodule {__name__!r} has no attribute {attr!r}) AttributeError: module 'numpy' has no attribute 'trapz'. Did you mean: 'trace'? 仍然有问题，是不是akshare的数据源问题，我太多次频繁访问，导致ip被限制了？
- body: 已帮你修复并提交 ✅\n- 已对报错的 10 个 Python 文件执行 Black 格式化\n- 已提交到分支 dev/v1.1.0\n- 提交哈希：516e8e2\n- 已推送到远端：origin/dev/v1.1.0\n你现在可以直接去看这次 Actions，理论上这个 black --check . 报错会消失。
- [message_id: om_x100b540373bb9484c3adc4678337a96] 胡锦晖: [Replying to: 已帮你修复并提交 ✅ - 已对报错的 10 个 Python 文件执行 Black 格式化 - 已提交到分支 dev/v1.1.0 - 提交哈希：516e8e2 - 已推送到远端：origin/dev/v1.1.0 你现在可以直接去看这次 Actions，理论上这个 black --check . 报错会消失。 我在执行回测的时候有报错 获取股票 000001 分时数据失败: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) 获取分钟数据失败: 'datetime' INFO: 211.95.108.226:2051 - POST /api/backtest/run HTTP/1.1 500 Internal Server Error
- 优点：慢删除不阻塞请求、体验稳定、可观察
- 你要的话我可以直接给你做一版“最小性能修复包”（后端2处+前端1处），先把页面卡顿明显降下来。
