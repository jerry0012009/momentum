# Rank 259 / bear-shock short-alt lag pocket — survivor follow-up exit to background/P0

- Time: `2026-03-30 20:15 UTC`
- Target: `Rank 259 / bear-shock short-alt lag pocket`
- Cycle slot executed: `cycle_plan[1]`
- Source digest: `research/quant_digests/2026-03-30_1728_bear-shock-short-alt-lag-pocket.md`
- Prior state record: `research/optimization_loop/2026-03-30_1941_rank259_bear_shock_short_alt_lag_pocket_intake_keep_p1.md`

## What this follow-up had to answer
按 state 的唯一 survivor follow-up 要求，我只回答一个出口问题：

> 把对象继续锁定为 `bear regime 下 BTC 5m shock -> short alt basket 15m delayed selloff`，从 `Spot proxy` 切到可交易 `perp` 口径，并在 **冻结 basket、next-bar 进场、统一成本** 下，成本后 edge 是否仍然足够诚实地存活，值得升 `P2`？

这里不允许继续做 hindsight 路由，不允许把样本内赢家漂成动态 basket，也不允许把对象偷换成“更宽泛的 risk-off alt short”。

## Follow-up setup
- 市场：Binance USDⓈ-M perp 月度公开 `5m` kline（`BTCUSDT` + 冻结 top5 basket：`TIA / SOL / NEAR / APT / OP`）
- 时间窗：`2025-11-30 17:25 UTC` 到可获得的月度 futures 数据末端（`2026-02` 月底）；`2026-03` 月度包当前公开端尚未提供，因此这次 follow-up 只用已可审计到的完整月包
- 触发条件：
  - `BTC 5m drop ∈ [1.0%, 2.0%]`
  - `BTC 7d return <= -5%`
  - 跳过 `UTC 07:00~11:59`
- 执行：
  - signal bar 结束后 **next-bar open** 进场（比原 digest 里的“同 bar 末尾 proxy”更诚实）
  - 持有 `15m`（即从下一根 bar 开始持有 3 根 `5m` bar，至第 4 根 close 退出）
  - 方向：等权 short 冻结 top5 basket
- 成本口径：统一看 `6 / 10 / 14 bps`，并额外看 `18 bps stress` 作为 `fees + slippage + funding/basis` 的更厚压力测试

## What came back
满足条件且能在冻结 top5 perp basket 上完整对齐的事件，**只有 7 个**。

逐事件 top5 basket gross mean（未扣成本）：
- `2026-01-31 18:35 UTC`: `+4.63 bps`
- `2026-02-05 15:20 UTC`: `-77.82 bps`
- `2026-02-05 15:25 UTC`: `-180.45 bps`
- `2026-02-05 20:15 UTC`: `+35.93 bps`
- `2026-02-05 20:50 UTC`: `-124.22 bps`
- `2026-02-06 00:05 UTC`: `+670.40 bps`
- `2026-02-06 00:10 UTC`: `-346.96 bps`

扣成本后的 event-level 汇总：
- `6 bps`：mean `-8.64 bps`，median `-83.82 bps`，hit rate `28.6%`
- `10 bps`：mean `-12.64 bps`，median `-87.82 bps`，hit rate `28.6%`
- `14 bps`：mean `-16.64 bps`，median `-91.82 bps`，hit rate `28.6%`
- `18 bps stress`：mean `-20.64 bps`，median `-95.82 bps`，hit rate `28.6%`

## Decisive read
这次 follow-up 不支持 `promote_P2`，理由有三条，而且都是出口级别的：

1. **从 Spot proxy 切到 perp + next-bar 以后，冻结 top5 basket 的中心收益已经转负。**
   不是“成本再压一点才变差”，而是连 `6 bps` 下的 event mean 都已经是负值，median 更明显为负。

2. **样本稳定性不够，且分布被单一 crash window 主导。**
   7 个事件里，只有 `2026-02-06 00:05 UTC` 那一次给出极大的正收益（`+670 bps gross mean`）；除此之外，大多数窗口是小赚或显著亏损。当前更像是“极端 stress 时偶尔能抓到一次补跌尾段”，而不是稳定的可 admission pocket。

3. **冻结 basket 后，原 digest 里的 top-pocket 优势无法诚实外推成稳定策略骨架。**
   之前 `Spot proxy` 的亮点里，`TIA/SOL/NEAR/APT/OP` 看起来最强；但一旦固定成 perp basket 并用 next-bar 进场，它们并没有在统一成本下保住足够稳定的成本后 edge，说明原先更像是样本内 pocket + 触发时点偏乐观，而不是已经足够进入 `P2 admission` 的对象。

## Verdict
唯一 survivor follow-up 已用尽，且出口结论明确：

`Rank 259：冻结 top5 perp basket + next-bar 执行后，bear-shock short-alt lag pocket 的成本后中心收益转负、事件分布被单一 crash 主导，不足以诚实升 P2；唯一 follow-up 用尽，回 background/P0。`

## Runtime writeback summary
- `Surviving candidate slot`：清空 `Rank 259`
- `Background pool.latest_parked`：更新为本次 `Rank 259` 出口结论
- `cycle_plan[1]`：`status = done`
- 不升 `P2`，不分配新的前排 survivor
