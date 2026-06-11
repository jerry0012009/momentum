# 2026-03-18 03:57 UTC — BotScalpingTwinRange / PSAR anchor + EMA confirm clean replication

## Context
- Trigger: bot3 13m auto desk run
- Desk state at start:
  - `Run 1 / EMA` = `running paper / waiting_not_due`
  - `Run 2 / Scout Seat` active and required by top `TRADING DESK BOARD`
  - Fresh source chosen from current active Scout candidates by marginal value: `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm`
- Why this one:
  - `Rank 43` and `Rank 40` had just spent their one fast-lane clean-replication budget and were already back in `park / evidence pool`
  - `Rank 17 / Rank 2 / Rank 29 / Rank 32b` were all existing `P3` lanes without a new due-now status-changing event
  - This repo source had already passed the two lightweight honesty gates at `03:39 UTC`, so the highest-value allowed next move was its single minimal clean replication

## Repo / workspace check
- Git head: `e2e1db4`
- There were many unrelated dirty/untracked files already present in the repo and parent workspace before this turn.
- I kept this turn scoped to:
  - `scripts/build_repo_psar_anchor_ema_confirm_clean_replication.py`
  - `reports/artifacts/scout_repo_psar_anchor_ema_confirm_15m/`
  - `reports/site/factors/scout_repo_psar_anchor_ema_confirm_15m/report.html`
  - `docs/TODO.md`
  - this run log

## Claimed point
- **Main point:** the one allowed minimal clean replication for `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm`
- **Adjacent sub-point:** authoritative board write-back + reader-facing report landing

## What I froze
Instead of inheriting the repo’s heavy execution stack (`ALWAYS_IN_MARKET`, multi-pair ranking, `30m/5m/1m` plumbing), I compressed it into one honest clean-room comparison:

### Shared execution freeze
- sample: `BTC / ETH / SOL` local Binance `120d 15m` cache
- entry: `signal bar close -> next-bar open`
- exit: fixed hold `8` bars
- overlap: `no-overlap`
- costs: `6 / 10 / 15 / 20 bps per side`

### Three arms
1. `EMA_raw`
   - `trade on = 15m EMA20 > EMA50 and ema_fast 3-bar slope > 0.0003` (short mirrored)
2. `PSAR_raw`
   - `trade on = 15m PSAR flips direction`
3. `PSAR_anchor+EMA_confirm` (primary)
   - `trade on = 1h PSAR direction permits side, then 15m EMA20 > EMA50 + slope > 0.0003, and close is on the fast-EMA-confirmed side`

### Early-failure proxy
- `flip_to_fail = within first 4 bars mark-to-market turns negative OR same-arm opposite signal appears`

## Deliverables produced
- Script:
  - `scripts/build_repo_psar_anchor_ema_confirm_clean_replication.py`
- Artifact directory:
  - `reports/artifacts/scout_repo_psar_anchor_ema_confirm_15m/`
- Reader-facing page:
  - `reports/site/factors/scout_repo_psar_anchor_ema_confirm_15m/report.html`
- Board write-back:
  - `docs/TODO.md`

## Hard result
### Aggregate summary (`6bps/side`)
- `EMA_raw`
  - `mean_total_return≈-47.28%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈487.7`
  - `mean_flip_to_fail_rate≈53.75%`
- `PSAR_raw`
  - `mean_total_return≈-62.96%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈654.0`
  - `mean_flip_to_fail_rate≈52.14%`
- `PSAR_anchor+EMA_confirm`
  - `mean_total_return≈-27.84%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈455.3`
  - `mean_flip_to_fail_rate≈50.70%`

### Cross-asset primary-arm read (`6bps/side`)
- `BTC ≈ -25.87%`, `trades=439`, `flip_to_fail≈50.57%`
- `ETH ≈ -29.06%`, `trades=454`, `flip_to_fail≈53.52%`
- `SOL ≈ -28.59%`, `trades=473`, `flip_to_fail≈47.99%`

### Time stability (primary arm, `6bps/side`)
- `bucket_1 ≈ -12.81% / positive_asset_ratio=0/3`
- `bucket_2 ≈ -17.23% / positive_asset_ratio=0/3`
- `bucket_3 ≈ +0.89% / positive_asset_ratio=1/3`

### Cost slope (primary arm)
- `6bps ≈ -27.84%`
- `10bps ≈ -49.87%`
- `15bps ≈ -68.21%`
- `20bps ≈ -79.84%`

## Verdict
- **Hard verdict:** `park / evidence pool`
- Reason in plain language:
  - The anchor+confirm version is **less bad** than raw EMA and raw PSAR.
  - It does reduce early failure somewhat.
  - But that is not enough: after costs it is still `0/3` assets positive, and the time pockets do not show a durable survival zone.
  - So this repo idea can stay as **engineering/structure evidence**, but not as an active Scout candidate that deserves more default budget.

## Board / routing consequence
- Updated top board so the next default order becomes:
  - `Run 1 = EMA due-check (skip if still waiting_not_due)`
  - if still waiting: compare `Rank 27b > Rank 35b > Run 3 / tiny-live plumbing`
- Explicitly **do not** keep polishing this repo template next round unless bot2 points to a genuinely verdict-changing new fact.

## Validation / completion notes
- The replication script completed successfully with exit code `0`.
- Verified that these landed:
  - artifact directory exists
  - site report exists
  - TODO write-back present and deduplicated
  - current-window authoritative paragraph updated to `03:57 UTC`

## Commands run
- `python3 scripts/build_repo_psar_anchor_ema_confirm_clean_replication.py`
- board cleanup patch for duplicated TODO note

## Final status
- Main point completed
- Reader-facing landing completed
- Next natural Scout fallback is **fresh intake / park-reframe comparison (`Rank 27b > Rank 35b`)**, not more continuity work on this line
