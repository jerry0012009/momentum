# Crypto Top50 Factor Library — Result Summary (crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1)

- universe: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_crypto_native_v1`
- evaluation_period: `2024-06-01 01:00:00+00:00 ~ 2026-06-13 00:00:00+00:00`
- generated_at: `2026-06-14T19:33:43Z`
- caveat: Static current Top50 diagnostic universe; debug and initial screening only.
- excluded_symbols (missing_bar_rate > 5%): ['0GUSDT', '1MBABYDOGEUSDT', '2ZUSDT', '4USDT', 'ACTUSDT', 'AERGOUSDT', 'AIGENSYNUSDT', 'AIOTUSDT', 'AIXBTUSDT', 'ALCHUSDT', 'ALLOUSDT', 'ALPINEUSDT', 'ANIMEUSDT', 'ARCUSDT', 'ARIAUSDT', 'ASTERUSDT', 'ATUSDT', 'AVNTUSDT', 'AZTECUSDT', 'BABYUSDT', 'BANANAS31USDT', 'BARDUSDT', 'BASEDUSDT', 'BASUSDT', 'BEATUSDT', 'BERAUSDT', 'BILLUSDT', 'BIOUSDT', 'BIRBUSDT', 'BLESSUSDT', 'BREVUSDT', 'BROCCOLI714USDT', 'BRUSDT', 'BSBUSDT', 'BULLAUSDT', 'BUSDT', 'CATIUSDT', 'CGPTUSDT', 'CHIPUSDT', 'CLOUSDT', 'COAIUSDT', 'COOKIEUSDT', 'COWUSDT', 'CUSDT', 'DIAUSDT', 'DOGSUSDT', 'EDENUSDT', 'EDGEUSDT', 'EIGENUSDT', 'ENSOUSDT', 'ERAUSDT', 'ESPUSDT', 'EVAAUSDT', 'FARTCOINUSDT', 'FFUSDT', 'FHEUSDT', 'FIDAUSDT', 'FOLKSUSDT', 'GIGGLEUSDT', 'GOATUSDT', 'GUNUSDT', 'HAEDALUSDT', 'HEMIUSDT', 'HIVEUSDT', 'HMSTRUSDT', 'HOMEUSDT', 'HUMAUSDT', 'HUSDT', 'HYPERUSDT', 'HYPEUSDT', 'INITUSDT', 'IPUSDT', 'JELLYJELLYUSDT', 'KAITOUSDT', 'KATUSDT', 'KERNELUSDT', 'KGENUSDT', 'KITEUSDT', 'LABUSDT', 'LAUSDT', 'LAYERUSDT', 'LIGHTUSDT', 'LINEAUSDT', 'LYNUSDT', 'MELANIAUSDT', 'MEUSDT', 'MMTUSDT', 'MONUSDT', 'MOODENGUSDT', 'MOVEUSDT', 'MUBARAKUSDT', 'MUSDT', 'MYXUSDT', 'NEIROUSDT', 'NIGHTUSDT', 'NILUSDT', 'NOMUSDT', 'NXPCUSDT', 'OPENUSDT', 'OPNUSDT', 'ORCAUSDT', 'PAXGUSDT', 'PENGUUSDT', 'PHAUSDT', 'PIEVERSEUSDT', 'PIPPINUSDT', 'PLAYUSDT', 'PNUTUSDT', 'POPCATUSDT', 'POWERUSDT', 'PROMPTUSDT', 'PROVEUSDT', 'PUMPBTCUSDT', 'PUMPUSDT', 'RAREUSDT', 'RAVEUSDT', 'REDUSDT', 'RESOLVUSDT', 'RIVERUSDT', 'ROBOUSDT', 'SAHARAUSDT', 'SENTUSDT', 'SIGNUSDT', 'SIRENUSDT', 'SKYAIUSDT', 'SOMIUSDT', 'SOONUSDT', 'SOPHUSDT', 'SPACEUSDT', 'SPKUSDT', 'SPXUSDT', 'STABLEUSDT', 'STBLUSDT', 'STOUSDT', 'SUNUSDT', 'SUSDT', 'SWARMSUSDT', 'TAUSDT', 'TRADOORUSDT', 'TREEUSDT', 'TRUMPUSDT', 'TRUSTUSDT', 'TRUTHUSDT', 'TSTUSDT', 'UAIUSDT', 'UBUSDT', 'USUALUSDT', 'VIRTUALUSDT', 'VVVUSDT', 'WCTUSDT', 'WLFIUSDT', 'XAUTUSDT', 'XNYUSDT', 'XPINUSDT', 'XPLUSDT', 'ZBTUSDT', 'ZEREBROUSDT', 'ZORAUSDT']
- timestamp_convention: timestamp = bar_close_time; factor known_at = bar_close_time
- label_convention: calendar-time forward returns (no row-shift across gaps)

| factor | label | direction | IC_mean | ICIR | RankIC_mean | RankICIR | raw_spread | raw_spread_t | dir_adj_spread | dir_adj_t | turnover | coverage | n_ts |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| taker_buy_ratio_20h | ret_fwd_1h | positive | 0.000312 | 0.002899 | -0.004358 | -0.038454 | 0.000046 | 2.080101 | 0.000046 | 2.080101 | 0.151749 | 0.935718 | 16736 |
| taker_buy_ratio_20h | ret_fwd_4h | positive | 0.002810 | 0.026120 | -0.003121 | -0.027177 | 0.000204 | 4.609372 | 0.000204 | 4.609372 | 0.151749 | 0.935718 | 16737 |
| taker_buy_ratio_20h | ret_fwd_24h | positive | 0.006131 | 0.055258 | 0.001151 | 0.009730 | 0.000912 | 8.047129 | 0.000912 | 8.047129 | 0.151749 | 0.935718 | 16737 |
| taker_buy_ratio_20h | ret_fwd_72h | positive | 0.010465 | 0.090060 | 0.007680 | 0.063965 | 0.001989 | 9.438221 | 0.001989 | 9.438221 | 0.151749 | 0.935718 | 16737 |
| taker_buy_zscore_20h | ret_fwd_1h | positive | -0.006147 | -0.055269 | -0.010387 | -0.091534 | -0.000051 | -2.408027 | -0.000051 | -2.408027 | 0.779727 | 0.935718 | 16736 |
| taker_buy_zscore_20h | ret_fwd_4h | positive | -0.004026 | -0.036362 | -0.007785 | -0.068561 | -0.000107 | -2.532934 | -0.000107 | -2.532934 | 0.779727 | 0.935718 | 16737 |
| taker_buy_zscore_20h | ret_fwd_24h | positive | -0.001144 | -0.010432 | -0.002307 | -0.020407 | -0.000053 | -0.494019 | -0.000053 | -0.494019 | 0.779727 | 0.935718 | 16737 |
| taker_buy_zscore_20h | ret_fwd_72h | positive | -0.000346 | -0.003164 | -0.000807 | -0.007148 | 0.000072 | 0.372133 | 0.000072 | 0.372133 | 0.779727 | 0.935718 | 16737 |
| taker_buy_delta_5h | ret_fwd_1h | positive | -0.004739 | -0.047390 | -0.007857 | -0.071888 | -0.000048 | -2.441193 | -0.000048 | -2.441193 | 0.769936 | 0.937524 | 16768 |
| taker_buy_delta_5h | ret_fwd_4h | positive | -0.002214 | -0.022358 | -0.005190 | -0.047378 | -0.000073 | -1.890970 | -0.000073 | -1.890970 | 0.769936 | 0.937524 | 16769 |
| taker_buy_delta_5h | ret_fwd_24h | positive | -0.000733 | -0.007329 | -0.001468 | -0.013383 | -0.000044 | -0.440653 | -0.000044 | -0.440653 | 0.769936 | 0.937524 | 16769 |
| taker_buy_delta_5h | ret_fwd_72h | positive | -0.000357 | -0.003521 | -0.000607 | -0.005595 | 0.000047 | 0.248880 | 0.000047 | 0.248880 | 0.769936 | 0.937524 | 16769 |
| funding_rate_level_20h | ret_fwd_1h | negative | 0.008041 | 0.036948 | 0.010915 | 0.087416 | -0.000025 | -1.018005 | 0.000025 | 1.018005 | 0.036542 | 0.877449 | 16756 |
| funding_rate_level_20h | ret_fwd_4h | negative | 0.013668 | 0.062363 | 0.017711 | 0.142376 | -0.000092 | -1.899681 | 0.000092 | 1.899681 | 0.036542 | 0.877449 | 16757 |
| funding_rate_level_20h | ret_fwd_24h | negative | 0.021364 | 0.102790 | 0.028736 | 0.229568 | -0.000488 | -3.961185 | 0.000488 | 3.961185 | 0.036542 | 0.877449 | 16757 |
| funding_rate_level_20h | ret_fwd_72h | negative | 0.021168 | 0.113283 | 0.030142 | 0.249018 | -0.000497 | -2.391241 | 0.000497 | 2.391241 | 0.036542 | 0.877449 | 16757 |
| funding_rate_zscore_80h | ret_fwd_1h | negative | 0.002584 | 0.017864 | 0.003299 | 0.026438 | -0.000006 | -0.246057 | 0.000006 | 0.246057 | 0.114052 | 0.773713 | 16696 |
| funding_rate_zscore_80h | ret_fwd_4h | negative | 0.002736 | 0.019011 | 0.006612 | 0.052628 | 0.000026 | 0.518313 | -0.000026 | -0.518313 | 0.114052 | 0.773713 | 16697 |
| funding_rate_zscore_80h | ret_fwd_24h | negative | 0.005910 | 0.041487 | 0.012330 | 0.095148 | 0.000235 | 1.806826 | -0.000235 | -1.806826 | 0.114052 | 0.773713 | 16697 |
| funding_rate_zscore_80h | ret_fwd_72h | negative | 0.001892 | 0.014111 | 0.006951 | 0.054131 | -0.000087 | -0.376010 | 0.000087 | 0.376010 | 0.114052 | 0.773713 | 16697 |
| funding_rate_change_24h | ret_fwd_1h | negative | 0.002275 | 0.010531 | 0.002146 | 0.018583 | -0.000015 | -0.607281 | 0.000015 | 0.607281 | 0.120442 | 0.877246 | 16751 |
| funding_rate_change_24h | ret_fwd_4h | negative | 0.004050 | 0.018756 | 0.004505 | 0.039184 | -0.000043 | -0.899806 | 0.000043 | 0.899806 | 0.120442 | 0.877246 | 16752 |
| funding_rate_change_24h | ret_fwd_24h | negative | 0.011561 | 0.057017 | 0.005907 | 0.050565 | -0.000178 | -1.478934 | 0.000178 | 1.478934 | 0.120442 | 0.877246 | 16752 |
| funding_rate_change_24h | ret_fwd_72h | negative | 0.011571 | 0.063588 | 0.002455 | 0.021187 | -0.000176 | -0.831442 | 0.000176 | 0.831442 | 0.120442 | 0.877246 | 16752 |

Next: inspect NaN, timestamp alignment, and IC signs before V1.
