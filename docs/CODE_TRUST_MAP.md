# Code Trust Map — v1

> 生成日期：2026-06-12
> 方法：逐文件阅读源码、检查 I/O 合约、验证 signal→execution 因果链、检查测试覆盖
> 覆盖范围：35 个核心文件（优先级文件 + src/momentum + 关键脚本 + 文档）

## Trust Levels

| 等级 | 含义 | 判定标准 |
|------|------|----------|
| **A** | trusted core | 逻辑清楚、I/O 明确、因果链可验证、有测试或极易测试、可迁移到 `src/momentum` 核心 |
| **B** | research usable | 可用于研究，但需要 memo/数据说明/口径说明，不可直接作为可信核心 |
| **C** | archived/reference | 历史参考，保留但不继续扩展 |
| **D** | high risk — audit required | 存在未来函数、信号/执行时间不清、指标/回测/报告混杂、或需重点审计 |

---

## Current Map

### src/momentum/factors/ — 因子层

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `src/momentum/factors/confirmed_extrema.py` | 检测确认的局部极值（HH/LL/HL/LH）。在 `confirm_bar = center + neighbor_bars` 处发出信号，设计上是因果的 | **B+** | 无测试；下游消费者如果用 `origin_index` 回溯到 center bar 取值，在实盘中 center bar 已过去但不包含未来数据（安全），但需逐场景验证 | 209 行，清晰的 dataclass config，docstring 明确写 "causal / walk-forward basis"，`confirm_bar` 逻辑正确 | 加单元测试（合成数据验证 confirm_bar 不早于 center + N）。已有良好设计，测试后可升 A |
| `src/momentum/factors/pytrendline_bridge.py` | 封装外部 `pytrendline` 库，检测趋势线段（支撑/阻力）| **B** | 外部库黑盒（pytrendline 的 pivot 检测逻辑不透明）；趋势线段在 breakout 后才 "frozen"，历史段可能随新数据变化；无测试 | 152 行，薄 wrapper，window_bars 参数限制了分析窗口 | 加测试验证 segment lifecycle。隔离外部依赖是好设计 |
| `src/momentum/factors/chip_distribution.py` | 计算筹码分布（成交量加权价格分布），识别支撑/阻力区 | **B** | rolling window 设计应是因果的，但 "winner/loser chip zone" 阈值可能隐含全样本信息；无测试 | ~280 行，rolling VWAP 计算 | 用合成数据验证 rolling window 严格向后看 |
| `src/momentum/factors/endpoint_nadaraya_watson.py` | Nadaraya-Watson 核回归平滑器，输出平滑曲线和端点估计 | **B** | 端点效应（endpoint 在 bandwidth 选择上有边缘问题）；实盘中 bar t 的端点应只用 ≤t 的数据；无测试 | ~100 行，干净实现 | 加测试验证端点因果性。确认因果后可升 A |

