# 2026-03-16 07:58 UTC · Desk Board Review

## 本轮一句话判断

**这轮不换席，也不改 verdict；但排兵布阵需要前推一格：`Paper Seat = EMA` 继续按 `running paper pilot / waiting_not_due` 读；`Live Seat = breakout` 继续维持 `bench`；而 `Scout Seat` 现在应重新拿回默认 bot3 主资源，因为 breakout 的 bench sync 已经做完，tiny-live 执行链也已补到 `operator reconciliation sequence v1`。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮继续只做 `TRADING DESK BOARD` 顶部最小排班更新、review 记录、plans 镜像/首页刷新与邮件摘要。
2. **最近 optimization logs**
   - `2026-03-16_0730_breakout-bench-reader-sync.md`
   - `2026-03-16_0738_small-live-routing-dryrun-sample-row.md`
   - `2026-03-16_0751_small-live-operator-reconciliation-sequence.md`
3. **最近 strategy review**
   - 上一轮（`07:16`）已经把 `breakout` 正式收口到 `bench`。
4. **当前 cron**
   - `bot2-strategy-review-40m`：running
   - `bot3-momentum-auto-opt-13m`：当前列表显示 `error`
   - 但从最近成功产物看，bench reader sync 与 tiny-live 两个相邻卡已经落下；所以这轮更该做的是**重排资源顺序**，而不是再改 desk verdict。

## 当前 strongest evidence

1. **Paper Seat 没变化：EMA 继续是 running paper，但当前真实 waiting_not_due**
   - `07:13 UTC` 的 guarded refresh 回执仍成立：当前没有新的 `due-now / overdue` lane；
   - `ema_paper_trading_due_guardrail_snapshot.csv` 继续显示 A 股下一次 close 在 `2026-03-17 07:00 UTC`；
   - 所以这条线现在不该再占默认 bot3 主资源。

2. **Live Seat 没变化：breakout 继续 bench，而且 reader-facing sync 已完成**
   - `07:30 breakout bench reader-facing sync` 已把 `alpha_closure_board` / 首页外显口径从旧的 `one_more_gate` 改成 `bench / conditional alpha`；
   - 当前关键 blocker 仍没有任何新下降证据：`pure_down=0/100`、`predown_bridge_12h=0/11`、`downrisk_48h=0/109`、`future_pure_down_48h=0/44`；
   - 所以这轮不再需要为 `bench` 本身继续消耗默认主资源。

3. **Scout Seat 现在重新成为更该优先吃资源的主入口**
   - 当前没有新的 shortlist；
   - 但 `Rank 1 τ-band` 仍是最值得等 genuinely new bar 的 honest recheck 对象；
   - `Rank 2 combo_all` 仍是当前最强的 confirmation challenger，若 `Rank 1` 继续没新 bar，就该吃下一轮轻量 forward 复核资源。

4. **tiny-live plumbing 已经从“零散卡片”推进到顺序化执行链**
   - `routing dry-run green sample row`
   - `paper-live shadow parity checklist`
   - `parity_red action ladder`
   - `reopen gate checklist`
   - `green resume sample row`
   - `operator reconciliation sequence v1`
   - 这说明 Run 3 现在不是泛研究，而是已有一条可以继续向前补相邻执行卡的连续链路。

## 当前 weakest / should-park lines

- 在下一次真实 due 窗口前重复 `EMA guarded refresh`：继续 park。
- 在没有 genuinely new blocker reduction 前继续给 breakout 同类 rerun / wording：继续 park。
- 在 `Rank 1` 没 genuinely new bar 前重复 same-sample scout recheck：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`bench`**
- **Scout Seat：继续找更短周期、更贴 crypto 的 breakout / confirmation challenger；当前没有新的 shortlist，但它已重新成为默认 bot3 主资源入口。**

## 接下来优先级 Top 1~3

1. **Scout Seat 回到默认主资源位**
   - 优先查 `Rank 1 τ-band` 是否终于有 genuinely new local bar；
   - 若没有，则只允许对 `Rank 2 combo_all` 做轻量 `forward` 复核，或切 `Rank 3 third-touch + EMA/MACD confluence` clean-room spec。

2. **small-live 沿现有执行链继续补相邻卡**
   - 现在已经有 `operator reconciliation sequence v1`；
   - 后续若继续补，只应补更靠近真实 route/shadow ledger 对账的那一格。

3. **breakout 继续停在 bench，等待 genuinely new blocker reduction**
   - 在没有新 blocker reduction 前，不再给默认重跑资源。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `Live Seat verdict`：补一条 `07:30 UTC` 的 reader-facing sync 说明，明确 `bench` 已经外显，不再需要重复同步。
- 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：把默认顺序从 `bench sync -> Scout -> tiny-live` 前推成 **`Scout -> tiny-live -> breakout remains bench`**。

### 这轮不改
- 不改 `Paper Seat`
- 不改 `Paper Seat = running paper pilot / waiting_not_due`
- 不改 `Live Seat = bench`
- 不改 `Scout shortlist` 本身
- 不改 cron 频率

## 风险与不确定性

1. `bot3` 当前列表再次显示 `error`，说明执行层稳定性仍需留心；但它不改变 desk 当前席位判断。
2. `Rank 2 combo_all` 仍只是 `120d / 15m / 3` 币种口径，不能因 breakout 被 bench 就自动升格成 Live Seat。
3. `small_live` 虽然执行链越来越完整，但当前仍是 plumbing，不是 live approval。

## 本轮一句话结论（给 Jerry）

**这轮结论本身没变：EMA 继续是 running paper、breakout 继续是 bench；真正变化是默认资源顺序——breakout 的 bench sync 已经做完，tiny-live 链也补到 sequence v1，所以接下来 bot3 应该先回 Scout，再把 fallback 给 tiny-live，而不是继续在 breakout 上打转。**
