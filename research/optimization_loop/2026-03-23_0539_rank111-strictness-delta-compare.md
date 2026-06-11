# 2026-03-23 05:39 UTC · Rank 111 strictness delta compare

## 本轮执行顺序（按顶板）

### 1) 先读 `TRADING DESK BOARD`
- `Paper / 待开启自动运行 = empty`
- 无 fresh intake reserve 已 guard-pass
- 因此本轮按顶板默认落到：
  - `Run 1` 无可开新 P3 runner
  - `Run 2` 做 `Rank 140` 的 shortest decisive compare
  - `Run 3` 只把剩余预算留给 `Rank 111` 这种 compare 价值更高的 evidence anchor

### 2) interrupt check
本轮只按顶板定义排查是否存在真实抢占事件：
- `EMA / PSAR raw alpha focus`：未见新的 `stale / error / refresh 失步 / red-watch`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b / Rank 139 / Rank 122`：顶板未给出新的 `ledger 爆雷 / open-position 异常 / blocking anomaly`

结论：**无 interrupt，继续按默认 compare 队列执行。**

---

## 本轮主点

主点仍是：**给 `Rank 140` 找最短 decisive compare，而不是回头重磨任何已 budget-used 的 P1。**

本轮只做一个紧邻子点：
> 把 `Rank 111` 已有两版 strict arm（`same_window_only` 与 `window_plus_timeout`）放到同一张轻量 compare 卡里，判断“放宽 strict 语义”到底有没有让 `Rank 140` 的 honesty 读法变得更可信。

这一步不新开 family，不重跑近义实验，也不碰已自跑 paper runner。

---

## 使用的现有 authoritative artifact

来源：
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`

本轮新增轻量 compare artifact：
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_strictness_delta_compare_20260323.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_strictness_delta_compare_20260323.json`

---

## 结果：Rank 111 的 strictness delta

### A) `same_window_only`
- `baseline_rows = 198`
- `kept:veto = 105:93`
- `PBO = 0.7143`
- `kept_minus_veto_mean_net_6bps = +5.987e-04`
- `verdict = guard_failed`

### B) `window_plus_timeout`
- `baseline_rows = 198`
- `kept:veto = 113:85`
- `PBO = 0.8000`
- `kept_minus_veto_mean_net_6bps = +1.709e-04`
- `verdict = guard_failed`

### delta（`window_plus_timeout - same_window_only`）
- `kept_rows = +8`
- `veto_rows = -8`
- `PBO = +0.0857`
- `kept_minus_veto_mean_net_6bps = -4.278e-04`

---

## 人话解释

这张 compare 卡给出的结论很直接：

1. **放宽 strict arm 没有让 Rank 111 变得更诚实。**
   - kept 行数变多了，说明规则更宽；
   - 但 `PBO` 从 `0.7143` 变成 `0.8000`，反而更差。

2. **区分度也没有变强。**
   - `same_window_only` 的 `kept-veto` 均值差更大；
   - 放宽到 `window_plus_timeout` 后，差值明显收窄。

3. **因此 Rank 111 最有用的身份仍是 evidence anchor，而不是可继续烧预算的独立 primary。**
   - 它能帮助说明 `Rank 140`：`split 可看` 不等于 `honesty 过关`；
   - 但它本身没有出现足以升层级的新证据。

---

## 对 desk 的最小结论

### 对 `Rank 111`
- 维持：`keep_P1 / evidence anchor / compare value > standalone budget`
- 不升级，不回到默认 primary

### 对 `Rank 140`
- 维持：`keep_P1 / active compare anchor / balance-aware freeze / not default primary`
- 本轮新增的 decisive point：
  - **当 Rank111 的 strict 语义放宽时，split 变宽但 honesty 反而更差；因此 `Rank 140` 不能靠“再放松 family strictness”来重新拿回默认主位。**

---

## 轻量 scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = weak_to_medium`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `looser_strict_arm_worsens_pbo`
- `kept_veto_gap_shrinks_after_relaxing_rule`
- `rank111_still_guard_failed`
- `no_new_p2_to_p3_signal`
- `rank140_cannot_recover_primary_status_via_looser_family_read`

### recommended_action
- **`keep_P1`**

### why_now
顶板已经明确：没有 fresh reserve 时，默认只允许做最短 decisive compare。本轮这张 compare 卡正好把 `Rank 111` 的剩余边际价值一次性收干净，避免后面又用“再换一个松一点的 strict 定义”重复烧预算。

### main_weakness
`Rank 111` 仍只有“拆分可读”的优点，没有给出可 deploy 的 OOS honesty；一旦 strict 语义放松，稳定性还会继续恶化。

---

## TODO writeback
本轮**不修改** `docs/TODO.md`。
原因：
- 没有新的层级变化；
- 顶板现有口径已经足够表达 `Rank 111 = compare 价值高于继续单独烧预算` 与 `Rank 140 = not default primary`。

## 交付
- 日志：`research/optimization_loop/2026-03-23_0539_rank111-strictness-delta-compare.md`
- 轻量 artifact：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank111_strictness_delta_compare_20260323.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank111_strictness_delta_compare_20260323.json`
