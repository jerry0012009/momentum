# analytics

## 职责
- 产出回测核心指标与报告（收益、回撤、夏普等）

## 当前状态
- 已新增 `wave_hold_backtest.py`：
  - 信号事件回测（T 日信号，T+1 开盘进场，持有 N 日，按收盘离场）
- 已新增 `report_pipeline.py`（第一阶段）：
  - 报告流水线编排入口（`build / insights / publish / all`）
  - 可选完成回调（用于长任务自动通知）
- 已新增 `updownwave_insights.py`：
  - 从已生成 artifacts 独立汇总 Q1~Q14 文字洞察（json + md）
  - 支持按 Q 组分段运行（Q1~Q3 / Q4~Q6 / Q7~Q9 / Q10~Q14）

## M1 下一步
- 继续将 `build_updownwave_report.py` 拆分为 stage 函数（Q1~Q14）
  - 当前已抽离：`compute_core_baseline_metrics()`、`compute_usage_q1_q3()`、`compute_usage_q4_q6()`、`compute_usage_q7_q9()`、`compute_usage_q10_q11()`、`compute_usage_q12_q14()`
- 增加 stage 级缓存与增量重跑
- 增加更完整的绩效统计（回撤、年化、夏普、卡玛）
