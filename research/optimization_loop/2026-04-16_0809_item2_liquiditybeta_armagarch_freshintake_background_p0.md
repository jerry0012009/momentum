# bot3 auto execution log — item2 liquidity-adjusted ARMA-GARCH sign（fresh intake）

- 时间：2026-04-16 08:09 UTC
- 对象：`research/quant_digests/2026-04-16_0639_liquiditybeta-armagarch-ts-alpha.md`
- 执行动作：fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + `Asia/EU/US`），并补 1 个最小 honesty/execution realism 子检查（分钟流动性代理定义与预测时点泄露风险）

## 本轮新增证据
新增最小可复现实验（Binance perp：`BTC/ETH/SOL/XRP`，`15m`，`t+2` 延迟入场，等权组合，统一成本梯度）：
- `reports/artifacts/quant_digests/2026-04-16_liquiditybeta_armagarch_t2_session_cost_summary.csv`
- `reports/artifacts/quant_digests/2026-04-16_liquiditybeta_armagarch_t2_session_cost_summary.json`

组合层结果：
- `t+2 + 4bps`: `gross_bps=-0.03`，`net_bps=-1.13`
- `t+2 + 6bps`: `net_bps=-1.68`
- `t+2 + 8bps`: `net_bps=-2.23`

分时段结果（`net_bps`）：
- `Asia`: `-1.12 / -1.68 / -2.24`（4/6/8bps）
- `EU`: `-0.79 / -1.23 / -1.68`
- `US`: `-1.48 / -2.12 / -2.77`

## 最小 honesty / execution realism 子检查
本轮只补一个决定性检查：
- 将 `mu_hat` 与 `sigma_hat` 统一滞后一根（仅使用 `t-1` 及更早信息）并执行 `t+2` 入场后，费后表现仍全段为负；
- 说明该对象当前不是“因预测时点泄露导致的假阳性”，而是本身在可执行延迟+成本口径下无可复制净优势。

## 判定
`background/P0`（不进入 survivor，不分配 Rank）。

一句会改变系统认知的话：
> `liquidity-adjusted ARMA-GARCH sign` 在统一 `t+2 + 4/6/8bps` 与 `Asia/EU/US` 口径下组合及分时段费后全负，且滞后防泄露检查后结论不变，不具备进入 survivor 的最小可执行 alpha 形态。

## 对 runtime 的写回
- `cycle_plan` item2：`status -> done`
- `cycle_plan` item2：`result -> background/P0` 结论
- `Fresh intake slot.latest_result` / `latest_result_record` 更新为本结论
- `Background pool.latest_parked` / `latest_parked_record` 追加本对象与日志
