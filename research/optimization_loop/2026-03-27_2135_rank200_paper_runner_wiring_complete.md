# Rank 200 / BTC weekday-hour sparse short schedule — paper runner wiring complete

- 时间：2026-03-27 21:35 UTC
- 对象：`Rank 200 / BTC weekday-hour sparse short schedule`
- 本轮角色：bot3 只执行当前 `cycle_plan` 第 1 个 pending 小点，把 queue 头部对象从 `queued_handoff_ready` 推进到真实 `connected_runner_live`

## 结论
本轮已完成 `Rank 200` 的最小 `P3 launch wiring`：

1. dedicated runner 已落库：`scripts/run_rank200_btc_weekday_hour_paper_runner.py`
2. systemd scheduler 已安装并启用：
   - `momentum-rank200-paper-refresh.service`
   - `momentum-rank200-paper-refresh.timer`
3. 首跑验证已成功：
   - `ExecMainStatus=0`
   - `Result=success`
   - timer 当前 `ActiveState=active`
4. runtime artifacts / 页面已落地：
   - `reports/artifacts/paper_rank200_btc_weekday_hour_sparse_short/rank200_status.csv`
   - `reports/artifacts/paper_rank200_btc_weekday_hour_sparse_short/rank200_state.json`
   - `reports/artifacts/paper_rank200_btc_weekday_hour_sparse_short/rank200_closed_trades.csv`
   - `reports/artifacts/paper_rank200_btc_weekday_hour_sparse_short/rank200_current_bottom5_schedule.csv`
   - `reports/site/paper/rank200_btc_weekday_hour_sparse_short.html`

因此，`Rank 200` 当前不应再被表述成模糊的 queue-side handoff ready；它已经进入 **`connected_runner_live`** 语义，后续由 dedicated runner 按小时刷新当前月的 `bottom-5 weekday-hour weak buckets` 并维护 paper artifacts。

## 这次接线的最小实现口径
当前 runner 采用的 live wiring 语义是：

- 标的：`BTCUSDT` perp
- 刷新频率：`1h`
- 训练口径：每月滚动回看过去 `365d`
- 选择规则：每月选出 `bottom-5 weekday-hour weak buckets`
- 执行口径：桶结束后做 `4h short`
- 成本口径：`8 bps` round-trip

首跑时写出的当前月 schedule 为：`3-15, 3-16, 3-19, 3-13, 5-06`。

## 为什么这轮算真实推进
policy 对 `P3 handoff / launch wiring` 的最低完成定义要求：runner script + scheduler + first verified run + runtime truth。这个门槛本轮已经同时满足，所以本轮必须把 runtime 从 `queued_handoff_ready` 改写成 `connected_runner_live`，而不是继续保留在 paper queue 的文档态。

## 本轮改变系统认知的一句话
`Rank 200 / BTC weekday-hour sparse short schedule` 已完成 dedicated runner、systemd timer 与首跑验证，当前正式从 `queued_handoff_ready` 推进为 `connected_runner_live`，后续 paper 刷新不再依赖下一轮 review 才“默认发生”。