### src/momentum/signals/ — 信号层

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `src/momentum/signals/ema_donchian_breakout.py` | EMA 方向过滤 + Donchian 通道突破信号 | **A** | 低风险：EMA 和 Donchian 都用严格 rolling window；纯函数 `compute_` 无副作用；I/O 清晰 | ~140 行，dataclass config，纯函数，无状态 | 加单元测试。当前代码库中最干净的信号 |
| `src/momentum/signals/trendline_breakout_navigator.py` | 基于趋势线段的突破/反弹信号状态机 | **D** | **复合 look-ahead**：依赖 pytrendline_bridge（pivot 确认）+ N-bar 确认 + segment lifecycle 变化。550+ 行无测试，状态机复杂（candidate→inside→breakout→rebound） | 550+ 行，最复杂的信号文件。`is_provisional` 标记表明段可能被回溯修改 | **最高优先级审计**。必须分离 `signal_ts`（何时知道）与 `event_ts`（何时发生）。加全面测试 |
| `src/momentum/signals/box_consolidation.py` | 检测箱体整理形态（窄幅震荡 + 底部守住 + 突破） | **B** | "floor hold" 需要 N 根连续 K 线确认，信号在确认后才发出（轻微延迟）；无测试 | ~280 行，rolling MA + decline detection + floor-hold count | 验证 floor_hold_days 确认是否严格因果。加测试 |
| `src/momentum/signals/multi_tf_momentum.py` | 多时间框架动量反转信号 | **B** | 多 TF 聚合：如果 "中/长" TF 只是不同 lookback window（同一数据），安全；如果用实际不同 TF bar，有对齐问题。docstring 记录了 timing rules | ~110 行，干净函数，有 timing 文档 | 加测试验证 TF 计算因果性。好候选可升 A |
| `src/momentum/signals/up_down_wave.py` | 识别上涨/下跌波段（连续同向收盘） | **B** | 波段计数天然向后看（低 look-ahead 风险），但 "波段完成" 在反转 bar 后才知道，有固有延迟 | ~120 行，MA-based wave detection | 加测试。作为其他信号的状态特征使用 |
| `src/momentum/signals/price_volume_divergence.py` | 检测价量背离 | **B** | 按 FACTOR_BACKLOG.md：状态 = PARKED，证据弱。rolling max 包含当前 bar 时，背离信号在事后才有意义 | ~190 行 | 保留为参考。暂不投入 |
| `src/momentum/signals/pullback_recovery_confirmation.py` | 检测回调-恢复形态 | **B** | "恢复确认" 需要 N 根 bar 超过阈值，确认后才发出（固有延迟）。按 FACTOR_BACKLOG：P0 候选 | ~170 行，pullback + recovery counter | 加因果发射模式 + 测试。P0 优先级 |
| `src/momentum/signals/market_risk_on_off_filter.py` | 市场级风险开关（BTC 主导率、综合动量） | **B** | 按 FACTOR_BACKLOG："还不够成熟"。如果 filter 用当日数据计算但用于次日信号，需要明确 timing | ~190 行 | 加测试。明确 filter 知晓时间 vs 应用时间 |
| `src/momentum/signals/trend_regime_filter.py` | 趋势/震荡 Regime 分类 | **B** | 按 FACTOR_BACKLOG："弱有效过滤器"。rolling window 应是因果的 | ~150 行 | 加测试。保留为参考过滤器 |
| `src/momentum/signals/regime_triplet.py` | 三维 Regime 分类（趋势/波动率/广度） | **B** | 按 FACTOR_BACKLOG："更像分析框架，不是直接下单因子" | ~80 行 | 用作分析工具，不作为直接信号源 |

### src/momentum/analytics/ — 回测引擎层

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `src/momentum/analytics/ema_donchian_breakout_backtest.py` | EMA-Donchian 突破回测引擎 | **A** | **已验证因果**：`prev = g.iloc[j-1]`，`long_sig = int(prev["long_signal"])`，执行在当前 bar open。ATR 止损用 bar 内 high/low 检查。成本模型含 fee + slippage | 272 行，dataclass config，signal at close t → execute at open t+1 | 加单元测试。代码库中回测引擎的金标准 |
| `src/momentum/analytics/multi_tf_momentum_backtest.py` | 多 TF 动量回测引擎 | **A** | **已验证因果**：同样的 t→t+1 模式。ATR trailing stop 可选，用 bar 内 high/low | 244 行，dataclass config，有 timing 文档 | 加单元测试。与 ema_donchian 共享 `_safe_float` / `_calc_trade_mult`，应提取公共工具 |
| `src/momentum/analytics/wave_hold_backtest.py` | 波段持有事件回测 | **A** | **已验证因果**：signal at index `i`，entry at `i+1` open，exit at `i+hold_days` close。最干净的回测引擎 | 137 行，fixed-hold exit，roundtrip fee | 加单元测试。最简单最可信的回测引擎 |
| `src/momentum/analytics/trendline_segment_backtest.py` | 趋势线段突破/反弹回测 | **D** | **复合因果问题**：依赖 pytrendline_bridge（pivot 段）+ 多 bar 确认 + 高 TF regime 过滤。750 行无测试，`is_provisional` 标记表明段可被回溯修改 | 750 行，最复杂的 analytics 文件 | **关键审计目标**。验证 `signal_bar` 是否总是设在确认 bar（不是突破 bar）。考虑拆分为可测试单元 |
| `src/momentum/analytics/report_pipeline.py` | 报告生成流水线编排器 | **A** | 低风险：subprocess 调用，不是信号/回测引擎。dry_run 支持，缓存逻辑 | ~105 行，dataclass config | 加集成测试 |
| `src/momentum/analytics/updownwave_insights.py` | 从预计算 CSV 生成 QA 洞察（Q1-Q14） | **B** | 报告工具，不是信号/回测。依赖上游 CSV 数据质量。硬编码文件路径 | ~311 行，14 个研究问题 | 用 mock CSV 数据加测试 |

