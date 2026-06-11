# 别把这份 2025 cash-and-carry repo 只读成 basis 教材：对 short-cycle desk，更该先测的是「positive-basis carry × 15m slot execution × rollover/rehedge shell」这条完整 raw alpha

- 时间：2026-04-07 13:34 UTC
- 类型：GitHub repo source audit（`README.md` + `README_backtest_with_rollovers.md` + `task1.py` + `backtest_with_rollovers.py`）
- 主题类型：raw alpha
- 基础 alpha：当 BTC 现货与 Binance COIN-M 季度合约之间存在**正 basis / 正 annualized carry** 时，做多现货、做空季度合约，吃期现价差向到期收敛；执行层再用 15 分钟切片、rollover 与 delta rehedge 把这条 carry 真正做成可长期持有的策略壳。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / carry / basis / spot-perp / spot-quarterly / delta-neutral / binance / coin-m / execution / rollover / rehedge / 15m / 5m / 1m / repo / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这次看的是 **Krish Saraf (2025)** 的 GitHub 仓库 **`KrishSaraf/BTC-Cash-and-Carry`**。它最有价值的地方不是“basis 会收敛”这句常识，而是把一条 **carry raw alpha** 从入场、分片执行、近月切换、日度再对冲、到最终平仓，写成了能直接拿来做 first verdict 的完整策略链条。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值得 intake 的不是“做多 spot 做空 futures”六个字，而是“**正 basis carry 本体 + 15m child-order 执行 + 近到期 rollover + delta 漂移再对冲**”这个完整可交易外壳。
- **一句话证明方式：** 证据来自源码闭环：`task1.py` 负责 basis 扫描与 24h 进场，`backtest_with_rollovers.py` 负责多日持有、近到期移仓与 EOD 再对冲，README 直接给出 2025 回测摘要与执行假设。
- README 写得很明确：2025-01-01 到 2025-11-17、初始资金 **$1,000,000**，组合总收益 **$79,781（+7.98%）**，对应 **9.15% APR**。
- 仓位定义也很干净：**long `BTCUSDT` spot + short Binance COIN-M `BTCUSD` 季度合约**；入场时会在 CURRENT / NEXT quarter 中选 **basis 更高的那只**。
- `task1.py` 用 **1m** 对齐现货与季度合约行情，算 `basis_bps=(F-S)/S*1e4` 与 `ann_return=((F-S)/S)*(365/dte)`，再把 24 小时切成 **96 个 15m slot** 做分片执行。
- 执行不是死 TWAP：仓库会用 **历史时段权重 + recent 15m volume + 是否落后于进度 + basis 压缩情况** 决定 child size 和是否更激进挂价。
- 持仓管理也完整：**到期前 2 天 roll**，**净 delta 偏离 spot 仓位 5% 就再对冲**，roll / rehedge / unwind 全部有日志与 PnL 跟踪。

## 3. 为什么和当前项目有关
这条线对当前 `momentum` 有价值，不是因为它能冒充 `5m` 方向信号，而是因为它补的是 **carry / basis 这类可独立实盘的 raw alpha**：
1. **base alpha 很清楚**：正 basis 收敛，不是 filter 伪装。
2. **完整策略壳现成**：entry / sizing / roll / rehedge / exit / logs 都写了。
3. **短周期映射方式诚实**：alpha 本体是低换手 carry，但执行与风险控制天然可落到 `1m/5m/15m` 子时钟。
4. **适合做 desk 的异质化原料**：它能和 trend / MR / maker 书并行，提供非方向性的收益来源。

