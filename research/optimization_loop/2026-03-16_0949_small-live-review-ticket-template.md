# 2026-03-16 09:49 UTC｜small-live review ticket template：把 handoff bundle 再压成可复用的关单模板

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- **Run 1 / Paper Seat**：`EMA` 早前已完成 guarded refresh，并如实回到 `waiting_not_due`；当前没有新的 `due-now / overdue` paper 动作。
- **Run 2 / Scout Seat**：本轮再次先核对 `Rank 3 third_touch_plus_ema_macd` 是否已有 genuinely new local bar；结果确认共享 Binance `15m` cache 的 `BTCUSDT / ETHUSDT / SOLUSDT` 最新 completed bar 仍都只到 `2026-03-16 09:15 UTC`。
- 因此本轮依旧**没有**合规的 Scout continuity 可做，也不该回头重做旧样本的近义续切；按 desk 规则继续如实回退到 **Run 3 / tiny-live plumbing**。

紧接上一轮刚落下的 `small_live operator handoff packet v1`，当前最贴近 future venue review 的缺口已经不是“再解释一遍要开哪些卡”，而是：

**当 operator 真要开一张 dry-run / parity / red-freeze / resume review 时，这张 review ticket 至少要绑定哪些 ref、成功时怎么关单、失败时必须怎样收口。**

所以本轮只认领 1 个主点：
- **主点**：新增 `small_live review ticket template v1`
- **紧邻子点**：把它同步到 `alpha_closure_board` 与 `TODO / plans`，让 reader-facing 页面也能直接看到这次 fallback 产物

## 本轮做了什么改动
### 1）新增 `small_live_review_ticket_template_v1.csv`
修改：`scripts/build_alpha_closure_board_report.py`

新增 artifact：
- `reports/artifacts/alpha_closure_board/small_live_review_ticket_template_v1.csv`

这张卡不是再写一份抽象 live 规则，而是把 handoff bundle 再往前压成 4 类可复用的 review ticket closeout 模板：

1. **新的 venue / route dry-run review**
   - ticket stub：`SL-DRYRUN-<candidate>-<yyyymmddhhmm>`
   - 至少绑定：`candidate_id / deployment_scope`、白名单快照、ledger 主键字段、`intent -> ack -> cancel` receipt ref
   - 成功关单：绑定 1 条 green dry-run row，并明确写成 `dry_run_pass -> eligible_for_shadow_parity_review`
   - 失败收口：若 ack/cancel 缺失、clock drift 超阈值或 candidate/scope 对不上，只能关成 `dry_run_only / blocked`
2. **paper vs live-shadow parity review**
   - ticket stub：`SL-PARITY-<paper_ref>-<yyyymmddhhmm>`
   - 至少绑定：`paper_ref_id`、`live_shadow_ref_id`、shadow price snapshot、qty rounding / cap snapshot、parity checklist ref
   - 成功关单：绑定 1 条 `mismatch_status=green` 的 shadow parity row，并写成 `continue_shadow_review`
   - 失败收口：任一 `rounded_qty / cost / clock / whitelist` 不合格，就必须关成 `parity_red / freeze_review`
3. **parity_red 冻结 / reopen 准备 review**
   - ticket stub：`SL-RED-<candidate>-<yyyymmddhhmm>`
   - 至少绑定：prior red row、`trigger_reason`、`reopen_earliest_ts`、root-cause evidence ref、reopen gate checklist ref
   - 成功关单：显式留下 `freeze_review_with_reopen_gate` 与 reopen 所需补件列表
   - 失败收口：如果 red 只有日志没有 ledger writeback，继续 `paper_only / blocked`
4. **red cause 已关闭，恢复 shadow review**
   - ticket stub：`SL-RESUME-<prior_red_ref>-<yyyymmddhhmm>`
   - 至少绑定：`prior_red_ref_id`、reopen gate pass ref、最新 dry-run receipt ref、green resume row / reconciliation sequence ref
   - 成功关单：绑定 1 条带 `prior_red_ref_id` 的 green resume row，并写成 `resume_shadow_review`
   - 失败收口：如果 `prior_red_ref_id` 缺失、receipt 没重走、或新的 qty/cost parity 仍未过关，就继续 `freeze_review`

