# Rank 285 — 24h losers-vs-winners XS reversal × dispersion / turnover：first verdict = keep_P1

- 时间：2026-04-01 23:53 UTC
- 对象：`24h losers-vs-winners XS reversal × dispersion / turnover 约束`
- 来源：`research/quant_digests/2026-04-01_2322_24h-xs-reversal-dispersion-turnover-shell.md`
- 本轮角色：bot3 当前唯一 pending 小点执行

## 本轮结论

这条 fresh intake 已经形成**可独立审计的 cross-sectional mean-reversion raw alpha skeleton**，因此本轮正式记为 `Rank 285` 并首判 `keep_P1`。

支撑它进入前排、但还不够直升 `P2` 的判断很明确：

1. alpha 本体是清楚的：`long recent 24h losers / short recent 24h winners`，赚的是横截面短期 overshoot 后的回归；
2. digest 已把最小策略壳写完整：universe、ranking、持有窗、rebalance cadence、cost ladder、turnover/dispersion/liquidity veto 与 perp transfer path 都已经明确；
3. repo 的关键信号不是“20d 动量失效”，而是 **1d reversal 在 2025-2026 OOS 里 gross alpha 很强，但原始 daily spot implementation shell 被 turnover/cost 打死**；
4. 因此它值得保留的不是现成可 live 策略，而是“24h XS reversal + 更低换手执行壳”的可迁移 raw alpha family。

但这轮不能诚实地直接升到 `P2`，原因同样具体：

1. 当前硬证据仍来自 `25` 个 liquid crypto 的 **日频 Binance spot OOS repo**，不是已经在 top-liquid perp / short-cycle desk 口径下完成 clean-room 复现的 after-cost 结果；
2. digest 虽给出了 `4h rebalance / 1h + trade buffer / dispersion gate / execution shell attribution` 的明确迁移方案，但这些仍是待测实验，不是已验证 admission evidence；
3. repo 自带结果反而强调：gross Sharpe 很高并不等于可交易，`138.83%` 的 daily turnover 与约 `101%` 的 annual cost drag 说明原始壳子完全不够诚实；
4. 目前还没有回答最关键的 desk 问题：**把 universe 收窄到 top-liquid perps、把换手压到 realistic 壳子后，after-cost pocket 是否仍真实存在**。

所以更准确的口径是：

> `Rank 285` 值得保留的，不是 repo headline，而是“24h 横截面 reversal 可能是真 raw alpha，但只有在更低 turnover、更高流动性、带 dispersion/liquidity 约束的 execution shell 里才值得继续审”的这条骨架；在 top-liquid perp clean-room after-cost 迁移前，它应停在 `keep_P1`，不该跳升 `P2`。

## 为什么不是 P0

因为它已经具备可迁移的最小策略定义：

- universe：有（top-liquid perps 缩版候选清楚）；
- ranking/signal：有（最近 `24h` 横截面收益排名）；
- entry/exit/holding：有（`4h` / `1h` 两套最小节奏）；
- risk/cost realism：有（liquidity veto、turnover veto、dispersion gate、maker/mixed/taker 三档成本）；
- transfer path：有（从 daily repo 明确迁移到 short-cycle perp desk 的步骤）。

这已经超过“只有论文叙事或 repo headline”的程度，足够保留为前排 survivor。

## 为什么不是 P2

因为 admission 还缺最关键的一层现实检验：

- top 8~12 liquid perps 下，`24h` XS reversal 在 `4h rebalance` 后是否仍保留可观 gross edge；
- 加入 realistic maker/mixed/taker friction ladder 后，净 pocket 是否转正；
- trade buffer 是否能把 turnover 从 repo 的不可交易区间压回可交易区间；
- dispersion gate 对 reversal 是真正生存条件，还是只是 momentum 失败的伴随现象。

这些问题没回答前，把它升到 `P2` 会把“值得继续做一次便宜诚实 follow-up”误写成“已经接近 paper-worthy”。

## 对 runtime 的实际影响

- 新分配正式 `Rank`：`285`
- 当前 fresh intake 首判：`keep_P1`
- survivor 槽应切换为 `Rank 285`
- 唯一 follow-up 应直接检查：在 top-liquid perp universe 上，用 `24h` 排名 + `4h rebalance` / `1h buffer` 的低换手壳子后，这条 reversal 是否还能留下 after-cost pocket。
