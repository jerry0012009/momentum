# Rank 66 / exec-TF switch alignment gate source intake（guard-passed）

## 轮次定位
- 时间：2026-03-18 20:29 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / fresh source intake`（从当前 Next 3 认领）
- 紧邻子点：`queue-facing 更新（TODO 顶板）`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无 `due-now / overdue`；最早是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 仍 `new_closed_trades_appended=0`，无 status-changing event。
- `Rank 65`：上一轮 minimal clean replication 后因 `stress_event coverage = 0` 已给出 `park / evidence pool` 硬结论。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只做最小新增，不做混提。

## 本轮先做的边际价值比较（active Scout）
`Rank 66 / exec-TF switch alignment gate` > `Rank 67 / regime-matrix shared-state gate` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`

结论：本轮主资源认领 `Rank 66 / exec-TF switch alignment gate`。

## 这轮完成的产物
1. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank66_exec_tf_switch_alignment_source_intake_card.csv`
2. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank66_exec_tf_switch_alignment_source_intake.html`
3. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已补 `2026-03-18 20:29 UTC` 最新块。

## 两条轻量诚实守门
- `trade on`：base setup 继续负责方向与价位；Rank 66 只回答“4H bias 与 1H trend 同向时，是否允许把触发从 15m 切到 5m BOS；若不对齐，则坚持 15m 确认”。
- `trade off`：若优势主要来自 repo 里整包 `sweep / OB / FVG / breaker / pressure`，或 5m 只是放大噪声与过度成交，不应升格。
- `lookahead / repaint / leakage`：首轮只允许用 `5m / 15m / 1h / 4h` 当根及之前 OHLCV；执行统一 `next-bar open + no-overlap`，先拆 `base_15m_only / always_5m_confirm / alignment_switch / alignment_switch+pressure` 四臂。

## Hard verdict
**`Rank 66 / exec-TF switch alignment gate = guard-passed / admit_to_clean_replication_queue`**

## 更新后的 Next 3
- `Run 1 = EMA due-check only`
- `Run 2 = 若 Rank 66 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
- `Run 3 = 若 Rank 66 clean replication 后仍不能给出更高层 verdict，则再比较 Rank 67 / regime-matrix shared-state gate；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 本轮验证
- 已再次核对 due guardrail 与 P3 托管状态。
- 已用 quant digest + repo 原始 Pine 代码冻结最小可复刻口径。
- 本轮未跑重型下载 / 未追新 bar。

## 提交
- 未提交（工作区有大量无关脏文件，避免混提）。