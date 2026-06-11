# 2026-03-16 07:16 UTC · Desk Board Review

## 本轮一句话判断

**这轮最大的变化不是换席，而是给 Live Seat 下了明确收口：`Paper Seat = EMA` 继续按 `running paper pilot / on-clock waiting next refresh` 读；`Live Seat = breakout` 虽然仍是当前名义占位者，但在“唯一一枪”打完且 blocker 仍无下降后，这轮应正式给出 `bench` verdict；`Scout Seat` 因此重新成为默认寻找下一位 live challenger 的主资源入口。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮只做 `TRADING DESK BOARD` 顶部最小收口更新、review 记录、plans 镜像/首页刷新与邮件摘要。
2. **最近 optimization logs**
   - `2026-03-16_0642_breakout-hard-verdict-sync.md`
   - `2026-03-16_0646_small-live-reopen-gate.md`
   - `2026-03-16_0706_small-live-reopen-resume-row.md`
   - `2026-03-16_0714_ema-paper-guarded-waiting.md`
3. **最近 strategy review**
   - 上一轮（`06:33`）还把当前主排班写成“close 前打一枪 Live，close 后第一轮回 Paper”。
4. **当前 cron**
   - `bot2-strategy-review-40m`：running
   - `bot3-momentum-auto-opt-13m`：当前已回到 `ok`
   - 说明 close 前后的关键 run 已经跑完，当前更该做的是 desk 收口，而不是再为执行失败找借口。

## 当前 strongest evidence

1. **Paper Seat 已完成 post-close 守门，当前如实回到 waiting_not_due**
   - `07:13 UTC` 已实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 返回结论不是脚本失败，而是当前没有新的 `due-now / overdue` lane；
   - `ema_paper_trading_refresh_history.csv` 仍是 `6` 条，没有伪造 completed-bar append；
   - `ema_paper_trading_due_guardrail_snapshot.csv` 已把 A 股下一次 close 推到 `2026-03-17 07:00 UTC`。
   - 所以 `EMA` 继续坐 `Paper Seat`，但从现在起直到下一个真实 due 窗口前，都应按 **真实 `waiting_not_due`** 读。

2. **Live Seat 的“唯一一枪”已经用掉，且 blocker 仍无下降**
   - `06:24` 已执行过一次 Live Seat hard verdict sync：尝试重跑 heavy path，但因长下载路径超时风险明显，最终按 cached latest evidence 收口。
   - 对应 artifact：`reports/artifacts/support_breakout_v0_h24/breakout_live_seat_hard_verdict_20260316_0624.csv`
   - 当前关键 blocker 仍是：
     - `pure_down = 0/100`
     - `predown_bridge_12h = 0/11`
     - `downrisk_48h = 0/109`
     - `future_pure_down_48h = 0/44`
   - 也就是说，上一轮写下的“若下一轮仍无 blocker reduction，则优先 bench review”这条条件，现在已经被满足。

3. **Scout Seat 没有新 shortlist，但当前重新获得主资源优先级**
   - `Rank 1 τ-band` 仍缺 genuinely new local bar 的诚实 recheck；
   - `Rank 2 combo_all` 仍是当前更强的 confirmation challenger：
     - first verdict：`mean_total_return ≈ +2.33%`
     - friction recheck：`10/15/20 bps` 下仍约 `+1.78% / +1.10% / +0.42%`
   - 它仍不是 replace-ready，但在 breakout 被 bench 后，Scout 现在重新成为最该吃默认 bot3 资源的地方。

4. **tiny-live plumbing 已形成连续执行链，不再只是抽象规则**
   - `parity_red action ladder`
   - `reopen gate checklist`
   - `green resume sample row`
   - 说明当 Paper / Live 同时不该继续重跑时，Run 3 也有明确且不空转的 execution-adjacent 任务池。

## 当前 weakest / should-park lines

- `breakout` 的同样本 rerun：当前应正式 park，除非拿到 genuinely new blocker reduction。
- 在下一次真实 due 窗口前重复 `EMA guarded refresh`：当前边际价值很低。
- 在 `Rank 1` 没 genuinely new local bar 前重复 same-sample scout continuation：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / on-clock waiting next refresh`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`bench`**
- **Scout Seat：继续找更短周期、更贴 crypto 的 breakout / confirmation challenger；当前没有新的 shortlist，但 `Rank 2 combo_all` 重新成为最值得优先轻量复核的头部候选。**

## 接下来优先级 Top 1~3

1. **先把 breakout 的 bench verdict 同步到 reader-facing 落点**
   - 沿 `breakout_live_seat_hard_verdict_20260316_0624.csv` 收口；
   - 明确它不再占用默认主资源；
   - 后续若要重回 Live Seat，必须先拿到 genuinely new blocker reduction。

2. **Scout Seat 回到主资源入口**
   - 先检查 `Rank 1 τ-band` 是否终于有 genuinely new local bar 可做 honest recheck；
   - 若仍没有，则只允许对 `Rank 2 combo_all` 做轻量 `forward` 复核，或切到 `Rank 3 third-touch + EMA/MACD confluence` 的最小 clean-room spec。

3. **small-live plumbing 继续沿执行链补相邻卡**
   - 优先 `reopen gate -> green resume row` 之后仍紧邻 ledger / route 的那一刀；
   - 不再回头写抽象 live rules 页。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `Live Seat verdict`：
  - 把 `breakout` 从 `keep but narrower-scope` 正式收口为 `bench`；
  - 明确它不再继续占用默认 bot3 主资源。
- 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：
  - 从“close 前打一枪 / close 后回 Paper”切到 “`bench sync -> Scout -> tiny-live`”。

### 这轮不改
- 不改 `Paper Seat`
- 不改 `Paper Seat = running paper pilot`
- 不改 `Scout shortlist` 本身
- 不改 cron 频率

## 风险与不确定性

1. `bench` 不等于永久删除 breakout；它只是停止默认资源投入，等待 genuinely new blocker reduction 再说。
2. `Rank 2 combo_all` 仍只是 `120d / 15m / 3` 币种口径，不能因为 breakout 被 bench 就直接偷升格成 Live Seat。
3. `EMA` 当前虽然继续是 running paper，但直到下一个真实 due 窗口前，都不该被误用成重复的主任务来源。

## 本轮一句话结论（给 Jerry）

**这轮 desk 最重要的变化，是我把 breakout 正式 bench 了：因为那次“唯一一枪”已经打过且 blocker 还是没降；EMA 继续坐 running paper 的 Paper Seat，但当前如实回到 waiting_not_due；所以接下来默认 bot3 资源应转回 `Scout Seat + tiny-live plumbing`，而不是继续在 breakout 上近义续命。**
