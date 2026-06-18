# Crypto Top50 Factor Library — Result Summary (crypto_top50_usdt_perp_1h_crypto_native_v1)

- universe: `crypto_top50_usdt_perp_1h_crypto_native_v1`
- evaluation_period: `2025-12-15 09:00:00+00:00 ~ 2026-06-13 08:00:00+00:00`
- generated_at: `2026-06-14T19:33:01Z`
- caveat: Static current Top50 diagnostic universe; debug and initial screening only.
- excluded_symbols (missing_bar_rate > 5%): ['SPACEUSDT']
- timestamp_convention: timestamp = bar_close_time; factor known_at = bar_close_time
- label_convention: calendar-time forward returns (no row-shift across gaps)

| factor | label | direction | IC_mean | ICIR | RankIC_mean | RankICIR | raw_spread | raw_spread_t | dir_adj_spread | dir_adj_t | turnover | coverage | n_ts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| taker_buy_ratio_20h | ret_fwd_1h | positive | -0.005954 | -0.038639 | -0.012390 | -0.081023 | -0.000112 | -0.976821 | -0.000112 | -0.976821 | 0.146941 | 0.754861 | 3261 |
| taker_buy_ratio_20h | ret_fwd_4h | positive | -0.013003 | -0.084243 | -0.017818 | -0.114687 | -0.000465 | -1.712160 | -0.000465 | -1.712160 | 0.146941 | 0.754861 | 3261 |
| taker_buy_ratio_20h | ret_fwd_24h | positive | -0.022766 | -0.139124 | -0.021708 | -0.133766 | -0.002344 | -3.479450 | -0.002344 | -3.479450 | 0.146941 | 0.754861 | 3261 |
| taker_buy_ratio_20h | ret_fwd_72h | positive | -0.010236 | -0.060215 | 0.001234 | 0.007649 | 0.001891 | 1.782025 | 0.001891 | 1.782025 | 0.146941 | 0.754861 | 3261 |
| taker_buy_zscore_20h | ret_fwd_1h | positive | -0.001528 | -0.009640 | -0.008379 | -0.052458 | -0.000037 | -0.313988 | -0.000037 | -0.313988 | 0.771258 | 0.754861 | 3261 |
| taker_buy_zscore_20h | ret_fwd_4h | positive | -0.001531 | -0.009591 | -0.007474 | -0.046130 | -0.000011 | -0.042771 | -0.000011 | -0.042771 | 0.771258 | 0.754861 | 3261 |
| taker_buy_zscore_20h | ret_fwd_24h | positive | -0.002739 | -0.017283 | -0.003588 | -0.022818 | -0.000482 | -0.800379 | -0.000482 | -0.800379 | 0.771258 | 0.754861 | 3261 |
| taker_buy_zscore_20h | ret_fwd_72h | positive | -0.001668 | -0.010262 | -0.002125 | -0.013755 | -0.000514 | -0.505996 | -0.000514 | -0.505996 | 0.771258 | 0.754861 | 3261 |
| taker_buy_delta_5h | ret_fwd_1h | positive | -0.001101 | -0.007988 | -0.006149 | -0.039860 | 0.000061 | 0.674979 | 0.000061 | 0.674979 | 0.759586 | 0.758102 | 3275 |
| taker_buy_delta_5h | ret_fwd_4h | positive | -0.002225 | -0.016079 | -0.007212 | -0.047228 | 0.000020 | 0.111054 | 0.000020 | 0.111054 | 0.759586 | 0.758102 | 3275 |
| taker_buy_delta_5h | ret_fwd_24h | positive | -0.001352 | -0.009439 | -0.004054 | -0.026645 | -0.000309 | -0.614827 | -0.000309 | -0.614827 | 0.759586 | 0.758102 | 3275 |
| taker_buy_delta_5h | ret_fwd_72h | positive | -0.001680 | -0.011198 | -0.003451 | -0.022777 | -0.000577 | -0.650191 | -0.000577 | -0.650191 | 0.759586 | 0.758102 | 3275 |
| funding_rate_level_20h | ret_fwd_1h | negative | 0.003527 | 0.012049 | -0.005023 | -0.028413 | 0.000292 | 1.944402 | -0.000292 | -1.944402 | 0.040452 | 0.739153 | 3261 |
| funding_rate_level_20h | ret_fwd_4h | negative | 0.008837 | 0.029866 | -0.002762 | -0.015645 | 0.001285 | 3.931028 | -0.001285 | -3.931028 | 0.040452 | 0.739153 | 3261 |
| funding_rate_level_20h | ret_fwd_24h | negative | 0.033670 | 0.112461 | 0.015948 | 0.090055 | 0.005347 | 7.977177 | -0.005347 | -7.977177 | 0.040452 | 0.739153 | 3261 |
| funding_rate_level_20h | ret_fwd_72h | negative | 0.055458 | 0.212460 | 0.021671 | 0.120969 | 0.019763 | 17.553884 | -0.019763 | -17.553884 | 0.040452 | 0.739153 | 3261 |
| funding_rate_zscore_80h | ret_fwd_1h | negative | 0.001293 | 0.007104 | 0.000131 | 0.000779 | -0.000033 | -0.252191 | 0.000033 | 0.252191 | 0.115561 | 0.666553 | 3201 |
| funding_rate_zscore_80h | ret_fwd_4h | negative | 0.004494 | 0.024462 | 0.000956 | 0.005702 | 0.000344 | 1.215220 | -0.000344 | -1.215220 | 0.115561 | 0.666553 | 3201 |
| funding_rate_zscore_80h | ret_fwd_24h | negative | 0.008199 | 0.045290 | -0.001915 | -0.011021 | 0.000438 | 0.837024 | -0.000438 | -0.837024 | 0.115561 | 0.666553 | 3201 |
| funding_rate_zscore_80h | ret_fwd_72h | negative | -0.001527 | -0.008948 | -0.013401 | -0.081283 | -0.000441 | -0.463720 | 0.000441 | 0.463720 | 0.115561 | 0.666553 | 3201 |
| funding_rate_change_24h | ret_fwd_1h | negative | -0.004158 | -0.014492 | -0.000265 | -0.001655 | -0.000071 | -0.491206 | 0.000071 | 0.491206 | 0.125351 | 0.738256 | 3256 |
| funding_rate_change_24h | ret_fwd_4h | negative | 0.000202 | 0.000698 | 0.000199 | 0.001252 | 0.000164 | 0.526814 | -0.000164 | -0.526814 | 0.125351 | 0.738256 | 3256 |
| funding_rate_change_24h | ret_fwd_24h | negative | 0.023928 | 0.081873 | 0.005486 | 0.032010 | 0.002210 | 3.330703 | -0.002210 | -3.330703 | 0.125351 | 0.738256 | 3256 |
| funding_rate_change_24h | ret_fwd_72h | negative | 0.001088 | 0.003950 | -0.004023 | -0.024544 | 0.001883 | 1.728812 | -0.001883 | -1.728812 | 0.125351 | 0.738256 | 3256 |

Next: inspect NaN, timestamp alignment, and IC signs before V1.
