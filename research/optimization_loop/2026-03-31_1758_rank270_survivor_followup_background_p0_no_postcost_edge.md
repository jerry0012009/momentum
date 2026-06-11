# Rank 270 / front-back annualized basis calendar spread — survivor follow-up 后转 background/P0

- 时间：2026-03-31 17:58 UTC
- 对应 cycle_plan 小点：`Rank 270 / front/back annualized basis calendar spread`
- 执行动作：执行它作为当前 `Surviving candidate` 的唯一一次 decisive follow-up；只回答在 same-venue BTC dated futures 上，统一 front/back 四腿成本、dated futures 流动性与 spot/proxy 误差后，这条 calendar-spread MR 是否仍保留可迁移净边，以及 holding-days distribution 是否仍 desk-feasible

## 本轮只回答什么
只回答 bot2 指定的 survivor 问题：

> 现有 clean-room replication 证据，是否足以支持 `same-venue BTC front/back annualized basis 收敛 × regime-aware calendar spread` 在现实成本与成交约束下升到 `P2`；若不能，是否应在用尽唯一 follow-up 后直接退出前排。

## 本轮使用的最小证据
沿用已落库的同 venue dated-futures 快检产物，并把它压成 survivor 所需的决定性摘要：

- 信号样本：`reports/artifacts/quant_digests/term_structure_calendar_20260324_0730/term_spread_15m_30d.csv`
- non-overlap 事件 PnL：`reports/artifacts/quant_digests/term_structure_calendar_20260324_0814_followup/event_pnl_nonoverlap.csv`
- 本轮补写摘要：`reports/artifacts/optimization_loop/rank270_survivor_followup_20260331_1758/summary.json`

这份 clean-room 代理口径已经是偏乐观的：它用 same-venue current/next quarter calendar ratio 做非重叠事件复盘，尚未额外计入更严的 dated-futures 深度折价、真实四腿冲击与更严格的 spot/proxy 误差惩罚；因此若它在这个口径下都站不住，就没有诚实理由升 `P2`。

## 决定性结果
### 1) 成本阈值不够厚
`126` 笔 non-overlap 事件的核心统计：

- 毛均值：`+6.61 bps/trade`
- 毛中位：`+5.66 bps/trade`
- `6 bps` round-trip 后净均值：`+0.61 bps/trade`
- `10 bps` round-trip 后净均值：`-3.39 bps/trade`
- `14 bps` round-trip 后净均值：`-7.39 bps/trade`

更关键的是分布而不是均值幻觉：

- `54.8%` 的交易毛收益 **小于 6 bps**
- `79.4%` 的交易毛收益 **小于 10 bps**

这说明这条线即使存在“会回归”的方向性，也大多只留下很薄的一层毛边；一旦把 four-leg 成本、dated futures 流动性和 proxy 误差压实，净边极易被完全吃掉。

### 2) 持有期 desk-feasible，但不是问题核心
holding distribution 本身并不差：

- 平均持有：`47.4` 分钟
- 中位持有：`45` 分钟
- `77.8%` 在 `60` 分钟内结束
- `100%` 在 `120` 分钟内结束
- `91.3%` 通过回归条件离场，`8.7%` timeout

所以这轮的新认知不是“它太慢所以不行”，而是：

> **它的持有期是可以接受的，但毛边太薄；问题在 post-cost edge，不在 desk 节奏。**

### 3) same-venue / spot-proxy 口径下的最诚实结论
当前这份 replication 仍是偏乐观 clean-room proxy：

- 已经限定在 `same-venue` dated futures，避免跨 venue 假象；
- 但 still 只是 calendar-ratio 代理，尚未把更严的真实四腿冲击、盘口容量衰减与 spot/proxy 定义误差全部单独罚进去；
- 在这个偏乐观口径下，净均值已经只剩 `+0.61 bps/trade @ 6bps`，并在 `10bps+` 全部转负。

因此 survivor 轮最该收口的话不是“再补一点稳定性”，而是：

> **即使沿用偏乐观的 same-venue clean-room 代理，Rank 270 的 post-cost edge 也不够厚；再加上 dated futures 真实四腿成本与 spot/proxy 误差，只会更差，不会更好。**

## survivor verdict
`Rank 270`：**用尽唯一 follow-up 后，不升 `P2`，直接转 `background/P0`**。

一句会改变系统认知的话：

> `Rank 270 / front/back annualized basis calendar spread` 的唯一 survivor follow-up 已完成：same-venue dated-futures clean-room 代理显示其持有期虽可接受，但毛均值仅 `+6.61 bps/trade`、`54.8%` 交易毛边低于 `6bps`，导致净均值在 `6bps` 下只剩 `+0.61 bps/trade`、在 `10bps+` 全部转负；因此这条 calendar-spread MR 不具备足够厚的可迁移 post-cost edge，本轮用尽唯一 follow-up 后直接回 `background/P0`。

## runtime write-back
- `Surviving candidate slot.current_target` → `none`
- `Surviving candidate slot.followup_budget_remaining` → `0`
- `Surviving candidate slot.latest_result` → 写为 `Rank 270` 已用尽 survivor follow-up，因成本后净边不够厚而不升 `P2`
- `Background pool.latest_parked` → 写为 `Rank 270` 回 `background/P0`
- `cycle_plan` 第 1 项：
  - `result` = `Rank 270 / front/back annualized basis calendar spread` 的唯一 survivor follow-up 已完成：same-venue dated-futures clean-room 代理显示其持有期虽可接受，但毛均值仅 `+6.61 bps/trade`、`54.8%` 交易毛边低于 `6bps`，导致净均值在 `6bps` 下只剩 `+0.61 bps/trade`、在 `10bps+` 全部转负；因此这条 calendar-spread MR 不具备足够厚的可迁移 post-cost edge，本轮用尽唯一 follow-up 后直接回 `background/P0`。
  - `status` = `done`
