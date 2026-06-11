# Rankless fresh intake — cross-sectional funding carry × breakout net-bias shell -> background/P0

- Time: 2026-04-23 08:41 UTC
- Target: `research/quant_digests/2026-04-22_1945_xs-fundingcarry-breakout-shell.md`
- Cycle action: fresh intake first verdict
- Verdict: `background/P0`

## What changed system belief

`cross-sectional funding carry × breakout net-bias shell` 没有证明自己相对已 live `Rank 389 / cross-venue net-carry ranking alpha` 留下新的独立 after-cost alpha：当前 public probe 只确认方向上更像 continuation，但 liquid majors 的平均 funding spread 只有约 `1.88bps`，gross 仅 `+1.01bps/8h`，统一最小多空 round-trip `8bps` 后约 `-6.99bps/笔`；因此新增价值主要退化为 `8h parent carry rank + maker-first child execution / breakout bias overlay` 的 router 提示，而不是值得前排保留的新对象。

## Minimal decisive blocker used

只用了一个 blocker：**它是否真比现有 carry/ranking family 多出可独立排队的 after-cost alpha**。

### Evidence

From `reports/artifacts/quant_digests/xs_funding_carry_probe_summary_2026-04-22.csv`:

- `gross_continuation`: `n=183`, `mean_bps=+1.01`, `cum_return_pct_simple=+1.85%`, `Sharpe_8h≈0.44`
- `net_continuation_8bps`: `mean_bps=-6.99`, `cum_return_pct_simple=-12.79%`, `Sharpe_8h≈-3.03`
- `gross_reversal`: `mean_bps=-1.01`

This is enough to say the signal direction is continuation, but not enough to survive honest costs.

From `reports/artifacts/quant_digests/xs_funding_carry_probe_assets_2026-04-22.csv`:

- mean funding spread across the long-short event set is only about `1.88bps`
- more active names are `SOL/AVAX/XRP/ADA/LINK`, but the artifact does not show a non-single-window, independently durable after-cost pocket that clearly escapes the already-live carry/ranking family

## Why this is not `keep_P1`

To keep `P1`, this object needed to show at least one non-single-coin / non-single-month lucky-run after-cost pocket that is distinct from the existing live carry/ranking stack. It did not.

The honest residual is:

- carry rank can still be useful as an `8h parent router`
- breakout can still be a `net-bias overlay`
- maker-first child execution may still matter

But those are implementation/design hints, not a new queue-facing alpha object.

## Runtime impact

- current cycle item marked `done`
- fresh intake latest result updated to `background/P0`
- no survivor retained
- no P2/P3 movement
