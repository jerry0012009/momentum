# 2026-03-16 13:34 UTC · Desk Board Review

## 本轮一句话判断

**这轮不是简单巡检，而是把 desk 读法再收紧一层：`Paper Seat = EMA` 不变；`Live Seat` 当前应继续保持暂空，不强行给 breakout 或任何未过快筛的候选占位；`Scout Seat` 也不再按“谁有新 15m bar 就追谁”来排，而是明确按 `source intake -> clean replication -> Light Stability Pack -> paper candidate / park` 来分层。按这个口径，`Rank 2 combo_all` 现在最适合进入窄范围 `paper candidate pool`，`Rank 3 third_touch_plus_ema_macd` 仍停在 `Light Stability Pack`，`Rank 1 τ-band` 则应收口到 `park / evidence pool`。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮只做 `TRADING DESK BOARD` 顶部最小同步、review 记录、plans 镜像刷新与首页发布。
2. **最近 optimization logs**
   - `2026-03-16_1246_scout-rank2-shadow-readiness.md`
   - `2026-03-16_1302_scout-rank2-trade-count-honesty.md`
   - `2026-03-16_1315_scout-rank2-time-stability.md`
   - `2026-03-16_1334_scout-rank2-parameter-stability.md`
3. **最近 strategy review**
   - `12:50` 那轮已经把 routing 收紧成：Scout 默认先做历史样本上的 `verdict / friction / trade-count / shadow-readiness`，而不是继续把 continuity 当默认主点。
4. **当前 cron**
   - `bot2-strategy-review-40m`：running
   - `bot3-momentum-auto-opt-13m`：ok
   - `bot7-quant-digest-4h`：ok

## 当前 strongest evidence

1. **Paper Seat 继续是 EMA，且当前是真实 waiting_not_due**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
     - 美股下一次 close：`2026-03-16 20:00 UTC`
     - Crypto 1d 下一次 close：`2026-03-17 00:00 UTC`
     - A 股下一次 close：`2026-03-17 07:00 UTC`
   - 因此当前 `Paper Seat` 不换人，也不应该抢占 bot3 默认主资源。

2. **Live Seat 当前更该保持暂空，而不是继续强调 breakout**
   - `support_breakout_v0` 仍只有旧的 hard verdict：`breakout_live_seat_hard_verdict_20260316_0624.csv`
   - blocker 仍无 genuinely new reduction：
     - `pure_down = 0/100`
     - `predown_bridge_12h = 0/11`
     - `downrisk_48h = 0/109`
     - `future_pure_down_48h = 0/44`
   - 新规则也明确说：**当前 `Live Seat` 默认允许为空；不要为了“必须有 live challenger”而继续强调已 bench 的 breakout。**
   - 因此本轮更诚实的 desk call 是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 已经走完整个基础快筛，当前最像 `paper candidate`**
   - 来源：`Yumna et al. (2024)`，属于明确的 paper-based 15m crypto 候选；
   - 状态：`clean replication` 已跑通，且 `Light Stability Pack` 四件套已有最小版本：
     - 成本/跨标的基线：
       - `mean_total_return ≈ +2.33%`
       - `mean_false_break_ratio ≈ 6.67%`
       - `positive_asset_ratio = 2/3`
     - friction：`15bps` 下仍约 `+1.10%`
     - trade-count honesty：
       - 最小资产交易数 `5` 笔，月度分布过关；
       - 但 `idle_gap_guard` fail，最大空窗约 `58.6` 天
     - time stability：
       - `2/3` 时间窗口为正；
       - 但最早窗口是 `-1.34%` 且 `0/3` 资产为正，`false-break` 某窗口升到 `33.33%`
     - parameter stability：
       - `7/7` 参数邻域为正；
       - `6/7` 近邻保持 `>=2/3` 资产为正；
       - 最弱邻域仍约 `+0.03%`
   - 更诚实的结论：**它没有被快筛判死，也不该继续无限停在研究态；当前最合适的是把它升入窄范围 `paper candidate pool`，但保留 `one more light check` 标签，不偷升格成 Live Seat / tiny-live。**

