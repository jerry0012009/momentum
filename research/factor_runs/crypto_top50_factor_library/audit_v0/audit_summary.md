# V0 Factor Audit Summary

- generated_at: 2026-06-12T14:33:31Z
- universe: crypto_top50_usdt_perp_1h
- evaluation_period: 2025-12-14 ~ 2026-06-12

## A. IC Sign Consistency

| factor | label | IC_sign | RankIC_sign | spread_sign | consistent | notes |
|---|---|---:|---:|---:|---:|---|
| mom_20h | ret_fwd_1h | + | - | + | ✗ | IC↔RankIC conflict |
| mom_20h | ret_fwd_4h | - | - | + | ✗ | IC↔spread conflict |
| mom_20h | ret_fwd_24h | + | - | + | ✗ | IC↔RankIC conflict |
| mom_20h | ret_fwd_72h | + | + | + | ✓ | OK |
| reversal_5h | ret_fwd_1h | - | + | - | ✗ | IC↔RankIC conflict |
| reversal_5h | ret_fwd_4h | - | + | - | ✗ | IC↔RankIC conflict |
| reversal_5h | ret_fwd_24h | + | + | - | ✗ | IC↔spread conflict |
| reversal_5h | ret_fwd_72h | - | - | - | ✓ | OK |
| volatility_20h | ret_fwd_1h | + | - | + | ✗ | IC↔RankIC conflict |
| volatility_20h | ret_fwd_4h | + | - | + | ✗ | IC↔RankIC conflict |
| volatility_20h | ret_fwd_24h | + | - | + | ✗ | IC↔RankIC conflict |
| volatility_20h | ret_fwd_72h | + | - | + | ✗ | IC↔RankIC conflict |
| rsi_14h | ret_fwd_1h | + | - | + | ✗ | IC↔RankIC conflict |
| rsi_14h | ret_fwd_4h | + | - | + | ✗ | IC↔RankIC conflict |
| rsi_14h | ret_fwd_24h | + | - | + | ✗ | IC↔RankIC conflict |
| rsi_14h | ret_fwd_72h | + | + | + | ✓ | OK |
| bb_zscore_20h | ret_fwd_1h | + | - | + | ✗ | IC↔RankIC conflict |
| bb_zscore_20h | ret_fwd_4h | + | - | + | ✗ | IC↔RankIC conflict |
| bb_zscore_20h | ret_fwd_24h | + | - | + | ✗ | IC↔RankIC conflict |
| bb_zscore_20h | ret_fwd_72h | + | + | + | ✓ | OK |

**Conflicts:** 16 / 20 pairs

- mom_20h × ret_fwd_1h: IC↔RankIC conflict
- mom_20h × ret_fwd_4h: IC↔spread conflict
- mom_20h × ret_fwd_24h: IC↔RankIC conflict
- reversal_5h × ret_fwd_1h: IC↔RankIC conflict
- reversal_5h × ret_fwd_4h: IC↔RankIC conflict
- reversal_5h × ret_fwd_24h: IC↔spread conflict
- volatility_20h × ret_fwd_1h: IC↔RankIC conflict
- volatility_20h × ret_fwd_4h: IC↔RankIC conflict
- volatility_20h × ret_fwd_24h: IC↔RankIC conflict
- volatility_20h × ret_fwd_72h: IC↔RankIC conflict
- rsi_14h × ret_fwd_1h: IC↔RankIC conflict
- rsi_14h × ret_fwd_4h: IC↔RankIC conflict
- rsi_14h × ret_fwd_24h: IC↔RankIC conflict
- bb_zscore_20h × ret_fwd_1h: IC↔RankIC conflict
- bb_zscore_20h × ret_fwd_4h: IC↔RankIC conflict
- bb_zscore_20h × ret_fwd_24h: IC↔RankIC conflict

## B. Monthly Stability

### mom_20h

| label | month | IC | RankIC | spread_t | n_ts |
|---|---|---:|---:|---:|---:|
| ret_fwd_1h | 2025-12 | 0.0033 | -0.0296 | 0.67 | 399 |
| ret_fwd_1h | 2026-01 | -0.0216 | -0.0362 | -1.15 | 744 |
| ret_fwd_1h | 2026-02 | -0.0119 | -0.0108 | 0.07 | 672 |
| ret_fwd_1h | 2026-03 | 0.0278 | -0.0149 | 1.14 | 744 |
| ret_fwd_1h | 2026-04 | -0.0054 | -0.0248 | -0.56 | 720 |
| ret_fwd_1h | 2026-05 | 0.0138 | -0.0012 | 0.93 | 744 |
| ret_fwd_1h | 2026-06 | 0.0405 | 0.0462 | 3.48 | 276 |
| ret_fwd_4h | 2025-12 | -0.0102 | -0.0578 | 0.29 | 399 |
| ret_fwd_4h | 2026-01 | -0.0251 | -0.0423 | -1.39 | 744 |
| ret_fwd_4h | 2026-02 | -0.0322 | -0.0231 | -0.36 | 672 |
| ret_fwd_4h | 2026-03 | 0.0301 | -0.0265 | 2.76 | 744 |
| ret_fwd_4h | 2026-04 | -0.0102 | -0.0415 | 0.10 | 720 |
| ret_fwd_4h | 2026-05 | 0.0041 | 0.0075 | 1.75 | 744 |
| ret_fwd_4h | 2026-06 | 0.0616 | 0.0830 | 7.10 | 273 |
| ret_fwd_24h | 2025-12 | -0.0229 | -0.0425 | 1.33 | 399 |
| ret_fwd_24h | 2026-01 | -0.0111 | -0.0397 | 0.42 | 744 |
| ret_fwd_24h | 2026-02 | -0.0504 | -0.0315 | -1.37 | 672 |
| ret_fwd_24h | 2026-03 | -0.0160 | -0.0081 | 1.19 | 744 |
| ret_fwd_24h | 2026-04 | 0.0120 | -0.0523 | 0.51 | 720 |
| ret_fwd_24h | 2026-05 | 0.0278 | 0.0456 | 7.70 | 744 |
| ret_fwd_24h | 2026-06 | 0.1704 | 0.1662 | 14.42 | 253 |
| ret_fwd_72h | 2025-12 | 0.0059 | -0.0106 | 0.48 | 399 |
| ret_fwd_72h | 2026-01 | 0.0551 | 0.0428 | 6.18 | 744 |
| ret_fwd_72h | 2026-02 | -0.0170 | -0.0262 | 1.70 | 672 |
| ret_fwd_72h | 2026-03 | -0.0390 | -0.0190 | -3.40 | 744 |
| ret_fwd_72h | 2026-04 | -0.0705 | -0.0107 | -5.37 | 720 |
| ret_fwd_72h | 2026-05 | 0.0346 | 0.0759 | 6.08 | 744 |
| ret_fwd_72h | 2026-06 | 0.1584 | 0.0513 | 16.13 | 205 |

