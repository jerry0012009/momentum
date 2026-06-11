# Rank 157 / H<0.5 spread-band fast mean-reversion fresh intake

- 时间：2026-03-25 02:00 UTC
- 执行身份：bot3 自动执行器
- 本轮执行小点：`cycle_plan #1` / Fresh intake slot
- 来源底稿：`research/quant_digests/2026-03-25_0158_antipersistent-hurst-pairs-fast-meanreversion.md`

## 1. 本轮为什么选它
当前 runtime 前排已清空为 `ready_for_new_intake`，且 policy 要求 bot3 只执行当前 `cycle_plan` 最前的 pending 小点。因此本轮只认领一个新的 raw alpha intake，并直接回答它是 `park` 还是 `keep_P1`。

我选用刚完成的 `Anti-Persistent Values of the Hurst Exponent Anticipate Mean Reversion in Pairs Trading` clean-room digest 作为 intake 对象，因为它同时满足：
1. 有公开全文与完整可编码骨架；
2. 不是纯 filter story，而是可独立落地的 pairs / stat-arb raw alpha；
3. 已有本地 Binance 公共数据最小快检，不需要再靠空泛摘要猜测。

## 2. 最小公开证据
底稿已给出三个足够改变系统认知的公开证据：
1. 2024 主论文不是只讲“相关性更高”，而是把 `local H<0.5` 明确绑定到 **spread 更快回归**，并给出 quasi-natural experiment；
2. 论文主策略是完整闭环：`pair selection + spread z-score entry + H<0.5 admission + mean/2σ/72h exit`，不是只有单一指标；
3. 2025 follow-up 继续支持 GHE / Hurst 路线在 crypto pairs 上相对传统选对方法仍具竞争力。

翻成人话：这条线真正有价值的地方，不是“又多了一个 fancy filter”，而是它把 pairs desk 最难活过成本的那一段——**回得慢**——压成了一个可验证的 fast-reversion admission layer。

## 3. 本地最小快检怎么读
底稿里的本地 probe（Binance USDT perp，15m，最近 60 天，28 个 pair）已经足够做 fresh-intake first verdict：
- `H<0.5` pocket 很稀疏（约 `5.47%`），说明它天然更像 admission layer，不是全时常开策略；
- 但一旦触发，median 回归时间从约 `24.0h` 缩到约 `13.75h`，速度优势仍然存在；
- 可是若把它粗暴地当成“所有 pair 一起扫”的简化盈利策略，正收益占比只有约 `35.2%`，说明 **速度优势 ≠ 已经证明成本后赚钱**。

这一步已经足以回答 intake 问题：
- 它不是空洞文献线索；
- 它也还没到 `promote_P2`，因为选对、成本、timeout、并发治理这些 admission 关键块还没被 honest 封口；
- 最诚实的位置是：**有独立 alpha identity，值得保留一次 survivor follow-up。**

## 4. fresh intake verdict
本轮将该对象正式分配为 **`Rank 157`**，verdict = **`keep_P1`**。

原因：
1. 它有清楚的 raw alpha 骨架（不是只有模糊 ML / 叙事）；
2. 本地快检已经复现出“更快回归”这一核心机制，足以证明不是纸上谈兵；
3. 但当前还缺唯一 decisive follow-up：必须把它从“全宇宙 H filter”收缩成“候选 pair admission layer”，并用 `pair selection × H window × timeout × cost` 的最小 honest 切面回答它是否真能跨过成本线。

## 5. 对 runtime 的唯一必要影响
- Fresh intake slot：从 `ready_for_new_intake` 更新为 `Rank 157 / H<0.5 spread-band fast mean-reversion`，结论 `keep_P1`；
- `cycle_plan #1`：标记为 `done`，并写入改变系统认知的一句话结果；
- 其余轮次排班不在本轮改动范围内。

## 6. 一句话结果（用于 state 回写）
`Rank 157 / H<0.5 spread-band fast mean-reversion` 已凭“公开论文给出完整 pairs fast-reversion 骨架，且本地 15m probe 复现出明显更快回归但尚未证明成本后盈利”的证据进入 `keep_P1`；下一步只值得做 1 次 survivor 级的 `pair-selection × cost × timeout` decisive follow-up。
