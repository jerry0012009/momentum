# Factor Evaluation: `volatility_20h`

- universe: `crypto_top50_usdt_perp_1h`
- evaluation_period: `2025-12-15 09:00:00+00:00 ~ 2026-06-13 08:00:00+00:00`
- generated_at: `2026-06-13T08:37:03Z`
- caveat: Static current Top50 diagnostic universe; debug and initial screening only.
- excluded_symbols (missing_bar_rate > 5%): ['SPACEUSDT']

| label | direction | IC_mean | ICIR | RankIC_mean | RankICIR | raw_spread | raw_spread_t | dir_adj_spread | dir_adj_t | turnover | coverage | n_ts |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ret_fwd_1h | negative | 0.004792 | 0.012671 | -0.016717 | -0.084511 | 0.000706 | 4.235828 | -0.000706 | -4.235828 | 0.059551 | 0.995370 | 4299 |
| ret_fwd_4h | negative | 0.015121 | 0.040835 | -0.019965 | -0.102663 | 0.003085 | 8.967944 | -0.003085 | -8.967944 | 0.059580 | 0.995370 | 4296 |
| ret_fwd_24h | negative | 0.029351 | 0.081632 | -0.015317 | -0.075673 | 0.017359 | 19.171337 | -0.017359 | -19.171337 | 0.059622 | 0.995370 | 4276 |
| ret_fwd_72h | negative | 0.058967 | 0.184306 | -0.009959 | -0.051245 | 0.044270 | 26.373004 | -0.044270 | -26.373004 | 0.059889 | 0.995370 | 4228 |

This is factor evaluation, not strategy PnL.
