# 别把 crypto options 只当慢频长波动：JFM 2024 + 2025 新仓库更该先测的是「近到期 OKX-Deribit 同 strike call premium 收敛」raw alpha

- 主题类型：raw alpha
- 基础 alpha：同一 BTC 到期日 / 同一 strike call 在 OKX 与 Deribit 之间的 premium spread 收敛（short rich venue / long cheap venue）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/options/cross-exchange/near-expiry/premium-convergence/settlement-window/okx/deribit/btc/1m/3m/5m/15m/repo/paper/external-data

这轮我不再把 crypto derivatives 文献继续读成“市场效率讨论”或“options 只是波动率工具”。先把 **base alpha** 说清楚：**做的是同一张合约的跨 venue 相对定价，而不是猜 BTC 方向**。更具体说，先盯 **近到期 BTC call**，在 OKX 和 Deribit 上做同 expiry / same strike 的 premium spread，赌它往一价收敛。

这条线比继续写一个泛 `filter / confirmation` 更值得进池，原因很直接：
1. 它本身就是 **完整 raw alpha**，不是给别的 alpha 打下手；
2. 数据是 **公开 API 可拿**，30 秒到 1 分钟就能开始最小实验；
3. 它补的是当前 desk 相对少的 **crypto options / derivatives relative-value** 素材，而不是再在 breakout/retest 上内循环。

## 1) 这次真正值得 desk 化的，不是“crypto options 有无效率”，而是「短到期 × 跨 venue × 同合约价差」

我这次主要拼了两份材料：

- **Alexander, Chen, Deng, Wang (2024, Journal of Financial Markets)**：*Arbitrage opportunities and efficiency tests in crypto derivatives*。
  这篇论文不是给你一个“方向因子”，但它给了很关键的 desk 结论：**bitcoin / ether 的 options + perpetual 市场虽然整体在变有效，尤其 `>=15d` maturity 更有效，但短周期无效率 pocket 仍会在高交易量或链拥堵时冒出来，而且保守成本下仍可能盈利。**
- **cbyhre (2025) GitHub repo**：`OKX-Deribit-Arbitrage`。
  这份小仓库虽然很轻，但它把一个更适合我们 desk 的旁支直接钉住了：**近到期 BTC call 在 Deribit 和 OKX 上，因为 settlement window / price discovery / 流动性同步并不完全一致，会出现同 strike premium divergence。**

这两份东西拼起来以后，最值得先 intake 的不是“期权市场有时候不有效”这种泛结论，而是这条非常具体的 raw alpha：

> **只做短到期（优先 `DTE<=7d`，尤其 `0~3d`）、同 expiry / same strike / same option type 的 cross-exchange premium spread convergence。**

它和我们现在做的 `pairs / carry / basis / cross-sectional rv` 是同一家族，只不过标的是 **option premium**，不是 perp basis 或 spot-perp spread。

## 2) 对短周期 desk 最有价值的读法

这条线能直接映射到 `1m / 3m / 5m / 15m`：

- **交易对象**：BTC 近到期 call（后续可扩 put，但先从 call 开始）
- **信号频率**：repo 默认 30 秒抓一次，天然可以聚合成 `1m/3m/5m`
- **alpha 事件**：同合约在两家交易所的 premium 相对失衡
- **退出机制**：spread 回归 / 时间止损 / 逼近结算窗口强平
- **风险形态**：不是方向风险为主，而是 **跨 venue / gamma / 流动性 / 结算机制** 风险为主

这里一个很重要的 desk 化判断是：

**别把它当 always-on 扫描器。**
更诚实的读法应该是：

- `short-dated` 比 `15d+` 更有机会；
- `高成交 / 微结构失衡 / 逼近结算` 时 pocket 更可能出现；
- 平时多数价差可能只是 **bid-ask 宽、深度薄、看起来有 edge 但吃不穿成本**。

