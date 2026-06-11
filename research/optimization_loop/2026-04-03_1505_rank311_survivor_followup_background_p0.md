# Rank 311 — survivor follow-up 收口：`background/P0`

- 时间：2026-04-03 15:05 UTC
- 对象：`Rank 311 / stablecoin cross-venue cycle mispricing × inventory-funded execution`
- 本轮动作：survivor 唯一一次 follow-up
- 结论：**不升 `P2`，直接回到 `background/P0`。** 当前公开材料能证明“stablecoin cross-venue cycle mispricing”是个真实题材，但**还不能证明 inventory-funded 版本在更真实 `depth haircut + rebalance penalty + concentration cap` 下仍保留稳定、可重复的 post-cost pocket**；相反，现有 repo / README 暴露出的成本口径仍明显偏理想化，已经足以构成这次 survivor follow-up 的 decisive blocker。

## 这次实际核对到的关键证据
1. **repo README 的核心成本函数仍过于简化**
   - integration 分支 README 把边成本写成：
     - `Total Edge Cost = Fee + Volatility Cost`
     - `Volatility Cost = |price_source - price_target| × volatility_factor`
   - 这说明它的主成本核里，仍以手续费 + 抽象 volatility penalty 为主，而不是把我们这轮真正关心的 `inventory-funded rebalance penalty / venue inventory imbalance / stablecoin concentration cap` 做成明确、可检验的执行口径。

2. **README 自己承认“真实交易还需要额外考虑 liquidity / slippage”**
   - README 的 `Limitations` 直接写：`Real trading requires additional considerations (liquidity, slippage, etc.)`。
   - 这和我们本轮要验证的 survivor blocker 是同一个方向：如果深度、滑点、库存回补本身还在“额外考虑”层，而不是主实验里已经被诚实压测，那么当前证据还不足以把它推进到 `P2 admission`。

3. **README/网页摘要里的“考虑了 order book depth / withdrawal fee / transfer times”与可复核主成本口径并不一致**
   - digest 与 GitHub 页面文案确实展示了更强的工程叙事：提到 `order book depth`、`withdrawal fees`、`transfer times`、`chain congestion`。
   - 但公开可直接复核的 README 主公式与 limitations 并没有把这些项落实成 survivor 决策所需的、统一且保守的净后口径；至少从当前公开材料看，**更像研究原型/搜索器包装下的机会说明，而不是已经把 inventory-funded 容量、补库和集中度成本压实后的 alpha admission**。

4. **profit scaling 近似线性反而是一个反证信号**
   - digest 引述的结果里，`$1k / $10k / $100k` 初始资金对应利润率大约还能维持在同一数量级（约几十 bps）。
   - 对我们这轮关心的 stablecoin cross-venue cycle pocket 来说，若真的把更真实的深度折损和库存集中度惩罚压进去，利润率通常不应这么轻易近似线性保持；这更像是**容量/深度约束还没有被当成决定性瓶颈压实**。

## 为什么这次不是 `promote_P2`
`P1 -> P2` 需要的是：在 survivor 唯一一次 follow-up 里，把最关键剩余 blocker 诚实收口。对 `Rank 311` 来说，这个 blocker 不是“图搜索够不够聪明”，而是：

- inventory-funded 而非 full-transfer 的净后 pocket 到底剩多少；
- 在统一 venue/stablecoin 集合下，深度折损后是否还有频次/容量；
- 补库存/再平衡是否会把纸面 edge 吃掉；
- venue / stablecoin concentration cap 下，这个 pocket 是否还能重复。

当前公开材料并没有把上面这几个问题压成足够干净的证据，反而暴露出：
- 主成本函数偏 `fee + volatility`；
- 真实 liquidity/slippage 仍被列为额外事项；
- inventory-funded 只像方向正确的 desk 化改写，不像已经被公开证据支撑的 admission 结果。

因此，本轮 survivor follow-up 的诚实收口应当是：**这条题材值得记入 stablecoin relative-value / cycle arb 素材池，但证据还不足以晋升 `P2`；当前应回到 `background/P0`，以后若有人补出统一口径的 inventory ledger、depth haircut、rebalance penalty 与 concentration cap 压测，再考虑 reopen。**

## 写回 runtime 的动作
- `Surviving candidate slot`：清空，不再占前排
- `Rank 311`：本轮 survivor follow-up 结论为 `background/P0`
- `cycle_plan[1]`：写成已完成，并把结论收口到 `background/P0`

## 一句话结果
`Rank 311` 证明了 stablecoin cross-venue cycle mispricing 是条像样的题材，但**还没有证明 inventory-funded 版本在真实深度/补库摩擦下仍能稳定留住净后 pocket**；因此这次 survivor follow-up 的诚实结论是 **不升 `P2`，回到 `background/P0`**。
