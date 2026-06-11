# 2026-03-20 02:54 UTC — Rank 107 MTF CHOP charged-up count source intake（guard-passed）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前无 `due-now / overdue` lane
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`（约 `4.1h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 `Next 3`，本轮主资源必须继续留在 `Scout Seat`。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1641`
- 最近 optimization logs：
  - `2026-03-20_0231_rank106-clean-replication-park.md`
  - `2026-03-20_0228_rank106-elephant-intake.md`
  - `2026-03-20_0220_rank105-clean-replication-park.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 上轮已把 `Rank 106` 压回 `park / evidence pool`

## Active Scout 候选边际比较（先比较后认领）
1. **MTF CHOP charged-up count（fresh repo reserve）**
   - `Rank 106` 已收口为 `park` 后，这条是当前最靠前且最直接服务主线的 fresh intake。
   - 它不是再扩一条新 alpha，而是最快回答：`Fib retest_hold / EMA continuation long` 是否该先避开多周期 CHOP 同时抬高的高噪声窗口。
2. **prebreak higher-low pressure ladder context gate**
   - 仍是后置 context backlog，优先级低于 MTF CHOP 的 queue-facing intake。
3. **fresh paper / repo intake reserve（7.10）**
   - 只在当前 backlog 也 exhausted 时才切过去。
4. **旧 evidence_pool / P3 continuity / tiny-live plumbing**
   - 当前都不该抢主资源位。

结论：本轮只认领 `MTF CHOP charged-up count` 这一条，不并开其他候选。

## 本轮认领
- 主点：`MTF CHOP charged-up count`
- 紧邻子点：正式编号 + source intake card + reader-facing 页面 + 顶板顺序同步

## 本轮动作
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，把该线正式冻结为：
  - **`Rank 107 / MTF CHOP charged-up count`**
- 完成 `source intake + 两条轻量诚实守门`：
  1. `trade on / trade off`
     - `trade on`：它不单独开仓，只做 veto / size-down 风险覆盖层；默认先服务 `Fib retest_hold long` 与 `EMA continuation long`。
     - 最小冻结口径：在 `15m / 30m / 60m` 上分别计算 `CHOP(14)`，若 `charged_count>=2`（例如 `CHOP>=61.8` 的 TF 数达到 `2` 个及以上），则 long-side retest / continuation 默认不放行，或最多降到 `0.5x`。
     - `trade off`：若 breakout-short follow-up 上看不到稳定改善，不得把它硬包装成 shared admission gate；若证据只支持 long-side veto，也不得偷渡成多空对称万能过滤器。
  2. `lookahead / repaint / leakage`
     - 原仓库 `request.security(..., lookahead=barmerge.lookahead_on)` 有前视风险，不能原样抄；desk clean-room 必须统一改成 `lookahead_off / 右侧对齐`。
     - 条件必须只用 signal 当根及之前数据；下一轮 clean replication 强制 `next-bar open + no-overlap`。
     - 第一轮 replication 只允许比较 `baseline / charged_count>=2 hard veto / charged_count>=2 size-down` 三臂，禁止 future CHOP 状态、future bar path 与阈值事后重配倒灌。

## 当前硬结论
**`Rank 107 = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：先把它当“别在多周期一起变糊的时候硬做 long retest / continuation”的便宜 veto 层，而不是新的独立 alpha。它当前最像的是 long-side anti-chop gate，不是 breakout-short 的统一放行键。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/literature/scout_rank107_mtf_chop_chargedup_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank107_mtf_chop_chargedup_source_intake.html`

## 对顶板的直接影响
- `Paper Seat = EMA / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 当前主资源位更新为：`Rank 107 / MTF CHOP charged-up count`
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 107 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 107 hard-fail / exhausted，则切 prebreak higher-low pressure ladder context gate 的 source intake；若这条 fresh backlog 也 exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 回读确认：
  - `reports/artifacts/literature/scout_rank107_mtf_chop_chargedup_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank107_mtf_chop_chargedup_source_intake.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 clean replication 或 Light Stability Pack（遵守 1 主点 + 1 紧邻子点约束）
- `Rank 17` 虽有 hosted paper sidecar 事件，但当前仍只保留为低频 fallback，不改写默认 seat
- 工作区仍有大量无关脏文件；本轮未尝试混提
