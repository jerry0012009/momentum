# Rank 311 — stablecoin cross-venue cycle mispricing × inventory-funded execution 首判 `keep_P1`

- 时间：2026-04-03 14:01 UTC
- 对象：`research/quant_digests/2026-04-03_1313_stablecoin-crossvenue-cycle-alpha.md`
- 本轮动作：fresh intake first verdict
- 结论：`stablecoin cross-venue cycle mispricing × inventory-funded execution` 具备独立 raw alpha 主语，不只是图搜索/路由器包装；因此给予正式 `Rank 311`，首判为 `keep_P1`，进入 `Surviving candidate slot` 做唯一一次最小 decisive follow-up。

## 为什么这次不是直接打回背景
1. **alpha 主语是可独立 desk 化的净后错价闭环**
   - 核心交易对象不是“搜索算法更快”，而是同组稳定币在多 venue、多报价边之间出现的短周期净错价环。
   - 图搜索只是求解器；即便后续把 `A* / H4` 换成更简单的 greedy / constrained router，待验证的 alpha 仍然成立：是否存在能覆盖 fee、slippage、inventory penalty 的可成交 cycle pocket。

2. **执行壳已经足够完整，不是概念拼装**
   - digest 已给出最小可复现骨架：`(venue, coin)` 节点、top-of-book + fee 边、inventory-funded 跨所库存边、`net_return_bps` 触发门槛、venue/stablecoin concentration cap、rebalance penalty。
   - 这已经超出“课程作业里找路径”的程度，具备 entry/exit/cost/risk 的最小 desk 语义。

3. **与既有 pairs / funding / basis 家族有可检验区分**
   - 它不依赖统计回归残差、资金费率期限结构或单所 basis，而是依赖多 venue 稳定币报价边之间的瞬时相对价值闭环。
   - 因此更像独立的 `stablecoin relative-value / cycle arb` 分支，可以单列进入素材前排。

## 为什么这次还不直接升 P2
1. 当前强证据主要来自课程项目 repo + 报告，不是已经做过统一口径的公开复现。
2. 目前最关键、也最可能改变层级的剩余 blocker 只有一个：**inventory-funded 版本在更真实的 depth haircut / rebalance penalty 下，是否仍保留足够稳定的 post-cost positive cycle pocket**。
3. 这正好适合 survivor 预算内的一次最小 follow-up；若 follow-up 不能证明这点，就应诚实回到背景，而不是空转成开放式研究。

## survivor follow-up 应聚焦什么
唯一值得做的后续不是继续解释图搜索，而是收口到：
- 用统一 venue set 和稳定币集合，确认 `inventory-funded net bps` 相对 `full-transfer net bps` 的保留程度；
- 检查 pocket 是否在 `1m~5m` 粒度下仍有足够频次/容量，不会被 depth haircut 一下吃光；
- 若这一步通过，再考虑是否足以进 `P2`。

## 本轮写回 runtime 的变化
- 分配新正式编号：`Rank 311`
- fresh intake first verdict：`keep_P1`
- `Surviving candidate slot` 切换为 `Rank 311`
- follow-up budget：`1`

## 一句话结果
`Rank 311` 不是“图搜索包装过的旧套利描述”，而是一条可独立 desk 化的 `stablecoin cross-venue cycle mispricing × inventory-funded execution` raw alpha；但在升 `P2` 前，还需要用唯一一次 survivor follow-up 验证它在更真实库存/深度摩擦下是否仍有稳定净后 pocket。
