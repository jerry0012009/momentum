# Rank none / perp-vs-quarterly annualized basis spread fade / fresh intake first verdict
- Time: 2026-04-21 17:30 UTC
- Cycle item: `research/quant_digests/2026-04-21_1245_perp-calendar-basis-spreadfade-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `background/P0`

## Why this was the front legal action
`Paper launch queue` is `none`, `Active P2` is `none`, survivor follow-up for `Rank 432` is already done, and the prior fresh intake item has already been resolved. The first remaining `pending` cycle item is therefore the perp-calendar basis spread fade intake.

## Minimal decisive blocker checked
The cycle item asked only one decisive question:

> under `BTC/ETH`, `5m/15m`, unified two-leg cost and timeout realism, does `annualized basis spread deviation × perp-vs-quarterly mean reversion` still leave an after-cost pocket that is not just conceptually correct but too thin to trade?

The existing digest and artifacts already answer that blocker directly.

## Evidence used
Digest: `research/quant_digests/2026-04-21_1245_perp-calendar-basis-spreadfade-alpha.md`
Artifacts referenced by the digest:
- `reports/artifacts/quant_digests/perp_calendar_summary_all_2026-04-21.csv`
- `reports/artifacts/quant_digests/perp_calendar_summary_15m_2026-04-21.csv`
- `reports/artifacts/quant_digests/perp_calendar_summary_5m_2026-04-21.csv`
- `reports/artifacts/quant_digests/perp_calendar_trades_15m_2026-04-21.csv`
- `reports/artifacts/quant_digests/perp_calendar_trades_5m_2026-04-21.csv`

Key first-verdict stats captured in the digest:
- `15m BTCUSDT vs BTCUSDT_260626`: `141` trades, gross `+1.33 bps/trade`, net `-6.67 bps/trade`
- `15m ETHUSDT vs ETHUSDT_260626`: `174` trades, gross `+2.20 bps/trade`, net `-5.80 bps/trade`
- `5m BTCUSDT vs BTCUSDT_260626`: `373` trades, gross `+1.84 bps/trade`, net `-6.16 bps/trade`
- `5m ETHUSDT vs ETHUSDT_260626`: `500` trades, gross `+2.14 bps/trade`, net `-5.86 bps/trade`

The digest also notes that raising entry threshold to `z>=3~4` or extending timeout still does not flip the results positive in this sample.

## Decision
This intake does **not** pass the front-slot standard for `keep_P1`.

Reason:
- the raw alpha family is coherent (`perp-vs-calendar basis mean reversion`),
- but the portable short-cycle edge visible here is only `~1–2 bps` gross per trade,
- which is far below the unified two-leg friction hurdle,
- and the remaining value is better described as a carry / inventory / timing overlay idea than a standalone front raw alpha.

## Runtime-changing conclusion
`annualized basis spread 偏离 × perp-vs-quarterly 回归` 的 fresh intake first verdict 已诚实收口：公开 `BTC/ETH` `5m/15m` portability probe 里单笔 gross 仅约 `1~2bps`，统一双腿 `8bps` 成本后整体稳定为负，且提高 `z` 阈值或拉长 timeout 也未翻正；它当前更像 carry / inventory overlay 的 timing layer，而不是值得前排保留的 standalone raw alpha，因此本轮直接收口 `background/P0`.

## Tail operations
- Homepage publish command `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ended with async process failure (`SIGKILL`); treated as non-blocking tail failure per policy.
- Email summary send succeeded (`send_text_email.py` returned success).
