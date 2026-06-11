# 别把 funding 极端固定写成“只反转”或“只延续”：同一 z-score 在 15m 上应先做 mode switch（trend=momentum，range=mean-reversion）
- 时间：2026-03-23 02:45 UTC
- 类型：GitHub 仓库 + 官方 API 文档
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/funding-rate/zscore/mode-switch/regime-gate/filter/position-sizing/open-interest/crypto/5m/15m
- 证据类型：仓库 README + 源码（signals/backtest/config）+ Bybit 官方文档

## 1) 这次看了什么
这轮优先做三条收口线可直接用的外部数据旁支，不再重复“funding 只当单向反指针”。

我看的是一个 2026 的新仓库：**farrellh1 / crypto-funding-rate-strategy**。它最值钱的点不是“又一个 funding 阈值”，而是把同一套 funding z-score 明确拆成两种互斥解释：
- `mean_reversion`（极端 funding → 反向）
- `momentum`（极端 funding → 同向延续）

也就是：**同一个 funding 极端，在不同 regime 下方向含义可能相反**。

## 2) 核心结论（先说人话）
- **一句话结论：** 对我们 5m/15m desk，funding 不该是固定方向信号，而应先做 `mode switch`：
  - `trend` 环境按 **momentum** 解释；
  - `range/chop` 环境按 **mean-reversion** 解释。  
- **对应三条收口线的意义：** 这不是替代主触发，而是给 `breakout-short / Fib retest / EMA-PSAR` 的 shared veto 与仓位层提供“方向语义翻译器”。

### 关键数据点（来自仓库实现）
1. 默认参数：`lookback_periods=168`（按 8h funding 计约 **56 天**）、`threshold=2.5`。
2. 同一 z-score 的两种模式（源码 `signals/zscore.py`）：
   - `mean_reversion`: `z>=thr -> SHORT`, `z<=-thr -> LONG`
   - `momentum`: `z>=thr -> LONG`, `z<=-thr -> SHORT`
3. 过滤层（`signals/filters.py` + `config.yaml`）：
   - `volume_filter.min_zscore=0.5`
   - `oi_filter.max_zscore=2.0`
4. 成本口径（`config.yaml`）：
   - taker `0.055%`，maker `0.02%`（Bybit Non-VIP），可并入 slippage。

> 这比“funding 高就永远做空、低就永远做多”更接近实盘，因为它承认了 funding 解释的 **regime 依赖性**。

## 3) 为什么它比继续死磕单线参数更值得
它**直接服务三条收口线**，不是旁逸斜出：
- `V3 breakout-short follow-up`：能先判断“当前 funding 极端到底在提示延续还是挤仓反转”，避免把高拥挤误读成必然 continuation；
- `Fibonacci retest_hold`：在 trend 模式里更敢持有顺势回踩，在 range 模式里对“过热回踩”更保守；
- `EMA / PSAR raw alpha focus`：把低频 crowding 信息定位为 **filter / sizing overlay**，而不是伪装成逐根 15m 主信号。

## 3.5) 策略拆解（必填）
- 方向属性：**regime-conditional**（同一特征可反向解释）
- 基础 alpha：沿用当前 desk 主触发（breakout/fib/ema-psar 任一）
- regime：`trend` vs `range`（建议先用 1h EMA slope + ADX）
- filter / veto：funding z-score 方向解释 + volume/OI zscore 约束
- risk / sizing overlay：在“解释与主触发同向”时放大仓位，反向时降杠杆或 veto

## 4) 外部数据口径（公开性 / 频率 / 可复现）
### 数据源与公开性
- **Funding Rate**：Bybit V5 `GET /v5/market/funding/history`（公开可得，REST）
- **Open Interest**：Bybit V5 `GET /v5/market/open-interest`（公开可得，REST）
- **Kline/Volume**：Bybit V5 `GET /v5/market/kline`（公开可得，REST）

