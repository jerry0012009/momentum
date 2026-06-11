# 2026-03-16 15:58 UTC｜Run 3 closeout：Rank 2 blocked dry-run registry row

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 仍是 `waiting_not_due`，当前没有新的 `due-now / overdue` refresh。
- `Run 2 / Scout Seat`：`Rank 2 combo_all` 这几轮已经把 `paper candidate admission / monitoring / cross-asset stability` 补得足够明确；当前 bot2 最新 review 也明确说，这条线下一步更像 `admission write-back / narrow scope / monitoring constraint`，若没有新的合格 scout 主动作，就应直接回退到 `tiny-live plumbing`。
- 因此这轮按顺序进入 `Run 3`，但不再重复抽象规则页，而是把 `Rank 2` 真正落成一条**可审计的 closeout / registry row**。

本轮只认领：
- **主点**：把 `Rank 2 combo_all` 写成一条 concrete `blocked dry-run registry row`，明确它当前只能停留在 `paper_candidate_only`，并排队到 `routing_dry_run_replay`。
- **紧邻子点**：把该 row 同步到 reader-facing 网页，避免只留 artifact / 日志不可见。

## 开始前检查
- `git status --short`：工作区仍有大量与本轮无关的历史脏文件 / 未跟踪文件；本轮坚持 selective 改动，不混提。
- 最近 optimization logs：最新两轮已分别补了 `Rank 2 cross-asset stability` 与 `Rank 2 -> tiny-live handoff map`。
- 最新 strategy review（`2026-03-16_1551_strategy-review.md`）判断不变：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat` 里只有 `Rank 2 combo_all` 仍留在窄范围 `paper candidate / one more light check`
  - 若 Scout 暂时没有新的合格主点，默认就沿 `handoff / review-ticket / writeback / registry` 这条 `tiny-live plumbing` closeout 链继续补相邻卡。

## 本轮做了什么
### 1）新增 concrete closeout artifact
新增：
- `reports/artifacts/alpha_closure_board/small_live_rank2_dry_run_registry_row_v1.csv`

这不是模板，而是一条具体的 `Rank 2` registry row，核心字段包括：
- `ticket_id=rank2-dryrun-001`
- `candidate_id=rank2_combo_all_15m_narrow_paper`
- `deployment_scope=paper_candidate_only`
- `review_stage=dry_run`
- `ticket_status=blocked`
- `closeout_state=dry_run_only`
- `next_queue=routing_dry_run_replay`
- `blocking_watchers=idle_gap_watch=58.6d; time_pocket_review=early_bucket_-1.34%_0of3_positive; promotion_boundary=paper_candidate_only`

一句话：
**现在允许写入 registry，但不允许把这条 plumbing row 误读成已经通过 dry-run，更不允许借机偷升格成 tiny-live。**

### 2）更新 reader-facing 页面
修改：
- `scripts/build_trendline_alpha_scout_report.py`

新增网页卡片：
- `Run 3 closeout registry（Rank 2 blocked dry-run row）`

这样 Jerry 在网页上可以直接看到：
- 当前 `Rank 2` 不是“又多一张近义说明页”，而是已经被写成一条 concrete closeout row；
- 但这条 row 的状态仍是 **blocked / paper_candidate_only**；
- 当前 blocker 仍是 `idle-gap / early-pocket / promotion boundary`，不是 live 资格已通过。

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_trendline_alpha_scout_report.py`
3. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
4. `grep -n "Rank 2 blocked dry-run row\|small_live_rank2_dry_run_registry_row_v1.csv" reports/site/reading/trendline_alpha_scout/report.html`

命中结果：
- 网页已出现 `Run 3 closeout registry（Rank 2 blocked dry-run row）`
- artifact 链接已可见：`small_live_rank2_dry_run_registry_row_v1.csv`

## 关键结果 / hard verdict
核心 hard verdict：

**`Rank 2 combo_all` 现在可以被更诚实地写成一条 concrete `blocked dry-run registry row`，但它仍只配停在 `paper_candidate_only`；在补齐真实 dry-run receipt chain、并清楚处理 `idle-gap / early-pocket` 之前，不得进入 `shadow_parity`，更不得偷写成 tiny-live ready。**

这条结论比“继续口头说 narrow scope”更硬，因为它已经进入 closeout / registry 链，后续任何升级都必须显式跨过这条 row，而不是靠 wording 漂移。

## 网页可见落点
- `reports/site/reading/trendline_alpha_scout/report.html`
- 首页索引已刷新：`https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 本轮没有新增 alpha 证据，也没有重开 Scout heavy analysis。
- 本轮不是 tiny-live 放行；相反，它是在**更明确地阻止越级放行**。
- 当前 `Rank 2` 仍只是窄范围 `paper candidate / one more light check`，不是 `Live Seat`。

## Commit hash
- 基线：`76cea75`

## 未提交原因
当前 worktree 含大量与本轮无关的历史脏文件 / 未跟踪文件；为避免混提，本轮只做 selective artifact、网页同步、日志与邮件交付，不提交。
