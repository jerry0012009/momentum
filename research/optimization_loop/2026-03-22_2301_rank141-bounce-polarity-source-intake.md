# 2026-03-22 23:01 UTC · Rank 141 / bounce polarity not-shared gate

## 本轮按顶板顺序执行

### Run 1 · EMA due-check first
已实际运行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果：`waiting_not_due`，当前没有 `due-now / overdue` lane。
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 状态：`due_soon`
- 距下次到点：约 `57 分钟`

结论：本轮不得伪造 paper refresh，按顶板立即切下一允许动作。

### Run 2 · Hosted P3 continuity（只认 status-changing event）
已核对：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`

结果：当前没有值得抢 bot3 主资源位的明确 `status-changing event`。
- manual narrow paper 最新 refresh：`2026-03-22T22:38:48Z`
- `new_closed_trades_appended=0`
- Rank 139 独立 runner 仍在刷新（监控板更新时间 `2026-03-22 22:58 UTC`）

结论：Run 2 合法跳过，不做近义 health-check 重复劳动。

### Run 3 · 只选 1 个 active Scout / fresh intake reserve
这轮**不继续追 Rank 140**。
原因：最近两轮 bot3 主资源位连续围绕 Rank 140 展开，但没有层级变化，也没有新的 decisive evidence；按顶板规则，当前必须切离该 P1 主点，转向下一条 active Scout / fresh intake reserve。

本轮认领：**fresh intake reserve → `Rank 141 / bounce polarity not-shared gate`**
- 来源：`research/quant_digests/2026-03-22_2258_bounce-polarity-not-shared-gate.md`
- 主题：回踩后那根 bounce candle 是否必须是同方向实体（long 收阳 / short 收阴）

## 本轮硬结论
**`Rank 141 = park / not_shared / do_not_admit_to_clean_replication_queue`**

### 为什么直接 park
本轮已有最小 proxy 证据足够说明：
1. `same-direction body` 不适合升成 `Fib retest_hold / EMA continuation / breakout-short follow-up` 的 shared hard gate；
2. 它更像更晚、更激进的追单，而不是更诚实的确认；
3. long 侧最明显地变差，short 侧也没有 shared uplift；
4. 当前更像应被写成“不要默认照搬的 repo 小审美”，而不是下一轮继续消耗 clean replication 预算的候选。

### 关键证据（来自同一篇 digest）
样本：`BTC/ETH/SOL`，Binance Spot `15m`，最近 `120d`，事件数 `n=1126`

- `same_body=False`：`continue 40.7% / fail 57.7% / timeout 1.7%`
- `same_body=True`：`continue 35.4% / fail 63.2% / timeout 1.4%`

分方向：
- `long, same_body=False`：`continue 43.1% / fail 55.1%`
- `long, same_body=True`：`continue 32.7% / fail 65.1%`
- `short, same_body=False`：`continue 38.3% / fail 60.2%`
- `short, same_body=True`：`continue 37.9% / fail 61.5%`

### desk 口径（本轮只留 1 个主点 + 1 个紧邻子点）
- **主点**：`Rank 141 / bounce polarity not-shared gate` 直接压回 `P0 / park`
- **紧邻子点**：若后续真要重开，只配把确认改写成 `close reclaim + 2-close persistence` 的对照臂，而不是继续使用 `same-direction body` 审美 gate

## 对下一轮的明确含义
若下一轮 EMA 仍 `waiting_not_due`，Scout 主资源应继续留在**非 Rank 140** 的 active Scout / fresh intake reserve，**不要再回到 bounce polarity 这条线**。它当前已经足够给出 hard verdict，不值得继续占默认预算。

## 本轮交付
- 日志：`research/optimization_loop/2026-03-22_2301_rank141-bounce-polarity-source-intake.md`
- 网页落点：`reports/site/reading/repo_scout/rank141_bounce_polarity_not_shared_source_intake.html`
