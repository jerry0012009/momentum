# Rank 201 / UTC clock seasonality intake keep_P1

- 时间：2026-03-27 19:48 UTC
- 对象：`research/quant_digests/2026-03-27_1822_utc-clock-seasonality-alpha.md`
- 结论：`Rank 201 / UTC clock seasonality low-switch schedule` 首轮 intake 完成，正式 verdict = `keep_P1`。

## 为什么不是直接升 P2
这条线的优点很明确：
1. 不是空泛 market-structure 解释，而是可直接写成定时开平仓的 raw alpha family；
2. 当前 digest 已给出 OOS pocket（`long 20~21 UTC / short 22~23 UTC`），而且在受限低切换 family 下 2026 test 有成本后正收益；
3. 标的不是只看 BTC 单资产，而是 8 币等权 perp 组合，方向上比纯单币时钟袋更像可迁移 schedule 母线。

但当前还不够直接升 `P2`，因为首轮证据仍有两个明显边界：
1. 现有 pocket 来自 `1h` 训练/测试后再映射到 `15m` 执行，真正 desk 要跑的 `15m` causal executable version 还没做；
2. 它与已在前排的时钟族对象（尤其 `Rank 200 / BTC weekday-hour sparse short schedule`）同属 clock/schedule 家族，当前 digest 还没证明自己不是“同一家族里另一组 pocket 参数”，而是值得单独占一个 admission 名额的独立母策略。

## 正式系统认知更新
- 这条线**不是**单纯重复论文 headline 的 `tea time` 叙事；真正可保留的是“固定 UTC clock schedule 作为独立 raw alpha 家族”这一层。
- 但本轮更诚实的层级是 `keep_P1`：先保留为 survivor，下一次只做 1 个最便宜但 decisive 的 follow-up，回答“在 `15m` 真执行口径下，它是否仍然独立、稳定、足够区别于已有 weekday/event-clock pocket”。
- 已分配正式 `Rank 201`。

## 对下一次唯一 follow-up 的约束
唯一值得做的 survivor follow-up 应该是：
- 固定当前 pocket（先不要再重搜更多小时窗）；
- 直接做 `15m` executable transfer check；
- 顺带检查它相对 `Rank 200` 的独立性（至少回答是否只是 BTC weekday-hour pocket 的 cross-asset 换壳）。

若该 follow-up 不能证明 `15m` 口径仍存活且具备独立性，就应结束 survivor 预算并移入 background，而不是继续扩写 clock 题材。
