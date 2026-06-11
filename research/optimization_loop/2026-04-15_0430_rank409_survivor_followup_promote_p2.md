# Rank 409 survivor follow-up（唯一一次）— 1h 可交易 market proxy + continuation/reversal 对照

- 时间：2026-04-15 04:30 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：#1 `Rank 409 / BTC-beta-neutral residual momentum ranking shell`

## 本轮执行
1. 按计划完成 `1h` 主频复核，使用可交易 market proxy：`BTC` 与 `BTC+ETH`（双代理对照）。
2. 使用 residual ranking 同一底座做符号对照：
   - continuation：`+rank(residual_mom)`
   - reversal：`-rank(residual_mom)`
3. 统一 friction 口径：one-way `4/6/8 bps`。
4. honesty / execution realism 最小核验：
   - 信号仅用 `t` 及历史窗口；
   - 执行收益按 `t+1` 后持有窗口计入（strict next-bar mapping）；
   - market proxy 显式替换为可交易腿（不使用截面均值 market factor）。

## 关键结果
样本：`2026-03-01 00:00 UTC ~ 2026-04-15 04:00 UTC`，`1h` bars=`1085`。

- **continuation（两种 proxy）在 1/4/8/24h 持有下均为费后负**。
- **reversal 在 `24h` 持有出现稳定费后正 pocket（两种 proxy、三档成本均为正）**：
  - BTC proxy：net bps = `+19.97 / +15.97 / +11.97`（4/6/8 bps），net Sharpe = `2.03 / 1.62 / 1.22`
  - BTC+ETH proxy：net bps = `+21.37 / +17.37 / +13.37`，net Sharpe = `2.25 / 1.83 / 1.41`

## 产出工件
- `research/optimization_loop/artifact_rank409_survivor_1h_proxy_scan_20260415.csv`
- `research/optimization_loop/artifact_rank409_survivor_1h_proxy_scan_20260415.json`

## 结论（改变系统认知）
`Rank 409` 的 survivor 唯一 follow-up 已给出 decisive 结果：该家族在 `1h` 上不是 residual continuation，而是**可交易 residual reversal（24h hold）**，且在 `BTC`/`BTC+ETH` 可交易代理与 `4/6/8 bps` 下均保持费后正；满足升级条件，**从 P1 直接 `promote_P2`**（后续以 sign-fade 规格进入 P2 admission）。
