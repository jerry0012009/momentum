# spot / futures 价差冲击 × perp follow-through directional shell
- 时间：2026-04-10 17:29 UTC
- 类型：论文 + 公共数据 portability probe
- 主题类型：raw alpha
- 基础 alpha：**当 perp 这根 `5m` bar 明显跑赢 spot，且主动买/卖盘同向确认时，接下来约 `1h` 的 perp 更容易顺着 futures-led 方向继续走。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（首版 time-stop 壳已足够）
- 主题标签：raw alpha / cross-market / lead-lag / spot-futures / perpetuals / continuation / BTC / ETH / 5m / 15m
- 证据类型：论文证据（article-page snippets + DOI metadata）+ public-data portability probe

## 1. 这次看了什么
Robertson, Kevin & Zhang, Rene (2025) 的 *Price discovery in bitcoin spot and futures markets*（*Journal of International Money and Finance*）。论文主结论不是“市场更有效了”这种空话，而是：**比特币 futures 在多数时期更像信息先到的那条腿，且高波动、大额交易时这种价格发现角色更明显。**

## 2. 核心结论
- 对 desk 最值钱的读法，不是硬做同标的双腿 spread arb，而是把它改写成 **directional continuation admission**：`perp return - spot return` 同向扩张时，优先跟随 perp。
- 我用 Binance 公共 `spot + USDⓈ-M perp` `5m`、近约 `60d` 做快检：`BTCUSDT` 若只做“perp 跑赢 spot > 2bps 且 perp 当根上涨” 的裸 long，约 `113` 笔、每笔 gross 仅 `+4.23bps`，粗扣 `8bps` 后变 `-3.77bps`；加上 `taker_share > 0.56` 与 `|ret_perp| > 3bps` 后只剩 `40` 笔，但提升到 `+21.90bps gross / +13.90bps net`。
- `ETHUSDT` 更像 **short-side** alpha：对应 short flow-gate 壳约 `59` 笔、`+9.73bps gross / +1.73bps net`；但 `SOL/XRP` 同壳显著为负，说明这不是“全币通用 price-discovery 规则”，而是 **asset × side admission**。
- 因此，这条线更像：**BTC 做 long follow-through、ETH 做 short follow-through**；若不做 whitelist，edge 很容易被 alt 噪音和成本吃掉。

## 3. 为什么和当前项目有关
这条线直接扩充的是 **cross-market / price-discovery raw alpha 素材池**。它不是又一个“funding / sentiment / regime overlay”，而是能独立写成 `entry / exit / cost` 的单腿方向书，而且天然适合 `5m`，再往 `1m/3m` 缩也有明确方向：只保留 futures 明显先动、spot 还没 fully absorb 的 bar。

## 3.5 策略拆解（必填）
- 方向属性：cross-market lead-lag / directional continuation
- 基础 alpha：`gap_bps = 1e4 * (ret_perp_5m - ret_spot_5m)`；当 `gap_bps` 同向显著扩张且 perp 主动成交方向一致时，下一段 `perp` 更易续行
- regime：高信息到达 / 高波动 impulse bar 更优
- filter / veto：`BTC long` 先看 `gap_bps > 2`、`ret_perp > 0`、`taker_share > 0.56`、`|ret_perp| > 3bps`；`ETH short` 镜像；其他币默认 veto
- risk / sizing / execution overlay：`next-bar open` 入场、固定持有 `12` 根 `5m`（约 `1h`）、`no-overlap`、首轮 round-trip 成本先粗扣 `8bps`

## 4. 可复刻的最小实验
- 研究假设：**futures-led impulse** 不是均匀存在，而是只在 `gap + aggressor-flow` 同向的强 bar 上，才会转成可交易 continuation。
- 可计算定义：
  - `ret_spot_5m = close_spot / close_spot[-1] - 1`
  - `ret_perp_5m = close_perp / close_perp[-1] - 1`
  - `gap_bps = 1e4 * (ret_perp_5m - ret_spot_5m)`
  - `taker_share = taker_quote / quote_vol`
- 最小回测切口：Binance `BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT` spot + USDⓈ-M perp，`5m`，近 `45~90d`；信号在 bar close 生成，`next-bar open` 入场，`12-bar` time-stop，`no-overlap`。
- 先看 2 个指标：
  1. `gross/net bps per trade`（先粗扣 `8bps`）
  2. `asset × side` 稳定性（BTC long / ETH short 是否持续优于 alt）

## 5. 风险与保留意见
- 论文证据目前是 **ScienceDirect article page snippets + DOI metadata**，不是全文逐表复刻；不能编造成“已完整复刻 paper tables”。
- 我这里用的是 Binance 同 venue 的 spot/perp proxy，不是论文里的完整 spot/futures price-discovery 框架；因此更像 **desk transfer**，不是 faithful replication。
- 阈值（`2bps / 0.56 / 3bps / 12 bars`）目前仍属于 first-cut admission，后续必须补 rolling / 邻域稳定性，避免把 sample-specific 噪音当规律。
- 同标的 spot-perp 双腿价差 close 本身在顶级 venue 很可能过薄；当前更诚实的落点是 **单腿 perp directional shell**，不是把它包装成无风险套利。

## 6. 来源
- Robertson, K., & Zhang, R. (2025). *Price discovery in bitcoin spot and futures markets*. *Journal of International Money and Finance*.
- DOI: `10.1016/j.jimonfin.2025.103415`
- Readable URL: `https://www.sciencedirect.com/science/article/pii/S0261560625001500`
- 本地 portability artifact：`/root/clawd/jerry/momentum/reports/artifacts/literature/spot_futures_price_discovery_probe_summary_2026-04-10.csv`
