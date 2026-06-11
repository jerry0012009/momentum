# 2026-04-21 13:28 UTC — cross-exchange funding spread carry × dip-tolerance 持仓门控 fresh intake first verdict

- Target: `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
- Action: fresh intake first verdict
- Verdict: `background/P0`

## Why this changes system belief
同源 repo（`kohtabeloff/funding-arb-bot`）虽然把 `positive net APR streak + 4h negative-hours stop + liquidation-distance auto-close` 工程化得很完整，但仓库内现成 portability probe 已经给出这条 raw alpha 在公开可复算口径下的唯一 decisive blocker：`BTC/ETH/SOL` 三个 liquid majors 在 `15m`、`160d`、`z_entry=2.0`、`funding_min_bps=0.5`、`hold<=96 bars`、统一 roundtrip `34bps` 成本后全部费后显著为负，组合 `145` 笔交易 `avg_net_bps≈-32.33`、`win_rate=0`，没有留下至少两个 symbol / venue-pair 同向 after-cost carry pocket，因此本轮不能 `keep_P1`，直接收口 `background/P0`。

## Evidence used
1. Digest: `research/quant_digests/2026-04-21_1104_crossvenue-funding-spread-diptolerance-shell.md`
2. Same-source prior repo audit: `research/quant_digests/2026-04-16_0018_positive-streak-netcarry-shell.md`
3. Portability artifact: `reports/artifacts/quant_digests/funding_spread_threshold_portability_probe_2026-04-16_summary.json`
4. Detail table: `reports/artifacts/quant_digests/funding_spread_threshold_portability_probe_2026-04-16.csv`

## Minimal decisive blocker
- The shell's claimed edge still does not survive unified execution-cost reality.
- Probe summary shows:
  - `BTCUSDT`: `61` trades, `avg_net_bps≈-32.81`, `win_rate=0`
  - `ETHUSDT`: `56` trades, `avg_net_bps≈-32.64`, `win_rate=0`
  - `SOLUSDT`: `28` trades, `avg_net_bps≈-31.54`, `win_rate=0`
- Average realized funding contribution per trade is only about `0.036~0.062bps`, far below the unified cross-venue roundtrip cost assumption (`34bps`).
- Therefore the remaining story is execution-shell completeness, not a live after-cost carry pocket.

## Scope control
This round intentionally did **not** open a new follow-up axis. Existing same-source probe already resolves the first-verdict question under the policy's required cost realism, so repeating another funding-axis check would be low-leverage duplication.