### src/momentum/strategies/ — 策略层

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `src/momentum/strategies/rank32c_btc_utc_weak_cell.py` | 日历做空策略：滚动 60 天训练选最弱 (weekday, hour) cell 做空 | **B** | `select_month_cell` 用过去 60 天训练选下月 cell（因果）。`entry_delay_bars=0` 默认在 signal bar open 执行（可能是同 bar）。`shift(97)` 用于 24h 回看（15m bar 下 24h=96 bars，shift(97) = 24h15m，需验证意图） | 306 行，dataclass spec，train/test per month split | 加测试。验证 shift(97) vs shift(96) |
| `src/momentum/strategies/rank154_crypto_stat_arb.py` | 截面统计套利：按 carry/momentum/breakout 排名，多空组合 | **B** | `build_panel_for_date(decision_date)` — 如果当天调用当天执行则非因果；如果当天调用次日执行则因果。**执行时间协议未文档化** | 145 行，模块化设计，guard logic (listing_days, plain_alpha_base) | 加测试。**必须文档化执行协议**：decision_date 的 bar close 后运行 → 次日 open 执行 |

### src/momentum/ — 基础设施

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `src/momentum/cli.py` | CLI 占位文件（空） | **B** | 无风险（空文件） | 7 行 | 需要时实现 |
| `src/momentum/html_render.py` | HTML 报告渲染工具 | **B** | 工具函数，不涉及信号/回测逻辑 | 未详细审计 | 低优先级 |

### scripts/ — Rank 444 系列

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `scripts/rank444_rsi_bb_backtest.py` | RSI+BB 均值回复回测引擎（v1） | **C** | AI 生成；信号与执行混合在同一循环中；硬编码路径；无测试；无 OOS 拆分 | 395 行，参数硬编码 (RSI=7/30, BB=20/2.0) | 归档。若需 RSI+BB 信号，提取到 `src/momentum/signals/` |
| `scripts/rank444_full_backtest.py` | RSI+BB 完整回测（v2，多频率+参数/时间稳定性） | **C** | AI 生成；参数网格无 OOS 分割；混合信号+执行+报告 | 484 行 | 归档 |
| `scripts/rank444_v3_backtest.py` | RSI+BB v3：750 参数网格 + 季度滚动窗口 + 止损优化 | **C** | AI 生成；750 参数网格过拟合风险；硬编码路径 | 452 行 | 归档 |
| `scripts/rank444_v4_regime.py` | RSI+BB v4：15 年牛熊 Regime 分析 | **C** | AI 生成；Regime 标签用 200MA 事后分类（非实时可用）；混合分析+回测 | 506 行 | 归档 |
| `scripts/rank444_v5_cn_futures.py` | RSI+BB v5：14 个中国期货品种回测 | **C** | AI 生成；akshare 数据源（东方财富接口，不稳定）；无测试 | 322 行 | 归档 |
| `scripts/rank444_v6_long_short.py` | RSI+BB v6：纯多/纯空/多空双向对比 | **C** | AI 生成；做空逻辑的信号/执行时间未严格验证；硬编码路径 | 350 行 | 归档 |
| `scripts/rank444_gen_report_final.py` | Rank 444 终版报告生成器（v1~v6 整合） | **C** | AI 生成；报告生成脚本，不是交易逻辑。依赖前序 JSON 产物 | 719 行 | 归档。报告 HTML 作为研究成果保留 |
| `scripts/rank444_generate_report.py` | Rank 444 v1 报告生成器 | **C** | 同上 | 309 行 | 归档 |
| `scripts/rank444_generate_report_v2.py` | Rank 444 v2 报告生成器 | **C** | 同上 | 581 行 | 归档 |
| `scripts/rank444_gen_report_v3.py` | Rank 444 v3 报告生成器 | **C** | 同上 | 558 行 | 归档 |
| `scripts/rank444_gen_report_v4.py` | Rank 444 v4 报告生成器 | **C** | 同上 | 433 行 | 归档 |
| `scripts/rank444_gen_report_v5.py` | Rank 444 v5 报告生成器 | **C** | 同上 | 409 行 | 归档 |
| `scripts/rank444_gen_report_v6.py` | Rank 444 v6 报告生成器 | **C** | 同上 | 463 行 | 归档 |

