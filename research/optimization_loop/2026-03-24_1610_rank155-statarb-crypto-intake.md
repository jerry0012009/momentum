# Rank 155 / Jamestilfords/statarb-crypto fresh intake

- Time: 2026-03-24 16:10 UTC
- Slot: Fresh intake
- Rank: 155
- Target: `Jamestilfords/statarb-crypto`
- Source: <https://github.com/Jamestilfords/statarb-crypto>

## What it claims
- 这是一个针对 Binance USDT 流动性较好币对的横截面 stat-arb 研究仓库，核心比较 `cross-sectional momentum` 与 `short-horizon reversal`。
- README 公开写明了策略骨架：横截面排序、分桶、top/bottom 分位多空、1-bar lag 执行、turnover-based 交易成本、可选流动性过滤。
- 作者直接给出 4H reversal 的 fee-aware 压力测试：`H=3` 在 `20 bps` 成本下 Sharpe/CAGR 很强，但到 `40/60 bps` 会快速衰减甚至转负，明确把“执行成本”放进结论主体。

## What is actually evidenced
- 这不是只停在 README 口号的 repo：公开页面已经给出 reversal / momentum 对照图、bucket 图、成本压力测试图、带/不带 liquidity filter 的权益与 turnover 图。
- 执行诚实度比普通壳项目高一档：README 明写 `daily rebalancing`、`1-bar lag`、`turnover-based transaction costs`，至少不是把信号收益直接冒充可成交收益。
- 它还主动提示可复现风险：如果重下 OHLCV 或重做 universe 过滤，样本期和最优参数会漂移；因此要冻结 `start/end date + universe + cache` 才能锁住结果。这个提醒本身说明作者知道样本漂移是决定性风险，而不是刻意回避。
- 目前公开证据的不足也很清楚：
  - 公开主结果是 4H 口径，不是我们 desk 更关心的 15m/5m 可交易层；
  - 公开结果来自作者自己的数据切片与资产过滤，我们还没做 clean-room replication；
  - README 给出的是强 reversal 结论，但是否能在冻结样本、固定币池和统一成本口径下复现，仍是唯一需要先回答的 blocker。

## Intake verdict
`Rank 155 / Jamestilfords/statarb-crypto` 本轮 fresh intake 结论为 **keep_P1**。

原因不是它已经通过 admission，而是它已经拿出了足够具体且带成本口径的公开证据，值得消耗那唯一一次 surviving follow-up：先做 `frozen-sample clean-room replication`，验证 4H reversal 在固定 universe / date / cost 口径下是否还能诚实复现。换句话说，它不再属于“只有故事没有证据”的 direct-park repo，而是一个有明确单一 follow-up 方向的 surviving candidate。

## Result sentence
`Rank 155 / Jamestilfords/statarb-crypto` 公开了带 1-bar lag 与 turnover-based 成本的 4H reversal 证据，已足以进入 `keep_P1`，其唯一高杠杆下一步是 frozen-sample clean-room replication，而不是继续停留在 fresh-intake 壳项目层。