### 2）同步 reader-facing 页面
本轮同步更新：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- 首页 index（`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`）

其中：
- `alpha_closure_board` 新增区块：`Small-live review ticket template（v1）`
- `TODO` 顶部新增 `2026-03-16 09:49 UTC` 的 desk 补充，明确说明：本轮再次先核对过 `Run 2`，但因为 shared cache 最新 completed bar 仍停在 `09:15 UTC`，所以继续如实回退到 `Run 3`

## 为什么这一步有用
上一轮的 `handoff packet` 已经回答了“先开哪几张 artifact”。
本轮补的是更接近真实开工的一层：

- future operator 不只知道该开哪几张卡，还知道**这张 review ticket 自己至少要绑哪些 ref**
- review 结束时不再只留下口头结论，而是知道**必须怎样 closeout 才算可审计**
- 失败时也不再只是“先 hold 一下”，而是固定成 `blocked / freeze_review / paper_only` 之类可复用的关单语义

更直白地说：

**它把 tiny-live fallback 从“有手册、有启动包”再推进到“有 review ticket 模板和关单模板”，更接近 future venue/shadow review 真开工时会用到的执行颗粒度。**

## 最小验证
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py` ✅
2. `python3 scripts/build_alpha_closure_board_report.py` ✅
3. `python3 scripts/build_plans_site.py` ✅
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ✅
5. 读取共享 Binance `15m` cache 末端时间，确认 `BTCUSDT / ETHUSDT / SOLUSDT` 最新 completed bar 仍都为 `2026-03-16 09:15 UTC` ✅
6. `grep -n "09:49 UTC\|small_live_review_ticket_template_v1.csv" docs/TODO.md reports/site/plans/momentum_todo.html reports/site/factors/alpha_closure_board/report.html` ✅
7. `head -5 reports/artifacts/alpha_closure_board/small_live_review_ticket_template_v1.csv` ✅

核对结果：
- shared cache 末端确实仍停在 `09:15 UTC`，所以本轮继续回退到 `Run 3` 是诚实动作；
- 新 artifact 已生成；
- `alpha_closure_board`、`TODO / plans` 与首页索引都已同步外显。

## 本轮 hard verdict
一句话结论：

**这轮再次确认 `Scout Seat` 没有 genuinely new local bar，因此没有伪造 continuity；随后继续如实回退到 `Run 3`，把 tiny-live fallback 从 handoff bundle 再推进到一张可复用的 `review ticket / closeout` 模板。**

证据如何支持这句话：
- 共享 Binance `15m` cache 三个币种的最新 completed bar 仍都停在 `09:15 UTC`；
- 新 `small_live_review_ticket_template_v1.csv` 已落地；
- `alpha_closure_board`、`TODO / plans` 与首页可见落点都已同步。

## 风险 / 边界
- 这仍然不是 tiny-live 放行，也不是任何真实下单。
- 这张 ticket template 复用的是已有 `handoff / checklist / sample row / reopen` artifact；它本身不替代底层规则。
- 当前只是把 future venue/shadow review 的开工与关单语义再压实一层，还没有接到真实交易所 routing。

## 下一步建议
1. 若下一轮 `EMA` 仍是 `waiting_not_due` 且 Scout 仍无 genuinely new local bar，优先继续补 tiny-live fallback 中最贴近实际 venue review 的 `closeout / ticket writeback / operator handoff` 级 artifact。
2. 一旦 `Rank 3 third_touch_plus_ema_macd` 出现 genuinely new completed 15m bar，优先回到 `Run 2` 做 honest continuity。
3. `breakout` 继续按 `bench / recheck-only` 处理；没有 genuinely new blocker reduction 前，不应重开 heavy rerun。

## 网页可见落点
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页：`https://jp.jerrypsy.top/momentum/`

## Commit hash
- HEAD：`573439c`
- 本轮未提交。

## 如果未提交，原因
当前 worktree 仍有大量与本轮无关的既有脏文件与未跟踪文件；本轮继续只做 selective 改动与页面刷新，避免混提。
