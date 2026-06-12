# Factor Library Pipeline Plan

> Current execution policy: run V0 first. V0 means static current Top50 universe plus latest 180 days of 1h bars. V0 is for pipeline validation and initial screening only.

## Completed

- [x] `data/cache/crypto_top50_usdt_perp_1h/manifest.json`
- [x] `data/cache/crypto_top50_usdt_perp_1h/universe_membership.parquet`
- [x] `data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet` initial schema
- [x] `data/features/crypto_top50_usdt_perp_1h/labels.parquet` initial schema
- [x] `docs/FACTOR_REGISTRY.md`
- [x] `requirements-crypto.txt`
- [x] `scripts/fetch_crypto_top50_bars.py`
- [x] `scripts/build_labels.py`
- [x] `scripts/build_factor_values.py`
- [x] `scripts/evaluate_factors.py`
- [x] `docs/CRYPTO_FACTOR_PIPELINE_RUNBOOK.md`

## V0 run

Smoke test:

```bash
python scripts/fetch_crypto_top50_bars.py --days 7 --symbols BTCUSDT ETHUSDT
python scripts/build_labels.py
python scripts/build_factor_values.py
python scripts/evaluate_factors.py
```

Full V0:

```bash
python scripts/fetch_crypto_top50_bars.py --days 180
python scripts/build_labels.py
python scripts/build_factor_values.py
python scripts/evaluate_factors.py
```

Expected V0 size:

```text
50 symbols × 180 days × 24 bars/day ≈ 216,000 rows
```

## Pipeline steps

1. `fetch_crypto_top50_bars.py`: reads manifest symbols, fetches closed 1h OHLCV bars, writes `bars_1h.parquet`, `fetch_log.json`, and manifest metadata.
2. `build_labels.py`: writes `ret_fwd_1h`, `ret_fwd_4h`, `ret_fwd_24h`, `ret_fwd_72h` to `labels.parquet`.
3. `build_factor_values.py`: writes factor values for `mom_20h`, `reversal_5h`, `volatility_20h`, `rsi_14h`, `bb_zscore_20h`.
4. `evaluate_factors.py`: writes IC, RankIC, quintile spread, turnover, coverage, per-factor summaries, and a master summary.

## Outputs

```text
data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet
data/cache/crypto_top50_usdt_perp_1h/fetch_log.json
data/features/crypto_top50_usdt_perp_1h/labels.parquet
data/features/crypto_top50_usdt_perp_1h/<factor>/factor_values.parquet
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor>/metrics.json
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor>/result_summary.md
research/factor_runs/crypto_top50_factor_library/result_summary.md
```

## V0 pass criteria

1. Most symbols fetch successfully.
2. Bars, labels, and factor values align by `timestamp + symbol`.
3. Registered factors have reasonable non-null coverage.
4. Evaluation metrics are generated without mass null values.
5. Master summary is generated.

## V1 after V0 passes

```bash
python scripts/fetch_crypto_top50_bars.py --start 2024-01-01T00:00:00Z
python scripts/build_labels.py
python scripts/build_factor_values.py
python scripts/evaluate_factors.py
```

V1 still uses static current Top50. Treat it as a baseline, not final evidence.