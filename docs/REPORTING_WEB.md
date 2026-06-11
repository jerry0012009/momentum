# Web Reporting（可复用）

用于将 `momentum` 项目的因子评估结果以静态网页方式发布，便于后续持续追加其他因子。

## 目录约定

- 原始产物：`reports/artifacts/<factor>/`
- 网页站点：`reports/site/`
- 因子页面：`reports/site/factors/<factor>/report.html`

当前已落地：
- `factors/updownwave`
- `factors/regime_triplet`
- `factors/box_consolidation`
- `factors/multi_tf_momentum`
- `factors/pullback_recovery_confirmation`
- `learning-mainline1-map.html`（主线1学习地图，支持勾选进度）
- `single-factor-template.html`（单因子记录模板网页版）
- `reading/quant_digests/report.html`（自动研究笔记聚合页）
- `reading/deep_dives/report.html`（长篇研究报告聚合页）
- `reading/trendline_alpha_scout/report.html`（外部 alpha / 文献侦察总览页）
- `reading/trendline_replication_briefs/report.html`（外部论文 clean-room replication brief 页面）
- `reading/chan2022_paper_spec/report.html`（Chan 2022 faithful replication 规范提取页）
- `reading/chan2022_sr_feature_replication/report.html`（Chan 2022 第一版 clean-room 复现报告）

## 生成报告

```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/build_updownwave_report.py
```

或使用流水线入口（推荐）：
```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/run_report_pipeline.py --stage build
```

快速生成文字洞察（不重跑全量回测）：
```bash
python scripts/run_report_pipeline.py --stage insights
# 会产出 reports/artifacts/updownwave/insights_q1_q14.{json,md}
```

分组洞察（独立解耦单元）：
```bash
python scripts/run_report_pipeline.py --stage q1_q3
python scripts/run_report_pipeline.py --stage q4_q6
python scripts/run_report_pipeline.py --stage q7_q9
python scripts/run_report_pipeline.py --stage q10_q14
# 会产出 insights_q1_q3.* / insights_q4_q6.* / ...
```

缓存模式（基础跳过）：
```bash
python scripts/run_report_pipeline.py --stage all --use-cache
# 若 report/manifest 或 insights 产物已存在，对应 stage 会跳过
```

生成后会刷新：
- `reports/artifacts/updownwave/*.csv`
  - 重点：`universe_coverage.csv`（成功加载的资产清单）
  - 重点：`universe_failed.csv`（加载失败清单）
  - 重点：`sensitivity_cost_big_table.csv`（asset_class × market × ma × mode × hold × cost 大表）
  - 重点：`sensitivity_param_agg_cross_market.csv`（跨市场参数聚合）
  - 重点：`sensitivity_cost_agg_cross_market.csv`（跨市场成本聚合）
  - 重点：`sensitivity_break_even_cost.csv`（成本抗压阈值）
  - 重点：`market_year_regime.csv` / `annual_regime_summary.csv`（年份趋势分类）
- `reports/site/factors/updownwave/report.html`
- `reports/site/factors/updownwave/assets/*.png`
- `reports/site/index.html`

## 发布到 Web

```bash
cd jerry/momentum
bash scripts/publish_report_site.sh
```

或使用流水线入口：
```bash
cd jerry/momentum
source .venv/bin/activate
python scripts/run_report_pipeline.py --stage publish
```

脚本会先自动执行 `python3 scripts/build_quant_digest_site.py`、`python3 scripts/build_deep_dive_site.py`、`python3 scripts/build_plans_site.py`、`python3 scripts/build_trendline_tracks_site.py`、`python3 scripts/build_site_index.py`，再将 `reports/site/` 同步到 `/var/www/momentum-report/`。

站点首页 `reports/site/index.html` 会自动扫描各 `report.html` 页面，展示“最新更新时间”，并按更新时间倒序排列（最新更新优先）。

对于最近拆得比较细的趋势线研究：首页会优先展示两个大入口：
- `factors/trendline_pyindicator_track/report.html`
- `factors/trendline_pytrendline_track/report.html`

原始小报告不会删除，但默认不再在首页逐个铺开，而是收拢到这两个 track 页面里统一查看。

## 访问地址

- 常规：https://jp.jerrypsy.top/momentum/
- 非常用端口：https://jp.jerrypsy.top:24443/momentum/

## 扩展到新因子

建议复用同样的结构：
1. 新建 `scripts/build_<factor>_report.py`
2. 产出到 `reports/artifacts/<factor>/`
3. 网页放在 `reports/site/factors/<factor>/report.html`
4. 在 `reports/site/index.html` 增加入口链接

研究笔记（digest）走另一条自动链路：
1. 写入 `research/quant_digests/*.md`
2. 运行 `python3 scripts/build_quant_digest_site.py`
3. 自动生成 `reports/site/reading/quant_digests/*.html`
4. 再发布到站点

这样后续可以逐个追加，不破坏已有报告。

## 报告重构路线（进行中）

当前目标是把“单一大脚本”逐步升级为“可分阶段、可复用”的因子评估工具。第一阶段已落地流水线入口：
- `scripts/run_report_pipeline.py`
- `src/momentum/analytics/report_pipeline.py`

后续将继续推进：
1. 按研究问题拆分 stage（Q1~Q3 / Q4~Q6 / Q7~Q9 / Q10~Q14）
2. 引入中间产物缓存与参数指纹
3. 支持增量重跑与快速渲染
4. 抽象成因子适配器（可复用到新因子）

详见：`docs/REPORT_PIPELINE_REFACTOR.md`
