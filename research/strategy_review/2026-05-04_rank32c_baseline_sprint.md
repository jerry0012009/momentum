# Rank32c baseline sprint: BTC UTC weak-cell short

Generated: 2026-05-04T05:12:53Z

## Family choice
Chosen family: single-asset BTCUSDT UTC weekday-hour weak-cell short. This is not selected from the rank winner list; prior rank/clock work is treated as cautionary evidence that broad fixed UTC sleeves can fail. The family is retained only because it is simple, explainable, and fully schedulable before order time.

## Module split
- universe: `BTCUSDT` only, eligible after `2019-09-25T08:00:00Z`; no future return, future volume, current active-list, or hindsight hot-coin selection.
- baseline: each UTC month, use only the trailing `60` calendar days to find the weakest `(weekday, hour)` cell by future `16`-bar long return; next month short the weakest cell.
- entry: scheduled bar-open entry for the selected cell.
- exit: fixed time stop after `16` 15m bars.
- cost: `8.0` bps round trip for baseline, `12.0` bps plus 1-bar delay in execution-realistic.
- veto: optional skip when prior 24h absolute BTC move is above trailing `180`d mean + `2.0` std.
- gate: optional require trailing cell edge to exceed assumed cost.
- sizing: fixed 1x research unit; tiny-live config caps notional separately.
- execution: no-overlap, bar-open accounting from cached Binance UM klines; execution-realistic adds 1-bar latency and higher cost.

## Data
- source: local Binance USD-M 15m raw zip cache
- first bar: `2020-01-01T00:00:00Z`
- last bar: `2026-04-11T23:45:00Z`
- bars: `220128`

## Ablation
| variant | trades | net_mean_bps | net_cum_pct | max_drawdown_pct | win_rate_pct | positive_year_ratio_pct | avg_trades_per_month |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline_only | 328 | 4.1286 | 10.5801 | -24.0891 | 47.8659 | 71.4286 | 4.3733 |
| baseline_plus_veto | 313 | 7.9375 | 24.4845 | -10.8139 | 47.6038 | 71.4286 | 4.1733 |
| baseline_plus_gate | 328 | 4.1286 | 10.5801 | -24.0891 | 47.8659 | 71.4286 | 4.3733 |
| baseline_plus_veto_plus_gate | 313 | 7.9375 | 24.4845 | -10.8139 | 47.6038 | 71.4286 | 4.1733 |
| execution_realistic | 309 | 4.6207 | 12.0758 | -14.3767 | 46.9256 | 71.4286 | 4.1200 |

## Walk-forward yearly check
| variant | year | trades | net_mean_bps | net_cum_pct | max_drawdown_pct | win_rate_pct |
| --- | --- | --- | --- | --- | --- | --- |
| baseline_only | 2020 | 46 | -46.9135 | -19.7597 | -19.9174 | 36.9565 |
| baseline_only | 2021 | 55 | 13.3076 | 6.3010 | -11.8709 | 50.9091 |
| baseline_only | 2022 | 53 | 19.1845 | 10.2309 | -3.3196 | 45.2830 |
| baseline_only | 2023 | 53 | -8.1118 | -4.4173 | -6.9663 | 43.3962 |
| baseline_only | 2024 | 50 | 9.2770 | 4.2004 | -10.0177 | 58.0000 |
| baseline_only | 2025 | 56 | 23.3195 | 13.4279 | -5.6844 | 53.5714 |
| baseline_only | 2026 | 15 | 28.2459 | 4.1060 | -2.9481 | 40.0000 |
| baseline_plus_gate | 2020 | 46 | -46.9135 | -19.7597 | -19.9174 | 36.9565 |
| baseline_plus_gate | 2021 | 55 | 13.3076 | 6.3010 | -11.8709 | 50.9091 |
| baseline_plus_gate | 2022 | 53 | 19.1845 | 10.2309 | -3.3196 | 45.2830 |
| baseline_plus_gate | 2023 | 53 | -8.1118 | -4.4173 | -6.9663 | 43.3962 |
| baseline_plus_gate | 2024 | 50 | 9.2770 | 4.2004 | -10.0177 | 58.0000 |
| baseline_plus_gate | 2025 | 56 | 23.3195 | 13.4279 | -5.6844 | 53.5714 |
| baseline_plus_gate | 2026 | 15 | 28.2459 | 4.1060 | -2.9481 | 40.0000 |
| baseline_plus_veto | 2020 | 43 | -25.6675 | -10.6382 | -10.8139 | 39.5349 |
| baseline_plus_veto | 2021 | 54 | 27.8266 | 15.0354 | -9.2161 | 51.8519 |
| baseline_plus_veto | 2022 | 51 | 14.4646 | 7.2456 | -3.3196 | 45.0980 |
| baseline_plus_veto | 2023 | 53 | -12.2746 | -6.5035 | -8.0093 | 41.5094 |
| baseline_plus_veto | 2024 | 45 | 12.9552 | 5.4932 | -7.7248 | 57.7778 |
| baseline_plus_veto | 2025 | 52 | 19.0709 | 9.9657 | -5.7894 | 51.9231 |
| baseline_plus_veto | 2026 | 15 | 28.2459 | 4.1060 | -2.9481 | 40.0000 |
| baseline_plus_veto_plus_gate | 2020 | 43 | -25.6675 | -10.6382 | -10.8139 | 39.5349 |
| baseline_plus_veto_plus_gate | 2021 | 54 | 27.8266 | 15.0354 | -9.2161 | 51.8519 |
| baseline_plus_veto_plus_gate | 2022 | 51 | 14.4646 | 7.2456 | -3.3196 | 45.0980 |
| baseline_plus_veto_plus_gate | 2023 | 53 | -12.2746 | -6.5035 | -8.0093 | 41.5094 |
| baseline_plus_veto_plus_gate | 2024 | 45 | 12.9552 | 5.4932 | -7.7248 | 57.7778 |
| baseline_plus_veto_plus_gate | 2025 | 52 | 19.0709 | 9.9657 | -5.7894 | 51.9231 |
| baseline_plus_veto_plus_gate | 2026 | 15 | 28.2459 | 4.1060 | -2.9481 | 40.0000 |
| execution_realistic | 2020 | 43 | -16.8615 | -7.1464 | -7.0197 | 34.8837 |
| execution_realistic | 2021 | 52 | 6.3479 | 2.4696 | -10.3743 | 50.0000 |
| execution_realistic | 2022 | 51 | 10.0457 | 4.6518 | -6.4377 | 50.9804 |
| execution_realistic | 2023 | 52 | -17.6653 | -8.9854 | -10.6710 | 36.5385 |
| execution_realistic | 2024 | 45 | 7.0103 | 2.6816 | -11.8077 | 57.7778 |
| execution_realistic | 2025 | 52 | 22.3107 | 11.8880 | -6.6644 | 48.0769 |
| execution_realistic | 2026 | 14 | 53.8134 | 7.6426 | -2.2606 | 57.1429 |

