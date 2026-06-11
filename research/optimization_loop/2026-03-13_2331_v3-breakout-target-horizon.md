# 把 breakout short 的主评估 horizon 定死：先盯 h24，h48 只做次级复核，h72 暂不做主结论

## 为什么这次选这个

这轮继续沿同一条 `pytrendline_event_validation_v3` 的 breakout short OOS 线程推进，而且仍然只做一个很小的动作。

前两轮已经解决了两个问题：
1. breakout short 比 rebound long 更值得先做 OOS；
2. breakout short 内部，`support_breakout_confirm_1` 比 `raw / confirm_2` 更适合当第一顺位对象；
3. 这条线不是 `h6` 立刻下跌，而更像 `h24+` continuation short。

但还有最后一个容易模糊的点：**在 `h24 / h48 / h72` 里，后续正式 OOS 到底应该把哪一个 horizon 当主评估指标？**

如果这点不先写死，后面很容易因为 `h72` 看起来跌得更大，就误把更远的 horizon 当主结果；但那可能只是更不稳定的尾部展开，而不是最诚实的主结论层。

这轮最值得复用/借鉴的点是：**一个候选即使在更长 horizon 看起来跌得更多，也不代表它就更适合作为主评估档；主评估 horizon 应优先选“跨 split 更稳定”的那一档。**

## 核心结论（中文摘要）

核心结论：**对当前 `support_breakout_confirm_1` 而言，后续正式 OOS 的主评估档应优先锁定 `h24`；`h48` 只做次级复核，`h72` 暂不应作为主结论档。**

证据如何支持这个结论：**`support_breakout_confirm_1` 在 `h24` 的 `train / validate / test` 三段均值都为负（约 `-1.45% / -0.76% / -0.51%`），而且 split 内方向最稳定；`h48` 虽然三段均值也都为负（约 `-3.76% / -0.50% / -0.59%`），但 validate 段按资产已出现 `2/4` 翻正；`h72` 则在 validate 段直接转成明显正值（约 `+3.10%`），说明它更像不稳定尾部 horizon，而不是当前最诚实的主结论层。**

## 本轮做了什么改动

本轮只做一个主点：**给 `support_breakout_confirm_1` 定主评估 horizon。**

具体动作：

1. 继续使用同一份现有样本
   - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`
   - 全局 `60/20/20` 时间切分

2. 只看 `support_breakout_confirm_1`
   - 比较 `h6 / h24 / h48 / h72` 在 `train / validate / test` 三段的表现

3. 产物
   - `reports/artifacts/pytrendline_event_validation_v3_horizon_target_v1/support_breakout_confirm_1_split_by_horizon.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_horizon_target_v1/summary.json`

4. 更新 `docs/TODO.md`
   - 在 `V3X-E` 的 breakout family OOS 进度说明中补入：
     - `h24` = primary horizon
     - `h48` = secondary check
     - `h72` = not primary for now
   - 并同步重建 `plans/momentum_todo.html`

## 验证 / 证据

### 1) `h24`
- `train ≈ -1.45%`
- `validate ≈ -0.76%`
- `test ≈ -0.51%`
- 三段均值全负，且 split 内方向最稳

### 2) `h48`
- `train ≈ -3.76%`
- `validate ≈ -0.50%`
- `test ≈ -0.59%`
- 虽然三段均值也都为负，但 validate 段按资产已经出现明显松动

### 3) `h72`
- `train ≈ -5.72%`
- `validate ≈ +3.10%`
- `test ≈ -1.42%`
- validate 直接翻正，说明它当前更像不稳定尾部 horizon

### 4) 怎么解读

- 如果只看“跌得够不够大”，可能会被 `h72` 吸引；
- 但如果看“哪一档最适合当诚实主结论”，`h24` 明显更合理；
- 当前更稳的研究口径应是：
  - 先回答 `support_breakout_confirm_1` 在 `h24` 是否真的有 continuation short 优势；
  - 再把 `h48` 当次级复核；
  - 暂时不要把 `h72` 当主 KPI。

## 风险 / 边界

- 这轮没有新增事件或新增回测，只是基于现有 split summary 做 target-horizon 定义；
- 样本依然偏小，尤其 validate / test 段事件数不多；
- 所以这轮结论是“后续 OOS 的主问题该怎么问”，不是最终 alpha verdict。

## 下一步建议

1. 后续正式 OOS 应优先围绕这个问题展开：
   - `support_breakout_confirm_1` 在 `h24` 上是否仍保有诚实、可复现的 continuation short 优势？
2. `h48` 可作为 secondary robustness check；
3. `h72` 目前不建议作为 headline metric。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件、artifact 落盘与 TODO 镜像同步，不做提交。