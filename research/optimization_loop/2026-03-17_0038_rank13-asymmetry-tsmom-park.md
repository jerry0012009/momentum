# 2026-03-17 00:38 UTC｜Scout Seat：Rank 13 partial-moment asymmetry TSMOM gate（park）

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 走：

- `Run 1 / Paper Seat`：上一轮 `EMA crypto 1d+1wk` 的 due-now 补账已经完成，当前重新回到 `waiting_not_due`，这轮不能继续在 paper 窗口里空转；
- `Run 2 / Scout Seat`：当前默认主资源位；
- `Run 3 / tiny-live plumbing`：只有在 `Scout Seat` 也没有合格动作时才回退。

本轮先比较 active Scout 候选的边际价值：

1. `Rank 2 combo_all`
   - 仍是 `narrow paper pilot approved`；
   - 但当前没有新的真实 `append/review need`，继续做大概率又会滑回近义 wiring。
2. `Rank 7 ~ Rank 12`
   - 都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；
   - 当前没有新的数据源 / 新 spec / bot2 重开指令，不该继续吃默认主资源。
3. 新鲜候选里，`Liu, Lu, Wang (2021)` 这条 `partial-moment asymmetry TSMOM gate`
   - 已有现成 digest，可直接写成清楚的 `trade on / trade off`；
   - 不再强调 breakout，而是更像动量风险门 / continuation honesty 检查；
   - 能完全复用现有 `Binance 120d 15m` cache，在一轮内完成 `clean replication + Light Stability Pack + hard verdict`。

因此这轮主点定为：**把 partial-moment asymmetry gate 从 paper digest 直接推进到最小 clean replication，并在同一轮给出 `paper candidate / park` verdict。**

## 本轮主点（1 个）
- 新增脚本：`scripts/build_asymmetry_tail_tsmom_clean_replication.py`
- 用现有 `BTC/ETH/SOL` 的 `120d / 15m` cache，把下面几档最小 clean-room 规则一次跑完：
  - `baseline_sign_mom`
  - `pm_guard_090`
  - `pm_guard_100`
  - `pm_guard_110`
  - `pm_guard_125`
- clean-room 读法：
  - `mom_16 = close / close.shift(16) - 1`
  - 最近 `32` 根 15m bar 计算 `up_pm / down_pm`（正负收益平方均值）
  - 多头只有在 `down_pm / up_pm < threshold` 时才允许继续做多
  - 空头只有在 `up_pm / down_pm < threshold` 时才允许继续做空
  - 持仓按 bar 级 momentum sign / guard 切换，成本按持仓切换收 `6/10/15/20 bps/side`

## 紧邻子点（1 个）
- 最小回写 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 新增 `Rank 13 partial-moment asymmetry TSMOM gate`
  - 明确它已完成 `clean replication + Light Stability Pack`
  - 并把当前 hard verdict 回写为 `park / evidence pool`

## 产物 / deployable artifact
### 新脚本
- `scripts/build_asymmetry_tail_tsmom_clean_replication.py`

### 新 artifacts
- `reports/artifacts/scout_asymmetry_tsmom_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/bar_level_simulation.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/nav_series.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/asset_summary.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/overall_summary.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/primary_asset_summary.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/time_stability_drycheck.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/time_stability_detail.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/parameter_stability_drycheck.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/parameter_stability_detail.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/cross_asset_stability_drycheck.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/cost_trade_stability_drycheck.csv`
- `reports/artifacts/scout_asymmetry_tsmom_15m/clean_replication_meta.csv`

### 网页可见落点
- `reports/site/factors/scout_asymmetry_tsmom_15m/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`（Control Tower 会同步）

## 最小验证
已执行：

1. `python3 scripts/build_asymmetry_tail_tsmom_clean_replication.py`
2. 读取并核对：
   - `clean_replication_meta.csv`
   - `overall_summary.csv`
   - `primary_asset_summary.csv`
   - 四张 `Light Stability Pack` gate 表
