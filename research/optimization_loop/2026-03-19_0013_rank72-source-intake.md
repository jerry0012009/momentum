# Rank 72 / realized-vol mid-band cost-survival gate source intake（guard-passed）

## 轮次定位
- 时间：2026-03-19 00:13 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 72 source intake + 两条轻量诚实守门`
- 紧邻子点：`TODO 顶板顺序刷新`

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 显示全 desk 当前无 `due-now / overdue` lane；最早 due 点已切到 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 当前是真 `running paper / waiting_not_due`，不是可继续硬刷 refresh 的窗口。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T00:05:52Z` 仍是 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。
- 上一轮 `Rank 71` 已在 minimal clean replication 后给出 **`park / evidence pool`** hard verdict；因此按顶板顺序，本轮合法主动作必须回到 fresh source intake，而不是继续围着旧 rank 或 `P3 continuity` 打转。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 72` source-intake artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 为什么这轮选 Rank 72
本轮按当前 active Scout 候选重新比较边际价值：
- `Rank 72 / realized-vol mid-band cost-survival gate`
- `Rank 73 / PSAR close-confirmed follow-up gate`
- `Rank 35b / Rank 16b / tiny-live plumbing`

最终先认领 `Rank 72`，原因很直接：
1. `Rank 71` 刚证明“graded continuation score 还不够诚实”之后，当前 desk 更值得先回答的不是再加一个花哨打分，而是 **哪些 vol pocket 根本不该做**；
2. `Rank 72` 是三条主线共用的 shared allow/deny gate，覆盖 `breakout-short / Fib / EMA-PSAR`，边际价值比更单轴的 `Rank 73` 高；
3. 它只需要现有 `15m OHLCV` 就能起步，第一轮实现摩擦更低；
4. 它符合当前 Scout Seat 的预算：先 `source intake -> guard-passed`，若通过，再给 `1` 次最小 clean replication。

## 这轮冻结的两条轻量诚实守门
- `trade on`：base setup 继续负责方向、entry、exit；这条 gate 只回答当前 realized-vol pocket 是否放行。首轮冻结成两个便宜版本：
  - `no_high_vol_extreme`：仅剔除 `rv_pct >= 0.8`
  - `rv_midband_q20_80`：只保留 `0.2 <= rv_pct < 0.8`
- `trade off`：若结果只能靠把它包装成新的独立 regime alpha、同时偷改 entry/exit、或顺手引入未来窗口重算 percentile 才成立，则不应升格；它当前只能当 shared allow/deny gate，而不是新的 15m 开仓信号。
- `lookahead / repaint / leakage`：`rv20` 与 `rv_pct` 必须完全用 trailing 历史窗口计算；desk 迁移统一冻结成 `signal 当根及之前数据 + next-bar open + no-overlap`。第一轮只允许比较 `baseline / no_high_vol_extreme / rv_midband_q20_80` 三臂，不得把 PSY bubble、未来 realized vol、或事后 regime 标签偷渡进来。

## 本轮新增产物
1. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank72_realized_vol_midband_cost_survival_source_intake_card.csv`
2. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank72_realized_vol_midband_cost_survival_source_intake.html`
3. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `TRADING DESK BOARD`

## Hard verdict
**`Rank 72 / realized-vol mid-band cost-survival gate = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它只决定放不放行，不改原策略的方向和 entry；
- 首轮实现足够便宜：只靠现有 `15m OHLCV` 就能做 realized-vol gate，不需要先接更重的外部数据；
- 相比 `Rank 73`，它更像当前 desk 真正缺的 shared 生存门，而不是单轴 follow-up 口径；
- 但它现在仍只是 `guard-passed`，不是已验证 alpha；下一轮若 clean replication 发现改善只是靠大幅砍交易数，仍应快速压回 `park / evidence pool`。

## 对交易台顺序的影响
- 当前更诚实的 active Scout 顺序更新为：
  - `Rank 72 / realized-vol mid-band cost-survival gate`
  - `Rank 73 / PSAR close-confirmed follow-up gate`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 更新后的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 72 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  - `Run 3 = 若 Rank 72 这一轮直接 hard-fail / 未 admitted，则立刻切到 Rank 73 source intake；只有 fresh source 这一层也 exhausted，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已重新核对 `EMA due guardrail` 与 `manual_narrow_paper_lanes` 最新状态，确认本轮合法落在 `Scout Seat / fresh intake`。
- 已核对 `research/quant_digests/2026-03-18_2136_realized-vol-midband-cost-survival-gate.md`，并把最小可复刻口径冻结到 source-intake card / reader-facing 页面 / TODO 顶板。
- 已检查新增 card/html 文件存在且成功写入。

## 风险 / 边界
- 这条线来自论文读法与本地 pocket check，不是已经在当前 15m crypto 口径里验证通过的 execution-ready alpha；
- 它最容易犯的错，是靠大幅砍单换来一点点结果改善；若 clean replication 只剩“少做了很多”，就不该升格；
- 这轮只做到 source intake + 两条轻量诚实守门，不展开 clean replication，也不顺手去改 `Rank 73`。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
