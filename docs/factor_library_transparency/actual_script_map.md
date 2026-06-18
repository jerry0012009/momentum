# 真实执行脚本地图 (Actual Script Map)

**Phase 12D-C · 真实代码结构与脚本地图修复**

> 基于实际扫描 `scripts/` (602 文件)、`src/momentum/` (39 文件)、`research/factor_runs/` (273+ 文件) 的真实执行链路。
> 未编造不存在的脚本。如果某个功能没有明确脚本，标记为"未确认 / 需要人工确认"。
> 数据范围: 2024-06-01 → 2026-06-13, 266 symbols, 14,365 parquet files。主 run: crypto_top50_usdt_perp_1h (2025-12-15 → 2026-06-13, 50 symbols)

---

## 当前真实架构

**当前真实架构不是纯 src-package-driven，而是 scripts-driven research pipeline + partial reusable src components。**

- 当前 run 的主要执行入口在 `scripts/`
- 研究档案在 `research/`
- 可复用组件部分在 `src/`
- 未来如果要工程化，应逐步把稳定逻辑从 `scripts/` 沉淀到 `src/`，但当前阶段不做重构

---

## 1. 构建原始数据 / cache 用哪些脚本？

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| 下载全量 1h K线 | `scripts/download_full_binance_1h_universe.py` | ✅ | Binance USDT-perp API | `data/raw/{symbol}/bars_1h.parquet` | ✅ | ✅ | ❌ | 266 symbols, 6,650 parquet files |
| 构建 crypto-native 缓存 | `scripts/build_crypto_native_caches.py` | ✅ | Binance API (funding, taker, OI) | `data/cache/crypto_native/` | ✅ | ✅ | ❌ | 已下载: funding_rate (3 files, 3.3M rows), taker_volume (嵌入 bars)。未下载: OI, basis, long_short_ratio, liquidations, orderbook_depth |

## 2. 构建 dynamic universe 用哪些脚本？

> 当前是 dynamic Top50：每月根据上一个完整月 quote_volume 选择 Top 50

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| 构建 Top50 universe | `scripts/build_crypto_top50_universe.py` | ✅ | Binance API (成交量) | `data/cache/crypto_top50_universe.json` | ✅ | ✅ | ❌ | crypto top 50 USDT-perp 列表 |
| 月度成交量排名 | `scripts/build_dynamic_universe_monthly_volume.py` | ✅ | `data/raw/` bars_1h | `data/cache/*/universe_membership.parquet` | ✅ | ✅ | ✅ | Top 50 by monthly volume |
| Universe 过滤 bars | `scripts/build_dynamic_universe_bars_1h.py` | ✅ | universe + raw bars | `data/cache/*/bars_1h_universe.parquet` | ✅ | ✅ | ✅ | 按 universe 过滤并拼接 |

## 3. 构建 factor values 用哪些脚本？

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| 基础因子 | `scripts/build_factor_values.py` | ✅ | `bars_1h_universe` | `data/features/*/factor_values.parquet` | ✅ | ✅ | ✅ | 11 个基础截面因子: momentum_1h, momentum_4h, momentum_24h, volatility_24h, volume_zscore, rsi_14, macd_hist, bollinger_pctb, atr_pct, obv_slope, vwap_deviation |
| 批量因子 | `scripts/build_factor_values_batch.py` | ✅ | bars_1h + `src/momentum/factors/` | `data/features/*/factor_values_batch.parquet` | ✅ | ✅ | ❌ | 多 batch |
| Crypto-native 因子 | `scripts/build_crypto_native_factor_values.py` | ✅ | crypto_native_caches + bars_1h | `data/features/*/crypto_native_factor_values.parquet` | ✅ | ✅ | ✅ | 6 个 crypto-native 因子: funding_rate_zscore, funding_rate_ma7, taker_buy_ratio, taker_volume_zscore, taker_buy_sell_imbalance, funding_rate_trend |

## 4. 构建 forward return labels 用哪些脚本？

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| Forward return labels | `scripts/build_labels.py` | ✅ | `bars_1h_universe` | `data/features/*/labels.parquet` | ✅ | ✅ | ✅ | 1h / 4h / 24h / 72h horizons |

