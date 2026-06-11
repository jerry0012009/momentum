# Rank none / partial-moment downside TSMOM fresh intake -> background/P0

- Time: 2026-04-25 15:19 UTC
- Target: `research/quant_digests/2026-04-25_1315_partialmoment-downside-tsmom-alpha.md`
- Slot: `Fresh intake slot`
- Action type: `fresh intake first verdict`
- Verdict: `background/P0`

## Why this step was the current legal action
`BOT2_BOT3_STATE.md` 当前 `cycle_plan` 的第一个 `status = pending` 小点就是这条 fresh intake，因此本轮只执行它，不重排、不扩展成其他 pending 项。

## Minimal decisive blocker checked
按 state 里的成功标准，这一步只需要回答：

> `downside-tail-dominant continuation` 在统一成本口径下，是否已经留下至少一个**不是高 beta 小样本偶然**的明确 after-cost pocket，可以支持 `keep_P1`？

我复核了本轮已经落地的公开 probe 汇总：
`reports/artifacts/quant_digests/2026-04-25_partial_moment_tsmom_probe_summary.csv`

## What the probe actually says
### 1) liquid majors 没有留下可保留的 after-cost pocket
`BTC / ETH / SOL` 在 downside bucket 下，无论 `dn_pm` 还是 `dn_base`，`hold 1/3/6` 全部仍为负：

- `BTCUSDT dn_pm hold6 = -10.63 bps`
- `ETHUSDT dn_pm hold6 = -2.15 bps`
- `SOLUSDT dn_pm hold6 = -2.20 bps`
- 对应 `dn_base hold6` 也同样为负

这意味着最关键的 desk 问题已经有答案：**公开 liquid-major portability 没有证明 downside continuation 在统一成本后可留。**

### 2) 唯一为正的 pocket 只出现在 high-beta alts
汇总里只有两条正值：

- `DOGEUSDT dn_pm hold6 = +1.83 bps`（`dn_base hold6 = +1.53 bps`）
- `ADAUSDT dn_pm hold6 = +1.21 bps`（`dn_base hold6 = +1.17 bps`）

但这两条都属于 state 成功标准里明确不够的情况：
- 它们不在 liquid majors；
- 都是 high-beta alt；
- `dn_pm` 相比 `dn_base` 增益极小，说明**partial-moment gate 本身没有拿出会改变系统认知的新增 edge**，更像 alt downside continuation 本来就稍好，而不是这篇 paper 提供了一个足够硬的新 raw alpha。

### 3) pooled 结论仍然是“方向不对称值得记住”，不是“策略可保留”
该 digest 自己已经给出 pooled 快检：
- downside baseline `hold6 ≈ -2.75 bps`
- downside + PM gate `hold6 ≈ -2.93 bps`
- upside 更差，但并不会因此自动把 downside 升成 `P1`

所以这轮真正能改变系统认知的话不是“值得继续测”，而是：

> **目前公开证据只支持把它记成一个“downside continuation 通常没 upside 那么差”的研究提醒，不支持把 partial-moment downside TSMOM 保留成前排 raw alpha 候选。**

## Result sentence to write back into runtime
`partial-moment downside TSMOM` first verdict 已诚实收口 `background/P0`：公开 `15m` portability probe 在统一成本口径下未能给 `BTC/ETH/SOL` 留下任何成本后为正的 downside continuation，唯一正 pocket 只出现在 `DOGE/ADA` high-beta alt，且 partial-moment gate 对 baseline 几乎无增益，因此它目前更像 asymmetry/router 研究原料，而不是可保留的 raw alpha survivor。

## Runtime impact
- 无 `Rank` 分配：因为 verdict 不是 `keep_P1` / `promote_P2` / `promote_P3`
- 无层级升级
- 当前小点应标记为 `done`
- `Fresh intake slot` 的 `latest_result` / `latest_result_record` 更新为本结论
