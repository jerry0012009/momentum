# Factor Library Design

This document defines the minimum design for building a reusable, auditable factor library in the `momentum` project.

It complements:

- `docs/AUDITABLE_FACTOR_RESEARCH_SKILL.md`
- `docs/RESEARCH_LIFECYCLE.md`
- `docs/CODE_TRUST_MAP.md`
- `docs/DATA_CONTRACT.md`
- `docs/FACTOR_BACKLOG.md`

The goal is to move from exploratory strategy scripts to a small, reliable factor research system.

---

## 1. What the Factor Library Is Not

The factor library is not:

- a collection of attractive backtest reports;
- a list of strategies that made money on selected symbols;
- a pile of AI-generated scripts;
- a record of which factor worked on which single asset after ad-hoc testing;
- a production trading system;
- a substitute for data, signal, execution, and cost audits.

A factor that works only after searching across many assets and parameters is not automatically a useful factor. It may simply be a fitted result.

---

## 2. What the Factor Library Is

The factor library is a standardized registry of factor definitions, computed factor values, labels, and evaluation results under fixed research protocols.

A valid factor library entry should answer:

1. What is the factor?
2. When is the factor known?
3. What universe was it evaluated on?
4. What future return label was used?
5. What are the IC / Rank IC / ICIR results?
6. What is the cross-sectional spread between high and low quantiles?
7. What is the turnover and cost sensitivity?
8. Under what market regime does it work or fail?
9. Is it stable enough to keep, park, rebuild, or drop?

The library should emphasize comparability over quantity.

---

## 3. First Universe

The first standard universe is:

```yaml
universe_name: crypto_top50_usdt_perp_1h
market: crypto
venue: Binance USDT-margined perpetual futures
instrument_type: perpetual_swap
quote_asset: USDT
frequency: 1h
selection_rule: top 50 symbols by trailing 30-day dollar volume
rebalance_frequency: monthly
min_listing_age_days: 90
exclude_stablecoin_pairs: true
exclude_leveraged_tokens: true
survivorship_bias_policy: record universe membership at each rebalance date
```

This universe is chosen because:

- it matches the intended crypto quant research direction;
- it is liquid enough for first-pass factor research;
- it supports cross-sectional IC / Rank IC evaluation;
- it avoids trying to mix equities, A-shares, futures, gold, and crypto in one benchmark;
- it can be cached locally without requiring a full market data warehouse.

Do not start with multiple universes. The first factor library version should use one universe, one frequency, and one label protocol.

---

## 4. Data Policy

The project should not store all historical Binance data.

Data storage policy:

| Data Type | Store? | Reason |
|---|---:|---|
| Full Binance market history | No | Too large and unnecessary for early research |
| Data slice used by a specific factor library evaluation | Yes | Required for reproducibility |
| Universe membership snapshots | Yes | Required to reduce survivorship bias |
| Factor values | Yes | Core research asset |
| Labels / forward returns | Yes | Required for re-evaluation |
| Evaluation metrics | Yes | Required for comparison |
| Raw zip / CSV from public source | Optional | Can be deleted if reproducible from source |
| Live orders / fills / paper trading logs | Yes | Not reconstructable later |

For the first universe, store only the required research slice:

```text
data/cache/crypto_top50_usdt_perp_1h/
  manifest.json
  universe_membership.parquet
  bars_1h.parquet
```

Suggested `bars_1h.parquet` schema:

```text
timestamp
symbol
open
high
low
close
volume
quote_volume
trade_count
source
market
instrument_type
timeframe
```

Suggested `universe_membership.parquet` schema:

```text
rebalance_date
symbol
rank_by_dollar_volume
trailing_30d_dollar_volume
listing_age_days
included
exclusion_reason
```

---

## 5. Standard Labels

The first label protocol should be simple and fixed.

Required labels:

```text
ret_fwd_1h
ret_fwd_4h
ret_fwd_24h
ret_fwd_72h
```

Label definitions:

```text
ret_fwd_h = close[t+h] / close[t] - 1
```

Optional cost-adjusted labels may be added later, but the first version should keep raw forward returns and trading-cost evaluation separate.

Label output path:

```text
data/features/crypto_top50_usdt_perp_1h/labels.parquet
```

Suggested schema:

```text
timestamp
symbol
ret_fwd_1h
ret_fwd_4h
ret_fwd_24h
ret_fwd_72h
```

Important rule:

> Labels may use future prices for evaluation, but factor values and signals must not.

---

## 6. Factor Registry

The factor registry is a table of factor definitions, not a table of backtest winners.

Suggested file:

```text
docs/FACTOR_REGISTRY.md
```

Minimum columns:

| Field | Meaning |
|---|---|
| `factor_name` | Stable unique name |
| `category` | momentum / reversal / volatility / liquidity / carry / regime / technical |
| `formula` | Exact definition |
| `parameters` | Windows and thresholds |
| `known_at` | When the value is knowable |
| `universe` | First evaluation universe |
| `frequency` | 1h / 4h / 1d etc. |
| `status` | IDEA / PROTOTYPED / REVIEW_REQUIRED / REVIEWED / KEEP / PARK / DROP |
| `artifact_path` | Where factor values and evaluation results live |
| `notes` | Caveats |