## 5. 构建 Phase 9B signal panel 用哪个脚本？

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| Signal panel 构建 | `scripts/build_phase9b_signal_panel.py` | ✅ | factor_values + forward_returns + signal_basket_plan | `research/.../phase9b_signal_panel.parquet` | ✅ | ✅ | ✅ | 3 signal variants, 214MB (gitignored) |

## 6. 跑 Phase 10A / 10D 评估用哪些脚本？

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| Phase 10A signal backtest | `scripts/run_phase10a_signal_backtest.py` | ✅ | signal_panel + forward_returns | `phase10a_*.csv / .parquet` | ✅ | ✅ | ✅ | RankIC, 48 variants |
| Phase 10A R diagnostics | `scripts/run_phase10a_r_diagnostics.py` | ✅ | phase10a results | `phase10a_r_*.csv` | ✅ | ✅ | ✅ | direction consistency |
| Phase 10B tail diagnostics | `scripts/run_phase10b_tail_diagnostics.py` | ✅ | phase10a results | `phase10b_*.csv` | ✅ | ✅ | ✅ | bucket0, PM decision |
| Phase 10D tail-aware variants | `scripts/run_phase10d_tail_aware_variants.py` | ✅ | phase10a/b + tail policy | `phase10d_*.csv / .parquet` | ✅ | ✅ | ✅ | pass/fail matrix |

## 7. 跑 Phase 11A / 11B 成本和流动性用哪些脚本？

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| Phase 11A cost / slippage | `scripts/run_phase11a_cost_slippage_capacity.py` | ✅ | phase10d + turnover + volume + spread | `phase11a_*.csv` | ✅ | ✅ | ✅ | spread cost, capacity |
| Phase 11B liquidity / capacity | `scripts/run_phase11b_liquidity_capacity.py` | ✅ | phase11a + orderbook + volume | `phase11b_*.csv / .parquet` | ✅ | ✅ | ✅ | bottleneck symbols |

## 8. 跑 Phase 12A / 12B paper signal 和 monitoring 用哪些脚本？

> Phase 12A/12B：手动运行，本地诊断，不是后台定时任务，不是实盘

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| Phase 12A paper signal | `scripts/run_phase12a_paper_signal_harness.py` | ✅ | phase11b + signal_panel + candidate_freeze | `phase12a_*.csv` | ✅ | ✅ | ✅ | candidate freeze, preflight |
| Phase 12B paper monitoring | `scripts/run_phase12b_paper_monitoring.py` | ✅ | phase12a + live market data | `phase12b_*.csv` | ✅ | ✅ | ✅ | 30-day rolling monitoring |

## 9. 生成 transparency docs / showcase website 用哪些脚本？

| 功能 | 文件路径 | 主线 | 输入 | 输出 | 手动运行 | 生成文件 | 测试 | 备注 |
|------|----------|------|------|------|----------|----------|------|------|
| Showcase 网站生成 | `scripts/build_showcase_workflow_page.py` | ✅ | research/ + docs/ | `reports/site/factor-library/*.html` | ✅ | ✅ | ❌ | showcase 页面 |
| Site index | `scripts/build_site_index.py` | ✅ | reports/site/ 结构 | `reports/site/index.html` | ✅ | ✅ | ❌ | 站点主页 |
| 报告站点发布 | `scripts/publish_report_site.sh` | ✅ | reports/site/ | `/var/www/momentum-report/` | ✅ | ✅ | ❌ | rsync 到 nginx |
| 报告管线 | `scripts/run_report_pipeline.py` | ✅ | 多个 build_*.py | reports/ | ✅ | ✅ | ❌ | 串联生成 |
| 因子警告标记 | `scripts/apply_factor_warning_flags.py` | ✅ | evaluation results | warning_flags/ | ✅ | ✅ | ❌ | 自动标记 |

## 10. 哪些脚本只是历史/legacy，不属于当前主线？