### reversal_5h

| label | month | IC | RankIC | spread_t | n_ts |
|---|---|---:|---:|---:|---:|
| ret_fwd_1h | 2025-12 | -0.0227 | 0.0350 | -0.01 | 414 |
| ret_fwd_1h | 2026-01 | 0.0095 | 0.0315 | -0.02 | 744 |
| ret_fwd_1h | 2026-02 | 0.0013 | 0.0123 | -1.12 | 672 |
| ret_fwd_1h | 2026-03 | -0.0262 | 0.0200 | -0.73 | 744 |
| ret_fwd_1h | 2026-04 | 0.0117 | 0.0280 | 0.62 | 720 |
| ret_fwd_1h | 2026-05 | -0.0066 | 0.0251 | -0.46 | 744 |
| ret_fwd_1h | 2026-06 | -0.0362 | 0.0178 | -0.67 | 276 |
| ret_fwd_4h | 2025-12 | -0.0337 | 0.0405 | -0.63 | 414 |
| ret_fwd_4h | 2026-01 | 0.0112 | 0.0193 | -0.41 | 744 |
| ret_fwd_4h | 2026-02 | 0.0104 | 0.0036 | -1.09 | 672 |
| ret_fwd_4h | 2026-03 | -0.0254 | 0.0355 | -1.30 | 744 |
| ret_fwd_4h | 2026-04 | 0.0337 | 0.0373 | 1.18 | 720 |
| ret_fwd_4h | 2026-05 | -0.0239 | 0.0208 | -2.18 | 744 |
| ret_fwd_4h | 2026-06 | -0.0528 | 0.0015 | -3.49 | 273 |
| ret_fwd_24h | 2025-12 | -0.0150 | 0.0250 | -1.66 | 414 |
| ret_fwd_24h | 2026-01 | 0.0197 | 0.0257 | -0.38 | 744 |
| ret_fwd_24h | 2026-02 | 0.0485 | 0.0322 | 1.46 | 672 |
| ret_fwd_24h | 2026-03 | -0.0196 | 0.0152 | -2.01 | 744 |
| ret_fwd_24h | 2026-04 | 0.0097 | 0.0504 | 2.83 | 720 |
| ret_fwd_24h | 2026-05 | -0.0126 | -0.0146 | -3.74 | 744 |
| ret_fwd_24h | 2026-06 | -0.0668 | -0.0829 | -6.47 | 253 |
| ret_fwd_72h | 2025-12 | -0.0089 | 0.0109 | 1.02 | 414 |
| ret_fwd_72h | 2026-01 | -0.0164 | -0.0161 | -2.44 | 744 |
| ret_fwd_72h | 2026-02 | 0.0205 | 0.0156 | -0.69 | 672 |
| ret_fwd_72h | 2026-03 | 0.0010 | 0.0180 | 1.27 | 744 |
| ret_fwd_72h | 2026-04 | 0.0293 | 0.0176 | 3.14 | 720 |
| ret_fwd_72h | 2026-05 | -0.0211 | -0.0293 | -4.75 | 744 |
| ret_fwd_72h | 2026-06 | -0.0938 | -0.0438 | -6.35 | 205 |

### volatility_20h

| label | month | IC | RankIC | spread_t | n_ts |
|---|---|---:|---:|---:|---:|
| ret_fwd_1h | 2025-12 | -0.0046 | -0.0164 | 0.75 | 399 |
| ret_fwd_1h | 2026-01 | -0.0260 | -0.0313 | -2.07 | 744 |
| ret_fwd_1h | 2026-02 | -0.0110 | -0.0130 | 1.02 | 672 |
| ret_fwd_1h | 2026-03 | 0.0297 | -0.0192 | 2.29 | 744 |
| ret_fwd_1h | 2026-04 | 0.0137 | -0.0199 | 2.66 | 720 |
| ret_fwd_1h | 2026-05 | 0.0159 | -0.0131 | 2.60 | 744 |
| ret_fwd_1h | 2026-06 | 0.0325 | 0.0184 | 2.93 | 276 |
| ret_fwd_4h | 2025-12 | 0.0023 | -0.0108 | 2.36 | 399 |
| ret_fwd_4h | 2026-01 | -0.0542 | -0.0509 | -3.63 | 744 |
| ret_fwd_4h | 2026-02 | 0.0013 | -0.0144 | 2.68 | 672 |
| ret_fwd_4h | 2026-03 | 0.0509 | -0.0248 | 3.73 | 744 |
| ret_fwd_4h | 2026-04 | 0.0261 | -0.0234 | 4.91 | 720 |
| ret_fwd_4h | 2026-05 | 0.0419 | -0.0104 | 5.64 | 744 |
| ret_fwd_4h | 2026-06 | 0.0856 | 0.0467 | 6.08 | 273 |
| ret_fwd_24h | 2025-12 | -0.0229 | -0.0169 | 4.71 | 399 |
| ret_fwd_24h | 2026-01 | -0.1174 | -0.0958 | -9.17 | 744 |
| ret_fwd_24h | 2026-02 | 0.0043 | -0.0148 | 4.78 | 672 |
| ret_fwd_24h | 2026-03 | 0.0654 | -0.0135 | 6.64 | 744 |
| ret_fwd_24h | 2026-04 | 0.0782 | -0.0047 | 12.35 | 720 |
| ret_fwd_24h | 2026-05 | 0.0842 | -0.0032 | 12.28 | 744 |
| ret_fwd_24h | 2026-06 | 0.1216 | 0.1099 | 10.08 | 253 |
| ret_fwd_72h | 2025-12 | -0.0487 | 0.0008 | 4.29 | 399 |
| ret_fwd_72h | 2026-01 | -0.1894 | -0.1487 | -18.08 | 744 |
| ret_fwd_72h | 2026-02 | 0.0471 | -0.0187 | 9.74 | 672 |
| ret_fwd_72h | 2026-03 | 0.0621 | -0.0101 | 6.69 | 744 |
| ret_fwd_72h | 2026-04 | 0.1817 | 0.0509 | 23.56 | 720 |
| ret_fwd_72h | 2026-05 | 0.1279 | 0.0085 | 16.50 | 744 |
| ret_fwd_72h | 2026-06 | 0.1291 | 0.0613 | 13.99 | 205 |

