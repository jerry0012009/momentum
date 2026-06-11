# bot3 optimization loop — term-structure calendar spread follow-up park

- 时间：2026-03-24 08:17 UTC
- 路径判断：Scout
- 顶板动作：`Next 3 bot3 runs #2 = 若新 intake = keep_P1：做唯一一次最小 decisive follow-up`
- 本轮对象：term-structure calendar-spread reversion raw alpha
- 上轮 intake：`research/optimization_loop/2026-03-24_0745_term-structure-calendar-spread-keep-p1.md`

## 本轮只推进的 1 个主点
把上轮的“事件会回归”证据，压成 **post-cost non-overlap PnL**，直接回答这条线能不能升 `P2`。

## 紧邻 1 个子点
保持口径最小且诚实：
- 仅用已有 `30d / BTCUSDT / 15m` 公共数据样本；
- 仅做 non-overlap 事件；
- 仅把 `|z|>=2 -> |z|<=0.5 or 8 bars timeout` 转成 calendar ratio PnL；
- 仅看成本后是否还能站住，不扩成多品种大研究。

## 最小实验口径
- 数据：`reports/artifacts/quant_digests/term_structure_calendar_20260324_0730/term_spread_15m_30d.csv`
- 交易代理：`ratio = next_quarter / current_quarter`
- 方向：`direction = -sign(z_entry)`（term spread 极值后做回归）
- 退出：`|z|<=0.5` 或最多 `8` 根 15m bar
- 成本压力：`6 / 10 / 14 / 20 bps` round-trip

## 结果
核心结果（`126` 笔 non-overlap 事件）：
- 毛均值：`+6.61 bps/trade`
- 毛中位：`+5.66 bps/trade`
- 毛胜率：`94.4%`
- `6 bps` 成本后：均值只剩 `+0.61 bps/trade`，净胜率 `45.2%`
- `10 bps` 成本后：均值 `-3.39 bps/trade`
- `14 bps` 成本后：均值 `-7.39 bps/trade`
- `20 bps` 成本后：均值 `-13.39 bps/trade`

一句会改变系统认知的话：
> term-structure calendar-spread reversion 的唯一 follow-up 已完成；它虽然事件回归率高，但 30 天 15m non-overlap calendar-ratio PnL 在 `10bps+` 成本下已转负，`6bps` 下也只剩擦边正值，因此本轮结论是 `park`，不升 `P2`。

## 简短 scorecard
- 事件回归存在：`通过`
- non-overlap PnL 已落地：`通过`
- 6bps 后仍强：`未通过（仅擦边）`
- 10bps 后仍为正：`未通过`
- 升 P2 资格：`未通过 -> park`

## 产物
- `reports/artifacts/quant_digests/term_structure_calendar_20260324_0814_followup/event_pnl_nonoverlap.csv`
- `reports/artifacts/quant_digests/term_structure_calendar_20260324_0814_followup/summary.json`

## 下一步
按 policy，这条 survivor 已用完唯一一次 follow-up 且未升 `P2`，应移入 `Background pool`；下一轮默认动作应回到 **fresh intake**。
