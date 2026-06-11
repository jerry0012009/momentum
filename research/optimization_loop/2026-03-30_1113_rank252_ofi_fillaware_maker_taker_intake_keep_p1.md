# Rank 252 intake — OFI fill-aware maker/taker routing 进入 P1

- 时间：2026-03-30 11:13 UTC
- 对象：Rank 252 / order-flow imbalance × fill-aware maker/taker routing
- 别名：`lagged OFI z-score × cost-aware gating × fill-aware maker/taker split`
- 来源摘要：`research/quant_digests/2026-03-30_0944_ofi-fillaware-maker-taker-alpha.md`
- 本轮动作：fresh intake first verdict，只回答它是否形成独立前排对象
- 本轮结论：`keep_P1`

## 为什么这轮不直接回 background/P0
这条线和当前库里已有的 microstructure 近邻并不等价，至少有 3 个不可省略的新边界：

1. **不是旧 `single-asset OFI + VWAP taker` 的换壳。**
   - `Rank 161` 的主语是 `OFI + depth imbalance + VWAP pressure -> future 3s return`，执行默认是“信号过阈值就立即吃单”的 taker directional alpha。
   - 这次对象的主语更窄也更完整：`lagged OFI z-score -> future 30s drift` 只是第一层；真正新东西是把 `成本门槛 + maker/taker 分流 + fill proxy` 直接写进入场定义。
   - 换句话说，它不是“OFI 有效所以交易”，而是“OFI 只有在净边覆盖 friction 时，才允许被翻译成仓位”。

2. **也不是旧 `Kalman fair-value maker skew` 家族。**
   - `2026-03-25_1411` 那条线的核心是 `fair value drift -> skewed quotes -> markout clean`，本质是 maker-side quote skew raw alpha。
   - 这次对象的判决核心不是 quote skew 本身，而是 **先做 admission，再按 maker_edge 决定 maker 还是 taker**；也就是 directional alpha 和 execution choice 被写成一个联合状态机。

3. **从 raw alpha 到最小可证伪骨架已经够清楚。**
   - 信号：`ofi_z`、`beta_fwd`、`alpha_bps`
   - 成本门槛：`|alpha| >= max(绝对阈值, 成本阈值)`
   - 执行选择：`maker_edge > 0` 才挂 maker，否则走 taker / 放弃
   - 抑制 churn：`cooldown`、`min_hold`、`kill-switch`
   - 公开代理路径也明确：`bookTicker + aggTrades -> L1 OFI / microprice / spread -> 1m/3m proxy`

所以它已经不是“泛 OFI 方向预测”或“generic maker rebate shell”，而是一个独立、可被单轮证伪的前排对象。

## 为什么这轮也不直接升 P2
目前最值钱的是对象边界和研究骨架，不是 repo headline 回测数字。

repo 自带 `IS/OOS` 摘要、csv/json、脚本里的样本区间彼此有口径冲突；这意味着：
- **结构值得留，收益数字不能直接认账；**
- 现阶段更诚实的动作是先给一次 survivor follow-up，而不是把它直接推成 pre-paper admission。

## 单一 decisive blocker（供唯一 survivor follow-up 使用）
只追问一个问题：

> 在公开 `bookTicker + aggTrades` 代理下，把对象压成 `L1 OFI + spread hurdle + sign-flip exit` 的最小公开版后，`1m/3m` 上按 maker/taker 分层，成本后是否还剩稳定正的 executable pocket？

允许的下一步 verdict 只有两个主方向：
- 若成本后仍有稳定 pocket：`promote_P2`
- 若优势主要来自口径幻觉、maker fill 想象或成本后被吃光：`drop_to_background`

## 本轮写回 runtime 的一句话
`Rank 252 / order-flow imbalance × fill-aware maker/taker routing` 不是旧 `single-asset OFI + VWAP taker` 或 `Kalman fair-value maker skew` 的换壳，因为它把 `lagged OFI z-score -> future 30s drift` 与 `成本门槛 + maker/taker 分流 + fill proxy + cooldown/kill-switch` 写成同一套 admission / execution state machine；因此本轮给 `keep_P1`，进入唯一 survivor follow-up。
