# 别把 perp-perp funding diff 继续写成 funding 排名表：这份 2026 GitHub 仓库更该先测的是「net-EV hurdle × same-underlier venue pair」raw alpha
- 时间：2026-03-30 19:19 UTC
- 类型：2026 GitHub 仓库 + `README` / `config/main.yaml` / `strategies/perp_perp.py` / `optimization/opportunity_ranker.py` / `portfolio/profit_model.py` / `scripts/run_live_screener.py` source audit + Binance/Bybit/OKX 公开 funding live sanity check
- 主题类型：raw alpha
- 基础 alpha：同一币种跨 venue 做 `short 高 funding perp + long 低 funding perp`，只在 funding differential **扣完完整成本栈后** 仍有净边时入场
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/perp-perp/cross-venue/relative-value/stat-arb/same-underlier/net-ev-hurdle/cost-stack/8h-clock/binance/bybit/okx/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：工程实现证据 + 公开 live 快照 + 本地成本复核

## 1. 这次看了什么
主材料是 **gencersarp** 在 2026-03 仍在更新的 GitHub 仓库 **`cryptoarb`**。我重点看了：
- `README.md`
- `config/main.yaml`
- `strategies/perp_perp.py`
- `optimization/opportunity_ranker.py`
- `portfolio/profit_model.py`
- `scripts/run_live_screener.py`

这次真正值得 intake 的，不是“跨所 funding 有时不一样”这个老结论，而是 repo 把 **same-underlier、same-contract-family 的 perp-perp funding differential** 写成了一个可以直接做 first verdict 的完整骨架：
1. 先做 **venue pair 同币 funding spread**；
2. 再用 **spread z-score** 过滤薄边噪音；
3. 再把 **fees / slippage / latency / inventory risk** 一次性扣进 `net_ev`；
4. 只留下 **扣完成本仍为正** 的候选。

对当前 desk 来说，这比“看谁 funding 最高就去收租”更有价值，因为它把这条 alpha 最容易自欺的地方——**毛边很多，净边很少**——直接工程化了。

## 2. 核心结论
- **一句话核心结论：** 这条 raw alpha 的本体不是“funding spread 大”，而是 **funding spread 大到足以覆盖完整双腿成本栈**；如果过不了这道门，它就不是可执行 alpha，只是观察指标。
- **一句话它怎么证明：** repo 一边在 `PerpPerpDiffStrategy` 里给出 entry/exit/hold/sizing，另一边在 live screener 里用 `expected_profit()` 把净边算到美元级别，而我补的 live 快照显示：**当前 BTC / ETH 三所公开 funding spread 远远不够过线。**

### 2.1 repo 里最该记住的策略骨架
`config/main.yaml` 给的 `PerpPerpDiff` 默认参数相当直接：
- `assets = [BTC, ETH]`
- `venues = [binance, bybit]`
- `min_funding_spread = 0.0002`（即 **2 bps / 8h**）
- `zscore_lookback = 30`
- `entry_z = 2.0`
- `exit_z = 0.5`
- `max_hold_bars = 6`（8h bar 下即 **最多持有 48h**）
- `position_size_pct = 0.30`
- `max_open_positions = 2`

`strategies/perp_perp.py` 的逻辑也很干净：
- 同币对比两 venue funding；
- `spread = fr_hi - fr_lo`；
- 若 `abs(spread) < min_funding_spread` 或 `abs(z) < entry_z`，直接不做；
- 若满足阈值，则 **short 高 funding venue、long 低 funding venue**；
- 若已持仓且 `abs(z) < exit_z`，则平仓。

这说明它不是纯 headline carry，而是已经具备：
- `entry`
- `exit`
- `max hold`
- `position cap`
- `open position limit`

也就是完整 raw alpha 应有的最小结构。

### 2.2 repo 里最值钱的不是信号，而是净边核算
真正把这条线从“想法”拉到“可执行”的，是 `portfolio/profit_model.py`：

`net = funding_edge - trading_fees - slippage_cost - latency_cost - inventory_risk_cost`

其中：
- `funding_edge = notional * funding_diff`
- `trading_fees = notional * taker_fee_rate * 2`
- `slippage_cost = notional * (slippage_bps / 10000) * 2`
- `latency_cost = notional * (latency_bps / 10000)`
- `inventory_risk_cost = notional * (inventory_risk_bps / 10000)`

