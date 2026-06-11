# 2026-04-06 05:52 UTC — Rank 348 / basis relaxation × regime-sized funding carry first verdict keep_P1

## 本轮执行对象
- target: `research/quant_digests/2026-04-06_0458_basis-relaxation-regimesized-funding-carry-alpha.md`
- action: 作为当前首条 `fresh intake`，判断 `basis relaxation × regime-sized funding carry` 是否构成 distinct 的 funding/basis raw alpha，而不是已有 funding 阈值 carry 的复杂包装。

## 结论
**`Rank 348 / basis relaxation × regime-sized funding carry` 完成 fresh intake first verdict：对象保留了独立的 raw alpha 主语，不是“funding 高就收、再叠一层 sizing” 的换皮，因此本轮给出 `keep_P1`，并进入唯一 `Surviving candidate slot`。**

## 为什么这次不是旧 funding carry 换皮
这份材料虽然仍属于 `delta-neutral funding + basis convergence` 家族，但它新增的不是泛泛的“再加一个 regime filter”，而是把 carry 是否值得拿、能拿多久、该拿多大，压成一套能落到完整策略骨架里的因果时钟：

1. **`8h funding anchor + basis relaxation ratio` 把 payoff clock 写清了。**
   它不是只看当前 funding 高不高，而是先问 `basis` 能否在下一次 funding 前回锚；这直接定义了 entry 是否成立，也定义了 carry 持有窗口。
2. **`regime-sized exposure` 不是装饰性 overlay，而是策略主体的一部分。**
   `EQUILIBRIUM / WARM / NESS = 1.0x / 0.6x / 0.25x` 让同一条 carry 壳天然带有 hold / de-risk / size-down 机制，不再是假设 fixed size always-on。
3. **repo 的 PnL 口径已显式包含 `signed funding + basis MTM + fees`。**
   这意味着它并非只在论文层面讲“市场像热力学”，而是已经把 `basis path risk` 与成本后边界写进可执行骨架。

因此，这条线最诚实的 desk 读法是：

> **raw alpha 仍是 carry / basis convergence，但对象新增了一个可独立检验的 `basis relaxation -> carry timing -> regime-sized hold governance` 主语。**

这与已有那些 `threshold funding`、`fee-coverage gate`、`persistence horizon`、`richest venue routing` 的 funding carry 路线不同：
- 旧壳更多在回答 **“哪笔 funding 值得拿”**；
- 这条线更明确在回答 **“basis 回得够不够快、该不该在这个 regime 放大去拿”**。

## 为什么现在只给 keep_P1，不直接升 P2
现在还缺的不是故事，而是一个廉价但决定性的 portability check：
- 这套 `relaxation ratio / entropy / JE health / temperature` 的 regime-sized shell，
- 在 short-cycle desk 的 `1m/5m/15m` 更新频率和 after-cost 口径下，
- 是否真的能稳定改善 `BTC/ETH/SOL` 上的 next-cycle net PnL、drawdown、以及 adverse basis excursion，
- 还是只是原 repo 的 `8h funding-cycle` 叙事在年化 Sharpe 放大下看起来很漂亮。

也就是说，这一轮已经足够说明它**不是重复件**，但还不足以说明它已经通过 `P2` 所需的跨资产 / 时间 / 参数 / honesty admission。

## 建议的唯一 survivor follow-up 方向
下一步只值得做一件事：
- 直接把 `basis relaxation × regime-sized carry` 压成最小 portability check，
- 重点看 `BTC/ETH/SOL × 5m/15m` 下，`naive carry` vs `extreme-funding-only` vs `regime-sized carry` 是否在显式 after-cost 口径下仍保留稳定增量；
- 若优势只来自论文年化口径或单一币种/单一时段，就应诚实退回 `background / P0`。

## 对 runtime 的直接影响
- 分配下一个未使用的正式整数 `Rank 348`
- `Fresh intake slot.latest_result` 更新为 `Rank 348 ... keep_P1`
- `Surviving candidate slot` 切换为 `Rank 348`
- 本轮 `cycle_plan` 第 2 项写成 `done`
