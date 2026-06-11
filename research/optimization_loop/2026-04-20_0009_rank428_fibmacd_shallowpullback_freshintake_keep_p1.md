# Rank 428 / fib-MACD shallow pullback continuation fresh intake -> keep_P1
- 时间：2026-04-20 00:09 UTC
- 对象：`research/quant_digests/2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`
- 轮次角色：bot3 当前 cycle_plan 第 2 项（fresh intake first verdict）

## 本轮只回答的 blocker
`EMA200 趋势内 shallow Fibonacci pullback × MACD recross` 在统一成本、低样本、月份切片与固定 bracket/timeout 诚实口径下，是否仍保有可独立承接的 after-cost continuation sleeve。

## 读取与最小核验
基于既有产物 `reports/artifacts/quant_digests/2026-04-19_fibmacd_pullback_probe_events.csv` / `*_summary.csv` 做最小 honesty 收口：
- 全体 `15m long`：`n=14`，`gross_mean≈+17.86bps`，`net8≈+9.86bps`
- 全体 `15m short`：`n=11`，`net8≈-58.71bps`
- 全体 `5m long`：`n=7`，`net8≈+13.59bps`，但样本更稀，不适合直接抬成主 pocket
- 聚焦 desk 指向的 `15m long + zone1~2`（浅回撤）后：共 `n=6`
  - `2026-02`: `5` 笔，均值 `net8≈+44.86bps`
  - `2026-03`: `1` 笔，`net8≈+92bps`
  - exit 结构：`4` 笔 TP（均 `+92bps net`），`2` 笔 timeout（均值约 `-25.84bps net`）
  - symbol 分布：`ETH/SOL/DOGE/ADA` 各 `1` 笔正样本，`LTC` `2` 笔 timeout 负样本

## 结论
**Rank 428：保留为 `P1 / surviving candidate`，但对象必须收窄成 `15m long-only shallow pullback (zone1~2) × fixed bracket continuation sleeve`，不能把 repo 原始 `多空对称 + 任意 zone + 5m 也可主跑` 叙事直接带进前排。**

## 为什么是 keep_P1 而不是 background/P0
1. 这条线已经留下一个会改变系统认知的独立 pocket：`15m long-only + zone1~2` 在统一 `8bps` 与固定 `1%/1.5% + timeout` 口径下仍为正，不是纯成本吞噬。
2. 它不是单一币硬撑；当前正样本分散在 `ETH/SOL/DOGE/ADA`，说明“顺趋势浅回撤 continuation” 这条骨架尚有跨币可迁移性。
3. 但它还远没到 `P2`：总样本仅 `6` 笔、月份厚度不足，`2026-04` 目前没有新的 `zone1~2 long` 命中，不能宣称 time stability 已闭合。

## 因此本轮 verdict
- `fresh intake first verdict = keep_P1`
- 分配正式 `Rank 428`
- 进入 `Surviving candidate slot`
- 唯一 follow-up 的默认问题应收敛为：**把对象固定在 `15m long-only zone1~2` 后，补 1 个最便宜且最能改变结论的时间稳定性 / child-entry realism 检查，回答这是不是仅靠少数 TP 命中的稀疏 bracket pocket。**

## 不做的事
- 不把 `5m` 直接升级成主周期
- 不把 short leg 一起保留
- 不在本轮直接升 `P2`
