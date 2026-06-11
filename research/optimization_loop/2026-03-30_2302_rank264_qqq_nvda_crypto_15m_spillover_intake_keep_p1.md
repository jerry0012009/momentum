# Rank 264 / QQQ-NVDA lead-lag × crypto 15m spillover — fresh intake keep_P1

- Time: 2026-03-30 23:02 UTC
- Target: `QQQ / NVDA lead-lag × crypto 15m spillover`
- Source digest: `research/quant_digests/2026-03-30_2204_qqq-nvda-crypto-15m-leadlag-alpha.md`
- Runtime action: `fresh intake first verdict`
- Assigned Rank: `264`

## What was executed

按当前 `cycle_plan`，本轮只执行这一个 pending 小点：把 `QQQ / NVDA 5m shock -> BTC/ETH/DOGE future 15m move` 作为新的 fresh intake 做 first verdict，不重排其余小点。

## Read-through

这条线的主语是明确的：

- external leader: `QQQ`, `NVDA`
- target: `BTC / ETH`（`DOGE` 只是 beta 扩展样本）
- clock: `U.S. cash session`
- signal: `leader 5m tail shock`
- execution skeleton: `next bar entry -> fixed 15m hold / veto`

它不是泛 risk-on/risk-off 叙事，也不是普通相关性观察。原 digest 已把 base alpha 压缩成可执行骨架：**先看美股 tech leader 的短窗冲击，再交易 crypto 在后续 15m 的 follow-through。**

## First-verdict judgment

本轮 first verdict 结论是：

> `QQQ / NVDA lead-lag × crypto 15m spillover` 足以构成一条独立的 cross-market raw alpha skeleton，因此正式纳入前排并分配 `Rank 264`；但当前最像真钱 pocket 的只有 `QQQ downside 5m shock -> ETH/BTC future 15m follow-down`，证据仍主要来自最近 60 天公开 `5m` transfer check 与粗略 taker 成本包络，尚未完成对 perp 口径、confirmation/veto 规则与 execution realism 的 admission，所以本轮只给 `keep_P1`，不直接升 `P2`。

## Why not P0

不该直接打回 background，原因有三条：

1. **alpha 主语清楚**：不是解释型论文，而是 `leader shock -> follower delayed move` 的明确信号框架；
2. **执行骨架已存在**：`5m trigger -> next bar entry -> 15m hold` 已足以构成最小策略；
3. **本地最小 transfer check 有具体 pocket**：尤其是 `QQQ downside -> ETH/BTC short` 显示出不对称 follow-down，而不是完全空的相关性故事。

## Why not P2 yet

还不能直接升 `P2`，因为目前关键 admission 问题还没被回答：

1. **perp / live-feasible 口径未核实**：当前 digest 主要用了 Yahoo + Binance `5m` 数据的最小快检，离真正 desk 执行口径还差一步；
2. **成本后净边未被诚实锁死**：虽然文中提到粗略 taker round-trip 包络，但还没把 perp spread / fee / shock 后追单滑点明确扣净；
3. **规则仍偏 prototype**：`QQQ-only`、`NVDA-only`、`QQQ&NVDA confirm`、`crypto local veto` 哪组是真正决定性 blocker，目前未收口；
4. **当前 pocket 明显不对称**：更像 `QQQ downside follow-down` 的单侧口袋，不适合直接包装成对称 long-short 成品。

## Runtime result sentence

`Rank 264：fresh intake 首判完成；QQQ/NVDA 5m 冲击驱动 ETH/BTC 未来 15m spillover 已构成独立 cross-market raw alpha skeleton，但当前真钱感主要集中在 QQQ downside -> ETH/BTC follow-down，admission 仍缺 perp 成本后净边与确认/否决规则，因此本轮记为 keep_P1。`
