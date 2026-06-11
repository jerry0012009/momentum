# 2026-03-20 01:15 UTC — Rank 104 post-break sign-flip density source intake

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `5.7h`）
  - 脚本如实返回 `require-due` guard，不做伪 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮必须切到 `Scout Seat`，不能空转。

## 开轮检查
- branch：`master`
- repo 工作区仍有大量与本轮无关的既有脏文件；本轮不混提、不清理。
- 最近 optimization logs：
  - `2026-03-20_0054_rank103-clean-replication-park.md`
  - `2026-03-20_0034_rank103-confirmed-extremum-intake.md`
  - `2026-03-20_0009_ema-crypto-due-refresh.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前的 `Scout Seat` 候选顺序为：`post-break sign-flip density > body-defined zone re-entry honest failure verdict > MTF CHOP charged-up count > prebreak higher-low pressure ladder context gate`

## Active Scout 候选边际比较（先比较后认领）
1. **`post-break sign-flip density`**
   - 当前边际价值最高，因为它直接服务三条主线共用的 post-break 路径质量问题。
   - `Rank 103` 已 park 后，它是当前最靠前的 fresh paper source。
2. **`body-defined zone re-entry honest failure verdict`**
   - 仍有价值，但更像 failure 边界修正 reserve；先后顺序落在 `sign-flip density` 之后。
3. **`MTF CHOP charged-up count`**
   - 当前更像 `Fib retest_hold long-side veto`，适合后置 overlay，不如 `sign-flip density` 直接贴当前主线。
4. **`prebreak higher-low pressure ladder context gate` / 旧 evidence pool / P3 continuity / tiny-live plumbing`**
   - 当前都不该抢主资源位。

结论：本轮只认领 `post-break sign-flip density` 的 source intake，不并开第二条候选。

## 本轮认领
- 主点：`Rank 104 / post-break sign-flip density`
- 紧邻子点：把 source intake card、reader-facing 页面、`TODO` 顶板与下一轮顺序一次写齐

## 两条轻量诚实守门（已过）
### 1) trade on / trade off
- `trade on`：只把它当 **post-break hold-quality / management overlay**。breakout 是否成立、方向是否允许，仍由原主线决定；它只在 breakout 之后，用来决定持有窗口、size-down 或 retest 二次确认阈值。
- `trade off`：若必须等完整的 breakout 后 `6` 根路径都走完，才能回头决定 breakout 当下应不应该进场，那就是未来路径回填；这种写法不得升格。它不是新的独立 alpha，也不是默认 entry admission gate。

### 2) lookahead / repaint / leakage
- digest 里的 `flip_count` 是完整 post-break 小路径读数，直接拿来回填入场属于不诚实。
- queue-facing 版本必须改成 **`non-leaky early-window`**：只允许使用决定时点之前已经完成的 `2-3` 根 post-break bars，去管理后续 `4-8` bars 的持有/确认。
- 若改成不前视版本后就失效，应直接 `park`，不能继续靠 digest 口径续命。

## 当前硬结论
**`Rank 104 = guard-passed / admit_to_clean_replication_queue`**。

## 证据摘要（source intake 级）
- 现有 digest 样本 `N=1,940` 显示：超顺滑路径 (`low_flip=0~1`) 并不天然更健康；在当前 15m 代理下，反而更容易出现 `8-bar` 回吐。
- 关键读数：
  - `mean_ret8`: `low_flip=-0.062%`、`mid_flip=+0.029%`、`high_flip=+0.083%`
  - long 侧 `cont_hit_0.5ATR@8bars`: `low_flip=63.7%` vs `high_flip=78.2%`
- 更诚实的 desk 读法：这条线当前更像 **post-break 路径质量层**，值得做最小 clean replication；但前提是必须先改成 `non-leaky early-window` 版本。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/literature/scout_rank104_post_break_signflip_density_source_intake_card.csv`
- reader-facing 页面：
  - `reports/site/reading/repo_scout/rank104_post_break_signflip_density_source_intake.html`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat = Rank 104 / post-break sign-flip density`
- 当前 active Scout 顺序应改写为：
  1. `Rank 104 / post-break sign-flip density`
  2. `body-defined zone re-entry honest failure verdict`
  3. `MTF CHOP charged-up count`
  4. `prebreak higher-low pressure ladder context gate`
  5. `旧 P1 evidence_pool`
  6. `P3 continuity sidecar`
  7. `tiny-live plumbing`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 104 1 次最小 clean replication（strict non-leaky early-window 版本）`
  3. `Run 3 = 若 A股 lane 已 due-now / overdue，则先执行 EMA guarded refresh；若到时仍 waiting_not_due 且 Rank 104 clean replication 直接 hard-fail / exhausted，则切 body-defined zone re-entry honest failure verdict 的 source intake；只有 fresh source 也 exhausted，才允许继续回退到 MTF CHOP > prebreak ladder > 旧 evidence pool > P3 continuity > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前仍是 `waiting_not_due`
- 回读以下文件，确认已写入成功：
  - `reports/artifacts/literature/scout_rank104_post_break_signflip_density_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank104_post_break_signflip_density_source_intake.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 `body-defined zone re-entry`、`MTF CHOP` 或 `P3 continuity`
- 本轮没有触发 `edit exact text 不匹配` fallback（直接使用脚本稳健改写）
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
