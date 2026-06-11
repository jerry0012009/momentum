# 负 funding 结算边界短打：most-negative funding coin 的 1m/3m continuation short
- 时间：2026-04-12 07:14 UTC
- 类型：GitHub repo / 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：`8h funding 结算边界 × most-negative funding coin 的超短续跌`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：funding / carry / event-driven / positioning / crowding / short-horizon / 1m / 3m / 5m / 15m
- 证据类型：工程实现 + 公共数据 portability probe

## 1. 这次看了什么
看的是 GitHub 仓库 **wangshaofu (2026), _Binance Futures Latency Analyser_**。它表面上是在测 Binance USDⓈ-M funding 结算点附近的 WebSocket 延迟，但源码里真正值得 desk 拿出来单独验证的，不是“延迟本身”，而是它默认盯住 **当下 funding 最负的合约**，并把结算边界当成一个可交易事件点。对我们更有价值的 desk 化读法是：**把“most-negative funding at settlement”当成 crowding 信号，先问结算后 1m/3m/5m/15m 是继续跌，还是会反打。**

## 2. 核心结论
- **一句话核心结论：** 在 Binance 公开数据里，`most-negative funding coin` 在 funding 结算后的超短窗口更像**续跌 short**，不是立刻均值回归，尤其当前 15 分钟本来就在走弱时更明显。
- **一句话证明方式：** 我把 repo 的“盯最负 funding + 盯结算边界”思路，映射到 Binance `fundingRate + 1m klines` 做事件研究，直接看结算后收益，而不是只看延迟曲线。
- 用 `BTC/ETH/SOL/XRP/DOGE/BNB/ADA/SUI/1000PEPE/LTC/LINK/TRX/AVAX/WIF/AAVE` 这 15 个 liquid-ish USDⓈ-M 合约，取 `2025-10-01 ~ 2026-04-12`，每个 funding 时间戳只选 **funding 最负** 的那一个；若该 funding `<= -4 bps / 8h`，共有 **33** 个事件。
- 事件上，若在**结算分钟收盘**做空并退出：`+1m` 平均约 **+6.76 bps**、胜率 **69.7%**；`+3m` 平均约 **+6.12 bps**、胜率 **66.7%**；拉到 `+5m/+15m` 均值明显变差，说明更像**边界后 1~3 分钟的短打**，不是拿很久。
- 再加一个非常朴素的 filter：**结算前 15m 已经下跌**（`pre15_ret < 0`）。样本缩到 **17** 个事件后，`+3m` 做空平均约 **+11.21 bps**、中位数 **+10.90 bps**、胜率 **64.7%**；按 **8 bps round-trip** 粗扣，仍约 **+3.21 bps/笔**。
- 但它不是“全市场普适 alpha”。这 33 个事件几乎都集中在 **WIF / TRX / 1000PEPE / AVAX / SOL**，更像**高 beta / 拥挤 alt crowding pocket**，不是 BTC/ETH 级别主流币通用规律。

## 3. 为什么和当前项目有关
这条线和我们最近持续补的 `funding / basis / positioning` raw alpha 是一条很自然的延伸，但它更短、更 event-driven，也更直接贴 `1m / 3m / 5m`。重点不是把 funding 当成低频 carry，而是把 **funding 结算边界** 当成一个会把拥挤仓位“挤出来”的瞬时事件。对 short-cycle desk 来说，这比“高 funding 就一直拿”更像能快速做 first verdict 的素材。

## 3.5 策略拆解（必填）
- 方向属性：逆势中的事件驱动续跌 / crowding unwind
- 基础 alpha：`结算时 funding 最负的合约，在结算后 1~3m 更容易继续向下`
- regime：高拥挤、高 beta alt、funding 绝对值偏大时更明显
- filter / veto：`min funding <= -4bps/8h`；`pre15_ret < 0`；只做流动性足够的 alt perp；BTC/ETH 默认不纳入主书
- risk / sizing / execution overlay：事件单笔小仓；只拿 `1~3m`；若结算后第一分钟没继续走弱就撤；优先 maker / rebate / 低费通道，否则 edge 很容易被 taker 成本吃掉

## 4. 可复刻的最小实验
- 研究假设：在同一 funding 时间戳里，**最负 funding = 最拥挤空头仓位**，结算后短时间内仍可能因仓位与流动性挤压继续下行。
- 可计算定义：
  1. 每个 8h funding 边界，取候选池里 funding rate 最低的合约；
  2. 要求 `funding <= -0.0004`；
  3. 若 `pre15_ret < 0`，在**结算分钟收盘**做空；
  4. 固定在 `+1m / +3m / +5m` 退出，先比 gross，再跑 `4/6/8/10 bps` friction ladder。
- 最小回测切口：先只测 `WIF / TRX / 1000PEPE / AVAX / SOL`，周期先上 `1m`，再聚合到 `3m/5m`；不要一上来扩全市场。
- 最该先看：`+3m` 的 post-cost mean bps、胜率，以及事件是否被少数极端日驱动。
- 本轮产物：
  - `reports/artifacts/literature/negative_funding_boundary_probe_2026-04-12_summary.csv`
  - `reports/artifacts/literature/negative_funding_boundary_probe_2026-04-12_detail.csv`
  - `reports/artifacts/literature/negative_funding_boundary_probe_2026-04-12_costladder.csv`

## 5. 风险与保留意见
- 这条线**高度依赖执行**。repo 本身就在强调结算边界的延迟与可成交价，所以用 `1m close` 只能算粗 proxy，不能替代真实 book-ticker / aggTrade 级回放。
- 样本不大，而且明显集中在 meme / high-beta alt；如果直接扩到 majors，edge 很可能消失。
- `+5m/+15m` 的均值明显变差，说明这不是“越拿越赚”的 carry/趋势，而更像**结算后的几分钟微结构冲击**。
- 如果只能 taker 双边 8~10 bps，很多变体会被吃掉；所以这条线天然需要 fee tier、maker、或更细粒度入场优化。

## 6. 来源
- wangshaofu. (2026). *Binance Futures Latency Analyser / LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps*. GitHub.
  - Repo URL: `https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps`
  - Readable files:
    - `README.md`
    - `streams.py`
    - `analyze_latency.py`
    - `short_order.py`
- Binance USDⓈ-M Futures public endpoints:
  - Funding Rate History: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`
  - Kline/Candlestick Data: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
