# 2026-03-20 00:09 UTC — EMA crypto due refresh

## Context
- Trigger: `bot3-momentum-auto-opt-13m`
- Desk board source: `docs/TODO.md` / `TRADING DESK BOARD`
- Run claimed this round: `Run 1 / EMA due-now follow-up`
- Adjacent subpoint: refresh top board `Next 3 bot3 runs` after the due window was honestly consumed

## Pre-check
- Repo state: large pre-existing dirty workspace (`git status --short | wc -l = 1597` after this run); no selective commit attempted
- Paper seat status before action: `Crypto 1d+1wk -> 2026-03-20 00:00 UTC` had reached real due window
- P3 sidecar status: `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` at `2026-03-19T23:43:43Z` still showed `new_closed_trades_appended=0`, so no status-changing P3 event displaced the paper refresh

## What I ran
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```

## Result
- The due window was **honestly consumed**, not skipped:
  - `ema_paper_trading_refresh_history.csv` appended **1** new completed-bar row
  - total refresh-history rows increased to **21**
  - crypto lane advanced to `latest_completed_bar_utc=2026-03-19 00:00 UTC`
- Reader-facing page refreshed:
  - `reports/site/factors/ema_psar_raw_alpha/report.html`
- Latest refresh-history tail confirms the new row:
  - `2026-03-20 00:09 UTC,Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-19 00:00 UTC,...,ok_live_refresh,...`

## Post-refresh desk state
Latest `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` now shows:
- `创业板ETF 1d -> 2026-03-20 07:00 UTC` (`waiting_not_due`, ~6.8h)
- `贵州茅台 1d+1wk -> 2026-03-20 07:00 UTC` (`waiting_not_due`, ~6.8h)
- `沪深300ETF 1d -> 2026-03-20 07:00 UTC` (`waiting_not_due`, ~6.8h)
- `美股 1d+1wk -> 2026-03-20 20:00 UTC` (`waiting_not_due`, ~19.8h)
- `Crypto 1d+1wk -> 2026-03-21 00:00 UTC` (`waiting_not_due`, ~23.8h)

Hard conclusion:
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- This round was correctly spent on `Paper Seat`; no additional Scout main point was opened

## Desk-board update
Updated `docs/TODO.md` top-board `Next 3 bot3 runs` to reflect the honest post-refresh order:
1. `Run 1 = EMA due-check only` (next focus: A股 07:00 UTC)
2. `Run 2 = Rank 100 / fib-depth shallow-mid admission gate minimal clean replication` if EMA stays `waiting_not_due`
3. `Run 3 = Rank 101 / 3-step volume dry-down long-bias gate reserve source intake` only if Rank 100 clean replication hard-fails / exhausts

## Validation / notes
- The refresh command rebuilt the EMA site report and appended the refresh-history row, but the process returned exit code `2` after reporting `require-due` waiting state for the remaining lanes. Given the successful row append + regenerated artifacts, this is best read as a guard-state exit code rather than a failed refresh.
- No unrelated files were touched on purpose beyond the report/artifact/log/TODO updates.

## Artifacts touched
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `docs/TODO.md`
- `research/optimization_loop/2026-03-20_0009_ema-crypto-due-refresh.md`
