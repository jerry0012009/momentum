# bot3 auto — regime-aware XSM router overlay fresh intake first verdict
- time: 2026-04-21 19:38 UTC
- executor: bot3
- cycle item: 1
- target: `research/quant_digests/2026-04-21_1817_regimeaware-xsmomentum-router-overlay.md`
- action: fresh intake first verdict

## verdict
`regime-aware XSM router overlay` 的 fresh intake first verdict 已诚实收口：现有 15m public probe 中静态 long-short `gross≈-0.36bps/bar`、统一成本后 `net≈-1.40bps/bar`，BTC-vol/dispersion scaling 后仍 `scaled_net≈-1.38bps/bar`，digest 里的 strongest-only 也只有亚 bps gross、未证明能覆盖统一成本；因此它当前更像 shared exposure/router overlay 提示，而不是可前排保留的独立 after-cost alpha，本轮直接收口 `background/P0`。

## 最小 decisive blocker
本轮只补一个 blocker：确认 `cross-sectional relative momentum × BTC-vol / dispersion exposure scaling` 是否能作为可保留的 `router + overlay` 组合壳，还是静态 long-short / strongest-only 在统一成本下仍太薄。

## evidence
- existing digest public-data probe: `reports/artifacts/quant_digests/2026-04-21_xsm_regimeaware_probe_summary.csv` / `..._detail.csv`
- 静态 15m long-short：`gross≈-0.36bps/bar`，不是正 raw edge。
- 统一成本后：`net≈-1.40bps/bar`，累计约 `-60%`。
- BTC realized-vol / cross-asset dispersion scaling 后：`scaled_net≈-1.38bps/bar`，累计约 `-59%`，没有把成本后收益翻正。
- 月份切片：`2026-03≈-43.66%`，`2026-04≈-15.81%` scaled net，两个可见月份都为负。
- digest 里提到的 `lookback=16 long_top1` strongest-only 仅约 `+0.36bps/bar` gross，next `2/4/8 bars` 也只有 `+0.56/+0.63/+0.18bps` gross，未证明能覆盖统一成本，更未证明不是少数窗口/少数好日子支撑。

## runtime update
- Fresh intake slot 结论写成 `background/P0`，不分配 Rank，不进入 survivor。
- Fresh intake current_target 按 cycle_plan 顺序切到 item 2：`research/quant_digests/2026-04-21_1914_btcresid-xs-fastreversal-dailyrebalance-alpha.md`。
- `cycle_plan` item 1 status 写成 `done`。

## tail
- homepage refresh: attempted via `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`; process exited with `SIGKILL`, treated as non-blocking tail failure.
- email notification: sent via `send_text_email.py` to configured recipient.
