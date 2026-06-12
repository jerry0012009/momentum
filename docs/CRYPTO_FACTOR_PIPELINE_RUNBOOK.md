# Crypto Factor Pipeline Runbook

This runbook executes the `crypto_top50_usdt_perp_1h` factor research pipeline.

Default mode is V0 Debug Run:

- universe: `crypto_top50_usdt_perp_1h`
- data: Binance USDT-M 1h OHLCV
- window: latest 180 days by default
- purpose: validate data, labels, factor values, and evaluation outputs
- caveat: current universe is static current Top50, so V0 results are for debug and initial screening only

## Install

```bash
cd /root/clawd/jerry/momentum
source .venv/bin/activate
pip install -r requirements-crypto.txt
```

If `.venv` does not exist:

```bash
cd /root/clawd/jerry/momentum
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-crypto.txt
```

## Smoke test: BTC/ETH, 7 days

```bash
python scripts/fetch_crypto_top50_bars.py --days 7 --symbols BTCUSDT ETHUSDT
python scripts/build_labels.py
python scripts/build_factor_values.py
python scripts/evaluate_factors.py
```

Check outputs:

```bash
ls -lh data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet
ls -lh data/features/crypto_top50_usdt_perp_1h/labels.parquet
ls -lh reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/*/metrics.json
cat research/factor_runs/crypto_top50_factor_library/result_summary.md
```

## V0 Debug Run: Top50 latest 180 days

```bash
python scripts/fetch_crypto_top50_bars.py --days 180
python scripts/build_labels.py
python scripts/build_factor_values.py
python scripts/evaluate_factors.py
```

Expected size:

```text
50 symbols × 180 days × 24 bars/day ≈ 216,000 rows
```

## V1 baseline after V0 passes

```bash
python scripts/fetch_crypto_top50_bars.py --start 2024-01-01T00:00:00Z
python scripts/build_labels.py
python scripts/build_factor_values.py
python scripts/evaluate_factors.py
```

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
3. Five registered factors have reasonable coverage.
4. IC, RankIC, spread, and turnover are generated without mass null values.
5. Master result summary is generated.
