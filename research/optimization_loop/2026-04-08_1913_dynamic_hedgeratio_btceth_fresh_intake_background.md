# Rankless fresh intake verdict — dynamic hedge-ratio BTC/ETH pairs fade -> background / P0

- Time: 2026-04-08 19:13 UTC
- Target: `research/quant_digests/2026-04-08_1429_dynamic-hedgeratio-btceth-pairs-fade-alpha.md`
- Cycle slot: `cycle_plan[3]`
- Action: fresh intake first verdict + minimal honesty / execution-realism check

## What I checked
1. Re-read the digest itself, especially its own portability section and explicit caveats.
2. Cross-checked against existing pairs-family baselines already in the repo:
   - `2026-03-26_1505_plain-pairs-longshort-vs-longonly.md`
   - `2026-03-29_2058_btc-eth-beta-neutral-sizing-alpha.md`
   - `2026-04-01_1850_hyperliquid-cointegration-halflife-pairs-alpha.md`
3. Applied the cheapest honesty question that could still flip the verdict: does this intake already prove a distinct queue-facing alpha survives beyond friendly close-to-close execution assumptions?

## Decision
`dynamic hedge-ratio BTC/ETH spread × z-score fade` 本轮 fresh intake 收口为 `background / P0`，不升 `keep_P1`。

## Why
### 1) Its real increment is implementation tightening inside the existing pairs family
This digest does add something useful: it reinforces that **dynamic hedge ratio** compresses spread noise better than static ratio, and that short-cycle pairs should not be read as a dashboard story.

But that increment is still mostly **within** an already-covered family:
- plain pairs / spread convergence baseline already exists;
- BTC/ETH beta-consistent sizing already exists as a more specific execution-layer lesson;
- dynamic-hedge-ratio + pair admission shells already exist in the broader cointegration pairs family.

So the new object is better read as:
- **"dynamic beta alignment is an important implementation/governance upgrade for pairs"**
not as:
- **"a new independent queue-facing raw alpha family"**.

### 2) The decisive blocker is still execution realism, and the digest explicitly admits it is unresolved
The digest's own best numbers come from a friendly simplification:
- synchronized bar-close spread,
- zero impact,
- no funding,
- no next-bar execution lag.

It explicitly says the next thing to test is `close-to-close vs next-bar-open` and cost laddering. That means the one cheapest honesty axis that could change the system verdict is still **open**.

For a fresh intake to earn `keep_P1`, I need evidence that the distinct new subject survives at least one decisive realism check. Here, the claimed edge is still too entangled with friendly fill assumptions.

### 3) The repo's best contribution is better preserved as a family-level lesson
The durable takeaway worth keeping is:
- short-cycle pairs should default to **dynamic beta / hedge-ratio-aware alignment**,
- then test spread fade under realistic entry/exit and cost routing.

That is a valuable research lesson, but it is not enough to justify a new front-slot identity.

## Runtime-changing sentence
`dynamic hedge-ratio BTC/ETH spread × z-score fade` 当前新增的是对既有 pairs / stat-arb family 的实现层收紧：它说明 dynamic beta alignment 可能优于 static ratio，但现有 portability 仍主要建立在过于友好的 close-to-close spread 口径上，尚未证明 next-bar / friction realism 下的独立 queue-facing edge，因此本轮 fresh intake 收口为 `background / P0`。
