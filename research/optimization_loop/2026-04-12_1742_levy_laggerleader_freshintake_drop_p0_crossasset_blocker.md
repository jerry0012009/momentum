# bot3 执行日志｜levy-hermitian lagger-leader catch-up fresh intake first verdict

- 时间：2026-04-12 17:42 UTC
- 执行小点：`cycle_plan` #2（`research/quant_digests/2026-04-12_1436_levy-hermitian-lagger-leader-catchup-alpha.md`）
- 目标：在最小跨标的口径下给出 fresh intake first verdict，并补 1 条 delayed-confirmation / leakage honesty 子检查

## 本轮最小证据

1) 复核既有 portability 结果（15m lagger-vs-leader）
- artifact: `reports/artifacts/literature/hyperliquid_levy_laggervsleader_15m_probe_detail_2026-04-12.csv`
- 样本事件数：4283
- 立即执行口径均值：
  - horizon=1: `+0.263 bps`
  - horizon=2: `+0.431 bps`
  - horizon=4: `+0.435 bps`

2) honesty 子检查（delayed-confirmation / leakage）
- 用同一明细做 `delay+1` 近似核验：`(h2 - h1)` 作为“延后一根再进、持有一根”
- 结果：`+0.168 bps`（仍为正，但明显变薄）
- 解释：未观察到“只在信号当根成立、延后一根即符号翻转”的泄漏型失真；该对象本轮 blocker 不落在 `honesty 失真`。

3) 跨标的复现性快速检查
- 在 `horizon=2` 下按 leaders/followers 组合分组：`1059` 个组合里仅 `562` 个均值为正；高频组合中多组均值显著为负（如 `DOGE,XRP|SOL,BNB`、`XRP,DOGE|BTC,ETH`）。
- 说明正边际依赖子集组合与时段，难形成稳定、可迁移的最小跨标的 first verdict。

## 结论（本小点）

- first verdict：`background/P0`
- 唯一 decisive blocker：`跨资产不可复现`
- 一句话：**levy-hermitian lagger-leader catch-up 在当前最小跨标的口径下未形成稳健可复现边际；honesty 子检查未见决定性 leakage，但不改变其跨资产复现不足的主结论。**

## 回写动作

- 更新 `docs/BOT2_BOT3_STATE.md`：
  - `cycle_plan` #2 -> `status: done`
  - `cycle_plan` #2 -> 写入会改变系统认知的 `result`
  - `Fresh intake slot` 最新结论与记录更新到本日志
  - `Background pool` 最新 parked 更新到本对象