First candidate factors:

| factor_name | category | definition |
|---|---|---|
| `mom_20h` | momentum | `close / close.shift(20) - 1` |
| `reversal_5h` | reversal | `-(close / close.shift(5) - 1)` |
| `volatility_20h` | volatility | rolling std of 1h returns over 20 bars |
| `rsi_14h` | technical / reversal | RSI over 14 1h bars |
| `bb_zscore_20h` | technical / mean reversion | `(close - SMA(close,20)) / STD(close,20)` |

These factors are intentionally simple. The first objective is to validate the pipeline, not to maximize alpha.

---

## 7. Factor Values

Every factor must export standalone factor values.

Output path pattern:

```text
data/features/crypto_top50_usdt_perp_1h/<factor_name>/factor_values.parquet
```

Minimum schema:

```text
timestamp
symbol
factor_name
factor_value
known_at
source_timeframe
computed_at
```

Wide-format is acceptable during early research if documented:

```text
timestamp
symbol
mom_20h
reversal_5h
volatility_20h
rsi_14h
bb_zscore_20h
```

But long-format is preferred for a mature factor library.

---

## 8. Evaluation Protocol

The first factor evaluation should focus on cross-sectional predictiveness rather than strategy PnL.

Required metrics:

```text
coverage
IC_mean
IC_std
ICIR
RankIC_mean
RankIC_std
RankICIR
quantile_spread_mean
quantile_spread_tstat
turnover
missing_rate
```

Evaluation frequency:

```yaml
factor_frequency: 1h
rebalance_frequency: 1h
labels:
  - ret_fwd_1h
  - ret_fwd_4h
  - ret_fwd_24h
  - ret_fwd_72h
```

Basic method:

1. At each timestamp, rank symbols by factor value.
2. Compute cross-sectional IC and Rank IC against each future return label.
3. Split symbols into quantiles.
4. Compute high-minus-low or low-minus-high spread depending on expected factor direction.
5. Compute turnover of the top and bottom quantile memberships.
6. Aggregate by month and by regime.

Output path:

```text
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/metrics.json
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/result_summary.md
```

---

## 9. Factor Status

Each factor should have one status:

```text
IDEA
SCOPED
PROTOTYPED
REVIEW_REQUIRED
REVIEWED
KEEP
PARK
DROP
```

Suggested interpretation:

| Status | Meaning |
|---|---|
| `IDEA` | Not implemented |
| `SCOPED` | Formula and universe defined |
| `PROTOTYPED` | Factor values generated once |
| `REVIEW_REQUIRED` | AI-assisted or not yet audited |
| `REVIEWED` | Formula, timing, data, and evaluation checked |
| `KEEP` | Useful enough to keep in registry |
| `PARK` | Not enough evidence, but not falsified |
| `DROP` | Fails evaluation or has no stable signal |

Do not use `KEEP` merely because a factor works on one symbol.

---

## 10. Relationship to `factor_runs`

`research/factor_runs/` is not the factor library itself.

It is the audit dossier layer.

Example:

```text
research/factor_runs/rank444_rsi_bb_v0/
```

This folder records why the old Rank444 RSI+BB strategy package is not directly admissible into the factor library.

If the RSI+BB idea is rebuilt cleanly, create a new research dossier:

```text
research/factor_runs/clean_rsi_bb_baseline_v0/
```

Then, if the factor component is useful, register factor definitions such as:

```text
rsi_14h
bb_zscore_20h
```

The rule is:

> `factor_runs` records research process and decisions; `FACTOR_REGISTRY.md` records factor definitions and status.

---

## 11. Minimum First Milestone

The first milestone is not a profitable strategy.

The first milestone is:

```text
A reproducible factor evaluation table for 3-5 simple factors on crypto_top50_usdt_perp_1h.
```

Required files for milestone 1:

```text
docs/FACTOR_REGISTRY.md

data/cache/crypto_top50_usdt_perp_1h/manifest.json
data/cache/crypto_top50_usdt_perp_1h/universe_membership.parquet
data/cache/crypto_top50_usdt_perp_1h/bars_1h.parquet

data/features/crypto_top50_usdt_perp_1h/labels.parquet

data/features/crypto_top50_usdt_perp_1h/<factor_name>/factor_values.parquet

reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/metrics.json
reports/artifacts/factor_eval/crypto_top50_usdt_perp_1h/<factor_name>/result_summary.md
```

First milestone factors:

```text
mom_20h
reversal_5h
volatility_20h
rsi_14h
bb_zscore_20h
```

Do not add more factors until the pipeline can produce comparable metrics for these five.

---

## 12. Practical Rule for This Repository

For the current stage:

1. Do not build a full Binance data warehouse.
2. Do not add many factors before the evaluation protocol works.
3. Do not promote strategy backtests into the factor library directly.
4. Do not mix A-shares, US equities, gold, Chinese futures, and crypto in the first factor library benchmark.
5. Use `crypto_top50_usdt_perp_1h` as the first standard benchmark.
6. Store only the data slice required for this benchmark.
7. Treat factor values, labels, evaluation metrics, and research memos as long-term assets.

Default rule:

> The factor library starts with definitions and comparable evaluation, not with strategy PnL.
