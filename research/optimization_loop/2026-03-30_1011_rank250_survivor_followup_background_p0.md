# Rank 250 / pseudosession open leader continuation survivor follow-up 收口

- 时间：2026-03-30 10:11 UTC
- 对象：`Rank 250 / pseudosession open leader continuation`
- 本轮动作：执行当前 `cycle_plan` 最前 pending 小点，作为唯一合法 `Surviving candidate` 的唯一一次 follow-up，只回答这条 `00/08/16 UTC pseudo-session` 开头 `30m` 的 `dominant leader 自身继续领跑` pocket，在 `spread_to_runner` 阈值与 `12/24/30 bars` 持有窗的 rolling / OOS、perp / after-cost 口径下是否仍保有稳定边。
- 输入文件：
  - `reports/artifacts/literature/tmp_crossmarket_intraday_tsmom_leader_session_events_2026-03-30.csv`
  - `reports/artifacts/literature/tmp_crossmarket_intraday_tsmom_leader_session_summary_2026-03-30.csv`

## 结论（result）

**Rank 250：唯一 survivor follow-up 已用完；`leader>=50bps + spread_to_runner>=40bps` 虽在全年汇总里留下 `12/24/30 bars = +2.34/+8.96/+16.16 bps/trade` 的 after-cost 均值，但 rolling / OOS 并不稳定——最近 `2026 Q1` 已转成 `-53.63/-37.63/-26.57 bps`，而且阈值从 `40bps` 稍改到 `30bps` 或 `50bps` 就失去 after-cost 边，因此这条 pocket 还不够诚实地升 `P2`，当前 verdict 是收口回 `background/P0`。**

## 这次 follow-up 实际回答了什么

### 1) 固定对象主语后，只有 `spread_to_runner >= 40bps` 看起来像 pocket
- `leader>=50bps + spread>=20bps`：`n=253`
  - `12/24/30 bars` after-cost 均值：`-4.98 / -6.23 / -2.85 bps`
- `leader>=50bps + spread>=30bps`：`n=184`
  - `12/24/30 bars` after-cost 均值：`-5.72 / -5.99 / +3.21 bps`
- `leader>=50bps + spread>=40bps`：`n=112`
  - `12/24/30 bars` after-cost 均值：`+2.34 / +8.96 / +16.16 bps`
- `leader>=50bps + spread>=50bps`：`n=74`
  - `12/24/30 bars` after-cost 均值：`-9.88 / -14.99 / -13.52 bps`

结论：这不是宽阔稳定带，而是只在 `40bps` 一档看起来成立；阈值轻微挪动后就塌，说明对象当前更像参数尖峰，不像可直接升级到 `P2` 的稳定 pocket。

### 2) OOS / 时间稳定性不过关，最近样本已明显转弱
对 `leader>=50bps + spread>=40bps` 这唯一看起来成立的档位做时间切片：

- 前半样本（前 56 笔）：`-8.57 / +15.80 / +32.95 bps`
- 后半样本（后 56 笔）：`+13.24 / +2.12 / -0.63 bps`

按季度拆：
- `2025 Q2`（38 笔）：`-24.98 / -6.55 / +20.65 bps`
- `2025 Q3`（29 笔）：`+34.88 / +54.13 / +30.99 bps`
- `2025 Q4`（24 笔）：`+55.22 / +19.70 / +28.51 bps`
- `2026 Q1`（21 笔）：`-53.63 / -37.63 / -26.57 bps`

结论：这条线不是“最近也还在 work 的稀疏 alpha”，而是至少在最新季度已经明显翻负；即便全年均值还在，OOS 角度也不支持直接升 `P2`。

### 3) Rolling 检查只能说明“历史上常常为正”，不能掩盖最近翻负
对 `spread>=40bps` 的 112 笔事件做 rolling trade-window 检查：
- `24-trade rolling`：`12/24/30 bars` 为正窗口占比约 `70.8% / 73.0% / 75.3%`
- `28-trade rolling`：为正窗口占比约 `72.9% / 70.6% / 74.1%`
- `32-trade rolling`：为正窗口占比约 `72.8% / 74.1% / 77.8%`

但同一组 rolling 的最差窗口均值也能下探到：
- `24-trade rolling`：`-55.99 / -76.50 / -82.22 bps`
- `28-trade rolling`：`-43.40 / -53.76 / -54.04 bps`
- `32-trade rolling`：`-30.57 / -46.64 / -44.61 bps`

这说明它最多只能算“历史上有阶段性 pocket”，而不是已经通过 survivor follow-up 后可放心升 `P2` 的稳定对象。

## survivor 收口 verdict

- 本轮不给 `promote_P2`
- 本轮也不给新的开放式 `keep_P1`
- `Rank 250` 的唯一 survivor follow-up 预算已用完，按 policy 收口回 `background/P0`

## 本轮 runtime 写回

- `Surviving candidate slot` 清空为 `none`
- `Background pool.latest_parked` 改写为 `Rank 250 / pseudosession open leader continuation`
- `cycle_plan` 第 1 项写回 `done`
