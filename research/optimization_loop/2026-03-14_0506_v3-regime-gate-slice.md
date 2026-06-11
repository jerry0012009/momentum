# 给 support_breakout_raw 补一刀 regime-gate 切片：简单 EMA 趋势过滤没有支持“只在 downtrend 做空”

## 为什么这次选这个

上一轮已经对 `support_breakout_raw` 做了最小 `volume confirmation` 切片，结果是：
- 直觉上很合理的放量过滤，当前并没有带来更诚实的 OOS 增量；
- 反而显著压缩了可用样本。

既然刚刚又把 `Naganjaneyulu et al. (2023)` 那条 regime-switch 线补成了正式来源卡，这轮最自然的一小步，就是把它也拉回当前主线做一个**最小本地验证**：

- 不重跑 pytrendline；
- 不改事件生成代码；
- 只用现成 `event_sample_purged.csv` + cache K 线；
- 看 `support_breakout_raw` 在最简单的 `EMA50/EMA200 + slope` regime 切分下，是否真的更适合“只在 downtrend 做空”。

这轮最值得复用/借鉴的点是：**外部论文里“先分趋势再交易”的原则是合理的，但具体到本地 15m support-breakout short，上来就套“只在 downtrend 做空”这种朴素直觉，可能并不成立。**

## 核心结论（中文摘要）

核心结论：**在当前 `pytrendline_event_validation_v3` 的 45d / 60m 样本里，最简单的 `EMA50/EMA200 + slope` regime gate 并没有支持“support_breakout_raw 只该在 downtrend 做空”这个直觉；相反，OOS 段里 `uptrend` 标记下的 support-break 反而更负，而 `fluctuating` 才更像最该回避的那档。**

证据如何支持这个结论：**按 confirm-time `EMA50 > EMA200` 且 `EMA50` 24-bar slope > 0 记为 `uptrend`、反之 `<0` 记为 `downtrend`，在 validate+test 的 `h24` 上，`uptrend` 的 `oos_avg_excess_ret` 约为 `-2.24%`（`4/4` 资产负 excess），`downtrend` 约为 `-1.73%`（同样 `4/4` 资产负 excess），而 `fluctuating` 则转成了正 excess（约 `+1.38%`，但样本很小）。这说明当前更合理的读法不是“简单趋势过滤已经证实”，而是“简单 EMA regime gate 可能更适合帮我们回避震荡段，但还不能把 breakout short 机械地限死在 downtrend。”**

## 本轮做了什么改动

本轮只做一个主点：**对 `support_breakout_raw` 补一刀 regime-gate 小切片。**

具体动作：

1. 使用现有 artifacts，不重跑主报告
   - 输入：
     - `reports/artifacts/pytrendline_event_validation_v3/event_sample_purged.csv`
     - `reports/artifacts/pytrendline_event_validation_v3/cache/*.csv`

2. 固定对象与口径
   - 对象：`support_breakout_raw`
   - horizon：`h24`
   - split：沿用当前全局 `60/20/20` 的 `train / validate / test`
   - regime 规则（最小 proxy）：
     - `uptrend`：confirm-time `EMA50 > EMA200` 且 `EMA50 - EMA50[t-24] > 0`
     - `downtrend`：confirm-time `EMA50 < EMA200` 且 `EMA50 - EMA50[t-24] < 0`
     - `fluctuating`：其余

3. 只做现成样本的 regime 切分
   - 不新增事件生成；
   - 只在已有事件上打 regime 标签，并计算 split-specific excess。

4. 产物
   - `reports/artifacts/pytrendline_event_validation_v3_regime_slice_v1/support_breakout_raw_regime_summary.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_regime_slice_v1/support_breakout_raw_regime_by_asset.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_regime_slice_v1/support_breakout_raw_regime_oos.csv`
   - `reports/artifacts/pytrendline_event_validation_v3_regime_slice_v1/summary.json`

5. 更新 `docs/TODO.md`
   - 在 `V3X-E` breakout family OOS 进度下补充：
     - 简单 regime gate 没有支持“only short in downtrend”；
     - 但它可能提示：`fluctuating` 才是当前更该回避的环境。

## 验证 / 证据

### 1) OOS 汇总（validate + test, h24）

- `uptrend`
  - `oos_events = 9`
  - `oos_mean_ret_h24 ≈ -1.53%`
  - `oos_avg_excess_ret_h24 ≈ -2.24%`
  - `4/4` 资产负 excess

- `downtrend`
  - `oos_events = 7`
  - `oos_mean_ret_h24 ≈ -1.29%`
  - `oos_avg_excess_ret_h24 ≈ -1.73%`
  - `4/4` 资产负 excess

- `fluctuating`
  - `oos_events = 3`
  - `oos_mean_ret_h24 ≈ +1.02%`
  - `oos_avg_excess_ret_h24 ≈ +1.38%`
  - 方向混杂，且样本很小

### 2) split 视角

- `uptrend / validate`
  - `events = 5`
  - `avg_excess_ret_h24 ≈ -2.17%`
- `uptrend / test`
  - `events = 4`
  - `avg_excess_ret_h24 ≈ -2.33%`

说明 `uptrend` 这档在 validate / test 里都保持了相对干净的负 excess。

- `downtrend / validate`
  - `events = 3`
  - `avg_excess_ret_h24 ≈ -3.89%`
- `downtrend / test`
  - `events = 4`
  - `avg_excess_ret_h24 ≈ -0.29%`

说明 `downtrend` 不是没用，但它在 test 段明显变弱，不像“只要 downtrend 就稳定好用”。

- `fluctuating / validate`
  - `events = 3`
  - `avg_excess_ret_h24 ≈ +1.38%`
- `fluctuating / test`
  - `events = 0`

这至少给了一个很明确的 warning：
- 当前最简单 regime 切分下，**震荡段更像是该警惕的环境**。

## 怎么解读

最诚实的读法不是“regime gate 没用”，而是：

1. **简单 EMA 趋势过滤没有支持“support-breakout short 只能在 downtrend 做”；**
2. 相反，它提示：
   - `uptrend` 里的 support-break 也可能是有价值的（更像结构性失守 / reversal continuation）；
   - `fluctuating` 反而更像噪声环境；
3. 所以如果后续要继续做 regime gate，更合理的问题应该是：
   - **是否该优先回避 `fluctuating`，而不是机械地只做 `downtrend`。**

## 风险 / 边界

- 这轮 regime 定义是一个非常粗的 proxy；
- `EMA50/EMA200 + 24-bar slope` 只是为了做 first-pass honesty，不代表最佳状态识别器；
- 样本仍然偏小，尤其 `fluctuating` 的 OOS 只有 `3` 条；
- 所以这轮更像在否定一个过于简单的直觉，而不是在给最终 regime 规则定版。

## 下一步建议

如果后续继续沿这条线往下走，最有价值的不是继续调 EMA 参数，而是：

1. 把 regime gate 的问题改写成：
   - `trade all` vs `avoid fluctuating` vs `only downtrend`
2. 或者把 regime gate 和已有 confirmation layer 组合：
   - `support_breakout_raw + avoid fluctuating`
   - `support_breakout_confirm_1 + avoid fluctuating`
3. 重点看：
   - `false_break_ratio`
   - `post_cost_return`
   - `excess_ret`
   - `sample retention`

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成 artifact、TODO、日志与邮件同步，不做提交。