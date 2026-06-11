# Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day — survivor follow-up 收口回 background/P0

- 时间：2026-03-30 10:49 UTC
- 轮次动作：`cycle_plan` 第 1 项（唯一 survivor follow-up）
- 对象：`Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day`
- 结论：**唯一 follow-up 用完，不升 P2，回 `background/P0`**

## 本轮只回答什么
只回答一个问题：

> 在 `BTCUSDT` 近 90 天本地 `1m` 数据上，把 `pseudo trading day` 锚点限制为 `UTC 00/08/16`，并做 `30d train / 7d OOS` 的滚动 `hour-pair` 审查后，是否还能留下少数对 `15m/5m` 执行成本后有边的稳定 `continuation / reversal` pockets？

## 采用的最小诚实检查
- 数据源：`reports/artifacts/scout_rank228_dc_overshoot_survivor_followup/btcusdt_1m.csv`
- 样本区间：`2025-12-28 19:00 UTC` 到 `2026-03-28 19:00 UTC`
- 先把 `1m` 聚成 `1h`；不扩成跨资产，不偷换成 generic seasonality
- 仅测 3 个允许锚点：`UTC 00 / 08 / 16`
- 每个锚点下：
  - 用完整伪交易日构造 `24` 个 hour slot
  - 每窗 `30d` 训练、`7d` OOS
  - 在训练窗里从 `hour-pair (i,j)` 网格里选当窗最强 pair
  - 用 `sign(beta) * sign(r_i) * r_j - 6bps roundtrip` 记 OOS 净收益
- 这一步不是证明“某个时钟口袋能偶尔赚钱”，而是看 **最佳 pair 是否能跨窗重复出现、且 OOS 成本后仍为正**

产物：
- `reports/artifacts/rank251_survivor_followup_20260330/anchor_summary.csv`
- `reports/artifacts/rank251_survivor_followup_20260330/pair_reuse_counts.csv`
- `reports/artifacts/rank251_survivor_followup_20260330/all_window_best_pairs.csv`
- `reports/artifacts/rank251_survivor_followup_20260330/decision.json`
- 复现实验脚本：`scripts/build_rank251_survivor_followup.py`

## 结果
### 1) 三个锚点的 OOS 平均都为负
`anchor_summary.csv`：

- `UTC 00`：`8` 个 OOS 窗，`6` 个不同最佳 pair，平均 `test_mean_net_bps = -9.07`
- `UTC 08`：`8` 个 OOS 窗，`6` 个不同最佳 pair，平均 `test_mean_net_bps = -9.87`
- `UTC 16`：`8` 个 OOS 窗，`8` 个不同最佳 pair，平均 `test_mean_net_bps = -10.29`

也就是说，即便允许每个滚动窗都重新挑“当时最强”的 pair，三种伪交易日锚点的 OOS 成本后平均结果仍然都是负的。

### 2) 最佳 pair 会频繁换槽，不像稳定 pocket
`pair_reuse_counts.csv` 里只有少数 pair 重复出现：

- `anchor 00`：`11 -> 17` continuation，出现 `3` 次
- `anchor 08`：`0 -> 6` continuation，出现 `2` 次
- `anchor 08`：`3 -> 9` continuation，出现 `2` 次

但这些“重复出现”的 pair 仍没有留下稳定正 OOS：

- `anchor 00 / 11 -> 17`
  - 三次测试分别约 `-0.91 / +0.82 / -19.33 bps`
- `anchor 08 / 0 -> 6`
  - 两次测试约 `-40.09 / -13.27 bps`
- `anchor 08 / 3 -> 9`
  - 两次测试约 `-0.91 / +0.82 bps`

所以问题不是“没有任何重复 pair”，而是 **重复 pair 也不稳定，且净边不够诚实**。

### 3) 偶尔正窗存在，但更像网格挖掘噪音
例如：
- `anchor 00 / 13 -> 19` reversal 在一个 OOS 窗是 `+28.55 bps`
- `anchor 08 / 5 -> 11` reversal 对应同一物理时段也有 `+28.55 bps`
- `anchor 00 / 6 -> 13` reversal 在最后一窗是 `+23.28 bps`

但这些胜窗都没有在后续滚动窗里延续成可重复 pocket；最佳 pair 不断漂移，本质更像 `24x24` 网格里滚动挑赢家，而不是策略对象本身已经压缩成少数稳定映射。

## survivor 收口 verdict
`Rank 251` 的唯一 survivor follow-up 已经给出否定回答：

**在 `UTC 00/08/16` 三种受限 pseudo-day 锚点下，近 90 天 BTC `hour-pair` 映射没有留下“重复出现且 OOS 成本后仍为正”的稳定 pocket；最佳 pair 跨窗频繁换槽，重复 pair 自身也缺乏稳定正边。**

因此，这条线当前更像：
- 论文层可讲述的 `hour-pair mining framework`
- 但落到 desk 的最小 honest 检查后，仍主要依赖网格挑选与样本漂移

所以按 policy，**不升 `P2`，唯一 follow-up 用完，回 `background/P0`。**

## 本轮结果句
`Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day` 的唯一 survivor follow-up 已收口：受限于 `UTC 00/08/16` pseudo-day 锚点与 `30d train / 7d OOS` 审查后，BTC 近 90 天并没有留下少数可重复、成本后仍为正的稳定 `hour-pair` pocket；最佳 pair 跨窗频繁漂移，因此本轮 verdict 是唯一 follow-up 用完，回 `background/P0`。
