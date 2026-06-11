# Rank none / ConnorsRSI triple-extreme overshoot × cross-back exit / fresh intake first verdict
- Time: 2026-04-21 18:30 UTC
- Cycle item: `research/quant_digests/2026-04-21_1718_connorsrsi-tripleextreme-router-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `background/P0`

## Why this was the front legal action
`Paper launch queue` is `none`, `Active P2` is `none`, `Surviving candidate slot` is `none`, and the first remaining `pending` cycle item is the ConnorsRSI fresh intake. Under the policy ladder this is therefore the current legal front action.

## Minimal decisive blocker checked
The cycle item asked only one decisive question:

> under `15m/5m`, unified cost, and strongest-only/router realism, does `ConnorsRSI triple-extreme overshoot × cross-back exit` still keep at least two same-direction after-cost symbol pockets that are not just broad mean-reversion gross or a few lucky pockets?

The existing digest already answers that blocker directly, so no extra axis expansion was needed.

## Evidence used
Digest: `research/quant_digests/2026-04-21_1718_connorsrsi-tripleextreme-router-alpha.md`
Artifacts referenced by the digest:
- `reports/artifacts/quant_digests/2026-04-21_connorsrsi_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_connorsrsi_probe_router.csv`
- `reports/artifacts/quant_digests/2026-04-21_connorsrsi_probe_trades.csv`

Key first-verdict stats captured in the digest:
- `15m` broad-pool: `2924` trades, gross `+2.19 bps/trade`, net after `8 bps` round-trip `-5.81 bps/trade`
- `5m` broad-pool: `4102` trades, gross `+0.94 bps/trade`, net after `8 bps` round-trip `-7.06 bps/trade`
- `15m` single-symbol gross pockets exist (`LTC +6.02`, `ADA +5.61`, `DOGE +3.86`, `BTC +2.71 bps/trade`), but they are still gross-only and do not clear the unified cost hurdle
- `15m top1 strongest-only`: next `8` bars mean gross about `+5.73 bps`; still below the `8 bps` round-trip hurdle
- `5m top1 strongest-only`: next `12` bars mean gross about `+1.74 bps`; also far below cost

## Decision
This intake does **not** pass `keep_P1`.

Reason:
- the alpha family is coherent as a `triple-extreme overshoot` scorer,
- but the portable short-cycle thickness stays below the unified cost hurdle in both broad-pool and router readings,
- and the apparent pockets remain gross-only / symbol-selective rather than two clear after-cost same-direction pockets.

So the honest read is that this is more useful as a mean-reversion router / scoring component than as a front-slot standalone raw alpha.

## Runtime-changing conclusion
`ConnorsRSI triple-extreme overshoot × cross-back exit` 的 fresh intake first verdict 已诚实收口：公开 `15m/5m` portability probe 里 broad-pool 分别只有约 `+2.19bps` 与 `+0.94bps` gross，`15m/5m` strongest-only router 也只到约 `+5.73bps / +1.74bps` gross，统一 `8bps` 成本后都没有留下至少两个同向 after-cost symbol pocket；它当前更像 mean-reversion overshoot 的 router / scorer，而不是值得前排保留的 standalone raw alpha，因此本轮直接收口 `background/P0`。

## Tail operations
- Homepage publish command `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 未成功完成（async 进程最终 `SIGKILL`）；按 policy 记为非阻断尾部失败，不影响本轮 verdict/state/log 生效。
- Email summary command `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] ConnorsRSI 收口为 P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-21_1830_connorsrsi_freshintake_background_p0.md` 成功发送。
