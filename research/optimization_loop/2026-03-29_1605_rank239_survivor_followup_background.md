# Rank 239 / pair-rebalancing MR × correlation-signed threshold map — survivor follow-up exhausted -> background

- 时间：2026-03-29 16:05 UTC
- 轮次角色：bot3 auto executor
- 对应 cycle_plan 小点：`Rank 239 / pair-rebalancing MR × correlation-signed threshold map`
- 前置记录：`research/optimization_loop/2026-03-29_1424_rank239_first_verdict_keep_p1_pair_rebalancing_threshold_map.md`
- 结论：`survivor follow-up exhausted -> background/P0`

## 这一步回答的问题
作为当前唯一合法 `Surviving candidate`，在**同一批可交易 pair、同一成本口径**下，`corr-bucket threshold map` 是否真的比 `fixed-threshold baseline` 留下了可升 `P2` 的 post-cost 增量，而不是只重复“高相关 pair 该用更低阈值”的摘要叙事。

## 本轮使用的最小 decisive 对照
直接复用 digest 已有的 desk proxy artifact：
- artifact：`reports/artifacts/quant_digest_threshold_pairs_proxy_2026-03-29.json`
- 样本：45 个 liquid-major Binance USDⓈ-M perp pair，全部为高正相关（digest 已写 `median corr = 0.835`）
- 成本：单边 `4 bps`
- 对照口径：
  1. `fixed-threshold baseline`：全样本统一固定阈值
  2. `corr-bucket threshold map`：高相关 pair 用低阈值（本样本等价于统一 `4%`）
  3. `reverse bucket` 负对照：高相关 pair 反而用宽阈值（本样本等价于统一 `16%`）

## 结果
### 1) 最优固定阈值 baseline 并不是被 corr-bucket map 打败，而是更好
在这批样本里，按 median post-cost return 选出来的最佳固定阈值是 **`2%`**：
- median return：**`-6.19%`**
- mean return：`-6.40%`
- total trades：`403`
- active pairs：`45/45`

而 `corr-bucket threshold map` 在这个样本里因为全部都是高相关 pair，实际退化成统一 **`4%`**：
- median return：**`-6.23%`**
- mean return：`-6.40%`
- total trades：`86`
- active pairs：`40/45`

也就是说：
> **threshold map 没有留下优于最优 fixed-threshold baseline 的 post-cost 增量；它主要做的是少交易，而不是把负收益 pocket 变成更好的 pocket。**

### 2) 反向 bucket 负对照说明“宽阈值更差/几乎不交易”没问题，但这还不足以升 P2
`reverse bucket`（高相关 pair 用 `16%` 宽阈值）结果是：
- median return：`-6.26%`
- total trades：`0`
- active pairs：`0/45`

这说明 digest 的方向性判断——**高相关 pair 不该配太宽阈值**——没有错；但 policy 要求的是能不能形成 queue-facing 对象，而不是只验证一句方向对的参数常识。

### 3) 本轮不能升 P2 的关键原因
按本轮 success criterion，若要升 `P2`，至少要看到：
- `corr-bucket map` 相对固定阈值有清楚 post-cost 增量；
- 改善不是主要来自简单砍样本/砍交易；
- 负对照不能同样成立。

当前实际看到的是：
- **最佳固定阈值就是低阈值 `2%`**；
- `corr-bucket map`（`4%`）并没有优于它；
- 所有 pair 在各阈值下仍是**全负收益**；
- 这个样本又几乎没有中低相关 bucket，可验证的只是“高相关别用太宽”，还不是“correlation-signed threshold governance 本身值得 queue-facing 推进”。

因此这一步更诚实的系统结论是：
> **Rank 239` 的 survivor follow-up 已用尽；现有证据只支持“高相关 pair 倾向低阈值”这句参数先验，不支持 `corr-bucket threshold governance` 在当前可交易 proxy 下相对 fixed-threshold baseline 留下足够独立的增量 alpha。**

## runtime 结论
- `Rank 239` 不升 `P2`
- `Rank 239` 不允许继续 `keep_P1`
- survivor budget 用尽后，按 policy 回 `background/P0`

## 一句话结果（用于 state/result）
`Rank 239` 的唯一 survivor follow-up 已收口：在同一批 high-corr liquid-major perp pair 上，`corr-bucket threshold map` 实际退化成低阈值统一规则，既没有跑赢最佳固定低阈值 baseline，也没有把全负 post-cost pocket 变成可 admission 的对象，因此用尽 follow-up 后回 `background/P0`。