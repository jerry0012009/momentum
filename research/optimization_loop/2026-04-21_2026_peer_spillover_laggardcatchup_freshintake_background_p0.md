# bot3 optimization loop — peer-return spillover × laggard catch-up fresh intake first verdict

- Time: 2026-04-21 20:26 UTC
- Target: `research/quant_digests/2026-04-21_1506_crosscrypto-peer-spillover-laggardcatchup-alpha.md`
- Cycle item: `fresh intake first verdict`
- Verdict: `background/P0`

## What I checked
只做 bot2 指定的最小 decisive blocker：确认 `peer-return spillover × laggard catch-up basket` 在当前 `15m/5m`、统一成本与 basket/router 现实下，是否还保留可复制的 after-cost pocket，还是只剩 shared feature / router 提示。

读取并复核 digest 自带 artifact：
- `reports/artifacts/quant_digests/2026-04-21_crosscrypto_predictability_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_crosscrypto_predictability_15m_trades.csv`
- `reports/artifacts/quant_digests/2026-04-21_crosscrypto_predictability_5m_trades.csv`

## Decisive findings
### 1) 15m strongest-only 也没有穿过统一成本
- `peer_lag_gap_ew_top1`: `gross_mean_bps ≈ +0.219`, 但 `net4_mean_bps ≈ -3.781`
- `peer_lag_gap_vw_top1`: `gross_mean_bps ≈ +0.211`, 但 `net4_mean_bps ≈ -3.789`
- 等权 top2-vs-bottom2 与 quote-volume 加权全篮子更差，`net4_mean_bps` 约 `-3.85 ~ -3.91`

### 2) 5m 已经接近直接判死
- `peer_lag_gap_ew_top1`: `gross_mean_bps ≈ +0.034`, `net4_mean_bps ≈ -3.966`
- `peer_lag_gap_vw_top1`: `gross_mean_bps ≈ +0.003`, `net4_mean_bps ≈ -3.997`
- 非 top1 版本 gross 已转负，说明更宽 basket 根本撑不住

### 3) 不是“少数好日子遮住总体仍可保留”，而是统一口径下持续费后为负
15m 月份切片已经足够说明问题：
- `ew_top1`: `2026-02 ≈ -3.066bps`, `2026-03 ≈ -3.928bps`, `2026-04 ≈ -3.849bps`
- `vw_top1`: `2026-02 ≈ -3.276bps`, `2026-03 ≈ -3.879bps`, `2026-04 ≈ -3.860bps`

也就是说，这条线不是“总体可留，只是被单月拖累”；而是 strongest-only 版本在可见月份里都没能越过统一 `4bps roundtrip` 成本门槛。

## Conclusion
`peer-return spillover × laggard catch-up basket` 的 fresh intake first verdict 已诚实收口：公开 probe 虽保留了 `15m top1` 约 `+0.21~+0.22bps/bar` 的薄 gross spillover 方向感，但 strongest-only、quote-volume 加权与更宽 basket 在统一 `4bps roundtrip` 后全部稳定转成约 `-3.78~-4.05bps/bar`，且 `15m` 可见月份切片无一为正、`5m` 更接近零厚度。这说明它当前更像可服务其他横截面策略的 `shared spillover feature / router score`，而不是值得前排保留的 standalone after-cost alpha；本轮直接收口 `background/P0`。
