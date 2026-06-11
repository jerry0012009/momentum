# 用现成 v3 事件样本补一刀 volume-confirmation：当前没证据支持把它升成默认 breakout 过滤器

## 为什么这次选这个

这轮我没有继续补来源卡。

原因很直接：前几轮已经连续把 `regime gate`、`volume-confirmed breakout`、`third-touch + EMA/MACD confluence` 这些外部材料推进成正式来源卡了；如果继续只补 source card，就容易变成“只进不验”。

更有价值的一小步，是把刚刚补完来源卡的那条 `volume-confirmed breakout` 线，直接拉回当前主线做一个**最小本地验证切片**：
- 不重跑 pytrendline；
- 不改事件生成代码；
- 只用现成 `event_sample_purged.csv` + cache K 线；
- 看 `support_breakout_raw` 在加了一个非常朴素的 `volume confirmation` 后，`h24` 的 OOS honesty 是否真的更好。

这轮最值得复用/借鉴的点是：**外部论文里“听起来合理”的 confirmation 层，不该直接当默认过滤器；先在现有样本上补一刀最小切片，能更快排除“直觉很好但本地没增量”的对象。**

## 核心结论（中文摘要）

核心结论：**在当前 `pytrendline_event_validation_v3` 的 45d / 60m 样本里，给 `support_breakout_raw` 加一个非常朴素的 `volume confirmation`（`event volume / prev20 median volume >= 1.2 / 1.5`）并没有让 `h24` 的 OOS honesty 更好，反而显著压缩了可用样本。**

证据如何支持这个结论：**在保留 `prev20 median volume > 0` 的可用事件后，裸 `support_breakout_raw` 的 `h24 avg_excess_ret` 在 validate / test 约为 `-3.11% / -2.33%`；而加上 `>=1.2x` 放量过滤后，validate 只剩 `4` 条、test 只剩 `1` 条，`avg_excess_ret` 约为 `-2.75% / -2.08%`，并没有比裸 breakout 更干净；`>=1.5x` 时样本更小，结论更不稳。**

## 本轮做了什么改动

本轮只做一个主点：**对 `support_breakout_raw` 补一刀 volume-confirmation 小切片。**

具体动作：

1. 使用现有 artifacts，不重跑主报告
   - 输入：
     - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`
     - `reports/artifacts/pytrendline_event_validation_v3/cache/*.csv`

2. 固定对象与口径
   - 对象：`support_breakout_raw`
   - horizon：`h24`
   - split：沿用当前全局 `60/20/20` 的 `train / validate / test`
   - volume feature：
     - `event bar volume / previous 20-bar median volume`
   - 过滤阈值：
     - `>= 1.2`
     - `>= 1.5`

3. 只保留可计算 volume 特征的事件
   - 为避免 `prev20 median volume = 0` 导致 `inf`，这轮只保留：
     - `prev20_median_vol > 0`
   - 这一步是为了让结果可解释，不把无效 volume 样本混进去。

4. 产物
   - `reports/artifacts/pytrendline_event_validation_v3_volume_filter_slice_v1/support_breakout_raw_volume_filter_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_volume_filter_slice_v1/support_breakout_raw_volume_filter_by_asset.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_volume_filter_slice_v1/coverage.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_volume_filter_slice_v1/summary.json`

5. 更新 `docs/TODO.md`
   - 在 `V3X-E` breakout family OOS 进度下补充：
     - 当前简单 `volume confirmation` 没有显示出比裸 breakout 更干净的 OOS 增量；
     - 暂不把它升为默认过滤器。

## 验证 / 证据

### 1) 可用样本覆盖
在加入 `prev20_median_vol > 0` 约束后：
- `train`: `14` 条
- `validate`: `9` 条
- `test`: `4` 条

这已经说明：**当前 volume 数据口径本身就会明显缩小可分析样本。**

### 2) 裸 `support_breakout_raw`（只看 valid-vol 子样本）
- `validate`
  - `events = 9`
  - `mean_ret_h24 ≈ -2.35%`
  - `avg_excess_ret_h24 ≈ -3.11%`
  - `4/4` 资产负 excess
- `test`
  - `events = 4`
  - `mean_ret_h24 ≈ -1.89%`
  - `avg_excess_ret_h24 ≈ -2.33%`
  - `4/4` 资产负 excess

### 3) 加 `volume >= 1.2 × prev20 median`
- `validate`
  - `events = 4`
  - `avg_excess_ret_h24 ≈ -2.75%`
  - `3` 个资产负 excess
- `test`
  - `events = 1`
  - `avg_excess_ret_h24 ≈ -2.08%`
  - 只剩 `1` 个资产事件

### 4) 加 `volume >= 1.5 × prev20 median`
- `validate`
  - `events = 3`
  - `avg_excess_ret_h24 ≈ -1.81%`
- `test`
  - `events = 1`
  - `avg_excess_ret_h24 ≈ -2.08%`

### 5) 怎么解读

最诚实的读法不是“volume filter 无效，永远别用了”，而是：

1. **在这份 45d / 60m 样本里，最简单的放量门槛没有显示出额外增量；**
2. 它的问题不只是“结果没更好”，还包括：
   - 样本数大幅下降；
   - OOS 尤其 test 段几乎被压到不可读；
3. 因此当前更合理的态度是：
   - `volume confirmation` 可以继续保留为候选确认层；
   - 但现在没有证据支持把它升成 `support_breakout_raw` 的默认过滤器。

## 风险 / 边界

- 这轮没有新增事件生成，只是对现有事件做了一个简单的 volume gate；
- `volume` 本身来自当前 yfinance cache，质量和 market microstructure 解释力都有限；
- 过滤后样本很小，尤其 test 段只剩 `1` 条，因此不能过度解读“过滤后更差 / 更好”的数值本身；
- 当前更像是一个 **negative screening**：先排除“简单放量门槛已经明显更好”的乐观假设。

## 下一步建议

如果后续继续沿这条线往下走，最有价值的不是加更高阈值，而是：

1. 改成更贴近结构的 volume/filter 组合：
   - `breakout + support-flip`
   - `breakout + higher-low`
   - `breakout + volume only when support-flip also成立`
2. 或者把 volume 当排序特征，而不是硬阈值过滤器；
3. 在更长样本上再复核一次，而不是急着把它升成默认 gate。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成 artifact、TODO、日志与邮件同步，不做提交。