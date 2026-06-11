# 2026-03-23 15:43 UTC · Rank 151 / rolling-split stability verdict

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 本轮未见 `Interrupt` 级异常
- 顶板 `Next 3 bot3 runs / Run 1 = Rank 151 的 rolling / split 稳定性`
- 因此本轮不再补第三条 family，也不回头重做同类诚实门；只回答一个最值钱问题：

> `Rank 151` 在已经通过的两条 family 上，`band_pass` 的 uplift 是否前后半程都还站得住？

## 1. 为什么这轮做这件事
到上一轮为止，`Rank 151` 已经拿到三层证据：
1. local frozen A/B/C cut；
2. `breakout-short` family honest gate + 月度时间稳定性初检；
3. `fib retest` 第二 family replication 通过。

这时继续补第三条 family 的边际价值已经下降。真正能改变 desk 层级判断的一刀，是把两条已通过 family 都做一个最小但正式的 `rolling / split` 裁决，回答它是否真有资格进入 `P2 discussion`。

## 2. 本轮实际动作
新增并执行：
- `scripts/build_rank151_rolling_split_verdict.py`

输入：
- `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/trades.csv`
- `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/monthly_uplift_vs_baseline_primary_cost.csv`
- `reports/artifacts/scout_rank151_fib_retest_family_honest_gate_15m/trades.csv`

固定口径：
- 只看 `6bps / side` primary 成本层
- family 只用已经完成的两条：`breakout_short`、`fib_retest_long`
- 对每条 family 按时间顺序切成 `front_half / back_half`
- 主判据：`band_pass` 在两个 split 上都要继续优于 `baseline`

新增产物：
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/rolling_split_summary.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/rolling_split_uplift.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/rolling_split_family_score.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/rolling_split_scorecard.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/rolling_split_summary.json`
- 页面：
  - `reports/site/factors/scout_rank151_ewmac_breakout_bandpass_gate_15m/rolling_split_verdict.html`
  - `reports/site/reading/repo_scout/rank151_ewmac_breakout_bandpass_gate_rolling_split.html`

## 3. 主结果：两条 family 的 split uplift
来自：`rolling_split_uplift.csv`

### breakout_short
- `front_half`
  - baseline = `+0.53 bps/trade`
  - band_pass = `+10.35 bps/trade`
  - uplift = **`+9.82 bps`**
  - trades：band_pass `530` vs baseline `861`
- `back_half`
  - baseline = `-7.45 bps/trade`
  - band_pass = `+0.49 bps/trade`
  - uplift = **`+7.94 bps`**
  - trades：band_pass `503` vs baseline `866`

### fib_retest_long
- `front_half`
  - baseline = `+34.03 bps/trade`
  - band_pass = `+44.71 bps/trade`
  - uplift = **`+10.68 bps`**
  - trades：band_pass `5` vs baseline `11`
- `back_half`
  - baseline = `+1.29 bps/trade`
  - band_pass = `+33.57 bps/trade`
  - uplift = **`+32.28 bps`**
  - trades：band_pass `15` vs baseline `23`

## 4. 紧邻子点：family 级 pass/fail 是否统一成立
来自：`rolling_split_family_score.csv`

- `breakout_short`：
  - positive uplift splits = `2/2`
  - positive band_pass splits = `2/2`
  - `family_pass = True`
- `fib_retest_long`：
  - positive uplift splits = `2/2`
  - positive band_pass splits = `2/2`
  - `family_pass = True`

补充：
- `breakout-short` 之前的月度初检已确认：`band_pass uplift` 在 `7` 个月里 `5/7` 为正
- 现在又补上前后半程 split 也都为正，说明它不是只在单月或单半段 pocket 成立

## 5. 本轮最值钱的结论
1. **Rank 151 已完成顶板要求的 rolling/split 稳定性。**
   两条已通过 family 在 `front_half / back_half` 上都继续保持 `band_pass > baseline` 的 uplift，且 `band_pass` 自身也都没有 split 内翻负。
2. **它现在更像真正的 shared gate 预审通过，而不只是 replication 漂亮。**
   `breakout-short` 的样本更大，前后半程都继续优于 baseline；`fib retest` 虽然样本小，但方向一致且 back-half 甚至继续扩大 uplift。
3. **desk 口径应从 `keep_P1 but stronger` 正式推进到 `P2 / pre-paper candidate`。**
   下一轮最值钱动作不再是补 family，而是写清楚 `P2 discussion`：
   - 这条 shared gate 到底解决了什么；
   - 为什么还不能直接进 `P3 / Paper launch queue`；
   - 若继续推进，最小 admission bar 是什么。

## 6. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 3/3`
- `cross_asset_stability = 3/3`
- `cost_trade_stability = 3/3`
- `deployability = 2/3`
- `recommended_action = promote_P2_discussion`
- `why_now = 顶板 Run 1 已明确要求在两条 family replication 之后，优先用 rolling/split 稳定性回答它是否真有资格进 P2 discussion。`
- `main_weakness = fib retest 样本仍偏小；这次裁决更像 shared-gate 预审通过，不是直接进入 Paper 的 deploy 证据。`

## 7. 本轮顺手刷新了 authoritative 顶板
已同步更新：
- `Active Scout 排序` 中 `Rank 151` 的层级口径：`P2 / pre-paper candidate`
- `Next 3 bot3 runs`：把默认 Run 1 改成 `Rank 151` 的 `P2 discussion` write-up
- `最近关键 evidence`：补入 rolling/split 通过的最新一条

## 8. 一句话结论
`Rank 151` 这轮拿到的不是又一条重复 replication，而是更值钱的层级裁决：在 `breakout-short` 与 `fib retest` 两条已通过 family 上，`band_pass` 对 baseline 的 uplift 在 `front_half / back_half` 都继续成立，因此它已经足以从 **`keep_P1 but stronger`** 正式推进到 **`P2 / pre-paper candidate`**；下一轮应写 `P2 discussion`，而不是继续补第三条 family。
