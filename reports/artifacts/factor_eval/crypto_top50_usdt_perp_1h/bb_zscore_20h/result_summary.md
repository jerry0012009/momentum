# Factor Evaluation: `bb_zscore_20h`

- universe: `crypto_top50_usdt_perp_1h`
- evaluation_period: `2025-12-15 09:00:00+00:00 ~ 2026-06-13 08:00:00+00:00`
- generated_at: `2026-06-13T12:20:27Z`
- caveat: Static current Top50 diagnostic universe; debug and initial screening only.
- excluded_symbols (missing_bar_rate > 5%): ['SPACEUSDT']

| label | direction | IC_mean | ICIR | RankIC_mean | RankICIR | raw_spread | raw_spread_t | dir_adj_spread | dir_adj_t | turnover | coverage | n_ts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ret_fwd_1h | negative | 0.004508 | 0.019717 | -0.018719 | -0.099459 | 0.000415 | 2.707575 | -0.000415 | -2.707575 | 0.294756 | 0.995602 | 4300 |
| ret_fwd_4h | negative | 0.006658 | 0.028868 | -0.020366 | -0.106457 | 0.001556 | 4.894199 | -0.001556 | -4.894199 | 0.294826 | 0.995602 | 4297 |
| ret_fwd_24h | negative | 0.016142 | 0.073852 | -0.005676 | -0.028756 | 0.006892 | 8.451591 | -0.006892 | -8.451591 | 0.294535 | 0.995602 | 4277 |
| ret_fwd_72h | negative | 0.013084 | 0.060492 | 0.007260 | 0.039551 | 0.008392 | 5.422941 | -0.008392 | -5.422941 | 0.294578 | 0.995602 | 4229 |

This is factor evaluation, not strategy PnL.
