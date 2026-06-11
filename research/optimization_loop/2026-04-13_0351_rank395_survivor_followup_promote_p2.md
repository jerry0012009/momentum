# Rank 395 — survivor 唯一 follow-up：FDS threshold governance 冻结并做独立切片复核（promote_P2）

- 时间：2026-04-13 03:51 UTC
- 执行器：bot3
- 对象：`Rank 395 / bucket dispersion MR × FDS admission`
- 对应小点：`cycle_plan #1`

## 本轮执行（最小 honesty/治理检查）
按小点要求仅做一次最小、可复现的 `fds_threshold_governance` 收口：

1. **预注册阈值网格**：`gate > {0.00, 0.25, 0.50}`（固定，不允许事后扩表）
2. **预注册选择规则（单一）**：仅在训练切片内，选择“**最小**且满足 `n>=80 && mean_edge_bps>0`”的阈值；若无阈值满足则判定失败
3. **独立切片**：按事件时间做 70/30 时间切片，后 30% 仅用于 out-of-sample 复核
4. **honesty 子检查**：禁止在看到测试结果后改阈值或改 bucket 定义

数据与实现：
- 仓库：`https://github.com/Jbdelrio/hyperstat-arb-bot`（depth-1 clone）
- 数据：repo 自带 `data/candles/*/5m.parquet` 与 `data/funding/*/8h.parquet`
- 标的：`ETH/SOL/AVAX/ARB/OP`
- 口径：`horizon=12 bars (1h)`，事件 `|z|>=1.5`，edge 记为 bucket-relative contrarian forward return（bps）
- FDS：使用 repo `FundingDivergenceSignal(FDSConfig())` 原始实现

## 结果摘要
时间切片点：`2026-02-15 20:39:00+00:00`

- events_total=`7245`（train=`5071`，test=`2174`）

训练切片（阈值治理选择面板）：
- `gate>0.00`: n=`2113`, mean=`+1.30 bps`, hit=`40.3%`
- `gate>0.25`: n=`1886`, mean=`+1.81 bps`, hit=`40.8%`
- `gate>0.50`: n=`1159`, mean=`-0.18 bps`, hit=`37.9%`

按预注册规则，**选中阈值 `gate>0.00`**（满足条件的最小阈值）。

独立测试切片（仅复核选中阈值）：
- `gate>0.00`: n=`1166`, mean=`+27.46 bps`, hit=`51.0%`

## 结论（会改变系统认知）
`Rank 395` 的唯一 survivor blocker（`fds_threshold_governance`）已完成最小治理收口：在预注册网格+单一选择规则下，选中阈值在独立时间切片保持费前正向边际，故本轮将对象从 `Surviving candidate` **升级为 `Active P2 (promote_P2)`**。

## blocker 状态
- 原唯一 blocker：`fds_threshold_governance` → **cleared（在本轮治理检查口径内）**
- 当前无新的单一 decisive honesty blocker（进入 P2 后再按 admission 五维做系统化出口决策）。