## 3.5 策略拆解（必填）
- 方向属性：carry / basis / delta-neutral relative value
- 基础 alpha：季度合约相对现货的正溢价向到期收敛
- regime：basis 为正且年化 carry 高于 fee / borrow / slippage / rollover 成本的时段
- filter / veto：basis 不足、到期结构太差、volume 太薄、执行进度过慢时不做或降速
- risk / sizing / execution overlay：96×15m 分片、PoV 限额、近到期前 2 天移仓、净 delta 超过 5% 再对冲、最终 24h 平仓清 book

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设：** Binance BTC 现货 vs COIN-M 季度合约的正 basis，在扣掉真实 fee / borrow / rollover friction 后，仍能形成可保留的 carry edge；而 repo 的价值主要在于把这条 edge 做成“可长期拿”的执行壳。

**最小实验口径：**
- 标的：`BTCUSDT` 现货 + Binance COIN-M `BTCUSD` CURRENT / NEXT quarter
- 数据：公开 `1m` spot klines、COIN-M continuous klines、合约到期信息；执行聚合到 **15m slots**
- 入场：`annualized_basis > hurdle`（先测 `8% / 10% / 12%` 三档）且 basis 为正；CURRENT / NEXT 选更高 carry 合约
- 持有：每日收盘检查 `|net_delta| > 5%` 是否再对冲；`days_to_expiry <= 2` 触发 24h rollover
- 平仓：basis 压缩到低于 hurdle、或达到测试窗口终点，按 24h TWAP/PoV unwind
- 成本：现货手续费 + COIN-M 手续费 + 借币/资金占用 + 8/15/25bps slippage ladder

**先看 3 个指标：**
1. net APR / post-cost carry
2. rollover loss 占总收益比例
3. delta drift / adverse basis move 对回撤的贡献

如果 carry 本体成立、但 `1m/5m` 做得太碎导致摩擦过高，就保留它的 **15m/日度执行壳**，不要硬伪装成逐 bar 高频 alpha。

## 5. 风险与保留意见
- 这不是“每根 5m K 都给方向”的策略，**alpha 本体是 carry，不是 intraday directional signal**；对 short-cycle desk 的意义主要在执行层和组合分散。
- README 回测结果是作者自报，当前还需要补充真实 fee、借币成本、COIN-M 资金效率与极端行情下的基差跳变压力测试。
- 仓库默认规模是 **$1M**，child-order / PoV 参数对小账户或更大账户未必同样成立。
- 期货侧用的是 **inverse COIN-M** 结构，PnL 公式与 USDⓈ-M 不同，迁移时不能直接照搬。

> **最值得复用/复现的点：** 不是“basis 会收敛”这个老知识，而是 repo 把 **carry alpha → 15m execution → rollover → rehedge → flat exit** 全链条写出来了。

## 6. 来源
1. **Saraf, K. (2025). _BTC-Cash-and-Carry_. GitHub Repository.**
   - Venue：GitHub
   - DOI：N/A
   - Readable URL：`https://github.com/KrishSaraf/BTC-Cash-and-Carry`
   - Repo URL：`https://github.com/KrishSaraf/BTC-Cash-and-Carry`
2. **关键源码 / 文档**
   - `README.md`：`https://raw.githubusercontent.com/KrishSaraf/BTC-Cash-and-Carry/main/README.md`
   - `README_backtest_with_rollovers.md`：`https://raw.githubusercontent.com/KrishSaraf/BTC-Cash-and-Carry/main/README_backtest_with_rollovers.md`
   - `task1.py`：`https://raw.githubusercontent.com/KrishSaraf/BTC-Cash-and-Carry/main/task1.py`
   - `backtest_with_rollovers.py`：`https://raw.githubusercontent.com/KrishSaraf/BTC-Cash-and-Carry/main/backtest_with_rollovers.py`
3. **公开数据口径（最小复现实验可得）**
   - Binance Spot Klines：`https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`
   - Binance COIN-M Continuous Contract Klines：`https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/rest-api/Continuous-Contract-Kline-Candlestick-Data`
   - Binance COIN-M Exchange Info：`https://developers.binance.com/docs/derivatives/coin-margined-futures/market-data/rest-api/Exchange-Information`