3. 确认 `docs/TODO.md` 已出现 `Rank 13` 的 board 回写

执行结果：
- 脚本成功输出：`[ok] asymmetry tail tsmom clean replication generated`

## 硬结论（hard verdict）
### Primary variant
- `winner / primary variant`：`pm_guard_100`
- `primary cost`：`6 bps / side`

### 关键数值
来自 `reports/artifacts/scout_asymmetry_tsmom_15m/clean_replication_meta.csv` 与相关 summary：

- `mean_total_return ≈ -71.90%`
- `positive_asset_ratio = 0/3`
- `mean_trade_events ≈ 2027`
- `mean_max_drawdown ≈ -75.70%`
- 三个资产分别约：
  - `BTC ≈ -67.10%`
  - `ETH ≈ -76.50%`
  - `SOL ≈ -72.09%`

对比看，`partial-moment` guard 虽然比 `baseline_sign_mom`（约 `-78.35%`）略少亏，但只是“没那么糟”，不是“已经像样”。

## Light Stability Pack
### 1) 时间稳定性
- `positive_bucket_floor = fail`（`0/3 positive buckets`）
- `worst_bucket_watch = watch`（最差 bucket 约 `-45.23%`）

### 2) 参数稳定性
- `neighbor_positive_floor = fail`（`0/5 positive configs`）
- `trade_density_floor = pass`（不是因为样本太薄才负）

### 3) 跨标的稳定性
- `positive_asset_floor = fail`（`0/3 positive assets`）
- `worst_asset_watch = watch`（最差资产约 `-76.50%`）

### 4) 成本 / 交易数稳定性
- `positive_cost_levels = fail`（`0/4 positive cost levels`）
- `worst_cost_watch = watch`（20bps 下约 `-98.62%`）
- `trade_floor = pass`（也不是因为过滤后几乎没交易）

## 这轮最诚实的 desk 读法
- 这条线**不是**一个接近 `paper candidate` 的快筛 winner；
- 更像一个说明“**单靠 partial-moment asymmetry 风险门，不足以救活 15m crypto sign-momentum**”的反例证据；
- 因此当前最诚实 verdict 是：
  - **`Rank 13 partial-moment asymmetry TSMOM gate` → `park / evidence pool`**
  - 当前只适合作为后续 `EMA / TSMOM risk gate` 的参考证据，**不进入 `paper candidate pool`**。

## 对主线的意义
- 这轮没有改变 `Paper Seat = EMA` 的席位判断；
- 也没有给 `Live Seat` 送出新的 promoted candidate；
- 但它确实把一个 paper-based fast-lane 候选在一轮内完成了闭环：
  - `source intake -> clean replication -> Light Stability Pack -> park`
- 这比继续在 `Rank 2` 上补近义 wiring 更符合当前 board 的资源分配规则。

## 风险 / 边界
1. 这条 clean-room 规则是论文思想迁移，不是 faithful 复刻原论文日频商品期货实现；
2. 当前实现用的是最简单的 bar-level `sign(momentum)` 持仓切换口径，因此结论应解读成：
   - “这层 asymmetry gate 单独拿出来，救不活 15m crypto sign-momentum”；
   - 不是“partial moments 在任何 system overlay 上都永远没用”。
3. 如果后续要重开，最合理的方向应是把它当作 **risk / environment gate** 嵌进已有方向层，而不是继续把它当独立 candidate 打磨。

## Git / 提交
- 未提交。
- 原因：工作区里存在大量与本轮无关的脏文件与未跟踪文件，不适合安全 selective commit。

## 下一轮建议
- 若 `EMA` 仍是 `waiting_not_due`：继续 `Scout Seat`，但默认应再换一条新的 paper / repo based 5m/15m crypto 候选，而不是重开 `Rank 13`。
- `Rank 2` 仍只在出现真实 `append/review need` 或会改变 paper verdict 的最小检查时再继续认领。
- `Rank 13` 当前默认不再占主资源，除非 bot2 明确要求把它当动量风险门反例重看。
