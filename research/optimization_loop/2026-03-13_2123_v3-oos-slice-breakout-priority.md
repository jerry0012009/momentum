# 用现有 purged 事件样本做第一刀 OOS 切片：breakout short 仍优先，但强度要下调

## 为什么这次选这个

这轮继续严格沿上一轮刚定下来的 `pytrendline_event_validation_v3` 优先级往前走，但仍然控制在一个很小的闭环里：**不重跑 pytrendline，不扩样本，只用现有 `event_sample_purged.csv` 先做一个最小 OOS honesty 切片。**

原因很直接：
- 上一轮已经用 `event_excess_summary.csv / family_excess_summary.csv` 做了 horizon stability 小审计；
- 但那一轮还只是“不同 horizons 是否同向”，还没回答时间顺序上的 honesty 问题；
- 当前最省成本、但最有决策价值的一小步，就是先看这些候选在 `train / validate / test` 时间切分下，会不会明显翻脸。

这轮最值得复用/借鉴的点是：**在真正重跑大样本 OOS 前，先对现有 purged 事件样本做一个时间切分 honesty slice，能很快筛掉“只在整体 pooled summary 里好看”的候选。**

## 核心结论（中文摘要）

核心结论：**基于现有 `event_sample_purged.csv` 的最小 60/20/20 时间切分，breakout short 仍然是当前最值得先做正式 OOS 的对象，但信号强度需要下调；相比之下，`support_rebound_confirm_1` 与 `resistance_breakout_confirm_1` 都表现出明显的 split-instability。**

证据如何支持这个结论：**`support_breakout_confirm_2` 在 `h24` 的 train / validate / test 三段均值分别约为 `-1.62% / -0.97% / -0.29%`，方向仍保持为负，只是 OOS 段明显变弱；`support_breakout_raw` 也在 `h24` 三段都维持为负（约 `-1.45% / -1.16% / -0.87%`）。相比之下，`support_rebound_confirm_1` 的 `h24` 呈现 `train 负 / validate 正 / test 正`（约 `-1.83% / +0.71% / +1.36%`），而 `resistance_breakout_confirm_1` 也是 `train 负 / validate 正 / test 正`（约 `-1.14% / +3.25% / +1.32%`）。这说明 breakout short 至少还保留了同向性，而其他两个候选更像样本期敏感对象。**

## 本轮做了什么改动

本轮只做一个主点：**基于现有 purged 事件样本做第一刀时间切分 OOS slice。**

具体动作：

1. 读取现有样本
   - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`

2. 用全样本 `action_timestamp` 做全局时间切分
   - `train = 前 60%`
   - `validate = 中间 20%`
   - `test = 最后 20%`

3. 对 4 个当前最值得比较的对象做 split summary
   - `support_breakout_confirm_2`
   - `support_breakout_raw`
   - `support_rebound_confirm_1`
   - `resistance_breakout_confirm_1`

4. 产物
   - `reports/artifacts/pytrendline_event_validation_v3_oos_slice_v1/oos_split_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_oos_slice_v1/oos_split_by_asset.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_oos_slice_v1/summary.json`

5. 更新 `docs/TODO.md`
   - 在 `V3X-E` 下补入这轮 split-honesty 进度判断；
   - 并同步重建 `plans/momentum_todo.html`。

## 验证 / 证据

### 1) `support_breakout_confirm_2`（当前 breakout short 主候选）

#### h24
- `train`：`mean_ret ≈ -1.62%`（28 events）
- `validate`：`mean_ret ≈ -0.97%`（10 events）
- `test`：`mean_ret ≈ -0.29%`（8 events）

#### h48
- `train ≈ -4.02%`
- `validate ≈ -0.44%`
- `test ≈ -0.02%`

#### h72
- `train ≈ -5.97%`
- `validate ≈ +3.09%`
- `test ≈ -1.50%`

怎么读：
- 这条线最值得注意的是：`h24` 在三段里仍保持同为负值；
- 但强度从 train 到 validate/test 明显衰减；
- 说明它仍是最值得优先 OOS 的 short 候选，但不应再被当成“强确定性负 alpha”解读。

### 2) `support_breakout_raw`

#### h24
- `train ≈ -1.45%`
- `validate ≈ -1.16%`
- `test ≈ -0.87%`

#### h48 / h72
- `h48`：`train ≈ -3.52% / validate ≈ +0.23% / test ≈ -1.05%`
- `h72`：`train ≈ -5.19% / validate ≈ +3.59% / test ≈ -1.73%`

怎么读：
- 它在 `h24` 上比 `confirm_2` 还更稳定地维持为负；
- 但更长 horizon 已开始出现 split 混合；
- 这说明 raw breakout 也值得保留在 OOS 篮子里，但仍需要更长样本来确认是否只是短 horizon 效应。

### 3) `support_rebound_confirm_1`

#### h24
- `train ≈ -1.83%`
- `validate ≈ +0.71%`
- `test ≈ +1.36%`

#### h48 / h72
- `h48`：`train ≈ -3.65% / validate ≈ +0.24% / test ≈ +0.62%`
- `h72`：`train ≈ -5.17% / validate ≈ +2.93% / test ≈ +0.59%`

怎么读：
- 它不是“持续为正”的 long 候选；
- 而是典型的 **train 负、后段转正** 的 split-instability；
- 当前更适合作为 `watch`，不适合先吃第一顺位 OOS 资源。

### 4) `resistance_breakout_confirm_1`

#### h24
- `train ≈ -1.14%`
- `validate ≈ +3.25%`
- `test ≈ +1.32%`

怎么读：
- 这条线看起来“后两段很亮”，但恰恰因为前段是负的，所以当前不能轻易把它当成稳定候选；
- 更像 regime / sample-phase 敏感对象。

## 风险 / 边界

- 这轮不是完整 OOS report，只是第一刀 split-honesty slice；
- 切分是全局时间切分，不是更正式的 walk-forward；
- 由于只用现有 purged 事件样本，没有重算 split 内基线，因此这轮重点看的是“方向 / 均值是否翻脸”，不是精确 split-excess；
- 事件数也不大（例如 `support_breakout_confirm_2` test 只有 8 条），因此不能过度下结论。

## 下一步建议

1. 下一步正式 OOS 仍应优先给 breakout short：
   - `support_breakout_confirm_2`
   - `support_breakout_raw`
2. 但当前口径应更保守：
   - 从“最强 shortlist”下调为“first-pass OOS priority, but honesty-risk remains”。
3. `support_rebound_confirm_1` 与 `resistance_breakout_confirm_1` 暂时不应抢第一顺位 OOS 资源。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件、artifact 落盘与 TODO 镜像同步，不做提交。