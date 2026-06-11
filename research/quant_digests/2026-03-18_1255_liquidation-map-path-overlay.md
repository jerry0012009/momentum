# 别把 liquidation map 当 15m 方向神图：更像该先测的是 `cluster path score`，给 breakout-short / Fib / EMA 做 shared path overlay
- 时间：2026-03-18 12:55 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/liquidation-map/path-overlay/risk/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
这次看的是 `aoki-h-jp/py-liquidation-map`（2023）这个仓库。它不是直接给你一个 15m 开平仓策略，而是用 **Binance / Bybit 的公开 `aggTrades` 历史成交**，把大额主动成交映射成潜在爆仓价，再画出 liquidation map。对我们 desk 最有价值的读法，不是把它当“价格会去哪”的神谕，而是把它降级成 **post-break / post-retest 的 path overlay**：前方是不是有顺势清算燃料，还是反方向的清算陷阱更近。

## 2. 核心结论
- **一句话核心结论**：对 `15m` 来说，liquidation map 更适合回答“这笔单子前方路况怎样”，而不是回答“这一根该不该直接开”。
- **一句话证明方式**：repo 直接把公开成交数据转成潜在清算层：大额 `Buy` 成交会被映射到 `0.99 / 0.98 / 0.96 / 0.90` 倍价格的 `100x / 50x / 25x / 10x` long-loss-cut；大额 `Sell` 则映射到 `1.01 / 1.02 / 1.04 / 1.10` 倍价格的 short-loss-cut，并支持 `>=100,000 USDT`、`top 100`、`top 1%` 三种筛选模式。
- 真正值得复用的，不是 repo 的图片本身，而是它那套 **“先挑大额主动成交，再把潜在爆仓价堆成密度”** 的骨架。翻成人话：别只看价格形态，也看价格前后有没有一团容易被挤爆的仓位。
- 这比继续给三条收口线各加一个独立过滤器更值得，是因为它能横向服务三条线：`breakout-short follow-up` 关心下方有没有 long liquidation fuel；`Fib retest_hold` 与 `EMA / PSAR continuation` 则更关心上方 short squeeze fuel 与下方 long cascade trap 的相对位置。

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：跌破后若下方 `0.3~1.5 ATR` 内堆着密集 long-liquidation cluster，short continuation 更像有“被动卖盘燃料”；若最近的大簇反而在上方，追空更容易踩回补。
- 对 `Fibonacci confirmation / retest_hold`：Fib 只告诉你“回到了哪”，liquidation map 可以补一句“守住后上方有没有 squeeze path，还是下方 cascade trap 更近”。这比把 retest_hold 继续写成二元开关更诚实。
- 对 `EMA / PSAR raw alpha focus`：EMA / PSAR 继续负责方向；`cluster path score` 负责给 continuation 一个路况分。这样它们不必继续单扛“后面还能不能走”。
- 如果要回答“为什么它比继续帮三条线收口更值得”：答案是它不是第四条新主线，而是一个能给三条线共用的 **路径/仓位 overlay**，且数据公开、最小实验很快能搭。

## 4. 可复刻的最小实验
- **研究假设**：在 `BTC / ETH / SOL` perpetual `15m` 上，给现有 `breakout_short`、`fib_retest_long`、`ema_psar_long` 叠加基于公开成交推断的 `cluster_path_score`，会比只看价格结构更早识别“前方有顺势燃料还是逆风陷阱”。
- **公开数据源**：
  1. Binance historical `aggTrades`（公开可下载，日级文件，可快速拼成 15m 前置窗口）；
  2. Binance perpetual `15m` klines（公开 REST）；
  3. 可选：后续再接 Bybit 做 cross-venue 稳健性。
- **最小定义**：
  1. 对 signal 前最近 `6h / 24h` 的大额主动成交做筛选：先测 `amount >= 100k USDT` 与 `top 1%` 两档；
  2. 把主动买成交映射到 long liquidation 价带，把主动卖成交映射到 short liquidation 价带；
  3. 计算入场价上下 `0.3~1.5 ATR` 内的 cluster density；
  4. long 侧：`path_score = short_liq_density_above - long_liq_density_below`；short 侧镜像；
  5. 先只测三臂：`base`、`base + binary path gate`、`base + size tilt`。
- **最小回测切口**：近 `180~365` 天，`15m`，`next-bar open`，`no-overlap`，成本先看 `6 / 10 / 15 bps per side`。
- **最先看的 4 个指标**：`post-cost return`、`false-follow-through rate`（入场后 4~8 根内反向穿越失效线）、`trade_count retention`、`positive_asset_ratio`。
- **下一步怎么测**：第一轮不要追求最漂亮的热力图，先回答一个更值钱的问题——**真正有增量的，是“顺势方向前方有清算燃料”，还是“逆风方向离陷阱太近所以该减仓/禁入”？** 如果只有其中一边有效，就先保留最简单那一边。

## 5. 风险与保留意见
- repo 不是直接读取真实账户杠杆与真实爆仓单，而是用 **大额主动成交 + 固定杠杆假设** 做 proxy；它更像 crowding/path 模型，不是真实 liquidation tape。
- `10x / 25x / 50x / 100x` 这些 loss-cut 倍数很粗糙，迁移到不同币种和不同波动环境时，可能只是“漂亮图像”，未必真有 alpha。
- 这类特征最容易犯的错是 **把 signal 之后的成交也倒灌进 path score**。最小实验必须严格冻结到 signal 前窗口。
- liquidation cluster 也可能更适合做 **target / sizing / veto**，而不是 entry gate；如果它只改善回撤、不改善收益，也要接受它只是 risk overlay。

## 6. 来源
- Aoki H. (2023). *py-liquidation-map: Visualize Liquidation Map from actual execution data*.
  - Venue / DOI：无
  - Repo URL: <https://github.com/aoki-h-jp/py-liquidation-map>
  - Readable URL: <https://github.com/aoki-h-jp/py-liquidation-map/blob/master/README.md>
  - Raw README: <https://raw.githubusercontent.com/aoki-h-jp/py-liquidation-map/master/README.md>
  - Key code: <https://raw.githubusercontent.com/aoki-h-jp/py-liquidation-map/master/liqmap/mapping.py>
  - Repo metadata snapshot: first commit `2023-08-25`, latest visible commit `2023-09-14`, `120` stars at fetch time.
