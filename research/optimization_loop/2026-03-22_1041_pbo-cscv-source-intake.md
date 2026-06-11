# bot3 optimization loop — 2026-03-22 10:41 UTC — pbo-cscv-source-intake

> 约束：按 TRADING DESK BOARD 的 Next 3 bot3 runs 执行（Run1→Run2→Run3）。本轮只做 1 个主交付：为 `pbo-cscv / deflated sharpe honesty gate` 补 **1 个权威 source intake + 人话摘要**。

## Run 1 — EMA due-check first（Paper Seat）

- 检查 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：
  - `创业板ETF 1d (active_primary)` 当前 `waiting_not_due`
  - `latest_completed_bar_utc=2026-03-20 00:00 UTC`
  - `next_expected_close_utc=2026-03-23 07:00 UTC`
  - 因此本轮 **不做伪 refresh**（保持 queue/ledger 口径，等 close 到点再做 due-now/overdue）。

结论：Run1 为 `waiting_not_due`，不占用本轮主资源位。

## Run 2 — Rank139(P3) hosted narrow paper pilot 低频健康检查

按 desk 规则，只做 1 件事：确认 ops page/CSV 是否持续可更新，粗扫 `no_event_timeout` 是否爆雷。

- 执行：`python3 scripts/build_rank139_narrow_paper_pilot_minimal.py`（刷新监控页/CSV 的 generated_at 与 refresh clock）。
- 观察（来自 `narrow_paper_pilot_monitoring_board.csv` 结构）：
  - `no_event_timeout_rate` 在 asset×setup 维度 **最高约 27.8%**（主要出现在 `fib_retest_long` / `breakout_short` 部分格子）
  - desk 默认 gate（`confirm_same_dir_only@thr_mult=0.8`）在 summary 维度的 `no_event_timeout` 仍为 **0%**（此处口径是：仅保留 `same_dir_first` 的交易，因此 timeout 被自然排除；这本身提示我们：健康检查时要同时盯 `retention` 与 “timeout 在 baseline 上的占比”，避免被口径掩盖）。

结论：Rank139 pilot artifacts **可持续刷新**，未见需要抢占主资源的“爆雷级”异常。

## Run 3 — pbo-cscv honesty gate：source intake（本轮主交付）

### 锁定的权威参考（1 组核心来源）

> 目标：让 `pbo-cscv` 不再停留在“proxy demo”，而是有一个可引用、可解释、可对齐实现细节的 canonical 来源。

1) **Probability of Backtest Overfitting (PBO) + CSCV（核心定义来源）**
- Authors: David H. Bailey, Jonathan M. Borwein, Marcos López de Prado, Qiji Jim Zhu
- Title: *The Probability of Backtest Overfitting*
- Where: 最早为 SSRN working paper，后续进入期刊版本（常被引用为 PBO/CSCV 的 canonical 来源）
- Why relevant: 这篇定义了 **CSCV（combinatorially symmetric cross-validation）** 的切分方式，并给出 **PBO** 的估计框架：当你在一堆策略/参数里挑最强回测结果时，OOS 失败的概率到底有多大。

2) **Deflated Sharpe Ratio (DSR)（对“挑出来的 Sharpe”做偏差折扣）**
- Authors: David H. Bailey, Marcos López de Prado
- Title: *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*
- Where: Journal of Portfolio Management（经典引用版本）
- Why relevant: DSR 提供一个把 “观测到的 Sharpe” 折算为 **更可信的显著性/置信度** 的方法，显式考虑：
  - 你试了很多策略（selection bias / multiple testing）
  - 收益分布偏离正态（non-normality）
  - 样本长度有限

> 备注：我们后续若要做更强的“工程化权威入口”，可以直接引用 Marcos López de Prado 的书 *Advances in Financial Machine Learning*（2018）相关章节：它把 PBO/CSCV/DSR 作为 ML-for-trading 的反过拟合基础设施来讲，适合作为团队内部的统一口径。

### 人话摘要：这三样东西在 desk 里各自“干嘛用”

- **CSCV**：不是普通 k-fold。它把样本分成 N 片，然后用“组合方式”构造很多 IS/OOS 配对，让你在同一份历史上得到大量、对称的 out-of-sample 检验，从而更像在问：
  - “如果我在这段数据里挑了一个最强参数，它在另一段数据里大概率会怎样？”

- **PBO**：给一个概率式的警报灯。
  - 如果 PBO 很高，意思是：你看到的回测冠军很可能是“挑出来的幻觉冠军”。
  - 这比只看 Sharpe/收益率更贴近我们当下的痛点：scout 池越来越大时，最怕“赢在筛选，不赢在未来”。

- **DSR**：把 Sharpe 做“折扣”。
  - 你试了 100 个策略，最大的那个 Sharpe 当然会被抬高；DSR 会把这种“运气加成”扣掉。
  - 适合当作 `honesty-layer` 的输出：给每个候选一个更诚实的“可信度分数”，决定它是否还能占用 paper/live seat。

### 对当前项目的最小落地建议（不扩 scope）

- pbo-cscv 的定位维持不变：**honesty-layer**，不直接产 signal。
- 近期最小交付可以是：
  1) 在 `scripts/build_pbo_cscv_dsr_scorecard.py` 旁边新增一个 `references` 段落（写到报告或 site 页），把上述 2 个 canonical 来源固定下来；
  2) 给当前 Rank139 / Rank125 这类候选补一行 DSR/PBO 解释字段：
     - “这个 uplift 在多重筛选下是否还显著？”

---

## Appendix — 本轮生成/更新的可见性落点

- Rank139 monitoring board（脚本刷新）：
  - `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_monitoring_board.html`
  - `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`

