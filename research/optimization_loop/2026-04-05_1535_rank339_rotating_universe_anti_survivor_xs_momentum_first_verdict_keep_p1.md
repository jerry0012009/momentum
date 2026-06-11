# Rank 339 / rotating universe anti-survivor XS momentum — fresh intake first verdict = keep_P1

- 时间：2026-04-05 15:35 UTC
- 对象：`research/quant_digests/2026-04-05_0015_rotating-universe-anti-survivor-xs-momentum-alpha.md`
- 执行动作：fresh intake first verdict
- 结论：`keep_P1`
- 分配 Rank：`339`

## 为什么这次不是 background/P0
这条线不是把已有 XS momentum 换个名字，而是把 **universe construction** 直接抬成 raw alpha 本体的一部分：

1. **distinct hypothesis 清楚**
   - 论文不是在说“crypto momentum 没有了”；
   - 它给出的更值钱命题是：**如果 universe 被长期幸存 core 币锁死，XS momentum 可能会被洗掉；真正该先测的是 rotating tradable sleeve。**

2. **tradable universe rule 已经写到可执行层**
   - digest 已给出 desk 可落地替代：
   - 用 `过去 180 天中进入 top-30/top-40 ADV 或 OI bucket 的频率 >= 80%` 定义 survivor；
   - 其余近期仍位于 top bucket、但不满足长期稳定留存的对象归 rotating sleeve。
   - 这不是抽象论文叙事，而是可以直接写进回测的 universe split。

3. **ranking shell / cadence / transfer path 足够具体**
   - `15m` bar；
   - `8h + 24h` blended cross-sectional momentum score；
   - `1h` rebalance；
   - long top quantile / short bottom quantile；
   - survivor / rotating / combined 三个 sleeve 分开看。
   - 已形成最小的 Binance perp 验证壳，不只是“以后再想怎么交易”。

4. **cost realism 不是缺席状态**
   - digest 明确写了 taker / maker 成本、warm-up、单币权重上限、funding/spread veto；
   - 虽然还没做实证 first test，但已经满足 fresh intake 阶段对 `execution shell + liquidity realism + post-cost transfer` 的最低要求。

## 为什么现在还不直接升 P2
当前材料仍主要是“论文 + 交易壳改写”，还缺最关键的一步便宜诚实检查：

- alpha 是否真的主要活在 `rotating sleeve`，而不是 survivor / combined 都只是噪声；
- rotating sleeve 的 turnover / cost / slippage 是否会把表面 long-short spread 吃光；
- `8h/24h × 1h hold` 是否只是周频论文叙事向短周期的过度投射。

所以最诚实的位置是：
- **保留为 `P1 / surviving candidate`**，
- 下一次只给它 **1 次**最小 decisive follow-up，专门回答“rotating sleeve 是否在 after-cost 口径下留下独立于 survivor sleeve 的净收益壳”。

## runtime-impact
- 新 fresh intake 获得正式身份：`Rank 339`
- verdict：`keep_P1`
- 层级迁移：`Fresh intake -> Surviving candidate`
- 下一前位 fresh intake 顺延到：`research/quant_digests/2026-04-05_0059_top20-depth-imbalance-tightspread-continuation-alpha.md`

## 一句话结果
`Rank 339 / rotating-universe anti-survivor XS momentum` 不是已有 cross-sectional momentum 的样本口径重命名，而是把 `rotating tradable sleeve vs survivor sleeve` 明确提升为 alpha 本体的 universe-engineering 命题；其 universe split、ranking shell、execution cadence 与 cost framing 已足够形成最小 Binance perp 验证路径，因此 fresh intake first verdict 写成 `keep_P1`，进入 survivor 槽位等待唯一一次 follow-up。
