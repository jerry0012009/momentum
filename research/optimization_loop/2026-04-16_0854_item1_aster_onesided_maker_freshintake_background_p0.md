# bot3 auto execution log — item1 Aster one-sided Avellaneda maker shell（fresh intake）

- 时间：2026-04-16 08:54 UTC
- 对象：`research/quant_digests/2026-04-16_0756_aster-onesided-avellaneda-maker-shell.md`
- 执行动作：fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + `Asia/EU/US`），并补 1 个最小 honesty/execution realism 子检查（maker-only 假设下成交概率漂移与排队/撤单时滞）

## 本轮新增证据
新增最小可复现实验（Binance perp proxy：`BTC/ETH/SOL/XRP`，`5m`，supertrend one-sided 状态机，`t+2` 延迟入场，统一成本梯度）：
- `reports/artifacts/quant_digests/2026-04-16_aster_onesided_maker_t2_session_cost_summary.csv`
- `reports/artifacts/quant_digests/2026-04-16_aster_onesided_maker_t2_session_cost_summary.json`

组合层结果（ALL_EQ，baseline）：
- `t+2 + 4bps`: `gross_bps=+0.084`，`net_bps=-0.117`
- `t+2 + 6bps`: `net_bps=-0.218`
- `t+2 + 8bps`: `net_bps=-0.318`

分时段结果（baseline，`net_bps`）：
- `Asia`: `-0.087 / -0.193 / -0.298`（4/6/8bps）
- `EU`: `-0.152 / -0.246 / -0.340`
- `US`: `-0.114 / -0.215 / -0.315`

## 最小 honesty / execution realism 子检查
本轮只补一个决定性检查：
- 在同一信号与成本口径下引入 maker 执行现实化约束（`fill_q=70%` + 每次换边 `0.6bps` 撤单/排队时滞惩罚）；
- 结果：`t+2 + 4/6/8bps` 组合层 `net_bps=-0.158/-0.258/-0.359`，较 baseline 进一步恶化，说明结论不依赖理想化成交假设。

## 判定
`background/P0`（不进入 survivor，不分配 Rank）。

一句会改变系统认知的话：
> `Aster one-sided Avellaneda maker shell` 在统一 `t+2 + 4/6/8bps` 与 `Asia/EU/US` 口径下已呈稳定费后负值，且加入成交概率/排队时滞 realism 后净值进一步下探，不具备进入 survivor 的最小可执行 alpha 形态。

## 对 runtime 的写回
- `cycle_plan` item1：`status -> done`
- `cycle_plan` item1：`result -> background/P0` 结论
- `Fresh intake slot.latest_result` / `latest_result_record` 更新为本结论
- `Background pool.latest_parked` / `latest_parked_record` 追加本对象与日志