### rsi_14h

| label | month | IC | RankIC | spread_t | n_ts |
|---|---|---:|---:|---:|---:|
| ret_fwd_1h | 2025-12 | 0.0092 | -0.0272 | 1.23 | 405 |
| ret_fwd_1h | 2026-01 | -0.0111 | -0.0318 | -0.48 | 744 |
| ret_fwd_1h | 2026-02 | 0.0068 | -0.0047 | 0.69 | 672 |
| ret_fwd_1h | 2026-03 | 0.0122 | -0.0172 | 0.82 | 744 |
| ret_fwd_1h | 2026-04 | 0.0010 | -0.0231 | 0.24 | 720 |
| ret_fwd_1h | 2026-05 | 0.0219 | 0.0030 | 2.36 | 744 |
| ret_fwd_1h | 2026-06 | 0.0534 | 0.0338 | 3.19 | 276 |
| ret_fwd_4h | 2025-12 | 0.0027 | -0.0510 | 0.03 | 405 |
| ret_fwd_4h | 2026-01 | -0.0123 | -0.0341 | -0.15 | 744 |
| ret_fwd_4h | 2026-02 | 0.0048 | -0.0102 | -0.25 | 672 |
| ret_fwd_4h | 2026-03 | 0.0124 | -0.0242 | 1.28 | 744 |
| ret_fwd_4h | 2026-04 | -0.0101 | -0.0306 | 0.57 | 720 |
| ret_fwd_4h | 2026-05 | 0.0404 | 0.0210 | 4.51 | 744 |
| ret_fwd_4h | 2026-06 | 0.0980 | 0.0591 | 6.23 | 273 |
| ret_fwd_24h | 2025-12 | 0.0020 | -0.0237 | 1.15 | 405 |
| ret_fwd_24h | 2026-01 | -0.0050 | -0.0327 | 1.70 | 744 |
| ret_fwd_24h | 2026-02 | -0.0004 | -0.0303 | -1.61 | 672 |
| ret_fwd_24h | 2026-03 | 0.0046 | -0.0149 | 0.08 | 744 |
| ret_fwd_24h | 2026-04 | -0.0050 | -0.0328 | -1.13 | 720 |
| ret_fwd_24h | 2026-05 | 0.0670 | 0.0696 | 10.20 | 744 |
| ret_fwd_24h | 2026-06 | 0.1946 | 0.1331 | 13.85 | 253 |
| ret_fwd_72h | 2025-12 | -0.0134 | -0.0222 | -2.77 | 405 |
| ret_fwd_72h | 2026-01 | 0.0861 | 0.0612 | 9.68 | 744 |
| ret_fwd_72h | 2026-02 | 0.0138 | -0.0122 | 1.92 | 672 |
| ret_fwd_72h | 2026-03 | -0.0153 | -0.0266 | -0.78 | 744 |
| ret_fwd_72h | 2026-04 | -0.0459 | -0.0044 | -6.26 | 720 |
| ret_fwd_72h | 2026-05 | 0.0680 | 0.0975 | 8.81 | 744 |
| ret_fwd_72h | 2026-06 | 0.2300 | 0.0383 | 14.14 | 205 |

### bb_zscore_20h

| label | month | IC | RankIC | spread_t | n_ts |
|---|---|---:|---:|---:|---:|
| ret_fwd_1h | 2025-12 | 0.0091 | -0.0263 | 0.59 | 400 |
| ret_fwd_1h | 2026-01 | -0.0152 | -0.0327 | -1.03 | 744 |
| ret_fwd_1h | 2026-02 | 0.0017 | -0.0112 | 0.95 | 672 |
| ret_fwd_1h | 2026-03 | 0.0046 | -0.0210 | 1.05 | 744 |
| ret_fwd_1h | 2026-04 | -0.0050 | -0.0273 | 0.11 | 720 |
| ret_fwd_1h | 2026-05 | 0.0128 | -0.0088 | 1.59 | 744 |
| ret_fwd_1h | 2026-06 | 0.0447 | 0.0170 | 2.53 | 276 |
| ret_fwd_4h | 2025-12 | -0.0011 | -0.0554 | 0.04 | 400 |
| ret_fwd_4h | 2026-01 | -0.0159 | -0.0302 | -0.63 | 744 |
| ret_fwd_4h | 2026-02 | 0.0004 | -0.0121 | 0.57 | 672 |
| ret_fwd_4h | 2026-03 | 0.0060 | -0.0294 | 2.53 | 744 |
| ret_fwd_4h | 2026-04 | -0.0128 | -0.0338 | -0.06 | 720 |
| ret_fwd_4h | 2026-05 | 0.0278 | 0.0038 | 3.75 | 744 |
| ret_fwd_4h | 2026-06 | 0.0780 | 0.0379 | 5.16 | 273 |
| ret_fwd_24h | 2025-12 | 0.0018 | -0.0362 | 0.75 | 400 |
| ret_fwd_24h | 2026-01 | -0.0167 | -0.0313 | 0.02 | 744 |
| ret_fwd_24h | 2026-02 | -0.0067 | -0.0202 | -1.64 | 672 |
| ret_fwd_24h | 2026-03 | 0.0134 | -0.0195 | 2.39 | 744 |
| ret_fwd_24h | 2026-04 | -0.0198 | -0.0408 | -2.14 | 720 |
| ret_fwd_24h | 2026-05 | 0.0519 | 0.0497 | 7.51 | 744 |
| ret_fwd_24h | 2026-06 | 0.1679 | 0.1221 | 10.30 | 253 |
| ret_fwd_72h | 2025-12 | -0.0106 | -0.0279 | -2.84 | 400 |
| ret_fwd_72h | 2026-01 | 0.0214 | 0.0266 | 2.77 | 744 |
| ret_fwd_72h | 2026-02 | -0.0055 | -0.0166 | 1.18 | 672 |
| ret_fwd_72h | 2026-03 | -0.0148 | -0.0252 | -2.41 | 744 |
| ret_fwd_72h | 2026-04 | -0.0274 | -0.0161 | -4.55 | 720 |
| ret_fwd_72h | 2026-05 | 0.0453 | 0.0644 | 6.18 | 744 |
| ret_fwd_72h | 2026-06 | 0.1879 | 0.0737 | 9.91 | 205 |

