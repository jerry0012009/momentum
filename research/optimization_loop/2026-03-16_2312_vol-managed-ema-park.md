# 2026-03-16 23:12 UTC — volatility-managed EMA / ATR sizing overlay park

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查：`Paper Seat = EMA` 当前仍是 `waiting_not_due / due_soon`，所以本轮不能在 `Run 1` 空转。
- 再比较 active Scout 候选的边际价值：
  - `Rank 2 combo_all` 已是 `narrow paper pilot approved`，当前没有真实 `append/review` need；
  - `Rank 7 / 8 / 9` 都已完成 `clean replication + Light Stability Pack` 并压回 `park`；
  - 因此本轮最诚实的主资源动作，是继续 `Run 2 / Scout Fast Lane`，但换成一条**新的 paper-based 15m crypto 候选**，而不是继续补旧候选 wiring。
- 这次选 `volatility-managed EMA / ATR sizing overlay`，原因不是想发明新 alpha，而是它离当前 desk 更近：如果它真的能改善风险收益，就可能成为 `EMA` 方向层的可接线风险层；如果不能，就应尽快给出 hard verdict，而不是漂成长期研究态。

## 本轮主点
- 主点：完成 `volatility-managed EMA / ATR sizing overlay` 的最小 `source intake -> clean replication -> Light Stability Pack`。
- 紧邻子点：把 `TODO` 顶部战板同步成最新 hard verdict，避免下一轮继续把它当 active fast-lane 候选。

## 做了什么
### 1) 新增 clean replication 脚本
新增：
- `scripts/build_vol_managed_ema_clean_replication.py`

脚本口径：
- 样本：`Binance 120d / 15m / BTC-USD + ETH-USD + SOL-USD`
- 信号：`trade on = EMA20 > EMA50`；`trade off = EMA20 <= EMA50`
- 仓位层：`position_size = clip(ATR_ref / ATR14_t, min, max)`
- 变体：
  - `baseline_100`
  - `atr_clip_075_125`
  - `atr_clip_050_150`
  - `atr_clip_025_175`
- 执行：`next-bar position lag`，并在仓位变化时扣 `6/10/15/20 bps per side` 成本
- 稳定性包：
  - 时间稳定性
  - 参数稳定性（EMA 邻域）
  - 跨标的稳定性
  - 成本 / 交易数稳定性

### 2) 生成 reader-facing artifact
落地产物：
- `reports/artifacts/scout_vol_managed_ema_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/clean_replication_meta.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/variant_aggregate.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/asset_summary.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/time_stability_drycheck.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/parameter_stability_drycheck.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/parameter_neighbor_grid.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/cross_asset_stability_drycheck.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/cost_trade_stability_drycheck.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/bar_level_summary.csv`
- `reports/artifacts/scout_vol_managed_ema_15m/nav_paths.csv`
- `reports/site/factors/scout_vol_managed_ema_15m/report.html`

### 3) 一个最小工程修补
- 首次运行后，`pandas` 对 `groupby(bucket)` 给了 `FutureWarning`；虽然不影响结果，但我顺手把 `observed=False` 写死，避免下轮重复噪音。
- 然后重跑脚本，确认 artifact 与网页页签一致更新。

### 4) 同步 desk board
最小更新：
- `docs/TODO.md`
  - 新增 `Rank 10 volatility-managed EMA / ATR sizing overlay`，状态直接写成 **`park / evidence pool`**；
  - 顶部当前窗口排班同步成：`Rank 7 / 8 / 9 / 10` 都不再是 active fast-lane 候选；
  - `Run 2` 具体顺序里补了一条 `2d`，避免下轮继续把这条线误当成默认主资源位。

## 最小验证
已执行并通过：
1. `python3 /root/clawd/jerry/momentum/scripts/build_vol_managed_ema_clean_replication.py`
2. 修补 `groupby(..., observed=False)` 后再次执行：
   `python3 /root/clawd/jerry/momentum/scripts/build_vol_managed_ema_clean_replication.py`

