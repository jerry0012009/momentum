# 2026-03-16 16:08 UTC｜Run 3 closeout：Rank 2 routing dry-run replay ticket

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 仍处于真实 `waiting_not_due`，当前没有新的 `due-now / overdue` refresh。
- `Run 2 / Scout Seat`：`Rank 2 combo_all` 这几轮已经完成 `paper candidate admission / monitoring / cross-asset stability`，并已被写成一条 concrete `blocked dry-run registry row`；当前没有新的合格 scout 主动作值得继续扩研究。
- 因此本轮按顺序进入 `Run 3 / tiny-live plumbing`，只认领一个紧邻 closeout 子点：**把 `routing_dry_run_replay` 从抽象 next_queue 压成一张可直接打开的 replay ticket。**

## 开始前检查
- `git status --short`：仓库仍有大量与本轮无关的历史脏文件 / 未跟踪文件；本轮坚持 selective 改动，不混提。
- 当前席位读法不变：`Paper = EMA running paper / waiting_not_due`，`Live = 暂空`，`Scout = Rank 2 narrow paper candidate`。
- 最近相邻 logs：
  - `2026-03-16_1549_scout-rank2-crossasset-stability.md`
  - `2026-03-16_1558_rank2-dryrun-registry-row.md`
- 当前 closeout 链已存在：
  - `small_live_rank2_paper_candidate_handoff_map_v1.csv`
  - `small_live_rank2_dry_run_registry_row_v1.csv`

## 本轮做了什么
### 1）新增 concrete replay artifact
新增：
- `reports/artifacts/alpha_closure_board/small_live_rank2_routing_dry_run_replay_ticket_v1.csv`

它把上一轮 registry row 里的：
- `next_queue = routing_dry_run_replay`

继续压成一张**可直接开工的 replay ticket**，明确写死：
- 当前候选仍是 `rank2_combo_all_15m_narrow_paper`
- `deployment_scope = paper_candidate_only`
- replay scope 只允许 `BTC/ETH/SOL whitelist`，且 `capital = 0`
- 必须补齐的 receipt chain 是：`intent -> ack -> cancel/close (test/no-fill)`
- 必绑 supporting refs：
  - `small_live_rank2_paper_candidate_handoff_map_v1.csv`
  - `combo_all_paper_candidate_monitoring_board.csv`
  - `small_live_review_ticket_template_v1.csv`
  - `small_live_routing_dry_run_checklist_v1.csv`
- 当前 blockers 继续明牌：
  - `idle_gap_watch = 58.6d`
  - `time_pocket_review = early_bucket_-1.34%_0of3_positive`
  - `route_receipt_chain_missing`
  - `promotion_boundary = paper_candidate_only`

### 2）同步 reader-facing 页面
修改：
- `scripts/build_trendline_alpha_scout_report.py`

新增网页卡片：
- `Run 3 replay bundle（Rank 2 routing dry-run replay ticket）`

这张卡把本轮结果同步到：
- `reports/site/reading/trendline_alpha_scout/report.html`

因此 Jerry 在网页上能直接看到：
**`Rank 2` 现在不仅有 blocked registry row，还有一张 concrete replay ticket；但它仍是 `blocked / paper_candidate_only`，并没有被偷升格成 tiny-live。**

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_trendline_alpha_scout_report.py`
3. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
4. `grep -n "Rank 2 routing dry-run replay ticket\|small_live_rank2_routing_dry_run_replay_ticket_v1.csv" reports/site/reading/trendline_alpha_scout/report.html`

命中结果：
- 网页已出现 `Run 3 replay bundle（Rank 2 routing dry-run replay ticket）`
- artifact 链接已可见：`small_live_rank2_routing_dry_run_replay_ticket_v1.csv`

## 关键结果 / hard verdict
核心 hard verdict：

**`Rank 2 combo_all` 现在已被更进一步写成一张 concrete `routing_dry_run_replay` ticket，但当前状态仍是 `blocked / paper_candidate_only`。在至少一条白名单 symbol 的 test/no-fill `intent -> ack -> cancel/close` 回执链真正补齐前，不得进入 `shadow_parity`，更不得写成 tiny-live ready。**

这轮价值不在于“证明它更接近 live”，而在于：
- 把上一轮的 `next_queue` 变成了一张能直接开的票；
- 同时把允许的边界和不得越级的条件继续写死。

## 网页可见落点
- `reports/site/reading/trendline_alpha_scout/report.html`
- 首页索引已刷新：`https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 本轮没有新增 alpha 证据，也没有重开 Scout heavy analysis。
- 本轮也不是 dry-run pass，只是把 replay queue 压成 concrete ticket。
- 若后续没有真实 receipt chain，本票应继续维持 `blocked / routing_dry_run_replay`，不能靠 wording 漂移升级。

## Commit hash
- 基线：`cdd91a4`

## 未提交原因
当前 worktree 含大量与本轮无关的历史脏文件 / 未跟踪文件；为避免混提，本轮只做 selective artifact、网页同步、日志与邮件交付，不提交。
