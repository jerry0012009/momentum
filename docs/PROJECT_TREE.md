# Project Tree

```text
jerry/momentum/
├─ config/
│  ├─ base.yaml
│  ├─ env/
│  │  ├─ backtest.yaml
│  │  ├─ paper.yaml
│  │  └─ live.yaml
│  ├─ markets/
│  │  ├─ crypto.yaml
│  │  ├─ a_share.yaml
│  │  ├─ us_equity.yaml
│  │  └─ gold.yaml
│  ├─ strategies/
│  │  └─ trend_momentum_v1.yaml
│  ├─ features/
│  │  └─ chip_distribution.yaml
│  └─ signals/
│     ├─ up_down_wave.yaml
│     └─ box_consolidation.yaml
├─ data/
│  ├─ raw/           # 原始数据（默认不入库）
│  ├─ bronze/        # 清洗中间层
│  ├─ silver/        # 标准化数据（回测主要读取）
│  └─ features/      # 因子结果
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ ROADMAP.md
│  ├─ LEARNING_TRACK.md
│  ├─ MAINLINE1_STRATEGY_FACTOR_MAP.md
│  ├─ CANDIDATE_FACTOR_POOL.md
│  ├─ AUDITABLE_FACTOR_RESEARCH_SKILL.md
│  ├─ RESEARCH_LIFECYCLE.md
│  ├─ CODE_TRUST_MAP.md
│  ├─ BACKTEST_HONESTY_CHECKLIST.md
│  ├─ SINGLE_FACTOR_REPORT_TEMPLATE.md
│  ├─ FACTOR_BACKLOG.md
│  ├─ TODO.md
│  ├─ DATA_CONTRACT.md
│  ├─ DATASET_XIAOMI_HK.md
│  ├─ CHIP_DISTRIBUTION.md
│  ├─ SIGNALS_UP_DOWN_WAVE.md
│  ├─ SIGNALS_BOX_CONSOLIDATION.md
│  ├─ FOUNDATION_KERNEL_EXTREMA.md
│  ├─ RESEARCH_PYTRENDLINE.md
│  ├─ SIGNALS_TRENDLINE_BREAKOUT_NAVIGATOR.md
│  ├─ BACKTEST_WAVE_HOLD.md
│  ├─ SIGNAL_PIPELINE.md
│  ├─ REPORTING_WEB.md
│  ├─ REPORT_PIPELINE_REFACTOR.md
│  ├─ MAINTENANCE.md
│  └─ STRATEGY_SPEC.md
├─ reports/
│  ├─ artifacts/
│  └─ site/
├─ research/
│  ├─ factor_runs/
│  │  ├─ _TEMPLATE/
│  │  │  ├─ status.md
│  │  │  ├─ factor_memo.md
│  │  │  ├─ data_contract.md
│  │  │  ├─ audit_notes.md
│  │  │  ├─ reproduction.md
│  │  │  └─ decision.md
│  │  └─ rank444_rsi_bb_v0/
│  │     ├─ status.md
│  │     ├─ factor_memo.md
│  │     ├─ data_contract.md
│  │     ├─ audit_notes.md
│  │     └─ reproduction.md
│  └─ quant_digests/   # 定时研究笔记 / 文献卡片 / 仓库拆解
├─ src/momentum/
│  ├─ domain/ data/ factors/ signals/ risk/
│  ├─ portfolio/ engines/ execution/ analytics/ utils/
│  └─ cli.py
│     # current kernel/extrema/trendline research modules include:
│     # - factors/endpoint_nadaraya_watson.py
│     # - factors/confirmed_extrema.py
│     # - factors/pytrendline_bridge.py
│     # - signals/trendline_breakout_navigator.py
├─ tests/
├─ notebooks/
├─ scripts/
└─ requirements-m1.txt
```

说明：`data/raw|bronze|silver|features` 在 `.gitignore` 中默认忽略，用于本地数据管理。

研究生命周期：
- `docs/AUDITABLE_FACTOR_RESEARCH_SKILL.md`：可审计研究资产的最低标准。
- `docs/RESEARCH_LIFECYCLE.md`：旧研究资产 / 新因子想法的标准流转流程。
- `research/factor_runs/_TEMPLATE/`：每个研究对象的标准审计卷宗模板。
- `docs/CODE_TRUST_MAP.md`：文件级代码可信度地图。
- `docs/FACTOR_BACKLOG.md`：因子研究队列和优先级。

关键脚本（当前）：
- `scripts/build_updownwave_report.py`：生成 UpWave/DownWave 研究报告
- `scripts/build_regime_triplet_report.py`：生成 Regime Triplet（上涨期/震荡期/下跌期）研究报告
- `scripts/build_box_consolidation_signals.py`：生成横盘/箱体建仓信号
- `scripts/build_box_consolidation_report.py`：生成 Box Consolidation（窄幅/箱体建仓）研究报告
- `scripts/build_kernel_extrema_foundation_report.py`：生成 Kernel Extrema Foundation 结构展示报告
- `scripts/build_pytrendline_report.py`：生成 PyTrendline 趋势线 / breakout 研究报告
- `scripts/build_trendline_breakout_navigator_report.py`：生成 clean reimplementation 趋势线突破研究报告
- `scripts/build_updownwave_insights.py`：从 artifacts 快速生成 Q1~Q14 文字洞察
- `scripts/publish_report_site.sh`：发布静态站点
- `scripts/run_report_pipeline.py`：报告流水线入口（build/insights/publish/all）
