# 2026-03-16 03:14 UTC｜tiny-live plumbing board：把 small-live 从抽象 gate 压成可执行 operator 栏位

## 为什么这轮切到 Run 3
- 先按要求检查了 repo 状态、`docs/TODO.md` 顶部 `TRADING DESK BOARD`、最近几轮 optimization logs、当前脏文件与席位状态。
- **Run 1 / Paper Seat（EMA）**：仍被真实 close waiting-window 挡住。`scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 的最近守门结果显示，A 股日频 lane 还在等下一次 completed bar，当前不能伪造 refresh / week-1 review。
- **Run 2 / Live Seat（breakout）**：最近一次 heavy rerun 刚在 `2026-03-15 23:25 UTC` 完成，而 `breakout rerun guard` 最新已收紧成 `cache_advanced_but_recent_recheck_cooldown_hold`；当前继续重跑只会撞 cooldown，不会新增 overturn `one_more_gate` 的更硬证据。
- 因此这轮按板上顺序自动切到 **Run 3**，优先做一刀与 `paper -> tiny-live` 直接相关、且不依赖新 market bar 的 **plumbing artifact**。

## 本轮主点
- 主点：**项目级 tiny-live plumbing board v1**
- 紧邻子点：把这张板子同步挂到 `alpha_closure_board` 与 `TODO/plans`，避免只留在脚本或口头规则里。

## 做了什么
1. 修改 `scripts/build_alpha_closure_board_report.py`
   - 新增 artifact 输出：
     - `reports/artifacts/alpha_closure_board/small_live_plumbing_v1.csv`
   - 新增网页区块：
     - `Tiny-live plumbing board（v1）`
   - 把已有的项目级 `promotion gate v1` 再往执行层压了一层，固定住：
     - `routing dry-run / symbol whitelist lock`
     - `paper-live shadow parity`
     - `tiny-live pilot start`
     - `rollback / re-entry`

2. 更新 `docs/TODO.md`
   - 在项目级 `paper trading -> 小资金实盘` promotion gate 条目下新增 `2026-03-16 03:13 UTC` 补充。
   - 把本轮价值明确写成：不是更激进地“催上 live”，而是把 future Step 5 真放行前必须先过的 operator 栏位固定下来。

3. 重建可见页面
   - `python3 scripts/build_alpha_closure_board_report.py`
   - `python3 scripts/build_plans_site.py`

## 新 artifact 的核心读法
### 1) Routing dry-run / symbol whitelist lock
- 真实资金仍为 `0`。
- 先验证目标 venue 的 symbol mapping、最小下单单位、时钟同步。
- 同一条信号必须先有 `intent -> route_ack -> cancel/close_ack` 三段回执；缺任一段就不允许进入 tiny-live。

### 2) Paper-live shadow parity
- 继续 `0` 真资金。
- 每条 paper 信号都生成一条 live-shadow payload，检查：
  - price source
  - qty rounding
  - venue precision
  - pair whitelist
- 若 live-shadow 与 paper 偏离超过 `1 bar` 或同笔预估成本偏离超过 `25bps`，标记 `parity_red`。

### 3) Tiny-live pilot start
- 资金上限继续严格沿用已有项目级硬规则：
  - 单候选 `<= 总可部署资金 1%`
  - 且 `<= sleeve 10%`
  - 单 symbol / pair `<= pilot capital 50%`
- 每笔 live 必须和 paper row 成对记账，新增：
  - `live_order_id`
  - `fill_price`
  - `fill_qty`
  - `slippage_bps`
  - `remaining_cap`
  - `mismatch_status`
- 若 live 与 paper 同步路径偏离超过 `5pp`，或出现未解释滑点超过 `50bps`，直接按 execution mismatch 处理。

### 4) Rollback / re-entry
- kill switch 后立即回到 `paper only`，真实资金归零。
- rollback 行必须落表记录：
  - `trigger_reason`
  - `trigger_ts`
  - `exposure_zeroed_ts`
  - `reopen_earliest_ts`
  - `operator_note`
- 修复后也必须重新走 `dry-run -> shadow parity`，不能直接偷跳回 live。

## 为什么这刀对当前席位有价值
- 它没有假装 EMA / breakout 已经能上 live；席位判断并没有被偷改。
- 但它确实把 **项目级 live bridge** 往前推了一步：
  - 之前更多是抽象 gate（什么时候“允许讨论 live”）；
  - 现在多了一张 **operator 可执行的 plumbing board**（真正开始前要先检查什么、落什么字段、何时直接 kill / rollback）。
- 对当前 desk 更诚实的说法是：
  - **EMA** 仍先继续等真实 close，沿同一张 paper ledger 续写；
  - **breakout** 仍先过 `one_more_gate`；
  - 但一旦未来任一候选真的拿到 Step 5 资格，现在已经有一张可复用的 tiny-live 底板，而不是临时拼接执行规则。

## 验证
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- 额外核对：
  - `reports/artifacts/alpha_closure_board/small_live_plumbing_v1.csv` 已生成
  - `reports/site/factors/alpha_closure_board/report.html` 已出现 `Tiny-live plumbing board（v1）`
  - `reports/site/plans/momentum_todo.html` 已同步本轮 TODO 更新

## 这轮没有做什么
- 没有伪造 EMA 的新 refresh / week-1 review。
- 没有在 breakout rerun cooldown 窗口里重复做同类 heavy rerun。
- 没有改写当前席位判断：EMA 仍是 closest to paper，breakout 仍是 one_more_gate。

## git / hygiene
- `git status --short` 显示 worktree 存在大量与本轮无关的既有脏改 / 未跟踪文件；本轮只安全地补了：
  - `scripts/build_alpha_closure_board_report.py`
  - `docs/TODO.md`
  - 以及随之重建的相关 site/artifact 页面
- **未提交 git。** 原因：当前工作区远不干净，不适合把本轮与历史脏改混提。

## Commit hash
- HEAD：`7a538cd`
- 本轮未提交。

## 下一刀默认
1. **Paper Seat**：等 A 股日频真实 close 到点后，继续优先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，沿同一张 live ledger 真续写。
2. **Live Seat**：等 breakout 当前 rerun cooldown 走完后，若 cache 仍领先，再做一次 heavy rerun 检查是否出现真正 overturn `one_more_gate` 的 forward 证据。
3. **Run 3 这条 tiny-live 线**：未来若任一候选拿到 live review 资格，默认先按 `small_live_plumbing_v1.csv` 做 `dry-run -> shadow parity -> tiny-live`，而不是现场临时拼规则。
