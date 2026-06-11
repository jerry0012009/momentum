# Rank 218 / Drift↔Hyperliquid same-asset perp-perp basis pocket × rollback execution intake → keep P1

- 时间：2026-03-28 10:31 UTC
- 对象：`Rank 218 / Drift↔Hyperliquid same-asset perp-perp basis pocket × rollback execution`
- 动作：fresh intake 首轮 verdict
- 来源：`research/quant_digests/2026-03-28_0903_drift-hyperliquid-basis-pocket.md`

## 本轮结论

`Rank 218 / Drift↔Hyperliquid same-asset perp-perp basis pocket × rollback execution` fresh intake 已完成首轮正式 verdict：这份 repo 留下的不是空泛的“双所价差扫描”，而是一条可独立判分的 cross-venue perp-perp basis raw alpha，并且执行层已经把双腿协调、超时、回滚与 safe-mode 骨架写到了可落地程度；但当前已知 live snapshot 同时表明 majors 上瞬时可交叉 gross edge 只有约 `0.8~2.3bps`，明显低于 repo 默认 taker/taker round-trip 成本 `30bps`，所以现阶段最诚实的位置是 `keep_P1`——保留这条对象，下一步只值得做一次 `pocket existence check`（depth-weighted、分 taker/taker 与 maker/taker 成本、看 pocket 频率/持续时间/markout），而不是直接升 `P2` 或把 taker-only 版本误判成可立即 admission 的策略。

## 为什么不是 P2

1. **alpha 是真的，但当前可活口径还没被证明。**
   - digest 已经明确把 base alpha 收口为 `same-asset perp-perp basis convergence`；
   - 但当前证据只证明“存在价差”，还没证明“在现实成本 + rollback buffer 下存在可重复 pocket”。

2. **当前 blocker 是 admission 级别缺口，不是标题润色。**
   - snapshot 里 `BTC/ETH/SOL` 的 gross crossable edge 约 `0.80~2.34bps`；
   - repo 默认 taker 成本口径约 `30bps` round-trip；
   - 这意味着 taker-only 读法当前明显不成立，必须先回答 pocket 是否只在 maker/taker 档存在。

3. **repo 的价值在“完整策略骨架”，不是“立即可上生产”。**
   - 有执行引擎、超时、回滚、safe mode，说明它值得继续跟；
   - 但当前最该补的是 `pocket existence`，不是再做泛化 admission 或直接推进 paper。

## 下一次唯一合法 follow-up 方向

若进入 survivor follow-up，唯一高杠杆动作应是：

- 仅针对 `BTC/ETH/SOL` 做 `1s` 级别 order-book 抓取；
- 用 depth-weighted price 构造双方向 `gross_edge_bps`；
- 分 `taker/taker`、`maker/taker`、`maker/taker + rollback buffer` 三种成本口径；
- 回答 pocket 的出现频率、持续时间与短窗 markout；
- 一次性收口成：`promote_P2` / `keep_P1 后转 background` / `drop_to_background`。

## Runtime writeback

- 分配新正式 rank：`218`
- `Fresh intake slot` 应切换到本对象
- `Surviving candidate slot` 应切换到本对象，`followup_budget_remaining: 1`
- 本轮 `cycle_plan` 第 3 项应改为 `done`

## Result sentence

`Rank 218 / Drift↔Hyperliquid same-asset perp-perp basis pocket × rollback execution` fresh intake 已完成首轮正式 verdict：这条对象确实留下了值得继续 admission 的 cross-venue raw alpha 骨架，但当前 live snapshot 同时证明 taker-only 口径被成本悬崖压死，因此本轮最诚实的层级是 `keep_P1`，只保留一次 `pocket existence check` 的 survivor 预算，而不是直接升 `P2`。
