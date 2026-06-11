# 2026-03-16 05:53 UTC · Desk Board Review

## 本轮一句话判断

**席位不换，但 desk 读法前推了两格：`Paper Seat = EMA` 现在更诚实的 reader-facing 位置已不是 `pre-paper`，而是 `running paper pilot / on-clock waiting next refresh`；`Live Seat = breakout` 仍先维持 `keep but narrower-scope`，但 cooldown 已走完，从这轮开始只再给 `1` 次 honest rerun 机会，若 blocker 仍不降，下一轮优先进 `bench review`。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮继续只做 `TRADING DESK BOARD` 顶部最小更新、review 记录、plans 镜像/首页刷新与邮件摘要。
2. **最近 optimization logs**
   - `2026-03-16_0515_scout-rank2-friction-recheck.md`
   - `2026-03-16_0525_small-live-parity-red-ladder.md`
   - `2026-03-16_0459_scout-rank2-first-verdict.md`
3. **最近 strategy review**
   - 最新 board 仍是：`Paper = EMA`、`Live = breakout narrower-scope`、`Scout = fast-cycle crypto shortlist`。
4. **当前 cron / 最近 bot3 runs**
   - `bot2-strategy-review-40m`：running
   - `bot3-momentum-auto-opt-13m`：当前列表显示 `error`
   - 进一步看 run history：最近 bot3 两次报错分别是
     - `build_alpha_closure_board_report.py` 的 exact-text edit mismatch
     - 以及最新一次模型超时
   - 这说明当前执行风险不只是研究方向，而是 **不要让同一类重跑在脚本 edit / timeout 上无限消耗回合**。

## 当前 strongest evidence

1. **Paper Seat 现在应改写成 running paper，而不是 pre-paper**
   - `ema_paper_trading_refresh_history.csv` 已有 `6` 条 completed-bar rows；
   - `创业板ETF 1d` 的 history 行已明确写成 `refresh_green_primary_live`；
   - `Crypto 1d+1wk` 也已在 `2026-03-16 00:01 UTC` 追加到新的 completed bar；
   - `ema_paper_trading_runbook.csv` 与 `ema_paper_trading_monitoring_board.csv` 也都已把 `创业板ETF 1d` 写成 `active_primary / 当前唯一 primary paper pilot`。
   - 所以这条线当前更诚实的位置，不再是“快要 paper”，而是**已经在运行 paper，只是当前 on-clock 等下一次真实 close**。

2. **Live Seat 仍没有新 blocker reduction，但 cooldown 已走完**
   - `avoid_fluctuating_revisit_guard_20bps.csv` 的原始 artifact 仍是 `cache_advanced_but_recent_recheck_cooldown_hold`，但按当前时间看，`6h` 短冷却已经基本走完；
   - 历次 hard blocker 仍没变：`pure down coverage = 0/100`、`pre-down bridge = 0/11`。
   - 因此这轮更诚实的读法是：**继续 `keep but narrower-scope`，但只再给 1 次 honest rerun；再不动，就优先进 `bench review`。**

3. **Scout Seat 没有新 shortlist，但头部 challenger 更清楚了**
   - `Rank 1 τ-band` 仍是“相对 raw 改善，但绝对仍负”；
   - `Rank 2 combo_all` 已有 first verdict + friction recheck：
     - first verdict：`mean_total_return ≈ +2.33%`、`mean_false_break_ratio ≈ 6.67%`、`positive_asset_ratio = 2/3`
     - friction 快检：在 `10/15/20 bps per side` 下仍约 `+1.78% / +1.10% / +0.42%`
   - 当前更诚实读法：**它是值得继续做轻量 forward 复核的 confirmation challenger，但还不是 replace-ready / tiny-live ready。**

4. **tiny-live plumbing 已从 checklist 进入 red-flag action ladder**
   - 最新 `small_live_parity_red_action_ladder_v1.csv` 与 `small_live_shadow_parity_sample_row_v1.csv` 已落下；
   - 当前 Run 3 若再 fallback，最值钱的是沿这条 execution chain 继续补相邻卡，而不是再写抽象 live prose。

## 当前 weakest / should-park lines

- `Fibonacci`：继续 `park / archive`。
- 在 `Rank 1` 没有新 bar 前重复 scout same-sample recheck：当前边际价值低。
- 让 breakout 在 cooldown 结束后对同一 rerun 无限重试：当前比“方向错”更像执行层浪费。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / on-clock waiting next refresh`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`keep but narrower-scope`，但从这轮起只再给 1 次 honest rerun；再不动就优先 `bench review`**
- **Scout Seat：继续找更短周期、更贴 crypto 的 breakout / confirmation challenger；当前 `Rank 2 combo_all` 是更值得继续轻量复核的头部候选之一。**

## 接下来优先级 Top 1~3

1. **先给 breakout 那唯一的一次 honest heavy rerun / hard verdict sync**
   - 现在 cooldown 已过；
   - 如果 rerun 后 blocker 仍不下降，下轮优先写 `bench review`，不要再默认 keep。

2. **若 Live Seat 那一枪打完仍无新 blocker reduction，就转回 tiny-live execution chain**
   - 优先 `parity_red action / sample-row` 这类相邻执行卡；
   - 不要回头再写近义 live rules 页。

3. **Scout 只在有 genuinely new bar 时才回到 Rank 1；否则只做更轻量 forward，不重复同样本**
   - `Rank 1 τ-band` 没新 bar 就不重跑；
   - `Rank 2 combo_all` 只允许做轻量 forward 复核，不再重复 first verdict / friction ladder。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  1. 把 `Paper Seat` 从 `pre-paper continuation` 改写为 `running paper pilot / on-clock waiting next refresh`；
  2. 把 `Live Seat` 写死为“cooldown 后只再给 1 次 honest rerun；再不动就优先 bench review”；
  3. 把 `Next 3 bot3 runs` 切到 `05:53` 的当前窗口排班。

### 这轮不改
- 不改 `Paper Seat` 归属
- 不改 `Live Seat` 归属
- 不改 `Live Seat = keep but narrower-scope` 这个当前 verdict
- 不改 cron 频率

## 风险与不确定性

1. `EMA` 虽然更该写成 running paper，但当前仍只是 paper，不是 live，也还要继续证明 refresh continuity / week-1 review continuity。
2. `Rank 2 combo_all` 仍只是 `120d / 15m / 3` 币种口径，不能直接宣布 replacement。
3. breakout 当前最危险的不是“没人给它机会”，而是**给了太多近义机会却还不收口**；因此这轮必须把“只再给 1 次”写死。

## 本轮一句话结论（给 Jerry）

**这轮我没换席，但把 board 写得更诚实了：EMA 现在已经不该再叫 pre-paper，而是 running paper pilot；breakout 继续坐 Live Seat 且暂时仍是 `keep but narrower-scope`，但 cooldown 已过，只再给 1 次 honest rerun——如果 blocker 还是不降，下轮就该优先进 `bench review`。**
