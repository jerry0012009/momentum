# Rank 389 survivor follow-up — collector_receive_ts 同窗护栏 + 成本后净边际收口（promote_P2）

- 时间：2026-04-12 13:15 UTC
- 对象：`Rank 389 / cross-venue net-carry ranking alpha`
- 对应 cycle 小点：`Surviving candidate` 唯一 follow-up
- 产出 artifact：`reports/artifacts/optimization_loop/rank389_survivor_followup_20260412_1315.json`

## 执行动作
在统一 `collector_receive_ts` 同窗护栏下，对 Binance / Hyperliquid / dYdX 的 BTC perp 进行一次最小可执行重算：
1. 同窗可得性：三所快照按采集接收时刻对齐，检查是否在容忍窗内。
2. 成本后净边际：按 `funding_apr + basis_apr` 做 venue ranking，并在 `25k USD`、`30d` 口径下注入 taker fee + orderbook slippage 的 round-trip 成本，计算 pair edge。

## 关键结果
- 同窗护栏：`collector_window_ms = 130`（`<= 5000ms`，通过）。
- pre-cost 排名：
  - `dydx net_before_cost_apr ≈ -0.1605`
  - `hyperliquid net_before_cost_apr ≈ -0.1997`
  - `binance net_before_cost_apr ≈ -0.2006`
- best pair：`earn = dYdX`，`hedge = Binance`
- pair edge：
  - `edge_before_cost_apr ≈ +0.0401`
  - `edge_after_cost_apr ≈ +0.0104`（成本后仍为正）

## honesty / execution 结论
- 上轮唯一 blocker（dYdX 缺少稳定 server timestamp）在本轮通过 `collector_receive_ts` 同窗护栏得到可执行补偿；未出现新的单一 decisive honesty blocker。
- 在最小成本注入后，pair 级净边际仍为正，满足 survivor follow-up 的 admission 收口条件。

## 本轮 verdict
**Rank 389：survivor follow-up 通过，`promote_P2`。**

会改变系统认知的一句话：
> Rank 389 在 `collector_receive_ts` 同窗护栏与最小 fee/slippage 注入下，cross-venue net-carry pair 仍保留正的成本后净边际，故由 survivor 直接升级到 `Active P2`。
