# Trendline interval sweep：补一层 long 侧资产赢家视图

## Why this was chosen now

当前最近未完主线还是 `trendline_segment_backtest` 的 Round A/B/C 优化后 interval sweep。
现有报告已经有 cross-asset 汇总，但还缺一个很关键的决策视角：**每个资产在 long 侧到底是哪一组 interval + strategy 真正赢了**。

这层视角能直接回答两个问题：
1. 下一步默认主线应该继续押 `30m rebound-long`，还是保留 `60m rebound-long` 作为并行候选；
2. `breakout-long` 是否还有继续投入的必要，还是应该阶段性降级。

## What changed

本轮没有重跑重型回测，而是复用本地已有的 `interval_strategy_summary.csv`，新增了一个轻量决策辅助脚本与两个衍生表：

### 1) 新增脚本
- `scripts/build_trendline_interval_long_winners.py`

作用：
- 从已有 interval sweep 汇总中提炼 **long 侧每资产最优配置**
- 同时输出 **rebound-long 的 5m / 15m / 30m / 60m 对比表**

### 2) 新增 artifact
- `reports/artifacts/trendline_segment_backtest_interval_sweep/interval_long_asset_winners.csv`
- `reports/artifacts/trendline_segment_backtest_interval_sweep/rebound_long_interval_compare.csv`

## Validation / evidence

### A. long 侧逐资产赢家结论
按 `total_return` 选每个资产的 long 侧最优配置，结果是：

- 8/8 个资产的赢家全部来自 **rebound-long**
- 其中 **30m rebound-long 占 6 个资产**：BTC / ETH / SOL / BNB / ADA / AVAX
- **60m rebound-long 占 2 个资产**：DOGE / XRP
- **breakout-long 在任何资产上都不是 long 侧最优配置**

这说明当前 Round A 之后，若只看核心 long 主线，研究资源应继续向 **rebound-long** 倾斜，而不是 breakout-long。

### B. cross-asset 层面的主候选对比
从现有 `interval_cross_asset_summary.csv` 可读出：

- `30m rebound-long`
  - positive_asset_ratio = `0.875`
  - mean_total_return = `+7.62%`
  - mean_max_drawdown = `-2.40%`
  - total_trades = `76`

- `60m rebound-long`
  - positive_asset_ratio = `0.500`
  - mean_total_return = `+2.95%`
  - mean_max_drawdown = `-3.74%`
  - total_trades = `45`

- `15m rebound-long`
  - positive_asset_ratio = `0.625`
  - mean_total_return = `+0.33%`

- `5m rebound-long`
  - positive_asset_ratio = `0.250`
  - mean_total_return = `-2.23%`

当前证据下，**30m rebound-long 是最适合继续做默认主线的 interval**。

### C. 30m vs 60m 的资产差异
新增的 `rebound_long_interval_compare.csv` 说明：

- `30m` 明显优于 `60m` 的资产：ETH / SOL / AVAX / BNB / BTC / ADA
- `60m` 明显优于 `30m` 的资产：DOGE / XRP

这提示下一步不必急着把 60m 全盘砍掉；更合理的动作是：
- 主线先锁 `30m rebound-long`
- 然后单独检查 DOGE / XRP 为什么更偏向 60m（波动簇、噪声密度、线段确认节奏，或 ATR trailing stop 的交互）

## Risks / caveats

- 这轮只做了 **基于已有 artifact 的解释层提纯**，没有新增回测样本，也没有做 rolling / OOS。
- 赢家标准目前按 `total_return` 选，尚未做更复杂的稳健性评分。
- DOGE / XRP 的 60m 优势，可能部分来自样本窗口偶然，需要后续 rolling 验证。

## Next recommended step

下一轮最值得做的小步动作是二选一：

1. **优先方案**：围绕 `30m rebound-long` 做 rolling / OOS 小验证，确认它不是这 60d 样本的偶然最优；
2. **次优方案**：对 `DOGE / XRP` 做 `30m vs 60m rebound-long` 的资产级对照分析，查明它们为何偏向 60m。

## Commit hash (code/artifacts)

8f1e1ff59298cc3ab871495dce58006bd8978da5

## Commit note

本轮 repo 内存在其他未合并的脏文件（来自更早的 interval/report 迭代），因此只做 selective commit，不打包无关改动。
