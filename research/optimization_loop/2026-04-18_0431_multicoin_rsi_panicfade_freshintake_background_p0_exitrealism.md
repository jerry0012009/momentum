# bot3 optimization loop — multicoin RSI panic fade fresh intake first verdict

- Time: 2026-04-18 04:31 UTC
- Target: `research/quant_digests/2026-04-17_2024_multicoin-rsi-panicfade-shell.md`
- Cycle item: item2 `conditional fresh intake`
- Verdict: `background/P0`

## Why this was the front pending action
Item1 (`RL pair dynamic scaling / excursion-aware sizing`) was already marked `done`, and there was still no active survivor / P2 / paper-launch wiring action ahead of this intake. Per current `cycle_plan`, the first legal pending small step was therefore item2: `major-coin oversold panic fade × hard stop / fixed TP` first verdict.

## Minimal honesty check executed
The digest's positive pocket relied on repo-style exits that effectively held until `RSI > 70` (with `+6% TP` rarely binding in the sampled `BTC/ETH 5m/15m` data). The cheapest decisive realism check was therefore:

- keep the same core entry: `RSI(14) < 30`
- force **next-bar entry**
- keep `-2%` stop and `RSI > 70` exit
- replace the repo's open-ended / oversized profit realization with a **short-cycle realistic time stop = 12 bars**
- charge the same round-trip cost used in the digest: `16 bps`
- symbols/frequencies checked: `BTCUSDT / ETHUSDT`, `5m / 15m`, recent `1000` bars from Binance public klines

## Result
Under the repo-style exit, the four major pockets were positive after cost:

- `BTC 5m`: `+18.73 bps/trade` (`12` trades)
- `BTC 15m`: `+17.28 bps/trade` (`13` trades)
- `ETH 5m`: `+23.56 bps/trade` (`14` trades)
- `ETH 15m`: `+11.75 bps/trade` (`13` trades)

But once the exit is compressed to a short-cycle realistic `12-bar` time stop, all four pockets flip negative after the same cost layer:

- `BTC 5m`: `-5.36 bps/trade` (`18` trades)
- `BTC 15m`: `-7.46 bps/trade` (`18` trades)
- `ETH 5m`: `-9.57 bps/trade` (`18` trades)
- `ETH 15m`: `-19.51 bps/trade` (`20` trades)

The key point is not that the repo's exact `+6% TP` fired often — it mostly did **not**. The problem is that the apparent edge depended on giving the trade a long, loose path to eventually mean-revert via `RSI > 70`, which is exactly the part that does not survive a more desk-realistic short-cycle exit discipline.

## System-level conclusion
`major-coin oversold panic fade × hard stop / fixed TP` does **not** survive as a new front-slot object once the exit is compressed from the repo's long/loose realization path to a short-cycle realistic holding window. What remains is a thin baseline story, not a clean independent survivor candidate.

Therefore this intake should be closed directly to `background/P0`, not kept as `P1`.

## Writeback sentence
`major-coin oversold panic fade × hard stop / fixed TP` 的可见正 pocket 主要依赖 repo 式宽松持有直到 `RSI>70` 的退出路径；一旦压成 short-cycle 更现实的 `12-bar` time-stop，`BTC/ETH 5m/15m` 四个 major pocket 在统一 `16bps` 后全部转负，因此本轮 fresh intake 直接收口 `background/P0`。
