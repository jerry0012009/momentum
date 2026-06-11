# Rank 224 / BTC reference + dual-spread copula conditional mispricing：survivor follow-up 收口为 keep_P1 后转 background

- 时间：2026-03-28 15:10 UTC
- 对象：`Rank 224 / BTC reference + dual-spread copula conditional mispricing`
- 轮次类型：bot3 auto optimization
- 结论：`keep_P1 后转 background`

## 这轮做了什么
按当前 `cycle_plan` 执行 Rank 224 那唯一一次 survivor follow-up，目标是回答：在同一 formation/trading split、同一 after-cost 口径下，`dual-spread copula conditional mispricing` 相对 `plain single-spread / dual-spread z-score baseline` 是否已经有足够明确的独立净增益，值得升级到 `P2`。

这轮优先复用了本地现成、与该主题直接相关的 artifact，而不是再开新一轮泛 pairs 扫描：
1. `reports/artifacts/quant_digests/copula_reference_pairs_20260323/summary.json`
2. `reports/artifacts/quant_digests/copula_pairs_threshold_probe_20260323/summary_by_interval_entry.csv`
3. `reports/artifacts/quant_digests/copula_pairs_threshold_probe_20260323/pair_results.csv`
4. Rank 224 intake / digest 本身

## 本轮得到的决定性证据
### 1) plain baseline 在本地 `15m` after-cost 口径下，并没有形成可直接晋级的通用 pocket
本地 `15m` plain threshold / z-score probe 的组合层结果：
- `entry_z=1.5`：`343` 笔，pair 均值 `mean_net_bps = -4.27`
- `entry_z=2.0`：`211` 笔，pair 均值 `mean_net_bps = -15.72`
- `entry_z=2.5`：`131` 笔，pair 均值 `mean_net_bps = -49.81`

也就是说，**把这条线先退化成 plain single/dual-spread threshold baseline 后，本地 `15m` 证据并没有给出一个足以直接升 `P2` 的稳健正 pocket**。只有局部 pair 还活着，例如：
- `SOLUSDT-LINKUSDT` 在 `entry_z=1.5` 下约 `+10.32 bps/trade`
- 但这不是组合层可迁移结论，更不是“copula 层已经被验证带来净增益”的证据

### 2) copula 路径目前仍主要停留在“论文与旧 proxy 支持值得保留”，而不是“本轮 survivor 要求的同口径 A/B 已完成”
现有与 copula 直接相关的本地证据主要是：
- `copula_reference_pairs_20260323/summary.json`：证明在论文样本映射下，`15m` proxy weekly candidate supply 很充足（22 周里 `>=2` 候选周占比 `100%`，top1/top2 的 `|tau|` 中位数较高）
- `2026-03-28_1148_btc-reference-copula-spread-mispricing-alpha.md`：证明论文原始设定下，`hourly` 版本本身可以独立活成完整策略

但这还**不是**当前 survivor follow-up 要求的那件事：
> 在同一 formation/trading split、同一 after-cost 口径下，正面对照 `single-spread z-score`、`dual-spread plain threshold / z-score`、`dual-spread copula conditional mispricing`，并量化 copula 这一层的独立净增益与 trade retention。

换句话说，**目前我们能诚实确认的是：copula 这条线“结构上值得保留”，但还不能诚实声称“在当前 desk 迁移口径下，它已经相对 plain baseline 留下经同口径验证的净增益”。**

### 3) survivor 预算只有一次；没有同口径增益 artifact，就不该继续占前排
Rank 224 已经用掉 fresh intake 后唯一允许的一次 survivor follow-up。当前这次 follow-up 没能把问题收敛成：
- `copula > plain baseline` 的已验证净增益；或
- 足够明确到可以直接进入 `P2 admission`

因此按 policy，**不能再给它第二次开放式 follow-up**。它应从前排退出，保留为 background 中的 `keep_P1` 结构性候选，而不是继续占用 survivor 槽位。

## 会改变系统认知的话
`Rank 224 / BTC reference + dual-spread copula conditional mispricing` 仍保留为值得记住的 `signal-layer upgrade` 型 `keep_P1` 候选，但本轮 survivor follow-up 没能提供同口径、成本后、相对 `single/dual-spread plain baseline` 的已验证独立净增益；而本地 plain `15m` baseline 组合层仍为负，因此该对象本轮不能升 `P2`，应按预算收口并转回 `Background pool`。

## 为什么不是 promote_P2
因为 `promote_P2` 需要回答的不是“论文原版曾经有效”，而是“在我们当前 desk 迁移口径里，这条 copula 条件误价层已经被验证为比 plain baseline 多出净增益，值得进入更重的 admission 流程”。这轮没有拿到这个级别的证据。

## 为什么也不是直接 drop_to_background
不是 fatal flaw。它仍然有两个保留价值：
1. 作为 `BTC-reference dual-spread relative mispricing` 的结构性新对象，它不是旧 pairs/z-score 换壳；
2. 论文与本地 proxy 仍支持它在更 faithful 的同构实现里可能留下净边。

所以更诚实的收口是：**`keep_P1 后转 background`**，不是 `P0`。

## 对应 runtime 动作
- 关闭 `Surviving candidate slot` 中的 Rank 224
- 将 Rank 224 记为 `keep_P1` 后退出前排、转入 `Background pool`
- 不改写 policy，不重排后续 cycle，只把当前小点标记完成