### Monthly direction consistency

| factor | label | months | consistent | ratio |
|---|---|---:|---:|---:|
| mom_20h | ret_fwd_1h | 7 | 4 | 0.57 |
| mom_20h | ret_fwd_4h | 7 | 4 | 0.57 |
| mom_20h | ret_fwd_24h | 7 | 4 | 0.57 |
| mom_20h | ret_fwd_72h | 7 | 4 | 0.57 |
| reversal_5h | ret_fwd_1h | 7 | 4 | 0.57 |
| reversal_5h | ret_fwd_4h | 7 | 4 | 0.57 |
| reversal_5h | ret_fwd_24h | 7 | 4 | 0.57 |
| reversal_5h | ret_fwd_72h | 7 | 4 | 0.57 |
| volatility_20h | ret_fwd_1h | 7 | 4 | 0.57 |
| volatility_20h | ret_fwd_4h | 7 | 6 | 0.86 |
| volatility_20h | ret_fwd_24h | 7 | 5 | 0.71 |
| volatility_20h | ret_fwd_72h | 7 | 5 | 0.71 |
| rsi_14h | ret_fwd_1h | 7 | 6 | 0.86 |
| rsi_14h | ret_fwd_4h | 7 | 5 | 0.71 |
| rsi_14h | ret_fwd_24h | 7 | 4 | 0.57 |
| rsi_14h | ret_fwd_72h | 7 | 4 | 0.57 |
| bb_zscore_20h | ret_fwd_1h | 7 | 5 | 0.71 |
| bb_zscore_20h | ret_fwd_4h | 7 | 4 | 0.57 |
| bb_zscore_20h | ret_fwd_24h | 7 | 4 | 0.57 |
| bb_zscore_20h | ret_fwd_72h | 7 | 4 | 0.57 |

## C. Non-Overlap Labels Audit

| factor | label | mode | IC_mean | RankIC_mean | spread_t | n_ts |
|---|---|---|---:|---:|---:|---:|
| mom_20h | ret_fwd_24h | full | 0.0022 | -0.0083 | 10.49 | 4276 |
| mom_20h | ret_fwd_24h | nonoverlap | 0.0112 | -0.0135 | 2.91 | 178 |
| mom_20h | ret_fwd_72h | full | 0.0025 | 0.0130 | 7.87 | 4228 |
| mom_20h | ret_fwd_72h | nonoverlap | 0.0154 | 0.0350 | 1.98 | 57 |
| reversal_5h | ret_fwd_24h | full | 0.0017 | 0.0156 | -4.66 | 4291 |
| reversal_5h | ret_fwd_24h | nonoverlap | -0.0173 | 0.0045 | -1.03 | 179 |
| reversal_5h | ret_fwd_72h | full | -0.0036 | -0.0004 | -4.60 | 4243 |
| reversal_5h | ret_fwd_72h | nonoverlap | -0.0219 | -0.0172 | -1.19 | 58 |
| volatility_20h | ret_fwd_24h | full | 0.0245 | -0.0178 | 18.73 | 4276 |
| volatility_20h | ret_fwd_24h | nonoverlap | 0.0160 | -0.0146 | 3.48 | 178 |
| volatility_20h | ret_fwd_72h | full | 0.0402 | -0.0177 | 25.11 | 4228 |
| volatility_20h | ret_fwd_72h | nonoverlap | 0.0468 | -0.0103 | 2.72 | 57 |
| rsi_14h | ret_fwd_24h | full | 0.0224 | -0.0008 | 10.33 | 4282 |
| rsi_14h | ret_fwd_24h | nonoverlap | 0.0284 | 0.0014 | 1.38 | 178 |
| rsi_14h | ret_fwd_72h | full | 0.0286 | 0.0203 | 9.43 | 4234 |
| rsi_14h | ret_fwd_72h | nonoverlap | 0.0415 | 0.0296 | 1.35 | 57 |
| bb_zscore_20h | ret_fwd_24h | full | 0.0142 | -0.0064 | 8.17 | 4277 |
| bb_zscore_20h | ret_fwd_24h | nonoverlap | 0.0242 | -0.0021 | 1.66 | 178 |
| bb_zscore_20h | ret_fwd_72h | full | 0.0117 | 0.0071 | 5.78 | 4229 |
| bb_zscore_20h | ret_fwd_72h | nonoverlap | 0.0404 | 0.0290 | 1.47 | 57 |

**Interpretation:** If spread_t drops significantly in nonoverlap mode, the
original t-stat was inflated by overlapping samples.

## D. Outlier Robustness (Winsorize)

