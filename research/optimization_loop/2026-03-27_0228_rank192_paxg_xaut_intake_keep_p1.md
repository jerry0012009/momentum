# Rank 192 / PAXG-XAUT rich-spread rolling-fair residual mean reversion — fresh intake keep_P1

- 时间：2026-03-27 02:28 UTC
- 对象：`research/quant_digests/2026-03-27_0145_paxg-xaut-rolling-fairspread-mr.md`
- 轮次角色：bot3 fresh intake 最小首判
- 结论：`keep_P1`
- Assigned Rank: `192`

## 本轮只回答一个问题
`PAXG/XAUT rolling fair-spread residual mean reversion`，是否已经值得作为一个**单一可执行对象**留在前排；还是它本质上只是 repo 里的 fixed-grid execution 包装，应该直接 `park`。

## 这轮保留的唯一对象
本轮保留的不是整个 GoldArb repo family，也不是“黄金双币套利”这个泛化题材；只保留下面这条最小对象：

`Rank 192 / PAXG-XAUT rich-spread rolling-fair residual mean reversion`

翻成人话：只盯 **同 venue、同黄金锚** 的 `PAXG/XAUT` 相对价差；不用固定 `10/20/30bps` 绝对网格，而是先用 rolling fair spread 定义“当前正常价差”，只在 **rich spread 明显高于 fair spread** 时做 `short rich leg / long cheap leg` 的收敛。

## 为什么这轮给 keep_P1
1. **base alpha 是独立对象，不只是 execution 花活。**
   这份 digest 已经把对象压成了可单独检验的 raw alpha：`spread - rolling fair spread` 的 residual mean reversion，而不是依赖 repo 原作者的固定阈值网格才能成立。
2. **固定绝对 spread 明显在漂移，rolling-fair 定义因此有信息增量。**
   digest 里给出的 Bybit 公共 `5m` 快检已经显示绝对 spread 中位数从 `21d` 的约 `59.6bps` 快速滑到 `3d` 的约 `14.7bps`；这会直接改变系统认知：对象该保留的是“相对 fair spread 的偏离”，不是“某个永恒固定档位”。
3. **信号方向已经足够收窄。**
   当前最像真的不是对称双边，而是 `z > 2` 一侧的 **rich-spread fade**；这让 survivor follow-up 可以继续保持单边、最小、可裁决。
4. **但它还没到 P2。**
   现有证据仍是 public kline quick check；`3h` 毛收敛只在约 `6bps` 量级，明显不足以支持“四腿 taker 直上”的乐观解释。这个对象能不能活，关键还在 maker-first / repair stress / 时间稳定性，而这些都还没被最小诚实复核完。

## 为什么不是 park
- 这不是空泛“黄金相关资产可能回归”的叙事，而是一个可直接写成 clean-room spec 的单 venue pairs 对象；
- 不需要跨 venue 搬砖，也不依赖私有数据才能起步；
- 更重要的是，它现在已经带着一个**唯一且便宜的 decisive follow-up**，而不是需要再补半页抽象研究计划。

## 唯一 survivor follow-up 应该测什么
只测一刀：

**在 Bybit 公共 `1m` 主时钟下，`PAXG/XAUT` 的 `rolling fair spread` rich-side residual（如 `z > 2 / 2.5`）相对 fixed absolute grid，是否能在显式 maker/taker repair stress 与时间分桶下，仍保留足以进入 `P2` 的单边净收敛轮廓。**

如果答案是：
- **有**：可以 `promote_P2`；
- **没有**：就应直接 `park_to_background`，不要把它扩写回整个 gold-arb family。

## 单一句子结果
`Rank 192 / PAXG-XAUT rich-spread rolling-fair residual mean reversion` 的 fresh intake 已收口为 `keep_P1`：当前值得保留的不是 repo 里的 fixed-grid 执行外壳，而是“同 venue 黄金双币价差相对 rolling fair spread 的单边高位回归”这条最小 raw alpha；它值得用唯一一次 survivor follow-up 去回答成本与时间稳定性后是否仍足够进入 `P2`。

## 运行态回写
- `Fresh intake slot`：更新为 `Rank 192 / PAXG-XAUT rich-spread rolling-fair residual mean reversion`，结论 `keep_P1`
- `Surviving candidate slot`：载入 `Rank 192`，`followup_budget_remaining = 1`
- `cycle_plan[2]`：写入上述单句结果并标记 `done`
- 其余前排槽位保持不变
