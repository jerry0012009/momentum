# Rank 322 — kraken pairs z-score stop-loss shell — first verdict keep P1

- 时间：2026-04-04 04:24 UTC
- 对象：`research/quant_digests/2026-04-04_0316_kraken-pairs-zscore-stoploss-shell.md`
- 轮次角色：bot3 自动执行
- 结论：`keep_P1`

## 为什么这一步改变系统认知
`cointegrated spread z-score × stop-loss/time-exit` 在这份 repo 里已经不是“pairs 教材名词”，而是带有 `entry / exit / stop / cost / portfolio` 完整壳的 raw alpha；它对当前 desk 的价值在于提供一条可直接复刻的 pairs/stat-arb 标准母板，而不是又一条只有信号、没有策略外壳的想法。

## 本轮依据
1. digest 已把 repo 主语锁定为 `spread z-score mean reversion`，不是 volume/filter/宏观叙事伪装。
2. 源码链条完整覆盖：pair admission（cointegration + hedge ratio）、阈值入场、回归出场、极端偏离止损、交易成本扣减、参数网格、组合层回测。
3. 公共数据快检给出的关键事实不是“短周期一定能做”，而是 **同壳子在 `15m` 仍能保留正净边，而 `3m/5m` 更容易被成本吃掉**；这说明对象具备诚实可迁移的 near-short-cycle pairs lane，但还不该被误写成“天然适合更快频率”。

## verdict
正式给予 `Rank 322`，并把对象记为 `keep_P1`：
- 它已经满足 fresh intake first verdict 的最低要求：主语清楚、策略壳完整、存在至少一条诚实可迁移的 `15m / near-short-cycle` pairs lane。
- 但它还没有证明自己能直接跨到更快节奏的 desk execution，因此当前最合适的位置是 `P1`，等待那唯一一次 survivor follow-up 去回答：
  - 哪些 pair admission 过滤（half-life / rolling corr / phi）能避免慢漂移假 pair；
  - `2/4/8/12 bps` 成本梯度下，哪些 pair 还能穿过 cost cliff；
  - 是否存在可被收窄到更短周期的唯一诚实 lane。

## 对 runtime 的直接影响
- fresh intake 槽位：本对象 first verdict 已完成，释放槽位。
- surviving candidate 槽位：由 `Rank 322` 占据，保留唯一一次 follow-up 预算。
- Active P2 / Paper launch queue：本轮不触发。
