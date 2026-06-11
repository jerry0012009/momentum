# 2026-03-23 16:35 UTC · Rank 151 / launch admission bar

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行` 在本轮开始时仍是 `empty`
- 本轮未见 `Interrupt` 级异常
- 顶板 `Next 3 bot3 runs / Run 1 = 给 Rank 151 做 1 个面向 launch 的 admission-bar check`
- 因此本轮不补第三条 family，不做新的大范围研究扩张；只回答一个最值钱问题：

> `Rank 151` 在最可能承载它的 `breakout-short` family 上，是否已经具备进入 `P3 / Paper launch queue` 的最小 launch 证据？

## 1. 本轮实际动作
新增并执行：
- `scripts/build_rank151_launch_admission_bar.py`

输入：
- `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/trades.csv`

固定口径：
- 只看 `breakout-short` 承载 family
- 只看 primary 成本层：`6 bps / side`
- 只做 `30 / 60 / 90d recent-slice` 检查
- 判据固定为：
  1. `band_pass uplift vs baseline > 0`
  2. `band_pass mean_net_bps > 0`
  3. `band_pass trades / active_day >= 4`
  4. `asset coverage = 3/3`

新增产物：
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/launch_admission_recent_slice_summary.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/launch_admission_recent_slice_asset_summary.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/launch_admission_density_scorecard.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/launch_admission_scorecard.csv`
- `reports/artifacts/scout_rank151_ewmac_breakout_bandpass_gate_15m/launch_admission_summary.json`
- 页面：
  - `reports/site/factors/scout_rank151_ewmac_breakout_bandpass_gate_15m/launch_admission_bar.html`
  - `reports/site/reading/repo_scout/rank151_ewmac_breakout_bandpass_gate_launch_admission_bar.html`

## 2. 主结果：recent-slice uplift + density 都过线
来自：`launch_admission_density_scorecard.csv`

### 30d
- `band_pass mean_net_bps = +11.63`
- `baseline mean_net_bps = -3.46`
- uplift = **`+15.09 bps`**
- `band_pass trades = 146`
- `active_days = 22`
- `trades / active_day = 6.64`
- `asset coverage = 3/3`
- `admission_slice_pass = True`

### 60d
- `band_pass mean_net_bps = +11.33`
- `baseline mean_net_bps = -2.44`
- uplift = **`+13.77 bps`**
- `band_pass trades = 345`
- `active_days = 48`
- `trades / active_day = 7.19`
- `asset coverage = 3/3`
- `admission_slice_pass = True`

### 90d
- `band_pass mean_net_bps = +2.43`
- `baseline mean_net_bps = -6.21`
- uplift = **`+8.63 bps`**
- `band_pass trades = 460`
- `active_days = 73`
- `trades / active_day = 6.30`
- `asset coverage = 3/3`
- `admission_slice_pass = True`

## 3. 紧邻子点：这不是“只在近月好看但跑不起来”的口袋
按 desk 现在要回答的问题，最关键的不是再证明它“研究上有意思”，而是看它有没有资格占用接下来 `Paper launch` 的 3 轮预算。

这轮 admission bar 给出的答案是：**有。**

原因：
1. recent slices 没有塌：`30 / 60 / 90d` 的 uplift 全为正；
2. `band_pass` 自身在这三个窗口里都保持正均值，而不是只靠 baseline 更差；
3. trade density 足够实用：聚合后约 `6.3~7.2 trades/active_day`；
4. `BTC / ETH / SOL` 三资产都继续有覆盖，不是单资产 carry。

换成人话：
- 它已经不像“论文里好看，但实际挂到 paper runner 会稀到没有存在感”的东西；
- 更像一个可以先挂到 `breakout-short` family 上做 paper overlay 的 shared gate 候选。

## 4. authoritative judgment
### 当前层级
- **`Rank 151 = P3 / admitted to Paper launch queue`**

### 本轮建议动作
- 不再继续补第三条 family
- 不再重复 split / monthly / replication 近义验证
- 直接把后续 `Next 3 bot3 runs` 切到：
  1. `build runner`
  2. `attach scheduler + status page`
  3. `verify + handoff`

### 保留的诚实边界
- 这轮 admission bar 只在默认承载 family `breakout-short` 上裁决；
- 它证明的是“值得进 launch queue”，不是“runner 已可直接交付”；
- 真正接线前仍需补最小 operating spec（输入、输出、ledger row、status json、refresh cadence）。

## 5. 简短 scorecard
- `shared_gate_evidence = 3/3`
- `recent_slice_honesty = 3/3`
- `trade_density = 3/3`
- `runner_feasibility = 3/3`
- `recommended_action = promote_P3_launch_queue`
- `why_now = 顶板 Run 1 要求用一个贴近 Paper launch 的最小检查回答 Rank 151 是否值得进 P3 / launch queue。`
- `main_weakness = 当前 admission bar 只在 breakout-short 承载 family 上做 recent-slice / density 裁决；runner 真正接线前仍要补最小 operating spec。`

## 6. 对 desk 的直接影响
1. `Paper / 待开启自动运行` 不再是 `empty`，应收进 `Rank 151`。
2. `Rank 151` 不再占默认 `Scout primary`；它已经完成从 `Scout` 到 `Paper launch queue` 的层级跃迁。
3. desk 的默认后续动作应从研究推进切到 paper 落地三步：`runner -> scheduler/status -> verify/handoff`。

## 7. 一句话结论
`Rank 151` 这轮做的不是又一条研究彩带，而是最关键的 launch admission 决策：在默认承载 family `breakout-short` 上，`30 / 60 / 90d` recent slices 全部同时保留正 uplift、正 band-pass 均值、足够 trade density 与 `3/3` 资产覆盖，因此它已经足够从 **`P2 / pre-paper candidate`** 升到 **`P3 / Paper launch queue`**；下一轮应直接进入 `build runner`。
