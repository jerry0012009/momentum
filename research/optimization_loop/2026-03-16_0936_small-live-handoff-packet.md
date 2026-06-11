# 2026-03-16 09:36 UTC｜small-live operator handoff packet：把 Run 3 常见 review 场景压成开工启动包

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- **Run 1 / Paper Seat**：`EMA` 早前已完成 guarded refresh，并如实回到 `waiting_not_due`；当前没有新的 `due-now / overdue` paper 动作。
- **Run 2 / Scout Seat**：本轮先核对 `Rank 3 third_touch_plus_ema_macd` 是否已有 genuinely new local bar 可做 honest continuity；结果确认共享 Binance `15m` cache 三个币种（`BTCUSDT / ETHUSDT / SOLUSDT`）最新 completed bar 仍都只到 `2026-03-16 09:15 UTC`，没有新的 completed 15m bar。
- 因此这轮不能伪造 Scout continuity，也不该回头重做 `Rank 1 / Rank 2` 旧样本近义续切；按板上规则如实回退到 **Run 3 / tiny-live plumbing**。

结合最近几轮 tiny-live 子链，当前已经落下：
1. `routing dry-run checklist`
2. `routing dry-run green sample row`
3. `shadow parity checklist`
4. `green shadow parity row`
5. `parity_red action ladder + red sample row`
6. `reopen gate`
7. `green resume row`
8. `operator reconciliation sequence`

现在最实际的缺口不是再补抽象规则，而是：

**future run 真要开始一次 venue/shadow review 时，operator 到底该先开哪几张 artifact、目标写哪条 row、什么情况下必须立刻停手。**

所以本轮只认领 1 个主点：
- **主点**：新增 `small_live operator handoff packet v1`
- **紧邻子点**：把它同步到 `alpha_closure_board` 与 `TODO / plans`，让 reader-facing 页面也能直接看到这次 fallback 产物

## 本轮做了什么改动
### 1）新增 `small_live_operator_handoff_packet_v1.csv`
修改：`scripts/build_alpha_closure_board_report.py`

新增 artifact：
- `reports/artifacts/alpha_closure_board/small_live_operator_handoff_packet_v1.csv`

这张卡不是发明新 tiny-live 规则，而是把已有 v1 artifact 压成 4 个最常见的开工场景：

1. **准备启动新的 venue / route review**
   - 先开：`routing_dry_run_checklist + routing_dry_run_sample_row + live_ledger_template`
   - 目标：先确认 receipt chain 与 ledger 主键字段齐，再决定能否从 `dry_run` 往 `shadow parity` 走
2. **dry-run 已干净，准备核对 paper vs live-shadow**
   - 先开：`shadow_parity_checklist + green_shadow_parity_sample_row`
   - 目标：一次核对 qty rounding、cap、price snapshot、cost snapshot，过关才写 green parity row
3. **shadow parity 出现 red，需要冻结并等待重开**
   - 先开：`parity_red_action_ladder + red_sample_row + reopen_gate`
   - 目标：把 red 变成清楚的 `hold / freeze review / reopen_earliest_ts`，而不是只留在日志里
4. **red cause 已关闭，准备恢复 shadow review**
   - 先开：`reopen_gate + reopen_resume_sample_row + operator_reconciliation_sequence`
   - 目标：把恢复动作接回同一条审计链，明确写出 `prior_red_ref_id`

### 2）同步 reader-facing 页面
本轮同步更新：
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- 首页 index（`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`）

其中：
- `alpha_closure_board` 新增区块：`Small-live operator handoff packet（v1）`
- `TODO` 顶部新增 `2026-03-16 09:36 UTC` desk 补充，明确说明：本轮先核对过 `Rank 3`，但因为没有 genuinely new local bar，所以如实回退到 `Run 3`

## 为什么这一步有用
前几轮 tiny-live 已经有不少 checklist / sample row / sequence，但 future operator 真开工时，仍然容易卡在：
- 不知道这次该先开哪几张卡
- 知道要对账，但不知道这次目标应该写 green row 还是 red row
- 知道 red 之后要重开，但没有把 `prior_red_ref_id` 接回同一条链

这张 handoff packet 的价值是把“资料齐了”进一步压成“开工入口也齐了”：

- 减少 future run 在多张 CSV / 页面之间来回找的摩擦
- 把每种 review 场景对应的目标 writeback 固定下来
- 把必须立即停手的条件写死，避免 tiny-live review 被口头推进

更直白地说：

**它让 Run 3 不只是有很多零散卡片，而是开始有了‘这次开工先拿哪几张、最终该写哪条 row’的启动包。**

## 最小验证
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py` ✅
2. `python3 scripts/build_alpha_closure_board_report.py` ✅
3. `python3 scripts/build_plans_site.py` ✅
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ✅
5. `grep -n "Small-live operator handoff packet（v1）\|small_live_operator_handoff_packet_v1.csv\|2026-03-16 09:36 UTC" reports/site/factors/alpha_closure_board/report.html reports/site/plans/momentum_todo.html docs/TODO.md` ✅
6. `sed -n '1,6p' reports/artifacts/alpha_closure_board/small_live_operator_handoff_packet_v1.csv` ✅
7. 额外核对 Scout fallback 前提：读取共享 cache 末端时间，确认 `BTCUSDT / ETHUSDT / SOLUSDT` 最新 completed bar 仍都为 `2026-03-16 09:15 UTC` ✅

核对结果：
- 新 artifact 已生成；
- `alpha_closure_board` 已出现新卡；
- `TODO / plans` 已同步 `09:36 UTC` 的 fallback 回执；
- shared cache 末端确实没有新 completed 15m bar，因此本轮回退到 `Run 3` 是诚实动作，不是借口。

## 本轮 hard verdict
一句话结论：

**这轮先确认了 `Rank 3` 没有 genuinely new local bar，因此没有伪造 Scout continuity；随后如实回退到 `Run 3`，把 tiny-live 现有卡片再压成一张 `operator handoff packet`，让 future venue/shadow review 不只“资料齐”，而是“开工入口也齐”。**

证据如何支持这句话：
- 共享 Binance `15m` cache 三个币种的最新 completed bar 均仍停在 `09:15 UTC`；
- 新 `small_live_operator_handoff_packet_v1.csv` 已落地；
- `alpha_closure_board`、`TODO / plans` 与首页索引都已同步外显。

## 风险 / 边界
- 这仍然不是 tiny-live 放行，也不是任何真实下单。
- 这张 handoff packet 复用的是已有 v1 artifact；它本身不替代底层 checklist / sample row / sequence。
- 当前只是把 operator 启动摩擦再压低一层，还没有真正接到实盘 venue 的 live routing。

## 下一步建议
1. 若下一轮 `EMA` 仍是 `waiting_not_due` 且 Scout 仍无 genuinely new local bar，优先沿这张 handoff bundle 再补一格更贴近 future venue review 的执行卡，而不是回头重复旧 Scout 样本续切。
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
