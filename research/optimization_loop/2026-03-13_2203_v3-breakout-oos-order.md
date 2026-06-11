# 在 breakout short 内部继续缩圈：先做 support_breakout_confirm_1，再看 raw，最后才是 confirm_2

## 为什么这次选这个

这轮继续严格沿上一轮刚做出的 `v3` 最小 OOS 切片往前走，但没有再扩样本、没有再重跑 pytrendline、也没有新开题，而是做一个更细的、真正会影响下一步资源分配的小判断：

**在 breakout short 内部，`raw / confirm_1 / confirm_2` 到底谁应该先吃 first-pass OOS 资源？**

上一轮已经回答了大方向：
- breakout short 比 rebound long 更值得先做 OOS；
- 但还没有回答 breakout short 内部的顺序。

如果这一步不补，后面依然会出现“到底先跑哪个 breakout 版本”的摇摆。所以这轮最小但最有用的动作，就是直接用现有 split slice 把顺序排出来。

这轮最值得复用/借鉴的点是：**在候选已经缩到一条 family 后，下一步不该继续泛泛说“先做 breakout OOS”，而应该把资源排序细化到具体变体。**

## 核心结论（中文摘要）

核心结论：**就当前 `h24` 的 split-honesty 而言，`support_breakout_confirm_1` 比 `support_breakout_confirm_2` 更适合当 first-pass OOS 主对象；当前更合理的顺序应是：`support_breakout_confirm_1` → `support_breakout_raw` → `support_breakout_confirm_2`。**

证据如何支持这个结论：**`support_breakout_confirm_1` 在 `train / validate / test` 三段的 `h24` 均值都为负（约 `-1.45% / -0.76% / -0.51%`），且 test 段 `4/4` 资产同向为负；`support_breakout_raw` 也维持三段全负（约 `-1.45% / -1.16% / -0.87%`），但 test 段只剩 `3/4` 资产为负；相比之下，`support_breakout_confirm_2` 虽然 test 均值仍为负（约 `-0.29%`），但 test 段已出现 `3/4` 资产为正的方向分裂。说明 `confirm_1` 当前给出的 split-honesty 更干净。**

## 本轮做了什么改动

本轮只做一个主点：**在 breakout short 内部做 first-pass OOS 排序。**

具体动作：

1. 继续使用上一轮同一份样本
   - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`
   - 同样按全局 `action_timestamp` 做 `60/20/20` 的 `train / validate / test` 时间切分

2. 只比较 breakout short 的三档 support 侧变体
   - `support_breakout_raw`
   - `support_breakout_confirm_1`
   - `support_breakout_confirm_2`

3. 只看最关键的 `h24` honesty 指标
   - split 内均值是否同号
   - split 内 up ratio
   - 按资产均值是否同向

4. 更新 `docs/TODO.md`
   - 在 `V3X-E -> breakout family 先做单独 OOS` 的进度说明下补入这一层资源排序；
   - 并同步重建 `plans/momentum_todo.html`。

## 验证 / 证据

### 1) `support_breakout_confirm_1`
- `train`：
  - `events = 28`
  - `mean_ret_h24 ≈ -1.45%`
  - `pos_symbol_ratio_h24 = 0.0`
  - `neg_symbol_ratio_h24 = 1.0`
- `validate`：
  - `events = 11`
  - `mean_ret_h24 ≈ -0.76%`
  - `pos_symbol_ratio_h24 = 0.25`
  - `neg_symbol_ratio_h24 = 0.75`
- `test`：
  - `events = 8`
  - `mean_ret_h24 ≈ -0.51%`
  - `pos_symbol_ratio_h24 = 0.0`
  - `neg_symbol_ratio_h24 = 1.0`

### 2) `support_breakout_raw`
- `train ≈ -1.45%`
- `validate ≈ -1.16%`
- `test ≈ -0.87%`
- test 段 `neg_symbol_ratio_h24 = 0.75`

### 3) `support_breakout_confirm_2`
- `train ≈ -1.62%`
- `validate ≈ -0.97%`
- `test ≈ -0.29%`
- 但 test 段 `pos_symbol_ratio_h24 = 0.75`、`neg_symbol_ratio_h24 = 0.25`

### 4) 怎么解读

- `confirm_2` 在 pooled mean 上看起来还保持为负，但 test 段内部已经开始明显分裂；
- `raw` 方向也还在，但少了 confirmation 这层保护；
- `confirm_1` 则在“均值仍为负”和“按资产方向还比较整齐”之间给出了当前最干净的平衡。

## 风险 / 边界

- 这轮没有新增 event generation，只是用上一轮的 split slice 做更细排序；
- 样本仍偏小，尤其 test 段只有 `8~11` 条；
- 所以当前结论是“first-pass OOS priority order”，不是最终 alpha verdict。

## 下一步建议

1. 下一步正式 OOS 最值得先做：
   - `support_breakout_confirm_1`
2. 第二顺位：
   - `support_breakout_raw`
3. 第三顺位：
   - `support_breakout_confirm_2`
4. 在当前证据下，不建议让 `confirm_2` 抢到第一顺位，只因为它在 pooled summary 上曾更亮眼。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件与 TODO 镜像同步，不做提交。