## Parameter plateau
Top grid rows are shown only to verify a plateau, not to choose a single best point. Frozen baseline remains `train=60d / hold=16 bars / bottom_k=1`.

| train_days | hold_bars | bottom_k | trades | net_mean_bps | net_cum_pct | max_drawdown_pct | positive_year_ratio_pct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 365.0000 | 32.0000 | 1.0000 | 318.0000 | 17.3609 | 65.6298 | -28.7186 | 57.1429 |
| 365.0000 | 32.0000 | 3.0000 | 425.0000 | 7.5348 | 28.8138 | -37.0750 | 42.8571 |
| 180.0000 | 32.0000 | 3.0000 | 453.0000 | 4.4535 | 14.0791 | -41.7899 | 57.1429 |
| 60.0000 | 16.0000 | 1.0000 | 328.0000 | 4.1286 | 10.5801 | -24.0891 | 71.4286 |
| 60.0000 | 32.0000 | 1.0000 | 327.0000 | 2.0002 | 1.3354 | -30.5483 | 57.1429 |
| 30.0000 | 32.0000 | 1.0000 | 326.0000 | 0.8040 | -3.4615 | -33.7183 | 57.1429 |
| 365.0000 | 16.0000 | 1.0000 | 319.0000 | -1.2287 | -6.4825 | -32.9207 | 28.5714 |
| 90.0000 | 32.0000 | 3.0000 | 492.0000 | -2.9958 | -19.9049 | -45.9660 | 42.8571 |
| 90.0000 | 16.0000 | 1.0000 | 328.0000 | -3.0016 | -12.2185 | -27.8648 | 42.8571 |
| 180.0000 | 32.0000 | 1.0000 | 321.0000 | -3.1522 | -14.2165 | -50.5381 | 28.5714 |
| 90.0000 | 32.0000 | 1.0000 | 326.0000 | -5.3089 | -21.3180 | -42.4062 | 57.1429 |
| 30.0000 | 16.0000 | 1.0000 | 331.0000 | -5.4141 | -19.2183 | -27.5386 | 42.8571 |

## Verdict
PASS -> tiny-live candidate emitted

Baseline pass rule: baseline-only must have positive post-cost mean bps and cumulative return, max drawdown better than -60%, at least 50% positive years, and at least 60 trades. Gate/veto are not allowed to rescue a failed baseline.

## Artifacts
- `reports/artifacts/rank32c_baseline_sprint/summary.json`
- `reports/artifacts/rank32c_baseline_sprint/ablation_summary.csv`
- `reports/artifacts/rank32c_baseline_sprint/walk_forward_yearly.csv`
- `reports/artifacts/rank32c_baseline_sprint/parameter_plateau.csv`
- `reports/artifacts/rank32c_baseline_sprint/trades.csv`
- `reports/artifacts/rank32c_baseline_sprint/monthly_selections.csv`
- `config/strategies/rank32c_btc_utc_weak_cell_tiny_live.yaml`
