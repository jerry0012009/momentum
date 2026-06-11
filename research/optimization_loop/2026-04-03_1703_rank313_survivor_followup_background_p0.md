# Rank 313 — survivor follow-up — background/P0

- 时间：2026-04-03 17:03 UTC
- 对象：`Rank 313 / liquid-major distance-to-high cross-sectional continuation`
- 执行动作：survivor 唯一一次 follow-up
- 结论：`background/P0`

## 这轮实际执行了什么
按 `cycle_plan` 要求，先检查项目内是否已经存在能回答 survivor 决策的 **clean first replication** 证据：统一 `liquid majors 5m/15m`、统一 `4/6/8bps` 成本口径、以及 `hmom / distance-to-high` 对 `ret_n` baseline 的直接对照。

本轮检索到的与该对象直接相关的仓库材料只有：

1. 原始 digest：`research/quant_digests/2026-04-03_1510_liquid-highmomentum-rolling-high-crosssectional-alpha.md`
2. first verdict 日志：`research/optimization_loop/2026-04-03_1624_rank313_liquid_highmomentum_first_verdict_keep_p1.md`
3. 站点发布页：`reports/site/reading/quant_digests/2026-04-03_1510_liquid-highmomentum-rolling-high-crosssectional-alpha.html`

未发现任何已经落库的：
- `liquid-major` desk 口径回测 artifact
- `hmom vs ret_n` 直接对照 summary
- `top liquidity / middle / tail` split 结果页或结果表
- 统一 `4/6/8bps` 成本敏感性输出

## 为什么这一步不能升 P2
`Rank 313` 的论文主语本身仍然成立：它不是 generic XS momentum/reversal 的换皮，而是明确提出 **large/liquid bucket 中测 distance-to-high continuation，尾部混入可能翻成 reversal**。

但 survivor 这一轮要回答的是更严格的问题：

> 在当前项目自己的 desk 口径里，是否已经有 clean first replication 证明 `hmom` 净后优于 `ret_n` baseline，且优势不是单一标的 / 单一方向 / 单一时间窗偶然支撑？

当前答案是否定的。原因不是“结果做坏了”，而是 **项目内目前根本还没有这一步 replication artifact**。在当前 policy 下，survivor 只有这唯一一次 follow-up 预算；如果这一步没有产出会改变层级的项目内证据，就不能继续把对象留在前排占用 survivor 槽位。

因此，这轮最诚实的收口不是 `promote_P2`，而是：

- 保留论文层面的系统认知：`liquidity split` 与 `distance-to-high` 值得记在素材池里；
- 但在 runtime 上把 `Rank 313` 从 survivor 前排移出，记入 `background/P0`；
- 未来若有人明确要求 reopen，再作为新的前排对象重新进入。

## Runtime 写回
- `Surviving candidate slot`：清空，不再保留 `Rank 313`
- `Background pool.latest_parked`：写入 `Rank 313` survivor follow-up 收口到 `background/P0`
- `cycle_plan[1]`：写成 `done`

## 一句话结果
`Rank 313` 的论文主语是成立的，但当前项目内没有统一 `liquid-major 5m/15m + 4/6/8bps` 的 clean replication artifact 来证明它在 desk 口径下足以升 `P2`；在 survivor 唯一 follow-up 用完后，本轮应诚实收口为 `background/P0`，而不是继续挂在前排。