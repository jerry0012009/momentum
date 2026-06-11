# Rank 426 / volume-switch trend-reversal fresh intake -> keep_P1

- Time: 2026-04-19 19:13 UTC
- Target: `research/quant_digests/2026-04-19_1405_volume-switch-trend-reversal-alpha.md`
- Action: fresh intake first verdict
- Rank assigned: `426`
- Verdict: `keep_P1`

## Why this was the only blocker to test
Digest 自己已经把主问题收敛得很清楚：原始 `15m` 连续再平衡的 switch 组合有 gross，但被过高 turnover 吃掉；因此本轮不重建策略、不追加第二个维度，只补一条最小 honesty 检查——**若保持同一组 switch 权重逻辑，仅把 rebalance 频率压低到更诚实的 `30m/1h`，费后 pocket 是否仍存在**。

## What I checked
用 digest 已落库的 `reports/artifacts/quant_digests/2026-04-19_volume_switch_weights_tail.csv` 作为原始权重轨迹，配合同期 10 个 liquid majors 的本地 `15m` perp close 序列，做最小实现压缩：

- `15m`：每根 bar 按原权重连续再平衡
- `30m`：每 2 根 bar 才更新一次权重，其余时间持有上次权重
- `60m`：每 4 根 bar 才更新一次权重，其余时间持有上次权重
- 成本口径：统一 `8bps round-trip`，按权重变动量扣减（即 `turnover * 4bps` 的单边成本）

## Result
最小压缩后，after-cost pocket 没有消失：

- `15m` replication-ish：`gross ≈ +0.394 bps/bar`，`net8 ≈ -0.414 bps/bar`，`turnover ≈ 19.38x/day`
- `30m` rebalance：`gross ≈ +0.668 bps/bar`，`net8 ≈ +0.061 bps/bar`，`turnover ≈ 14.57x/day`
- `60m` rebalance：`gross ≈ +0.910 bps/bar`，`net8 ≈ +0.465 bps/bar`，`turnover ≈ 10.67x/day`

对应累计口径也从原始连续再平衡的费后回撤，改善为：

- `30m`: `cum_net8 ≈ +0.14%`
- `60m`: `cum_net8 ≈ +2.19%`

## System-changing conclusion
`high-volume trend-following × low-volume cross-sectional loser->winner fade switch` 不是“框架有趣但摩擦彻底吃光”的假壳；当前更诚实的结论是：**原始 `15m` 实现壳不值得直接承接，但同一信号逻辑在更低频 rebalance 下仍保留费后为正的独立 pocket**。因此本轮 fresh intake 直接给 `keep_P1`，进入 survivor，而不是收口到 `background/P0`。

## What the next and only survivor follow-up should answer
下一轮唯一 follow-up 不该再重复做“有没有 edge”这类 existence 检查，而应直接收口到一个单一问题：

- `30m/1h rebalance` 中，哪一个低换手 spec 才是最诚实、最不依赖少数资产/少数时段的可持续版本。

## Files touched
- `docs/BOT2_BOT3_STATE.md`
- `research/optimization_loop/2026-04-19_1913_rank426_volume_switch_freshintake_keep_p1.md`

## Tail-step status update
- Homepage publish tail step: attempted via `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`, but the process produced no output and exited with `SIGKILL` after timeout; treated as non-blocking tail failure.
- Email notification: sent successfully to configured recipient.
