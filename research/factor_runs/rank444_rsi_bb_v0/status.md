# Rank444 RSI + BB — Status

## Research Identity

- **rank_id:** rank444
- **name:** RSI + Bollinger Bands 均值回复策略研究包
- **type:** strategy (NOT a pure factor)
- **version:** v0 (audit baseline)
- **created:** 2026-06-12

## Status Fields

```yaml
research_status: REVIEW_REQUIRED
code_trust_initial: B
promotion_status: NOT_PAPER_OR_LIVE_ELIGIBLE
```

## Status Rationale

### REVIEW_REQUIRED

Rank444 经历了 6 轮迭代（v1→v6），产出 14 个脚本和 6 个结果 JSON，但从未经过正式审计。主要问题：

1. **数据未固化** — 每次运行都从 yfinance / akshare 实时拉取，无法保证复现
2. **same-bar signal+execution** — 信号和执行都在同一根 bar 的 close 上，存在乐观偏差
3. **Sharpe 计算非标准** — 使用 trade-level 简化公式，不是 bar-level equity curve Sharpe
4. **无独立因子/信号产物** — RSI 和 BB 计算嵌入回测函数，无法单独审计
5. **成本模型不完整** — 有手续费（0.1% 单边），无滑点、无 spread、无资金成本

### code_trust_initial: B

- **B = research usable** — 代码能跑、逻辑清晰、有参数网格验证
- 不能升 A 的原因：数据获取、指标计算、信号生成、回测逻辑全部耦合在同一脚本中；无测试用例；无固定数据快照

### NOT_PAPER_OR_LIVE_ELIGIBLE

不满足晋级条件（参照 AUDITABLE_FACTOR_RESEARCH_SKILL.md §13）：

- [ ] 冻结输入数据或数据 manifest
- [ ] 独立 factor values（data/features/）
- [ ] 独立 signals
- [ ] 独立 trades（parquet 格式）
- [ ] 完整成本模型
- [ ] 标准 PnL / Sharpe 计算方法
- [ ] 无未解决的未来函数问题
- [ ] factor memo
- [ ] 复现命令
- [ ] 已审核的 Code Trust 状态

## Related Artifacts

| 产物 | 路径 | 说明 |
|------|------|------|
| v1 脚本 | `scripts/rank444_rsi_bb_backtest.py` | 基础回测引擎 |
| v2 脚本 | `scripts/rank444_full_backtest.py` | 多频率+参数稳定性+时间稳定性 |
| v3-v6 脚本 | `scripts/rank444_v{3,4,5,6}_*.py` | regime / cn_futures / long_short |
| 报告生成器 | `scripts/rank444_gen_report_*.py` | 各版本报告生成 |
| 结果 JSON | `reports/artifacts/rank444_rsi_bb/` | 6 个 JSON（v1→v6） |
| HTML 报告 | `reports/site/paper/rank444_rsi_bb.html` | 综合研究报告 |
| Fresh intake | `research/optimization_loop/2026-06-12_rank444_rsi_bb_freshintake_keep_p1.md` | 判定: keep_P1 |
