# 2026-03-16 17:07 UTC｜Run 3：Rank 2 receipt completion gate

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 仍处于真实 `waiting_not_due`，这轮不能停在 paper waiting-window 空转。
- `Run 2 / Scout Seat`：`Rank 2 combo_all` 已完成 `clean replication + Light Stability Pack + paper candidate admission`，当前 board 已明确不应继续无限扩研究。
- `Run 3 / tiny-live plumbing`：上一轮已把 `whitelist-bound receipt chain` 的 operator packet 与 writeback template 落表；本轮最接近主线的一小步，是把 **什么才算 receipt chain 真补齐** 压成 hard closeout gate，避免后续把模板行、单段 ack 或 scope 漂移误写成通过。

## 开始前检查
- `git status --short --branch`：仓库里仍有大量与本轮无关的历史脏文件 / 未跟踪文件，本轮继续坚持 selective 改动，不混提。
- 当前 authoritative desk 状态：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = Rank 2 narrow paper candidate`，若无新 scout 动作则回退到 tiny-live plumbing
- 相邻 runs：
  - `2026-03-16_1624_rank2-status-snapshot.md`
  - `2026-03-16_1658_rank2-receipt-log-template.md`

## 本轮改动
### 1）新增 deployable artifact：receipt completion gate
更新 `scripts/build_trendline_alpha_scout_report.py`，新增生成：

- `reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_completion_gate_v1.csv`

这张 gate 表把三条 whitelist leg（`BTC/ETH/SOL`）各自的 closeout 规则写成机器可读 row：
- `receipt_gate_status=blocked_until_three_real_refs_land`
- `required_real_refs=intent_ref + ack_ref + cancel_or_close_ref`
- `pass_condition=三段真实回执同链落地 + scope 不漂移 + capital=0`
- `pass_transition=eligible_for_shadow_parity_review only; still not tiny-live`
- `fail_transition=keep dry_run_only / blocked and route back to routing_dry_run_replay`

核心作用不是再加一张说明页，而是把 **“真实 replay 到底什么条件下才算 pass”** 固定下来。

### 2）同步 reader-facing 页面
已同步到：
- `reports/site/reading/trendline_alpha_scout/report.html`

新增卡片：
- `Run 3 receipt completion gate（Rank 2 hard closeout rule）`

页面现在直接外显：
**只有在同一条 whitelist-bound replay 上同时拿到真实 `intent_ref + ack_ref + cancel_or_close_ref`，并且 scope 不漂移、capital 继续为 0，才允许把 Rank 2 从 `paper_candidate_only / blocked` 收口到 `eligible_for_shadow_parity_review`；否则继续 blocked。**

### 3）回写 authoritative board
更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `Rank 2` 条目，新增 `2026-03-16 17:07 UTC` 补充：
- `small_live_rank2_receipt_chain_completion_gate_v1.csv` 已落表；
- 模板行、单段 ack、或 scope 漂移都不算 `receipt chain pass`；
- 只有三段真实回执同链落地，才允许往 `eligible_for_shadow_parity_review` 收口。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_trendline_alpha_scout_report.py`
3. 校验新 artifact：`small_live_rank2_receipt_chain_completion_gate_v1.csv` 共 `3` 行（`BTC/ETH/SOL`）
4. `grep -n "receipt completion gate\|small_live_rank2_receipt_chain_completion_gate_v1.csv" reports/site/reading/trendline_alpha_scout/report.html`
5. `grep -n "2026-03-16 17:07 UTC\|receipt_chain_completion_gate_v1.csv\|eligible_for_shadow_parity_review" docs/TODO.md`
6. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## 硬结论
本轮新的 hard verdict：

**`Rank 2 combo_all` 仍然只是窄范围 `paper candidate`，并且 receipt chain 的通过条件现在已经被收紧成一条 hard gate：必须是同一条 whitelist-bound `test/no-fill replay` 上的三段真实回执全落地，且 scope 不漂移、capital=0；否则一律继续 `paper_candidate_only / blocked`，不得偷进 `shadow_parity`，更不得写成 `tiny-live ready`。**

这轮的价值在于：
- 把“有模板”与“真补齐回执链”彻底分开；
- 把 future run 最容易发生的误判（只拿到单段 ack 就当通过、或 scope 漂移后硬说是同一条 replay）提前堵死；
- 让后续若真发生 receipt replay，可以直接按这张 gate 表做 pass/fail closeout，而不是再临时解释。

## 网页可见落点
- `reports/site/reading/trendline_alpha_scout/report.html`
- 首页索引已刷新：`https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
1. 本轮没有新增真实 venue receipt，也没有让 Rank 2 更接近 tiny-live 放行。
2. 这张 gate 仍然是 closeout rule，不是 dry-run pass 证据。
3. 当前任何把 Rank 2 写成“receipt chain 基本算补齐了”的表述，都应视为越界，除非三段真实 refs 同链落地。

## Commit hash
- 基线：`2080941`

## 未提交原因
当前 git 工作区仍含大量与本轮无关的历史脏文件 / 未跟踪文件；为避免混提，本轮只完成 selective artifact、reader-facing 页面、board write-back、日志与邮件交付，不提交。