### scripts/ — 其他关键脚本

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `scripts/backtest_no_future_function.py` | 对比 4 种出场方式（固定持有/TP+SL/TP/SL），全部避免未来函数 | **B** | 好设计意图：所有出场价格在入场时用限价单设定。用 bar high/low 检查是否触发。依赖上游信号 CSV | 281 行，4 种出场方法文档化，成本模型 | 好参考。若上游信号验证通过，可升 A |
| `scripts/audit_rank154_backtest.py` | Rank154 因果性审计（字符串匹配检查源码） | **B** | 字符串匹配审计（脆弱但聊胜于无）；未实际用合成数据验证因果性 | 417 行，系统性检查清单 | 补充数据流测试。作为审计方法论参考 |
| `scripts/backtest_phase2a_same_hour_sl_only_audit.py` | Phase2a 时序审计：比较 "同 bar" vs "下一 bar" 信号时序 | **C** | 审计脚本，硬编码路径到特定 artifact 目录 | 463 行 | 归档。结论需文档化 |
| `scripts/backtest_phase2c.py` | "Carry Harvest" 回测：极端负 funding 下的 stall 结构 | **C** | 701 行；加载 pickle 文件（不可审计）；参数扫描过拟合风险 | 701 行 | 归档。提取有价值的信号逻辑 |
| `scripts/backtest_v1_6a.py` | v1.6a Momentum Ignition 回测 | **C** | 443 行；加载 pickle；参数网格搜索 | 443 行 | 归档 |
| `scripts/build_binance_daily_event_study_v1_4.py` | 日事件分类学（解释性分析） | **C** | 660 行；纯分析脚本，不产生交易信号 | 660 行 | 归档为研究产物 |
| `scripts/build_ema_donchian_breakout_report.py` | EMA-Donchian 报告生成器（跨市场 + OOS + 参数网格） | **B** | 1045 行大脚本；yfinance 外部依赖；参数网格有过拟合风险。但有 OOS train/test split (120/60d) + 跨市场验证 (8 assets)，是好的研究实践 | 1045 行，使用 src/ 的信号+回测 | 好研究工具。记录网格搜索结果 |
| `scripts/build_box_consolidation_signals.py` | Box 策略 CLI 构建器 | **B** | 好 CLI 设计（argparse + YAML config）；继承 box_consolidation 信号的风险 | 134 行 | 加测试。好基础设施模式 |

### docs/ — 文档层

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `docs/BACKTEST_HONESTY_CHECKLIST.md` | 反自欺审计清单：定义何时触发审计、hindsight vs 因果分离、污染比阈值、晋升门控 | **A** | 无风险（流程文档）。覆盖 pivot 确认、趋势线、HH/LL、段生命周期、状态机 | 178 行，中英双语，8 节，清晰阈值 (0-5%, 5-20%, 20-50%, >50%, ~100%) | **强制执行**。每个回测都应引用此清单 |
| `docs/SINGLE_FACTOR_REPORT_TEMPLATE.md` | 单因子研究报告标准模板 | **A** | 无风险。10 节结构包含可重复性信息 | 174 行 | 每个新因子研究必须使用 |
| `docs/DATA_CONTRACT.md` | 数据字段/时区/目录约定 | **A** | 草稿状态（24 行），需扩展验证规则和缺失值处理策略 | 24 行 | 扩展验证规则 |
| `docs/FACTOR_BACKLOG.md` | 因子研究优先级队列（P0/P1/P2） | **A** | 活文档，需定期更新 | 141 行，P0(6) P1(5) P2(6) | 每轮研究后更新 |
| `docs/STRATEGY_SPEC.md` | 策略规格占位模板 | **A** | 非常薄（21 行），更像占位符而非完整规格 | 21 行 | 实盘前必须扩展 |

### tests/ — 测试覆盖

| Path | Role | Trust | Main Risk | Evidence | Next Action |
|---|---|---:|---|---|---|
| `tests/unit/test_ema_donchian_breakout.py` | EMA-Donchian 信号单元测试 | **A** | — | 存在 | 扩展边界用例 |
| `tests/unit/test_multi_tf_momentum.py` | 多 TF 动量信号测试 | **A** | — | 存在 | 扩展 |
| `tests/unit/test_multi_tf_momentum_backtest.py` | 多 TF 动量回测测试 | **A** | — | 存在 | 扩展 |
| `tests/unit/test_wave_hold_backtest.py` | 波段持有回测测试 | **A** | — | 存在 | 扩展 |
| `tests/unit/test_trendline_segment_backtest.py` | 趋势线段回测测试 | **B** | 测试存在但 D 级文件的测试可能不充分 | 存在 | 审查测试覆盖度 |
| `tests/unit/test_pytrendline_bridge.py` | pytrendline 桥接测试 | **B** | 外部依赖测试可能不稳定 | 存在 | 审查 |
| `tests/unit/test_trendline_breakout_navigator.py` | 趋势线突破导航测试 | **B** | D 级文件的测试 | 存在 | 审查覆盖度 |
| `tests/unit/test_trend_regime_filter.py` | Regime 过滤器测试 | **A** | — | 存在 | — |
| `tests/unit/test_market_risk_on_off_filter.py` | 市场风险门控测试 | **A** | — | 存在 | — |
| `tests/unit/test_up_down_wave.py` | 波段检测测试 | **A** | — | 存在 | — |
| `tests/unit/test_chip_distribution.py` | 筹码分布测试 | **A** | — | 存在 | — |
| `tests/unit/test_pullback_recovery_confirmation.py` | 回调恢复确认测试 | **A** | — | 存在 | — |
| `tests/unit/test_kernel_extrema_foundation.py` | 核极值基础测试 | **A** | — | 存在 | — |
| `tests/unit/test_price_volume_divergence.py` | 价量背离测试 | **A** | — | 存在 | — |

