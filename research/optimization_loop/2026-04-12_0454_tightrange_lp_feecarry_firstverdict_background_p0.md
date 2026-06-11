# bot3 optimization loop — tight-range LP fee carry × perp hedge first-verdict（background/P0）

- Time (UTC): 2026-04-12 04:54
- Cycle item: `cycle_plan` #1
- Target: `research/quant_digests/2026-04-11_1750_tightrange-lp-feecarry-perphedge-shell.md`

## 执行动作
按 `fees+滑点+funding` 最小统一口径重估净 carry，并补 1 条 honesty/execution realism 子检查（资金费窗口与可成交窗口是否同窗）。

## 证据（最小 decisive）
数据源：
- `reports/artifacts/literature/uniswapv3_hedged_lp_probe_summary_2026-04-11.csv`
- `reports/artifacts/literature/uniswapv3_hedged_lp_probe_band_resets_2026-04-11.csv`

关键数：
1. `pool_naive_fee_bps_per_day = 1.41989 bps/day`
2. `band_2pct_resets_per_day = 1.9726/day`
3. 由 (1)/(2) 得到可承受的**每次 reset 全部摩擦预算上限**约 `0.72 bps/reset`（还未计持续 hedge refresh、资金占用与链上尾部冲击）
4. `band_1pct_resets_per_day = 4.8452/day` 时预算仅约 `0.29 bps/reset`

结论含义：在 tight-range 执行壳下，净 carry 要为正，单次 recenter+对冲的 all-in 成本必须压到亚-bps 级别；该阈值对真实链上+跨 venue 执行不具稳健余量，成本后边际不足。

## honesty / execution realism 子检查
- funding 统计窗来自 `200` 个 `8h` 点（更长历史窗），执行可成交口径来自最近 `1500` 根 `5m` K（短窗）。
- 因窗口不同步，funding 只能作为弱辅助项，不能被当成主收益腿来抵消 tight-range 高频重平衡成本。
- 在不依赖 funding boost 的保守口径下，净 carry blocker 仍成立。

## first verdict
- Verdict: `background/P0`
- Decisive blocker（唯一）: `净 carry 不足覆盖成本`
- 处理：该 fresh intake 不进入 `P1`，转入 background pool。
