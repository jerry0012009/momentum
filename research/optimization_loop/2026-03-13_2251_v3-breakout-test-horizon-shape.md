# 只看 test 段再补一刀：breakout short 不是 h6 立刻下跌，而更像 h24+ 才展开

## 为什么这次选这个

这轮继续沿同一条 `pytrendline_event_validation_v3` 主线推进，而且仍然刻意保持“只做一件小事”。

上一轮已经把 breakout short 内部顺序排出来了：
- `support_breakout_confirm_1`
- `support_breakout_raw`
- `support_breakout_confirm_2`

但还有一个关键问题没完全说透：**这条 short thesis 到底是超短线立刻兑现，还是更像需要更长 horizon 才展开？**

如果这个问题不先补清楚，后面即使做正式 OOS，也容易把注意力放错地方，例如误把它当 `h6` 短打空头，而不是 `h24+` continuation short。

所以这轮最值钱的小步，是只看 test 段，专门比较这三档在 `h6 / h24 / h48 / h72` 的形状。

这轮最值得复用/借鉴的点是：**一个 short 候选即使在 24h 以后方向很稳，也可能在最短 horizon 先逆着你走；如果不先看 horizon shape，就很容易把同一条信号用错 holding frame。**

## 核心结论（中文摘要）

核心结论：**当前 breakout short 这条线不适合被理解成“事件后立刻下跌”的 `h6` 空头信号；更合理的解释是：它在 test 段的负向优势主要从 `h24+` 才开始显现，而其中 `support_breakout_confirm_1` 的跨资产方向最干净。**

证据如何支持这个结论：**在 test 段，三档 breakout short 的 `h6` 均值都还是正的：`support_breakout_confirm_1 ≈ +0.69%`、`support_breakout_confirm_2 ≈ +0.34%`、`support_breakout_raw ≈ +0.25%`；说明它们并不是“事件后立刻就跌”。但到 `h24 / h48 / h72`，`support_breakout_confirm_1` 变成稳定负值（约 `-0.51% / -0.59% / -1.42%`），且 `4/4` 资产均值同向为负；相比之下，`confirm_2` 在 `h24` 的 pooled mean 虽然为负，但 test 段按资产却有 `3/4` 为正，方向更分裂。**

## 本轮做了什么改动

本轮只做一个主点：**对 breakout short 三档做 test-only horizon shape 切片。**

具体动作：

1. 继续使用现有样本
   - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`
   - 沿用上一轮定义好的全局 `60/20/20` 时间切分

2. 只保留 test 段
   - 比较对象：
     - `support_breakout_raw`
     - `support_breakout_confirm_1`
     - `support_breakout_confirm_2`

3. 输出两个最小 artifact
   - `reports/artifacts/pytrendline_event_validation_v3_test_slice_v1/test_only_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_test_slice_v1/test_only_by_asset.csv`

4. 更新 `docs/TODO.md`
   - 把这条“不是 h6 立刻跌，而更像 h24+ continuation short”的约束写回 `V3X-E`；
   - 并同步重建 `plans/momentum_todo.html`。

## 验证 / 证据

### 1) test 段的 `h6`

- `support_breakout_confirm_1`：`mean_ret ≈ +0.69%`
- `support_breakout_confirm_2`：`mean_ret ≈ +0.34%`
- `support_breakout_raw`：`mean_ret ≈ +0.25%`

这说明：
- 三档在最短 horizon 上都没有体现出“立刻下跌”的短空特征；
- 如果后续把这条线硬套成 `h6` 空头，很可能会误用。

### 2) test 段的 `h24 / h48 / h72`

#### `support_breakout_confirm_1`
- `h24 ≈ -0.51%`
- `h48 ≈ -0.59%`
- `h72 ≈ -1.42%`
- `4/4` 资产在 `h24 / h48 / h72` 上都同向为负

#### `support_breakout_raw`
- `h24 ≈ -0.87%`
- `h48 ≈ -1.05%`
- `h72 ≈ -1.73%`
- 但 `h24` 资产方向只有 `3/4` 为负，干净度略差

#### `support_breakout_confirm_2`
- `h24 ≈ -0.29%`
- `h48 ≈ -0.02%`
- `h72 ≈ -1.50%`
- `h24` 的 pooled mean 为负，但按资产却出现 `3/4` 为正，方向分裂最明显

### 3) 怎么读

- 如果只看 pooled mean，容易误以为 `confirm_2` 还行；
- 但一旦只看 test 段、再看按资产方向，`confirm_1` 更干净；
- 更重要的是：**这条 short 候选的生效节奏，不像“马上跌”，而更像“先扰动，再往下走”。**

## 风险 / 边界

- 这轮只是 test-only shape 切片，不是完整 OOS 报告；
- test 样本仍然很小（每档大约 8 个 events）；
- 所以当前结论是“如何正确理解 holding frame”，不是“策略已经定型”。

## 下一步建议

1. 如果下一步进入正式 OOS，`support_breakout_confirm_1` 仍是第一顺位；
2. 但评估重点应放在：
   - `h24 / h48 / h72` 的 continuation short honesty
   - 而不是 `h6` 的 immediate short alpha
3. 这也意味着后续任何报告里，都不该把它包装成“超短线 break-and-dump”型信号。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件、artifact 落盘与 TODO 镜像同步，不做提交。