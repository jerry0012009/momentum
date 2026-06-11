# Final Objective: Honest Small-Live Strategy Pipeline

## Goal

Build and run one strategy from the current `momentum` project that is:

- causal, with no future function or hindsight universe/parameter selection;
- positive after explicit cost and funding/slippage assumptions;
- frequent enough to falsify in live market conditions;
- reasonably stable across adjacent time windows and parameter neighborhoods;
- implemented through one shared signal path for replay, shadow, and live order planning;
- run with tiny real notional only after a binary release gate;
- continuously compared against the exact replay/shadow expectation.

This is not a request for more broad research, rank expansion, or cosmetic reporting. The endpoint is either tiny real-money falsification or rejection of the candidate.

## Non-Negotiable Release Gate

| Gate | Required Evidence |
| --- | --- |
| Causality | Signal timestamp uses only bars/data completed before decision time. |
| Universe honesty | No current-active-only, future volume, future listing survival, or hindsight hot-coin selection. |
| Frozen spec | Universe rule, signal formula, side, horizon, cost, funding, sizing, veto, gate, and kill switch are fixed before final replay. |
| Positive edge | Net return is positive after costs in the chosen frozen replay and not concentrated in one isolated burst. |
| Trigger frequency | Expected live triggers are frequent enough for tiny-live falsification without waiting months. |
| Time stability | Adjacent windows and coarse parameter neighborhoods do not flip from viable to clearly dead. |
| Unified code path | Replay, shadow, and live order plan call the same signal implementation. |
| Executability | Entry, exit, residual flatten, duplicate-open guard, ledger, and account reconciliation are defined. |
| Live-vs-shadow | Every live order has a comparable shadow/replay row with delta fields. |
| Binary outcome | Release gate outputs exactly `launch_tiny_live` or `reject_before_live`. |

## Current Candidate State

| Candidate | Current Evidence | Blocking Issue |
| --- | --- | --- |
| `rank32c_btc_utc_weak_cell_v1` | Unique BTC-only spec and guarded release package exist. | Rejected: current May 2026 plan cannot be generated from stale local 15m cache. |
| `rank32b_global_live` | Already has live runner, state, order logging, and live-vs-shadow artifact. | Long-window stability artifacts were withdrawn after warmup audit; longer live-like windows are not positive enough to satisfy the final objective. |
| `rank213_age90_14d_skip1d_voladj` | Phase 3 validation unresolved issues, but live canary active since 2026-05-06. Signal engine cross-validated against backtest (identical output). | Tiny-live falsification in progress. Phase 3 issues (drawdown, cost sensitivity, walk-forward fragility, weak short-side) remain unresolved. |
| `rank154_crypto_stat_arb` | Current daily forward paper runner is active through 2026-05-03, positive lifetime return, daily trigger cadence, completed-bar design, and funding/cost accounting. | Needs a dedicated no-lookahead audit, time/parameter stability check, and a tiny-live order/reconciliation package before promotion. |
| `rank151_ewmac_breakout_bandpass_gate` | Positive paper status and high trade count. | Frozen digest seed is stale and not yet raw-bar live aligned. |

## Working Priority

`rank213_age90_14d_skip1d_voladj` is currently running as a tiny-live canary (since 2026-05-06). The immediate priority is to accumulate real-money samples and evaluate whether the Phase 3 issues (drawdown, cost sensitivity, walk-forward fragility, weak short-side) are survivable in live conditions.

`rank154_crypto_stat_arb` remains the next candidate for a formal release gate — it is current, runs daily, has positive paper equity, includes cost/funding accounting, and has a simple daily rebalance lifecycle. It is not approved for live yet.

## Current Stance

`rank213_age90` is running tiny-live for real-money falsification, not because it passed the release gate. `rank154` remains the strongest formal-gate candidate.
