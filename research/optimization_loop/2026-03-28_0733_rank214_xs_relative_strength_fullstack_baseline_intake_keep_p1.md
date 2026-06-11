# Rank 214 / XS relative-strength full-stack baseline intake → keep P1

- 时间：2026-03-28 07:33 UTC
- 对象：`research/quant_digests/2026-03-28_0512_xs-relative-strength-fullstack-baseline.md`
- 结论：`keep_P1`
- 新分配 Rank：`214`

## 本轮回答的问题
这条 `XS relative-strength full-stack baseline` 在 repo 已给出负收益结果的前提下，是否仍留下一个足够诚实、可直接承接 `jump-veto / rel-volume / low-sentiment` 增量件的 `XS momentum raw-alpha baseline shell`？

## 最小证据
1. digest 已明确指出该 repo 不是只给信号想法，而是把 `ranking / rebalance / sizing / cost` 一次性写成完整骨架：
   - `72 bar` ranking
   - `24 bar` rebalance
   - long `top 2` / short `bottom 2`
   - `48 bar` realized vol sizing
   - target vol `15%`
   - 单腿上限 `12%`
   - 显式成本 `2bps commission + 1bps slippage`
2. 直接核对外部 repo 文本后，README 与策略代码一致支持这个判断：
   - README 报告 `Cross-Asset Relative Strength` 在 `90 days`、`7` 个 Hyperliquid 币种、`hourly` 数据上的结果为 `-9.52% return / -7.49 Sharpe / 15.94% max DD / 116 trades`
   - `relative_strength.py` 确认它的核心实现就是最朴素的 cross-sectional return ranking + risk-parity sizing，而不是把多个 filter 预先揉成黑箱
3. 这意味着它的最大价值不在“repo 已经证明 alpha 成立”，而在“它把一个可复现、可插拔的 baseline shell 钉住了”，后续可以把我们已在前排验证过有信息量的部件接上去，例如：
   - `short-leg jump veto`
   - short-side single-name weight cap
   - rel-volume / sentiment 作为 quality gate
   - 更合适的 `5m/15m` cadence 和 universe widening

## 为什么不是 promote_P2
- 当前公开结果本身显著为负，不能把它当成已接近 paper trade 的对象。
- 这轮 intake 没有新增 desk 内部回测，只确认了“baseline shell 是否真实存在且足够干净可复用”。
- 因此它值得保留一轮 survivor follow-up，但还不够进入 `P2 admission`。

## 为什么不是直接 drop
- 和很多“只加 filter 不留 baseline”的材料不同，这条对象把 full-stack 策略骨架写得足够明确；这是当前 desk 缺的底座，而不是纯叙述性灵感。
- 它最适合作为承接增量件的 `raw-alpha baseline shell`，研究价值高于其 standalone pnl。

## 本轮正式 verdict
`Rank 214 / XS relative-strength full-stack baseline` fresh intake 首轮 verdict 完成：repo 公开结果虽然显著为负，但它确实提供了一个带排名、换仓、仓位和成本假设的可复现 `XS momentum raw-alpha baseline shell`，足以承接我们当前 desk 的 jump-veto / rel-volume / sentiment 增量件，因此本轮应记为 `keep_P1`，并占用唯一一次 survivor follow-up，而不是直接升 `P2`。
