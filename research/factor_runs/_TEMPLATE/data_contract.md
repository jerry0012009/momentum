# <Research Name> — Data Contract

## 1. Data Sources

| Source | Market | Symbols | Timeframe | Adjusted/Raw | Notes |
|---|---|---|---|---|---|
| `<provider>` | `<market>` | `<symbols>` | `<1d/1h/15m/etc.>` | `<adjusted/raw>` | |

## 2. Data Entry Points

List all functions, scripts, APIs, or files that introduce data into the research.

| Entry Point | Path / Function | Runtime Fetch? | Frozen? | Notes |
|---|---|---:|---:|---|
| script | `<path>` | yes/no | yes/no | |
| function | `<function>` | yes/no | yes/no | |
| file | `<path>` | no | yes/no | |

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

## 3. Required Input Schema

Minimum OHLCV schema:

```text
timestamp
symbol
open
high
low
close
volume
market
timeframe
source
adjusted_or_raw
```

Additional fields if needed:

```text
quote_volume
trade_count
funding_rate
open_interest
basis
spread
```

## 4. Time and Timezone Rules

- Storage timezone:
- Display timezone:
- Timestamp format:
- Bar close convention:
- Signal generated at:
- Tradable at:

Important rule:

```text
signal_time and execution_time must be explicitly separated.
```

## 5. Universe Definition

- Universe name:
- Inclusion rule:
- Exclusion rule:
- Universe fixed at:
- Rebalanced at:
- Survivorship bias risk:

## 6. Frozen Data Targets

Required if the research is rebuilt or promoted:

```text
data/cache/<name>/bars.parquet
data/cache/<name>/manifest.json
```

Manifest template:

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

## 7. Missing Data Handling

- Missing bars policy:
- Duplicate timestamp policy:
- Outlier policy:
- Suspended / delisted symbols policy:
- Newly listed symbols policy:

## 8. Known Data Risks

- [ ] Runtime fetch means exact reproduction is not guaranteed
- [ ] Provider may revise historical data
- [ ] Adjustment policy is unclear
- [ ] Timezone normalization is incomplete
- [ ] Universe may have survivorship bias
- [ ] Multiple providers are mixed without normalization
- [ ] Missing bars are not handled explicitly

## 9. Data Status

```yaml
data_status: <UNFROZEN | SNAPSHOT_CREATED | VERIFIED>
manifest_status: <MISSING | CREATED | VERIFIED>
reproduction_status: <UNVERIFIED | PARTIAL | VERIFIED>
```

Notes:

- 
