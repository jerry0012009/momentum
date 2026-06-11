# 2026-04-06 04:36 UTC · Rank 346 / scheduled-macro impulse × pre-event sentiment gate / survivor follow-up -> background P0

## 本轮对象
- Target: `Rank 346 / scheduled-macro impulse × pre-event sentiment gate`
- 当前层级动作：`Surviving candidate -> background / P0`
- 执行动作：对 survivor 唯一 follow-up 做最便宜但决定性的 honesty check：直接测 `FOMC × BTC/ETH × 1m/3m/5m/15m` 的 `post-event first-reaction continuation`，并把 `taker + delay` 明确记账。

## 这轮实际怎么做
沿用上一轮已经整理好的 `18` 次 FOMC 事件时钟与 sentiment bucket（fear / neutral / greed），新增拉取 Binance `BTCUSDT / ETHUSDT` 事件窗 `1m` K 线，统一按下面口径做 event-follow：

1. `r0` = 公布后第一根 `1m` bar 的收益；
2. 方向只取 `sign(r0)`，不让 sentiment 负责猜方向；
3. `delay0`：在第一根 bar 收盘后顺着 `sign(r0)` 入场；
4. `delay1`：再多等 `1` 根 bar 后入场；
5. 持有窗口分别看 `1m / 3m / 5m / 15m`；
6. round-trip 成本显式扣 `12bps / 20bps`（对应 per-side `6bps / 10bps` 的 taker 压力口径）。

产物：
- `reports/artifacts/rank346_survivor_followup/fomc_btc_eth_first_reaction_followthrough_1m.csv`
- `reports/artifacts/rank346_survivor_followup/summary.csv`

## 结论
**本轮 survivor follow-up 的答案是否定的：`Rank 346` 没有压出一个足够诚实、可迁移的 event sleeve，唯一 follow-up 用尽后应直接退回 `background / P0`，不升 `P2`。**

## 为什么这轮可以直接收口到 background
### 1) BTC 侧几乎没有可交易 pocket
即便只看 paper 最贴近的 `FOMC`，BTC 端在 fear / neutral bucket 基本全线为负：
- `BTC fear`：`1m/3m/5m` 在 `delay0/delay1`、`12bps/20bps` 下全部负；
- 唯一勉强转正的是 `15m delay1`，但均值也只有：
  - `+0.135%`（12bps round-trip）
  - `+0.055%`（20bps round-trip）
  且样本仅 `4` 次；
- `BTC neutral`：`1m/3m/5m/15m` 全部为负；
- `BTC greed` 虽然在 `3m/5m` 有些微正均值，但幅度很薄：
  - `3m delay1 @ 12bps`：`+0.090%`
  - `5m delay1 @ 12bps`：`+0.140%`
  - `15m` 基本又回到接近零。

翻成人话：**如果连 BTC 上最自然的 FOMC 壳都只能挤出很薄、很脆的 greed-only pocket，这还不够支撑一个应进入 admission 的 event sleeve。**

### 2) ETH 虽然在 greed bucket 有 pocket，但对象仍不够诚实地“可迁移”
ETH 的 greed bucket 确实比 BTC 好：
- `ETH greed 5m delay1 @ 12bps`：均值 `+0.283%`，胜率 `71.4%`；
- `ETH greed 15m delay1 @ 12bps`：均值 `+0.265%`，胜率 `71.4%`；
- 即便到 `20bps` round-trip，
  - `ETH greed 5m delay1` 仍有 `+0.203%`；
  - `ETH greed 15m delay1` 仍有 `+0.185%`。

但问题是：
- 这只成立在 **ETH + greed + FOMC** 这一条窄 sleeve；
- BTC 并没有同步复制；
- neutral / fear bucket 大多不成立；
- 当前还没有 `CPI / NFP / PCE` 的同口径复制。

也就是说，**这条线最多只证明“FOMC 下 ETH 在 greed 时可能存在一小段 first-reaction continuation”，还远远没到可以把对象整体升成 `P2` 的程度。**

### 3) 按 policy，这次 follow-up 用完后不能继续拖成开放式 P1
survivor 只有这一次便宜且决定性的 follow-up 预算。现在得到的结构是：
- 不是完全没信号；
- 但信号只停在过窄的 `ETH/FOMC/greed` 局部 pocket；
- 尚不足以回答 `cross-event portability`；
- 更不足以写成一个对 desk 有 admission 价值的通用 event sleeve。

因此更诚实的收口不是继续留在前排等“下次再补 CPI/NFP/PCE”，而是：
**承认它当前仍主要是一个有启发性的局部 observation，不是已经压实的前排对象，按 policy 退回 `background / P0`。**

## 会改变系统认知的一句话
`Rank 346` 的唯一 survivor follow-up 已经给出终局：在显式 taker + delay 口径下，`post-FOMC first-reaction continuation` 只在 `ETH × greed` 压出窄 pocket，`BTC` 与其他 sentiment bucket 不复制，当前仍不足以形成可 admission 的 event sleeve，因此 `Rank 346` 用尽唯一 follow-up 后退回 `background / P0`。
