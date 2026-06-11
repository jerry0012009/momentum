# 2026-03-16 07:06 UTC｜small-live reopen resume row：把 red→green 的恢复账本样例补齐

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前 desk 状态：

- **Repo / worktree**：仓库仍有大量与本轮无关的既有脏改和未跟踪文件；本轮继续只做 selective 改动，不混提。
- **最近 runs**：`06:24 breakout hard verdict sync` 已把 close 前那次 breakout 唯一重枪落地；`06:46 parity_red reopen gate checklist` 已把 small-live 的 red 后重开条件压成硬门槛。
- **Run 1 / Paper Seat**：当前 still 在 `07:00 UTC` close 切换窗口附近，本轮开始时 `EMA paper` 仍是 `waiting_not_due`，不应伪造日线 refresh。
- **Run 2 / Live Seat**：同一样本 breakout 不值得在 close 前重复 rerun；board 允许 fallback 到 `small_live` 侧补同链紧邻执行卡。

因此这轮按 `Run 1 -> Run 2 -> Run 3` 的 desk 顺序，认领 **Run 3 / tiny-live plumbing** 的 1 个主点 + 1 个紧邻子点：
1. **主点**：`small_live_reopen_resume_sample_row_v1.csv`
2. **紧邻子点**：把它同步挂到 `alpha_closure_board` 与 `TODO / plans` 可见落点

## 本轮做了什么
### 1) 新增 green shadow parity / resume 样例行
在 `scripts/build_alpha_closure_board_report.py` 里新增：
- `reports/artifacts/alpha_closure_board/small_live_reopen_resume_sample_row_v1.csv`

这张样例行不是新的放行规则，而是回答一个更执行型的问题：
**当上一条 `parity_red` 已被关掉、且 reopen gate 真的通过后，第一条恢复用的 `green shadow parity row` 该怎么写。**

当前样例固定了这些关键信息：
- `prior_red_ref_id`：把恢复行与上一条 red row 审计链连起来
- 新的 `paper_ref_id / live_shadow_ref_id`
- 重跑后的 `route_intent_ts_utc / route_ack_ts_utc / ack_latency_ms`
- 重新过关的 `rounded_qty / cost_estimate_bps`
- `mismatch_status=green`
- `operator_action=resume_shadow_review`
- 新的 `reopen_earliest_ts`

### 2) 同步 reader-facing 页面
本轮同步更新：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

其中 `alpha_closure_board` 新增卡片：
- `Reopen resume sample row（v1）`

`TODO / plans` 也同步新增 `2026-03-16 06:59 UTC` 的 latest supplement，明确这一步是 **red→green 恢复账本样例**，不是 tiny-live 放行。

## 为什么这一步有用
前两轮已经回答了：
- 出现 `parity_red` 时默认动作是什么；
- red 之后什么条件才允许 reopen。

但还缺最后一段最容易在执行时断链的地方：
- **reopen 真的通过后，恢复行到底怎么写**。

这轮把这段灰区补齐后，future run 就不会只会写一句“可以恢复 review 了”，却把：
- 上一条 red row，
- 新的 route 回执，
- 恢复后的 green row，

三者拆成互不相认的碎片记录。

## 最小验证
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
2. `python3 scripts/build_alpha_closure_board_report.py`
3. `python3 scripts/build_plans_site.py`
4. 检查 `small_live_reopen_resume_sample_row_v1.csv` 首行/样例行
5. 检查 `alpha_closure_board/report.html` 出现 `Reopen resume sample row（v1）`
6. 检查 `momentum_todo.html` 出现 `small_live_reopen_resume_sample_row_v1.csv` 与 `2026-03-16 06:59 UTC`

已确认：
- 新 CSV artifact 已生成；
- `alpha_closure_board` 已出现新卡片；
- `TODO / plans` 已出现本轮 latest supplement；
- 没有重跑重型下载，也没有重复 breakout 同样本 heavy rerun。

## 本轮 hard verdict
- **Paper Seat**：开始时仍是 `waiting_not_due`；本轮不伪造 EMA refresh。
- **Live Seat**：close 前 breakout 唯一一枪已经打过；本轮不重复同样本 rerun。
- **Run 3 / tiny-live plumbing**：当前最值得补的不是更多 live 规则页，而是把 `parity_red -> reopen_gate -> green resume row` 这条执行链补成闭环。

一句话结论：
**这轮把 small-live 里最容易“口头说恢复、账本却断链”的一段，压成了可复用的 green resume sample row。**

## 风险 / 边界
- 这不是 tiny-live 放行，也不是任何真实下单。
- 这张样例行只是 v1 审计模板，不是 live venue 接通证明。
- 当前阈值（如 `cost <= 25bps`、`clock drift <= 60s`）仍沿用前序 v1 口径；如需调整，应单独立项，不应静默改样例。

## 下一步建议
1. `07:00 UTC` 后的第一轮 paper 轮次，默认切回 **EMA paper ledger guarded refresh / append**；若 source 仍未出现新的 completed bar，就如实记成 waiting，不造 refresh。
2. 若后续再次回到 `small_live` 子链，优先补真实 ledger/route dry-run 对接检查，而不是再写抽象说明页。

## Commit hash
- HEAD：`1f84291`
- 本轮未提交。

## 如果未提交，原因
- 当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件，不适合安全 selective commit；本轮仅刷新必要脚本 / artifact / 页面 / 计划镜像。