关键验证读数：
- `baseline_100 @ 6bps/side`：
  - `mean_total_return ≈ -15.66%`
  - `mean_max_drawdown ≈ -31.01%`
  - `positive_asset_ratio = 0/3`
- `atr_clip_050_150 @ 6bps/side`（primary variant）：
  - `mean_total_return ≈ -26.21%`
  - `mean_max_drawdown ≈ -35.03%`
  - `positive_asset_ratio = 0/3`
  - `mean_trade_events ≈ 3982`
  - `mean_turnover ≈ 378.37`
- 其它 sizing 变体也都没有优于基线：
  - `atr_clip_075_125 @ 6bps ≈ -21.30%`
  - `atr_clip_025_175 @ 6bps ≈ -28.42%`

## Light Stability Pack
### 1) 时间稳定性
- `positive_bucket_floor`：**fail**（`0/3 positive buckets`）
- `bucket_trade_floor`：pass
- `worst_bucket_watch`：watch

### 2) 参数稳定性
- `neighbor_positive_floor`：**fail**（`0/5 positive configs`）
- `neighbor_trade_floor`：pass
- `worst_neighbor_watch`：watch

### 3) 跨标的稳定性
- `positive_asset_floor`：**fail**（`0/3 assets positive`）
- `min_trade_floor`：pass
- `worst_asset_watch`：watch

### 4) 成本 / 交易数稳定性
- `cost_survival_floor`：**fail**（`0/4 cost levels positive`）
- `trade_count_floor`：pass（不是样本太稀）
- `worst_cost_watch`：watch

## 硬结论（hard verdict）
- **`Rank 10 volatility-managed EMA / ATR sizing overlay` 当前应读作：`park / evidence pool`。**
- 更诚实的说法不是“波动管理可能有点帮助，只差后续微调”，而是：
  - 在这套 `15m crypto` 最小 clean replication 上，`ATR_ref / ATR14` 的 clipping 缩放没有把 `EMA20 > EMA50` 的方向层救活；
  - 不仅收益没有改善，连 `max_drawdown` 也比固定名义仓位更差；
  - 更窄或更宽的 sizing clip 邻域也都没有出现能改变 desk judgment 的正 pocket。
- 因此这条线当前最多只算**风险层反例证据**，不进入 `paper candidate pool`，也不应抢 `Live Seat`。

## 对 desk 主线的意义
- 这轮真正减少的是一个“看起来离 EMA 很近，所以容易被继续补”的假活跃项：
  - 现在 `Rank 7 / 8 / 9 / 10` 都已经是明确 `park / evidence pool`；
  - `Rank 2` 继续保留，但只在真实 `append/review` need 时再认领；
  - 所以下一轮如果 `EMA` 还在 `waiting_not_due`，更诚实的默认动作仍是**新的 paper / repo based 5m / 15m crypto intake**，而不是继续给旧候选补近义 wiring。

## 风险 / 边界
- 这仍是 fast-lane clean replication，不是更长窗口、更多资产、真实 funding/slippage、或更复杂 risk budget 的最终裁决；
- 但按当前 desk admission 规则，这已经足够给出 **`park`**，没必要再停在“也许只是 clip 参数没调好”的研究态；
- 这轮没有给 desk 新增 replacement winner，只是把一个离 `EMA` 很近、因此容易误判成“也许能接 paper”的候选及时压回证据池。

## 下一步建议
- 下一轮 `Run 2` 默认应继续转去**新的 `paper / repo based 5m / 15m crypto` source intake**；
- 不要继续把 `Rank 10` 当 active Scout 候选重跑，除非 bot2 明确要求把它当 `EMA risk-layer counterexample` 重看；
- 若 `EMA` 出现真实 `due-now / overdue` lane，则按规则临时切回 `Run 1` 做 paper continuation；否则优先新的 fresh intake，其次才是 `tiny-live plumbing`。

## 网页可见落点
- `reports/site/factors/scout_vol_managed_ema_15m/report.html`
- `docs/TODO.md`（及其站点镜像 / Control Tower）

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪产物，不适合安全 selective commit。
