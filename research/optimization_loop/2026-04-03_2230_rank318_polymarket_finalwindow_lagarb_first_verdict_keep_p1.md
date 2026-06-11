# Rank 318 — Polymarket final-window lag arb first verdict: keep_P1

- Time: 2026-04-03 22:30 UTC
- Target: `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1` → promote into `Surviving candidate slot`
- Assigned Rank: `318`

## Why this changes system belief
`Binance 领涨/领跌 → Polymarket final-window binary odds lag repair` 这条主语已经足够独立清楚：base alpha 不是 AI filter，而是 hard-expiry binary market 在最后 120s→3s 窗口对 leader venue 秒级价格发现的滞后修复；公开可复现的数据路径（Binance websocket / Polymarket Gamma+CLOB / Chainlink optional confirm）、最小 `5m/15m` paper shell、maker-first 成本边界、entry/exit/sizing/risk 框架都已明确，因此本轮可诚实首判 `keep_P1`，不应直接丢回 background。

## Decision details
1. **独立 raw alpha 成立**
   - 不是“AI 帮你下注”。
   - 真正可交易的对象是：leader venue 先动、临近到期的 binary odds 后动。
   - 这是可单独验证的 cross-market / hard-expiry lag-repair，而不是 overlay 叙事。

2. **最小实验壳已足够完整**
   - Venue/data: Binance websocket；Polymarket Gamma + CLOB；Chainlink 可选二次确认。
   - Clock: 原生就是 `5m/15m` recurring markets，时间尺度与 desk 当前短周期框架兼容。
   - Entry: fair value vs YES/NO 当前价格，结合 `min_edge_pct / lag_threshold / confidence / momentum / consecutive ticks`。
   - Exit/risk: 到期前平仓、maker-first、极端 edge 才 taker fallback、Kelly × cap、DD kill switch。

3. **诚实保留的关键风险**
   - maker fill risk 与 final-window 深度可能把薄 edge 吃掉；
   - late-window 竞争强，paper/live gap 可能很大；
   - AI filter 当前更像 overlay，且实现顺序可疑，所以首轮不应把 AI 当主研究对象。

## What survivor follow-up should answer
唯一值得花的 survivor one-shot follow-up，不是再重讲 repo，而是直接回答：
- 在不启用 AI 的前提下，`5m/15m` final-window lag arb 的 **maker-first honesty** 是否仍留下可穿成本与成交约束的最小正 edge；
- 优先看 `maker fill / depth / edge decay / 5m vs 15m`，避免把 overlay 包装成主因。

## Runtime impact
- New formal identity assigned: `Rank 318`
- Level change: fresh intake → `P1 / Surviving candidate slot`
- Fresh intake head should advance to next concrete intake item after this rank assignment.
