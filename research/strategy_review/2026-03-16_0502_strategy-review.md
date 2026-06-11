# 2026-03-16 05:02 UTC · Desk Board Review

## 本轮一句话判断

**席位不换，但排班要更贴当前时钟：`Paper Seat = EMA` 仍被真实 market close 阻塞；`Live Seat = breakout` 仍只能维持 `keep but narrower-scope`；`Scout Seat` 则因 Rank 2 已拿到正向 first verdict，短期内更适合吃掉 breakout cooldown 结束前的 bot3 资源。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮只做 `TODO` 顶部最小排班更新、review 记录、plans 镜像刷新与首页发布。
2. **最近 optimization logs**
   - `2026-03-16_0423_scout-rank2-clean-room-spec.md`
   - `2026-03-16_0436_paper-live-shadow-parity-checklist.md`
   - `2026-03-16_0459_scout-rank2-first-verdict.md`
3. **最近 strategy review**
   - 最新 review 仍把席位固定为：`Paper = EMA`、`Live = breakout keep but narrower-scope`、`Scout = fast-cycle crypto shortlist`。
4. **当前 cron**
   - `bot2-strategy-review-40m`：running
   - `bot3-momentum-auto-opt-13m`：ok
   - `bot7-quant-digest-4h`：ok

## 当前 strongest evidence

1. **Paper Seat 仍只能是 EMA**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示所有 active lane 都是 `waiting_not_due`；A 股下一次 close 仍在 `2026-03-16 07:00 UTC`。
   - 这说明当前不是“没推进”，而是真还没到 refresh 时点。

2. **Live Seat 仍没有新 blocker reduction**
   - `avoid_fluctuating_revisit_guard_20bps.csv` 依旧是 `cache_advanced_but_recent_recheck_cooldown_hold`。
   - 最近 heavy recheck 在 `2026-03-15 23:25 UTC`；短冷却大约到 `05:25 UTC`。
   - 最关键 blocker 仍没变：`pure down coverage = 0/100`、`pre-down bridge = 0/11`。
   - 所以当前 verdict 仍是：**`keep but narrower-scope`**，而不是升级，更不是 live-ready。

3. **Scout Seat 现在已经不只是一张 shortlist，而是有了更强的 Rank 2 challenger**
   - `Rank 1 τ-band` 先前已给出“相对 raw 改善，但绝对仍负”的 first verdict。
   - `Rank 2 volume + support-flip + higher-low` 现在已从 clean-room spec 推到本地 first verdict：
     - `raw_breakout`：`mean_total_return ≈ -40.39%`，`mean_false_break_ratio ≈ 48.75%`，`positive_asset_ratio = 0/3`
     - `combo_all`：`mean_total_return ≈ +2.33%`，`mean_false_break_ratio ≈ 6.67%`，`positive_asset_ratio = 2/3`
   - 当前更诚实读法：**它已成为值得继续做轻量 forward / friction 复核的 confirmation challenger，但还不是 replace-ready / tiny-live ready。**

4. **tiny-live plumbing 也继续往执行链收敛**
   - `paper_live_shadow_parity_checklist_v1.csv` 已落下。
   - 这让 `paper_ref -> live_shadow_ref` 的同步审计链也变成了可复用 operator artifact，而不只是抽象 live 规则。

## 当前 weakest / should-park lines

- `Fibonacci`：继续 `park / archive`。
- 在 breakout cooldown 还没走完前，重复写 `blocker sync / rerun reminder`：当前边际价值低。
- 对 `Scout Rank 2 combo_all` 重复改写 first verdict：当前不该再做同样本近义重写。

## Desk verdict

- **Paper Seat：`EMA`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`keep but narrower-scope`**
- **Scout Seat：继续找更短周期、更贴 crypto 的 breakout / confirmation / execution-guard challenger；当前 Rank 2 `combo_all` 已升为更值得继续轻量复核的 shortlist 头部候选之一。**

## 接下来优先级 Top 1~3

1. **在 breakout cooldown 结束前，先把 bot3 资源给 Scout Seat**
   - 先查 Rank 1 `τ-band` 是否已有足够新 bar 做 honest recheck；
   - 若还不够，就只给 Rank 2 `combo_all` 做轻量 `forward / friction` 复核。

2. **small_live 只允许沿 parity checklist 往前补紧邻执行卡**
   - 例如 `parity_red action / sample-row`；
   - 不要回头再写近义 live rules 页。

3. **等到 `05:25 UTC` 左右 cooldown 结束后，再给 breakout 一次 honest rerun 机会**
   - 前提是 cache 仍领先；
   - 若 rerun 之后 blocker 仍不下降，下一轮优先往 `bench review` 收口。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：
  - 把 breakout cooldown 结束前的前两轮资源，显式让给 `Scout Seat / tiny-live`；
  - 把 breakout 的 one-time rerun 放到 cooldown 结束后再执行。

### 这轮不改
- 不改 `Paper Seat`
- 不改 `Live Seat`
- 不改 `Live Seat = keep but narrower-scope`
- 不改 cron 频率

## 风险与不确定性

1. `Rank 2 combo_all` 目前仍只是 `3 assets / 120d / fixed exit` 的 first verdict，不能直接宣布 replacement。
2. breakout 只要 `pure-test / down-tail` blocker 仍不动，就不能因为“已经等了几轮”而自动升级。
3. EMA 当前是真 `waiting_not_due`；若错误把等待窗口当停滞，会把 bot3 推回低价值空转。

## 本轮一句话结论（给 Jerry）

**这轮 desk 不换席，但我把排班更贴当前时钟了：EMA 继续坐 Paper Seat，breakout 继续坐 Live Seat 且仍是 `keep but narrower-scope`；不过因为 breakout 要到大约 `05:25 UTC` 才结束 cooldown，而 Scout Rank 2 `combo_all` 已拿到正向 first verdict，所以接下来 bot3 的前两轮更该先做 `Scout / tiny-live`，等 cooldown 走完后再给 breakout 那唯一的一次 honest rerun。**
