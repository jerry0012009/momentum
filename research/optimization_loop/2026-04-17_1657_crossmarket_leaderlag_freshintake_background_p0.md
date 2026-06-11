# 2026-04-17 16:57 UTC · item3 · crossmarket leader-laggard fresh intake first verdict（background/P0）

## 执行对象
- target: `research/quant_digests/2026-04-16_1928_crossmarket-intraday-leaderlag-alpha.md`
- 本轮动作: `cycle_plan item3`（conditional fresh intake）

## 本轮最小可复算 spec（按 policy 要求统一口径）
- universe: Binance USDⓈ-M `BTC/ETH`（leader）-> `SOL/XRP`（laggard）
- bar/session: `15m`，`00/08/16 UTC` 的 `8h` session
- signal: 每个 session 前 `60m`（前 4 根 15m）`BTC/ETH` 等权收益方向
- gate: `abs(leader_ret)` 仅用**历史已完成 session**滚动 `q80`（不看未来）
- entry/exit: **strict `t+2`**（signal 后延迟两根，`idx6 open` 入场）+ 持有 4 根（`idx10 open` 出场）
- cost: round-trip `4/6/8 bps`

## 最小 honesty / execution realism 子检查（本轮唯一）
- 检查点：leader move 是否在 laggard 入场前完全已知，避免会话内重叠泄露。
- 结果：`entry_time - signal_close_proxy` 最小/均值均为 `30.0 min`，满足 strict `t+2`。

## 结果（会改变系统认知）
- 在统一 `t+2 + 4/6/8bps` 下，`BTC/ETH -> SOL/XRP` equal-laggard 口径**费前已负**，费后进一步下探：
  - overall（174 trades）：`gross=-5.25bps`，`net4=-9.25bps`，`net6=-11.25bps`，`net8=-13.25bps`
  - `SOL`：`net4=-4.20bps`，`net6=-6.20bps`，`net8=-8.20bps`
  - `XRP`：`net4=-14.31bps`，`net6=-16.31bps`，`net8=-18.31bps`
- 分时段也不支撑保留：EU/US 仅有轻微 gross pocket（EU `+0.70bps`、US `+3.52bps`），但 `4/6/8bps` 后全部转负；Asia 显著负值。
- 结论：该 alpha 的优势不具备统一 delayed+cost 可执行性，且 laggard leg（尤其 XRP）结构性拖累，**first verdict 直接收口 `background/P0`，不进入 survivor。**

## artifacts
- `reports/artifacts/optimization_loop/2026-04-17_crossmarket_leaderlag_t2_check/summary_t2strict.csv`
- `reports/artifacts/optimization_loop/2026-04-17_crossmarket_leaderlag_t2_check/events_t2strict.csv`
- `reports/artifacts/optimization_loop/2026-04-17_crossmarket_leaderlag_t2_check/meta_t2strict.json`
