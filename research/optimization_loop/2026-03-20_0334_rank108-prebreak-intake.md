# 2026-03-20 03:34 UTC — Rank 108 prebreak higher-low pressure ladder context gate source intake（guard-passed）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前无 `due-now / overdue` lane
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`（约 `3.4h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 `Next 3`，本轮主资源必须继续留在 `Scout Seat`。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1652`
- 最近 optimization logs：
  - `2026-03-20_0312_rank107-clean-replication-park.md`
  - `2026-03-20_0254_rank107-mtf-chop-intake.md`
  - `2026-03-20_0231_rank106-clean-replication-park.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 上轮已把 `Rank 107` 压回 `park / evidence pool`

## Active Scout 候选边际比较（先比较后认领）
1. **prebreak higher-low pressure ladder context gate（fresh repo context candidate）**
   - `Rank 107` 已收口后，这条是当前最靠前且最直接服务三条主线共同“回踩前结构背景”问题的 fresh intake。
   - 它的价值不是再造一个 breakout 硬门，而是更快回答：pre-break 的 higher-low ladder 到底只是背景分层，还是能和 retest quality 组合成诚实 gate。
2. **HTF premium/discount long-bias context gate**
   - 仍是紧邻 fresh repo reserve；但当前更偏 long-side asymmetric context，shared 覆盖面不如 prebreak ladder。
3. **fresh paper / repo intake reserve（7.10）**
   - 只在当前 backlog 也 exhausted 时才切过去。
4. **旧 evidence_pool / Rank 17 低频 health-check fallback / tiny-live plumbing**
   - 当前都不该抢主资源位。

结论：本轮只认领 `prebreak higher-low pressure ladder context gate` 这一条，不并开其他候选。

## 本轮认领
- 主点：`prebreak higher-low pressure ladder context gate`
- 紧邻子点：正式编号 + source intake card + reader-facing 页面 + 顶板顺序同步

## 本轮动作
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，把该线正式冻结为：
  - **`Rank 108 / prebreak higher-low pressure ladder context gate`**
- 完成 `source intake + 两条轻量诚实守门`：
  1. `trade on / trade off`
     - `trade on`：它不单独开仓，只做 context gate；首轮只回答 pre-break 是否已有 `higher-low ladder`（过去约 `16` 根内 swing low 连续抬高步数 `>=2`），以及这层背景是否必须与 `retest candle quality`（如 `close>=level` 且 `body_ratio<=0.30`）组合后才值得放行。
     - 默认先服务 `Fib retest_hold / EMA continuation`；对 `breakout-short` 最多保留 short-veto / size-down 先验，不把它写成 mandatory shared gate。
     - `trade off`：若 ladder 单独使用仍只是 pocket-level 改善、或收益只靠极端缩样本，不得包装成硬 admission gate；若 short 侧没有一致帮助，也不得偷渡成多空对称 shared filter。
  2. `lookahead / repaint / leakage`
     - `swing low`、`ladder_score`、`small-body quality` 都必须只用 signal 当根及之前数据；
     - 下一轮 clean replication 强制 `next-bar open + no-overlap`；
     - 第一轮只比较 `baseline / ladder_hard_gate / ladder_plus_smallbody_context` 三臂，禁止 future path 倒灌与阈值事后重配。

## 当前硬结论
**`Rank 108 = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：先把它当“回踩前结构背景 + 回踩质量组合”的便宜 context gate，而不是新的独立 alpha。它当前更像给 `Fib retest_hold / EMA continuation` 做先验分层，也帮 `breakout-short` 明确了一条负面边界：别把 prebreak ladder 直接镜像成 shared short admission。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/literature/scout_rank108_prebreak_higherlow_pressure_ladder_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank108_prebreak_higherlow_pressure_ladder_source_intake.html`

## 对顶板的直接影响
- `Paper Seat = EMA / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 当前主资源位更新为：`Rank 108 / prebreak higher-low pressure ladder context gate`
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 108 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 108 hard-fail / exhausted，则切 HTF premium/discount long-bias context gate 的 source intake；若这条 fresh reserve 也 exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 回读确认：
  - `reports/artifacts/literature/scout_rank108_prebreak_higherlow_pressure_ladder_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank108_prebreak_higherlow_pressure_ladder_source_intake.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 clean replication 或 Light Stability Pack（遵守 1 主点 + 1 紧邻子点约束）
- `Rank 17` 虽仍有 hosted paper sidecar，但当前只保留为低频 fallback，不改写默认 seat
- 工作区仍有大量无关脏文件；本轮未尝试混提
