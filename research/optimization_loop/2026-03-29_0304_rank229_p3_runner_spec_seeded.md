# Rank 229 / ETH-led abnormal-day continuation (session-defined) — P3 launch wiring 第 1 步：runner + frozen spec 落库

- Time: 2026-03-29 03:04 UTC
- Target: `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- Step type: `P3 launch wiring` / `runner + frozen spec`
- Verdict: `done`

## 本轮只执行这一小点
按照当前 `cycle_plan`，这轮不做 scheduler 安装，也不做 first verified run；只把 `Rank 229` 已经通过 admission 的 ETH 主 spec 明确冻结成 dedicated runner 可读的落库产物，确保它不再停留在“等后续人自己猜该怎么接线”的模糊状态。

## 新增落库产物
### 1) Dedicated runner
- `scripts/run_rank229_eth_abnormal_day_paper_runner.py`

这个 runner 明确绑定到 `Rank 229`，并且只认这一条 frozen queue-side paper spec：
- Symbol: `ETHUSDT` perpetual
- Venue: `Binance Futures`
- Bar: `5m`
- Session offset: `20h`
- Threshold: `k = 1.25 * sigma_session`
- Minimum remaining bars: `12`
- Entry: `next-bar open`
- Exit: `session close`
- Cost: `12 bps round-trip`

它当前做的事情是：
- 从 `reports/artifacts/rank229_p2_admission_time_parameter/trade_level.csv` 读取已通过 admission 的 frozen trade seed；
- 过滤出 `offset 20h / k=1.25 / M>=12` 这一条批准过的主 ridge；
- 写出 runner-grade artifact：
  - `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_closed_trades.csv`
  - `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_status.csv`
  - `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_state.json`
  - `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_last_run_summary.json`
  - `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_current_signal_frame.csv`
  - `reports/site/paper/rank229_eth_abnormal_day.html`

### 2) Frozen launch spec
- `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_frozen_launch_spec.json`
- `reports/artifacts/paper_rank229_eth_abnormal_day/rank229_frozen_launch_spec.md`

这里把 queue-side paper launch 需要冻结的运行真相写死了，不再让下一步 scheduler/handoff 自己从旧 admission 文档里猜：
- 主 spec 选用最厚、且 time/parameter admission 已通过的 ETH ridge：
  - `offset 20h / k=1.25 / M>=12`
  - `trades = 90`
  - `gross = +98.69 bps`
  - `net-12 = +86.69 bps`
  - `halves = 全正`
  - `thirds = 3/3 为正`
- 同时保留保守备选：`offset 0h / k=1.75 / M>=12`，但只作为 backup，不取代主 spec。

## 验证结果
已执行：

```bash
python3 /root/clawd/jerry/momentum/scripts/run_rank229_eth_abnormal_day_paper_runner.py --init-from-now
```

运行成功，runner 已能把 frozen seed 写成可供后续 scheduler 调起的 paper artifact，关键输出包括：
- `closed_trades_total = 90`
- `mean_net_bps = 86.68887720155885`
- `wiring_status = scheduler_ready_runner_seeded`

这一步的诚实表述是：
> `Rank 229` 的 dedicated runner 与 frozen launch spec 已经落库，并且 runner 已成功把已批准的 ETH frozen seed 写成 paper-grade artifact；对象现在从“等待接线”前进到“scheduler-ready”，下一步只剩 scheduler + first verified run，而不是继续开放式研究。

## Runtime writeback
### Paper launch queue
- `current_target` 维持：`Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- `latest_result` 更新为：`Rank 229` 的 dedicated runner 与 frozen launch spec 已落库，且已成功把 `offset 20h / k=1.25 / M>=12` 的 ETH approved seed 写成 paper-grade artifact；对象现处于 `scheduler_ready_runner_seeded`，下一步应直接做 scheduler + first verified run，而不是回到开放式研究
- `latest_result_record` 指向本文

### cycle_plan
- 第 1 项写为 `done`
- `result` 写为：`Rank 229` 的 dedicated runner 与 frozen launch spec 已落库，approved ETH ridge 已被写成 scheduler-ready 的 paper artifact，queue 状态从“等待接线”推进到 `scheduler_ready_runner_seeded`

## 一句话结果
`Rank 229` 已经不再只是 queue 里的研究结论：本轮把 ETH 主 spec 冻结成了 dedicated runner + frozen launch spec，并成功 seed 出一套 scheduler-ready 的 paper artifact，所以下一步应直接做 scheduler 安装与首跑验证。