也就是说，这条 alpha 的正确位置更像：

> **event-driven relative-value raw alpha**，不是全天候稳定 carry。

## 3) 当前最小快检：公开 API snapshot 先告诉我们，它现在不是常开边

我直接用 **Deribit / OKX 公共 API** 做了一个最小 snapshot，抓取：

- `DTE <= 7d`
- `|moneyness| <= 15%`
- BTC calls
- Deribit 与 OKX 的共同合约（same expiry, same strike）
- 用各自 quote mid × BTC index 转成 USD premium，再比较 premium diff 与双边 top-of-book spread cost

快检 artifact：
- `reports/artifacts/quant_digests/okx_deribit_near_expiry_call_arb_20260326/near_expiry_common_calls_snapshot.csv`
- `reports/artifacts/quant_digests/okx_deribit_near_expiry_call_arb_20260326/snapshot_summary.csv`

本次 snapshot（`2026-03-26 06:56 UTC`）的几个关键数：

1. **45 个**近 7 天共同 call 合约里，**0 个** 在 top-of-book 口径下 `|premium diff| > roundtrip spread`，也就是 **当前没有一笔一眼能过成本**。
2. 全样本 **median |premium diff| ≈ 2.31%**，但 **median roundtrip spread ≈ 15.19%**；说明很多“价差”其实只是 options 自己太宽。
3. 即便压到更像样的液态子集（`spread<=20%`），**median |diff| 仍只有 ≈ 1.15%**，而 **median spread ≈ 11.65%**。
4. 当前最接近可交易的 next-day / ATM-ish pocket 是：**2026-03-27 72k call，premium diff ≈ -8.69%，roundtrip spread ≈ 10.43%，还差约 1.75pct 才过 top-of-book 成本。**

这组结果对 desk 其实很有用，因为它很明确地把这条线从“想象中的常开套利”压回了更诚实的位置：

> **有研究价值，但目前更像 `watchlist alpha` / `event pocket alpha`，不是今天就能无脑开跑的生产 alpha。**

## 4) 这条 raw alpha 的最小完整策略骨架

### Entry
只在以下条件同时满足时开仓：

1. 共同合约：same expiry / same strike / same call；
2. `DTE <= 7d`，优先 `0~3d`；
3. `|moneyness| <= 5%`，先聚焦 ATM / slightly OTM，避免远虚值假 edge；
4. `|premium_diff_pct| > entry_threshold`，其中：
   - `entry_threshold = fees + 双腿 bid-ask + quote stale buffer + venue risk buffer`
   - 真实实现里建议再叠 `rolling z-score` 或 `rolling percentile`
5. 两腿都有真实 bid/ask，且 size 不低于最小下单量；
6. 若接近结算，只有在 `spread / cost` 仍明显大于 1 时才允许入场。

### Position
- **short rich venue call / long cheap venue call**
- 先做 **1:1 contract matching**，不在第一版里叠更复杂的 delta/gamma rebalance
- 单笔 notional 上限由 **较浅那一侧 top-of-book size** 决定

### Exit
任一满足就平：

1. spread 回到 `close_threshold`（例如回归到 entry 的 30~50%）；
2. 到达时间止损（例如 `30m / 60m / 120m`）；
3. 距离结算只剩最后 `T-30m` 或更短，但 spread 未继续收敛；
4. 一侧 quote 消失 / 明显 stale / 盘口突然变空。

### Sizing
- 初版别做“想象中的大容量”。
- 用 **min(venue A ask size, venue B bid size)** 的折扣版本做上限；
- 同一 expiry bucket 总敞口设 cap，防止临近到期 gamma 一起爆。

### Risk
这条线最重要的风险不是 BTC 方向，而是：

- **盘口深度薄 / quote stale**
- **结算规则与窗口差异**（repo 指出 Deribit 与 OKX 的 settlement TWAP window 不同；正式上线前必须再用官方规则页逐条复核）
- **跨 venue 资金占用 / counterparty risk**
- **近到期 gamma / vega 跳变**
- **极端波动时一腿可成交、一腿滑走**

