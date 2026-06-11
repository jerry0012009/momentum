# Rank 203 / graph-matching pairbook mean-reversion intake → keep_P1

- 时间：2026-03-27 22:33 UTC
- 轮次来源：bot3 13 分钟自动执行轮次
- 依据文件：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 执行动作：`research/quant_digests/2026-03-27_1748_graph-matching-pairbook-meanreversion.md` fresh intake
- 正式编号：在扫描现有 rank 后，当前下一个未使用整数为 `Rank 203`
- 结论：`keep_P1`

## 为什么本轮执行的是这条 intake
当前 `cycle_plan` 里第一个仍写成 `pending` 的小点是 `Rank 202` survivor follow-up，但 runtime truth 已经写明：
- `Surviving candidate slot = none`
- `followup_budget_remaining = 0`
- `Rank 202` 已在 `research/optimization_loop/2026-03-27_2224_rank202_survivor_followup_drop_background.md` 诚实收口并退回 `Background pool`

因此继续把 `Rank 202` 当成待执行动作会落到过期歪路径。按 policy 的兜底规则，本轮直接回退到合法前排动作：`graph-matching pairbook mean-reversion` 的 conditional fresh intake。

## 本轮真正改变系统认知的点
这条线保留下来的不是“`full matching` 一定比 overlap baseline 更赚钱”，而是：

> **`cointegration spread mean reversion + pair-book concentration governance` 是一条真实的 raw alpha skeleton；但当前 public `15m` 证据只证明它能把 pair book 做得更分散、更少公共腿，并没有证明它已经形成更好的短周期净收益策略。**

## intake 证据收口
### 1. 值得保留的部分
论文和本地 public-data transfer check 共同证明，matching 这层不是纯包装：
- raw alpha 本体仍然清楚：`cointegration spread mean reversion`
- matching 真正修的是 pair-book 构造错误，而不是凭空捏造 edge
- 本地 `Binance Futures 15m` 最小迁移里，matching 的结构收益是明确存在的：
  - 平均组合集中度：`1.0` vs baseline `3.6`
  - 平均覆盖资产数：`16.0` vs baseline `9.4`
  - 平均 pair turnover changes：`22.85` vs baseline `28.00`

也就是说，这篇 paper 至少已经证明：**对于 pairs/stat-arb，这不是“再包一层 graph 术语”，而是一个可以独立拿出来测的 pair-book governance module。**

### 2. 还不能升 P2 的原因
但当前 public `15m` proxy 也同样清楚地说明，这条线暂时不能被当成可直接升阶的 executable strategy：
- matching gross cumret：`+3.4%`
- baseline gross cumret：`+9.1%`
- matching net cumret：`-6.3%`
- baseline net cumret：`-3.6%`
- matching median half-life：`169` bars
- baseline median half-life：`129` bars

这说明：
1. matching 现在更多是在修 **book concentration / overlap**，不是已经证明更强的短周期 spread alpha；
2. 当前 `15m` 简化 `z-score` 版本里，baseline 选到的 pair 更强、更快；
3. matching 选出的 pair 更慢，可能需要不同的 `holding / scoring / overlap cap`，而不是把 `full matching` 直接硬塞进快周转 desk。

## 正式 verdict
首轮 intake 记为：`Rank 203 / graph-matching pairbook mean-reversion` → `keep_P1`

原因不是“论文很好看”，而是这条线仍然留下了一个明确、低成本、会改变层级判断的 survivor 问题：

> **在更强的 pair admission（`ADF + half-life + liquidity`）之上，把 `full matching` 与 `max-degree<=2` / `capped-overlap` hybrid 放到同一执行框架里，并把持有期拉到 `1h / 4h / 8h` 后，去集中度优势能不能真正转成净 alpha 优势？**

在这个问题回答前，它值得保留为前排唯一 survivor；但在这个问题回答前，它还不配直接升 `P2`。

## 对 state 的写回语义
- `Fresh intake slot`：写成 `Rank 203` 首轮 intake 完成、正式 verdict `keep_P1`
- `Surviving candidate slot`：切换为 `Rank 203`，`followup_budget_remaining = 1`
- `cycle_plan`：把本条 graph-matching intake 写成 `done`

## 一句话 result（用于 cycle_plan / state）
`Rank 203：graph-matching 这条线保留下来的不是“full matching 必胜”，而是“cointegration spread mean reversion + capped-overlap pair-book governance” 这条 raw alpha skeleton；当前 public 15m 证据只证明去集中度，不证明净优势，因此首轮 verdict 记 keep_P1，不升 P2。`
