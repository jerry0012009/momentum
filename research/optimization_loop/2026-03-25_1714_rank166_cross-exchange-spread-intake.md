# Rank 166 / BTC 跨所 spread-vol-congestion pocket fresh intake 首判

- 时间：2026-03-25 17:14 UTC
- 执行轮次：bot3 auto 13m
- 对象：`research/quant_digests/2026-03-25_1705_btc-cross-exchange-spread-vol-congestion-pocket.md`
- 本轮动作：只做 fresh intake 最小首判（`park` vs `keep_P1`）

## 结论
**Rank 166：BTC 跨所可执行 spread 在高波动 × 低同步 pocket 下的收敛 raw alpha 首判通过，记为 `keep_P1`，因为它已经具备清晰可复现的 signal/execution 骨架与公开 quote 数据入口，但真钱可转移性仍取决于下一步 maker-taker post-cost 回补验证。**

## 为什么不是直接 park
- 这不是泛泛“看见价差就打”的老故事，而是**明确限定到同币种跨 venue 可执行 spread 收敛**的独立 raw alpha。
- digest 已经把策略骨架写到可执行层：`maker 一腿 + taker 一腿 + fill-timeout + inventory cap + post-cost spread threshold`，不是只有解释没有交易闭环。
- 数据入口是公开且低摩擦的：Binance `bookTicker` 与 Coinbase websocket `best_bid/best_ask` 足够先做纯 quote 版 honesty check。
- regime 也不是空话：高波动 / 低同步 pocket 给了明确的分层假设，后续可以直接用 `15m realized vol × spread` 先做最小 desk transfer。

## 为什么还不能升 P2
- 论文与 digest 目前证明的是“机会会出现”，还没证明**扣掉双边成本、maker 成交不确定性与库存约束后**还能稳定留下净边。
- 现货 vs perp、不同 venue fee/rebate、maker adverse selection 都可能把表面 spread 变成不可赚噪音。
- 所以下一步唯一高杠杆 blocker 很明确：先验证 **高波动 pocket 下 maker-taker 可执行净 spread 是否存在可回补的 post-cost 边**。

## 对 runtime 的直接影响
- 该对象获得正式身份 `Rank 166`。
- 本轮只完成 fresh intake 首判，不顺手执行 survivor follow-up。
- 下一轮若 bot2/bot3继续推进，合法动作应是把 `Rank 166` 写入 `Surviving candidate slot`，并仅做一次最小 desk-transfer blocker 检查。
