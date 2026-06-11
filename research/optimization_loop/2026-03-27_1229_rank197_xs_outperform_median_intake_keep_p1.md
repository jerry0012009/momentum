# Rank 197 intake — xs outperform-median stat-arb keep_P1

- Time: 2026-03-27 12:29 UTC
- Target: `research/quant_digests/2026-03-27_1123_xs-outperform-median-statarb.md`
- Verdict: `keep_P1`
- Assigned Rank: `Rank 197`

## What was checked
- Re-read the digest and its linked local quick-check artifact `reports/artifacts/tmp_stat_arb_rf_5m_summary.txt`.
- Enforced first-intake scope only: decide whether this is worth preserving as a clean-room market-neutral raw-alpha object, not whether the 2018 paper transfers directly into a 2026 production edge.

## Evidence that matters
- The object definition is unusually clean and reproducible: cross-sectional relative-strength ranking, long top / short bottom, hold for ~120m, with explicit cost hooks and public-code lineage.
- The current public transfer check is cold, not supportive of direct promotion: Binance USDT perp `5m` quick check over `2026-03-12 ~ 2026-03-26` shows about `-20.8 bps/day`, daily t about `-1.22`, and only `26.7%` positive days.
- That negative transfer result is enough to reject any immediate `P2` story, but it is not enough to park the theme entirely, because the current failure is still bundled with a heavy paper-era RF framing and a narrow quick-check implementation.
- The real reusable alpha kernel here is cheaper and narrower: `lagged-return cross-sectional ranking` rather than `paper RF headline`.

## Decision
This intake is worth keeping as exactly one survivor, but only in compressed clean-room form.

`Rank 197 / top-vs-bottom lagged-return XS ranking` should be treated as:

> 在 liquid perp universe 上，用过去多窗口 lagged returns 做横截面排序；每个 rebalance 时做多排名最强的一篮子、做空最弱的一篮子，持有约 120 分钟，检验其 market-neutral top-minus-bottom spread 在成本后是否仍保留正向雏形。

Why `keep_P1` instead of `park`:
- The alpha object is specific, cheap to restate, and directly testable without inheriting the old RF machinery.
- It fills a real desk gap: a clean market-neutral XS baseline, complementary to single-name directional ideas.
- The first quick check already rules out naive “paper headline -> 2026 tradable edge”, which is good; the remaining honest next step is a single stripped-down clean-room follow-up on the simpler ranking baseline.

Why not `P2`:
- Recent transfer is negative.
- No post-cost contemporary evidence yet that the simplified ranking form survives across universe / timeframe / cost choices.

## Runtime writeback
- Fresh intake slot: update this digest to `Rank 197` with first verdict `keep_P1`.
- Surviving candidate slot: occupy it with the compressed object above and restore one follow-up budget.
- Cycle-plan item 4: mark `done` with the `keep_P1` result.

## Reader-facing takeaway
The thing worth preserving is not “2019 crypto random forest stat-arb works again”; it is the smaller and more honest mother-object underneath it:

**Rank 197 = top-vs-bottom lagged-return cross-sectional market-neutral ranking alpha.**

The paper/repo makes that object concrete, but the recent quick check is already negative enough that the next step must be a cheap clean-room baseline test, not a credibility leap.