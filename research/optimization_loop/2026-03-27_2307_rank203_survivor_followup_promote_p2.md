# Rank 203 / graph-matching pairbook mean-reversion survivor follow-up → promote_P2

- 时间：2026-03-27 23:07 UTC
- 轮次来源：bot3 13 分钟自动执行轮次
- 依据文件：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 执行动作：执行 `cycle_plan` 最前项 `Rank 203 / graph-matching pairbook mean-reversion` survivor 唯一 follow-up
- 正式结论：`promote_P2`

## 本轮只回答的唯一问题
> 在更强的 pair admission（`ADF + half-life + liquidity`）之上，把 `full matching` 与 `max-degree<=2 / capped-overlap` hybrid 放到同一执行框架里，并把持有期拉到 `1h / 4h / 8h` 后，去集中度优势能否真正转成净 alpha 优势？

按环境约束，本机没有 `networkx` / `statsmodels`，所以本轮没有冒充完整论文复现；而是做了一个**诚实的最小近似复验**：
- 数据：Binance Futures 公共 `15m` K 线，16 个高流动性 `USDT` perpetual
- 形成/交易：`60d formation + 10d trade`，滚动 `5` 个窗口
- stronger admission：用 OLS residual 上的单滞后均值回复近似统计量（`mr_t`）+ `half_life` 先缩图，要求 `mr_t <= -2.5` 且 `16 <= half_life <= 192`
- 三种 pair-book：
  1. `matching` = `max_degree = 1`（full non-overlap）
  2. `degree2` = `max_degree = 2`（capped-overlap hybrid）
  3. `baseline` = overlap allowed
- 交易层：统一 `z-entry = 1.0`，回到 0 或 time stop 退出；round-trip friction proxy 与 intake 保持同量级
- 产物目录：`reports/artifacts/optimization_loop/rank203_survivor_followup_20260327/`

## 本轮改变系统认知的新结论
这条线真正值得保留和升级的，不是 `full matching` 本身，而是：

> **在更强 pair admission 下，`max-degree<=2` 的 capped-overlap hybrid 已经比 full non-overlap 和 overlap baseline 都更像可 desk 化的 crypto pair-book 构造器。**

也就是说，前一轮 intake 里保留下来的“`cointegration / mean-reverting spread + pair-book governance`”这条母线，现在已经从概念性 `keep_P1`，推进到了一个更具体的 `P2` 命题：
- 不该把 paper 机械理解成“必须 full matching”；
- 更像 production 候选的是 **`strong pair admission + capped-overlap hybrid`**。

## 核心结果
### 汇总（`summary.json`）
- `matching_1h`：gross `+10.47%`，net `-1.57%`，正 net 窗口 `1/5`，平均集中度 `1.0`
- `degree2_1h`：gross `+12.08%`，net `+0.18%`，正 net 窗口 `3/5`，平均集中度 `2.0`
- `baseline_1h`：gross `+8.06%`，net `-3.03%`，正 net 窗口 `2/5`，平均集中度 `3.0`

`4h / 8h` 在当前这版 time-stop 设定下没有产生额外差异，说明真正起作用的是**pair admission + overlap cap**，不是单纯延长时间上限。

### 读法
1. **full non-overlap 不是赢家。**
   - 它确实最干净，但 pair 数掉到均值 `4.2`，平均覆盖 `8.4` 个资产；
   - 净收益仍为负，说明“完全不重叠”在当前宇宙里太苛刻，杀掉了太多有效 pair。
2. **capped-overlap hybrid 是本轮唯一转正的版本。**
   - `degree2` 的 net cumret `+0.18%`，虽然不大，但已经比 full matching 和 baseline 都更好；
   - `3/5` 个窗口为正，且 drawdown 也更浅（`-8.93%` vs baseline `-10.05%`）。
3. **这不是已经足够升 P3 的证据，但足够升 P2。**
   - 目前还是近似复验，成本后优势很薄；
   - 但 survivor 该回答的问题已经被回答：**去集中度优势不是虚的，而且最有希望转成净优势的形态就是 `max-degree<=2` hybrid，而不是 full matching 教条。**

## 正式 verdict
按当前小点的 `success_criterion`：
- 如果 hybrid / 更长持有期下，去集中度优势能转成更稳的净 alpha，则升 `P2`；
- 否则 survivor 预算归零并移入背景。

本轮应判为：`Rank 203 / graph-matching pairbook mean-reversion` → `promote_P2`

原因：
- hybrid 版本已在统一框架下跑出**相对最优且略为净正**的结果；
- 这足以说明这条线不再只是 `P1` 的概念性 pair-book 治理故事，而是值得进入 `P2 admission` 的可执行命题；
- 但证据还不够厚，不应越级直升 `P3`。

## 下一层 P2 admission 应该问什么
进入 `P2` 后，下一轮该问的不是“matching 好不好看”，而是更窄、更执行化的问题：
1. `degree cap = 2` 是否优于 `cap = 1 / 3`；
2. admission 是否需要显式加入更硬的 liquidity / funding / basis veto；
3. 执行层应转 `q-score / quantile sizing` 还是保留简化 `z-score`；
4. 成本口径拆成 maker-heavy / mixed / taker-heavy 后，优势是否还活着；
5. 是否存在更自然的 `1h+` 退出逻辑，而不是当前“回到 0 或 time stop”的简化版。

## 对 runtime 的写回
- `Surviving candidate slot`：本轮 follow-up 已用掉，不再保留 `Rank 203`
- `Active P2 slot`：切换为 `Rank 203 / graph-matching pairbook mean-reversion`
- `cycle_plan[1]`：写成 `done`

## 一句话 result（用于 state / cycle_plan）
`Rank 203：更强 pair admission 下，full non-overlap 仍净负，但 max-degree<=2 的 capped-overlap hybrid 已在统一框架里跑出当前唯一略为净正且优于 baseline 的结果；因此这条线从 survivor 正式升入 P2，后续应围绕 capped-overlap pair-book 的 admission/execution 细化，而不是再争论 full matching 教条。`