| factor | label | version | IC_mean | RankIC_mean | spread_t |
|---|---|---|---:|---:|---:|
| mom_20h | ret_fwd_1h | raw | 0.0036 | -0.0147 | 2.12 |
| mom_20h | ret_fwd_1h | factor_w199 | 0.0037 | -0.0147 | 2.12 |
| mom_20h | ret_fwd_1h | both_w199 | 0.0063 | -0.0146 | 3.09 |
| mom_20h | ret_fwd_1h | factor_w595 | 0.0028 | -0.0147 | 2.27 |
| mom_20h | ret_fwd_1h | both_w595 | -0.0018 | -0.0133 | 0.40 |
| mom_20h | ret_fwd_4h | raw | -0.0022 | -0.0213 | 4.30 |
| mom_20h | ret_fwd_4h | factor_w199 | -0.0003 | -0.0213 | 4.29 |
| mom_20h | ret_fwd_4h | both_w199 | 0.0007 | -0.0212 | 3.95 |
| mom_20h | ret_fwd_4h | factor_w595 | 0.0028 | -0.0212 | 4.47 |
| mom_20h | ret_fwd_4h | both_w595 | -0.0052 | -0.0202 | 0.17 |
| mom_20h | ret_fwd_24h | raw | 0.0022 | -0.0083 | 10.49 |
| mom_20h | ret_fwd_24h | factor_w199 | 0.0139 | -0.0083 | 10.48 |
| mom_20h | ret_fwd_24h | both_w199 | 0.0186 | -0.0083 | 11.35 |
| mom_20h | ret_fwd_24h | factor_w595 | 0.0208 | -0.0078 | 10.47 |
| mom_20h | ret_fwd_24h | both_w595 | 0.0144 | -0.0075 | 5.63 |
| mom_20h | ret_fwd_72h | raw | 0.0025 | 0.0130 | 7.87 |
| mom_20h | ret_fwd_72h | factor_w199 | 0.0170 | 0.0130 | 7.86 |
| mom_20h | ret_fwd_72h | both_w199 | 0.0192 | 0.0131 | 8.91 |
| mom_20h | ret_fwd_72h | factor_w595 | 0.0210 | 0.0138 | 7.86 |
| mom_20h | ret_fwd_72h | both_w595 | 0.0204 | 0.0151 | 6.95 |
| reversal_5h | ret_fwd_1h | raw | -0.0064 | 0.0243 | -0.95 |
| reversal_5h | ret_fwd_1h | factor_w199 | -0.0035 | 0.0243 | -0.94 |
| reversal_5h | ret_fwd_1h | both_w199 | 0.0001 | 0.0242 | -0.49 |
| reversal_5h | ret_fwd_1h | factor_w595 | -0.0035 | 0.0244 | -1.01 |
| reversal_5h | ret_fwd_1h | both_w595 | 0.0107 | 0.0256 | 3.24 |
| reversal_5h | ret_fwd_4h | raw | -0.0059 | 0.0238 | -3.23 |
| reversal_5h | ret_fwd_4h | factor_w199 | -0.0050 | 0.0238 | -3.22 |
| reversal_5h | ret_fwd_4h | both_w199 | -0.0011 | 0.0238 | -1.86 |
| reversal_5h | ret_fwd_4h | factor_w595 | -0.0049 | 0.0240 | -3.08 |
| reversal_5h | ret_fwd_4h | both_w595 | 0.0086 | 0.0252 | 2.44 |
| reversal_5h | ret_fwd_24h | raw | 0.0017 | 0.0156 | -4.66 |
| reversal_5h | ret_fwd_24h | factor_w199 | -0.0016 | 0.0155 | -4.67 |
| reversal_5h | ret_fwd_24h | both_w199 | -0.0046 | 0.0156 | -4.75 |
| reversal_5h | ret_fwd_24h | factor_w595 | -0.0046 | 0.0149 | -4.69 |
| reversal_5h | ret_fwd_24h | both_w595 | -0.0008 | 0.0151 | -1.26 |
| reversal_5h | ret_fwd_72h | raw | -0.0036 | -0.0004 | -4.60 |
| reversal_5h | ret_fwd_72h | factor_w199 | -0.0087 | -0.0004 | -4.60 |
| reversal_5h | ret_fwd_72h | both_w199 | -0.0089 | -0.0005 | -4.55 |
| reversal_5h | ret_fwd_72h | factor_w595 | -0.0098 | -0.0004 | -4.60 |
| reversal_5h | ret_fwd_72h | both_w595 | -0.0065 | -0.0005 | -2.21 |
| volatility_20h | ret_fwd_1h | raw | 0.0056 | -0.0167 | 4.63 |
| volatility_20h | ret_fwd_1h | factor_w199 | 0.0063 | -0.0167 | 4.63 |
| volatility_20h | ret_fwd_1h | both_w199 | 0.0102 | -0.0166 | 5.43 |
| volatility_20h | ret_fwd_1h | factor_w595 | 0.0088 | -0.0166 | 4.51 |
| volatility_20h | ret_fwd_1h | both_w595 | -0.0005 | -0.0145 | 0.42 |
| volatility_20h | ret_fwd_4h | raw | 0.0169 | -0.0191 | 9.46 |
| volatility_20h | ret_fwd_4h | factor_w199 | 0.0167 | -0.0192 | 9.46 |
| volatility_20h | ret_fwd_4h | both_w199 | 0.0219 | -0.0191 | 10.08 |
| volatility_20h | ret_fwd_4h | factor_w595 | 0.0206 | -0.0189 | 9.28 |
| volatility_20h | ret_fwd_4h | both_w595 | 0.0110 | -0.0164 | 4.38 |
| volatility_20h | ret_fwd_24h | raw | 0.0245 | -0.0178 | 18.73 |
| volatility_20h | ret_fwd_24h | factor_w199 | 0.0262 | -0.0178 | 18.73 |
| volatility_20h | ret_fwd_24h | both_w199 | 0.0353 | -0.0179 | 20.58 |
| volatility_20h | ret_fwd_24h | factor_w595 | 0.0386 | -0.0169 | 18.82 |
| volatility_20h | ret_fwd_24h | both_w595 | 0.0347 | -0.0139 | 13.58 |
| volatility_20h | ret_fwd_72h | raw | 0.0402 | -0.0177 | 25.11 |
| volatility_20h | ret_fwd_72h | factor_w199 | 0.0424 | -0.0178 | 25.11 |
| volatility_20h | ret_fwd_72h | both_w199 | 0.0518 | -0.0178 | 28.98 |
| volatility_20h | ret_fwd_72h | factor_w595 | 0.0566 | -0.0174 | 25.03 |
| volatility_20h | ret_fwd_72h | both_w595 | 0.0420 | -0.0138 | 18.73 |
| rsi_14h | ret_fwd_1h | raw | 0.0095 | -0.0129 | 3.35 |
| rsi_14h | ret_fwd_1h | factor_w199 | 0.0086 | -0.0130 | 3.36 |
| rsi_14h | ret_fwd_1h | both_w199 | 0.0093 | -0.0129 | 4.37 |
| rsi_14h | ret_fwd_1h | factor_w595 | 0.0073 | -0.0128 | 3.42 |
| rsi_14h | ret_fwd_1h | both_w595 | 0.0004 | -0.0116 | 1.32 |
| rsi_14h | ret_fwd_4h | raw | 0.0125 | -0.0142 | 5.01 |
| rsi_14h | ret_fwd_4h | factor_w199 | 0.0119 | -0.0144 | 5.02 |
| rsi_14h | ret_fwd_4h | both_w199 | 0.0121 | -0.0143 | 5.67 |
| rsi_14h | ret_fwd_4h | factor_w595 | 0.0116 | -0.0139 | 5.09 |
| rsi_14h | ret_fwd_4h | both_w595 | 0.0036 | -0.0123 | 1.89 |
| rsi_14h | ret_fwd_24h | raw | 0.0224 | -0.0008 | 10.33 |
| rsi_14h | ret_fwd_24h | factor_w199 | 0.0218 | -0.0009 | 10.36 |
| rsi_14h | ret_fwd_24h | both_w199 | 0.0275 | -0.0008 | 12.06 |
| rsi_14h | ret_fwd_24h | factor_w595 | 0.0218 | 0.0004 | 10.68 |
| rsi_14h | ret_fwd_24h | both_w595 | 0.0200 | 0.0012 | 7.41 |
| rsi_14h | ret_fwd_72h | raw | 0.0286 | 0.0203 | 9.43 |
| rsi_14h | ret_fwd_72h | factor_w199 | 0.0281 | 0.0202 | 9.42 |
| rsi_14h | ret_fwd_72h | both_w199 | 0.0278 | 0.0203 | 10.64 |
| rsi_14h | ret_fwd_72h | factor_w595 | 0.0263 | 0.0211 | 9.57 |
| rsi_14h | ret_fwd_72h | both_w595 | 0.0242 | 0.0229 | 8.44 |
| bb_zscore_20h | ret_fwd_1h | raw | 0.0035 | -0.0185 | 2.54 |
| bb_zscore_20h | ret_fwd_1h | factor_w199 | 0.0034 | -0.0184 | 2.55 |
| bb_zscore_20h | ret_fwd_1h | both_w199 | 0.0021 | -0.0183 | 2.49 |
| bb_zscore_20h | ret_fwd_1h | factor_w595 | 0.0027 | -0.0186 | 2.37 |
| bb_zscore_20h | ret_fwd_1h | both_w595 | -0.0072 | -0.0175 | -1.43 |
| bb_zscore_20h | ret_fwd_4h | raw | 0.0059 | -0.0200 | 4.71 |
| bb_zscore_20h | ret_fwd_4h | factor_w199 | 0.0058 | -0.0199 | 4.74 |
| bb_zscore_20h | ret_fwd_4h | both_w199 | 0.0039 | -0.0198 | 4.01 |
| bb_zscore_20h | ret_fwd_4h | factor_w595 | 0.0052 | -0.0198 | 4.75 |
| bb_zscore_20h | ret_fwd_4h | both_w595 | -0.0050 | -0.0189 | -0.24 |
| bb_zscore_20h | ret_fwd_24h | raw | 0.0142 | -0.0064 | 8.17 |
| bb_zscore_20h | ret_fwd_24h | factor_w199 | 0.0142 | -0.0064 | 8.13 |
| bb_zscore_20h | ret_fwd_24h | both_w199 | 0.0174 | -0.0064 | 9.17 |
| bb_zscore_20h | ret_fwd_24h | factor_w595 | 0.0137 | -0.0069 | 8.17 |
| bb_zscore_20h | ret_fwd_24h | both_w595 | 0.0084 | -0.0065 | 4.10 |
| bb_zscore_20h | ret_fwd_72h | raw | 0.0117 | 0.0071 | 5.78 |
| bb_zscore_20h | ret_fwd_72h | factor_w199 | 0.0114 | 0.0073 | 5.76 |
| bb_zscore_20h | ret_fwd_72h | both_w199 | 0.0110 | 0.0074 | 6.06 |
| bb_zscore_20h | ret_fwd_72h | factor_w595 | 0.0102 | 0.0073 | 5.81 |
| bb_zscore_20h | ret_fwd_72h | both_w595 | 0.0086 | 0.0087 | 4.04 |

