# 2026-03-17 14:22 UTC · Rank 30 clean replication hard park

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- `Run 1 / Paper Seat` 先做守门：`EMA` 当前仍是 `waiting_not_due`，没有新的 `due-now / overdue` lane。
- 因此按板子回退到 `Scout Seat`，并先比较当前 active Scout 的边际价值：
  - `Rank 17 / Rank 29 / Rank 2` 都是 `P3`，日常 refresh 已交给专属 cron + 状态页托管，当前没有新的真实 `append/review need`；
  - `Rank 7 / 25 / 26 / 33 / 35` 等近期已完成允许的最小检查并给出 verdict，不应继续续命；
  - `Rank 30` 是当前最接近“1 轮内就能从 intake 走到 hard verdict”的 repo-based 15m crypto 候选，所以本轮主资源给它。

## 为什么这轮选这个
`Rank 30 trendln paired-channel breach / corridor breakout gate` 在上一轮只完成了 source intake，还停在 `admit_to_clean_replication_queue`。按当前 `TRADING DESK BOARD`，这正好属于最该优先消化的一种：
- 不追新 bar；
- 不继续磨 P3 近义 wiring；
- 直接把 fresh intake 往前推一格，尽快拿到 `park / paper candidate` 这种硬结论。

## 做了什么改动
1. 先执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 结果：`EMA` 仍无 `due-now / overdue` lane；最靠前的是美股约 `5.6h` 后、Crypto 约 `9.6h` 后。
   - 这个命令因 `--require-due` 在 waiting-window 下按设计返回非零并结束，本轮据此切到 `Scout Seat`，不是异常失败。
2. 执行 `python3 scripts/build_rank30_trendln_channel_clean_replication.py`
   - 产出最小 clean replication artifact：
     - `reports/artifacts/scout_rank30_trendln_channel_15m/overall_summary.csv`
     - `reports/artifacts/scout_rank30_trendln_channel_15m/asset_summary.csv`
     - `reports/artifacts/scout_rank30_trendln_channel_15m/trades_primary_6bps.csv`
     - `reports/artifacts/scout_rank30_trendln_channel_15m/width_stability_summary.csv`
   - 产出 reader-facing 页面：
     - `reports/site/factors/scout_rank30_trendln_channel_15m/report.html`
     - `reports/site/factors/scout_rank30_trendln_channel_15m/rank30_trendln_channel_clean_replication.html`
3. 把 `docs/TODO.md` 顶部 `Run 2 -> 2m2` 从旧的 `admit_to_clean_replication_queue` 同步成这轮的 hard verdict：`park / evidence pool`。
   - 这一步脚本没有把顶部 `2m2` 的旧 intake 文案一起替掉，所以我随后做了 1 次最小手工同步，避免板子和 reader-facing 页面读法不一致。

## 关键证据 / hard verdict
这轮只比较两档最小规则：
- `raw_corridor_breach`
- `breach_plus_reclaim_hold`

执行口径固定：
- 复用 `BTC/ETH/SOL 120d 15m` cache；
- 只用当时可见的因果确认 pivot 拟合成对通道；
- `next-bar open` 入场；
- 持有 `8` 根 `15m` bar；
- 若触发后 `4` 根内重新回到错误一侧边界内，记为假突破。

主变体 `breach_plus_reclaim_hold` 在 `6bps/side` 下的结果：
- 跨资产 `mean_total_return ≈ -7.33%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 57.3`
- `mean_false_break_ratio ≈ 82.39%`
- `mean_width_cv ≈ 0.137`

更直白地说：
- 通道宽度稳定性本身不算最差；
- 但真正致命的是 **假突破率太高，成本后回报三腿全负**；
- `breach_plus_reclaim_hold` 比 `raw_corridor_breach` 少亏一点，但没有接近 admission 线。

因此这轮 hard verdict 是：**`Rank 30 -> park / evidence pool`**。

## 最小验证
已执行 / 抽查：
1. `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. `python3 scripts/build_rank30_trendln_channel_clean_replication.py`
3. 抽查 `reports/site/factors/scout_rank30_trendln_channel_15m/report.html`
4. 抽查 `reports/artifacts/scout_rank30_trendln_channel_15m/overall_summary.csv`
5. 抽查 `docs/TODO.md` 的 `Rank 30` 总表条目与 `Next 3 bot3 runs -> 2m2`

## 风险 / 边界
- 本轮没有继续扩成完整 `Light Stability Pack`，因为最小 clean replication 已经给出足够硬的 `park` 证据；继续扩只会增加低边际工作。
- 当前 repo 仍有大量与本轮无关的脏文件 / 未跟踪文件，本轮不做混提。
- `Rank 30` 不是“永远判死”，但在当前预算下已经不配继续占默认 Scout 主资源；除非 bot2 明确要求重开，或后续出现新的 genuinely verdict-changing 证据。

## 下一步建议
1. 下一轮若 `EMA` 仍处于 `waiting_not_due`，继续按 `Scout Seat` 规则比较剩余候选的边际价值，而不是回头继续磨 `Rank 30`。
2. `Rank 30` 默认回到 evidence pool；若要重开，必须先说明为什么这次会改变 `高假突破率 + 成本后全负` 的核心读法。
3. 一旦 `EMA` 到点，优先切回 `Paper Seat`，不要因为 scout 线索继续拖延 paper refresh。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件与未跟踪文件，安全 selective commit 成本过高，避免混提。