`scripts/run_live_screener.py` 的默认 live 假设是：
- `notional_usd = 50,000`
- `slippage_bps = 2.0`
- `latency_bps = 0.5`
- `inventory_risk_bps = 1.0`
- taker fee：Binance `4 bps`、Bybit `6 bps`、OKX `5 bps`

这组参数其实已经很诚实了：它不是拿“paper-thin maker fee”去装收益，而是默认你最容易先踩到的 taker / legging / latency 现实。

### 2.3 本地 live sanity check：当前三所公开 funding spread 还远远不够
我用 Binance / Bybit / OKX 的公开 funding 接口做了一个本地快照，artifact 在：

`reports/artifacts/quant_digests/20260330_perp_perp_funding_diff_netev/live_sanity_snapshot.json`

快照时间：`2026-03-30T19:20:55Z`

最重要的几个硬数字：
- **BTC 当前最优 raw spread** 是 `OKX - Binance = 0.6836 bps / 8h`；
  - 对 `50k USD` 名义本金，`funding_edge ≈ +3.42 USD`
  - 但扣完 repo 默认成本后，`net_ev ≈ -114.08 USD`
- **ETH 当前最优 raw spread** 是 `Bybit - Binance = 0.5923 bps / 8h`；
  - `funding_edge ≈ +2.96 USD`
  - 扣完成本后，`net_ev ≈ -124.54 USD`
- repo 默认成本假设下的 **breakeven funding spread** 大概是：
  - `Binance ↔ OKX`：**23.5 bps / 8h**
  - `Binance ↔ Bybit`：**25.5 bps / 8h**
  - `Bybit ↔ OKX`：**27.5 bps / 8h**

换句话说，当前 live snapshot 给的不是“这条线没用”，而是一个更重要的 first verdict：

**这条 alpha 不能拿日常小 funding diff always-on 跑；它只适合做极端 funding dislocation 的事件型 pocket，或者必须叠加更强的 maker/queue/execution edge。**

### 2.4 这次最值得 desk 记住的交易结论
如果这条线要进当前素材池，正确写法不该是：
- “perp-perp funding diff 存在，所以可以套利”

而该是：
- “**same-underlier perp-perp funding differential** 是一条可独立复现的 raw alpha 候选；但它只有在 **spread 过 z-score 门、过净边门、过 quote/depth 门** 时才值得开机，平时大多数时段都应视作 `NO_TRADE`。”

这点和前两天已经 intake 的 spot-perp carry / richest-venue routing 也不同：
- 那两条更像 **去哪条腿收 cashflow**；
- 这条更像 **同一 underlier 的跨 venue funding mispricing 是否大到足以覆盖双腿现实摩擦**。

## 3. 为什么和当前项目有关
这条线和当前 desk 直接相关，因为它满足这轮优先级里比较靠前的那类：
**可独立复现、可直接落地为完整策略、并且明确属于 carry / relative-value / stat-arb 家族的 raw alpha。**

它和 `1m / 3m / 5m / 15m` 的关系也很清楚：
- 慢变量是 funding clock（通常 8h）
- 快变量是 **什么时候进、在哪个 venue 进、两腿价差有没有爆、top-of-book depth 能不能吃下、单腿滑点会不会把 funding edge 吃光**

也就是说：
**alpha 兑现靠 funding，alpha 存活靠短周期执行。**

## 3.5 策略拆解（必填）
- 方向属性：carry / relative-value / cross-venue market-neutral
- 基础 alpha：`funding_high_venue - funding_low_venue - fees - slippage - latency - inventory_risk`
- regime：只在 funding differential 异常放大、并且同币跨 venue 价差仍紧、深度仍足够时启动；平常绝大多数 funding spread 不应视为可交易
- filter / veto：
  - `abs(funding_spread) >= 2 bps / 8h`
  - `abs(zscore) >= 2.0`
  - `net_ev > 0`（desk 版必须强制加）
  - `cross-venue mid spread / top-of-book depth / settlement alignment` 任一异常直接 veto
- risk / sizing / execution overlay：
  - 单策略仓位 `30% capital` 起步
  - 最多 `2` 个同时 open pair
  - `max_hold = 6 × 8h = 48h`
  - `abs(z) < 0.5` 平仓
  - `orphan_protection.max_unhedged_bars = 1`
  - `max_leg_divergence_bps = 35`
  - 先以 taker-only 假设跑 first verdict，再讨论 maker 化

