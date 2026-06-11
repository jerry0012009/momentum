# Rank 333 — survivor follow-up — forecast shell vs plain z-score fade 收口失败，转入 background / P0

- 时间：2026-04-04 20:33 UTC
- 对象：`Rank 333 / dynamic-coint spread forecast × percentile trigger`
- 轮次角色：bot3 自动执行
- 结论：`drop_to_background / P0`

## 为什么这一步改变系统认知
`Rank 333` 的 survivor 唯一 follow-up 本来只需要回答一个 decisive question：在同一 `15m discovery -> 5m execution`、同 admission、同成本、同 time-stop 下，`forecast shell` 是否能系统性打赢 `plain z-score fade`。现有 clean-room A/B 结果已经足够明确：**forecast 只是在几组 major pairs 上“少亏一点”，没有把任何 pair 从负净边翻成可 admission 的正净边；因此它不是一个足以支撑升级的 distinct 可交易增量，而更像给本就不成立的 fade 壳加了一层过滤。**

## 本轮证据

### 1) 对照口径下，三组 pair 全部仍是负净边
来自 `reports/artifacts/rank248_dynamic_coint_followup/variant_summary.csv`：

- `BTCUSDT/ETHUSDT`
  - `plain_z`: `66` 笔，`mean_net_return = -0.002808`，`cumulative_net_return = -0.1699`
  - `forecast_q`: `52` 笔，`mean_net_return = -0.002307`，`cumulative_net_return = -0.1135`
  - `forecast_q_piw`: `34` 笔，`mean_net_return = -0.001686`，`cumulative_net_return = -0.0561`
- `BTCUSDT/SOLUSDT`
  - `plain_z`: `68` 笔，`mean_net_return = -0.001723`，`cumulative_net_return = -0.1114`
  - `forecast_q`: `47` 笔，`mean_net_return = -0.001920`，`cumulative_net_return = -0.0870`
  - `forecast_q_piw`: `28` 笔，`mean_net_return = -0.001012`，`cumulative_net_return = -0.0284`
- `ETHUSDT/SOLUSDT`
  - `plain_z`: `72` 笔，`mean_net_return = -0.002734`，`cumulative_net_return = -0.1797`
  - `forecast_q`: `61` 笔，`mean_net_return = -0.003188`，`cumulative_net_return = -0.1777`
  - `forecast_q_piw`: `40` 笔，`mean_net_return = -0.003539`，`cumulative_net_return = -0.1328`

这说明最关键的一点：**forecast filter 没有把任何一组 pair 变成成本后可 admission 的正净边 lane。** 最多只是降低交易数、压缩亏损幅度。

### 2) 汇总层面同样没有翻正，只是“少亏”
来自同一文件 `overall_compare.csv`：

- `plain_z`: `206` 笔，`mean_pair_mean_net_return = -0.002422`，`sum_cumulative_net_return = -0.4610`
- `forecast_q`: `160` 笔，`mean_pair_mean_net_return = -0.002472`，`sum_cumulative_net_return = -0.3783`
- `forecast_q_piw`: `102` 笔，`mean_pair_mean_net_return = -0.002079`，`sum_cumulative_net_return = -0.2173`

最好的版本 `forecast_q_piw` 确实比 `plain_z` 少亏，但系统该记住的不是“模型有点帮助”，而是：

> **在同 admission / 同 time-stop / 同成本下，它没有产出可交易正期望，只是把一个负期望 shell 过滤成“亏得慢一点”。**

这不满足 survivor follow-up 要求的 distinct 且可交易增量。

### 3) 另一份 pair-label gate 结果也只支持“过滤减损”，不支持升级
来自 `reports/artifacts/quant_digest_2026-04-04_pair_label_gate/pair_label_gate_summary.csv`：

- `ALL`: baseline `276` 笔，`baseline_avg_net = -0.5482 bps/trade`；筛选后 `111` 笔，`take_avg_net_selected = -0.3914 bps/trade`
- `BTCUSDT-ETHUSDT`: 从 `-0.6290` 改善到 `-0.3474 bps/trade`
- `BTCUSDT-SOLUSDT`: 从 `-0.3621` 改善到 `-0.2975 bps/trade`
- `ETHUSDT-SOLUSDT`: 从 `-0.6574` 改善到 `-0.4939 bps/trade`

AUC 有些区间高于随机，但 desk admission 看的不是“标签能不能分一点”，而是**成本后是否留下可交易 pocket**。这份结果同样没有给出任何正净边 lane。

## 出口判断
按 policy，这一步必须把 survivor 预算一次性收口，不能再拖第二次 follow-up。出口如下：

- **不是 `promote_P2`**：因为 forecast shell 没有在同口径 A/B 下留下任何成本后正净边 lane，达不到 admission 候选门槛。
- **也不是 `blocked`**：因为 decisive question 已经被现有证据明确回答，不存在“缺唯一 blocker 还得再测”的情况。
- **因此应直接 `drop_to_background / P0`**：系统应把 `Rank 333` 记成一条诚实结论——它的 forecast 叙事最多是负 alpha 上的 thinning/filter，而不是足以升级的 distinct tradable edge。

## 对 runtime 的直接影响
- `Surviving candidate slot`：`Rank 333` 用完唯一一次 follow-up，且结论失败，槽位释放为 `none`。
- `Background pool`：记录 `Rank 333` 因 survivor A/B 收口失败而转入 `P0`。
- `Fresh intake slot`：保留最近一次 fresh intake 完成记录即可，不需要改写其历史首判事实。
- `cycle_plan #1`：标记为 `done`，result 写成“forecast shell 在同口径下只实现减损、未产生正净边，故 `Rank 333` survivor follow-up 收口失败并转入 background/P0”。

## Reader-facing takeaway
这条线最该被记住的不是“dynamic-coint + forecast 很高级”，而是：

**如果 plain z-score fade 本身在 major-pair 诚实成本口径下就站不住，给它再叠一层 forecast / percentile trigger，往往也只是把亏损变稀，不会自动变成可 paper 的 edge。**