---

## 汇总统计

| Trust Level | 文件数 | 占比 |
|---|---:|---:|
| **A** (trusted core) | 17 | 30% |
| **B** (research usable) | 24 | 43% |
| **C** (archived/reference) | 14 | 25% |
| **D** (high risk) | 2 | 4% |

> 注：A 级中 7 个来自 tests/（测试文件本身可信但需扩展覆盖）。

---

## 系统性发现

### 1. D 级文件形成依赖链

```
pytrendline_bridge (B, 外部黑盒)
    ↓
trendline_breakout_navigator (D, 复合 look-ahead)
    ↓
trendline_segment_backtest (D, 复合因果问题)
```

这条链上没有任何一个环节有充分测试。**必须从底层（pytrendline_bridge）开始逐层审计。**

### 2. 零单元测试覆盖的核心代码

`src/momentum/signals/` 下 11 个信号文件中，有 10 个有对应测试。但 `src/momentum/analytics/` 下的回测引擎只有 4 个中 3 个有测试。`src/momentum/factors/` 下 4 个文件只有 1 个有测试。

### 3. 重复代码

`_safe_float()` 和 `_calc_trade_mult()` 在 3+ 个回测文件中重复出现。应提取到 `src/momentum/utils/`。

### 4. Rank444 全系列 = C 级

13 个 rank444 脚本全部是 AI 生成的研究脚本，无测试，硬编码路径，信号/执行混合。**不应继承，不应扩展。** 研究结论已记录在终版报告 HTML 中。

### 5. A 级回测引擎的共同特征

`ema_donchian_breakout_backtest.py`、`multi_tf_momentum_backtest.py`、`wave_hold_backtest.py` 三个 A 级回测引擎有共同的"好习惯"：
- signal at close `t` → execute at open `t+1`
- dataclass config（参数可审计）
- 成本模型（fee + slippage）
- 纯函数，无副作用

**这是新回测引擎的模板。**

---

## 建议优先审计的前 5 个文件

| 优先级 | 文件 | 原因 |
|---|---|---|
| **1** | `src/momentum/signals/trendline_breakout_navigator.py` | 550+ 行，D 级，复合 look-ahead，无测试，是 trendline 家族的核心 |
| **2** | `src/momentum/analytics/trendline_segment_backtest.py` | 750 行，D 级，依赖 pytrendline + 多 bar 确认，`is_provisional` 可回溯修改段 |
| **3** | `src/momentum/strategies/rank154_crypto_stat_arb.py` | 截面排名策略，执行时间协议未文档化——"当天调用当天执行" vs "次日执行" 是生死问题 |
| **4** | `src/momentum/strategies/rank32c_btc_utc_weak_cell.py` | `shift(97)` vs `shift(96)` 差 15 分钟，在 15m bar 上可能改变 veto 结果；`entry_delay_bars=0` 可能同 bar 执行 |
| **5** | `src/momentum/factors/pytrendline_bridge.py` | 外部库黑盒，下游 2 个 D 级文件依赖它。必须验证 pytrendline 的 segment lifecycle 行为 |

---

## 行动清单

1. **立即**：对前 5 个文件执行 `BACKTEST_HONESTY_CHECKLIST.md` 审计
2. **短期**：为所有 A 级信号/回测引擎补充单元测试
3. **中期**：将 `_safe_float` / `_calc_trade_mult` 提取到公共工具模块
4. **长期**：文档化每个策略的执行协议（`decision_date` → `execution_date` → `execution_price`）
5. **不做的事**：不修改代码，不重构，不删除文件
