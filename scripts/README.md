# Scripts

放置一次性或批处理脚本（拉数、批量回测、报表导出）。
稳定后建议迁移到 `src/momentum/cli.py` 子命令。

## 当前建议
- 数据刷新优先按 `docs/MAINTENANCE.md` 中的流程执行。
- 已落地：`build_chip_distribution.py`（筹码分布批处理）。
- 已落地：`build_up_down_wave_signals.py`（上涨浪/下跌浪信号批处理）。
- 等 M1 回测脚本稳定后，再把“数据拉取/标准化”进一步固化为子命令。
- 已落地：`backtest_wave_hold.py`（固定持仓天数的事件回测）。
- 默认参数由 `config/signals/up_down_wave.yaml` 管理。
- 已落地：`build_updownwave_report.py`（生成 UpWave/DownWave 网页评估报告）。
- 已落地：`build_regime_triplet_report.py`（生成 Regime Triplet：上涨期/震荡期/下跌期 报告；覆盖指数+Crypto+A/H/US个股对比）。
- 已落地：`build_box_consolidation_signals.py`（将“窄幅震荡/箱体震荡建仓”定义转为量化信号）。
- 已落地：`build_box_consolidation_report.py`（生成 Box Consolidation 因子网页报告，含数据/图表/Q&A）。
- 已落地：`build_multi_tf_momentum_signals.py`（从 5m bars 生成 5m/15m 多周期动量信号）。
- 已落地：`build_multi_tf_momentum_report.py`（多周期动量 baseline 回测 + artifacts + 网页报告）。
- 已落地：`build_pullback_recovery_confirmation_report.py`（缩量回调 + 放量恢复 的局部稳健性报告）。
- 已落地：`publish_report_site.sh`（发布 `reports/site` 到 `/var/www/momentum-report`）。
- 已落地：`publish_interview_showcase.sh`（只发布因子研究结果库和对应 CSV/PNG；适合文件很多、不想全量同步时使用）。
- 已落地：`run_report_pipeline.py`（报告流水线入口，支持 `build/insights/q1_q3/q4_q6/q7_q9/q10_q14/publish/all` 阶段）。
- 已落地：`build_updownwave_insights.py`（从 artifacts 快速生成 Q1~Q14 文字洞察，支持分组 stage）。

## 推荐执行方式（带阶段控制）
```bash
cd jerry/momentum
source .venv/bin/activate

# build + insights + publish
python scripts/run_report_pipeline.py --stage all

# 仅 build
python scripts/run_report_pipeline.py --stage build

# 仅 insights（快速）
python scripts/run_report_pipeline.py --stage insights

# 分组 insights（解耦单元）
python scripts/run_report_pipeline.py --stage q1_q3
python scripts/run_report_pipeline.py --stage q4_q6
python scripts/run_report_pipeline.py --stage q7_q9
python scripts/run_report_pipeline.py --stage q10_q14

# 仅 publish
python scripts/run_report_pipeline.py --stage publish

# 仅发布因子研究结果库，避免全量同步 reports/site 与全部 artifacts
bash scripts/publish_interview_showcase.sh

# 启用缓存（命中则跳过）
python scripts/run_report_pipeline.py --stage all --use-cache
```

可选：带完成回调
```bash
python scripts/run_report_pipeline.py --stage all --callback-text "Done: updownwave report built and published"
```
