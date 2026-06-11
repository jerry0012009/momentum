# 2026-04-03 08:18 UTC — funding-stability E24 × profit-lock fresh intake first verdict

## 执行动作
- 目标：`research/quant_digests/2026-04-03_0320_fundingstable-spotbasis-profitlock-alpha.md`
- 槽位：Fresh intake
- 动作：判断这条 `funding-stability E24 score × profit-lock exit` 是否足够独立于既有 funding/basis carry 家族，值得进入 `keep_P1 / P2`，还是应直接回到 `background/P0`

## 本轮结论
`funding-stability E24 × profit-lock` 不构成新的独立 raw alpha 主语，fresh intake first verdict = `background/P0`。

## 为什么这轮直接回 P0
1. **alpha 主语仍是老 carry，不是新家族。**
   这份 digest 自己已经把 base alpha 说死为 `same-underlier spot long / perp short` 的 `funding/basis carry`；`E24 net` 本质是把未来 24h carry 扣掉 fee、basis/liquidity/instability penalty 后再做排序，不是在创造不同于既有 carry 的收益来源。
2. **新增主要是 ranking / risk / exit 工程，而不是可单独 desk 化的新边。**
   `score_strict = e24_net_pct * confidence * capacity`、`profit-lock`、`drawdown/basis/stale guards` 都是很像 production 的治理层，能改善“怎么拿 carry”，但没有把对象从旧的 funding/basis carry 母线上分叉成新的 raw alpha 主语。
3. **和现有素材池重复度已经过高。**
   当前库里已经有至少三条更早、且主语同属 funding/basis carry 家族的 intake：
   - `2026-03-24_0806_single-venue-delta-neutral-funding-carry-fullstack.md`
   - `2026-04-01_1348_logbasis-pricevolume-funding-persistence-alpha.md`
   - `2026-04-02_2043_bestvenue-funding-zscore-hysteresis-carry.md`
   这条新 digest 的增量更像“单 venue carry 的 net-edge ranking + early profit capture 写法”，不足以再开一条新的 survivor/front-slot 叙事。
4. **它最值得复用的是组件，不是 front-slot 候选身份。**
   真正可迁移的东西是：
   - `future expected net edge = gross carry - fee - risk penalty`
   - `confidence × capacity` 排名
   - `profit already prepaid -> lock and exit`
   这些可作为 carry / pairs / relative-value 策略壳的组件库，但不意味着这条对象本身应继续占用前排 intake 资源。

## 对系统认知的更新
- 可以把 `E24 net` 与 `profit-lock` 记作 **旧 carry 家族的工程增强组件**。
- 不能把它记成一条独立于既有 `funding / basis / carry` 家族的新 raw alpha 主语。
- 因此前排不分配 rank，不进入 survivor，也不升 P2。

## 对应 runtime 写回
- `Fresh intake slot`: 更新为该对象，latest result 写成 `background/P0`
- `Background pool`: latest parked 更新为该对象
- `cycle_plan` 第 2 小点：`done`

## 结果句（用于 state）
`funding-stability E24 score × profit-lock exit` 不是新的独立 raw alpha 主语，而是既有 `funding / basis carry` 家族的 net-edge ranking 与退出治理增强，因此 fresh intake first verdict = `background/P0`。
