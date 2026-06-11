# bot3 optimization loop — 2026-03-22 12:16 UTC — ema-waiting_rank139-health_pbo-cscv-scorecard-refresh

> 约束：严格按 `docs/TODO.md` 顶部 TRADING DESK BOARD 的 **Next 3 bot3 runs**（Run1→Run2→Run3）；Run1 若 `waiting_not_due` 不空转，立刻切到下一允许动作；本轮只做 **1 个主点 + 1 个紧邻子点**。

## Run 1 — EMA due-check first（Paper Seat）

- 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：**waiting_not_due**（无 `due-now / overdue` lane）
  - Crypto 1d+1wk（BTC/ETH/SOL）：约 **11.7h** 后到点
  - 创业板ETF 1d：约 **18.7h** 后到点
  - 贵州茅台 1d+1wk：约 **18.7h** 后到点

结论：不做伪 refresh；按规则立即切到 Scout Seat。

## Run 2 — Rank 139（P3）hosted narrow paper pilot：低频健康检查（只做 1 件事）

目标：确认 ops/CSV 仍在更新，并粗扫是否出现“爆雷级”信号（`no_event_timeout_rate` 异常偏高 / retention 全盘崩塌）。

- refresh clock：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_refresh_clock.json`
  - `generated_at_utc = 2026-03-22 11:16 UTC`
- monitoring board：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`
  - 当前格子级 `no_event_timeout_rate` 大致 **0.056 ~ 0.273**（未见不可解释的极端爆表）
  - retention 有高低分化，但未见“全盘崩塌”

结论：Rank139 hosted pilot 仍在持续更新；按 desk 口径继续低频健康检查即可。

## Run 3 — pbo-cscv honesty gate：离线 scorecard 刷新（本轮主交付）

目的：把 `pbo-cscv / DSR` 从“概念/引用”压到一个可重复跑、可审计的离线 scorecard（用于 scout honesty-layer，而非直接产 signal）。

- 执行：
  - `python3 scripts/build_pbo_cscv_dsr_scorecard.py \
    --trade-log reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/trade_log.csv \
    --event-col event_0.8 \
    --out-dir reports/artifacts/pbo_cscv_honesty_gate \
    --label "Rank139 thr=0.8 offline honesty gate"`
- 产出：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_scorecard.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_meta.json`
- 最新 meta：`generated_at_utc = 2026-03-22 12:21 UTC`

关键读数（scorecard 头部行）：
- PBO（CSCV 估计）：`pbo = 0.1714` → **verdict=guard_passed**（在“多臂筛选”语境下不算高到离谱）
- baseline：`mean_net@6bps = -0.1549%`、`dsr_probability ≈ 0.0036`
- `confirm_same_dir_only`：`mean_net@6bps = +0.5370%`、`sharpe ≈ 0.365`、`dsr_probability ≈ 0.881`
- `veto_opp_dir`：`mean_net@6bps = +0.3428%`、`sharpe ≈ 0.268`、`dsr_probability ≈ 0.839`

结论：这份离线 scorecard 继续支持“Rank139 的 post-entry confirm/veto uplift 不完全是筛选幻觉”，可以作为后续把 `pbo-cscv` 固化为 desk honesty-layer 的最小可审计砖（但仍明确：这是近似实现，不是 library-grade 统计包）。
