# 2026-03-20 13:40 UTC · Rank 122 时间稳定性检查 → 升到 P3 narrow paper pilot

## 本轮一句话
先按 desk 规则确认 `EMA = waiting_not_due`，随后只认领 **`Rank 122 / ATR compression + ROC ignition short re-arm gate`** 的 **1 个 truly verdict-changing 最小时间稳定性检查**；结果没有出现 decisive fail，因此把它从 **`P2 / paper candidate`** 推进到 **`P3 / narrow paper pilot approved`**，但限定为 **`strict-only / short-side re-arm / paper-only / recent-month red-watch`**。

## 先检查了什么
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 约为：`美股 1d+1wk -> 6.3h`、`Crypto 1d+1wk -> 10.3h`、`创业板ETF 1d -> 65.3h`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 当前 authoritative `Next 3`：
    1. `Run 1 = EMA due-check first`
    2. `Run 2 = Rank 122 最小时间稳定性检查`
    3. `Run 3 = 若不过度爆雷，则给 P3 / park + 最小 paper 接线`
- repo 状态仍很脏；本轮只改 `Rank 122` 相关文件，不混提。

## 本轮主点
### Rank 122 最小时间稳定性检查
严格复用上一轮 clean-room 的同一份 `trade_log` 与执行口径：
- `signal 当根及之前数据`
- `next-bar open`
- `no-overlap`
- `hold 4 bars`

只比较：
- `baseline_short`
- `strict_short_rearm`

并按信号时间切成：
- `front_half`
- `back_half`

## 核心结果
### 6bps / side
- `front_half`
  - `baseline_short ≈ -0.78 bps`
  - `strict_short_rearm ≈ +26.09 bps`
- `back_half`
  - `baseline_short ≈ -14.50 bps`
  - `strict_short_rearm ≈ +17.24 bps`

### 10bps / side（strict）
- `front_half ≈ +18.07 bps`
- `back_half ≈ +9.22 bps`

### 需要如实保留的红灯
- `strict` trade retention 仍只有 **`29 / 890 ≈ 3.26%`**
- 月度快照里 `2026-02 / 2026-03` 已出现 **recent-month red-watch**（strict 月均值转弱 / 接近零）
- 分资产看，真正把 aggregate 扛住的主要仍是 `SOL`；`BTC/ETH` 的 back-half 仍偏弱

## authoritative verdict
**`Rank 122 = promote to P3 / narrow paper pilot approved`**

但限定词必须写全：
- `strict-only`
- `short-side re-arm`
- `paper-only`
- `recent-month red-watch`

翻成人话：
- 这条线还没烂到该直接 `park`
- 但也绝不能被误写成 broad/shared gate
- 现在只配当一条低频、窄口径的 hosted paper lane 先跑着看
- `mild` 继续判负；`long/shared/live` 继续不允许

## 紧邻子点：最小 P3 接线
已补：
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/narrow_paper_monitoring_board.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/narrow_paper_seed_packet.csv`

当前 operator 边界：
- 只允许后续继续做 `monitoring / refresh / weekly review / status sync`
- 若没有新的 due-now / status-changing event，下一轮就应回 fresh intake，而不是继续磨 Rank 122 文案

## 产物
### 新脚本
- `scripts/build_rank122_time_stability_check.py`

### artifacts
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/time_stability_summary.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/time_stability_asset_summary.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/time_stability_monthly_snapshot.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/narrow_paper_monitoring_board.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/narrow_paper_seed_packet.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/summary.json`（补写 time stability verdict）

### reader-facing
- `reports/site/factors/scout_rank122_atr_roc_short_rearm_15m/time_stability_check.html`
- `reports/site/factors/scout_rank122_atr_roc_short_rearm_15m/report.html`
- `reports/site/reading/repo_scout/rank122_atr_roc_short_rearm_time_stability.html`

## 对 desk board 的写回
已同步到 `docs/TODO.md`：
- `Rank 122` 从 `P2 / paper candidate` 升到 **`P3 / narrow paper pilot approved`**
- `Next 3` 改为：
  1. `Run 1 = EMA due-check first`
  2. `Run 2 = Rank 122 只允许做 P3 continuity 或 1 个真正会改变 paper verdict 的最小检查`
  3. `Run 3 = 若 Rank 122 暂无 due-now / status-changing event，则回 fresh intake`

## 验证
- 已执行：`python3 scripts/build_rank122_time_stability_check.py`
- 已生成并核对：
  - `reports/site/factors/scout_rank122_atr_roc_short_rearm_15m/time_stability_check.html`
  - `reports/site/reading/repo_scout/rank122_atr_roc_short_rearm_time_stability.html`
  - `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/narrow_paper_monitoring_board.csv`

## 风险 / 保留意见
- 这是 **strict-only** 的窄 lane，不是 broad alpha
- 最近月份转弱已经出现，后续 hosted paper review 应优先盯 recent-month red-watch
- 如果后续 review 显示 uplift 继续主要依赖 `SOL` 单腿，默认应优先考虑压回 `park`，而不是继续扩 scope

## 提交情况
- 未提交
- 原因：repo 有大量与本轮无关的脏文件；本轮只做 selective write-back
