# Rank154 / 154b Archive Close-out

更新时间：2026-05-10 03:34 UTC

## 最终状态

**Rank154 / Crypto-Stat-Arb：ARCHIVED / failed release candidate.**

**Rank154b / young funding continuation：ARCHIVED / research lead only, no paper lane.**

这份文件是 rank154 系列的收口入口。后续如果看到旧 paper runner、旧 hub、旧 admission notes 或旧 TODO 里出现 rank154，不应把它理解为当前 release candidate。

## 为什么关闭 Rank154 原策略

Rank154 原策略是一个日频截面组合：

- `carry_raw = funding_rate_last`
- `momo_10d = close.pct_change(10)`
- `breakout_raw = 19 - days_since_20d_high`
- combined score = `0.5*carry + 0.2*momo + 0.3*breakout` decile-centered

最终长历史和 postmortem 显示：

- 长历史 baseline release gate 失败；
- combined 信号长期 IC 接近 0，短 horizon 甚至偏负；
- 2022 / 2024 是强反证年份；
- Top-Bottom spread 不够厚；
- long/short leg 不是稳定双边 alpha；
- `carry` 语义本身不是传统 carry，而是“高 funding 偏多”的 crowding/trend 暴露。

结论：**不能继续通过调权重、buffer、universe size 或执行参数来救 Rank154 原组合。**

## 为什么关闭 Rank154b

Rank154b 是从 Rank154 postmortem 里拆出来的更窄假设：

> young coin 里，高 funding 可能代表 attention / crowding continuation，而不是普通老币上的 overcrowded long。

154b 当前只有一个 alpha 因子：

```text
factor = funding_rate_last
方向 = 高 funding 做多，低 funding 做空
universe = listing_days 180-365d + trailing 30d quote_volume Top30/Top50
```

严格回测和 IC 审计显示：

- 核心组合 `young 180-365d / Top30 / 5d staggered / 20bps`：总收益 `-4.3%`，年化 `-0.9%`，MaxDD `-63.1%`，Sharpe `0.14`。
- 成本曲线：`0bps +85.7%` → `10bps +33.3%` → `20bps -4.3%`，说明 gross edge 太薄。
- `5d price IC ≈ +0.0195`，说明价格延续故事有一点信号。
- 但 `5d long_total IC ≈ -0.0089`，扣 funding 后已经转负。
- 2024/2025 的 price IC 很弱，2026 前四个月贡献过大。

结论：**154b 有研究价值，但不是净 alpha；不进入 paper lane。**

## 当前网页入口

- Rank154 hub / 目录：<https://jp.jerrypsy.top/momentum/paper/rank154_hub.html>
- Rank154 postmortem：<https://jp.jerrypsy.top/momentum/paper/rank154_postmortem.html>
- Rank154b strict backtest + IC：<https://jp.jerrypsy.top/momentum/paper/rank154b_young_funding_backtest.html>
- 旧 overview：<https://jp.jerrypsy.top/momentum/paper/rank154_overview.html>
- 旧 long history：<https://jp.jerrypsy.top/momentum/paper/rank154_long_history.html>

Hub 页面应作为优先入口；旧 overview / live paper report 只保留为历史证据，不代表当前状态。

## 关键本地文件

### Final close-out

- `docs/RANK154_ARCHIVE_CLOSEOUT.md`
- `research/optimization_loop/2026-05-10_rank154_final_archive_closeout.md`

### Rank154 原策略 postmortem

- `research/optimization_loop/2026-05-09_rank154_postmortem_plan.md`
- `scripts/analyze_rank154_postmortem.py`
- `scripts/build_rank154_postmortem_report.py`
- `reports/artifacts/rank154_postmortem/factor_ic_summary.csv`
- `reports/artifacts/rank154_postmortem/yearly_factor_ic.csv`
- `reports/artifacts/rank154_postmortem/decile_spread_summary.csv`
- `reports/artifacts/rank154_postmortem/long_short_leg_summary.csv`
- `reports/artifacts/rank154_postmortem/age_bucket_ic_summary.csv`
- `reports/site/paper/rank154_postmortem.html`

### Rank154b young funding lead

- `research/optimization_loop/2026-05-09_rank154b_young_funding_hypothesis.md`
- `scripts/backtest_rank154b_young_funding.py`
- `scripts/audit_rank154b_funding_ic.py`
- `scripts/build_rank154b_young_funding_report.py`
- `reports/artifacts/rank154b_young_funding_backtest/rank154b_backtest_stats.csv`
- `reports/artifacts/rank154b_young_funding_backtest/rank154b_funding_ic_summary.csv`
- `reports/artifacts/rank154b_young_funding_backtest/rank154b_funding_spread_summary.csv`
- `reports/artifacts/rank154b_young_funding_backtest/rank154b_funding_ic_yearly.csv`
- `reports/site/paper/rank154b_young_funding_backtest.html`

## 后续规则

不要再做：

- Rank154 原 combined 权重优化；
- Rank154 原 paper lane 扩 notional；
- 把 Rank154 paper runner 的历史正收益当作 release evidence；
- 在没有新 regime 定义的情况下继续调 154b 的 TopN / holding / cost 参数；
- 把 154b 的 price IC 当作可交易净 alpha。

可以保留为 future lead 的只有两类问题：

1. **Funding 在不同上市年龄桶里的语义差异**：young coin high funding 可能是 attention continuation，old coin high funding 更像 overcrowded long。
2. **Regime-gated event strategy**：如果未来重新研究，必须先定义 risk-on / altseason / funding warm-up regime，再重新做 after-funding、after-cost 的事件策略验证。

默认动作：**Rank154 / 154b 都关闭并归档；研发队列切回其他 active P2 / fresh intake。**
