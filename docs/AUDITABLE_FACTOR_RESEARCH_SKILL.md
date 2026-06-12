# Auditable Factor Research Skill

This document defines the minimum standard for turning a trading idea, factor, signal, or strategy into an auditable research asset.

The goal is not to make every experiment profitable. The goal is to make every experiment reproducible, inspectable, falsifiable, and safe from obvious self-deception.

## 1. Scope

Use this skill whenever a research item involves any of the following:

* factor calculation
* signal generation
* backtest
* rank strategy
* parameter sweep
* regime filter
* order execution simulation
* paper or live candidate promotion
* published research report

A research item may be one of four types:

* `factor`: a numeric value observed at a timestamp, used to predict future returns or classify market state
* `signal`: a discrete decision derived from one or more factors
* `strategy`: signal + entry + exit + sizing + cost model
* `report`: human-readable output summarizing the research

A strategy can contain factors, but a strategy itself is not automatically a clean factor.

## 2. Required Research Folder

Every auditable research item must have a folder:

```text
research/factor_runs/<factor_or_strategy_name>/
  factor_memo.md
  data_contract.md
  audit_notes.md
  reproduction.md
  status.md
```

Optional files:

```text
  result_summary.md
  postmortem.md
  promotion_checklist.md
```

## 3. Data Entry Audit

Before evaluating results, identify the data entrance.

Required questions:

1. What function or script fetches the data?
2. What external provider is used?
3. Is the data fetched live at runtime?
4. Is the exact input data frozen?
5. Are timestamps timezone-normalized?
6. Is the data adjusted or raw?
7. Are missing bars handled explicitly?
8. Is the universe fixed before the test starts?
9. Could survivorship bias exist?
10. Could the data source return different results in future reruns?

Required output:

```text
data/cache/<name>/bars.parquet
data/cache/<name>/manifest.json
```

The manifest must include:

```json
{
  "name": "",
  "source": "",
  "downloaded_at": "",
  "symbols": [],
  "timeframe": "",
  "data_start": "",
  "data_end": "",
  "adjusted_or_raw": "",
  "script": "",
  "commit_sha": ""
}
```

## 4. Indicator and Factor Calculation Audit

Every indicator or factor must be separated from the backtest.

Required output:

```text
data/features/<name>/factor_values.parquet
```

Minimum required columns:

```text
timestamp
symbol
factor_name
factor_value
source_timeframe
computed_at
```

For wide-format research tables, the following is also acceptable:

```text
timestamp
symbol
close
rsi
bb_mid
bb_upper
bb_lower
bb_zscore
entry_signal
```

Required questions:

1. Does the factor use only current and past data?
2. Does it use rolling windows correctly?
3. Does it require future confirmation?
4. Does it contain any pivot, swing, trendline, support/resistance, HH/LL, or regime labels?
5. If future confirmation exists, are `origin_time` and `confirmed_at` both recorded?

## 5. Signal Timestamp Audit

Signal generation must distinguish between:

```text
signal_time
execution_time
```

A signal observed at bar close cannot automatically assume execution at the same close unless explicitly labeled as optimistic.

Preferred conservative assumptions:

```text
signal_time = close[t]
execution_time = open[t+1]
```

or:

```text
execution_price = close[t] + explicit_slippage
```

Every signal table must include:

```text
timestamp
symbol
signal
signal_reason
signal_price_reference
tradable_at
```

## 6. Trade and Execution Audit

Every backtest must export trades separately.

Required output:

```text
data/features/<name>/signals.parquet
reports/artifacts/<name>/trades.parquet
reports/artifacts/<name>/metrics.json
```

Minimum trade columns:

```text
symbol
entry_signal_time
entry_execution_time
entry_price
exit_signal_time
exit_execution_time
exit_price
side
size
gross_pnl
fees
slippage
net_pnl
return_pct
holding_bars
exit_reason
```

## 7. Cost Model

Every result must state its cost assumptions.

Minimum required fields:

