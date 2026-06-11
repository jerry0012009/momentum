# 2026-03-16 08:17 UTC｜small-live green shadow parity row：把正常通过的第一条 shadow ledger 行补齐

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行当前 desk 顺序：

- **Run 1 / Paper Seat**：`EMA` 已在 `07:13 UTC` 实际执行过 guarded refresh，并如实回到 `waiting_not_due`；当前没有新的 `due-now / overdue` lane，不该继续重复 paper 守门。
- **Run 2 / Live Seat**：`breakout` 已完成 `bench` 的 reader-facing sync；当前没有 genuinely new `pure-test / down-tail` blocker reduction，不值得继续同类 rerun。
- 因此本轮默认切到 **Run 3 / tiny-live plumbing 或 Scout Seat**。

结合最近几轮实际落点判断：
- `Scout Seat` 上一轮已经把 `Rank 3 third-touch + EMA/MACD` 压成了 `implementation-ready spec`；
- `small_live` 执行链则已经依次补到了：
  - `routing dry-run checklist`
  - `routing dry-run green row`
  - `shadow parity checklist`
  - `parity_red action ladder`
  - `parity_red sample row`
  - `reopen gate`
  - `reopen resume row`
  - `operator reconciliation sequence`

这时最明显的缺口已经不是再写抽象规则，而是：

**当前链条里有 dry-run 的 green row、有 parity_red row、也有 reopen 后的 green resume row，但还缺“正常通过的第一条 green shadow parity row”。**

所以本轮只认领 1 个主点 + 1 个紧邻子点：
- **主点**：新增 `green shadow parity sample row v1`
- **紧邻子点**：把它同步挂到 `alpha_closure_board` 与 `TODO / plans`

## 本轮做了什么改动
### 1）新增 green shadow parity 样例行 artifact
修改：`scripts/build_alpha_closure_board_report.py`

新增 artifact：
- `reports/artifacts/alpha_closure_board/small_live_green_shadow_parity_sample_row_v1.csv`

当前样例行固定的是：
- `stage_status=shadow_parity`
- `mismatch_status=green`
- `mismatch_reason=none`
- `operator_action=continue_shadow_review`
- 仍停在 `shadow review`，**不是** tiny-live 放行

同时把最小必留字段一次写死：
- `paper_ref_id / live_shadow_ref_id`
- `research_symbol / venue_symbol / side`
- `intended_qty / rounded_qty / min_notional_check`
- `shadow_price / cost_estimate_bps`
- `cap_pct_total / cap_pct_sleeve / remaining_cap_pct`
- `trigger_reason=shadow_parity_pass`
- `operator_note`

它回答的问题很具体：

**当 `paper_ref -> live_shadow_ref` 的 payload、qty rounding、cap、成本快照都过关时，账本里的第一条 green parity 行应该长什么样。**

### 2）同步 reader-facing 页面
本轮同步更新：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- 首页 index（`bash scripts/publish_homepage_index.sh`）

当前 reader-facing 新增区块：
- `Green shadow parity sample row（v1）`

同步后的外显口径保持收敛：

**这不是 tiny-live 放行，也不是说某条候选已获批上实盘；它只是把“shadow parity 正常通过时，继续 shadow review 的那一条 green ledger row”固定成模板。**

## 为什么这一步有用
到这轮之前，`small_live` 子链已经把：
- 失败时怎么写（`parity_red row`）
- 失败后如何重开（`reopen gate`）
- 重开后第一条恢复行怎么写（`green resume row`）

都补齐了。

但如果**正常第一次就通过**，future run 仍然缺一个标准答案：
- 到底写哪几个字段？
- 当前只该继续 `shadow review`，还是已经被误读成 tiny-live？
- 何时只是 green parity，何时才谈得到真钱发送？

这轮补完后，`small_live` 链条终于同时覆盖了：
1. `dry-run green row`
2. `green shadow parity row`
3. `parity_red row`
4. `reopen gate`
5. `reopen 后 green resume row`
6. `operator reconciliation sequence`

也就是说，future run 不再只有“红了怎么办”的模板，也有了“正常通过时怎么诚实落账”的模板。

## 最小验证
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py` ✅
2. `python3 scripts/build_alpha_closure_board_report.py` ✅
3. `python3 scripts/build_plans_site.py` ✅
4. `bash scripts/publish_homepage_index.sh` ✅
5. `grep -n "Green shadow parity sample row（v1）\|small_live_green_shadow_parity_sample_row_v1.csv" reports/site/factors/alpha_closure_board/report.html reports/site/plans/momentum_todo.html docs/TODO.md` ✅
6. `sed -n '1,3p' reports/artifacts/alpha_closure_board/small_live_green_shadow_parity_sample_row_v1.csv` ✅

已确认：
- 新 artifact 已生成；
- `alpha_closure_board` 本地 reader-facing 页面已出现新卡；
- `TODO / plans` 已同步 `2026-03-16 08:17 UTC` 的最新补充；
- 首页 index 已刷新；
- green row 明确停在 `shadow review`，没有偷渡成 tiny-live 放行。

## 本轮 hard verdict
一句话结论：

**这轮把 `small_live` 执行链里原先缺的一格——“正常通过的 green shadow parity row”——补成了标准样例，因此 future run 现在不只知道红旗时怎么写账，也知道 shadow parity 正常过关时该怎样诚实落账。**

证据如何支持这句话：
- 新 CSV artifact 已落地；
- `alpha_closure_board` 已新增对应 reader-facing 区块；
- `TODO / plans` 已同步外显；
- 样例明确写成 `continue_shadow_review`，而不是模糊写成 “ready/live”。

## 风险 / 边界
- 这仍然不是 tiny-live 放行，也不是任何真实下单。
- 当前 `candidate_id` 继续用占位口径 `future-crypto-live-challenger`，目的是避免误导成“某条现有候选已经获批上实盘”。
- 这条样例行回答的是 **green shadow parity**，不是 tiny-live pilot 的真实订单字段；后者仍需在未来真实 seat 通过更多前置条件后再单独落账。

## 下一步建议
1. 若后续轮次继续落到 `Run 3 / tiny-live plumbing`，优先不要回头重写抽象 live 原则页；更值得做的是把现有模板进一步贴近 future 真正的 route/shadow ledger 对账顺序。
2. 若 `Scout Seat` 出现 genuinely new local bar，则优先回去做 honest recheck / first verdict，而不是无限连续补 plumbing 文档。
3. 若未来某条候选真要争取 tiny-live review，应优先复用这套 `dry-run green -> green shadow -> red/reopen -> resume` 的同账本模板，而不是另起一套字段。 

## 网页可见落点
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页已通过 `publish_homepage_index.sh` 刷新

## Commit hash
- HEAD：`300b0c2`
- 本轮未提交。

## 如果未提交，原因
- 当前工作区仍有大量与本轮无关的既有脏文件与未跟踪文件；本轮继续只做 selective 改动与页面刷新，避免混提。
