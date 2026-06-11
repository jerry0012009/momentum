# Rankless fresh intake — opposite-sign funding spread × order-book slippage veto × 8h max-hold -> background/P0

- Time: 2026-04-25 11:34 UTC
- Executor: bot3
- Cycle-plan slot: #2
- Target: `research/quant_digests/2026-04-25_1037_oppositesign-funding-slippageveto-shell.md`
- Action: fresh intake first verdict with one minimal decisive blocker check

## What changed system belief
`opposite-sign funding spread × order-book slippage veto × 8h max-hold` first verdict closes at `background/P0`: the public three-venue majors probe shows the opposite-sign pocket exists but is too thin after realistic fee/slippage hurdles, so the repo currently contributes an event-scanner/deployment shell rather than a standalone, reusable after-cost raw alpha worth keeping in P1.

## Minimal decisive blocker used this round
The only blocker tested was the one named in the cycle plan: whether public majors still leave a reusable after-cost cross-venue carry pocket after fee/slippage-aware admission, instead of just a full strategy shell.

Evidence used:
- digest: `/root/clawd/jerry/momentum/research/quant_digests/2026-04-25_1037_oppositesign-funding-slippageveto-shell.md`
- artifact summary: `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_crossvenue_funding_oppositesign_probe_summary.csv`
- artifact detail: `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_crossvenue_funding_oppositesign_probe_detail.csv`

## Decisive read
Across the latest 51 aligned funding periods on Binance / Bybit / OKX:
- `BTCUSDT`: opposite-sign seen 22/51 times, but gross mean only `0.71 bps / 8h`; repo-style `gross - 4 bps` mean `-3.29 bps`; maker four-leg mean `-6.38 bps`; taker four-leg mean `-18.65 bps`.
- `ETHUSDT`: opposite-sign seen 26/51 times, but gross mean only `0.96 bps / 8h`; repo-style `gross - 4 bps` mean `-3.04 bps`; maker four-leg mean `-5.50 bps`; taker four-leg mean `-19.73 bps`.
- `SOLUSDT`: opposite-sign seen 12/51 times, but gross mean only `1.00 bps / 8h`; repo-style `gross - 4 bps` mean `-3.00 bps`; maker four-leg mean `-5.16 bps`; taker four-leg mean `-19.00 bps`.

That is enough to answer the first-verdict question honestly: on public large venues, the portable edge is not a durable after-cost pocket. The repo's real value is execution framing:
- opposite-sign funding admission
- fee-aware gating
- order-book slippage veto
- 8h max-hold/time-boxing

Those are useful deployment-shell components, but they do **not** by themselves establish a new tradable alpha family independent of existing live/candidate books.

## Verdict
- Verdict: `background/P0`
- Rank assignment: none, because it did not reach `keep_P1` or higher.
- Reason not to keep P1: there is no venue-pair/asset scope in the presented public probe that remains clearly positive under a unified realistic cost lens; keeping it in front slots would over-credit shell completeness versus actual portable edge.

## Runtime writeback required
- Mark cycle-plan item #2 as `done`.
- Write result sentence reflecting `background/P0` first verdict.
- Refresh Fresh intake slot latest result / latest result record to this verdict.

## Tail-step notes
Homepage publish and email are attempted separately after state writeback; tail-step failure does not roll back this verdict.
