# Rank 139 · residual-window rerun (`T+3 -> T+8` style)

## 为什么重跑
此前 `Rank 139` 的 clean replication 用“前 45m 路径分组”去比较“包含前 45m 在内的整段 8-bar 收益”，存在明显窗口重叠。

本轮按更严格口径重跑：
- **分组逻辑不变**：仍用 entry 后前 `45m` 的 1m 路径判定 `same_dir_first / opp_dir_first / no_event_timeout`
- **收益评估改为残余区间**：从 `latency_end`（约 `T+3`）到原 exit（约 `T+8`）的收益

## 结果摘要（全市场汇总）
### baseline
- trades = `141`
- `mean_net@6bps = -0.0321%`
- `positive_ratio_net = 41.13%`

### best arm after rerun
- `thr_mult = 0.8`
- `arm = veto_opp_dir`
- trades = `70`
- retention = `49.65%`
- `mean_net@6bps = +0.0474%`
- `positive_ratio_net = 37.14%`

### confirm_same_dir_only @ 0.8
- trades = `43`
- retention = `30.50%`
- `mean_net@6bps = +0.0206%`
- `positive_ratio_net = 30.23%`

## 对比旧口径后的判断
旧口径下，`confirm_same_dir_only @ 0.8` 看起来很强：
- `mean_net@6bps ≈ +0.5363%`
- `positive_ratio_net ≈ 60.5%`

改成 `T+3 -> T+8` 残余收益后：
- 优势**明显缩小**
- `confirm_same_dir_only` 不再像一个强 filter
- 仅 `veto_opp_dir @ 0.8` 还保留了**很弱但略正**的残余 uplift

## 当前结论
**Rank 139 仍有“早期路径可能有信息量”的迹象，但在去掉重叠窗口后，证据强度从“强 filter 候选”降到了“弱 residual effect / 需谨慎解释”。**

更具体地说：
- 现在还能勉强成立的是：`opp_dir_first` 可能确实是一个坏信号，剔掉它后残余收益略有改善；
- 但 `same_dir_first` 不再提供足够强的可执行证据，不能再把它讲成一个强 confirmation filter。

## 暂时建议
- **不要**把当前 `Rank 139` 作为“已被干净证明的 live filter”来叙述；
- 若后续继续研究，优先保留的方向应是：
  - `veto_opp_dir`（坏单否决）
  - 而不是 `confirm_same_dir_only`（强确认放行）
- 在没有专门对 `32b` 做同口径 residual / executable 验证前，**不建议**直接接到 live 仓位管理里。

## 产物
- `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
- `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/trade_log.csv`
- `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`
- `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_monitoring_board.html`
