# Phase 12D-C: Pipeline Detail and Factor Source Map

## Status: COMPLETE
## Date: 2026-06-18
## Previous Phase: 12D-B-R

---

## Background

User requested detailed pipeline information, data ranges, and factor source mapping for the momentum project. This phase documents the full data pipeline specifics including crypto-native data inventory, dynamic Top50 symbol explanation, and a comprehensive factor source map linking all 17 factors to their origin scripts, data sources, and pipeline positioning.

## Changes Made

### New Files Created
- `reports/site/factor-library/crypto-native-inventory.html` — HTML page documenting crypto-native data availability
- `reports/site/factor-library/crypto_native_inventory.json` — JSON data for crypto-native inventory
- `reports/site/factor-library/crypto_native_inventory.md` — Markdown version of crypto-native inventory
- `reports/site/factor-library/factor-source-map.html` — HTML page with full factor source mapping
- `reports/site/factor-library/factor_source_map.json` — JSON data for factor source map
- `reports/site/factor-library/factor_source_map.md` — Markdown version of factor source map

### Updated Files
- `reports/site/factor-library/actual-script-map.html/json/md` — Added data ranges (2024-06 → 2026-06-13, 266 symbols), crypto-native inventory references, dynamic Top50 explanation, factor source map link, Phase 9B/10A/10D/12 positioning
- `reports/site/factor-library/data-lineage.html` — Added dynamic Top50 explanation
- `reports/site/factor-library/index.html` — Added navigation links to new pages

## Data Range
- **Start**: 2024-06
- **End**: 2026-06-13
- **Universe**: 266 symbols

## Crypto-Native Data Inventory
| Data Type | Availability | Notes |
|---|---|---|
| Funding Rate | Available | From exchange APIs |
| Open Interest (OI) | NOT available | Not sourced in current pipeline |
| Liquidations | Available | Derived from trade data |
| Order Book Depth | Available | Snapshot-based |

## Dynamic Top50 Explanation
The Top50 symbol list is recalculated periodically based on market cap and liquidity metrics. It is not a static list — symbols rotate in and out as market conditions change.

## Factor Source Map (17 Factors)
All 17 factors are mapped to their source scripts, data inputs, and pipeline phase positioning (Phase 9B, 10A, 10D, 12).

## Phase Positioning
- **Phase 9B**: Core momentum factor computation
- **Phase 10A**: Cross-sectional normalization
- **Phase 10D**: Composite scoring
- **Phase 12**: Final portfolio construction and reporting

## Disclaimers
- **Phase 13 NOT STARTED** — No implementation, no backtest, no live trading
- **No real execution** — All outputs are documentation artifacts, not live data
- **No alpha claim** — No assertion of edge or profitability
- **No production claim** — Not deployed, not running, not live
- **No research results changed** — Documentation only; no underlying data or computations were modified
