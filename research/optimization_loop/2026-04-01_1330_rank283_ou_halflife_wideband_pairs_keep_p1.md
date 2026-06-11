# Rank 283 — OU half-life wideband pairs：first verdict = keep_P1

- 时间：2026-04-01 13:30 UTC
- 对象：`OU half-life wideband pairs / beta-hedged cointegration spread mean reversion`
- 来源：`research/quant_digests/2026-04-01_0428_ou-halflife-wideband-pairs-alpha.md`
- 本轮角色：bot3 当前唯一 pending 小点执行

## 本轮结论

`OU half-life gate × wide-band spread mean reversion` 已形成**可审计的 pairs raw alpha skeleton**，因此本轮正式记为 `Rank 283` 并首判 `keep_P1`。

但当前证据还不够诚实地直升 `P2`：

1. 现有本地 transfer check 只覆盖约 `1500` 根 `5m` bar（约 `5.2` 天），时间稳定性明显不够；
2. 当前最强证据是“`2.0σ~3.0σ` 宽 band + half-life gate 比 `1σ` 窄 band 更可交易”，这说明 admission logic 有价值，但还不是足够厚的 after-cost desk admission；
3. 这轮 quick check 仍是简化 beta-neutral package proxy，未把 maker/taker 分层、滑点、结构断裂 kill-switch、pair availability churn 这些现实执行约束补齐；
4. digest 自己也明确把下一步指向更长样本与更诚实对照：固定阈值 sweep vs repo `band_calc.py` free-boundary OU optimal band、`90d~365d`、major-only vs broader liquid universe、以及 pair availability 时间序列供给检验。

所以更准确的口径不是“这条线已能进 paper”，而是：

> `Rank 283` 已经把 pairs 线里最关键、且最容易被自欺的 admission discipline 讲清楚——`half-life gate`、`wide-band entry`、`band must widen with cost`；因此值得保留在前排做唯一一次 survivor follow-up，但当前还不能跳过更长样本与更诚实执行口径，直接升 `P2`。

## 为什么不是 P0

因为这条线不是空泛 textbook 叙事：

- base alpha 清楚：`beta-hedged cointegration spread mean reversion`；
- entry / exit / sizing / risk / cost 骨架完整；
- 本地最小 transfer check 至少证明了一个会改变系统认知的点：
  - `1σ` 窄 band 在 one-way `6bps` proxy 下平均已转负；
  - `2.5σ` 左右宽 band 平均结果更好；
  - `3.0σ` 虽略慢，但正收益 pair 数更多；
  - 领先 pair 会随 band 改变，不是“找到一对神 pair 就完事”；
  - 领先 pair 的 median half-life 大致在 `60~90 分钟`，说明 half-life 不是报表装饰，而是应进 gate 的 admission 组件。

这足以支持：对象不是“只有术语、没有迁移路径”的 P0。

## 为什么不是 P2

因为 P2 admission 至少要能更诚实回答以下问题，而当前 digest 还没补够：

- after-cost edge 是否跨更长时间窗仍存在；
- 正 alpha 是集中在个别短时 pocket，还是 pair supply 能稳定轮换；
- repo 的 OU optimal band 数值实现，是否真的优于固定阈值 sweep；
- 加入更现实 friction / churn / structure-break kill-switch 后，是否仍保留足够厚的 edge。

在这些问题没回答前，直升 `P2` 会把“admission discipline 有价值”误写成“策略已接近 paper-worthy”，这不诚实。

## 对 runtime 的实际影响

- 新分配正式 `Rank`：`283`
- fresh intake 当前结论：`keep_P1`
- survivor 槽应切换到 `Rank 283`
- 上一条 survivor `Rank 282` 自动退回 background / wait-for-reopen（除非未来人工明确 reopen）

## 建议给唯一一次 survivor follow-up 的精确问题

下一次且仅一次 follow-up 应直接回答：

> 在 `90d~365d` 的 Binance/Bybit intraday 样本、major-only 与 broader liquid universe 分开口径下，`Rank 283` 的 `OU optimal band / 2.0σ / 2.5σ / 3.0σ` 对照里，是否仍能看到一个 after-cost、pair-supply 不过度塌缩、且不依赖单一短 pocket 的诚实 survivor；还是说这条线真正存活的只是一条“band governance insight”，不足以保留前排。

若该 follow-up 不能给出更强生存证据，则默认应收口回 background，而不是继续拖长。
