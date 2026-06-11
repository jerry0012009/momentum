# 2026-03-19 11:49 UTC — Rank 88 宏观事件 blackout overlay source intake

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1396`
  - 最近 optimization logs 最新到 `11:26 UTC / Rank 87 clean replication -> park`
  - 当前工作区存在大量与本轮无关的脏文件，因此本轮不提交，避免混提。
- 已再实查当前席位状态：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 继续显示全 desk **无 `due-now / overdue`**，各 lane 仍是 `waiting_not_due`
  - `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T11:15:26Z` 显示 `new_closed_trades_appended=0`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮合法主动作必须落在 `Scout Seat`，不能伪造 refresh，也不该回头做 `P3 continuity`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / fresh paper intake`，认领 `Rank 88 / macro-event blackout + size-down risk overlay`
- **紧邻子点**：把 `TRADING DESK BOARD / Next 3` 改写到 `Rank 88`，并补一个 reader-facing intake 落点

## 先比较 active Scout 候选边际价值（3.5）
本轮显式比较后，当前更诚实顺序为：
1. `Rank 88 / macro-event blackout + size-down risk overlay`
2. 两条 breakout-centric digest backlog：
   - `outside-close -> back-inside-close failure verdict`
   - `close-range compression asymmetry`
3. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

为什么本轮该先拿 `Rank 88`：
- 它是 **shared risk overlay**，同时服务 `breakout-short / Fib retest_hold / EMA-PSAR`，边际价值高于继续磨单条 breakout 叙事；
- 实现更便宜，只需要公开日程 + 固定时间窗，不需要立刻追加新重型数据链路；
- 更符合当前 desk 纪律：`EMA waiting_not_due -> Scout Seat -> fresh intake（默认优先非 breakout-centric）`。

## 本轮 hard verdict
- **`Rank 88 / macro-event blackout + size-down risk overlay = guard-passed / admit_to_clean_replication_queue`**

### 两条轻量诚实守门（已冻结）
- **trade on**
  - base setup 继续负责方向、entry、exit；
  - overlay 只回答事件窗内是否要 `blackout / size-down`；
  - 首轮冻结为：`baseline / blackout[-1h,+1h] / size_down_0.5x / hybrid[-30m,+30m] blackout + [+30m,+120m] size_down`。
- **trade off**
  - 若不在事件窗内，overlay 不得强行改动原始信号；
  - 若只是事后觉得“这根像新闻 bar”，也不能倒灌成 veto；
  - 这条线不是独立 alpha，只能做 shared risk overlay / sizing。
- **lookahead / repaint / leakage**
  - 事件时间只能来自事前公开的官方发布时间；
  - 迁移口径统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap`；
  - 禁止把公告后 realized move、未来 volatility、人工补标 risk window 倒灌回 gate。

## 本轮新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/literature/scout_rank88_macro_event_blackout_source_intake_card.csv`

### reader-facing 网页
- `reports/site/reading/repo_scout/rank88_macro_event_blackout_source_intake.html`

### 已复用的现成证据
- digest：`research/quant_digests/2026-03-19_1128_macro-news-event-blackout-risk-overlay.md`
- quickcheck：
  - `reports/artifacts/literature/macro_event_overlay_quickcheck_events_2026-03-19.csv`
  - `reports/artifacts/literature/macro_event_overlay_quickcheck_summary_2026-03-19.csv`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `11:47 UTC` 补充，冻结 `Rank 88` 的 source intake 与两条轻量诚实守门；
- 当前 active Scout 顺序改为：`Rank 88 > 两条 breakout-centric backlog > Rank 82/80/81 evidence_pool > P3 continuity > tiny-live plumbing`；
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 Rank 88 仍 guard-passed 且 EMA 继续 waiting_not_due，则给 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 88 直接 hard-fail / park，则回到两条 breakout-centric backlog；只有 fresh backlog 也 exhausted 时，才回退到 Rank 82/80/81 evidence_pool > tiny-live plumbing`

## 最小验证
- 已读取并确认：
  - `docs/TODO.md` 新补充已写入；
  - `scout_rank88_macro_event_blackout_source_intake_card.csv` 已生成；
  - `rank88_macro_event_blackout_source_intake.html` 已生成并可读。
- 本轮只做文档 / artifact / board 写回，未新增重型回测或下载。

## 脏文件与提交
- 当前 repo 脏文件很多，且绝大多数与本轮无关；
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，默认只给 `Rank 88` **1 次最小 clean replication**：
  - 固定 `BTC/ETH/SOL 15m`
  - 固定 `next-bar open + no-overlap`
  - 比较 `baseline / blackout / size-down / hybrid`
  - 直接做 `keep_P1 / promote_to_P2 / park` 判断
- 若 `Rank 88` 一轮就证明只是靠大幅砍交易数换表面改善，则应快速压回 `park`，不要继续磨宏观叙事页。
