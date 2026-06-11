# 2026-03-16 07:51 UTC｜small-live operator reconciliation sequence：把分散的 plumbing 执行卡压成一条可顺走的对账顺序

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行当前 `Next 3 bot3 runs`：

- `Run 1 / Paper Seat`：`EMA` 已在 `07:13 UTC` 实际执行过 guarded refresh，并如实回到 `waiting_not_due`；当前不该继续重复 paper 守门。
- `Run 2 / Live Seat`：`support_breakout_v0` 的 `bench` verdict 已在 `07:30 UTC` 完成 reader-facing sync；当前没有新的 blocker reduction 证据，不值得继续同类 rerun。
- 因此本轮默认切到 `Run 3 / tiny-live plumbing`。

同时回看最近几轮 `small_live` 子链，已经分散落下：
1. `routing dry-run checklist`
2. `routing dry-run green sample row`
3. `paper-live shadow parity checklist`
4. `parity_red action ladder + red sample row`
5. `reopen gate checklist`
6. `green resume sample row`

问题变成：**artifact 已经不少了，但 future run 真开始核对时，operator 还是可能不知道先看哪张、失败后该退回哪一步。**

所以这轮只认领 1 个主点：

- **主点**：把前面分散的 `small_live` 执行卡压成一张 `operator reconciliation sequence v1`
- **紧邻子点**：把它同步挂到 `alpha_closure_board` 与 `TODO / plans`，让 reader-facing 页面也能直接看到这条执行顺序

## 本轮做了什么改动
### 1) 新增 `small_live_operator_reconciliation_sequence_v1.csv`
在 `scripts/build_alpha_closure_board_report.py` 中新增 artifact：

- `reports/artifacts/alpha_closure_board/small_live_operator_reconciliation_sequence_v1.csv`

这张表没有发明新规则，而是把已有的 v1 artifact 串成一条顺序化 operator 流程：

1. `dry-run green row` 先落账，确认 `intent -> ack -> cancel` 三段回执完整，且仍停在 `test/no-fill`
2. 再进 `paper-live shadow parity checklist`，把 `paper_ref / live_shadow_ref / qty / cost / clock` 审干净
3. 若出现 `parity_red`，按 `action ladder + red sample row` 的硬分支处理，而不是口头“先等等”
4. 只有 `reopen gate checklist` 真逐条过关，才允许讨论重开
5. 最后用 `green resume sample row` 把 `prior_red_ref_id -> 新 green row` 接回同一条审计链

### 2) 同步 reader-facing 页面
本轮同步更新：

- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

其中 `alpha_closure_board` 新增区块：
- `Small-live operator reconciliation sequence（v1）`

当前网页上已经可以直接看到：
- 先复用哪张 artifact
- 这一步到底核对什么
- 通过后应产出什么
- 失败后必须停在哪
- 同账本锚点字段是什么

## 为什么这一步有用
前几轮已经把 `small_live` 的局部卡片补得比较完整，但更像一叠零散材料。当前真正缺的是：

**把这些材料压成一条“operator 从上到下顺着走”的执行顺序。**

这一步的价值不是新增 tiny-live 放行，而是降低 future run 的执行歧义：

- 不再只是“有 checklist / sample row”
- 而是明确：
  - 先看哪张
  - 通过后写什么 row
  - 失败后退到哪一步
  - 哪些字段是同账本里的锚点

这样后续若真进入 venue dry-run / shadow parity，对账链不容易再断在：
- green row 没接到 parity checklist
- red row 只有日志没有账本动作
- reopen 只写“恢复 review”却没有接回 `prior_red_ref_id`

## 本轮 hard verdict
一句话结论：

**这轮把前面几轮分散的 `small_live` plumbing 执行卡，压成了一条可顺着执行的 `operator reconciliation sequence`，让 future tiny-live 对账不再只是“资料齐了”，而是“顺序也齐了”。**

更诚实的边界仍然是：
- 这不是 tiny-live 放行；
- 不是任何真实下单；
- 只是把 `dry-run -> shadow parity -> parity_red -> reopen -> green resume` 这条执行链进一步压成可复用顺序。

## 最小验证
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py` ✅
2. `python3 scripts/build_alpha_closure_board_report.py` ✅
3. `python3 scripts/build_plans_site.py` ✅
4. `grep -n "Small-live operator reconciliation sequence（v1）\|small_live_operator_reconciliation_sequence_v1.csv" reports/site/factors/alpha_closure_board/report.html reports/site/plans/momentum_todo.html docs/TODO.md` ✅
5. `sed -n '1,6p' reports/artifacts/alpha_closure_board/small_live_operator_reconciliation_sequence_v1.csv` ✅

核对结果：
- 新 artifact 已生成；
- `alpha_closure_board` 本地 reader-facing 页面已出现新卡；
- `TODO / plans` 已同步 `2026-03-16 07:51 UTC` 的最新补充；
- CSV 首行已明确串起 `dry-run green row -> parity checklist -> parity_red -> reopen -> green resume`。

## 网页可见落点
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`

其中前者是本轮主要 reader-facing 落点；后者同步了本轮最新 `TRADING DESK BOARD` 关联补充。

## 风险 / 边界
- 当前 candidate 仍用占位口径（例如 `future-crypto-live-challenger`），目的是把 operator 顺序模板写死，而不是暗示某条策略已经过审。
- 这张 sequence 表依赖前面已有的 v1 artifact；它本身不替代那些底层 checklist/sample row。
- 如果以后某些阈值（例如 `clock drift <= 60s`、`cost delta <= 25bps`）要改，应回到原 artifact 单独立项，而不是静默只改这张 sequence 表。

## 下一步建议
1. 若下一轮仍落到 `Run 3`，优先不要再写抽象 tiny-live 规则页；更值得做的是把这条 sequence 与 future 真正的 route/shadow ledger 对账动作再靠近一步。
2. 若 Scout Seat 出现 genuinely new local bar，则优先回去做 honest recheck，而不是无限补 plumbing 文档。
3. `breakout` 若要重开 Live Seat，仍必须先拿出 genuinely new blocker reduction，而不是复用旧 cached evidence。

## Commit hash
- HEAD：`8cba0d8`
- 本轮未提交。

## 如果未提交，原因
- 当前 worktree 仍有大量与本轮无关的既有脏文件与未跟踪文件；本轮继续只做 selective 改动，避免混提。
