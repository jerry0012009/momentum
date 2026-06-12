# <Research Name> — Factor Memo

## 1. What is the idea?

Describe the research idea in one paragraph.

Minimum:

- What market phenomenon does it try to capture?
- Why might it work?
- Is the expected edge directional, cross-sectional, carry-based, volatility-based, liquidity-based, or regime-based?

## 2. Research Type

```yaml
research_type: <factor | signal | strategy | filter | report | old_research_asset>
contains_factor: true/false
contains_signal: true/false
contains_strategy_rules: true/false
```

Important distinction:

> A strategy may contain factors, but the strategy itself is not automatically a clean factor.

## 3. Factor Definition

List all factors or indicators used.

| Factor | Formula | Window | Known At | Notes |
|---|---|---:|---|---|
| `<factor>` | `<formula>` | `<n bars>` | `<close[t] / open[t+1] / etc.>` | |

If no standalone factor exists yet, state:

```text
No standalone factor_values artifact exists yet.
```

## 4. Signal Definition

| Signal | Rule | Signal Time | Tradable At | Notes |
|---|---|---|---|---|
| entry_signal | | | | |
| exit_signal | | | | |

Explicitly distinguish:

```text
signal_time != execution_time
```

## 5. Strategy Rules

Only fill if the research item is a strategy.

### Entry

- Direction:
- Sizing:
- Entry trigger:
- Entry execution price:

### Exit

- Exit trigger:
- Stop loss:
- Take profit:
- Time exit:
- Reversal exit:

### Costs

- Commission:
- Slippage:
- Spread:
- Funding / borrow / tax:

## 6. Data Used

- Source:
- Symbols / universe:
- Timeframe:
- Data start:
- Data end:
- Adjusted or raw:
- Frozen snapshot exists: yes/no
- Manifest exists: yes/no

## 7. Current Results

Summarize only results that are supported by existing artifacts.

| Metric | Value | Basis | Notes |
|---|---:|---|---|
| Total return | | gross/net | |
| Max drawdown | | bar-level/trade-level | |
| Sharpe | | standard/trade-level simplified | |
| Win rate | | | |
| Number of trades | | | |

## 8. Trust Assessment

### Credible parts

- 

### Unreliable / unresolved parts

- 

### Blocking issues

- 

## 9. Falsification Criteria

What result would cause this idea to be dropped?

Examples:

- performance disappears after next-bar execution;
- performance disappears after realistic slippage;
- alpha comes only from one asset or one year;
- standard bar-level Sharpe is near zero;
- factor has no cross-sectional IC stability.

## 10. Current Status and Next Action

```yaml
research_status: REVIEW_REQUIRED
next_action: <archive | rebuild | promote | drop | park>
```

Recommended next action:

- 