| 功能 | 文件路径 | 说明 |
|------|----------|------|
| rank213 live paper reference | `scripts/build_rank213_live_paper_reference.py` | rank213 独立研究线 |
| rank32b 策略门户 | `scripts/build_rank32b_strategy_portal.py` | rank32b 独立研究线 |
| rank154 postmortem | `scripts/analyze_rank154_postmortem.py` | rank154 postmortem 分析 |
| rank29 监控 | `scripts/build_rank29_monitoring_hub.py` | rank29 独立研究线 |
| v1.6a 回测 | `scripts/backtest_v1_6a.py` | 早期策略，已被 factor library 取代 |
| manual narrow paper lanes | `scripts/run_manual_narrow_paper_lanes.py` | 独立 paper lane 管理 |
| 其他 rank*.py | 大量 `build_rank*`, `run_rank*` 脚本 | 属于各 rank 独立研究线 |

---

## src/momentum/ 可复用组件库

`src/momentum/` 是已有可复用代码组件库，包含 factors / signals / analytics / strategies 等模块；但当前 crypto_top50 factor library 研究 run 的主执行逻辑仍主要由 `scripts/` 驱动。src 中部分组件可复用，部分仍需审计，不等于当前 run 的全部执行链路。

| 模块 | 文件 | 角色 |
|------|------|------|
| `src/momentum/factors/` | chip_distribution, confirmed_extrema, endpoint_nadaraya_watson, pytrendline_bridge | 因子计算组件 |
| `src/momentum/signals/` | box_consolidation, ema_donchian_breakout, market_risk_on_off_filter, multi_tf_momentum, price_volume_divergence, pullback_recovery_confirmation, regime_triplet, trend_regime_filter, trendline_breakout_navigator, up_down_wave | 信号构建组件 |
| `src/momentum/analytics/` | ema_donchian_breakout_backtest, multi_tf_momentum_backtest, report_pipeline, trendline_segment_backtest, updownwave_insights, wave_hold_backtest | 分析和回测 |
| `src/momentum/strategies/` | rank154_crypto_stat_arb, rank32c_btc_utc_weak_cell | 特定 rank 策略 |
| `src/momentum/execution/` | canary32b/, rank32c/ | 执行引擎 |
| `src/momentum/risk/` | canary32b_guard | 风险管理 |
| `src/momentum/cli.py` | CLI 入口 | 通用工具 |
| `src/momentum/html_render.py` | HTML 渲染 | 通用工具 |

---

## research/factor_runs/ 的真实角色

`research/factor_runs/crypto_top50_factor_library/` 是当前研究 run 的**审计档案和结果目录**，主要保存 phase closeout、CSV 结果、quality checks、manifest、parquet 生成物等；**它不是主要代码目录**。

文件类型：
- `phase*_quality_checks.csv` — 各阶段质量检查
- `phase*_*.csv` — 各阶段评估结果表
- `phase*_*.parquet` — 各阶段大型数据表
- `phase*_*.md` — 各阶段 closeout / design spec 文档
- `factor_catalog_*.csv` — 因子目录
- `warning_flags/` — 因子警告标记
- 总计 273+ 文件

---

## Phase 9B Signal Panel 定位

Phase 9B signal panel 是**当前 run 的主信号面板**，不是"未来才需要"的东西。

- 当前 run 的所有 Phase 10A/10D 评估都基于 Phase 9B signal panel
- 以后在哪里增加新信号？→ 在 `scripts/build_phase9b_signal_panel.py` 的 signal basket plan 中增加新 variant，或新建 Phase 9C panel

---

## Phase 10A/10D 评估流程定位

Phase 10A/10D 是**信号质量评估协议**，不是回测引擎：

- Phase 10A: RankIC + direction consistency (48 variants)
- Phase 10D: tail-aware pass/fail matrix
- 输入: Phase 9B signal panel + forward returns
- 输出: CSV 结果，供 PM 人工决策

---

## Phase 12A/12B 运行方式

Phase 12A/12B 是**手动本地诊断工具**，不是后台 daemon：

- 手动运行：需要人工触发，不是 cron 定时任务
- 本地诊断：在本地环境运行，不是部署到服务器
- 不是实盘：无真实资金，无真实订单

---

## 重要声明

- 脚本清单基于实际文件系统扫描，未编造不存在的脚本
- 标记为"非主线"的脚本可能属于其他 rank 研究线或历史遗留
- Phase 13 NOT STARTED
- 无实盘执行 · 无 alpha 声明 · 无生产声明
- Phase 12D-C · 真实代码结构与脚本地图修复