### 更新频率与映射方式
- funding 天然是低频（常见 8h 结算节奏），**不应当作逐根 15m 主触发**；
- 在 15m 上的正确角色：`regime gate / filter / position sizing`；
- 具体映射：每次 funding 更新后重算 `z_funding`，在下一个 funding 时点前对 15m 信号使用“冻结值”。

## 5) 最小可复现实验（直接可开工）
### 研究假设
`H1`: funding 极端的方向语义取决于 regime；若不做 mode switch，会显著增加错向交易。

### 最小实验定义（15m 执行）
- 标的：`BTCUSDT / ETHUSDT`
- 执行框架：15m（主触发沿用当前线）
- 外部层更新：8h（funding/OI），15m（volume）
- 特征：
  - `z_funding(lookback=168, thr=2.5)`
  - `z_volume(lookback=168, min=0.5)`（可先简化成 15m volume z）
  - `z_oi(lookback=168, max=2.0)`
- mode switch：
  - `trend regime`：funding 用 momentum 解释
  - `range regime`：funding 用 mean-reversion 解释

### 对照组
- `A`：现有 baseline（无 funding 模式切换）
- `B`：baseline + funding 固定反转解释
- `C`：baseline + funding 固定延续解释
- `D`：baseline + funding mode switch（推荐）

### 下一步先看哪两个指标
1. `post-cost expectancy`（先按 taker 0.055% 双边近似）
2. `false-follow-up rate`（breakout/retest 后 N 根内反向触发止损比例）

> 若 `D` 在不显著增交易频次的前提下改善 expectancy 或降低 false-follow-up rate，就说明 funding 更适合作为“模式翻译器”，而不是单向神谕。

## 6) 风险与保留意见
- 该 repo 为新项目（公开社区验证有限），结果稳定性需独立复核；
- README 的“Results”部分尚未给出完整最终绩效表，当前更像研究框架而非已验证 alpha；
- 8h funding 映射到 15m 容易产生“信号稀疏 + 持续覆盖过长”问题，需配合失效计时器；
- mode switch 若直接由同一价格特征定义，存在同源信息重复计入风险。

## 7) 来源
1. **farrellh1. (2026). _crypto-funding-rate-strategy_. GitHub Repository.**
   - Authors / Org: farrellh1
   - Year: 2026（repo `created_at = 2026-01-25`）
   - Title: Crypto Funding Rate Strategy
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/farrellh1/crypto-funding-rate-strategy>
   - Repo URL: <https://github.com/farrellh1/crypto-funding-rate-strategy>

2. **farrellh1. (2026). _signals/zscore.py, signals/filters.py, config.yaml_.**
   - Authors / Org: farrellh1
   - Year: 2026
   - Title: Z-score signal modes + volume/OI zscore filters + cost config
   - Venue: GitHub source files
   - DOI: N/A
   - Readable URL: <https://github.com/farrellh1/crypto-funding-rate-strategy/tree/main/signals>
   - Repo URL:
     - <https://raw.githubusercontent.com/farrellh1/crypto-funding-rate-strategy/main/signals/zscore.py>
     - <https://raw.githubusercontent.com/farrellh1/crypto-funding-rate-strategy/main/signals/filters.py>
     - <https://raw.githubusercontent.com/farrellh1/crypto-funding-rate-strategy/main/config.yaml>

3. **Bybit API Documentation. (2026 access). _V5 Market Endpoints_.**
   - Authors / Org: Bybit
   - Year: 2026 (accessed)
   - Title: Get Funding Rate History / Get Open Interest / Get Kline
   - Venue: Official API Docs
   - DOI: N/A
   - Readable URL:
     - <https://bybit-exchange.github.io/docs/v5/market/history-fund-rate>
     - <https://bybit-exchange.github.io/docs/v5/market/open-interest>
     - <https://bybit-exchange.github.io/docs/v5/market/kline>
   - Repo URL: N/A

## 8) 产出文件（本轮）
- `research/quant_digests/2026-03-23_0245_funding-zscore-mode-switch-gate.md`
