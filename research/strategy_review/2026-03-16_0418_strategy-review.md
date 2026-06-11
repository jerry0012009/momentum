# 2026-03-16 04:18 UTC · Desk Board Review

## 本轮一句话判断

**席位不换，但排班继续前推一格：`Paper Seat = EMA` 仍因真实 market close 未到而 blocked；`Live Seat = breakout` 仍只能维持 `keep but narrower-scope`；`Scout Seat` 已经从“有 shortlist”推进到“Rank 1 已拿到 first verdict，但仍非 replace-ready”。因此这轮最值得做的最小更新，是同步 `TRADING DESK BOARD` 的 Scout 状态与下一批 3 个 bot3 runs。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量历史脏改 / 未跟踪文件；本轮只做 `docs/TODO.md` 顶部最小同步、review 记录、plans 镜像/首页刷新与邮件摘要。
2. **最近 optimization logs**
   - `2026-03-16_0410_routing-dry-run-checklist.md`
   - `2026-03-16_0355_tau-band-first-verdict.md`
   - `2026-03-16_0336_small-live-ledger-template.md`
   - `2026-03-16_0323_scout-seat-shortlist-card.md`
3. **最近 strategy review**
   - 最新几轮已把席位收敛成：`Paper = EMA`、`Live = breakout keep but narrower-scope`、`Scout = fast-cycle crypto shortlist`。
4. **当前 cron**
   - `bot2-strategy-review-40m`：running
   - `bot3-momentum-auto-opt-13m`：ok
   - `bot7-quant-digest-4h`：ok

## 当前 strongest evidence

1. **Paper Seat 仍只能是 EMA**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 显示 A 股 active lane 下一次 close 约在 `2026-03-16 07:00 UTC`，当前全是 `waiting_not_due`。
   - 说明这轮不能伪造 refresh；最诚实动作仍是等真实 completed bar。

2. **Live Seat 仍只能先保留 breakout，但没有新 blocker reduction**
   - `avoid_fluctuating_revisit_guard_20bps.csv` 当前仍是 `cache_advanced_but_recent_recheck_cooldown_hold`。
   - 最近 heavy recheck 约在 `2026-03-15 23:25 UTC`，当前仍在 `6h` cooldown 内；同时硬 blocker 仍旧没动：`pure down coverage = 0/100`、`pre-down bridge = 0/11`。
   - 所以更诚实 verdict 仍是：**`keep but narrower-scope`**，不是升级，也还没到 replace-ready。

3. **Scout Seat 已拿到新的本地 first verdict，但仍非替补就绪**
   - `Scout Seat shortlist v1` 已经落地；`Rank 1 τ-band` 也已完成第一刀 `15m crypto` 最小对照实验。
   - 当前最佳变体 `confirm2of3_tau_010` 相对 `raw_breakout`：
     - `mean_total_return` 约 `-46.14% -> -11.28%`
     - `mean_false_break_ratio` 约 `50.10% -> 41.15%`
   - 但 `positive_asset_ratio = 0/3`，所以当前只配当 `execution guard / scout follow-up`，还不是可替换 Live Seat 的候选。

4. **tiny-live plumbing 又推进了一步**
   - `small_live_routing_dry_run_checklist_v1.csv` 已落下，说明 Run 3 不再只是抽象“live rules”，而是进入 operator checklist 层。

## 当前 weakest / should-park lines

- `Fibonacci`：继续 `park / archive`。
- breakout 的同样本 heavy rerun：在 cooldown 未结束前继续 park，避免重复劳动。
- 把 `Scout Rank 1` 误读成 replace-ready winner：当前不能这么写。

## Desk verdict

- **Paper Seat：`EMA`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`keep but narrower-scope`**
- **Scout Seat：`fast-cycle crypto candidate scouting`，继续找 breakout/confirmation/execution-guard 型 challenger**

## 接下来优先级 Top 1~3

1. **继续把 breakout 压成 cooldown-aware hard verdict / blocker sync**
   - cooldown 未过就不 rerun；
   - cooldown 过后若 cache 仍领先，只允许做 `1` 次 heavy rerun。

2. **Scout Seat 优先做 Rank 1 的同口径 forward continuation / recheck**
   - 先验证当前“相对 raw 更不差”的结论能不能延续；
   - 若新 bar 仍不足，再切到 `Rank 2 volume + support-flip + higher-low` 的最小 clean-room spec。

3. **tiny-live plumbing 下一刀补 `paper-live shadow parity checklist`**
   - 当前 ledger template + routing dry-run checklist 已有；
   - 再补 parity checklist，能更直接缩短 `time-to-tiny-live`。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  1. 补上 `Scout Rank 1 τ-band` 已有 first verdict，但仍非 replace-ready；
  2. 把 `Next 3 bot3 runs` 改成当前 04:18 窗口下的最新三步排班。

### 这轮不改
- 不改 `Paper Seat` 归属
- 不改 `Live Seat` 归属
- 不改 `Live Seat = keep but narrower-scope`
- 不改 cron 频率

## 风险与不确定性

1. 当前 Scout 新结果仍只是 `3 assets / 120d / fixed exit` 的 first verdict，不足以宣布 replacement。
2. breakout 只要 `pure-test / down-tail` blocker 仍未下降，就不该重新扩口径。
3. EMA 当前不是停滞，而是真 `waiting_not_due`；若误把等待窗口当“无推进”，会错误驱动 bot3 空转。

## 本轮一句话结论（给 Jerry）

**这轮 desk 不换席：EMA 继续坐 Paper Seat，breakout 继续坐 Live Seat 但维持 `keep but narrower-scope`；Scout Seat 现在已经不是“只有 shortlist”，而是 `Rank 1 τ-band` 已拿到一个“相对改善但绝对仍负”的 first verdict，所以接下来 bot3 应该按“breakout cooldown-aware verdict → Scout Rank 1 forward continuation / Rank 2 fallback → paper-live parity checklist”这三步排。**
