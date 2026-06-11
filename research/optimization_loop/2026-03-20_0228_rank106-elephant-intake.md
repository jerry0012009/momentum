# 2026-03-20 02:28 UTC — Rank 106 elephant candle corridor source intake（guard-passed）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前无 `due-now / overdue` lane
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`（约 `4.6h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 `Next 3`，本轮主资源必须转到 `Scout Seat`。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1632`
- 最近 optimization logs：
  - `2026-03-20_0220_rank105-clean-replication-park.md`
  - `2026-03-20_0202_rank105-body-zone-intake.md`
  - `2026-03-20_0149_rank104-clean-replication-park.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 上轮已把 `Rank 105` 压回 `park / evidence pool`

## Active Scout 候选边际比较（先比较后认领）
1. **elephant candle corridor long-bias gate（fresh repo reserve）**
   - 上轮 `Rank 105` 已收口，当前是最靠前且可立刻推进的 fresh intake。
2. **MTF CHOP charged-up count**
   - 仍是后备 fresh intake，优先级低于 elephant。
3. **prebreak higher-low pressure ladder context gate**
   - 仍是后置 context backlog。
4. **旧 evidence_pool / P3 continuity / tiny-live plumbing**
   - 当前都不该抢主资源位。

结论：本轮只认领 elephant 这一条，不并开其他候选。

## 本轮认领
- 主点：`elephant candle corridor long-bias gate`
- 紧邻子点：正式编号 + source intake card + reader-facing 页面 + 顶板顺序同步

## 本轮动作
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，把该线正式冻结为：
  - **`Rank 106 / elephant candle corridor long-bias gate`**
- 完成 `source intake + 两条轻量诚实守门`：
  1. `trade on / trade off`
     - `trade on`：它只做确认 bar 质量门（`body_ratio>=0.5`、`body>prev_range`、`body>0.8*ATR14`、`full_range<3.5*ATR14`），默认先用于 `Fib retest_long / EMA continuation long`。
     - `trade off`：若 short-side 没改善或只靠极端缩样本，不得包装成 breakout-short shared gate。
  2. `lookahead / repaint / leakage`
     - 条件必须只用 signal 当根及之前数据；
     - 下一轮 clean replication 强制 `next-bar open + no-overlap`；
     - 只比较 `baseline / body_only / full_corridor` 三臂，禁止 future path 倒灌与阈值事后重配。

## 当前硬结论
**`Rank 106 = guard-passed / admit_to_clean_replication_queue`**。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/literature/scout_rank106_elephant_candle_corridor_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank106_elephant_candle_corridor_source_intake.html`

## 对顶板的直接影响
- `Paper Seat = EMA / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 当前主资源位更新为：`Rank 106 / elephant candle corridor long-bias gate`
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 106 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 106 hard-fail / exhausted，则切 MTF CHOP charged-up count source intake；仅当 fresh source 也 exhausted，才继续回退 prebreak ladder > 旧 evidence_pool > P3 continuity > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 回读确认：
  - `reports/artifacts/literature/scout_rank106_elephant_candle_corridor_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank106_elephant_candle_corridor_source_intake.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 clean replication 或 Light Stability Pack（遵守 1 主点 + 1 紧邻子点约束）
- 工作区仍有大量无关脏文件；本轮未尝试混提
