# 2026-03-23 01:18 UTC · Rank 140 / Rank 137 exclusive pocket shape

## 本轮按顶板顺序执行

### Run 1 · Paper / interrupt check
- `docs/TODO.md` 顶板显示 `Paper / 待开启自动运行 = empty`
- 未见需要抢占默认队列的真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`
- 因此本轮继续按默认队列走 `Scout`

### Run 2 · 当前主点
- `Rank 14b` 已完成唯一允许的最小 clean replication，并已补 scorecard；本轮不回头续磨
- 延续上一轮 `Rank 140 / Rank 137` 的 family 诊断，只做 **1 个主点**：
  - 把 `Rank 137` 的 **exclusive pockets** 压成更清楚的 desk 读法

### Run 3 · 唯一紧邻子点
承接 `00:39 UTC` overlap cut 与 `01:05 UTC` shared-pocket cut，本轮只追问：

> `confirm_window12_only` 这块正 pocket，到底像不像“可解释 strict 语义”，还是仍然只是零散 pocket？

本轮 **不**：
- 新开第二个 family
- 回头碰 `Rank 125 / 112 / 111`
- 给 `Rank 14b` 第二刀
- 做已自跑 paper runner 的 routine health-check

---

## 本轮产物
目录：`reports/artifacts/pbo_cscv_honesty_gate/rank137_exclusive_pocket_diagnosis/`

- `asset_summary.csv`
- `setup_summary.csv`
- `hour_summary.csv`
- `dow_summary.csv`
- `confirm_window12_only_asset_setup_summary.csv`
- `confirm_window12_only_asset_hour_summary.csv`
- `confirm12_entry24_only_asset_setup_summary.csv`
- `confirm12_entry24_only_asset_hour_summary.csv`
- `summary.json`

输入口径：
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_entry24_overlap_matrix.csv`
- 对每笔统一计算 `net_6bps = gross_return - 12bps roundtrip`
- 继续只比较三段：
  1. `confirm_window12_only`
  2. `confirm12_entry24_only`
  3. `shared`

---

## 核心结果

### 1) `confirm_window12_only` 不是单一资产侥幸 pocket，而是三资产都为正
`confirm_window12_only`：
- `trades = 88`
- `mean_net_6bps = +100.62 bps`
- `win_rate = 72.7%`

分资产：
- `SOL-USD`：`40` 笔，`+113.64 bps`，`win_rate = 75.0%`
- `ETH-USD`：`28` 笔，`+94.23 bps`，`win_rate = 71.4%`
- `BTC-USD`：`20` 笔，`+83.54 bps`，`win_rate = 70.0%`

这比上一轮的 desk 读法更进一步：
- 它**不是只靠 SOL 单腿拉出来**；
- 三资产方向一致都偏正；
- 因而 `confirm_window_12` 的 exclusive pocket 至少具备了“不是孤立样本噪声”的最低诚实度。

### 2) 但它仍未收敛成“简单单一 setup 规则”
`confirm_window12_only` 的正 pocket 主要分布：
- `ETH / breakout_short`：`27` 笔，`+96.08 bps`
- `SOL / breakout_short`：`33` 笔，`+86.37 bps`
- `BTC / breakout_short`：`13` 笔，`+73.99 bps`
- 同时还夹着一小块 `ema_psar_long`：
  - `SOL / ema_psar_long`：`6` 笔，`+281.91 bps`
  - `BTC / ema_psar_long`：`5` 笔，`+128.81 bps`

最重要的 desk 解释：
- 正值主体看起来还是 **`breakout_short` across 3 assets**；
- 但 pocket 里并不是只剩一个非常干净的 setup 语义，仍夹着少量 `EMA/PSAR long` 的高收益小样本；
- 所以它更像 **“偏宽但确实有料的 exclusive pocket”**，还不是能直接写成 reader-friendly strict deployment rule 的状态。

### 3) `confirm12_entry24_only` 更窄、更弱，也更不像主规则
`confirm12_entry24_only`：
- `trades = 47`
- `mean_net_6bps = +37.59 bps`
- `win_rate = 59.6%`

分资产：
- `ETH-USD`：`15` 笔，`+65.09 bps`
- `SOL-USD`：`19` 笔，`+43.55 bps`
- `BTC-USD`：`13` 笔，`-2.85 bps`

读法：
- 它仍是正 pocket，但比 `confirm_window12_only` 更窄、更弱；
- `BTC` 已接近打平偏负；
- 因此当前更不适合作为 family 的默认主语义。

---

## 轻量 scorecard
- `usefulness = medium_to_high`
- `time_stability = weak_to_medium`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `confirm_window12_only_not_single_clean_setup_rule`
- `exclusive_alpha_still_depends_on_pocket_selection`
- `ema_psar_long_subsample_still_mixed_into_positive_pocket`
- `confirm12_entry24_only_btc_not_working`

### recommended_action
- **`keep_P1`**

### why_now
上一轮已经证明 `shared core` 为负；本轮需要进一步回答：`Rank 137` 的正 evidence 是否至少收敛成一块有解释性的 exclusive pocket。答案是：`confirm_window12_only` 已不再像单资产偶然噪声，但仍未收敛成足够简单、足够可部署的 strict rule，因此可以增强 evidence，却还不该 promote。

### main_weakness
当前 family 的正值仍主要来自 pocket selection，而不是一个干净的 shared rule。即便 `confirm_window12_only` 在三资产上都为正，它内部仍混着不止一个 setup 语义，说明“为什么它该被保留、为什么另一块该被剔除”还不够简洁稳定。

---

## Desk 结论更新
对 `Rank 140 / Rank 137` 当前最诚实的读法可进一步压缩为：

1. `Rank 137` 仍是 `Rank 140` 当前最像样的正例 family；
2. `shared` overlap core 为负，这点不变；
3. 最强正 evidence 来自 `confirm_window12_only`；
4. 这块 exclusive pocket **并非单一资产噪声**，因为 BTC / ETH / SOL 三腿都为正；
5. 但它仍**不是一个足够干净的单一 strict 语义**，暂时更适合继续作为 `keep_P1 / active compare anchor evidence strengthened`，而不是升到 `P2/P3`。

## 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0118_rank140-rank137-exclusive-pocket-shape.md`
- 诊断产物：`reports/artifacts/pbo_cscv_honesty_gate/rank137_exclusive_pocket_diagnosis/`

## 对下一轮的最短提醒
- 若继续给 `Rank 140` 预算，下一刀只值得做：
  - 把 `confirm_window12_only` 里 `breakout_short` 主体单独剥出来，看去掉零碎 `ema_psar_long` 后是否仍保持 guard-passed 级别的正 pocket；
- 若不做这刀，就应把 `Rank 140` 继续留作 active compare anchor，并考虑切 fresh intake reserve。
