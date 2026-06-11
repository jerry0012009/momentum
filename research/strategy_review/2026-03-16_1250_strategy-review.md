# 2026-03-16 12:50 UTC · Desk Board Review

## 本轮一句话判断

**这轮仍是无换席巡检，但有一个重要的 routing 收紧已经生效：`Paper Seat = EMA running paper / waiting_not_due`，`Live Seat = breakout bench / recheck-only` 不变；真正变化是 `Scout Seat` 不再默认把“shared Binance 15m cache 续写 / 追最新 completed bar / continuity”当作主点，而是先回到历史样本上的 `verdict / friction / trade-count / shadow-readiness`。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
     - 美股下一次 close：`2026-03-16 20:00 UTC`
     - Crypto 1d 下一次 close：`2026-03-17 00:00 UTC`
     - A 股下一次 close：`2026-03-17 07:00 UTC`
   - 所以当前 `EMA` 继续是 running paper，但此窗口只该做 waiting 状态维护与 next-close 核对，不该重回默认 bot3 主任务。

2. **Live Seat 继续维持 bench / recheck-only**
   - `breakout_live_seat_hard_verdict_20260316_0624.csv` 仍是当前有效硬锚点；
   - blocker 仍无 genuinely new reduction：
     - `pure_down = 0/100`
     - `predown_bridge_12h = 0/11`
     - `downrisk_48h = 0/109`
     - `future_pure_down_48h = 0/44`
   - 因此这轮仍不应把 breakout 拉回默认任务队列，也不应重开 heavy rerun。

3. **Scout Seat 的关键变化不在 verdict，而在 task selection 规则**
   - 直到上一轮前，`Rank 3 third_touch_plus_ema_macd` 已经在多个 genuinely new completed `15m` bar 上连续通过 continuity；
   - 但这些 continuity 刷新并没有带来 seat-level 升级，最佳版本读法始终稳定在：
     - `mean_total_return ≈ +0.78%`
     - `mean_false_break_ratio = 0.00%`
     - `positive_asset_ratio = 1/3`
   - 这反过来证明：**在候选尚未进入明确的 `shadow-admission / continuity-week / live-readiness` 之前，默认继续追最新 `15m` bar，本身不是高杠杆主点。**
   - 因而当前 authoritative override 是合理的：Scout 默认先用历史样本推进 `first verdict / friction / trade-count / shadow-readiness`，而不是把“追最新 completed 15m bar”当成本轮主点。

4. **Rank 2 `combo_all` 目前是更符合新规则的 Scout 主点**
   - 最新 `combo_all_shadow_readiness_drycheck.csv` 已把它压成一张纯历史样本的 fast screen：
     - `base_post_cost_return`：pass（`+2.33%` @ `6bps/side`）
     - `friction_15bps_hold`：pass（`+1.10%`）
     - `cross_asset_floor`：pass（`2/3` assets positive）
     - `trade_count_floor`：pass（mean trades `6.7` / asset）
     - `false_break_guard`：pass（`6.67%`）
     - `shadow_admission_scope`：fail（仍只有 `120d / 15m / 3 assets`，样本偏窄）
   - 更诚实的结论是：**`Rank 2 combo_all` 已通过最小 `trade-count / friction / false-break` 快筛，当前值得保留为 `keep-narrower shadow-candidate`；但还不是 `shadow-admission-ready / replace-ready / tiny-live ready`。**

5. **tiny-live fallback 继续向 closeout / registry / writeback 颗粒度推进**
   - `small_live review writeback matrix v1`
   - `small_live review registry template v1`（且网页/CSV 现在已真正发布）
   - 这说明在 Scout 当前窗口无更高杠杆历史样本刀口时，Run 3 fallback 不是空转，而是在把 future venue/shadow review 的 closeout / registry / next-queue 链继续压实。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 在未被 board / 最新 review 明确授权前，把“shared Binance 15m cache 续写 / 等下一根 bar / continuity refresh”当作 Scout 默认主点：继续 park。
- 在 `EMA waiting_not_due` 窗口里重开 EMA 发散研究：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`bench`**
- **Scout Seat：继续找更短周期、更贴 crypto、可快速验证的 challenger；当前没有新的 shortlist 排名变化，但默认主点已明确收紧为**：优先历史样本上的 `verdict / friction / trade-count / shadow-readiness`，而不是默认追最新 completed `15m` bar。**

## 建议优先级 Top 1~3

1. **Scout 继续拿默认主资源，但先做历史样本收紧**
   - 优先补 `Rank 2 combo_all` / `Rank 3 third_touch_plus_ema_macd` 的 `trade-count / shadow-readiness / more-honest dry-check`；
   - 不要默认把 `shared Binance 15m cache` 续写与 continuity 当成本轮主点。

2. **tiny-live 继续当第二顺位 fallback**
   - 沿 `handoff / review-ticket / writeback-matrix / registry-template` 这条更贴近 future venue review 的 closeout / writeback 链再补相邻缺口；
   - 不回头重写抽象 live 规则页。

3. **breakout 继续停在 bench / recheck-only**
   - 只有在 `TRADING DESK BOARD` 或最新 bot2 review 明确点名且基于新 blocker reduction 时，才允许一次受控 recheck；
   - 当前没有这类新证据。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1250_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 `docs/TODO.md`：当前顶板已经被最新 bot3 run 收紧到 `12:31 authoritative override + 12:39 Rank 2 shadow-readiness dry-check`，足以诚实反映这轮判断。
- 不改 cron 频率：当前节奏仍合理，`bot3` 当前也为 `ok`。
- 不改单独网页 verdict：当前没有新的席位判断变化需要新增外显改写。

## 风险与不确定性

1. `Rank 2 combo_all` 虽然更符合当前 Scout routing，但样本仍偏窄；不能因为它通过了 shadow-readiness dry-check，就偷升格成 shadow/live 候选。
2. `Rank 3` 的 continuity 连续通过，并不自动等于“值得继续追新 bar”；如果没有 desk 明确授权，继续追 bar 只是低杠杆重复劳动。
3. `EMA waiting_not_due` 窗口还很长；若不严守 `Scout > tiny-live plumbing > 其他维护` 与本轮新补充的“历史样本优先”约束，bot3 仍可能回到低价值空转。

## 本轮一句话结论（给 Jerry）

**这轮最重要的不是席位变了，而是排兵布阵更收紧了：EMA 继续 running paper 且 waiting_not_due，breakout 继续 bench / recheck-only；Scout 继续拿主资源，但默认主点现在应是历史样本上的 `trade-count / friction / shadow-readiness`，而不是继续把“追最新 15m bar continuity”当成本轮主任务。**
