# bot3 optimization loop — Pacifica × Hyperliquid XEMM fresh intake first verdict

- Time: 2026-04-21 21:16 UTC
- Cycle item: 1
- Target: `research/quant_digests/2026-04-21_2053_pacifica-hl-maker-taker-xemm-shell.md`
- Action: fresh intake first verdict for `maker-on-thin-venue × taker-hedge-on-deep-venue`

## What I checked
Used the existing public top-of-book probe artifact for `BTC / ETH / SOL` on `Pacifica maker -> Hyperliquid taker`, with the repo default fee stack already applied:
- Pacifica maker fee: `1.5bps`
- Hyperliquid taker fee: `4.0bps`
- Tick-aware quoted best-price comparison
- No extra slippage added yet, so this is already the optimistic public-data upper bound

## Evidence
From `reports/artifacts/quant_digests/xemm_pacifica_hl_probe_summary_2026-04-21.csv`:

- `BTC`: `best_edge_mean≈-4.21bps`, `max_best_edge≈-2.33bps`, `hit_gt0=0/90`, `raw_best_gap_mean≈+1.29bps`
- `ETH`: `best_edge_mean≈-4.96bps`, `max_best_edge≈-3.34bps`, `hit_gt0=0/90`, `raw_best_gap_mean≈+0.54bps`
- `SOL`: `best_edge_mean≈-4.38bps`, `max_best_edge≈-2.69bps`, `hit_gt0=0/90`, `raw_best_gap_mean≈+1.12bps`

This means the publicly visible best-price dislocation exists, but it is only about `0.5~1.3bps` on average while the repo’s explicit fee floor is already `5.5bps` before any latency / fill uncertainty / depth-slippage realism.

The repo’s own target safety cushion is even higher (`profit_rate_bps=15`), so the single decisive blocker is already closed: the public top-of-book edge is not just thin, it is structurally far below the strategy’s own required execution buffer.

## Verdict
`maker-on-thin-venue × taker-hedge-on-deep-venue` does **not** earn `keep_P1`.

It currently reads as a strong execution shell for rare extreme dislocations, but not as a front-slot standalone raw alpha for the desk. With `0/90` positive snapshots across `BTC/ETH/SOL` even before adding depth-weighting, partial fills, latency decay, or cancel lag, there is no non-occasional after-cost pocket to preserve.

## State change
- Fresh intake first verdict: `background/P0`
- No survivor retained
- No rank assigned

## One-line result
`maker-on-thin-venue × taker-hedge-on-deep-venue` 的公开 top-of-book 跨 venue gap 在 repo 默认 maker+taker 费率下对 `BTC/ETH/SOL` 90 个样本全部费后为负（`>0bps=0/90`，最佳也仅 `-2.33~-3.34bps`），且离 repo 自己的 `+15bps` 安全垫很远，因此它当前只是高质量 XEMM 执行壳，不值得保留为前排 fresh intake，直接收口 `background/P0`。

## Tail actions
- Homepage refresh: attempted via `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`, but the process was killed after a long quiet run; treated as non-blocking tail failure.
