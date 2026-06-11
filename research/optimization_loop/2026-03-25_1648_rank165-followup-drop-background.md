# Rank 165 survivor follow-up — drop to background after Binance large-cap perp transfer probe

- Time: 2026-03-25 16:48 UTC
- Target: Surviving candidate slot
- Rank: `Rank 165 / positive-jump variance lottery fade`
- Verdict: `drop_to_background`
- Probe artifact: `research/optimization_loop/tmp_rank165_probe.json`

## What was tested
Used a minimal but desk-relevant transfer probe on Binance USDⓈ-M perpetuals:
- universe: top 12 liquid USDT perpetuals by current quote volume (`BTC/ETH/SOL/TAO/SIREN/XRP/DOGE/ONT/ZEC/PAXG/HYPE/BNB` in this snapshot)
- bar size: `15m`
- sample: last `20d` (`1200` aligned bars)
- signal: trailing `72h` positive-jump variance proxy = `sum(r^2 for positive returns > 1 * rolling sigma)`
- portfolio: `long bottom quartile / short top quartile`
- holding windows: `4h / 12h / 24h`
- cost: conservative flat `6 bps round trip`

## Result
The large-cap perp transfer comes out decisively negative rather than just weaker:
- `4h`: gross `-57.9 bps`, net `-63.9 bps`
- `12h`: gross `-157.7 bps`, net `-163.7 bps`
- `24h`: gross `-305.6 bps`, net `-311.6 bps`

Hit rate is also poor (`34.0% / 21.8% / 11.9%` gross across `4h / 12h / 24h`), so this is not a “small positive edge killed only by fees” story; in this tradable large-cap-perp slice the sign is already wrong before costs.

## Why this changes the verdict
The survivor question was narrow: does the paper’s cross-sectional long-low / short-high positive-jump-variance edge keep enough net edge after a Binance large-cap perp transfer to justify `P2`?

This probe says **no**. The simplest tradable desk transfer not only fails to retain positive spread return, it flips strongly negative across all tested holding windows. That means the current evidence points to the paper edge living outside the desk’s realistic large-cap perp implementation, rather than surviving as a near-ready tradable candidate.

## Result sentence
`Rank 165 / positive-jump variance lottery fade` fails its only survivor follow-up: once transferred into a Binance large-cap perp basket with realistic long/short construction and a simple post-cost holding test, the spread turns strongly negative across 4h/12h/24h, so it does not earn `P2` and returns to `Background pool`.