**Focus:** If volatility_20h Pearson IC drops sharply after winsorize,
its signal depends on extreme returns.

## E. Symbol Contribution

### mom_20h × ret_fwd_1h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| LABUSDT | 0.001814 | 0.0330 | 1837 | 1427 | -0.002791 |
| BEATUSDT | 0.000658 | 0.0157 | 1823 | 1677 | 0.000357 |
| SKYAIUSDT | 0.000871 | 0.0173 | 1796 | 1438 | 0.000168 |
| SIRENUSDT | 0.001831 | 0.0376 | 1719 | 1308 | 0.002089 |
| HUSDT | 0.000714 | 0.0166 | 1709 | 1461 | 0.001840 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| PLAYUSDT | 0.000522 | 0.0119 | 1584 | 1765 | 0.000524 |
| BEATUSDT | 0.000658 | 0.0157 | 1823 | 1677 | 0.000357 |
| HUSDT | 0.000714 | 0.0166 | 1709 | 1461 | 0.001840 |
| ESPORTSUSDT | 0.000441 | 0.0085 | 1427 | 1456 | 0.000625 |
| SKYAIUSDT | 0.000871 | 0.0173 | 1796 | 1438 | 0.000168 |

### mom_20h × ret_fwd_24h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| LABUSDT | 0.039494 | 0.0323 | 1825 | 1427 | -0.009272 |
| BEATUSDT | 0.016208 | 0.0150 | 1814 | 1669 | 0.030843 |
| SKYAIUSDT | 0.020592 | 0.0154 | 1773 | 1438 | -0.012229 |
| SIRENUSDT | 0.045091 | 0.0387 | 1719 | 1285 | -0.018740 |
| HUSDT | 0.020461 | 0.0125 | 1686 | 1461 | 0.025143 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| PLAYUSDT | 0.014714 | 0.0134 | 1584 | 1742 | 0.012071 |
| BEATUSDT | 0.016208 | 0.0150 | 1814 | 1669 | 0.030843 |
| HUSDT | 0.020461 | 0.0125 | 1686 | 1461 | 0.025143 |
| ESPORTSUSDT | 0.009997 | 0.0042 | 1407 | 1456 | 0.027824 |
| SKYAIUSDT | 0.020592 | 0.0154 | 1773 | 1438 | -0.012229 |

