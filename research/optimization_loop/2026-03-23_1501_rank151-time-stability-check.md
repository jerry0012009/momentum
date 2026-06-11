# 2026-03-23 15:01 UTC · Rank 151 / breakout-short family time-stability check

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 本轮未见 `Interrupt` 级异常
- 顶板 `Next 3 bot3 runs` 里，`Run 1 = Rank 151 的单 family honest gate`
- 该主动作已在上一轮（`2026-03-23_1440_rank151-breakout-short-family-honest-gate.md`）完成，所以本轮沿同一主线继续做**最短 verdict-changing 邻近检查**：时间稳定性

## 1. 为什么这轮做这件事
`Rank 151` 现在已经有两层证据：
1. local frozen A/B/C cut
2. `breakout-short` 单 family honest gate

这时最便宜、最能改变 desk 判断的一刀，不是继续微调阈值，而是先回答：

> 上一轮看到的 `band_pass` uplift，是否只是某一个月份的偶然窗口？

如果答案是否，那么它才有资格从“generic proxy 有戏”进一步收紧为“family 级 evidence 真存在”；如果答案是“纯靠单月”，那就不该急着讨论 `P2`。

## 2. 本轮实际动作
新增并执行：
- `scripts/build_rank151_time_stability_check.py`

复用输入：
- `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/trades.csv`
- `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/pooled_summary.csv`

新增产物：
- `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/monthly_stability_primary_cost.csv`
- `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/monthly_uplift_vs_baseline_primary_cost.csv`
- 刷新页面：
  - `reports/site/factors/scout_rank151_breakout_short_family_honest_gate_15m/report.html`
  - `reports/site/reading/repo_scout/rank151_breakout_short_family_honest_gate.html`

固定口径：
- family：`breakout-short`
- variants：`baseline / hard_positive / band_pass`
- primary cost：`6bps / side`
- 时间切片：按 `ts` 月份拆分

## 3. 主结果（按月）
来自：`monthly_stability_primary_cost.csv`

### baseline（月均 net / trade, bps）
- `2025-09`: `-23.07`
- `2025-10`: `+2.48`
- `2025-11`: `+7.67`
- `2025-12`: `-6.20`
- `2026-01`: `-3.02`
- `2026-02`: `+0.74`
- `2026-03`: `-18.79`

### hard_positive（月均 net / trade, bps）
- `2025-09`: `-26.70`
- `2025-10`: `+5.08`
- `2025-11`: `+9.94`
- `2025-12`: `-22.15`
- `2026-01`: `-1.15`
- `2026-02`: `+7.44`
- `2026-03`: `-18.95`

### band_pass（月均 net / trade, bps）
- `2025-09`: `-13.21`
- `2025-10`: `-4.49`
- `2025-11`: `+28.34`
- `2025-12`: `-4.82`
- `2026-01`: `-3.77`
- `2026-02`: `+15.53`
- `2026-03`: `+0.07`

## 4. 紧邻子点：uplift 是否跨月存在
来自：`monthly_uplift_vs_baseline_primary_cost.csv`

### band_pass - baseline（月均 net uplift, bps）
- `2025-09`: `+9.86`
- `2025-10`: `-6.97`
- `2025-11`: `+20.67`
- `2025-12`: `+1.38`
- `2026-01`: `-0.75`
- `2026-02`: `+14.79`
- `2026-03`: `+18.85`

### quick read
- `band_pass` 相对 `baseline` 的 uplift 为正：`5/7` 个月
- `band_pass` 自身月均净值为正：`3/7` 个月
- `hard_positive` 相对 `baseline` 的 uplift 为正：`4/7` 个月，但月份分布更弱，且没有上一轮那种 pooled 优势质量

## 5. 本轮最值钱的结论
1. **Rank 151 不是“只靠单月 luck”的 family 假象。**
   `band_pass` 相对 `baseline` 的 uplift 在 `7` 个月里有 `5` 个月为正，说明它确实抓到某种跨月可复现的 family 守门方向。
2. **但它也还不是成熟 allow gate。**
   `band_pass` 自己只有 `3/7` 个月月均为正，且 `2025-10 / 2026-01` 仍会失手；因此这条线更像“减少坏交易、改善 family 结构”，还不是稳定 deployment gate。
3. **当前最诚实 desk 口径仍是 `keep_P1 but stronger`，但已经更接近 `P2 discussion`。**
   现在它不再只是 generic proxy 里的漂亮切片，也不只是单 family 上的单点 uplift；它已经开始展现跨月的 family-level evidence。下一刀该优先做：
   - 第二 family 复核，或
   - 更正式的时间稳定性切片（rolling / split）

## 6. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 2/3`
- `cross_asset_stability = 3/3`（沿用上一轮，3 资产都优于 baseline）
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `recommended_action = keep_P1 but stronger`
- `why_now = 首条 family gate 已落地，最便宜且最能改变判断的一刀就是先验真它是不是时间窗幻觉。`
- `main_weakness = uplift 跨月存在，但 band_pass 自身仍不是每月都稳；还缺第二 family 或更严格 rolling/stability 复核。`

## 7. 一句话结论
`Rank 151` 现在已经不只是“generic proxy 上看起来不错 + 单 family 上偶然转正”。在 `breakout-short` family 里，`band_pass` 对 `baseline` 的 uplift 已经表现出 **5/7 个月为正** 的跨月证据；但由于它自身仍只有 `3/7` 个月月均为正，所以当前最诚实的 desk verdict 仍应维持：**`keep_P1 but stronger`，离 `P2` 还差第二 family 或更严格稳定性复核。**
