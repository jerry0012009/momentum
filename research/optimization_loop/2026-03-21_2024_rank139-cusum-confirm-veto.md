# bot3 optimization loop — 2026-03-21 20:24 UTC — Rank 139 CUSUM confirm/veto minimal clean replication

## Context（TRADING DESK BOARD / Next 3 runs）
- Run 1：EMA due-check first（若 waiting_not_due 不得空转）
- Run 2：若 EMA 仍 waiting_not_due → 执行 Rank 139 最小 clean replication
- Run 3：根据 Rank 139 结果给 promote/keep/park 硬结论

本轮严格按顺序执行 Run1→Run2→Run3。

---

## Run 1 — EMA due-check（require-due）
执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果（脚本输出要点）：
- **无 due-now / overdue lane**，因此本轮不允许跑 full refresh（避免伪 refresh）。
- 最靠前 due：**Crypto 1d+1wk（BTC/ETH/SOL）约 3.6 小时后到点**。
- 其他：创业板ETF 1d / 贵州茅台 1d+1wk 约 34.6 小时后到点。
- 结论：**EMA = waiting_not_due**，合法切到 Scout Seat。

---

## Run 2 — Rank 139 minimal clean replication（CUSUM first-event confirm/veto）
执行：
```bash
python3 scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py
```
产物：
- artifacts：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
- report：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

关键读数（跨 BTC/ETH/SOL × 3 个 setup 汇总；成本 6bps/side；hold=8×15m；阈值=thr_mult×ATR15m%）：
- baseline：**mean_net@6bps ≈ -0.1548%**（141 trades，总体为负）
- **veto_opp_dir**（先出现反向事件则否决该笔）：
  - thr=0.8：trades=70（retention≈49.65%），**mean_net@6bps ≈ +0.3423%**，positive_ratio_net≈51.43%
  - thr=0.6：trades=66（retention≈46.81%），mean_net@6bps≈+0.1957%
- confirm_same_dir_only（只保留 same_dir_first）：
  - thr=0.8：trades=43（retention≈30.50%），mean_net@6bps≈+0.5363%，positive_ratio_net≈60.47%

备注（守门约束）：为避免本轮变成 API 压测，脚本对每个 asset×setup 只取最近 18 个信号样本做最小复现；属于“方向性 verdict”而非最终定量结论。

---

## Run 3 — Hard verdict（promote/keep/park）
**Hard verdict：`Rank 139 = promote_P2（paper candidate / shared confirm-veto layer）`**。

理由（按 desk 口径）：
- `veto_opp_dir` 在 **retention 仍约 50%** 的前提下，能把成本后期望从 baseline 的负值拉到明显正值（thr=0.8 时 mean_net@6bps≈+0.34%）。
- `confirm_same_dir_only` 虽更强，但 retention 塌到 ~30%，更像后验筛选；不作为当前主升格依据。

下一步（留给下一轮 / 不在本轮扩写）：
- 对 `veto_opp_dir @ thr=0.8` 做一次 **更完整样本** 的 replication（仍固定 BTC/ETH/SOL 15m baseline + 1m confirm 数据），验证 uplift 是否稳定、是否只来自样本波动。

---

## Notes / Ops
- 本轮没有触碰 P3 narrow paper lanes（无 status-changing event）。
- 本轮已生成 Rank 139 网页落点，待首页 index 刷新后外显。
