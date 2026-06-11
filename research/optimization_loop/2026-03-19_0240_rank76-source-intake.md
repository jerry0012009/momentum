# 2026-03-19 02:40 UTC｜Rank 76 / intraday clock polarity + event blackout gate source intake（guard-passed）

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 76 source intake + 两条轻量诚实守门`
- 紧邻子点：`TODO` 顶板 `Next 3 bot3 runs` 顺序刷新

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 当前无 `due-now / overdue` lane；最早 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 仍是真 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T02:26:30Z` 继续是 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。
- 上一轮 `Rank 75` 已在 minimal clean replication 后给出 **`park / evidence pool`** hard verdict；因此按顶板最新顺序，本轮合法主动作必须切到 fresh source，而不是继续围着 `Rank 75` 或 `P3` 托管位打转。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 76` source-intake script、artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 为什么这轮选 Rank 76
这轮先按当前板子显式比较 active Scout 候选的边际价值：
1. `Rank 76 / intraday clock polarity + event blackout gate`
2. `one-regime-per-session overlay`
3. `Rank 35b`
4. `Rank 16b`
5. `tiny-live plumbing`

先认领 `Rank 76` 的原因：
1. 它仍是 **paper-based / queue-facing** 的 shared gate，直接服务 `breakout-short / Fib retest_hold / EMA-PSAR` 三条当前 desk 主线；
2. 相比 `one-regime-per-session overlay`，它更接近当前允许动作：先给现有 archetype 一个 `continuation / reversal / neutral` session polarity allow-deny 层，而不是先做 desk-level allocation overlay；
3. 它不要求现在就开新大框架，先做 source intake + 两条守门就能诚实回答“值不值得进 minimal clean replication queue”；
4. `EMA = waiting_not_due`，且 `P3 continuity` 没有 status-changing event，因此这条 fresh Scout 候选正是当前默认优先项。

## 这轮冻结的两条轻量诚实守门
- `trade on`：先用 rolling 180d 的 hourly pocket 给 15m setup 打 `continuation / reversal / neutral` 极性标签；
  - `polarity=+1`：放宽 `breakout-short follow-up / EMA-PSAR continuation`
  - `polarity=-1`：放宽 `Fib retest_hold`
  - `polarity=0`：`half-size / no-trade`
  - 事件层只加最小 `FOMC ±2h blackout`
- `trade off`：若 polarity 没过最小显著门槛、当前小时仍是 `neutral`、或碰到 `FOMC blackout` 窗口，则 shared gate 只能 veto / half-size；它不能单独开仓，也不能自己创造方向。
- `lookahead / repaint / leakage`：hourly polarity 只能用当前小时及之前的 rolling 历史估计；FOMC blackout 只能使用事先公开的会议时点；desk 迁移必须统一冻结为 `signal 当根及之前数据 + next-bar open + no-overlap`，不能把未来小时关系或公告后反应倒灌回 gate。

## 本轮新增产物
1. Source-intake script：
   - `scripts/build_rank76_intraday_clock_polarity_source_intake.py`
2. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank76_intraday_clock_polarity_event_blackout_source_intake_card.csv`
3. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank76_intraday_clock_polarity_event_blackout_source_intake.html`
4. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`

## Hard verdict
**`Rank 76 / intraday clock polarity + event blackout gate = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它不是新 alpha，而是 shared `session-polarity / event-blackout` gate；
- 论文证据明确支持 crypto intraday relation 同时存在 momentum 与 reversal，不是默认全天同一逻辑；
- FOMC blackout 也能保持在诚实角色：只做低频风险 veto，不伪装成逐根 15m 主信号；
- 实现层口径可以冻结成 `signal 当根及之前数据 + next-bar open + no-overlap`，目前没有一眼可判死刑的 `lookahead / repaint / leakage`；
- 但它现在仍只是 admitted，不是已验证 alpha；下一轮若 minimal clean replication 发现改善主要来自极端砍单、跨 archetype 不稳、或只在局部时段 pocket 勉强成立，就应快速压回 `park / evidence pool`。

## 对交易台顺序的影响
- 当前最新 `Next 3` 已更新为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 Rank 76 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 76 这一轮给出 hard verdict，则先回到 fresh paper / repo source re-rank（默认比较 one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source）；只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`
- 本轮后，当前合法 fast-lane 头部已不再是 `Rank 75`，而是 `Rank 76 / intraday clock polarity + event blackout gate`。

## 最小验证
- 已实际运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank76_intraday_clock_polarity_source_intake.py`
- 已确认以下输出文件存在：
  - `reports/artifacts/literature/scout_rank76_intraday_clock_polarity_event_blackout_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank76_intraday_clock_polarity_event_blackout_source_intake.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 这条线的核心证据来自论文方法迁移，不是现成 15m 可部署 alpha；值钱的是 regime 口径，不是原文绩效可直接照抄。
- `event blackout` 很容易因为砍掉少量坏样本而看起来漂亮，因此下一轮 minimal clean replication 必须显式盯住 `trade_retention`，不能只看收益。
- 本轮只做到 source intake + 两条轻量诚实守门，不展开 clean replication，也不顺手去开第二条 fresh source。

## 下一步建议
- 直接按顶板切到 **`Rank 76 minimal clean replication`**。
- 默认只比较 `baseline / polarity_only / polarity_plus_blackout` 三臂，不把它扩成新的宏观事件大研究。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
