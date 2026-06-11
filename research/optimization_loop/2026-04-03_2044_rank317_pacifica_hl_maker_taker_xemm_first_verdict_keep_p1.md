# Rank 317 — Pacifica × Hyperliquid maker-taker XEMM first verdict: keep P1

- Time: 2026-04-03 20:44 UTC
- Target: `research/quant_digests/2026-04-03_1845_pacifica-hl-maker-taker-xemm-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1` → 分配正式 `Rank 317`，转入 `Surviving candidate slot`

## 为什么不是直接 P2
这条线的优点已经够清楚：
1. base alpha 主语明确，不是方向预测，而是 `Pacifica maker quote edge -> Hyperliquid taker hedge` 的跨 venue 微观流动性不对称；
2. repo 已把 entry / cancel / hedge / cost 写到规则级，公开 source 足够支撑最小复现；
3. public-data 路径清楚，至少能立刻做 `BTC/ETH/SOL` 的 top-of-book edge occupancy 与 spell-duration 验证。

但当前还不诚实支持直接升 `P2`，因为决定这条线是否可 paper 化的核心 blocker 不是“有没有公式”，而是：
1. Pacifica maker fill probability 是否足以把理论 edge 变成真实 edge；
2. fill → Hyperliquid hedge 这段 latency / slippage 是否会系统性吃掉 repo 里预留的 `15bps` 目标余量；
3. queue position、partial fill、refresh/cancel race 这些 maker honesty 问题，在公开数据最保守近似下是否仍留下可存活 pocket。

## 本轮改变了什么系统认知
`Pacifica maker × Hyperliquid taker XEMM` 已经通过 fresh intake 第一关：它不是“纯做市工程叙事”，而是一条值得继续做一次最小 honesty follow-up 的独立 maker-taker relative-value raw alpha；但在 fill / hedge realism 没被最保守代理检验前，还不诚实直接升 `P2`。

## 唯一 survivor follow-up 应测什么
下一步只做一次便宜且 decisive 的检查：
- 在统一 `BTC/ETH/SOL` shell 下，用 Pacifica 与 Hyperliquid 公共 top-of-book / trade 数据，先做 `1m/3m` 级最小 maker honesty probe；
- 核心只回答三件事：`edge > 10/15bps` 的占比、持续时间、以及加入最保守 fill proxy + hedge slippage stress 后是否还剩净 pocket；
- 若净 pocket 仍可复现，则可 `promote_P2`；若 edge 主要停留在理论 top-of-book、被 fill/hedge realism 吃光，则直接收口 `background/P0`。
