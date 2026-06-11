# 给 support_breakout_confirm_1 的 h24 补 split-specific excess：OOS 段更像样，但 train 段并不干净

## 为什么这次选这个

这轮继续沿同一条 `pytrendline_event_validation_v3` 主线推进，而且仍然只做一个很小但更诚实的动作。

前两轮已经把 `support_breakout_confirm_1` 缩成了当前 breakout short 的第一顺位对象，并把主评估 horizon 定到了 `h24`。但那时还主要在看 **raw mean return**。这还不够，因为：

- 绝对收益为负，不代表它就比同段市场无条件基线更差；
- 如果要真的说“更像 short alpha / continuation short”，最好至少看一下 **split-specific excess**。

所以这轮最合适的小步，不是再扩 OOS 设计，而是把 `support_breakout_confirm_1 @ h24` 的结论从 raw mean 升级成 **train / validate / test 各自相对同段基线** 的判断。

这轮最值得复用/借鉴的点是：**一个候选在 OOS 段看起来负得更明显，不一定代表它在 train 上也真的是 alpha；把 raw return 和 split-specific excess 分开看，能防止过度吹捧“全段稳定”。**

## 核心结论（中文摘要）

核心结论：**`support_breakout_confirm_1` 的 `h24` 在 validate / test 上确实表现出干净的负 excess，更像 continuation short 候选；但在 train 段它只是“绝对收益为负”，并没有稳定跑赢同段无条件基线，所以当前不能把它吹成“全段稳定 short alpha”。**

证据如何支持这个结论：**在 `h24` 上，`validate / test` 的 `avg_excess_ret` 分别约为 `-1.52% / -0.95%`，而且两段都是 `4/4` 资产同向为负；但 `train` 的 `avg_excess_ret` 约为 `+0.07%`，并且 4 个资产里是 `2 正 / 2 负`，说明 train 段并没有给出同样干净的 relative short edge。**

## 本轮做了什么改动

本轮只做一个主点：**给 `support_breakout_confirm_1 @ h24` 补 split-specific excess。**

具体动作：

1. 继续使用现有样本
   - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`
   - `reports/artifacts/pytrendline_event_validation_v3/cache/*.csv`

2. 沿用当前同一套 `60/20/20` 时间切分
   - `train / validate / test` 仍按全局 `action_timestamp` 顺序切分

3. 为每个 split 重新计算同段 baseline
   - 不是再用全样本 baseline_summary 直接套；
   - 而是对每个 symbol、每个 horizon，在对应 split 内重新算无条件 forward return baseline。

4. 只聚焦当前第一顺位对象
   - `event_type = support_breakout_confirm_1`
   - horizons：`24 / 48 / 72`

5. 产物
   - `reports/artifacts/pytrendline_event_validation_v3_split_excess_v1/baseline_split_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_split_excess_v1/support_breakout_confirm_1_split_excess.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_split_excess_v1/support_breakout_confirm_1_split_excess_by_asset.csv`

6. 更新 `docs/TODO.md`
   - 在 `V3X-E` 的 breakout OOS 进度说明下补入：
     - validate / test 的 `h24` split-excess 确实为负；
     - 但 train 上并不干净，因此表述要更诚实。

## 验证 / 证据

### 1) `h24` split-specific excess

- `train`
  - `event_mean ≈ -1.45%`
  - `avg_excess_ret ≈ +0.07%`
  - `pos_symbols_excess = 2`
  - `neg_symbols_excess = 2`

- `validate`
  - `event_mean ≈ -0.76%`
  - `avg_excess_ret ≈ -1.52%`
  - `pos_symbols_excess = 0`
  - `neg_symbols_excess = 4`

- `test`
  - `event_mean ≈ -0.51%`
  - `avg_excess_ret ≈ -0.95%`
  - `pos_symbols_excess = 0`
  - `neg_symbols_excess = 4`

### 2) 怎么解读

- 如果只看 raw mean，会觉得 `train / validate / test` 三段都支持 short；
- 但一旦换成 split-specific excess，就会发现：
  - **train 只是市场本身也偏弱，这条事件未必额外更差；**
  - **validate / test 才是真正更像“比同段基线更弱”的 continuation short。**

这意味着：
- 当前更合理的表述不是“它在所有阶段都稳定成立”；
- 而是“它在 OOS 段比同段基线更像样，因此值得继续做诚实验证”。

### 3) 额外观察：`h48 / h72`

- `h48`
  - `train avg_excess ≈ -0.82%`
  - `validate avg_excess ≈ -2.71%`
  - `test avg_excess ≈ -1.33%`
  - 但 validate 段资产方向已经松动到 `2 正 / 2 负`

- `h72`
  - `train avg_excess ≈ -1.58%`
  - `validate avg_excess ≈ -0.23%`
  - `test avg_excess ≈ -1.76%`
  - validate 段同样变得不稳

所以当前仍然不改前一轮结论：
- `h24` 仍是最合理的 primary horizon；
- `h48` / `h72` 更适合做 secondary robustness check。

## 风险 / 边界

- 这轮依然没有新增 event generation；
- 只是把同一套 split-honesty 从 raw mean 提升到 split-specific baseline/excess；
- 样本依然小，所以当前结论仍应理解为“更诚实的中间判断”，不是最终 alpha verdict。

## 下一步建议

1. 如果下一步进入正式 OOS，最该问的问题现在更清楚了：
   - `support_breakout_confirm_1` 在 `h24` 上，是否能持续跑输同段无条件基线？
2. 当前不建议把“train 也为负”误解成“train 也有稳定 excess”；
3. 这条线值得继续，但措辞要收紧为：
   - **OOS 段更像样的 continuation short 候选**
   - 不是“全段稳定 short alpha”

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件、artifact 落盘与 TODO 镜像同步，不做提交。