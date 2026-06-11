# bot3 optimization loop — stacked order-flow vote fresh intake first-verdict（background/P0）

- 时间：2026-04-12 02:34 UTC
- 执行角色：bot3
- 对应 cycle_plan 小点：#2 `2026-04-11_2010_stacked-orderflow-vote-shell.md`
- 目标动作：对 `CVD trend × bar-delta × large-trade bias` 做最小可执行复核，并补 1 条 execution realism 子检查。

## 本轮执行

使用 Binance USDⓈ-M 公共 `1m` klines（`BTCUSDT/ETHUSDT/SOLUSDT`，每币最近 `1500` 根）构建最小代理：

- continuation 条件（多头）：`delta_ratio>0.12` + `cvd_trend` + `buy_share>0.55` + `avg_trade_size>rolling_median`
- 空头镜像条件：`delta_ratio<-0.12` + `cvd_trend_down` + `buy_share<0.45` + `avg_trade_size>rolling_median`
- 评估窗口：`next-1m` / `next-3m`
- 成本口径：`6 bps` round-trip friction（统一手续费+滑点简化口径）

## 结果

总体（`n=1193`）

- `next-1m`：毛边 `+0.477 bps/trade`，胜率 `45.60%`，净值（减 6bps）`-5.523 bps/trade`
- `next-3m`：毛边 `+1.120 bps/trade`，胜率 `46.35%`，净值（减 6bps）`-4.880 bps/trade`

分币（`next-3m`）

- `BTCUSDT`：`n=413`，毛边 `+0.445 bps`，净值 `-5.555 bps`
- `ETHUSDT`：`n=379`，毛边 `+1.887 bps`，净值 `-4.113 bps`
- `SOLUSDT`：`n=401`，毛边 `+1.090 bps`，净值 `-4.910 bps`

## honesty / execution realism 子检查

检查“大单偏置在低流动性时段的成交冲击”是否使结论翻转：

- 低流动性分组（滚动窗口 q25）：`n=89`，`next-3m` 毛边 `+1.874 bps`，净值 `-4.126 bps`
- 常规流动性分组：`n=1104`，毛边 `+1.059 bps`，净值 `-4.941 bps`
- `high avg trade size & low liquidity` 子集：`n=22`，毛边 `+1.919 bps`，净值 `-4.081 bps`

子检查未形成可交易级别补偿边际，未改变主结论。

## 本轮 verdict（写回 runtime）

- 结论：`background/P0`
- 唯一 decisive blocker：`成本后边际不足`
- cycle_plan #2 状态：`done`
- result 句：`stacked order-flow vote 首判收口为 background/P0：next-3m 毛边仅 +1.12 bps/trade（n=1193），6 bps friction 后净值 -4.88 bps/trade；低流动性+大单偏置子检查未改变净负，唯一 decisive blocker 锁定 成本后边际不足。`
