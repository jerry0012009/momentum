# 2026-03-17 22:22 UTC · Rank 35 park reframe review

## Scope
- Source rank: `Rank 35 VWAP pullback + trend-template qualifier`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 35 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- Needed evidence:
  - `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md`
  - `reports/site/reading/trendline_alpha_scout/rank35_vwap_pullback_clean_replication.html`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **one visible local pocket** instead of total collapse: `bias_plus_rsi_pullback` stayed modestly positive at `6bps/side` (`mean_total_return≈+2.71%`, `positive_asset_ratio≈100%`, `mean_trades≈12.0`).
- The main blocker looked concentrated in **VWAP anchor dependence + combo overspecification**, which makes it a better reframe candidate than ranks that simply hard-failed everywhere.
- It has not yet been reviewed by `bot6` in the recent park-reframe queue.

## 1) Why was Rank 35 parked?
Rank 35 was parked because the intended edge was **not the higher-tf trend bias itself**, but the stricter `VWAP reclaim + RSI pullback` entry story. That stricter story failed the current desk honesty bar:
- `combo_long_only` only produced about `3.7~4.0` trades on average, too thin for promotion;
- the middle time bucket turned negative for both allowed anchors;
- `bias_plus_vwap_reclaim` was clearly anchor-sensitive (`utc_day @ 6bps≈+8.69%` vs `funding_8h @ 6bps≈-0.51%`);
- therefore the apparent pullback story depended too much on implementation choice, while the deployable sample stayed too sparse.

## 2) Hard park or soft park?
**Closer to soft park.**

Reason:
- The original `VWAP pullback + RSI + trend-template` package does not pass.
- But the failure does **not** read like “directional idea is dead everywhere.”
- It reads more like “the current packaged entry is too strict and the VWAP piece is the least honest part.”

So the original verdict should stay parked, but it looks more like a **soft park with one narrow salvage axis** than a terminal hard park.

## 3) Is there any rescue signal?
Yes — but only a small one.

Most useful rescue signal:
- `bias_plus_rsi_pullback` kept a modest positive read without needing VWAP:
  - `6bps/side ≈ +2.71%`
  - `positive_asset_ratio ≈ 100%`
  - `mean_trades ≈ 12.0`
- That is still thin and not enough for direct promotion.
- But it suggests the **higher-tf bias + simple RSI pullback timing** may contain more honest information than the full VWAP reclaim combo.

What does **not** count as rescue:
- `baseline_higher_tf_bias≈+53.93%` is not a rescue for Rank 35 specifically; that mostly says the trend proxy itself had directionality in this sample.
- `bias_plus_vwap_reclaim` is not a rescue because it is exactly where anchor sensitivity becomes obvious.

## 4) The single best modification axis
**Remove the VWAP reclaim requirement; keep the higher-tf bias + RSI pullback reclaim entry.**

This is the narrowest honest cut because it:
- keeps the long-only pullback framing;
- keeps the same higher-tf trend qualifier;
- keeps the same fixed-hold execution style;
- removes only the least stable / most anchor-sensitive gate.

It does **not** expand into multi-axis surgery like changing universe + exits + anchors + regime filters at once.

## 5) Is a new derived hypothesis worth drafting?
**Yes — `derived_hypothesis_drafted`.**

Not because Rank 35 is suddenly good enough to unpark.
Because the evidence is enough to justify one narrow derived hypothesis that `bot2` could later choose to intake if fresh sources are exhausted.

## 6) Proposed derived hypothesis
- `proposed_rank`: `Rank 35b`
- `source_rank`: `Rank 35`
- `single modification axis`: `remove VWAP reclaim requirement; keep higher-tf bias + RSI pullback reclaim`
- `trade on`: `higher-tf trend bias stays true, and RSI14 first tags pullback territory (<=35 in recent window) then reclaims above 40; enter next-bar open, fixed 8-bar hold, long-only`
- `trade off`: `higher-tf bias absent, or RSI pullback-reclaim does not happen; explicitly give up VWAP-based reclaim confirmation`
- `trade on / trade off` summary in plain words: keep “顺势回调后再接回去” 的故事，但不再要求 VWAP 那道最容易因 anchor 选法而变形的门
- `trade on`: simpler, less anchor-sensitive pullback timing
- `trade off`: more noise / weaker confirmation, so false entries may rise
- `why now`: original clean replication already showed the combined variant was too sparse and VWAP was the unstable leg, while the RSI-only pullback slice retained a small positive pocket
- `suggested initial state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `reframe_quality`: `soft park -> narrow derived hypothesis worth drafting`

## Minimal audit note
This round does **not** reopen Rank 35 itself.
It only records that if the desk later wants one narrow reframe candidate from the parked pool, the most honest single-axis derivative is: **Rank 35b = delete VWAP reclaim, keep higher-tf bias + RSI pullback reclaim.**