### reversal_5h × ret_fwd_1h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| PLAYUSDT | 0.000516 | -0.0028 | 1768 | 1507 | 0.000307 |
| BEATUSDT | 0.000764 | -0.0040 | 1746 | 1773 | 0.000314 |
| HUSDT | 0.000714 | -0.0040 | 1540 | 1620 | -0.001792 |
| ESPORTSUSDT | 0.000432 | -0.0023 | 1500 | 1415 | -0.000061 |
| LABUSDT | 0.001809 | -0.0080 | 1499 | 1807 | 0.000766 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| LABUSDT | 0.001809 | -0.0080 | 1499 | 1807 | 0.000766 |
| BEATUSDT | 0.000764 | -0.0040 | 1746 | 1773 | 0.000314 |
| HUSDT | 0.000714 | -0.0040 | 1540 | 1620 | -0.001792 |
| SKYAIUSDT | 0.000873 | -0.0045 | 1465 | 1598 | -0.002615 |
| SIRENUSDT | 0.001818 | -0.0095 | 1416 | 1537 | -0.001487 |

### reversal_5h × ret_fwd_24h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| PLAYUSDT | 0.014518 | -0.0033 | 1748 | 1507 | -0.001252 |
| BEATUSDT | 0.017577 | -0.0040 | 1737 | 1765 | -0.017869 |
| HUSDT | 0.020459 | -0.0035 | 1537 | 1603 | -0.015264 |
| ESPORTSUSDT | 0.009836 | -0.0011 | 1495 | 1397 | -0.004719 |
| LABUSDT | 0.039280 | -0.0077 | 1494 | 1791 | 0.010966 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| LABUSDT | 0.039280 | -0.0077 | 1494 | 1791 | 0.010966 |
| BEATUSDT | 0.017577 | -0.0040 | 1737 | 1765 | -0.017869 |
| HUSDT | 0.020459 | -0.0035 | 1537 | 1603 | -0.015264 |
| SKYAIUSDT | 0.020535 | -0.0042 | 1465 | 1579 | 0.004195 |
| SIRENUSDT | 0.044808 | -0.0097 | 1403 | 1533 | 0.015611 |

### volatility_20h × ret_fwd_1h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| BEATUSDT | 0.000658 | 0.0248 | 3724 | 5 | -0.005993 |
| PLAYUSDT | 0.000522 | 0.0260 | 3174 | 140 | -0.001494 |
| LABUSDT | 0.001814 | 0.0260 | 3092 | 229 | 0.002046 |
| HUSDT | 0.000714 | 0.0200 | 2890 | 80 | -0.002693 |
| SIRENUSDT | 0.001831 | 0.0303 | 2580 | 242 | 0.002953 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| TRXUSDT | 0.000027 | 0.0023 | 0 | 4125 |  |
| PAXGUSDT | -0.000003 | 0.0027 | 25 | 3917 | -0.000070 |
| BNBUSDT | -0.000078 | 0.0043 | 0 | 3899 |  |
| BTCUSDT | -0.000069 | 0.0044 | 0 | 3847 |  |
| LTCUSDT | -0.000130 | 0.0053 | 3 | 2967 | 0.005028 |

### volatility_20h × ret_fwd_24h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| BEATUSDT | 0.016208 | 0.0247 | 3708 | 5 | -0.001699 |
| PLAYUSDT | 0.014714 | 0.0259 | 3165 | 140 | 0.000877 |
| LABUSDT | 0.039494 | 0.0259 | 3071 | 229 | 0.041266 |
| HUSDT | 0.020461 | 0.0197 | 2867 | 80 | -0.078344 |
| SIRENUSDT | 0.045091 | 0.0303 | 2579 | 242 | 0.059936 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| TRXUSDT | 0.000754 | 0.0023 | 0 | 4102 |  |
| PAXGUSDT | -0.000051 | 0.0027 | 25 | 3894 | -0.013802 |
| BNBUSDT | -0.001694 | 0.0043 | 0 | 3876 |  |
| BTCUSDT | -0.001492 | 0.0044 | 0 | 3824 |  |
| LTCUSDT | -0.003056 | 0.0053 | 3 | 2944 | 0.043617 |

### rsi_14h × ret_fwd_1h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| TRXUSDT | 0.000027 | 51.7292 | 1628 | 998 | 0.000050 |
| SKYAIUSDT | 0.000864 | 51.1776 | 1578 | 1102 | 0.001270 |
| LABUSDT | 0.001808 | 51.6076 | 1514 | 950 | -0.002277 |
| SIRENUSDT | 0.001828 | 51.1776 | 1484 | 967 | 0.001786 |
| BEATUSDT | 0.000733 | 50.2492 | 1457 | 1209 | 0.000754 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| PLAYUSDT | 0.000519 | 48.7605 | 1295 | 1376 | 0.001594 |
| VELVETUSDT | 0.000717 | 49.0612 | 1229 | 1329 | 0.002023 |
| ESPORTSUSDT | 0.000437 | 49.0847 | 1303 | 1305 | 0.001325 |
| AIOUSDT | 0.000279 | 49.9028 | 1383 | 1251 | 0.000280 |
| BEATUSDT | 0.000733 | 50.2492 | 1457 | 1209 | 0.000754 |

### rsi_14h × ret_fwd_24h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| TRXUSDT | 0.000741 | 51.8379 | 1628 | 975 | -0.001766 |
| SKYAIUSDT | 0.020530 | 51.0526 | 1555 | 1102 | -0.021744 |
| LABUSDT | 0.039395 | 51.5718 | 1506 | 945 | -0.012282 |
| SIRENUSDT | 0.044978 | 51.2982 | 1484 | 944 | -0.052860 |
| BEATUSDT | 0.016410 | 50.1955 | 1447 | 1202 | 0.025605 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| PLAYUSDT | 0.014637 | 48.8878 | 1295 | 1353 | 0.019981 |
| VELVETUSDT | 0.017643 | 48.9727 | 1216 | 1329 | 0.055366 |
| ESPORTSUSDT | 0.009944 | 48.9723 | 1287 | 1302 | 0.016778 |
| AIOUSDT | 0.008090 | 49.8887 | 1381 | 1243 | -0.000747 |
| BEATUSDT | 0.016410 | 50.1955 | 1447 | 1202 | 0.025605 |

