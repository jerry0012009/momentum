# Rank 69 / IVU 开盘量不确定性 gate source intake（guard-passed）

## 轮次定位
- 时间：2026-03-18 22:23 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / fresh paper-repo intake -> Rank 69 source intake + 两条轻量诚实守门`
- 紧邻子点：`queue-facing 更新（TODO 顶板）`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无新的 `due-now / overdue`；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- 上一轮 `Rank 68` 已在 minimal clean replication 后给出 `park / evidence pool`，因此按顶板顺序，本轮不得继续围着旧 rank 或 `P3 continuity` 打转，必须回到 `fresh paper / repo intake`。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 69` 对应 source-intake artifact、reader-facing 页面、TODO 顶板更新与本轮日志，不做混提。

## 为什么这轮选 Rank 69
这轮按 7.10 先比较三个允许来源里的当前边际价值：
- `Rank 69 / IVU opening-volume uncertainty gate`
- `realized-vol mid-band`（与已 park 的 `Rank 23` 波动口径重叠更高）
- validated shortlist 里的通用结构 / TSM 论文（更像研究地基，不像当前 fast-lane 可直接冻结的 15m gate）

本轮最终认领 `Rank 69`，原因很直接：
1. 只依赖现有 `15m OHLCV volume`，不需要额外微结构 / OI / 外部 feed；
2. 直接服务 `breakout-short / Fib retest_hold / EMA-PSAR` 三条主线；
3. 比继续写一个泛化的波动过滤层更不重叠；
4. 已有 fresh digest，可立即冻结成 queue-facing 候选，而不是继续停留在线索态。

## 这轮冻结的两条轻量诚实守门
- `trade on`：base setup 继续负责方向与价位；这条 gate 只回答固定 session anchor 后，是否出现“高开盘量 + 低 IVU（首段量占前 7 段总量比偏低）”的 continuation-friendly 状态；它只能给三条主线做 shared allow/deny 或一档降仓，不单独开仓。
- `trade off`：若开盘量不高、IVU 不在低区间，或优势必须依赖股票收盘结构、复杂 ML 分类器、未来 session 成交分布、或主观锚点微调才成立，则不应升格；它只能是 shared regime gate，不是新的逐根 15m 主信号。
- `lookahead / repaint / leakage`：首轮只允许使用固定 session anchor 后前 `7` 根已完成 `15m` bar 的 volume 计算 IVU，统一 `next-bar open + no-overlap`；禁止把论文里的 logistic/XGBoost 结果、未来 session 量分布、或主观锚点微调偷渡进第一轮。

## 本轮新增产物
1. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank69_ivu_opening_volume_uncertainty_source_intake_card.csv`
2. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank69_ivu_opening_volume_uncertainty_source_intake.html`
3. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已补 `2026-03-18 22:23 UTC` 最新块。

## Hard verdict
**`Rank 69 / IVU opening-volume uncertainty gate = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它不是再造一个独立 alpha，而是给已有三条线加一个共享 continuation gate。
- 首轮迁移只需要现有 `OHLCV volume`，实验成本比当前 fresh alternatives 更低。
- 与当前 desk 主线的耦合足够直接，而且比 generalized vol gate 更不容易和已 park 的旧 vol/regime 轴混成同一件事。

## 对交易台顺序的影响
- 当前更诚实的 active Scout 顺序更新为：
  - `Rank 69 / IVU opening-volume uncertainty gate`
  - `fresh source（next）`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 更新后的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 69 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  - `Run 3 = 若 Rank 69 clean replication 后仍不能给出更高层 verdict，则继续按 7.10 再认领 1 条新的 5m / 15m crypto source；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已重新核对 `EMA due guardrail` 与 `manual_narrow_paper_lanes` 最新状态，确认本轮合法落在 `Scout Seat / fresh intake`。
- 已核对 `research/quant_digests/2026-03-18_2229_ivu-opening-volume-uncertainty-gate.md` 并把最小可复刻口径冻结到 source-intake card / reader-facing 页面 / TODO 顶板。
- 已检查新增 card/html 文件存在且成功写入。

## 风险 / 边界
- 原论文样本是中国股票 `30m`，不是 crypto `15m`；这条线当前仍只是 `guard-passed`，不是已验证 alpha。
- session anchor 选择会明显影响 IVU 稳定性；下一轮 minimal clean replication 必须把 `anchor` 与 `threshold` 先冻结，再回答它到底是 shared gate 还是只是“砍样本换胜率”。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