### Cost
必须显式进模型：

- 两腿 taker/maker fee
- 两腿 bid-ask spread
- 盘口吃单冲击
- 跨 venue 资金占用成本
- 结算前强平/roll 的额外摩擦

## 5) 我的 hard verdict

这条线我会给：**`keep in raw-alpha pool, but only as event-driven near-expiry arb pocket`**。

不是因为论文/仓库不有趣，而是因为当前公开 quote 快检已经很清楚：

- **edge 不是没有；**
- 但 **大多数时刻先被 option spread 吃掉**；
- 所以它的正确落点不是“全天候 production alpha”，而是：
  - 一条值得继续采样的 **raw alpha 候选**；
  - 重点观察 **结算前、成交放大、链拥堵、短到期** 这些 pocket；
  - 若这些 pocket 也始终过不了成本，就要快速降级，不要硬留。

## 6) 下一步怎么测

按 desk 当前预算，我建议只做这 4 步，不扩 scope：

1. **做 7~14 天 30 秒 snapshot sidecar**
   - 标的：BTC 共同近到期 calls
   - 记录：mid、bid/ask、index、depth、DTE、moneyness、premium diff、spread cost
   - 先回答：`真正过 top-of-book cost 的 pocket 占比有多少？`

2. **只测 3 个 pocket 维度**
   - `DTE bucket`: `0~1d / 1~3d / 3~7d`
   - `moneyness bucket`: `ATM / ±5% / ±10%`
   - `liquidity bucket`: `combined spread <= 8% / 12% / 20%`

3. **把“结算事件 pocket”单独拉出来**
   - 重点看 `T-180m ~ T-30m`
   - 回答：repo 所说的 settlement-window mismatch，到底有没有在这个时间窗里变成可交易 edge

4. **设置明确 kill rule**
   - 若连续 2 周样本里：
     - `crosses_cost_rate` 很低，且
     - 所有 pocket 的 `edge_minus_spread` 仍系统性为负，
   - 就把它从前排 raw-alpha 候选降到 `watchlist / derivatives niche backlog`，不要继续烧时间。

## Sources

1. **Alexander, C., Chen, X., Deng, J., & Wang, T. (2024). _Arbitrage opportunities and efficiency tests in crypto derivatives_. Journal of Financial Markets.**
   - Venue: *Journal of Financial Markets*
   - DOI: `10.1016/j.finmar.2024.100930`
   - Readable URL: `https://doi.org/10.1016/j.finmar.2024.100930`

2. **Alexander, C., Chen, X., Deng, J., & Wang, T. (2023). _Arbitrage Opportunities and Efficiency Tests in Crypto Options_. SSRN Electronic Journal.**
   - Venue: *SSRN Electronic Journal*
   - DOI: `10.2139/ssrn.4495548`
   - Readable URL: `https://doi.org/10.2139/ssrn.4495548`

3. **cbyhre. (2025). _OKX-Deribit-Arbitrage_. GitHub repository.**
   - Repo URL: `https://github.com/cbyhre/OKX-Deribit-Arbitrage`
   - Readable README: `https://raw.githubusercontent.com/cbyhre/OKX-Deribit-Arbitrage/main/README.md`
   - GitHub metadata: created `2025-08-03`, updated `2025-12-31`

4. **Public market data endpoints used for the minimal experiment**
   - Deribit public instruments/order book API: `https://www.deribit.com/api/v2/public/get_instruments` and `https://www.deribit.com/api/v2/public/get_order_book`
   - OKX public instruments/ticker/index API: `https://www.okx.com/api/v5/public/instruments`, `https://www.okx.com/api/v5/market/ticker`, `https://www.okx.com/api/v5/market/index-tickers`
