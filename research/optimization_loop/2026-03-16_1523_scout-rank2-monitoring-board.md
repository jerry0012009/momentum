# 2026-03-16 15:23 UTC｜Scout Seat：Rank 2 combo_all paper candidate monitoring board / admission write-back

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 当前处于真实 `waiting_not_due`，没有新的 `due-now / overdue` refresh。
- 因此本轮切到 `Run 2 / Scout Fast Lane`。
- `Next 3 bot3 runs` 当前 authoritative 顺序是：`Rank 2 paper-candidate narrow scope -> tiny-live plumbing -> 其他维护 / 等 bot2 新点名`。
- `Rank 2 combo_all` 已在上一轮完成 `paper candidate admission memo`；这轮最贴主线的一小步，不该再扩研究，而是把 memo 里那句“最小 ledger / monitoring”真正压成可复用 artifact。

本轮只认领：
- **主点**：把 `Rank 2 combo_all` 的最小 `ledger / monitoring` 接口落成 deployable artifact。
- **紧邻子点**：同步更新 reader-facing 页面（factor 页 + scout 汇总页）并刷新首页索引。

## 开始前检查
- `git status --short`：工作区仍有大量与本轮无关的历史脏文件 / 未跟踪文件；本轮坚持 selective 产物与日志，不混提。
- 当前席位：`Paper=EMA waiting_not_due`，`Live=暂空`，`Scout=默认主资源`。
- 当前 Rank 2 状态：仍是**窄范围 `paper candidate / one more light check`**；尚未进入 live / tiny-live。

## 本轮做了什么
1. 修改 `scripts/build_volume_supportflip_higherlow_first_verdict.py`
   - 新增 artifact：
     - `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_monitoring_board.csv`
   - 新增逻辑：
     - `build_paper_candidate_monitoring_board(...)`
     - `derive_paper_candidate_monitoring_verdict(...)`
   - 将 monitoring verdict 写入 `trial_meta.csv`（字段 `paper_candidate_monitoring_verdict`）
   - 在 Rank 2 factor 页新增 `paper candidate 最小 ledger / monitoring board` 卡片。

2. 修改 `scripts/build_trendline_alpha_scout_report.py`
   - 在 Rank 2 汇总卡同步展示 `paper candidate monitoring` reader-facing 结论；
   - 让 Scout 汇总页能直接看到这轮不是“又补一张近义说明页”，而是把 paper-candidate 接线压成可复用 board。

3. 新增 monitoring board 的最小执行栏位
   - `scope_lock`
   - `signal_ledger`
   - `false_break_watch`
   - `idle_gap_watch`
   - `time_pocket_review`
   - `promotion_boundary`

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
5. `grep` 校验网页落点：
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## 关键结果 / hard verdict
新增 artifact：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_monitoring_board.csv`

核心结论：
- `combo_all` 这轮**没有**新增 seat-level 升格；它仍是**窄范围 `paper candidate / one more light check`**。
- 但 admission memo 里原先只写在一句话里的 `minimal_ledger_monitoring`，现在已经被压成真正可复用的 board，可更诚实地接到后续 `paper candidate` 级别的记账 / 巡检。
- 当前最该盯的 watch 位被明确锁成两条：
  - `idle_gap_watch`：历史样本最大 gap 仍约 `58.6 days`
  - `time_pocket_review`：仍需固定回看 `early bucket` 的弱 pocket
- 因此这轮结果是：**推进了 Rank 2 的 admission write-back / monitoring 接线，但没有改变它仍不得偷升格成 Live Seat / tiny-live 的边界。**

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 这轮不是新的 Light Stability Pack 扩展，也不是 forward continuity 证据。
- monitoring board 只服务 `paper candidate` 级别接线；若要进 `shadow / tiny-live`，仍必须另拿新证据。
- 当前工作区存在大量无关脏文件；本轮没有做提交。

## Commit hash（基线）
- `76cea75`

## 如果未提交，原因
当前 worktree 有大量与本轮无关的脏文件 / 未跟踪文件；为避免混提，本轮只做 selective 构建、网页刷新、日志与邮件交付，不提交。
