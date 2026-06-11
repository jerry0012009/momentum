# bot3 optimization loop — OI crowding reversal confluence fresh intake -> background/P0

- Time: 2026-04-21 20:40 UTC
- Target: `research/quant_digests/2026-04-21_2020_oi-crowding-reversal-confluence-alpha.md`
- Action: fresh intake first verdict
- Verdict: `background/P0`

## Why this changed system belief
`crowded perp positioning reversal × OI/taker/CVD/RSI confluence` 没有通过 fresh intake 的最小 decisive blocker：在现成 probe 的 `5m/15m` 事件样本里，统一 roundtrip 成本后整体已转负，且表面正 pocket 只剩 `15m SOL` 与 `1` 个 `ADA` 单例，明显不满足“至少两个非单日/非单币支撑的正 pocket”。因此它当前更像 event router / execution veto 提示，而不是值得前排保留的 standalone crowding-reversal alpha。

## Minimal evidence used
直接复核 `reports/artifacts/quant_digests/2026-04-21_oi_crowding_probe.csv`（共 37 个事件；8 个 liquid majors；`5m/15m` 两个周期）。

### Overall summary
- `5m`：`n=17`
  - `next3 gross ≈ +0.17bps`，统一 `4bps roundtrip` 后约 `-3.83bps`
  - `bracket gross ≈ -6.30bps`，统一 `4bps / 8bps roundtrip` 后约 `-10.30 / -14.30bps`
- `15m`：`n=20`
  - `next12 gross ≈ +7.66bps`，统一 `8bps roundtrip` 后约 `-0.34bps`
  - `bracket gross ≈ +2.16bps`，统一 `4bps / 8bps roundtrip` 后约 `-1.84 / -5.84bps`

### Symbol concentration
`15m bracket` 的正 pocket 只有：
- `SOLUSDT`: `n=5`, `gross ≈ +83.02bps`, `net8 ≈ +75.02bps`
- `ADAUSDT`: `n=1`, `gross ≈ +150.0bps`, `net8 ≈ +142.0bps`

其余 `ETH/XRP/DOGE/LINK/BNB` 全部为负；`5m` 只剩 `DOGEUSDT n=5` 的局部正 pocket，而整体 `5m bracket` 仍显著费后为负。

### Day concentration
- `15m` 三个交易日中，`2026-04-19` 贡献 `+173.01bps` gross，`2026-04-20` 则为 `-163.52bps`
- `5m` 两个交易日里，`2026-04-20` 为 `+79.34bps`，`2026-04-21` 为 `-186.43bps`

说明这条线当前更像稀疏、日期敏感、币种敏感的 crowding-event 提示，而不是稳定可迁移的 after-cost alpha。

## Honesty / execution note
本轮不需要再额外进入 OI/funding 发布时间与拥挤滑点的更深 honesty 子检查：因为它在更前面的门槛——“至少两个非单日/非单币支撑的 after-cost 正 pocket”——已经失败。即使先不把这些 realism 惩罚继续加严，本对象也不值得保留 survivor。

## Runtime writeback
- `cycle_plan[1]` -> `done`
- fresh intake latest result -> `background/P0`
- append to background parked summary

## Tail steps
- Homepage refresh: attempted `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`; process exceeded the command timeout and was killed, treated as non-blocking tail failure.
