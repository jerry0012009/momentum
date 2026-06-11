# 2026-03-23 13:58 UTC · Rank 150 / EMA family honest gate

- 路径判断：`Scout`
- 认领动作：`Next 3 bot3 runs / Run 1 = Rank 150 的单 family A/B/C honest gate`
- 本轮只推进：
  1. **主点**：把 `Rank 150 / DFA Hurst persistence gate` 落到 **`EMA / PSAR raw alpha continuation` 单 family**；
  2. **紧邻子点**：给出最小可审计 scorecard，明确它现在更像 `keep_P1` 还是更接近 `P2`。

## 1) 为什么本轮走这条
- `Paper / 待开启自动运行` 仍是 `empty`，所以不走 `Paper launch`。
- 当前没有 `runner stale / error / refresh 失步` 之类 interrupt 证据，所以不走 `Interrupt`。
- 顶板 `Next 3` 已明确把 `Run 1` 升级成：**`Rank 150` 用已完成的 `window=192` calibration，落到 1 条 desk family 做 baseline vs high-persistence allow vs low-persistence veto。**
- 三个候选 family 里，`EMA / PSAR` 是当前最短路径：
  - 已有清晰的 desk family 骨架；
  - 规则和执行口径最容易冻结成 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`；
  - 如果这条都看不到 uplift，继续把 shared gate 往前讲就容易变成 generic proxy 故事。

## 2) 本轮实际做了什么
新建并执行：
- `scripts/build_rank150_ema_family_honest_gate.py`

产出：
- `reports/artifacts/scout_rank150_ema_family_honest_gate_15m/pooled_summary.csv`
- `reports/artifacts/scout_rank150_ema_family_honest_gate_15m/asset_summary.csv`
- `reports/artifacts/scout_rank150_ema_family_honest_gate_15m/bucket_mix_primary_cost.csv`
- `reports/artifacts/scout_rank150_ema_family_honest_gate_15m/family_honest_gate_meta.json`
- `reports/site/factors/scout_rank150_ema_family_honest_gate_15m/report.html`
- `reports/site/reading/repo_scout/rank150_ema_family_honest_gate.html`

## 3) 固定口径
- 数据：`BTC/ETH/SOL 120d 15m cache`
- Family：`EMA / PSAR raw alpha continuation`
- Gate：复用上一轮本地 calibration 的 `DFA window=192`
  - `low < 1.4319`
  - `high > 1.5423`
- A/B/C：
  - `A = baseline`
  - `B = high_only`（只有 `high-persistence` 放行）
  - `C = low_veto_mid_half`（`low=0x / mid=0.5x / high=1x`）
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 成本：主看 `6bps/side`，并补 `10/15bps` 敏感性。

## 4) 主结果（6bps/side）
### pooled scorecard
- `baseline`
  - `trades = 100`
  - `retention = 95.2%`
  - `mean_net_ret ≈ -0.1243% / trade`
  - `total_net_return ≈ -12.43%`
  - `early_fail_rate ≈ 53.0%`
- `high_only`
  - `trades = 33`
  - `retention = 31.1%`
  - `mean_net_ret ≈ +0.0779% / trade`
  - `total_net_return ≈ +2.57%`
  - `early_fail_rate ≈ 54.5%`
- `low_veto_mid_half`
  - `trades = 55`
  - `retention = 51.9%`
  - `mean_net_ret ≈ +0.0283% / trade`
  - `total_net_return ≈ +1.56%`
  - `early_fail_rate ≈ 54.5%`

### by asset（6bps/side）
- `BTC`
  - baseline 近乎持平略负；`high_only` 与 `low_veto_mid_half` 仍小负。
- `ETH`
  - baseline 明显最差；`high_only` 显著收敛亏损，但还没转正；`low_veto_mid_half` 也仍负。
- `SOL`
  - 三臂里 gate 版本都优于 baseline；其中 `high_only` 的单笔收益最高，`low_veto_mid_half` 的总收益更高。

## 5) 这轮最值钱的读法
1. **Rank 150 第一次从 generic regime story 变成了 desk-family honest evidence。**
   不是只说 “high persistence 可能更好”，而是已经在 `EMA / PSAR` 单 lane 上看到：
   - baseline 成本后为负；
   - `high_only` 与 `low_veto_mid_half` 都能把 pooled 结果拉回正值。
2. **最干净的主读法是 `B = high_only`。**
   - 它最像真正的 allow gate：不是靠复杂加权，而是直接把非 high-persistence 区间砍掉；
   - 代价也很清楚：retention 只剩约 `31%`，说明它更像“少做，但挑更像趋势的段”。
3. **`C = low_veto_mid_half` 也有信息，但更像 sizing overlay，而不是最强 verdict。**
   - 收益转正，但 uplift 斜率弱于 `high_only`；
   - 若下一轮只给 1 个最小检查，优先继续围绕 `high_only` 做稳定性/第二 family 复核，而不是先打磨 mid bucket 权重。
4. **这还不够直接升 `P2`。**
   - `positive_asset_ratio` 仍只有 `1/3`；
   - `BTC/ETH` 还没被真正“救活”；
   - `10/15bps` 下优势明显收缩，说明当前证据更像 **family-level keep_P1 强化**，还不是 desk-ready promotion。

## 6) 简短 verdict / scorecard
- `path`: `Scout`
- `main_point`: `Rank 150 / EMA family honest gate`
- `adjacent_subpoint`: `把 shared gate 压成 family-specific pooled/asset scorecard`
- `result`: **`keep_P1 but stronger`**
- `why_now`: `顶板 Run 1 已明确要求从 calibration 前推到单 family A/B/C honest gate；EMA / PSAR 是最短可验证落点。`
- `evidence_gain`: `从 generic local calibration -> EMA 单 family 真实 uplift`
- `main_weakness`: `uplift 仍集中在 SOL，BTC/ETH 不够整齐；高成本下优势快速收缩。`
- `next_best_step`: `若继续给 Rank 150 一轮，优先做 1 个 truly verdict-changing 的轻量检查：时间稳定性 或 第二 family（breakout-short / fib retest 二选一）复核，默认先别再调 Hurst 阈值。`

## 7) 对 desk board 的含义
本轮最重要的不是“Rank 150 变成 paper candidate”，而是：

> **它已经不再只是 source-intake / calibration reserve，而是拿到了 `EMA / PSAR` 单 family 的诚实 gate 证据。**

更准确的当前定位：
- `Rank 150 = P1 / keep_P1 stronger / family-level evidence gained / next = 轻量稳定性或第二 family 复核`
- 还**不够**直接写成 `promote_P2`，但比上一轮更接近那一步。
