# 2026-03-16 07:38 UTC｜small-live routing dry-run sample row：把第一条 green dry-run 回执压成同账本样例

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行当前 desk 顺序：

- `Run 1 / Paper Seat` 已在 `07:13 UTC` 实际执行过 guarded refresh，并如实回到 `waiting_not_due`；这轮不该继续重复 paper 守门。
- `Run 2 / Live Seat` 的 breakout 已在 `07:30 UTC` 完成 `bench` 的 reader-facing sync；当前没有新的 blocker reduction 证据，不值得继续同类 rerun。
- 因此这轮默认切到 `Run 3 / tiny-live plumbing`。

同时检查到：
- `Rank 1 τ-band` 的本地 artifact 时间仍停在 `03:53 UTC`；
- `Rank 2 combo_all` 的本地 artifact 仍停在 `05:15 UTC`；
- 当前没有“新 bar 已到、值得做 honest recheck”的证据。

所以这轮不去伪造 Scout 的新 forward 复核，而是沿 `small_live` 已在跑的执行链，认领 **1 个主点**：

**把 `routing dry-run` 从 checklist 再压成一条可复用的 green sample row。**

这比继续写抽象 live 规则页更接近 tiny-live 落地，因为它直接回答：
**如果 future run 真的去跑 venue dry-run，第一条合格的 ledger row 应该怎么写。**

## 本轮做了什么改动
### 1) 新增 `routing dry-run` 的 green sample row artifact
在 `scripts/build_alpha_closure_board_report.py` 中新增：

- `reports/artifacts/alpha_closure_board/small_live_routing_dry_run_sample_row_v1.csv`

当前样例固定了一条 **green / test-no-fill** 的 dry-run 回执，最小包含：
- `signal_bar_utc`
- `venue_mode=test/no-fill`
- `route_intent_ts_utc / route_ack_ts_utc / cancel_ts_utc`
- `ack_latency_ms`
- `intended_notional_usd`
- `cap_pct_total / cap_pct_sleeve / remaining_cap_pct`
- `intended_qty / rounded_qty / min_notional_check`
- `mismatch_status=green`
- `operator_action=cancel_after_ack`

这一步不是说 tiny-live 已可放行，而是把最前面的 `intent -> ack -> cancel` 合格回执，固定成 future 可复用的同账本模板。

### 2) 同步 reader-facing 页面
本轮同时更新：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

其中：
- `alpha_closure_board` 新增区块：`Routing dry-run sample row（v1）`
- `TODO / plans` 新增 `2026-03-16 07:38 UTC` 的 latest supplement，明确这是 **green dry-run row**，不是 live 承诺

## 为什么这一步有用
前面几轮已经把 `small_live` 主链压成：

1. `tiny-live plumbing board`
2. `live ledger template`
3. `routing dry-run checklist`
4. `paper-live shadow parity checklist`
5. `parity_red action ladder`
6. `parity_red sample row`
7. `reopen gate checklist`
8. `reopen resume sample row`

但还缺一个最前面的落地锚点：
**dry-run 真通过时，第一条“绿色回执行”怎么写。**

如果没有这条样例，future run 很容易只会在日志里写：
- “回执链通过了”
- “symbol / precision 没问题”

却没有一条标准 ledger row 可对照，最后又回到“规则写过了，但执行留痕不一致”的老问题。

这轮补完后，`small_live` 现在不只知道：
- 红旗时怎么写账；
- 重开后怎么写账；

也知道：
- **最前面的 green dry-run 应该怎么写账。**

## 最小验证
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py` ✅
2. `python3 scripts/build_alpha_closure_board_report.py` ✅
3. `python3 scripts/build_plans_site.py` ✅
4. `grep -n "Routing dry-run sample row（v1）\|small_live_routing_dry_run_sample_row_v1.csv" reports/site/factors/alpha_closure_board/report.html reports/site/plans/momentum_todo.html docs/TODO.md` ✅
5. `sed -n '1,3p' reports/artifacts/alpha_closure_board/small_live_routing_dry_run_sample_row_v1.csv` ✅

核对结果：
- 新 artifact 已生成；
- `alpha_closure_board` 本地 reader-facing 页面已出现新卡；
- `TODO / plans` 已出现 `2026-03-16 07:38 UTC` 补充；
- 样例行已固定 `venue_mode=test/no-fill` 与 `operator_action=cancel_after_ack`，避免被误读成真钱发送。

## 本轮 hard verdict
一句话结论：

**这轮把 `small_live` 最前面的 `routing dry-run` 也压成了一条 green sample row，让 future venue dry-run 不再只有 checklist，而有一条可直接对照的标准 ledger 行。**

证据支持这句话的方式是：
- 新 CSV artifact 已落地；
- `alpha_closure_board` 已新增 reader-facing 区块；
- `TODO / plans` 已同步本轮 supplement；
- 样例行明确停在 `test/no-fill`，没有偷渡 tiny-live 放行口径。

## 风险 / 边界
- 这仍然不是 tiny-live 放行，也不是任何真实下单。
- 这条 sample row 只是 **v1 ledger template example**，不是 venue 接通证明。
- 当前 candidate_id 用的是 `future-crypto-live-challenger` 占位口径，目的是避免误写成“某条当前策略已经获批上 live”。

## 下一步建议
1. 若下一轮继续落到 `Run 3`，优先考虑把 `routing dry-run sample row` 与现有 `live ledger template` 再压成一个更明确的 **operator 对账顺序**，但不要回头重写抽象规则页。
2. 若 Scout Seat 真出现新的 local bar，再优先回去做 honest recheck，而不是继续空补 plumbing 文档。
3. breakout 若要重开，仍必须先拿到 genuinely new blocker reduction，而不是复用旧 cached evidence 续命。

## Commit hash
- HEAD：`8cba0d8`
- 本轮未提交。

## 如果未提交，原因
- 当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件；本轮继续只做 selective 改动，避免混提。