### bb_zscore_20h × ret_fwd_1h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| SKYAIUSDT | 0.000874 | 0.0851 | 1470 | 1127 | 0.002484 |
| TRXUSDT | 0.000028 | 0.1158 | 1459 | 1076 | -0.000017 |
| SIRENUSDT | 0.001832 | 0.1121 | 1413 | 1091 | 0.002606 |
| LABUSDT | 0.001810 | 0.0957 | 1409 | 1069 | -0.001420 |
| BEATUSDT | 0.000668 | 0.0335 | 1395 | 1200 | 0.000804 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| PLAYUSDT | 0.000522 | -0.0847 | 1241 | 1335 | 0.000769 |
| VELVETUSDT | 0.000711 | -0.0517 | 1299 | 1320 | 0.001068 |
| ESPORTSUSDT | 0.000439 | -0.0762 | 1304 | 1299 | 0.000782 |
| AIOUSDT | 0.000285 | 0.0208 | 1360 | 1239 | 0.000129 |
| BEATUSDT | 0.000668 | 0.0335 | 1395 | 1200 | 0.000804 |

### bb_zscore_20h × ret_fwd_24h

Top Q5 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| TRXUSDT | 0.000752 | 0.1236 | 1459 | 1055 | -0.000105 |
| SKYAIUSDT | 0.020585 | 0.0775 | 1458 | 1127 | -0.007936 |
| SIRENUSDT | 0.045073 | 0.1195 | 1413 | 1069 | -0.026785 |
| LABUSDT | 0.039478 | 0.0898 | 1397 | 1065 | -0.010603 |
| BEATUSDT | 0.016225 | 0.0333 | 1391 | 1191 | 0.020663 |

Top Q1 symbols:
| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |
|---|---:|---:|---:|---:|---:|
| VELVETUSDT | 0.017630 | -0.0592 | 1288 | 1319 | 0.030075 |
| PLAYUSDT | 0.014701 | -0.0772 | 1241 | 1312 | 0.006801 |
| ESPORTSUSDT | 0.009989 | -0.0842 | 1292 | 1297 | 0.008948 |
| AIOUSDT | 0.008027 | 0.0229 | 1359 | 1225 | 0.010691 |
| BEATUSDT | 0.016225 | 0.0333 | 1391 | 1191 | 0.020663 |

### Concentration Risk

If any single symbol appears in Q5 > 30% of timestamps, it dominates the factor.

- ⚠ **mom_20h × ret_fwd_1h**: LABUSDT in Q5 43% of timestamps
- ⚠ **mom_20h × ret_fwd_4h**: LABUSDT in Q5 43% of timestamps
- ⚠ **mom_20h × ret_fwd_24h**: LABUSDT in Q5 43% of timestamps
- ⚠ **mom_20h × ret_fwd_72h**: LABUSDT in Q5 43% of timestamps
- ⚠ **reversal_5h × ret_fwd_1h**: PLAYUSDT in Q5 41% of timestamps
- ⚠ **reversal_5h × ret_fwd_4h**: PLAYUSDT in Q5 41% of timestamps
- ⚠ **reversal_5h × ret_fwd_24h**: PLAYUSDT in Q5 41% of timestamps
- ⚠ **reversal_5h × ret_fwd_72h**: BEATUSDT in Q5 41% of timestamps
- ⚠ **volatility_20h × ret_fwd_1h**: BEATUSDT in Q5 87% of timestamps
- ⚠ **volatility_20h × ret_fwd_4h**: BEATUSDT in Q5 87% of timestamps
- ⚠ **volatility_20h × ret_fwd_24h**: BEATUSDT in Q5 87% of timestamps
- ⚠ **volatility_20h × ret_fwd_72h**: BEATUSDT in Q5 87% of timestamps
- ⚠ **rsi_14h × ret_fwd_1h**: TRXUSDT in Q5 38% of timestamps
- ⚠ **rsi_14h × ret_fwd_4h**: TRXUSDT in Q5 38% of timestamps
- ⚠ **rsi_14h × ret_fwd_24h**: TRXUSDT in Q5 38% of timestamps
- ⚠ **rsi_14h × ret_fwd_72h**: TRXUSDT in Q5 38% of timestamps
- ⚠ **bb_zscore_20h × ret_fwd_1h**: SKYAIUSDT in Q5 34% of timestamps
- ⚠ **bb_zscore_20h × ret_fwd_4h**: SKYAIUSDT in Q5 34% of timestamps
- ⚠ **bb_zscore_20h × ret_fwd_24h**: TRXUSDT in Q5 34% of timestamps
- ⚠ **bb_zscore_20h × ret_fwd_72h**: TRXUSDT in Q5 34% of timestamps

## Verdict

- IC sign conflicts: **16** / 20
- Overlap-inflated t-stats (>30% drop): **10**
  - mom_20h × ret_fwd_24h: spread_t 10.49 → 2.91 (drop 72%)
  - mom_20h × ret_fwd_72h: spread_t 7.87 → 1.98 (drop 75%)
  - reversal_5h × ret_fwd_24h: spread_t -4.66 → -1.03 (drop 78%)
  - reversal_5h × ret_fwd_72h: spread_t -4.60 → -1.19 (drop 74%)
  - volatility_20h × ret_fwd_24h: spread_t 18.73 → 3.48 (drop 81%)
  - volatility_20h × ret_fwd_72h: spread_t 25.11 → 2.72 (drop 89%)
  - rsi_14h × ret_fwd_24h: spread_t 10.33 → 1.38 (drop 87%)
  - rsi_14h × ret_fwd_72h: spread_t 9.43 → 1.35 (drop 86%)
  - bb_zscore_20h × ret_fwd_24h: spread_t 8.17 → 1.66 (drop 80%)
  - bb_zscore_20h × ret_fwd_72h: spread_t 5.78 → 1.47 (drop 75%)

**Factors worth deeper investigation in V1:** volatility_20h, bb_zscore_20h, rsi_14h

## Next Steps

1. If volatility_20h survives winsorize + non-overlap: try combining with rsi_14h as composite
2. Run regime analysis (bull/bear/sideways) to check conditional IC
3. Add cost-adjusted labels (ret_fwd_Xh - estimated_cost) before any strategy consideration
4. Consider 4h or 1d frequency to reduce noise
