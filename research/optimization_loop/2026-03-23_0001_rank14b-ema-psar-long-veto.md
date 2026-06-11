# 2026-03-23 00:01 UTC · Rank 14b / EMA-PSAR long 单臂 clean replication

## 本轮按顶板顺序执行

### Run 1 · EMA due-check first
已实际运行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果：`waiting_not_due`
- 当前没有 `due-now / overdue` lane
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 状态：`due_soon`
- 到点读数仍显示约 `1 分钟`，说明当前仍未拿到可落账的 completed bar

结论：按顶板纪律，本轮**不得伪造 EMA refresh**，立刻切去 Scout Seat。

### Run 2 · Scout Seat 主点
本轮只保留 **1 个主点**：`Rank 14b / directional-breadth-coherence long-side continuation veto`

承接上两轮冻结口径，本轮不并行打开 `Fib retest_hold`、不回头继续磨 `Rank 140 / 125 / 112 / 111`，只把 `Rank 14b` 落成 **EMA/PSAR continuation long 单臂 A/B**。

### Run 3 · 便宜但可能改变级别的小动作
本轮唯一紧邻子点：
- 只比较 `baseline_long` vs `low_breadth_veto_long`
- 阈值固定：`dir_breadth_1h <= 0.45` 时 **veto 新 long entry**
- 不加入 `half-size / short mirror / 第二阈值 / 第二条 base setup`

## 本轮实际实现
- 复用 `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/trade_log.csv` 中的 `ema_psar_long / raw_trigger` 交易日志
- 复用 `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/spot_cache/{BTC,ETH,SOL}USDT_120d_5m.csv` 计算 `dir_breadth_1h`
- 定义：对每个 long 信号时刻 `t`，取过去 `60m` 内 `BTC/ETH/SOL` 的 `5m` 收益；`dir_breadth_1h = mean(ret>0)`
- gate：`dir_breadth_1h <= 0.45` 直接 veto，否则按 baseline 保留

## 核心结果（EMA/PSAR long only）

### 成本 6 bps / side
- `baseline`：`N=104`，`mean_net = -16.36 bps`，`trade_retention = 100%`，`false_follow_ratio = 39.42%`
- `veto_long`：`N=62`，`mean_net = +3.80 bps`，`trade_retention = 59.62%`，`false_follow_ratio = 37.10%`

### 成本敏感性
- `10 bps / side`：`baseline = -24.35 bps` → `veto_long = -4.21 bps`
- `15 bps / side`：`baseline = -34.34 bps` → `veto_long = -14.21 bps`

### 分资产（6 bps / side）
- `BTC-USD`：`-12.44 bps` → `-8.32 bps`
- `ETH-USD`：`-53.39 bps` → `-51.36 bps`
- `SOL-USD`：`+16.85 bps` → `+78.75 bps`

## 这轮最诚实的 desk 读法
1. **`Rank 14b` 确实拿到了最小级别的 decisive evidence**：同样是 `EMA/PSAR long`，只加一刀 `low breadth veto`，就把 `6 bps / side` 的整体期望从负值拉到轻正。
2. 但它还**不够支持 promote**：
   - `trade_retention` 只有 `59.6%`，砍单不算轻；
   - 改善目前明显更偏 `SOL`，`ETH` 仍是硬拖累；
   - 到 `10/15 bps` 后仍是负值，只能算“减亏显著”，还不是足够稳的 shared gate。
3. 因此本轮最合理状态不是 `park`，也不是 `promote_P2`，而是：
   - **`Rank 14b = keep_P1 / evidence strengthened / no promote yet`**
   - 下一轮若继续给预算，应优先回答：`ETH 拖累是否只是样本 pocket，还是说明这条 gate 只适合更窄 universe / 更严格 setup 版本`。

## 对下一轮的最短提醒
- 若 EMA 真正到点：先做真实 `Run 1` refresh。
- 若 EMA 仍未到点：`Rank 14b` 已经用掉 1 次最小 clean-replication 预算；下一轮不要继续扩成多 setup 并行，只允许 1 个更便宜的相邻验证（例如同一口径下看 `close_confirmed` 是否比 `raw_trigger` 更诚实），否则就切下一 active Scout / fresh reserve。

## 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0001_rank14b-ema-psar-long-veto.md`
- 网页落点：`reports/site/reading/repo_scout/rank14b_ema_psar_long_veto_clean_replication.html`
