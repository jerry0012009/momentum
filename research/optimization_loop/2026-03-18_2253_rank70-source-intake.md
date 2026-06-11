# Rank 70 / fast-entry slow-exit handoff spine source intake（guard-passed）

## 轮次定位
- 时间：2026-03-18 22:53 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / fresh paper-repo intake -> Rank 70 source intake + 两条轻量诚实守门`
- 紧邻子点：`queue-facing 更新（TODO 顶板）`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无新的 `due-now / overdue`；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- 上一轮 `Rank 69` 已在 minimal clean replication 后给出 `park / evidence pool`，因此按顶板顺序，本轮不得继续围着旧 rank 或 `P3 continuity` 打转，必须回到 `fresh paper / repo intake`。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 70` 对应 source-intake artifact、reader-facing 页面、TODO 顶板更新与本轮日志，不做混提。

## 为什么这轮选 Rank 70
这轮按 7.10 先比较当前允许动作的边际价值：
- `Rank 70 / fast-entry slow-exit handoff spine`
- `realized-vol mid-band cost-survival gate`
- `PSAR close-confirmed follow-up gate`
- `Rank 35b / Rank 16b / tiny-live plumbing`

本轮最终认领 `Rank 70`，原因很直接：
1. 当前三条主线的 entry 端已经很拥挤，继续叠一个新 veto 边际价值下降；
2. 这条 fresh repo 直接补的是三条主线共同缺位的 **post-confirmation 持仓时钟**；
3. repo 已把“快 entry / 慢 exit”写成了可冻结的参数骨架，source intake 成本低；
4. 它是 `paper / repo based` 的 `15m` 近邻候选，符合当前 Scout Seat 只认领一条 fresh source 的预算约束。

## 这轮冻结的两条轻量诚实守门
- `trade on`：base setup 继续负责 entry 方向与价位；这条 spine 只负责 post-entry 管理：前 `2~3` 根 bar 先沿用 fast failure check，若 trade 已存活且达到最小顺向展开（如存活满 `3` 根或浮盈 `>=0.75 ATR`），则 handoff 到 slow Donchian / ATR Chandelier exit；它不单独开仓，不改 entry alpha。
- `trade off`：若优势只能靠同时重写 entry、靠 long-only 源码自动偷渡 short mirror、或靠超细 hyperopt 参数才能成立，则不应升格；它只能回答“活下来后该不该继续拿”，不是新的 15m 入场按钮。
- `lookahead / repaint / leakage`：desk 迁移时必须冻结为 `entry 不变、exit-only 对照`，统一 `signal 当根及之前数据 + next-bar open + no-overlap`；首轮只允许比较 `baseline exit / all-fast fail / all-slow trailing / handoff` 四臂，不得把 hyperopt 结果、未来高点回看、或主观 ROI table 偷渡进第一轮。

## 本轮新增产物
1. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank70_fast_entry_slow_exit_handoff_source_intake_card.csv`
2. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank70_fast_entry_slow_exit_handoff_source_intake.html`
3. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已补 `2026-03-18 22:53 UTC` 最新块。

## Hard verdict
**`Rank 70 / fast-entry slow-exit handoff spine = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它是 shared post-entry management spine，不是新的独立 alpha。
- repo 已把快 entry / 慢 exit 写成了可直接冻结的参数骨架，首轮迁移成本低。
- 相比继续往 entry 端堆新 gate，它更直接服务当前 desk 三条主线共同缺的持仓时钟问题。

## 对交易台顺序的影响
- 当前更诚实的 active Scout 顺序更新为：
  - `Rank 70 / fast-entry slow-exit handoff spine`
  - `realized-vol mid-band cost-survival gate`
  - `PSAR close-confirmed follow-up gate`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 更新后的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 70 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  - `Run 3 = 若 Rank 70 clean replication 后仍不能升到更高层 verdict，则优先回到 fresh source 比较 realized-vol mid-band > PSAR close-confirmed follow-up；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已重新核对 `EMA due guardrail` 与 `manual_narrow_paper_lanes` 最新状态，确认本轮合法落在 `Scout Seat / fresh intake`。
- 已核对 `research/quant_digests/2026-03-18_2250_fast-entry-slow-exit-handoff-spine.md` 并把最小可复刻口径冻结到 source-intake card / reader-facing 页面 / TODO 顶板。
- 已检查新增 card/html 文件存在且成功写入。

## 风险 / 边界
- 这份 repo 是工程 repo，不是已经充分 OOS 证明的论文；当前仍只是 `guard-passed`，不是已验证 alpha。
- 源码主版本偏 `long-only`；short-side chandelier / Donchian 镜像必须在 clean replication 里单独检验，不能自动当对称成立。
- slow exit 很可能只是把 winner 拖长，也可能把利润吐回去；下一轮 minimal clean replication 必须把 `MFE_capture_ratio` 与 `giveback_after_handoff` 一起看。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
