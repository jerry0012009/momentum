# 把 regime gate 压成可执行 policy：当前更像样的是 avoid_fluctuating，不是 only_downtrend

## 为什么这次选这个

上一轮已经把 `support_breakout_raw` 的简单 regime 切分跑出来了，得到一个很关键但还不够“可执行”的结论：
- 简单 `EMA50/EMA200 + slope` 并没有支持“只在 downtrend 做 support-breakout short”；
- `fluctuating` 反而更像该回避的环境。

但这还不够。因为研究上知道“可能要避开震荡段”，和工程上知道“到底该怎么设默认规则”，是两回事。

所以这轮最值得做的一小步，不是继续调更多 regime 参数，而是把问题直接压成**最小 policy 对照**：
- `trade_all`
- `avoid_fluctuating`
- `only_downtrend`
- （顺手保留 `only_uptrend` 作为参考，不作为主结论）

这轮最值得复用/借鉴的点是：**当一个过滤层看起来“有点道理”时，最先要比较的不是更多参数，而是它到底能不能在保留足够样本的同时，让 OOS 结果更诚实。**

## 核心结论（中文摘要）

核心结论：**对当前 `support_breakout_raw @ h24` 而言，simple regime gate 的 first-pass 默认口径更像是 `avoid_fluctuating`，而不是 `only_downtrend`。**

证据如何支持这个结论：**在 OOS 段（validate+test），`trade_all` 的 `avg_excess_ret_h24` 约为 `-1.55%`；改成 `avoid_fluctuating` 后提升到约 `-1.88%`，同时仍保留约 `84%` 样本；而 `only_downtrend` 虽然也保持负 excess（约 `-1.73%`），但样本只剩约 `37%`，性价比明显不如 `avoid_fluctuating`。`only_uptrend` 数字最亮（约 `-2.24%`），但只保留约 `47%` 样本，更像观察项而不是当前该默认启用的硬过滤器。**

## 本轮做了什么改动

本轮只做一个主点：**把 regime gate 从“研究口径”压成“可执行 policy 对照”。**

具体动作：

1. 延续上一轮同一套 regime proxy
   - confirm-time `EMA50 > EMA200` 且 `EMA50` 24-bar slope > 0 → `uptrend`
   - confirm-time `EMA50 < EMA200` 且 `EMA50` 24-bar slope < 0 → `downtrend`
   - 其余 → `fluctuating`

2. 固定对象与 horizon
   - 对象：`support_breakout_raw`
   - horizon：`h24`
   - split：沿用当前全局 `60/20/20`

3. 比较 4 个 policy
   - `trade_all`
   - `avoid_fluctuating`
   - `only_downtrend`
   - `only_uptrend`（只作参考）

4. 产物
   - `reports/artifacts/pytrendline_event_validation_v3_regime_policy_slice_v1/support_breakout_raw_regime_policy_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_regime_policy_slice_v1/support_breakout_raw_regime_policy_by_asset.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_regime_policy_slice_v1/support_breakout_raw_regime_policy_oos.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_regime_policy_slice_v1/summary.json`

5. 更新 `docs/TODO.md`
   - 在 `V3X-E` 下补入：
     - 当前最像样的 first-pass policy 是 `avoid_fluctuating`；
     - `only_downtrend` 不应被默认化；
     - `only_uptrend` 先保留为观察项。

## 验证 / 证据

### 1) OOS policy compare（validate + test, h24）

- `trade_all`
  - `oos_events = 19`
  - `oos_retention_vs_all = 100%`
  - `oos_avg_excess_ret_h24 ≈ -1.55%`
  - `4/4` 资产负 excess

- `avoid_fluctuating`
  - `oos_events = 16`
  - `oos_retention_vs_all ≈ 84%`
  - `oos_avg_excess_ret_h24 ≈ -1.88%`
  - `4/4` 资产负 excess

- `only_downtrend`
  - `oos_events = 7`
  - `oos_retention_vs_all ≈ 37%`
  - `oos_avg_excess_ret_h24 ≈ -1.73%`
  - `4/4` 资产负 excess

- `only_uptrend`
  - `oos_events = 9`
  - `oos_retention_vs_all ≈ 47%`
  - `oos_avg_excess_ret_h24 ≈ -2.24%`
  - `4/4` 资产负 excess

### 2) 怎么解读

先看最重要的工程问题：
**过滤器有没有在“少丢样本”的前提下，把 OOS 结果变得更诚实？**

答案是：
- `avoid_fluctuating`：**有一点，而且代价不大**；
- `only_downtrend`：**没有更值，反而丢太多样本**；
- `only_uptrend`：**数值好看，但样本保留率已经太激进**。

### 3) 为什么 `avoid_fluctuating` 更像当前默认口径

因为它是三者里最平衡的：
- 比 `trade_all` 更干净；
- 不像 `only_downtrend` 那样把样本砍掉太多；
- 也不像 `only_uptrend` 那样过于依赖一档小样本状态。

换成人话：
**现在更像是在说“别在震荡里做这条线”，而不是“这条线只能在下跌趋势里做”。**

### 4) split 视角补充

- `avoid_fluctuating / validate`
  - `events = 8`
  - `avg_excess_ret_h24 ≈ -2.75%`
- `avoid_fluctuating / test`
  - `events = 8`
  - `avg_excess_ret_h24 ≈ -1.31%`

- `only_downtrend / validate`
  - `events = 3`
  - `avg_excess_ret_h24 ≈ -3.89%`
- `only_downtrend / test`
  - `events = 4`
  - `avg_excess_ret_h24 ≈ -0.29%`

这说明 `only_downtrend` 的问题不在 validate，而在 test 段明显发虚。

## 风险 / 边界

- 这轮 regime 定义仍然是很粗的 first-pass proxy；
- `only_uptrend` 虽然数值最亮，但不能因为更负就直接上默认规则；
- 当前更像是完成了一个 **policy triage**：
  - 先排除 `only_downtrend` 这个朴素默认；
  - 暂时保留 `avoid_fluctuating` 作为更值得继续验证的候选口径。

## 下一步建议

如果后续继续沿这条线往下走，最有价值的不是再调 EMA 参数，而是：

1. 把 `avoid_fluctuating` 和已有 confirmation layer 组合：
   - `support_breakout_raw + avoid_fluctuating`
   - `support_breakout_confirm_1 + avoid_fluctuating`
2. 比较它们相对 `trade_all` 的：
   - `post_cost_return`
   - `avg_excess_ret`
   - `sample retention`
   - `false_break_ratio`
3. 当前暂不建议把 `only_downtrend` 写成默认规则。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成 artifact、TODO、日志与邮件同步，不做提交。