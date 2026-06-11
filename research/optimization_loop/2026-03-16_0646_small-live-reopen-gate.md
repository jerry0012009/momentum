# 2026-03-16 06:46 UTC｜small-live reopen gate checklist：把 parity_red 之后的重开条件压成硬门槛

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前 desk 状态：

- **Repo / worktree**：当前仓库仍有大量与本轮无关的既有脏改和未跟踪文件；本轮继续只做 selective 改动，不混提。
- **最近 runs**：`05:25 parity_red action ladder + sample row`、`06:24 breakout hard verdict sync` 已分别把 Run 3 的红旗动作链和 Run 2 的“唯一一枪”落地。当前不该再重复同一样本的 breakout rerun，也不该回头补近义 live 规则页。
- **Run 1 / Paper Seat**：当前时间仍在 `07:00 UTC` 前，`EMA paper ledger` 的真实 completed-bar refresh 还没 due；不能伪造 paper append。
- **Run 2 / Live Seat**：`breakout` 的 hard verdict 已在 `06:24` 用 cached evidence 同步完毕；board 当前 close 前 fallback 明确允许转去 `small_live` 侧补 `parity_red action / sample-row` 或同链紧邻执行卡。

因此这轮按 `Run 1 -> Run 2 -> Run 3` 的权威顺序，认领 **Run 3 的同链紧邻子点**：
1. **主点**：`parity_red reopen gate checklist v1`
2. **紧邻子点**：把它同步挂到 `alpha_closure_board` 与 `TODO / plans` 镜像，避免只留在日志里。

## 做了什么改动
### 1) 新增 tiny-live 的 `parity_red` 重开门槛 artifact
在 `scripts/build_alpha_closure_board_report.py` 中新增：
- `reports/artifacts/alpha_closure_board/small_live_reopen_gate_checklist_v1.csv`

这张表把前一轮已经出现的 `reopen_earliest_ts` 收紧成真正的 operator 条件，而不是“时间到了自动再试”。当前 v1 共 5 步：
1. **先尊重 cooldown / reopen_earliest_ts**
2. **上一条 red cause 必须被单独关单**（`mismatch_reason / trigger_reason` 要有明确解释与证据）
3. **先重走一次最小 routing dry-run 回执链**（`intent -> ack -> cancel/close`）
4. **新的 shadow row 必须重新过 qty / cost parity**
5. **只有拿到新的 `green shadow parity row` 才允许恢复 review**

### 2) 同步 reader-facing 页面
这轮同步更新：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

网页上当前已经能直接看到：
- `Parity-red reopen gate checklist（v1）`
- 对应 artifact 路径 `small_live_reopen_gate_checklist_v1.csv`
- `2026-03-16 06:46 UTC` 的最新 desk 补充说明

### 3) 本轮真正解决的是什么
前一轮已经回答了：
- 出现 `parity_red` 时要怎么 `hold / cancel / escalate / freeze review`
- 红旗样例行应该怎么写账

但还没写死的是：
- **什么时候才算真的可以重开**

这轮把那条灰区压掉了：
- `reopen_earliest_ts` 只是**最早时点**，不是自动赦免；
- 必须先把上一条 red cause 关掉，并重新拿到干净回执和新的 green shadow parity row，才配恢复 `small-live promotion review`。

## 验证 / 证据
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_alpha_closure_board_report.py`
3. `python3 scripts/build_plans_site.py`
4. 检查 `reports/artifacts/alpha_closure_board/small_live_reopen_gate_checklist_v1.csv` 前 5 行
5. 检查 `reports/site/factors/alpha_closure_board/report.html` 是否出现 `Parity-red reopen gate checklist（v1）`
6. 检查 `reports/site/plans/momentum_todo.html` 是否出现 `small_live_reopen_gate_checklist_v1.csv` 与 `2026-03-16 06:46 UTC`

已确认：
- 新 CSV artifact 已生成；
- `alpha_closure_board` 已出现新 reader-facing 卡片；
- `TODO` 与 plans mirror 已同步本轮补充；
- 没有重跑新的重型下载，也没有重复 breakout 同样本 rerun。

## 本轮 hard verdict
- **Paper Seat**：仍是 `waiting_not_due`，这轮不应伪造 EMA refresh。
- **Live Seat**：close 前的那次唯一 hard verdict 已在上一轮落地；这轮不值得继续重复 rerun / wording。
- **Run 3 / tiny-live plumbing**：当前最有效的一刀，是把 `parity_red` 之后的**重开条件**正式锁死，防止 future run 把等待时间误读成自动放行。

一句话结论：
**这轮把 `small_live` 路线里最后一个最容易被“先等一会儿再试”带过去的灰区，压成了 `reopen gate checklist` 硬门槛。**

## 风险 / 边界
- 这仍然不是 tiny-live 放行，也不是任何真实下单。
- 这张表约束的是 **red row 之后怎么重开**，不是重新定义 live admission 本身。
- 当前阈值（如 `clock drift <= 60s`、`cost delta <= 25bps`）仍是 v1 口径；若以后要调整，应该单独立项，而不是静默改表。

## 下一步建议
1. `07:00 UTC` 后的第一轮 bot3 run，默认按板子优先切回 **EMA paper ledger guarded refresh / append**；若 data source 仍未给出新的 completed bar，就如实记成 on-clock waiting，而不是伪造 refresh。
2. 若后续再次回到 `small_live` 链，优先补真正与现有 ledger 相邻的 green-row / resume 样例，而不是再写一张抽象 tiny-live 说明页。

## Commit hash
- HEAD：`7719bc3`
- 本轮未提交。

## 如果未提交，原因
- 当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件，不适合安全 selective commit；本轮只刷新必须的脚本 / artifact / 页面 / 计划镜像。