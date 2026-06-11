# bot3 auto：dual momentum breakout fresh intake first verdict -> background/P0

- 时间：2026-04-21 02:24 UTC
- 执行槽位：Fresh intake slot
- 对象：`research/quant_digests/2026-04-20_1129_dual-momentum-breakout-expansion-alpha.md`
- 策略名：`20-bar breakout × dual momentum × ATR expansion`
- 本轮动作：按 cycle_plan 只补一个最小 decisive blocker：`1h` 母信号 + `15m` next-open 子执行，统一扣 `8bps`，并看 recent 月份切片与跨币稳定性。

## verdict

`20-bar breakout × dual momentum × ATR expansion` fresh intake first verdict = `background/P0`。

原因：最小 desk 版复核显示，after-cost 正边际集中在 `ETH 2026-02` 与少数 `BNB` 笔，`BTC/SOL` 整体费后为负，且 recent `2026-04` 可触发样本只剩 `ETH` 且 `avg_net8≈-29.7bps`；因此它当前更像需要事后 ranking/regime 才能解释的趋势 sleeve 线索，而不是可前排保留的独立 breakout alpha。

## 最小复核口径

- 数据：Binance USDⓈ-M futures public klines，`BTCUSDT/ETHUSDT/SOLUSDT/BNBUSDT`，从 `2025-12-01` 到本轮时间附近。
- 母信号：`1h` bar 上满足：
  - `close > SMA20 > SMA50`
  - `ADX >= 18`
  - `close > previous rolling_high20`
  - `mom20 > 3%`
  - `mom60 > 5%`
  - `ATR/close >= rolling 120-bar q55`
- 子执行：母信号后一根 `15m` open 入场，固定持有 `16` 根 `15m`（约 4h）后下一根 open 出场。
- 成本：单笔 round-trip 统一扣 `8bps`。

## 核心结果

| symbol | trades | avg net8 bps | sum net8 bps | 2026-04 trades | 2026-04 avg net8 bps |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | 7 | -28.75 | -201.28 | 0 | n/a |
| ETHUSDT | 20 | +20.42 | +408.45 | 3 | -29.72 |
| SOLUSDT | 12 | -64.63 | -775.53 | 0 | n/a |
| BNBUSDT | 3 | +23.57 | +70.72 | 0 | n/a |

月份切片显示 strongest 月份主要来自 `2026-02`：`ETH` 6 笔 `avg≈+207bps`、`SOL` 4 笔 `avg≈+139bps`、`BNB` 1 笔 `avg≈+220bps`；但 `2026-03` 已明显回撤（`ETH≈-68bps`、`SOL≈-173bps`、`BNB≈-74bps`），`BTC` 也没有形成稳定正口袋。

## 认知更新

这条线仍可作为趋势族的设计提示：breakout 需要 acceleration 与 ATR expansion 配合，组合层 ranking/correlation gate 可能有研究价值。但作为本轮 fresh intake 的 front object，它没有通过“跨币或至少非单一月份 after-cost pocket”的最低门槛；若未来人工 reopen，必须先证明 ranking/correlation gate 是 ex-ante 可执行且不是事后挑 `ETH 2026-02`。

## runtime 写回

- Fresh intake slot：写成 `done/current_target none`，latest_result 指向本 verdict。
- Background pool：追加本对象为 latest parked。
- cycle_plan item 1：`status=done`，`result=...background/P0`。
