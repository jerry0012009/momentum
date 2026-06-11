# Rank 330 survivor follow-up：canonical SuperTrend 对账后恢复 firing density，升到 P2

- 时间：2026-04-04 14:28 UTC
- 对象：`Rank 330 / dual SuperTrend flip × EMA50 × volume gate`
- 动作：用掉 survivor 唯一一次 follow-up，直接做 `canonical SuperTrend / firing density` 对账
- 依据：`research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`
- 对账工件：`reports/artifacts/rank330_canonical_supertrend_btc90d_compare/summary.json`

## 本轮只回答一个问题

repo 当前 `SuperTrend` 实现之所以在 recent 90d 几乎不触发，到底是这条 raw alpha 天生不 firing，还是实现口径偏离 canonical 造成的冻结？

## 最小实验设计

- 标的：`BTCUSDT`
- 周期：`15m`
- 区间：最近 `90d`（`2026-01-04 11:00 UTC` ~ `2026-04-04 10:45 UTC`）
- 对比对象：
  1. repo 当前 `calculate_supertrend()` 口径
  2. 常见 canonical SuperTrend 口径（final upper/lower band 递推与 trend switch 按标准条件实现）
- 核对指标：
  - `bull_flip` / `bear_flip` 次数
  - 按同一 `EMA50 + volume + not high-vol + slow ST confirm` 外壳后的 `long_signal` / `short_signal` 数量
  - 方向序列一致率

## 结果

### repo 当前实现（fast ST 8, 2.5）
- `bull_flip = 2`
- `bear_flip = 3`
- `long_signal = 0`
- `short_signal = 0`

### canonical 口径（fast ST 8, 2.5）
- `bull_flip = 146`
- `bear_flip = 146`
- `long_signal = 69`
- `short_signal = 87`

### 差异
- 方向一致率仅 `54.79%`
- 不一致 bar 数：`3903 / 8640`

## 改变系统认知的一句话

`Rank 330` 当前“不 firing”并不是这条 `dual SuperTrend flip × EMA50 × volume gate` raw alpha 本身失效，而是 repo 现实现与 canonical SuperTrend 严重偏离，导致 fast flip 几乎冻结；一旦换回常见 canonical 口径，BTC 15m recent 90d 立刻恢复到可验证的信号密度，因此 survivor follow-up 通过，足以把它从 `P1` 升到 `Active P2`。

## 层级决定

- 本轮 verdict：`promote_P2`
- 理由：唯一 blocker 已被定位为实现/定义层的 canonical mismatch，而不是 raw alpha 没有触发壳；现在已经有理由进入 `P2 admission`，去正式回答成本后 effectiveness、跨资产稳定性、时间稳定性与参数稳定性。
- 还不能直接进 `P3`：本轮只证明 firing density 被 canonical 化恢复，还没完成 admission 五维收口。
