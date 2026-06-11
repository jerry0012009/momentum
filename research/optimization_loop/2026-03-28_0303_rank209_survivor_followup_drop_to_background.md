# Rank 209 / US close -> crypto synthetic open spillover survivor follow-up drop_to_background

- Time: 2026-03-28 03:03 UTC
- Target: `Rank 209 / US close -> crypto synthetic open spillover`
- Action type: survivor唯一 follow-up
- Verdict: `drop_to_background`
- Artifact dir: `reports/artifacts/rank209_survivor_followup_20260328`

## 本轮只回答的 decisive 问题
对 `QQQ / NVDA` 的 US close 最后 `15m/30m` shock，映射到 `BTCUSDT / ETHUSDT` 的：
- `20:00 UTC` 即时释放
- `00:00 UTC` synthetic-open catch-up

并统一检查：
- 持有：`15m / 30m / 60m`
- friction：`4 / 6 / 8 / 10 bps` round-trip
- 样本：沿用已有 `15m` equity/crypto bars（`QQQ_yahoo_15m.csv / NVDA_yahoo_15m.csv / BTCUSDT_binance_15m.csv / ETHUSDT_binance_15m.csv`）
- 强 shock 口径：按每个 `leader × leader_window` 的 `abs(shock)` 取 top 30%

## 结果摘要
### 1) 确实看到了“像 pocket 的东西”，但不够清晰到升 P2
最像 synthetic-open pocket 的组合是：
- `QQQ -> BTCUSDT`, `leader_window = 30m`, `boundary = 00:00 UTC`
  - all days `n=28`
  - `30m hold`: gross `+11.87 bps`, net `+7.87 / +5.87 / +3.87 / +1.87 bps`（4/6/8/10bps）
  - `60m hold`: gross `+15.50 bps`, net `+11.50 / +9.50 / +7.50 / +5.50 bps`
- `QQQ -> ETHUSDT`, `leader_window = 30m`, `boundary = 00:00 UTC`
  - all days `n=28`
  - `30m hold`: gross `+19.66 bps`, net `+15.66 / +13.66 / +11.66 / +9.66 bps`
  - `60m hold`: gross `+20.23 bps`, net `+16.23 / +14.23 / +12.23 / +10.23 bps`

### 2) 但它没有诚实证明“gap-separated synthetic-open continuation”是独立 pocket
关键问题不在于有没有正收益，而在于：**synthetic-open 是否真的是唯一值得保留的 delayed catch-up 结构。** 这一步没有证明清楚：

- `QQQ -> ETHUSDT` 在 `20:00 UTC` immediate 也同样为正：
  - `30m hold`: gross `+10.47 bps`
  - `60m hold`: gross `+25.98 bps`
  这说明 ETH 更像是 **close 后就开始释放的延续**，不是一个必须等到 `00:00 UTC` 才出现的独立 pocket。
- `QQQ -> BTCUSDT` 的确呈现出 **synthetic-open 好于 immediate**：
  - immediate `30m / 60m`: gross `-1.05 / +3.29 bps`
  - synthetic-open `30m / 60m`: gross `+11.87 / +15.50 bps`
  但统计把握仍偏弱（对应 gross t-stat 约 `0.67 / 0.55`），更像“值得记一笔的弱迹象”，还不够到 `clear reproducible pocket`。
- `NVDA` 侧最强结果反而更多出现在 `20:00 UTC immediate`，不是 `00:00 UTC synthetic-open`：
  - `NVDA -> ETHUSDT`, `30m shock`, immediate `60m`: all days gross `+24.28 bps`，top30_abs gross `+75.51 bps`
  这进一步削弱了“必须是 synthetic-open catch-up”这个母命题。

## 诚实结论
`Rank 209` 的 survivor follow-up 证明了：
- **US close shock -> crypto 后续延续** 这个更宽泛的想法不是空的；
- 但它没有把 thesis 收口成一个足够清晰、足够独立的 **`gap-separated synthetic-open continuation pocket`**。

当前留下来的最好结果，要么：
1. 其实是 `immediate + synthetic` 都会释放的宽泛 cross-asset continuation；
2. 要么只在 `QQQ -> BTC/ETH @ 00:00 UTC` 上留下弱正值，但统计把握不足以把它当成一个已成型的 survivor->P2 对象。

因此这次 survivor 唯一预算应诚实用尽，并把该对象移入 `Background pool`，而不是为了几个方向正确但仍偏薄的结果继续拖成长尾 P1。

## Result sentence
`Rank 209 / US close -> crypto synthetic open spillover` 的 survivor 唯一 follow-up 已收口：QQQ 的确在 `00:00 UTC` 对 BTC/ETH 留下了成本后正值，但 ETH 的 immediate release 也同样为正、BTC 的 synthetic-only 优势统计仍偏弱，因此它没能诚实证明独立的 gap-separated synthetic-open pocket，预算用尽后应移入 `Background pool`。
