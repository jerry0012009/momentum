# jerry/momentum

## Current Mainline — Crypto Perpetual Cross-Sectional Factor Library

**Active project:** Crypto USDT perpetual cross-sectional momentum factor library research system.

- Current factor counts are generated, not hand-written: see [`factor_library_state.md`](research/factor_runs/crypto_top50_factor_library/factor_library_state.md)
- **10** factors in current signal panel, **3** signal variants
- **4** horizons: 1h, 4h, 24h, 72h
- **Status:** Research diagnostic only. NOT production. NOT live trading. NOT alpha-verified.

### Key Documents

| Document | Description |
|----------|-------------|
| [START_HERE.md](docs/factor_library/START_HERE.md) | Entry point — pipeline overview, canonical files, how to extend |
| [FACTOR_LIBRARY_CONTROL_CENTER.md](docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md) | Governance center — status, scripts, modules, extension points |
| [FILE_STATUS_REGISTER.csv](docs/factor_library/FILE_STATUS_REGISTER.csv) | File-level status register (active / deprecated / orphan) |
| [ORPHAN_WORK_AUDIT.md](docs/factor_library/ORPHAN_WORK_AUDIT.md) | Orphan risk audit |

### Adding Factors

Use the factor intake workflow. Do not create a parallel factor pipeline.

1. Read [`START_HERE.md`](docs/factor_library/START_HERE.md) and the current state artifact.
2. Add or adjust `FactorSpec` entries in `scripts/factor_formula_registry.py`, reusing `scripts/factor_ops.py` where possible.
3. Run `python scripts/run_factor_intake.py --factor-ids <factor_id...> --run-id <run_id>`.
4. Review the isolated run under `research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/`.
5. Do not add intake factors to `scripts/build_phase9b_signal_panel.py`.

### Public Site

| Page | Description |
|------|-------------|
| [Factor Library Home](reports/site/factor-library/index.html) | Entry page |
| [Code Structure Map](reports/site/factor-library/actual-script-map.html) | Pipeline execution map with 12 nodes |
| [Factor Evaluation](reports/site/factor-library/factor-evaluation.html) | Factor-level IC evaluation (see [current state](research/factor_runs/crypto_top50_factor_library/factor_library_state.md)) |
| [Signal Evaluation](reports/site/factor-library/signal-evaluation-summary.html) | Signal-level RankIC / Spread summary |

---

## Historical / Adjacent Research

> The sections below document earlier project phases (M1 single-market Backtrader, Xiaomi HK, box consolidation, regime triplet, etc.). These are preserved for historical reference and are **not** part of the current factor-library mainline.

面向趋势交易研究的量化项目（先做单市场 Backtrader，后续扩展到多市场与模拟盘/实盘）。

### Historical Phase: M1
目标：先跑通**单市场回测闭环**，并保持结构可扩展、可维护。

### 已完成（截至 2026-03-03）
- 项目骨架目录与分层文档已建立
- 配置分层已建立：`base / markets / env / strategies`
- M1 依赖清单已落地：`requirements-m1.txt`
- 本地虚拟环境已创建（本机）：`.venv`
- 小米港股（`1810.HK`）示例日线数据已准备：1年与5年
- 5年数据已标准化为 silver 契约格式（便于后续回测直接接入）
- Up/Down Wave 事件法粗略回测脚本已落地（T+1 进场，5日持有）
- 上涨浪/下跌浪信号已实现（Pandas + Backtrader Indicator）

## 设计原则
1. **研究与执行解耦**：因子/信号尽量不依赖交易所 API。
2. **配置驱动**：市场、策略、环境参数 YAML 化。
3. **可复现**：同一配置 + 同一数据输入，应得到同一结果。
4. **可审计**：关键输入输出（参数、交易日志、绩效）可追踪。

## 快速维护（本地）
```bash
cd jerry/momentum
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-m1.txt
```

依赖验证：
```bash
python -c "import backtrader,pandas,yaml,matplotlib,yfinance; print('ok')"
```

