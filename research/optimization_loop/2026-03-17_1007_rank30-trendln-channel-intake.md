# 2026-03-17 10:07 UTC · Rank 30 trendln paired-channel breach fresh intake

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 先执行 `Run 1` 守门：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：当前没有 `due-now / overdue` lane（美股约 9.9h、Crypto 约 13.9h、A 股约 20.9h 后到点），因此按板子规则切到 `Scout Seat`。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short --branch`：工作区存在大量与本轮无关的已修改/未跟踪文件；本轮避免混提。
- 最近 runs：`1006 rank29-p3-monitoring-redwatch`、`0941 rank29-time-stability-p3`、`0925 rank29-no-overlap-honesty-check`、`0921 rank29-clean-replication`、`0847 rank29-trendline-breakout-navigator-intake`。
- `Paper Seat / EMA`：`waiting_not_due`，无新 completed bar，不允许伪 refresh。
- `Live Seat`：仍无 bot2 新 promoted candidate；不重占位。
- `Scout Seat`：`Rank 29 / Rank 17 / Rank 2` 当前都没有新的真实 `append/review` need，因此本轮应回到 fresh intake。

## active Scout 边际价值比较（本轮前）
- `Rank 29`：已是 `P3 narrow paper pilot approved`，且刚补完 `monitoring / weekly-review` 最小接线；当前没有新的真实 append/review 行，再继续磨近义 wiring 边际价值低。
- `Rank 17`：已是 `P3 narrow paper pilot approved（ETH+SOL-only）`；当前最近一次新增是 weekly-review writeback seed，没有新的真实 append need。
- `Rank 2`：当前也没有新的真实 append/review 行；继续往 closeout / plumbing 近义文案推进，不符合当前 fresh-intake 优先级。
- `Rank 26 / 27 / 28`：都已明确 `park / evidence pool`，不重开。
- fresh intake 候选里，`trendln paired-channel breach / corridor breakout gate` 比 prediction-market / equity-proxy 这类额外数据依赖线更便宜诚实，也比继续打磨 P3 近义 wiring 更贴合当前 `paper / repo based 5m / 15m crypto` 约束。
- 结论：本轮主资源给新的 `Rank 30` fresh source intake，不并行打开第二条新候选。

## 本轮主点 + 紧邻子点
- 主点：把 `Rank 30 trendln paired-channel breach / corridor breakout gate` 压成一张可执行的 fresh intake 卡。
- 紧邻子点：把这张 intake 同步到 `TODO` 顶部 desk board、`Trendline Alpha Scout` reader-facing 页面，以及 literature map。

## 做了什么改动
1. 新增 artifact：
   - `reports/artifacts/literature/scout_rank30_trendln_channel_source_intake_card.csv`
2. 新增 reader-facing 页面：
   - `reports/site/reading/trendline_alpha_scout/rank30_trendln_channel_source_intake.html`
3. 更新 reader-facing 入口：
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - 新增 Rank 30 fresh intake 卡，并把生成时间同步到本轮。
4. 更新 desk board：
   - `docs/TODO.md`
   - 顶部 authoritative override 改为 `2026-03-17 10:07 UTC`，并把 `Rank 30 -> admit_to_clean_replication_queue` 写入当前默认顺序与 `2m2`。
5. 更新 literature map：
   - `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 在 `trendln` 卡下补记 `Rank 30` clean-room 入口。

## 关键证据 / hard verdict
- `Rank 30` 当前不是 clean replication 结果，而是 **fresh intake only**。
- 本轮 hard verdict：**`admit_to_clean_replication_queue`**。
- 冻结入口规则：
  - `trade on = 先得到因果配对的 support/resistance lines，且 corridor width 没有异常漂移；随后只有 close-confirm breach outer line、且 composite trend 同向时才允许进场`
  - `trade off = 没有 paired active lines / 只有 wick 穿越 / breach 后很快收回 corridor 内`
- 默认下一轮只允许做 1 个最小 clean replication：固定复用 `BTC/ETH/SOL 120d 15m` cache，比较 `raw corridor breach` vs `breach_plus_reclaim_hold`，先回答 `trade_count / false_break_ratio / post_cost_return / width-stability`，再快速判 `park / P1`。

## 最小验证
已执行：
1. `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 抽查新生成文件：
   - `reports/site/reading/trendline_alpha_scout/rank30_trendln_channel_source_intake.html`
   - `docs/TODO.md` 顶部 authoritative override
   - `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 中 `trendln` 卡补充段落
3. 抽查 reader-facing 入口：
   - `reports/site/reading/trendline_alpha_scout/report.html` 已出现 Rank 30 卡片链接

## 风险 / 边界
- 本轮没有偷跑 clean replication，也没有把 `trendln` geometry baseline 直接写成已验证 alpha。
- `Rank 30` 当前仍只有 intake 级别结论；若下一轮最小 clean replication 不能快速给出更诚实的 breach / false-break 证据，应尽快 `park`。
- 工作区仍有大量与本轮无关脏文件，不做混提。

## 下一步建议
1. 若下一轮 `Rank 29 / Rank 17 / Rank 2` 仍无新的真实 append/review 行，默认按 `Rank 30` 做 **1 次最小 clean replication**。
2. 若 clean replication 不能快速形成 `trade_count + false_break_ratio + post_cost_return` 的诚实优势，就直接把 `Rank 30` 压回 `park / evidence pool`。
3. 若 `EMA` 到点，则立即把主资源切回 `Paper Seat`，不因 Rank 30 intake 打断 due-now refresh。

## Commit hash
- 未提交。
- 原因：当前 repo 存在大量与本轮无关的脏文件与未跟踪文件，避免混提。
