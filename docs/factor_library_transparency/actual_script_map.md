# 因子库真实执行链路与脚本地图

> Phase 12D-G-R2 · 验收级 · 研究解释页

## 一句话总览

这页不是代码目录，也不是全部脚本列表。它只解释当前因子库主链路中真正相关的脚本，以及哪些脚本属于其他 momentum 功能。

## 已验证脚本

| 功能 | 脚本 |
|------|------|
| 数据下载 | scripts/download_full_binance_1h_universe.py |
| Universe | scripts/build_crypto_top50_universe.py |
| Labels | scripts/build_labels.py |
| Factor Values | scripts/build_factor_values.py |
| Signal Panel | scripts/build_phase9b_signal_panel.py |
| Phase 10A | scripts/run_phase10a_signal_backtest.py |
| Phase 10A-R | scripts/run_phase10a_r_diagnostics.py |
| Phase 10B | scripts/run_phase10b_tail_diagnostics.py |
| Phase 10D | scripts/run_phase10d_tail_aware_variants.py |
| Phase 11A | scripts/run_phase11a_cost_slippage_capacity.py |
| Phase 12A | scripts/run_phase12a_paper_signal_harness.py |
| Phase 12B | scripts/run_phase12b_paper_monitoring.py |

## 已验证数据

- Bars: 3,316,259 rows, 266 symbols, 17,808 timestamps, no taker columns
- Labels: 215,061 rows, 50 symbols, 4 horizons (1h/4h/24h/72h)
- Signal panel: 3,314,397 rows, 266 symbols, 17,801 timestamps
- Universe: 1,250 snapshots, 266 symbols, PARTIAL survivorship bias

## Not for production use.
No real execution. No alpha claim. Phase 13 NOT STARTED.