## 文档导航
- 架构说明：`docs/ARCHITECTURE.md`
- 路线图：`docs/ROADMAP.md`
- 数据契约：`docs/DATA_CONTRACT.md`
- 小米数据说明：`docs/DATASET_XIAOMI_HK.md`
- 筹码分布：`docs/CHIP_DISTRIBUTION.md`
- 波段信号（Up/Down Wave）：`docs/SIGNALS_UP_DOWN_WAVE.md`
- 横盘/箱体建仓信号：`docs/SIGNALS_BOX_CONSOLIDATION.md`
- 波段信号粗略回测：`docs/BACKTEST_WAVE_HOLD.md`
- 信号流水线：`docs/SIGNAL_PIPELINE.md`
- Web 报告发布：`docs/REPORTING_WEB.md`
- Rank213 证据地图：`docs/RANK213_EVIDENCE_MAP.md`
- 学习主线：`docs/LEARNING_TRACK.md`
- 主线1学习地图：`docs/MAINLINE1_STRATEGY_FACTOR_MAP.md`
- 单因子研究模板：`docs/SINGLE_FACTOR_REPORT_TEMPLATE.md`
- 因子积累清单：`docs/FACTOR_BACKLOG.md`
- 维护手册：`docs/MAINTENANCE.md`
- 项目树：`docs/PROJECT_TREE.md`

> 当前仓库重点是“先把结构和流程打稳”；策略和回测脚本将按 M1 继续推进。

## 快速跑通信号闭环（小米示例）
```bash
cd jerry/momentum
source .venv/bin/activate

python scripts/build_up_down_wave_signals.py
python scripts/build_box_consolidation_signals.py
python scripts/backtest_wave_hold.py
```

## 生成横盘/箱体建仓信号（指数+个股）
```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_box_consolidation_signals.py
```

## 生成因子网页报告（UpWave/DownWave）
```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_updownwave_report.py
bash scripts/publish_report_site.sh
```

## 生成 Regime Triplet 网页报告（上涨期/震荡期/下跌期）
```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_regime_triplet_report.py
bash scripts/publish_report_site.sh
```

> 当前覆盖：指数/指数ETF + Crypto + A/H/US 个股篮子（用于“适用市场”横向对比）。

## 生成 Box Consolidation 网页报告（窄幅震荡/箱体突破建仓）
```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_box_consolidation_report.py
bash scripts/publish_report_site.sh
```

> 当前覆盖：指数/指数ETF + A/H/US 个股（聚焦“先跌后横盘/箱体建仓”适配性）。

## 报告流水线（重构起步，推荐入口）
```bash
cd jerry/momentum
source .venv/bin/activate

# 一键：构建 + 洞察 + 发布
python scripts/run_report_pipeline.py --stage all

# 仅构建报告
python scripts/run_report_pipeline.py --stage build

# 仅生成 Q1~Q14 文字洞察（快速）
python scripts/run_report_pipeline.py --stage insights

# 仅跑分组洞察（独立解耦单元）
python scripts/run_report_pipeline.py --stage q1_q3
python scripts/run_report_pipeline.py --stage q4_q6
python scripts/run_report_pipeline.py --stage q7_q9
python scripts/run_report_pipeline.py --stage q10_q14

# 仅发布已有 reports/site
python scripts/run_report_pipeline.py --stage publish

# 启用缓存（命中则跳过对应 stage）
python scripts/run_report_pipeline.py --stage all --use-cache
```

> 说明：当前 `run_report_pipeline.py` 已支持独立洞察阶段和 Q 分组 stage，并提供基础 `--use-cache` 跳过机制；后续会继续扩展到更细粒度增量重跑。

## Rank213 证据地图
```bash
cd jerry/momentum
python3 scripts/build_rank213_evidence_map.py
```

> 说明：Rank213 的证据地图由 `reports/artifacts/rank213_evidence_map/manifests/*.json` 生成，输出到 `docs/RANK213_EVIDENCE_MAP.md` 和 `reports/site/paper/rank213_evidence_map.html`。后续调整 213 结论口径时，优先改 manifest。
