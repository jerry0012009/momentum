# EMA / PSAR overlay 失败进一步拆到 trade_delta 诊断层

## 为什么这次选这个

这轮继续沿 `EMA / PSAR raw alpha focus` 推进，但不再补 protocol / decision copy，而是在已经有的真实 overlay 结果上再切一刀真正有用的小诊断：**`PSAR exit overlay` 到底是不是主要因为把交易次数抬得太高，才把 net20 结果压坏。**

之所以选这个点：
1. `EMA 60m rolling slice` 和 `EMA 60m + PSAR exit overlay` 的真实结果已经落页；
2. 当前最值得继续追问的小问题，不是“overlay 有没有失败”，而是“它为什么失败”；
3. 这可以完全复用已有 `ema60m_psar_exit_overlay_window_metrics.csv`，不需要重跑下载或新增重回测。

## 做了什么改动

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 基于现有 `overlay_window_df` 新增 `trade_delta` 诊断层；
   - 新增一张 artifact：
     - `reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_trade_delta_buckets.csv`
   - 新增一个网页段：
     - **Q15. `PSAR exit overlay` 这次为什么更像是在放大交易次数，而不是在修复 EMA？**
   - 该段现在会直接回答：
     - `trade_delta` 与 `net20_delta` 的相关性；
     - 多加很多交易的窗口是否还能改善；
     - 少加一点交易时是否至少偶尔有帮助。
2. 更新 `docs/TODO.md`
   - 在 `EMA + PSAR` 最小组合研究条目下补上这轮 `trade_delta` 诊断结果；
   - 并同步到 `reports/site/plans/momentum_todo.html`。
3. 重建可见产物
   - `reports/site/factors/ema_psar_raw_alpha/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键结果

基于 `ema60m_psar_exit_overlay_window_metrics.csv` 的 30 个窗口：

### 1) 额外交易越多，结果通常越差

- `trade_delta` 与 `net20_delta` 的相关系数约 `-0.68`

这已经不是弱噪声，而是很明显的负相关：overlay 越是把 EMA 原策略切碎、抬高出入场频率，cost-adjusted 改善通常越不容易出现。

### 2) 高换手窗口基本没有救到 EMA

当 overlay 额外多出至少 `50` 笔交易时：
- 这类窗口约 `5/30`
- `0%` 窗口出现 net20 改善
- 中位 `net20 delta` 约 `-9.71pp`
- 中位 `trade_delta` 约 `55`

这说明最激进的快退出版本，几乎纯粹是在放大交易成本负担。

### 3) 就算交易增加得没那么夸张，也还谈不上稳定 rescue

当 overlay 额外交易控制在 `<45` 笔时：
- 这类窗口约 `13/30`
- 其中约 `4/13`（`30.77%`）窗口出现 net20 改善
- 但中位 `net20 delta` 仍约 `-1.13pp`

所以它最多算“有时少伤一点”，还远谈不上稳定把坏窗口修回来。

## 当前更清楚的项目级读法

这轮之后，对 `PSAR exit overlay` 的理解更明确了：
- 它失败并不只是抽象意义上的“没改善”；
- 更像是：在这批 60m crypto cache 上，`PSAR` 把 EMA 原本就不稳的区间切得更碎、更频繁出入；
- 但这些更快退出没有换来足够多的坏窗口修复，于是交易成本先把它吃掉了。

换句话说，当前更像是 **turnover problem > rescue benefit**。

## 验证 / 证据

验证命中：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现：
  - `Q15. PSAR exit overlay 这次为什么更像是在放大交易次数，而不是在修复 EMA？`
  - `相关系数约 -0.68`
- `reports/artifacts/ema_psar_raw_alpha/ema60m_psar_exit_overlay_trade_delta_buckets.csv` 已生成
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步这条诊断结论

## 下一步建议

这轮之后，如果还继续 `EMA / PSAR` 线，最合理的小步是二选一：
1. 去看 `日 / 周频 baseline family` 是否还站得住；
2. 或进一步诊断 `PSAR overlay` 的坏处具体来自哪里（例如：过早止盈、来回 whipsaw、还是 regime 不匹配）。

但无论如何，都不该再把当前 60m overlay 包装成“差一点就救回来”。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_ema_psar_raw_alpha_report.py`、`reports/site/factors/ema_psar_raw_alpha/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
