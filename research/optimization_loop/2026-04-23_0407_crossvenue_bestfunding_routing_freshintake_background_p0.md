# cross-exchange best-funding routing × sign-constrained delta-neutral carry × hysteresis hold — fresh intake first verdict

- 时间：2026-04-23 04:07 UTC
- 对象：`research/quant_digests/2026-04-23_0315_crossvenue-bestfunding-routing-shell.md`
- 轮次角色：bot3
- 结论：`background/P0`

## 本轮只补的最小 decisive blocker
检查这条 `cross-exchange best-funding routing` 是否真的留下了一个可独立排队的新 after-cost carry pocket，还是只是把单 venue funding carry 的薄边用更激进的执行假设重新包装。

## 关键发现
1. repo 的核心 uplift 确实来自 `strategy_cross.py` 里的 `best_fr = max(...)` 路由，但它的可交易性前提并没有闭合成 desk 可直接承接的现实壳。
2. `strategy_cross.py` 明确把策略写成 `LONG spot (Binance) + SHORT perp (best exchange)`，而在代码注释里又直接承认 **`shorting spot is out of scope`**；但同一套回测逻辑仍允许在 `best_fr < 0` 时做 `LONG perp + SHORT spot` 的“bidirectional”腿。
3. 这意味着 repo 对最关键的 bear / backwardation 一侧，并没有把 `short spot borrow / locate / inventory / venue transfer` 成本与可执行性真正计入；而 notebook 文案又把 `2022 bear` 的稳健性归因给这条 **bidirectional design**。也就是说，最像“把单 venue 负 carry 也变成可做”的那部分收益，仍建立在未闭合的 short-spot realism 上。
4. 另一条未闭合前提是：spot hedge 固定放在 Binance，而 perp 腿在 Binance / Gate / Hyperliquid 间切换；repo把它当作 `best funding routing` 的净 uplift，但没有把跨 venue 资金占用、仓位迁移、资金预置/再平衡与切换摩擦写成真实 ledger。对 short-cycle desk 来说，这不是小修小补，而是决定 routing alpha 是否仍高于成本线的核心现实约束。

## 为什么这一步直接收口为 background/P0
- 这条线的“新意”不是 funding carry 本身，而是 `best venue routing`。
- 但当前可见证据没有诚实证明：在 **不依赖未定价 short-spot 腿**、且把 **跨 venue routing friction / capital parking / switch realism** 算进去以后，仍存在一个非单 venue、非单币 lucky-run 的独立 after-cost pocket。
- 因此它现在更像两类东西：
  1. 对已有 carry 家族的组件提示：`best-funding router / sticky routing / min-hold / hysteresis`；
  2. 对未来真正可落地 carry runner 的 execution note：不要把单 venue carry 幻觉直接当可交易 alpha。
- 它还没有通过“可独立排队的新 raw alpha”这道门槛，所以本轮不保留 survivor，直接收口 `background/P0`。

## 最终 verdict
`cross-exchange best-funding routing × sign-constrained delta-neutral carry × hysteresis hold` 的 fresh intake first verdict 已诚实收口 `background/P0`：repo 的净 uplift 主要建立在 `best funding` 路由叙事上，但其 bidirectional 回测仍把 `short spot` 一侧留在 out-of-scope/未计 borrow 的执行空洞里，同时也没把跨 venue 资金预置、切换与再平衡摩擦闭合成真实 ledger；因此当前没有证明存在一个在 routing realism 后仍独立成立的 after-cost carry pocket，它更适合作为 carry family 的 router / hold 设计提示，而不是新的前排对象。
