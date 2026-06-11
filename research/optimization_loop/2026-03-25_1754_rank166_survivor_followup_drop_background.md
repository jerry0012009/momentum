# Rank 166 / BTC 跨所 spread-vol-congestion pocket survivor follow-up

- 时间：2026-03-25 17:54 UTC
- 执行轮次：bot3 auto 13m
- 对象：`Rank 166 / BTC 跨所 spread-vol-congestion pocket`
- 本轮动作：执行其唯一一次 decisive follow-up，只回答“高波动 pocket 下 maker-taker 净 spread 在扣除手续费、滑点缓冲与基础库存约束后，是否仍保留明确的 post-cost 可执行回补边”。

## 结论
**Rank 166：公开材料只足以证明“跨所 quote 裂口会出现 + 可以搭 maker-taker 执行骨架”，但还不足以证明该骨架在目标研究口径（Binance/Coinbase 公共 quote、扣除手续费/滑点缓冲/库存约束后）仍保留明确的 post-cost 可执行回补边，因此这次 survivor follow-up 诚实结束为 `drop_to_background`，不升 `P2`。**

## 这次具体确认了什么
- 论文与 digest 里的核心证据，能支持的是**机会出现条件**：高波动、低同步、链拥堵时跨所 spread 更容易被撑开；它没有直接给出 desk 可迁移的净收益口径。
- README 里的执行仓库虽然给了 `post-only maker + market taker + fill-timeout + max-position` 骨架，但明确写着**不能直接用于生产环境**，而且样例 venue 是 `edgeX / Lighter`，不是本轮要验证的 `Binance / Coinbase` 对。
- 该 README 的阈值参数是绝对价格差（如 `10`），不是已经扣完 fee/slippage 的统一 bps 净边；因此它证明了“有人在打这种结构”，但**没有证明在目标 venue 对上存在稳定可迁移的 post-cost 净边**。
- Binance `bookTicker` 与 Coinbase `ticker` 的公开文档只证明 public top-of-book 数据能拿到，仍不足以回答：
  - maker 腿在高波动 pocket 中的真实成交率是否足够；
  - taker 腿加上 fee/slippage buffer 后剩余净边是否仍显著为正；
  - 现货/永续、USD/USDT、库存预置约束是否会把表面 spread 变成结构性基差噪音。

## 为什么这次不该继续 keep_P1
- policy 对 survivor 只给 **1 次** decisive follow-up 预算；这次已经把唯一 blocker 收口到 post-cost execution realism，并给了诚实答案。
- 当前没有新的 reader-facing 证据能把它从“概念上可做”推进到“明确值得进 admission front”；继续拖只会变成开放式 research，而不是高杠杆验证。
- 因此最合规的收口是：**结束 Rank 166 的 survivor 预算，回到 Background pool，等待未来若出现更直接的 Binance/Coinbase post-cost 证据再由人工明确 reopen。**

## 对 runtime 的直接影响
- `Surviving candidate slot` 应清空为 `none`，因为 Rank 166 的唯一 survivor follow-up 已用完且 verdict 为 `drop_to_background`。
- `Background pool.latest_parked` 更新为 `Rank 166 / BTC 跨所 spread-vol-congestion pocket`。
- 本轮不把它写入 `Active P2 slot`，也不触发 `Paper launch queue`。