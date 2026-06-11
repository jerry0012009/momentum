# bot3 auto execution log — item1 cross-venue perp-perp spread hysteresis shell（fresh intake）

- 时间：2026-04-16 09:50 UTC
- 对象：`research/quant_digests/2026-04-16_0837_crossvenue-perpperp-spread-hysteresis-shell.md`
- 执行动作：fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + `Asia/EU/US`），并补 1 个最小 honesty/execution realism 子检查（跨 venue 触发到成交的时间错位 + 队列时滞惩罚）

## 本轮新增证据
新增最小可复现实验（Bybit/Binance perp close proxy：`BTC/ETH/SOL`，`5m`，`entry=5bps / exit=1.5bps / max_hold=2h`，`t+2` 延迟执行）：
- `reports/artifacts/quant_digests/2026-04-16_crossvenue_perpperp_hysteresis_t2_session_cost_summary.csv`
- `reports/artifacts/quant_digests/2026-04-16_crossvenue_perpperp_hysteresis_t2_session_cost_summary.json`

组合层结果（ALL_EQ，baseline `t+2`）：
- `4bps`: `gross_bps=+1.197`，`net_bps=-2.803`
- `6bps`: `net_bps=-4.803`
- `8bps`: `net_bps=-6.803`

分时段（baseline）可成交事件仅在 `EU` 触发，且同梯度费后均为负；`Asia/US` 本样本窗口无可成交事件。

## 最小 honesty / execution realism 子检查
本轮仅补一个决定性 realism 检查：
- 在同一阈值与成本口径下，把执行延迟从 `t+2` 提高到 `t+3`，并加入每笔 `1bps` 队列/撮合时滞惩罚。
- 结果：组合层 `net_bps=-5.005/-7.005/-9.005`（4/6/8bps），较 baseline 进一步恶化。

## 判定
`background/P0`（不进入 survivor，不分配 Rank）。

一句会改变系统认知的话：
> `cross-venue perp-perp spread hysteresis shell` 在统一 `t+2 + 4/6/8bps` 口径下仅出现稀疏可成交事件且费后为负，加入最小跨 venue 时间错位/队列时滞 realism 后净值进一步下探，当前不具备进入 survivor 的可执行 alpha 形态。

## 对 runtime 的写回
- `cycle_plan` item1：`status -> done`
- `cycle_plan` item1：`result -> background/P0` 结论
- `Fresh intake slot.latest_result` / `latest_result_record` 更新为本结论
- `Background pool.latest_parked` / `latest_parked_record` 追加本对象与日志
