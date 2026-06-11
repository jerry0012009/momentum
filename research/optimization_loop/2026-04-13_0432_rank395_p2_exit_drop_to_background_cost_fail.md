# Rank 395 — P2 admission 出口决策轮：统一成本后不成立，降级到 background/P0

- 时间：2026-04-13 04:32 UTC
- 执行器：bot3
- 对象：`Rank 395 / bucket dispersion MR × FDS admission`
- 对应小点：`cycle_plan #1`

## 本轮执行（仅此一个小点）
按 `P2 admission` 口径完成最小五维收口，并补 1 条 honesty 子检查：

- 数据：`/tmp/hyperstat-arb-bot/data`（repo 自带 `5m candles + 8h funding`）
- 标的：`ETH/SOL/AVAX/ARB/OP`
- 事件定义：`|z|>=1.5` 的 bucket-relative MR active events，`horizon=12 bars (1h)`，方向为 contrarian
- FDS：repo 原始 `FundingDivergenceSignal(FDSConfig())`
- 参数治理：固定阈值网格 `gate>{0,0.25,0.5}`，70/30 时间切片，训练段按单一规则 `n>=80 && mean_net_bps>0` 选最小阈值
- 统一成本口径：`12 bps round-trip`
- honesty 子检查：funding 对齐做保守延迟检查（`8h` lag 版本）

## 结果摘要
总 active events：`7245`

阈值治理面板（单位：`mean_net_bps`）：
- `gate>0.00`：train `n=2114`, `-7.31 bps`; test `n=1165`, `-18.74 bps`
- `gate>0.25`：train `n=1887`, `-7.73 bps`; test `n=1029`, `-22.42 bps`
- `gate>0.50`：train `n=1160`, `-2.16 bps`; test `n=678`, `-13.11 bps`

治理规则下 **无任何阈值** 同时满足 `n>=80 && train_mean_net_bps>0`，因此 admission 直接失败。

honesty 子检查（funding 8h-lag）在该失败前提下不改变结论：
- 因基线已无可通过阈值，lag 版本同样无法形成可通过 admission 的正净边际。

## 五维收口结论
1. effectiveness / expected return（含成本）：**失败**（统一成本后所有阈值净边际为负）
2. cross-asset stability：**无需继续开放检查**（主判据已失败）
3. time stability：**无需继续开放检查**（train/test 在可比阈值均为负）
4. parameter stability：**失败**（固定网格无可通过参数）
5. honesty / execution realism：**未发现可挽回主结论的唯一 blocker**（保守 funding 对齐不改变失败结论）

## 结论（会改变系统认知）
`Rank 395` 在 `P2 exit` 轮中被统一成本口径直接否决：`MR × FDS` 事件在预注册阈值网格下无法产出正的费后净边际，因此本轮执行 `drop_to_background`，不再保留在 `Active P2`。

## blocker 状态
- decisive blocker：`edge_after_cost`（统一 12bps 口径下全阈值为负）
- 动作：`Active P2 -> Background pool (P0)`