4. **Rank 3 `third_touch_plus_ema_macd` 目前更像还在 Light Stability Pack，而不是 paper candidate**
   - 来源：`Wiśniewski (2024)`，属于 paper-based / clean-room 候选；
   - 已完成：`clean replication + first verdict + friction + 多次 continuity`；
   - 当前稳定读法仍是：
     - `mean_total_return ≈ +0.78%`
     - `mean_false_break_ratio = 0.00%`
     - `positive_asset_ratio = 1/3`
     - `10 / 15 / 20 bps` 下仍约 `+0.70% / +0.60% / +0.50%`
   - 但它还没像 Rank 2 那样把 `trade-count / time stability / parameter stability / shadow-readiness` 补齐成完整快筛，因此当前更诚实的阶段仍是：**`Light Stability Pack`**。

5. **Rank 1 `τ-band` 现在更适合收口到 park / evidence pool**
   - 来源：`De Angelis et al. (2021)`；
   - 已完成：`clean replication + first verdict + honest recheck`；
   - 但当前最佳版本 `confirm2of3_tau_010` 仍约：
     - `mean_total_return ≈ -11.16%`
     - `mean_false_break_ratio ≈ 41.03%`
     - `positive_asset_ratio = 0/3`
   - 因此它现在更适合当 execution guard 证据，不再占默认主资源。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 在没有被 desk 明确授权前，继续把 Rank 3 的新 completed `15m` bar continuity 当默认主点：继续 park。
- 在 `EMA waiting_not_due` 窗口里重开 EMA 发散研究：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；没有候选值得在这轮被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ `paper candidate`（窄范围 / one more light check）
  3. `third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `Light Stability Pack`

## 接下来优先级 Top 1~3

1. **把 Rank 2 `combo_all` 从 scout 结果卡推进成窄范围 `paper candidate` scope / admission memo**
   - 目标不是继续漂亮研究，而是把当前 scope、最小 ledger/monitoring、最关键 blocker 写清楚。

2. **给 Rank 3 补它还缺的 Light Stability Pack 项**
   - 优先 `trade-count / time stability`；
   - 不再默认追最新 completed `15m` bar continuity。

3. **tiny-live 继续沿 plumbing / closeout / registry 链补紧邻卡**
   - 作为 `Run 3` fallback；
   - breakout 继续留在证据池，不回到默认主资源位。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  1. 把 `Live Seat` 明确写成 `暂空 / waiting for next promoted scout winner`；
  2. 给 `Scout Seat` 补上一张当前候选阶段表（`park / Light Stability Pack / paper candidate`）；
  3. 把 `Next 3 bot3 runs` 改成当前更贴阶段推进的顺序：`Rank 2 paper-candidate scope -> Rank 3 Light Stability Pack -> tiny-live fallback`。
- 新增本轮 review：`research/strategy_review/2026-03-16_1334_strategy-review.md`

### 这轮不改
- 不改 `Paper Seat`
- 不改 cron 频率
- 不重开 breakout

## 风险与不确定性

1. `Rank 2 combo_all` 虽然现在最像 `paper candidate`，但它仍只覆盖 `120d / 15m / 3 assets`，且时间稳定性与 cadence 还有弱 pocket；因此当前只能给“窄范围 paper candidate”，不能偷写成 live-ready。
2. `Rank 3` 的 continuity 连续通过，不等于它自动比 Rank 2 更该升级；在它补完完整 `Light Stability Pack` 前，不该抢走默认主资源。
3. `Live Seat` 允许为空的纪律是正确的，但也意味着 bot2 接下来要更明确地区分“paper candidate”与“tiny-live candidate”，避免二者混写。

## 本轮一句话结论（给 Jerry）

**这轮真正的变化是：我把桌面重新排清楚了——EMA 继续坐 Paper Seat，Live Seat 继续暂空；Scout 这边不再泛讲“谁有新 bar”，而是明确分层：Rank 1 进 park，Rank 3 还在 Light Stability Pack，Rank 2 `combo_all` 则最适合先升到窄范围 `paper candidate pool`。**
