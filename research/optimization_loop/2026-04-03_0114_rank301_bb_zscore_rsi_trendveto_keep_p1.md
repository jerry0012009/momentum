# Rank 301 / BB-zscore overshoot × RSI confirm × trend-veto mean reversion — fresh intake first verdict

- Time: 2026-04-03 01:14 UTC
- Executor: bot3 auto loop
- Source intake: `research/quant_digests/2026-04-02_2356_bb-zscore-rsi-trendveto-meanreversion-alpha.md`
- Object: `BB/z-score overshoot × RSI confirm × trend-veto` single-asset short-cycle mean reversion shell
- Verdict: `keep_P1`
- Assigned Rank: `301`

## Why this changes system belief
`Rank 301` 不是又一个把 RSI/BB 堆在一起的指标拼盘，而是已经有清楚 raw-alpha 主语的单币 `overshoot snapback` 壳：源码把 `|z|>=2` 的统计极端、`RSI` 确认、`EMA slope` 趋势 veto、`ATR` 防守、以及 `z-score bucket governance` 全都写成了可复核的 clean-room 策略骨架，因此它足够独立于既有 pairs / carry / breakout 家族，值得进入 `P1 survivor` 做唯一一次便宜但决定性的 existence check。

## Honest read
这轮还不该直接升 `P2`，因为当前证据主要来自 repo/source audit 与策略结构完整性，而不是我们自己的 clean-room existence 结果；也不该直接打回 `P0`，因为它已经满足了 fresh intake 的几个关键门槛：
1. raw alpha 主语明确：`single-asset overshoot snapback`；
2. 频率与 desk 对齐：`5m/15m`；
3. 可复现路径明确：公开 OHLCV 即可；
4. 最小实验壳明确：`z-only -> +RSI -> +trend veto` 的 ablation，加上 `z-score bucket` 治理；
5. 主要风险也清楚：短周期摩擦、强趋势左侧抄底、以及过深 z-score 可能对应 liquidation/regime break。

## Result sentence for runtime
`Rank 301` 的 fresh intake first verdict = `keep_P1`：`BB/z-score overshoot × RSI confirm × trend-veto` 已形成独立于 pairs/carry/breakout 家族的单币 `overshoot snapback` raw-alpha 主语与最小 clean-room 实验壳，因此进入 `Surviving candidate slot` 做唯一一次 existence / cost-survival follow-up，而不是停留在无 rank 的源码摘要。

## Immediate runtime implications
- `Fresh intake slot`: this object is now closed as a fresh-intake verdict and released.
- `Surviving candidate slot`: should now hold `Rank 301` as the one allowed follow-up target.
- Next legal work on this object: exactly one decisive survivor follow-up answering whether `15m` clean-room existence plus basic cost survival is strong enough to promote to `P2`, otherwise it should be parked back to `background/P0`.
