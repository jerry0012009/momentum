# Rank 307 first verdict — Kalshi strike-gap / neighboring-contract binary mispricing

- Time: 2026-04-03 10:09 UTC
- Target: `research/quant_digests/2026-04-03_0908_kalshi-strikegap-binary-mispricing-alpha.md`
- Decision: `keep_P1`
- Assigned rank: `Rank 307`
- Slot impact: fresh intake 完成；进入 `Surviving candidate slot`

## Why this changes system belief
`Kalshi strike-gap / neighboring-contract binary mispricing` 不是旧的 fee shell 或单纯 prediction-market infra 包装；公开 repo + sample features 已经给出清楚的 tradable 主语：`spot trend + price_vs_strike_pct + time_to_expiry + orderbook state -> fair YES probability`，然后交易 `fair probability - market mid` 的 15m fixed-expiry binary mispricing。它具备公开数据复现路径、最小 entry/exit/cost/risk 壳，也明显区别于更偏宏观 gate 的 `Rank 306`。

## Why not P2 yet
本轮仍停在 `P1`，因为当前证据主要来自小样本 repo starter kit（约 2470 行 sample features + 短代码骨架），还不足以直接回答：
1. 成本后 edge decile 是否在更长样本上仍单调；
2. alpha 主体到底来自 `price_vs_strike_pct`、spot trend，还是两者交互；
3. 该错价是否只集中在特定 `time_to_expiry` bucket；
4. maker-ish / taker-ish 下是否都还能存活。

## Honest first verdict
这条线已经足够作为正式前排候选保留：
- 有独立交易载体：Kalshi 15m crypto binary contract；
- 有清楚 raw alpha 主语：fair probability vs quoted mid 的回补；
- 有可公开复现实验壳：Kalshi 行情 + Coinbase 现货 + repo sample features；
- 有最小执行/风控口径：mid-range probability window、time-to-expiry window、spread veto、fee model、Kelly/position caps。

但要升 `P2`，还需要一次 survivor-only follow-up，把 `1m/3m/5m/15m` desk 版特征、`time_to_expiry` bucket、以及 maker/taker 成本梯度拆开，确认这不是只在 demo sample 上成立的薄容量错价壳。

## Result sentence for runtime
`Rank 307` 已正式分配给 `Kalshi strike-gap / neighboring-contract binary mispricing`；它具备清楚的 `fair probability - market mid` 误价主语、公开 Kalshi/Coinbase 复现路径与最小成本/风控壳，因此 fresh intake first verdict = `keep_P1`，进入 `Surviving candidate slot`。