```text
commission_rate
slippage_model
spread_assumption
funding_cost
borrow_cost
tax_or_stamp_duty
market_specific_fee
```

If any of these is ignored, state explicitly:

```text
ignored
```

Do not compare strategies with different cost assumptions unless the difference is disclosed.

## 8. PnL, Drawdown, and Sharpe Calculation

Metrics must state their calculation basis.

Required distinctions:

* trade-level PnL vs bar-level equity curve
* simple sum vs compounded return
* gross return vs net return
* annualized Sharpe vs trade-level simplified Sharpe
* realized equity curve drawdown vs trade-only drawdown

Minimum metrics file:

```json
{
  "total_return_pct": null,
  "annual_return_pct": null,
  "max_drawdown_pct": null,
  "sharpe": null,
  "sharpe_basis": "",
  "win_rate": null,
  "profit_factor": null,
  "n_trades": null,
  "avg_holding_bars": null,
  "cost_model": {},
  "notes": ""
}
```

If Sharpe is calculated from trade-level returns, it must be labeled:

```text
trade_level_simplified_sharpe
```

It must not be presented as equivalent to standard bar-level equity curve Sharpe.

## 9. Future Leak and Hindsight Audit

Trigger a mandatory honesty audit if the strategy contains:

* pivot confirmation
* swing high / swing low
* trendline
* support / resistance
* HH / LL
* segment lifecycle
* state machine with delayed confirmation
* regime labels that rewrite historical bars
* future bucket labels
* same-bar signal and execution

For such strategies, separate:

```text
hindsight/explanatory result
strict-causal/tradable result
```

A research report may show hindsight structures, but only strict-causal results may be used for strategy promotion.

## 10. Required Research Artifacts

A complete research run must produce:

```text
research/factor_runs/<name>/factor_memo.md
research/factor_runs/<name>/data_contract.md
research/factor_runs/<name>/audit_notes.md
research/factor_runs/<name>/reproduction.md
research/factor_runs/<name>/status.md

data/cache/<name>/manifest.json
data/cache/<name>/bars.parquet

data/features/<name>/factor_values.parquet
data/features/<name>/signals.parquet

reports/artifacts/<name>/trades.parquet
reports/artifacts/<name>/metrics.json
reports/artifacts/<name>/result_summary.md
```

## 11. Status System

Every research item must have one status:

```text
IDEA
SCOPED
PROTOTYPED
REVIEW_REQUIRED
REVIEWED
BENCH
PAPER_CANDIDATE
SHADOW_CANDIDATE
TINY_LIVE
LIVE
ARCHIVED
DROP
```

Default status for AI-generated or AI-assisted research:

```text
REVIEW_REQUIRED
```

## 12. Code Trust Levels

Code trust is separate from research status.

Use:

```text
A = trusted core
B = research usable
C = archived/reference
D = high risk, audit required
```

A file can only be marked `A` if:

1. Its input and output are clear.
2. It has at least one test or fixed reproduction case.
3. It does not hide data fetching, factor calculation, signal generation, and backtest logic in one opaque block.
4. Its assumptions are documented.
5. It has passed lookahead and timestamp checks where relevant.

## 13. Promotion Rule

No research item may be promoted to `PAPER_CANDIDATE` unless it has:

* frozen input data or frozen data manifest
* standalone factor values
* standalone signals
* standalone trades
* explicit cost model
* documented PnL and Sharpe calculation method
* no unresolved future-leak issue
* factor memo
* reproduction command
* reviewed status in Code Trust Map

## 14. Minimum Memo Questions

Each `factor_memo.md` must answer:

1. What is the idea?
2. Is it a factor, signal, strategy, filter, or report?
3. What market inefficiency does it claim to capture?
4. What data does it use?
5. What is the exact factor formula?
6. What is the exact signal rule?
7. When is the signal known?
8. When is the trade executed?
9. What are the cost assumptions?
10. How are PnL, drawdown, and Sharpe calculated?
11. What are the main results?
12. What would falsify this idea?
13. What is the current status?
14. What is the next action?
