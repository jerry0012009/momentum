# Rank 201 / UTC clock seasonality low-switch schedule — P3 launch wiring connected_runner_live

- 时间：2026-03-27 22:16 UTC
- 对象：`Rank 201 / UTC clock seasonality low-switch schedule`
- 本轮角色：bot3 对当前 `P3 / Paper launch queue` 头部对象执行最小 `launch wiring`；目标是把 queue-side 的 `promote_P3` 真正落成 `runner + scheduler + first verified run`

## 结论
**正式结果：`Rank 201` 已完成最小 launch wiring，运行态应从 queue-side 的 `promote_P3` 改写为 `connected_runner_live`。**

这次不是继续做研究，而是把已经足够值得 paper trade 的对象接上线：
- dedicated runner 已写出：`scripts/run_rank201_utc_clock_paper_runner.py`
- scheduler 已安装并启用：
  - `momentum-rank201-paper-refresh.service`
  - `momentum-rank201-paper-refresh.timer`
- 首跑验证已成功：
  - `systemctl start momentum-rank201-paper-refresh.service` 返回 `status=0/SUCCESS`
  - timer 已 `enable --now`，下一次触发时间为 `2026-03-27 22:17:20 UTC`

## 这次接线具体落了什么
### 1) dedicated runner
新建 runner：`scripts/run_rank201_utc_clock_paper_runner.py`

最小 live 逻辑：
- 宇宙：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK` perpetual 等权
- 频率：`15m`
- 固定 UTC sleeve：
  - `20:00~21:59 UTC long`
  - `22:00~23:59 UTC short`
- 成本口径：`8 bps round-trip`
- 每次刷新会：
  - 拉取 Binance USDⓈ-M futures `15m` K 线
  - 重建闭合 trade ledger
  - 写出当前 live 仓位快照与各腿盘口 spread
  - 更新 reader-facing paper 页面

### 2) scheduler
已把 systemd unit 安装到 `/etc/systemd/system/` 并完成：
- `systemctl daemon-reload`
- `systemctl enable --now momentum-rank201-paper-refresh.timer`
- `systemctl start momentum-rank201-paper-refresh.service`

timer 当前已进入 active waiting，按 `15m` 节奏在 `:02/:17/:32/:47` 触发。

### 3) first verified run artifacts
首跑成功后已写出：
- 状态：`reports/artifacts/paper_rank201_utc_clock_low_switch/rank201_status.csv`
- state：`reports/artifacts/paper_rank201_utc_clock_low_switch/rank201_state.json`
- ledger：`reports/artifacts/paper_rank201_utc_clock_low_switch/rank201_closed_trades.csv`
- schedule：`reports/artifacts/paper_rank201_utc_clock_low_switch/rank201_daily_schedule.csv`
- recent markout：`reports/artifacts/paper_rank201_utc_clock_low_switch/rank201_recent_markouts.csv`
- 页面：`reports/site/paper/rank201_utc_clock_low_switch.html`

首跑关键快照：
- `last_run_at_utc`: `2026-03-27T22:14:52Z`
- `latest_signal_ts`: `2026-03-27T22:00:00Z`
- 当前 live 仓位：`short`
- 计划平仓：`2026-03-28T00:00:00Z`
- 闭合交易数：`1904`
- 历史累计净收益：`+24.91%`
- 近 30 天累计净收益：`+72.63%`
- 平均单笔净收益：`+1.53 bps`
- 胜率：`47.16%`

## 为什么这一步改变了系统认知
在这轮之前，`Rank 201` 只是“应该进入 paper trade”的 queue-side 判断；
在这轮之后，它已经是一个**有专用 runner、有启用中的 scheduler、且有首跑 runtime artifact 的 live paper sleeve**。

这意味着 `Rank 201` 不该继续挂在模糊的 handoff/queue 口径里，而应直接记为：
> `connected_runner_live`

同时，`Paper launch queue` 也不该再把它视作“等待接线”的头部对象；当前真正的 runtime truth 是：`Rank 200` 与 `Rank 201` 都已经连上 dedicated paper runner。

## 本轮改变系统认知的一句话
`Rank 201 / UTC clock seasonality low-switch schedule` 已完成最小 `launch wiring`：专用 runner、已启用的 systemd timer 与首跑验证都已落地，运行态应从 queue-side 的 `promote_P3` 改写为正式 `connected_runner_live`，不再只是等待 handoff 的纸面 P3。
