# Rank 226 / IV quantile confirmation / veto shared gate：fresh intake keep_P1

- 时间：2026-03-28 16:48 UTC
- 对象：`research/quant_digests/2026-03-28_1433_iv-quantile-confirmation-gate.md`
- 轮次类型：bot3 auto optimization
- 结论：`keep_P1`
- Rank：`226`

## 这轮做了什么
按当前 `cycle_plan` 执行这条 fresh intake，回答它究竟只是给已有方向信号补一层 IV 确认话术，还是能诚实形成跨 BTC/ETH、面向 `5m/15m` continuation / fade 的 shared gate，并明确它不是冒充独立 raw-alpha 的 filter 包装。

## 本轮判断
结论是 **`keep_P1`**，但不直接升 `P2`。

原因分三层：
1. **它更像共享 gate，而不是独立 raw alpha。** 这条 intake 自己已经把边界写清：核心不是“IV 单独预测方向”，而是把 `IV quantile × IV change` 作为已有 `breakout/continuation` 与 `shock-fade` 的 admission / veto 层。这个定位是诚实的，也和论文里“高频下 IV 响应在各波动分位都显著、但价值更集中在较高 IV 分位与较慢一点的 intraday 频率”一致。
2. **它具备可独立复现的最小实验骨架，而且有跨资产共享潜力。** 数据侧可以用 Deribit 公共 IV / ATM IV proxy，执行侧可以走 BTC/ETH perp；主口径聚焦 `5m/15m`，而不是把 `1m/3m` micro-noise 当发现。作为共享组件，它至少天然服务两类现成基线：`continuation admit` 与 `fade admit / veto`。
3. **但当前证据仍停留在 paper-to-desk spec 层，没有证明它对任一现成 baseline 留下 after-cost 独立净增益。** 这轮没有 recent/live A/B 去回答：
   - `iv_q × ivchg` 对 `5m/15m breakout` 是否真的提高 markout / hit rate；
   - 它在 BTC 与 ETH 上是否都成立，而不是单币叙事；
   - 它对 `fade` 的帮助是否来自真实非确认信息，而不是把 trade 数量简单砍少；
   - 跨 Deribit IV 与 perp 执行的时钟错位、成本、采样平滑后，净收益是否还保留。

所以它值得保留在前排做唯一一次 survivor follow-up，但还不够进入 `P2 admission`。

## 会改变系统认知的话
`Rank 226 / IV quantile confirmation / veto` 不是新的独立 raw alpha，而是一条具备跨 BTC/ETH 复用潜力的 `5m/15m` shared admission-veto gate；但当前只有论文级与 desk-spec 级证据，尚未证明它能对任一现成 continuation / fade baseline 留下 after-cost 独立净增益，因此本轮只够 `keep_P1`，不直接升 `P2`。

## 为什么不是 promote_P2
`P2` 需要的是“已经看到值得做 admission 的最小实证”，不是“这个 filter 结构听起来合理”。这条线目前最缺的不是更多论文解释，而是最小 live/recent 对照：
- 选一条现成 `5m/15m breakout/continuation` baseline；
- 选一条现成 `5m/15m shock-fade` baseline；
- 在同一成本口径下比较 `baseline` vs `baseline + iv gate`；
- 输出 trade count、净均值、markout、tail loss、BTC/ETH 平行结果。

在这一步之前，把它直接送进 `P2`，会把“可复现 shared filter”误当成“已被证明会显著改善策略 admission 的组件”。

## 唯一合法下一步（survivor）
若给它唯一一次 survivor follow-up，应该只做一件事：
- 对一条现成 `5m/15m continuation` baseline 和一条现成 `5m/15m fade` baseline，各做一次同口径 A/B：
  1. `baseline`
  2. `baseline + iv_q gate`
  3. `baseline + iv_q + ivchg confirmation/non-confirmation`
- 输出 BTC/ETH 双资产的触发次数、成本后均值、`1/3/6 bar` markout、tail loss 与 veto 后 turnover 变化。

如果这一步不能证明它对至少一类 baseline 留下稳定独立净增益，它就应按预算做 `keep_P1 后转 background` 收口，而不是继续停留在“IV 很适合做 filter”的主题层。