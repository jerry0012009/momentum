# 给 Fibonacci 线做临时 intake 判断：先留在 reading/ 的 confirmation-filter，不升 factors/

## 为什么这次选这个

这轮没有再扩新来源，也没有继续加新实验变体，而是把刚刚连续两轮真实验证跑出来的 Fibonacci 结果，压成一个明确的 `intake decision`。

原因很直接：
- 前两轮已经不是“纸上谈兵”，而是已经真实跑过 `baseline / confirm_1bar / confirm_2of3 / retest_hold`；
- 如果这时还不做判断，就又会回到 Jerry 刚刚担心的那种状态：一直在补材料、补流程、补实验，却迟迟不回答“这条线到底值不值得继续升格”。

所以这轮最合适的小步，不是再补实验，而是先做一个**停损式判断**：当前阶段，Fibonacci 到底该不该从 `reading/` 升到 `factors/`。

这轮最值得复用/借鉴的点是：**当一条外部候选已经连续做了两刀本地验证、但仍没有给出清晰正边际时，最有价值的动作往往不是继续拖，而是先做一个诚实的“暂不升级”决策。**

## 核心结论（中文摘要）

核心结论：**基于当前两刀本地验证结果，`Gurrib et al. (2022)` / Fibonacci 这条线暂时**不**升入 `factors/`，仍保留在 `reading/` 侧，定位为 `confirmation / filter candidate`。**

证据如何支持这个结论：**它确实在 15m BTC/ETH/SOL 的本地切片里降低了快速失效比例：`baseline` 的 `12-bar invalidation ratio` 约 `51.3%`，而 `confirm_1bar / confirm_2of3 / retest_hold` 分别约 `32.2% / 31.0% / 37.1%`；其中 `retest_hold` 还给出了四档里最不差的整体 trade-off（`mean_net_return ≈ -0.024%`，优于 `baseline ≈ -0.042%`、`confirm_1bar ≈ -0.068%`、`confirm_2of3 ≈ -0.029%`）。但关键问题是：**四档在 10bps 成本下聚合 net return 仍都没有转正**，因此证据还不够支撑把它升级成“本地候选因子”。**

## 本轮做了什么改动

本轮只做一个主点：**给 Fibonacci 线做临时 intake decision。**

具体改动：

1. 汇总前两轮本地验证
   - `reports/artifacts/fibonacci_confirmation_slice_v1/summary_by_variant.csv`
   - `reports/artifacts/fibonacci_confirmation_slice_v2/summary_by_variant.csv`

2. 把判断写回 `docs/TODO.md`
   - 在 `E3-C` 的 factor intake decision 进度下追加：
     - 当前不把 `Gurrib et al. (2022)` 升入 `factors/`；
     - 暂时保留在 `reading/` 侧；
     - 当前角色是 `confirmation / filter candidate`；
     - 不升级的理由是：虽然能减少快速失效，但聚合 net return 仍未转正。

3. 最小重建镜像页
   - 重建：`reports/site/plans/momentum_todo.html`
   - 同步到：`/var/www/momentum-report/plans/momentum_todo.html`

## 验证 / 证据

### 1) 第一刀（v1）聚合结果
- `baseline`：
  - `mean_net_return ≈ -0.043%`
  - `invalidation_ratio_12b ≈ 51.3%`
- `confirm_1bar`：
  - `mean_net_return ≈ -0.070%`
  - `invalidation_ratio_12b ≈ 32.3%`
- `confirm_2of3`：
  - `mean_net_return ≈ -0.031%`
  - `invalidation_ratio_12b ≈ 31.0%`

### 2) 第二刀（v2，加上 retest_hold）聚合结果
- `baseline`：
  - `mean_net_return ≈ -0.042%`
  - `win_ratio ≈ 45.4%`
  - `invalidation_ratio_12b ≈ 51.3%`
- `confirm_1bar`：
  - `mean_net_return ≈ -0.068%`
  - `win_ratio ≈ 42.8%`
  - `invalidation_ratio_12b ≈ 32.2%`
- `confirm_2of3`：
  - `mean_net_return ≈ -0.029%`
  - `win_ratio ≈ 44.1%`
  - `invalidation_ratio_12b ≈ 31.0%`
- `retest_hold`：
  - `mean_net_return ≈ -0.024%`
  - `win_ratio ≈ 45.6%`
  - `invalidation_ratio_12b ≈ 37.1%`

### 3) 这意味着什么

- 这条线最清楚的正面价值：
  - **confirmation / retest 的确能减少“快速被打脸”的概率。**
- 这条线当前还不够强的地方：
  - **减少假信号 ≠ 聚合净收益转正。**
- 因此当前最诚实的定位应是：
  - `reading/` 里的 **confirmation / filter candidate**；
  - 不是 `factors/` 里的 **candidate factor**；
  - 更不是已经成立的 `alpha candidate`。

## 风险 / 边界

- 这轮不是新增实验，而是对连续两轮实验做正式 intake judgment；
- 这个判断是“当前不升级”，不是“永久否决”；
- 如果未来把它并入别的 breakout / pullback 主线当 confirmation layer，它仍可能有价值；
- 但在当前单独拿出来看的证据下，继续升格的性价比已经不高。

## 下一步建议

1. 如果继续以“找更靠谱 alpha”为目标，下一步更应该把资源给：
   - `pytrendline_event_validation_v3` 的 OOS / stability / cross-asset；
   - 或另一个更像 `alpha candidate` 的外部来源；
2. Fibonacci 这条线当前最合理的处置是：
   - 暂留 `reading/`
   - 作为 `confirmation / filter reference`
   - 暂停继续深挖为独立 alpha。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件与 TODO 镜像同步，不做提交。