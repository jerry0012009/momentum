# Rank 301 / BB-zscore overshoot × RSI confirm × trend-veto mean reversion — survivor decisive follow-up

- Time: 2026-04-03 02:34 UTC
- Executor: bot3 auto loop
- Target: `Rank 301 / BB-zscore overshoot × RSI confirm × trend-veto mean reversion`
- Stage: `Surviving candidate slot` 唯一一次 decisive follow-up
- Verdict: `background/P0`
- Artifact: `reports/artifacts/rank301_survivor_followup/summary.csv`
- Aggregate: `reports/artifacts/rank301_survivor_followup/aggregate.csv`

## Why this changes system belief
`Rank 301` 的 clean-room 存活不来自一个可迁移的 `overshoot snapback` pocket，而是来自把 admission 收紧到几乎没样本后的零星幸存：在公开 15m OHLCV、`BTC/ETH/SOL/BNB` 四个大币、`z20 + ATR stop + z-exit` 的最小 clean-room 下，`z-only` 与 `+RSI` 在 `12/20bps` 成本后全部明显为负；只有再叠 `trend-veto` 时才转正，但四资产全年合计只剩 `17` 笔交易，且主要集中在极深 `3.0+` overshoot，样本量不足以支撑 admission 到 `P2`。

## What I tested
只做这轮 survivor 要求的最小 existence / cost-survival 检查，不回去复述源码结构：

- 数据：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/cross_asset_cache/*__365d__15m.csv`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 周期：`15m`
- clean-room shell：
  - `z = (close - SMA20) / rolling_std20`
  - long when `z <= -2`, short when `z >= 2`
  - exit when `z` 回到 `-0.5 / +0.5`
  - stop = `2.5 * ATR(14)`
  - next-bar open 执行
- ablation：
  1. `z_only`
  2. `z + RSI(14)`
  3. `z + RSI(14) + 50-bar EMA slope trend-veto`
- 成本：round-trip `12bps` 与 `20bps`

## Key results
来自 `aggregate.csv`：

- `z_only @ 12bps`: `6875` 笔，平均 `-12.80bps/trade`，总和 `-88084.64bps`
- `z_only @ 20bps`: `6875` 笔，平均 `-20.80bps/trade`，总和 `-143084.64bps`
- `z+RSI @ 12bps`: `2468` 笔，平均 `-13.36bps/trade`，总和 `-33488.22bps`
- `z+RSI @ 20bps`: `2468` 笔，平均 `-21.36bps/trade`，总和 `-53232.22bps`
- `z+RSI+trend-veto @ 12bps`: 只剩 `17` 笔，平均 `+39.55bps/trade`
- `z+RSI+trend-veto @ 20bps`: 只剩 `17` 笔，平均 `+31.55bps/trade`

翻成人话：
- base `overshoot snapback` 在公开 15m clean-room 里并没有自己站住；
- `RSI` 不是救命层，只是减少交易后仍然亏；
- 真正让结果翻正的是把样本砍到几乎不可 admission 的 `trend-veto`，这更像“极重 gate 后的 anecdotal survivors”，不是可迁移 pocket。

## Bucket governance read
`summary.csv` 显示：
- `z_only` 与 `+RSI` 在 `2.0-2.5 / 2.5-3.0 / 3.0+` 各桶都没有费后活口；
- `trend-veto` 的幸存交易主要躲在 `3.0+` 深 overshoot，但 BTC/ETH/SOL/BNB 全年合计也只形成 `17` 笔；
- 这不符合进入 `P2` 所需的“可复核、可迁移、可继续 admission”的最小样本要求。

## Honest exit decision
这一步必须直接收口，而不是再给它第二次 survivor 或开放式 `keep_P1`：

`Rank 301` 的 survivor follow-up verdict = `background/P0`。原因不是“源码不完整”，而是**最小 clean-room existence 已经回答了关键问题：edge 只有在极度收紧 gate、把交易数压到全年十几笔后才显得存活；这不足以说明存在一个对 desk 有迁移价值的单币 short-cycle overshoot pocket。**

## Result sentence for runtime
`Rank 301` 的唯一 survivor follow-up 已完成：公开 `15m` clean-room 下，`overshoot snapback` base 壳与 `+RSI` 在 `BTC/ETH/SOL/BNB` 四资产、`12/20bps` 成本后均不存活；`+trend-veto` 虽转正但全年仅 `17` 笔样本，属于过度收紧后的零星幸存，因此本轮诚实收口为 `background/P0`，不升 `P2`。

## Runtime implications
- `Surviving candidate slot`: closed; `Rank 301` 用尽唯一 follow-up 预算，不再保留前排资格。
- `Background pool`: now includes `Rank 301` as the latest parked object.
- `cycle_plan[1]`: should be marked `done` with the above result; later items remain untouched.
