# 别把低频外部数据硬装成 15m 主信号：`Polymarket implied-probability breadth` 更像三条收口线共用的 event-risk overlay
- 时间：2026-03-21 02:21 UTC
- 类型：GitHub 仓库 + 外部公开数据（官方 API）
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/polymarket/implied-probability/breadth/event-risk/filter/position-sizing/crypto/5m/15m
- 证据类型：工程经验 + 外部公开数据快检（待最小回测）

## 1. 这次看了什么
看了 Polymarket 官方 `py-clob-client` 仓库与官方 API 文档，重点不是做 prediction-market alpha，而是把“事件概率横截面变化”抽成 15m Crypto 的 **risk overlay / veto 层**。

## 2. 核心结论
- **一句话核心结论**：`Polymarket 概率广度冲击` 更适合做 15m 的“别乱追”开关，而不是逐根 K 的入场信号。
- **一句话证明方式**：基于官方公开接口对 `macro` 标签市场做快检，观察到可交易子集里“概率跳变 + 点差成本”并存，说明它更像环境风险信息而非单笔触发器。
- 快检样本（2026-03-21 UTC 截面）：`tag_id=102000` 下 active 事件 39 个、Yes 市场 262 个；按 `v24>=100, spread<=0.05, 0.02<=price<=0.98` 过滤后仍有 42 个可用市场。
- 在这 42 个市场中：中位 spread 约 `0.020`，中位 `|1d 概率变动|` 约 `0.005`；约 `30%` 市场出现 `|1d 变动|>=1%`，说明“事件概率扰动”不是罕见噪声。
- 对三条收口线的含义：当 external event-risk 抬升时，**breakout-short follow-up 更容易假延续**，**Fib retest_hold 更需要额外确认**，**EMA/PSAR raw alpha 更该降杠杆而不是加触发条件复杂度**。

## 3. 为什么和当前项目有关
- 这条不是新主信号，而是三条线都能复用的 **shared overlay**：
  - `V3 breakout-short follow-up`：先拦“事件冲击期追空/追突破”。
  - `Fib confirmation / retest_hold`：冲击期提高确认门槛，减少一脚踏空。
  - `EMA / PSAR raw alpha`：保留原始触发，但用外部风险分层做仓位折扣与 veto。
- 相比继续堆内部微调，这条线的价值在于：**用公开、可抓、可解释的数据，给三条线统一加一层“何时少做”机制**。

## 4. 可复刻的最小实验
- 研究假设：`Polymarket implied-probability breadth shock` 上升时，BTC/ETH 15m 的 follow-through 下降、假突破率上升；此时 overlay 能改善回撤/成本后表现。
- 数据源（公开性/频率）：
  - 市场列表：`https://gamma-api.polymarket.com/events`（公开，无需鉴权，分页）
  - 盘口与价格：`https://clob.polymarket.com/*` 公共 market-data 接口（公开）
  - 历史价格：`/prices-history`（支持 `1m/1h/6h/1d/1w` + `fidelity`）
- 可计算定义（先做版本 v0）：
  1) 每小时拉取 macro 事件下市场，保留 `v24>=100, spread<=0.05, 0.02<=p<=0.98` 的 Yes 合约；
  2) 计算 `shock_i=|Δp_i(1h)|`；
  3) 定义 `BreadthShock_t = median_i(shock_i / max(spread_i, 0.005))`；
  4) 对 `BreadthShock_t` 做滚动分位（如 14 天），映射到 `low/mid/high risk`。
- 接入 15m 策略（先测一个最小口径）：
  - baseline：现有三线任一策略；
  - overlay：`high risk` 时仓位 ×0.4 且禁止 breakout chase；`mid risk` 仓位 ×0.7 且确认 bars +1；`low risk` 不改；
  - 先看 2 个指标：`cost后 Sharpe / Calmar` 与 `false-break rate`。

## 5. 风险与保留意见
- Polymarket 事件覆盖偏宏观与政治，不是专为 crypto 设计，存在映射误差。
- 不同市场流动性差异大，若不做 spread/volume 过滤，breadth 指标会被“假活跃”污染。
- 这是低频外部数据，**必须定位为 regime/filter/sizing overlay**，不应伪装成逐根 15m 主信号。
- 当前结论来自公开数据快检与工程可行性，不是正式 OOS 结论；必须进入最小回测后再升级优先级。

## 6. 来源
- Polymarket. (2025-2026). **py-clob-client (Python CLOB Client)**. GitHub Repository.  
  - Repo URL: `https://github.com/Polymarket/py-clob-client`
- Polymarket Docs. (2025-2026). **Fetching Markets** / **Get prices history** / **Public market-data methods**. Official API Documentation.  
  - Readable URL: `https://docs.polymarket.com/market-data/fetching-markets`  
  - Readable URL: `https://docs.polymarket.com/api-reference/markets/get-prices-history.md`  
  - Readable URL: `https://docs.polymarket.com/trading/clients/public`
- Polymarket Public API endpoints (sample):  
  - `https://gamma-api.polymarket.com/events?tag_id=102000&active=true&closed=false&limit=20`  
  - `https://clob.polymarket.com/prices-history?market=<token_id>&interval=1h`