# bot3 auto execution log — item1 correlation-first pair admission（fresh intake）

- 时间：2026-04-16 07:23 UTC
- 对象：`research/quant_digests/2026-04-16_0718_correlationfirst-zscore-futurespairs-alpha.md`
- 执行动作：fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + `Asia/EU/US`），并补 1 个最小 honesty/execution realism 子检查（高相关非协整漂移 + 双腿可成交同步）

## 本轮新增证据
在既有 probe 的基础上，补做最小 `t+2` 延迟入场（2 bar）与分时段成本口径验证，产出：
- `reports/artifacts/quant_digests/2026-04-16_correlation_zscore_pairs_t2_session_cost_summary.csv`
- `reports/artifacts/quant_digests/2026-04-16_correlation_zscore_pairs_t2_session_cost_summary.json`

关键结果（组合层）：
- `t+2 + 4bps`: `net_bps=-5.97`，`cum_net_pct=-19.44%`
- `t+2 + 6bps`: `net_bps=-7.97`，`cum_net_pct=-25.06%`
- `t+2 + 8bps`: `net_bps=-9.97`，`cum_net_pct=-30.30%`

分时段：
- `Asia` 与 `US` 在 `4/6/8bps` 全部显著负值；
- `EU` 仅在 `4/6bps` 为正，`8bps` 已转负（`net_bps=-0.23`）。

## 判定
`background/P0`（不进入 survivor，不分配 Rank）。

一句会改变系统认知的话：
> 该 `correlation-first pair admission × ratio z-score fade` 在统一 `t+2` 延迟与 `4/6/8bps` 成本下组合与分时段均未形成可复制费后 pocket，且“高相关≠可回复协整 + 双腿同步成交摩擦”是当前唯一且决定性的 execution realism blocker。

## 对 runtime 的写回
- `cycle_plan` item1：`status -> done`
- `cycle_plan` item1：`result -> background/P0` 结论
- `Fresh intake slot.latest_result` / `latest_result_record` 更新为本结论
- `Background pool.latest_parked` / `latest_parked_record` 追加本对象与日志
