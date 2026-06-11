# 2026-03-16 08:43 UTC · Desk Board Review

## 本轮一句话判断

**这轮不换席，也不改主 verdict；只把当前窗口排班再前推一格。`Paper Seat = EMA` 继续按 `running paper pilot / waiting_not_due` 读；`Live Seat = breakout` 继续维持 `bench / recheck-only`；`Scout Seat` 仍是当前默认主资源入口，而刚新增的 `Rank 3 first verdict` 与 `green shadow parity row` 说明 Run 2 / Run 3 两条 fallback 现在都比上一轮更具体了。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮只做 `TRADING DESK BOARD` 顶部一处最小排班更新、review 记录、plans 镜像/首页刷新与邮件摘要。
2. **最近 optimization logs**
   - `2026-03-16_0805_scout-rank3-clean-room-spec.md`
   - `2026-03-16_0817_small-live-green-shadow-row.md`
   - `2026-03-16_0838_scout-rank3-first-verdict.md`
3. **最近 strategy review**
   - 上一轮（`07:58`）已经把默认顺序收敛成：`Scout -> tiny-live -> breakout stays bench`。
4. **当前 cron**
   - `bot2-strategy-review-40m`：ok
   - `bot3-momentum-auto-opt-13m`：running
   - 当前没有新的调度异常需要改 cron 节奏。

## 当前 strongest evidence

1. **Paper Seat 仍无变化**
   - `EMA` 的 guarded refresh 回执仍成立；
   - `ema_paper_trading_due_guardrail_snapshot.csv` 继续显示 A 股下一次 close 在 `2026-03-17 07:00 UTC`；
   - 所以这轮仍应按 `running paper pilot / waiting_not_due` 读，而不是重复守门。

2. **Live Seat 仍无变化**
   - `breakout` 的 `bench` 已在 reader-facing 页面同步完成；
   - 当前也没有 genuinely new blocker reduction；
   - 因此继续维持 `bench / recheck-only`，不回头再消耗默认主资源。

3. **Scout Seat 这轮的新增价值，来自 Rank 3 不再只是 spec**
   - `Rank 3 third_touch_plus_ema_macd` 已从 `spec-ready` 推到本地 first verdict；
   - 当前最好读法：
     - `mean_total_return ≈ +0.78%`
     - `mean_false_break_ratio = 0.00%`
     - 但 `positive_asset_ratio = 1/3`
     - `mean_trades ≈ 0.33` 笔/资产
   - 所以它只配当 **更窄的 structure-confirmation guard / first-verdict-passed candidate**，还不是 replace-ready / tiny-live ready。

4. **tiny-live fallback 这轮的新增价值，来自 green shadow parity row 已补齐**
   - `small_live` 链现在已经覆盖：
     - `dry-run green row`
     - `green shadow parity row`
     - `parity_red row`
     - `reopen gate`
     - `green resume row`
     - `operator reconciliation sequence`
   - 所以当前 Run 3 fallback 已经不只是“有 checklist”，而是有一整条可顺着走的执行链。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`bench`**
- **Scout Seat：继续找更短周期、更贴 crypto 的 breakout / confirmation challenger；当前没有新的 shortlist，但 `Rank 3 third_touch_plus_ema_macd` 已升到 first-verdict-passed 的更窄 guard 候选。**

## 接下来优先级 Top 1~3

1. **Scout 继续拿默认主资源**
   - 优先查 `Rank 1 τ-band` 是否终于有 genuinely new local bar；
   - 若没有，则只对 `Rank 2 combo_all` 或 `Rank 3 third_touch_plus_ema_macd` 做轻量 `forward / friction` 复核。

2. **tiny-live fallback 沿现有执行链继续补相邻卡**
   - 当前最新链路应按 `dry-run green row -> green shadow parity row -> parity_red -> reopen gate -> green resume row -> operator reconciliation sequence` 来读；
   - 后续若继续认领，只应补更贴近真实 route/shadow ledger 对账的那一格。

3. **breakout 继续停在 bench**
   - 在没有 genuinely new blocker reduction 前，不回头默认重跑。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：
  - 把当前窗口时间改到 `08:43`；
  - 明确写入 `Rank 3 first verdict` 已落下；
  - 明确把 `green shadow parity row` 纳入 tiny-live 执行链。

### 这轮不改
- 不改 `Paper Seat`
- 不改 `Paper Seat = running paper pilot / waiting_not_due`
- 不改 `Live Seat = bench`
- 不改 `Scout shortlist` 本身
- 不改 cron 频率

## 风险与不确定性

1. `Rank 3` 虽然已通过 first verdict，但交易太少，不能因为相对 raw 更干净就偷升格成 Live Seat。
2. `small_live` 虽然执行链更完整，但仍是 plumbing，不是 live approval。
3. 当前 `bot3` 仍在 running，后续若它自己再产出 genuinely new local bar 或新的受控复核，下一轮再据此调整排班更稳妥。

## 本轮一句话结论（给 Jerry）

**这轮 desk 主判断没变：EMA 继续 running paper、breakout 继续 bench；我只把当前窗口排班补得更贴最新产物——Scout 现在不只是有 Rank 2，也有 Rank 3 的 first verdict，而 tiny-live fallback 也已经把 green shadow parity row 补齐，所以默认顺序继续是 `Scout -> tiny-live -> breakout stays bench`。**
