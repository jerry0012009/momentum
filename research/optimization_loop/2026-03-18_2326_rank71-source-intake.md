# Rank 71 / EMA-VWAP-ATR-volume graded admission score source intake（guard-passed）

## 轮次定位
- 时间：2026-03-18 23:26 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / fresh paper-repo intake -> Rank 71 source intake + 两条轻量诚实守门`
- 紧邻子点：`queue-facing 更新（TODO 顶板）`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无新的 `due-now / overdue`；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-18T22:58:30Z` 仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- 上一轮 `Rank 70` 已在 minimal clean replication 后给出 `park / evidence pool`，因此按顶板顺序，本轮不得继续围着旧 rank 或 `P3 continuity` 打转，必须回到 `fresh paper / repo intake`。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 71` 对应 source-intake artifact、reader-facing 页面、TODO 顶板更新与本轮日志，不做混提。

## 为什么这轮选 Rank 71
这轮按 7.10 先比较当前允许动作的边际价值：
- `Rank 71 / EMA-VWAP-ATR-volume graded admission score`
- `realized-vol mid-band cost-survival gate`
- `PSAR close-confirmed follow-up gate`
- `Rank 35b / Rank 16b / tiny-live plumbing`

本轮最终认领 `Rank 71`，原因很直接：
1. 当前 desk 已经堆了不少单轴 veto / follow-up / fail-fast 线索，但还缺一个把这些 continuation 条件**统一收束**的口径；
2. 这条 fresh repo 直接补的是 `EMA / PSAR raw alpha focus` 当前最缺的“graded admission”层，而不是再加一个新的二元开关；
3. repo 源码已经把 `EMA gap / ATR`、`VWAP gap / ATR`、`volume`、`ATR expansion` 写成可冻结的 4 块 score，首轮迁移成本低；
4. 它是 `paper / repo based` 的 `15m` 近邻候选，符合当前 Scout Seat 只认领一条 fresh source 的预算约束。

## 这轮冻结的两条轻量诚实守门
- `trade on`：base setup 继续负责方向与入场价位；这条 overlay 只负责 continuation 质量打分。第一轮冻结成四块各 `25` 分：`EMA spread / ATR`、`price-VWAP distance / ATR`、`volume > SMA20`、`ATR14 > ATR14-MA14`，总分 `0~100`。
- `trade off`：若结果只能靠把它当独立新策略、同时重写 entry、引入 0DTE 专属时段过滤、或马上优化权重/阈值才能成立，则不应升格；它当前只能是 shared continuation overlay，不是新的 15m 开仓按钮。
- `lookahead / repaint / leakage`：desk 迁移时必须冻结为 `signal 当根及之前数据 + next-bar open + no-overlap`；首轮只允许保留现成 trigger，不改 entry，只比较 `baseline（二元 gate） / score>=60 / score>=75 / bucket(<60,60~74,>=75)` 四档；不得把 event-anchored VWAP、未来 ATR、或主观权重调参偷渡进第一轮。

## 本轮新增产物
1. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank71_ema_vwap_atr_volume_score_source_intake_card.csv`
2. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank71_ema_vwap_atr_volume_score_source_intake.html`
3. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已补 `2026-03-18 23:26 UTC` 最新块。

## Hard verdict
**`Rank 71 / EMA-VWAP-ATR-volume graded admission score = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它不是新的独立 alpha，而是给已有 continuation 条件做统一打分。
- 首轮迁移不需要额外微结构 / OI / 事件锚点，只靠现有 `15m OHLCV + session VWAP + ATR` 就能起步。
- 相比继续认领 `realized-vol mid-band` 或 `PSAR close-confirmed`，它更能直接回答当前 desk 真空位：**continuation 应该 binary 还是 graded**。

## 对交易台顺序的影响
- 当前更诚实的 active Scout 顺序更新为：
  - `Rank 71 / EMA-VWAP-ATR-volume graded admission score`
  - `realized-vol mid-band cost-survival gate`
  - `PSAR close-confirmed follow-up gate`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 更新后的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 71 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  - `Run 3 = 若 Rank 71 clean replication 后仍不能升到更高层 verdict，则优先回到 fresh source 比较 realized-vol mid-band > PSAR close-confirmed follow-up；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已重新核对 `EMA due guardrail` 与 `manual_narrow_paper_lanes` 最新状态，确认本轮合法落在 `Scout Seat / fresh intake`。
- 已核对 `research/quant_digests/2026-03-18_2318_ema-vwap-atr-volume-graded-admission-score.md` 并把最小可复刻口径冻结到 source-intake card / reader-facing 页面 / TODO 顶板。
- 已检查新增 card/html 文件存在且成功写入。

## 风险 / 边界
- 这份 repo 是 0DTE intraday 风格，不是已经充分 OOS 证明的 crypto 15m continuation 论文；当前仍只是 `guard-passed`，不是已验证 alpha。
- `session VWAP` 在 crypto 24/7 环境里可能偏弱；若首轮 score 结果一般，不应急着调权重，而应先区分问题到底出在 `score` 结构，还是出在 `VWAP anchor`。
- 四块各 `25` 分是便宜 baseline，不应在 source-intake 阶段就把“分值好看”误当成 `P2` 证据。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
