# Rank 327 — Frost Asian-session MA deviation fade first verdict：keep_P1

- 时间：2026-04-04 10:30 UTC
- 对象：`research/quant_digests/2026-04-04_0905_frost-asian-ma-deviation-fade-alpha.md`
- 层级动作：`fresh intake -> keep_P1`，分配正式 `Rank 327`
- 结论一句话：这条 `Asian-session 20-bar MA deviation fade × ATR/trend veto × mean-target exit` 已经把 base alpha 与 `ATR / slope veto / mean-target exit` 的完整策略壳讲清，足以作为一条可迁移的 `15m` 单币 intraday mean-reversion 候选进入 `P1`，但当前 edge 仍明显偏薄且强依赖低成本，暂不升 `P2`。

## 为什么这轮给 keep_P1，而不是直接打回 background

这次 fresh intake 的关键不是“它最近能不能直接 production”，而是它有没有形成一条**独立、完整、可继续便宜验证**的 raw alpha 壳。

就这一点看，答案是有：

1. **base alpha 很清楚**：亚洲时段里，价格相对 `20 x 15m` 均线出现中等偏离，但又未进入明显 breakout / 趋势化环境时，反手做回均值；
2. **filter 与 alpha 本体能分账**：`ATR` 和 `10-bar slope veto` 都是在约束“别在太吵 / 太顺的行情里做反转”，不是把收益全伪装成 filter；
3. **exit 壳完整**：repo 已写清 `80%` mean-target、止损 buffer、`MIN_RR`、`MAX_CANDLES_HOLD=16`；
4. **时间框架可迁移**：虽然原生战场是 `15m`，但它至少留下了清楚的 desk shell，可继续做 `15m -> 5m` 的保时长迁移，而不是只剩论文式概念。

所以它不是一份只有 narrative 的 repo demo，也不只是某个现成策略的附属 filter；它确实构成了一条值得保留一次 follow-up 的单币 intraday mean-reversion raw alpha 候选。

## 为什么这轮也不能更乐观

同一份 digest 里已经把最主要的诚实约束写得很清楚：

- 代码阈值口径比注释意图明显更紧；
- 最近窗口里 `BTC` gross 虽正，但 `4bps` round-trip 后已翻负；
- `ETH` 也只是在极低成本下勉强保留 pocket，`8bps` 后就显著失活；
- 目前还没有足够严肃的 walk-forward / robustness 证据，不能直接上升为 admission-ready 对象。

换句话说，**它的价值在于“壳是完整的”，不是“边际已经厚到可以 admission”**。

## 本轮运行态影响

- 正式分配：`Rank 327`
- `Fresh intake slot`：完成，latest result 改写为 `Rank 327 first verdict = keep_P1`
- `Surviving candidate slot`：由空槽切换为 `Rank 327 / Frost Asian-session MA deviation fade`，保留唯一一次 follow-up 预算
- 不触发 `P2` / `P3` 迁移

## 给下一次 survivor follow-up 的唯一诚实问题

若后续要继续，只该回答一个高杠杆问题：

> 在修正“注释口径 vs 实际代码口径”之后，这条壳能否在 **不依赖过低成本** 的前提下，仍保留至少一块清楚可迁移的 `15m` 单币 mean-reversion pocket？

如果不能，就应诚实收口到 `background/P0`，不要把它拖成长尾均值回复 demo。
