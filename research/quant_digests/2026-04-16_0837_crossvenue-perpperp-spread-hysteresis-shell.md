# 别把这份 cross-exchange 套利仓只读成“搬砖脚本”：对 short-cycle desk，更该先修的是「perp-perp spread convergence × entry/exit hysteresis」这条 raw alpha 壳

- 时间：2026-04-16 08:37 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `spread_strategy.py` + GitHub API metadata）+ Bybit/Binance public ticker live sanity probe（`SOLUSDT`, 0.5s 轮询，120 样本）
- 主题类型：raw alpha
- 基础 alpha：**同一标的在两个 perp venue 的瞬时价差会向中枢回归；当 `Binance-Bybit` spread 偏离阈值后，做多便宜腿/做空昂贵腿，等价差收敛后双腿平仓**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（代码里已有完整壳，但参数需先修正）
- 主题标签：raw-alpha/relative-value/stat-arb/cross-venue/perp-perp/same-underlier/spread-convergence/hysteresis/execution-shell/bybit/binance/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 代码证据 + 公共行情快检

## 1) 先回答：这篇东西的 base alpha 是什么？

一句话：**base alpha 不是“自动下单”本身，而是“同一标的跨 venue perp 报价偏离后的回归”。**

在 `spread_strategy.py` 里写得很直白：
- `spread_percent = ((binance_price - bybit_price) / bybit_price) * 100`
- `spread > entry_th`：`LONG Bybit / SHORT Binance`
- `spread < -entry_th`：`SHORT Bybit / LONG Binance`
- 价差回归后反向平双腿。

这就是标准的 **same-underlier cross-venue relative-value / stat-arb** 主体，不是 filter/overlay。

## 2) 来源信息（repo-based）

- Authors / Maintainer：Kristofer Meio-Renn（GitHub: `kmrlab`）
- Year：2025（`created_at=2025-08-27`）
- Title：*Cryptocurrency Arbitrage Strategies*（repo: `algo-arbitrage`）
- Venue：GitHub Repository
- DOI：N/A（仓库）
- Readable URL：<https://github.com/kmrlab/algo-arbitrage>
- Repo URL：<https://github.com/kmrlab/algo-arbitrage>

## 3) 为什么这条线值得进当前素材池

这份材料的价值不在“又一个跨所套利故事”，而在于它把完整策略骨架写全了：
1. **entry/exit 是显式状态机**（`in_position` + `position_type`）；
2. **仓位单位统一到可下单精度**（按美元换算数量，并向下取整到 `0.1`）；
3. **双腿下单失败回滚逻辑**有雏形（第二腿失败时尝试撤第一腿）；
4. **可直接映射短周期验证**（默认 `CHECK_INTERVAL=1s`，天然兼容 `1m/3m/5m/15m` 聚合评估）。

## 3.5) 策略拆解（必填）

- 方向属性：相对价值 / 统计套利（非裸方向）
- 基础 alpha：`same-underlier cross-venue perp spread mean reversion`
- regime：默认未建模（可后续加波动/流动性 regime）
- filter / veto：
  - 仅当 `abs(spread) >= MIN_SPREAD_PERCENT` 才开仓
  - 数量最小精度检查（`qty >= 0.1`）
  - API 请求超时/签名失败保护
- risk / sizing / execution overlay：
  - 单腿名义默认 `POSITION_SIZE_USD = 500`
  - 双腿对冲开平（Bybit + Binance）
  - 1 秒轮询；日志与账户/持仓状态监控

## 4) 关键数据点（可直接指导“先修什么”）

### 4.1 repo 参数本身
- 开仓阈值：`MIN_SPREAD_PERCENT = 0.02`（代码按百分比计算，即 **2 bps**）
- 平仓条件：`abs(spread) <= 0.1`（即 **10 bps**）
- 轮询频率：`1s`

### 4.2 public live 快检（本轮）
对 `SOLUSDT` 做 `0.5s × 120` 样本快检（Bybit/Binance 公共 ticker）：
- `|spread|` 中位数约 **1.17 bps**
- `|spread| >= 2 bps` 占比约 **21.7%**
- `|spread| >= 5 bps` / `>=10 bps` 占比均 **0%**（本样本）

这直接暴露一个可交易性问题：**当前 exit 阈值（10 bps）大于 entry 阈值（2 bps），hysteresis 方向反了**。若按原逻辑直接跑，极易出现“进场后很快触发平仓判定”或策略行为异常，先别急着实盘。

## 5) 与 `1m/3m/5m/15m` 的关系

- `1m/3m`：最适合做 spread 事件密度、持仓时长、滑点冲击的 first verdict；
- `5m/15m`：更适合做“阈值是否足够覆盖成本”的稳健性层（尤其 taker 场景）；
- 结论：这条线是 **秒级执行 + 分钟级评估** 的典型 short-cycle 壳，和当前 desk 节奏兼容。

## 6) 可复刻最小实验（今天就能开）

- 研究假设：cross-venue perp spread 在短窗内存在可交易回归，但需要正确 hysteresis 与成本门槛。
- 数据源（公开可得）：
  - Bybit `v5/market/tickers`
  - Binance `fapi/v1/ticker/price`（最好再补 best bid/ask）
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT`
- 频率：原始 1s，评估聚合到 `1m/3m/5m/15m`
- 最小规则（修正版建议）：
  - `entry_abs >= 4~6 bps`
  - `exit_abs <= 1~2 bps`
  - `max_hold = 3~10 min` 强平
- 最先看两项指标：
  1. 成本后单笔 EV（含双腿手续费+滑点）
  2. `entry->exit` 收敛完成率与中位持有时长

## 7) 风险与保留意见

1. 仅用 last price 会高估可成交性；必须切到 bid/ask 与深度口径。  
2. 双腿执行存在腿风险（一腿成交一腿失败），回滚逻辑需要更严格。  
3. 阈值在不同币种、不同时段差异很大，单一常数阈值容易过拟合。  
4. 高波动时段 spread 可能“扩而不归”，需加超时止损与仓位上限。

## 8) 下一步怎么测（本轮后直接动作）

1. **先修 hysteresis**：把阈值改成 `entry > exit`（例如 `5 bps` 入、`1.5 bps` 出）。
2. **做 friction ladder**：`4 / 8 / 12 bps` 总成本三档，检查策略是否仍为正 EV。
3. **做资产分层**：先 `BTC/ETH/SOL`，再扩到高波动 alt，比较收敛率和腿风险。
4. **加超时与失败回滚审计**：`max_hold`、`one-leg timeout`、`forced flatten` 三个硬约束。

---

## 参考

1. Kristofer Meio-Renn (`kmrlab`). *algo-arbitrage* (GitHub repo, 2025).  
   <https://github.com/kmrlab/algo-arbitrage>
2. Repo source file: `spread_strategy.py`  
   <https://raw.githubusercontent.com/kmrlab/algo-arbitrage/main/spread_strategy.py>
3. Repo source file: `README.md`  
   <https://raw.githubusercontent.com/kmrlab/algo-arbitrage/main/README.md>
4. GitHub API metadata  
   <https://api.github.com/repos/kmrlab/algo-arbitrage>
