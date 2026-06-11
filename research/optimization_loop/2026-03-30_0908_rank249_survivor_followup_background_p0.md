# 2026-03-30 09:08 UTC — Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing：survivor follow-up -> background/P0

- 时间：2026-03-30 09:08 UTC
- 对象：`Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing`
- 轮次类型：bot3 auto optimization
- 结论：`唯一 survivor follow-up 用完 -> 回 background/P0`

## 这轮只回答什么
按当前 `cycle_plan`，本轮只执行最前的小点：

> `selected-follower routing` 在 **rolling** 口径下、切到 **perp / after-cost** 后，是否还留下可执行 pocket？

不重做泛 cross-crypto lead-lag，也不回退成 alt basket 追涨；只保留 `leader basket 先动 + pair-specific follower routing 的下一根 spread catch-up` 这个主语。

## 本轮最小诚实实验
我直接把首轮 spot pocket scan 收口到一个更接近执行的 perp walk-forward：

- 市场：Binance USDⓈ-M perpetual
- bar：`15m`
- leaders：`BTCUSDT / ETHUSDT / LTCUSDT`
- followers 候选：`LINKUSDT / ADAUSDT / XRPUSDT / TRXUSDT / ETCUSDT / DOGEUSDT`
- 滚动方式：`14d train -> 7d test`，在训练窗里只保留 **train mean > 0** 的 follower pocket，测试窗继续沿用该 pocket 与对应阈值
- 触发：`|leader_ret - follower_ret| >= train q80`
- 持有：下一根 `15m`
- 成本：`16 bps round-trip`（按 4 条腿的 taker-ish 最小诚实成本口径）

产物：
- `reports/artifacts/optimization_loop/rank249_survivor_followup_20260330_0904/summary.json`
- `reports/artifacts/optimization_loop/rank249_survivor_followup_20260330_0904/by_symbol.csv`
- `reports/artifacts/optimization_loop/rank249_survivor_followup_20260330_0904/events.csv`

## 结果
### 总体
- walk-forward 测试事件数：`715`
- gross：`-0.70 bps/event`
- net（after-cost）：`-16.70 bps/event`
- net 正收益占比：`20.0%`

### by symbol（只看 train 窗中被滚动选中的 pocket）
- `ETCUSDT`：gross `+0.84 bps`，net `-15.16 bps`，`212` events
- `DOGEUSDT`：gross `+0.60 bps`，net `-15.40 bps`，`127` events
- `TRXUSDT`：gross `-0.67 bps`，net `-16.67 bps`，`124` events
- `XRPUSDT`：gross `-2.43 bps`，net `-18.43 bps`，`92` events
- `ADAUSDT`：gross `-2.81 bps`，net `-18.81 bps`，`160` events
- `LINKUSDT`：在 rolling train 窗里没有稳定到足以连续入选的 pocket，没形成可交付的 perp survivor 主轴

## 这一步改变了什么认知
首轮 `spot 15m` pocket scan 留下的关键信号是：**别做 equal-weight follower basket，pair-specific pocket 可能存在。**

但这一步把问题收口到更诚实的执行口径后，答案变成：

1. **routing pocket 不够稳。** `spot` 上看着最像样的 `LINK/ADA/XRP`，切到 perp 并做 rolling 之后，没有留下一个持续、清楚、可复现的主 pocket；
2. **gross 也不够厚。** 即使让 walk-forward 只带着训练窗中为正的 pocket 进入测试，最好两条（`ETC / DOGE`）的 gross 也只有 `~0.6-0.8 bps/event`，远低于多腿 perp spread catch-up 需要覆盖的最小真实成本；
3. **因此 survivor 的唯一 blocker 已经被回答完。** 问题不是“还差一点参数微调”，而是当前对象在 `rolling routing + perp/after-cost` 下没有留下足够诚实的可执行 pocket。

## verdict
`Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing` 的 survivor follow-up 已诚实收口：首轮留下的 `selected-follower pocket` 在 `14d->7d rolling` 的 Binance perp `15m` walk-forward 里没有保住可交付的主 pocket，最好 gross 也不足以覆盖 4 腿 after-cost，因此这更像 spot 幻觉 / 过薄 pocket，而不是值得继续推进的前排对象；本轮结论是 **唯一 follow-up 用完，回 background/P0，不升 P2**。

## 对 runtime 的含义
- `Surviving candidate slot` 应释放
- `Background pool.latest_parked` 改写为 `Rank 249`
- 当前 `cycle_plan` 第 1 项写成 `done`

## 备注
如果将来要 reopen，这条线也不该以“泛 network lead-lag”重开；唯一值得重新开的方式，是拿到**更强的单 follower / 更短时钟 / 更低腿数实现**，证明 gross 足够厚，能真实覆盖 perp 多腿成本。