## 4. 可复刻的最小实验
### 4.1 研究假设
比起 always-on 地在每个 funding 周期都上，**只做 `net-EV hurdle` 之上的 perp-perp funding differential**，更像一条真实可活的 short-cycle carry alpha。

### 4.2 数据源、公开性、更新频率
- **Funding 数据**：
  - Binance `GET /fapi/v1/premiumIndex` / `GET /fapi/v1/fundingRate`
  - Bybit `GET /v5/market/funding/history`
  - OKX `GET /api/v5/public/funding-rate` / `funding-rate-history`
- **行情/执行数据**：三所公开 kline / ticker / order-book 顶档
- **公开性**：全都可公开抓；最小实验不需要私钥
- **更新频率**：funding 以 8h 为主，quote/depth 可以秒级采集，再聚合到 `1m / 3m / 5m / 15m`

### 4.3 最小实验口径（建议先做这个）
1. 标的先只做 `BTC / ETH / SOL`，venue 先做 `Binance / Bybit / OKX`。
2. 每分钟记录：
   - `funding_diff_{pair,t}`
   - `funding_diff_z_{pair,t}`
   - `cross_venue_mid_spread_{pair,t}`
   - `top_of_book_depth_{pair,t}`
   - `net_ev_{pair,t}`
3. 生成两套版本：
   - A：`spread-only`（只要 funding diff 为正就做 richest-vs-cheapest）
   - B：`net-hurdle`（`z >= 2`、`net_ev > 0`、`mid_spread <= x bps`、`depth >= y × notional` 才开）
4. 入场先用最保守的短周期映射：
   - 在下一次 funding 结算前 `5m / 15m` 窗口择最紧 mid spread 入场；
   - 持有到下一 funding 兑现窗，或 `z < 0.5` 提前出场；
   - 若腿间 mid spread 爆到阈值外则强平。
5. first-verdict 只看四个指标：
   - `net funding captured`
   - `mark-to-market leg drift`
   - `slippage + fee drag`
   - `trade admission ratio`（多少 funding 窗口 actually 过线）

### 4.4 当前 desk 更该先测哪一刀
不是先卷更复杂预测器，而是先问一句：

**在真实 taker 成本下，历史上到底有多少个 8h funding 窗口，真的能让 same-underlier perp-perp diff 过净边门？**

如果这个比例本身极低，这条线就该被降级成：
- 事件 pocket
- 极端拥挤时的 opportunistic carry
- 或者 maker/queue 优化的二阶段项目

而不是继续伪装成 always-on 收租机。

## 5. 下一步怎么测
1. **先补“过线率”统计**：按 `BTC / ETH / SOL × 3 venue pairs` 回放近 12 个月，统计 `net_ev > 0` 的 funding window 占比，而不是先看 headline spread。
2. **把执行口径分层**：至少拆 `taker-taker / maker-taker / maker-maker` 三档；如果只有 maker-maker 才勉强转正，就要诚实把它降级成 execution-heavy 项目，而不是信号项目。
3. **把 entry 时点前移/后移做成网格**：`-15m / -5m / +0m / +5m` relative to funding settlement，检验赚的是 funding 还是腿间 mark drift。
4. **加一个 quote-stability veto**：只有当腿间 mid spread、深度、盘口更新频率都稳定时才放行，避免把 funding edge 死在 legging risk 上。

## 6. 来源
1. **gencersarp. (2026). _cryptoarb_. GitHub repository.**
   - Author: gencersarp
   - Year: 2026（2026-03 持续更新）
   - Title: *cryptoarb*
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/gencersarp/cryptoarb
   - Repo URL: https://github.com/gencersarp/cryptoarb

2. **Binance USDⓈ-M Futures API. _Premium Index / Funding Rate_**
   - Venue: Binance API Docs
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price
   - Funding history URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History

3. **Bybit V5 API. _Get Funding Rate History_**
   - Venue: Bybit API Docs
   - Readable URL: https://bybit-exchange.github.io/docs/v5/market/history-fund-rate

4. **OKX API v5. _Get funding rate / funding rate history_**
   - Venue: OKX API Docs
   - Readable URL: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate
   - Funding history URL: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate-history

5. **本地 live artifact（本次快照）**
   - Path: `reports/artifacts/quant_digests/20260330_perp_perp_funding_diff_netev/live_sanity_snapshot.json`
   - Captured at: `2026-03-30T19:20:55Z`
