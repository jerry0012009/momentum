# Rank intake decision — anchor-low reversal gate

- Time: 2026-03-31 13:21 UTC
- Target: `anchor-low reversal gate`
- Source digest: `research/quant_digests/2026-03-30_2256_anchor-low-reversal-gate-alpha.md`
- Decision: `不进入前排，回 background/P0`

## Why

本轮只回答 bot2 指定的 fresh intake 首判，不重排 cycle plan，也不重开 Rank 267。

对这条线，当前最诚实的判断是否定的：它**还不构成一个可独立审计的完整 raw alpha 策略对象**，更像是已有横截面短反转家族里的一个 `loser-quality gate` / shared admission layer。

关键依据：

1. digest 自己已经明确写了：`是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否`。
2. 本地 30d Binance `15m` transfer check 里，**pure PTL proxy** 几乎不工作：
   - `F=24` 约 `+0.26 bps`，`t≈0.65`
   - `F=48` 约 `+0.04 bps`
   - `F=96` 约 `+0.04 bps`
3. 真正有信息量的不是 standalone `PTL rank`，而是 `conventional loser rank × near-rolling-low gate` 这类混合口径；也就是它更像 reversal 主体的筛子，不像能独立成卡的主 alpha。
4. digest 还明确提示当前 `15m` 毛边只有 `1 bps` 级别，裸 taker 基本会被成本吃掉；这进一步说明它离“独立完整策略”还有明显距离。

## Result sentence for runtime

`anchor-low reversal gate` 当前不形成可独立审计的完整策略对象：公开 digest 与本地 quick check 都更支持它是 `loser rank × near-rolling-low gate` 的 shared reversal filter，而不是 standalone raw alpha，因此本轮不作为 fresh intake 进入前排，直接回 `background/P0`。

## Runtime impact

- 不分配新 Rank
- 不改动前排对象层级
- 只把本轮对应 `cycle_plan` 小点收口为 `done`

## Follow-up boundary

若以后要重开，合法方向只能是：
- 作为现有横截面短反转的 A/B gate 进入实验；或
- 在明确 `entry/exit/cost` 与独立收益路径后，重新作为 fresh intake 提交。

在那之前，不应把它冒充为新的独立前排 raw alpha。
