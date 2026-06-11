# 2026-03-16 05:25 UTC｜small-live parity_red action ladder：把 Run 3 的红旗分支压成可执行 operator 动作

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前 desk 状态：

- **Repo / worktree**：当前仓库存在大量与本轮无关的既有脏改与未跟踪文件（docs / reports / artifacts / scripts / workspace 上层目录都有）；本轮继续只做 selective 改动，避免混提。
- **最近 runs**：`04:10 routing dry-run checklist`、`04:36 paper-live shadow parity checklist`、`04:59 scout rank2 first verdict`、`05:15 scout rank2 friction recheck`。根据 board，本轮不该再重复同一样本 scout 续切。
- **Run 1 / Paper Seat**：A 股 daily 仍在真实 `waiting_not_due` 窗口，当前不能伪造新的 paper refresh / week-1 review。
- **Run 2 / Live Seat**：breakout 在本轮认领时仍处于 rerun cooldown 窗口，board 明确写了 cooldown 结束前若再 fallback，优先去补 `small_live parity_red action / sample-row` 这类紧邻执行卡。

因此本轮按顺序从 `Run 1 -> Run 2 -> Run 3` 自动落到 **Run 3**，且只认领 1 个主点 + 1 个紧邻子点：
1. **主点**：`parity_red action ladder v1`
2. **紧邻子点**：`shadow parity sample row v1`

## 做了什么改动
### 1) 在 `scripts/build_alpha_closure_board_report.py` 中新增两张 tiny-live 执行卡
新增 artifacts：
- `reports/artifacts/alpha_closure_board/small_live_parity_red_action_ladder_v1.csv`
- `reports/artifacts/alpha_closure_board/small_live_shadow_parity_sample_row_v1.csv`

具体把什么写死了：
- 当 `shadow parity` 出现 `payload / whitelist / precision mismatch` 时，默认动作不是“再试一次”，而是 `hold + cancel_or_no_send`。
- 当出现 `clock drift > 60s / stale price / bar misalignment` 时，默认动作是停在 parity review，先重抓 price snapshot / 对齐 bar。
- 当 `rounded_qty` 把 notional 拉出 cap、或 `min_notional` 不过时，默认动作是退回 `paper only` 的 sizing/cap review，不能手改数量凑单。
- 当 `shadow` 成本偏差 `> 25bps` 或成本快照缺失时，默认动作是 `escalate`，不进入 tiny-live 资格讨论。
- 当连续 `2` 次 `parity_red` 或出现未解释 data gap / precision mismatch 时，默认动作是冻结当前 candidate 的 small-live promotion review，退回 `paper only`，并要求重新走 `routing dry-run -> shadow parity`。

### 2) 给出一条最小 `shadow_parity` 红旗样例行
sample row 选择的是一个故意 `red` 的场景：
- `candidate_id = breakout-live-challenger`
- `paper_ref_id / live_shadow_ref_id` 成对存在
- `shadow_price = 1985.20`
- `cost_estimate_bps = 31`
- `mismatch_status = red`
- `mismatch_reason = cost_gap_or_missing_snapshot`
- `operator_action = hold`
- `reopen_earliest_ts = 2026-03-16 05:35:00 UTC`

这条样例行的意义不是伪造真实订单，而是把“当成本偏差超阈值时，账本至少要同时留下哪些字段”压成 reader-facing 模板，避免 future run 只在日志里写一句“先 hold”。

### 3) 同步 reader-facing 落点
本轮同时更新了：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

这样本轮结果不只留在 log / 邮件里，网页上也能直接看到：
- `Parity-red action ladder（v1）`
- `Shadow parity sample row（v1）`

## 验证 / 证据
执行了最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_alpha_closure_board_report.py`
3. `python3 scripts/build_plans_site.py`
4. `sed -n '1,8p' reports/artifacts/alpha_closure_board/small_live_parity_red_action_ladder_v1.csv`
5. `sed -n '1,5p' reports/artifacts/alpha_closure_board/small_live_shadow_parity_sample_row_v1.csv`
6. `grep -n "Parity-red action ladder（v1）\|Shadow parity sample row（v1）" reports/site/factors/alpha_closure_board/report.html`
7. `grep -n "2026-03-16 05:19 UTC\|small_live_parity_red_action_ladder_v1.csv\|small_live_shadow_parity_sample_row_v1.csv" docs/TODO.md reports/site/plans/momentum_todo.html`

已确认：
- 两个新 CSV artifact 已生成；
- `alpha_closure_board` 已出现两块新 reader-facing 区块；
- `TODO` 与 plans mirror 已同步本轮补充；
- 没有重跑任何不必要的重型下载或同样本研究 rerun。

## 本轮 hard verdict
- **Paper Seat**：仍是 `waiting_not_due`，这轮不应伪造 refresh。
- **Live Seat**：本轮认领时仍处在 cooldown fallback 窗口；不值得再重复 breakout blocker wording 或同类 rerun。
- **Run 3 / tiny-live plumbing**：当前最有效的一刀，就是把 `parity_red` 从“知道要标红”推进成**出现红旗后 operator 到底该怎么做、账本该怎么写、何时才允许重开**的硬分支。

一句话结论：
**这轮把 small-live 路线里最容易被口头淡化的 `parity_red`，正式压成了 `action ladder + sample row` 两张执行卡。**

## 风险 / 边界
- 这仍然不是 tiny-live 放行，也不是已接入真实 venue。
- sample row 是执行模板，不是真实成交记录。
- `parity_red` 阈值与默认动作当前仍是 v1 口径；如果以后要放宽 / 收紧，应该单独立项，而不是静默改样例行。

## 下一步建议
1. 若下一轮已经脱离 cooldown，按 board 回到 **Run 2 / breakout**，只给一次 honest rerun / verdict 机会；若 blocker 仍不下降，优先走 `bench / narrower-scope review`。
2. 若仍落回 Run 3，不要再补近义 tiny-live 规则页；应只补与现有 ledger / routing / parity 链真正相邻的执行卡。

## Commit hash
- HEAD：`7719bc3`
- 本轮未提交。

## 如果未提交，原因
- 当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件，不适合安全 selective commit；本轮只刷新必须的脚本 / artifact / 页面 / 计划镜像。