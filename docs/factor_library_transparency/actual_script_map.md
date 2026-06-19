# 因子库真实执行链路与脚本地图

> Phase 12D-H3-R · 研究解释页

## 一句话总览

这页不是代码目录，也不是全部脚本列表。它只解释当前因子库主链路中真正相关的脚本，以及哪些脚本属于其他 momentum 功能。

## 活跃入口点

**`scripts/evaluate_signals.py`** — 规范的信号评估 CLI 入口，使用 `momentum.signal_evaluation` 公共 API。

```bash
python scripts/evaluate_signals.py \
    --signal-panel <path> --labels <path> \
    --signals signal_v0_core_only --horizons 1h 4h 24h 72h \
    --output-dir <dir> [--spread-mode standard|legacy_phase10a]
```

## 已验证脚本（活跃 pipeline）

| 功能 | 脚本 |
|------|------|
| 数据下载 | `scripts/download_full_binance_1h_universe.py` |
| Universe | `scripts/build_crypto_top50_universe.py` |
| Labels | `scripts/build_labels.py` |
| Factor Values | `scripts/build_factor_values.py` |
| Signal Panel | `scripts/build_phase9b_signal_panel.py` |
| **信号评估（活跃入口）** | **`scripts/evaluate_signals.py`** |
| Parity Harness | `scripts/run_signal_evaluation_parity_harness.py` |
| Phase 11A | `scripts/run_phase11a_cost_slippage_capacity.py` |
| Phase 12A | `scripts/run_phase12a_paper_signal_harness.py` |
| Phase 12B | `scripts/run_phase12b_paper_monitoring.py` |

## 已归档脚本（非活跃，仅供历史参考）

以下脚本已归档至 `archive/legacy_phase_scripts/phase10/`：

| 功能 | 归档位置 | 状态 |
|------|----------|------|
| Phase 10A | `archive/.../phase10/run_phase10a_signal_backtest.py` | 归档 |
| Phase 10A-R | `archive/.../phase10/run_phase10a_r_diagnostics.py` | 归档 |
| Phase 10B | `archive/.../phase10/run_phase10b_tail_diagnostics.py` | 归档 |
| Phase 10D | `archive/.../phase10/run_phase10d_tail_aware_variants.py` | 归档 |

**不要用于新研究。** 这些脚本使用内联实现，已被公共 `signal_evaluation` API 替代。

## 已验证数据

- Bars: 3,316,259 rows, 266 symbols, 17,808 timestamps, no taker columns
- Labels: 215,061 rows, 50 symbols, 4 horizons (1h/4h/24h/72h)
- Signal panel: 3,314,397 rows, 266 symbols, 17,801 timestamps
- Universe: 1,250 snapshots, 266 symbols, PARTIAL survivorship bias

## Not for production use.
No real execution. No alpha claim. Phase 13 NOT STARTED.
