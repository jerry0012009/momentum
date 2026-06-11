# bot3 optimization loop — Donchian breakout × vol-target × ATR trail fresh intake verdict

- 时间：2026-04-25 17:40 UTC
- 对象：`research/quant_digests/2026-04-25_1652_breakout-voltarget-atrtrail-portability-verdict.md`
- 执行动作：fresh intake first verdict（只基于该 digest 已给出的 repo source audit + `15m` public-data portability probe，判断这条 repo 趋势壳在 short-cycle desk 上是否仍保留足以支撑前排保留的 queue-facing pocket）
- 相关 policy：`BOT2_BOT3_POLICY.md` 中 fresh intake 必须直接收口为 `keep_P1` 或 `background/P0`；若结论只剩“慢周期骨架可借鉴”，但没有 short-cycle queue-facing pocket，则不得保留前排。

## 结论
本轮将 `Donchian breakout × vol-target × ATR trail` 直接收口为 `background/P0`，不保留 `keep_P1`。

## 改变系统认知的一句话
这条 repo 趋势壳对当前 short-cycle crypto desk 没有留下足以支撑前排保留的 raw pocket：`15m` portability probe 在全部参数组合上 validation/test 皆为负，且最不差组合连 gross 都为负，因此它当前只能作为 `4h/1h parent -> 15m/5m child execution` 的慢周期骨架素材，而不是值得继续占用前排预算的 short-cycle 候选。

## 为什么这已经足够形成 first verdict
digest 本身已经给出最小 decisive blocker，而且这个 blocker 足以直接决定前排去留：

1. **short-cycle 直接可交易 pocket 不存在**
   - `breakout=20/40/60`、`ma=none/100/200`、`volwin=20/30` 的 `15m` probe 全部在 validation/test 为负。
   - 最不差组合 `breakout=60, ma=200, volwin=30` 仍是：
     - validation net `-0.955 bps/bar`
     - test net `-1.274 bps/bar`
     - test Sharpe `-18.56`
   这已经不是“还没找到最好参数”，而是没有出现值得保留的 short-cycle after-cost pocket。

2. **不是单纯被成本吃死，而是信号本体在 `15m` 已失真**
   - digest 明确写出 test gross 也为 `-0.288 bps/bar`。
   - 因而问题不是把手续费口径再调松一点就能转正，而是 repo 的 `4h` breakout continuation 逻辑下沉到 `15m` 后，alpha 主体已不成立。

3. **当前能保留的只剩“慢周期骨架可借鉴”**
   - digest 的最佳 reader-facing 结论是：它更像 `trend parent shell`，可借的是 breakout/MA/ATR/cost-aware sizing 这些组件；
   - 但 policy 明确要求 fresh intake 只有在能保留一个值得继续跟进的 short-cycle queue-facing pocket 时才 `keep_P1`。
   - 既然当前没有这样的 pocket，就不能把“可做父信号骨架”误写成前排存活。

## 与 policy 的对应
- 该对象属于 fresh intake，不是 survivor / active P2 / P3 wiring。
- 当前 verdict 已足够直接回答 `keep_P1` vs `background/P0`。
- 因为没有 short-cycle queue-facing pocket，所以合法动作是直接收口到 `background/P0`，而不是把“父级别信号 + 子级别执行”留成开放式前排跟进。

## runtime write-back
- `Fresh intake slot.latest_result`：更新为本次 `background/P0` verdict。
- `Fresh intake slot.latest_result_record`：指向本日志。
- `cycle_plan[1]`：写入本轮 verdict 并标记 `done`。

## 尾注
后续若 human 或 bot2 想重开该主题，正确 reopen 方式应是把它作为一个新的派生 hypothesis（例如明确的 `4h/1h parent trend -> 15m/5m child execution` 结构）重新进入 fresh intake，而不是把这次失败的 `15m` 原生 breakout 继续留在前排。