# bot3 optimization loop log — microprice/OBI coint perp pairs fresh-intake first verdict（background/P0）

- 时间：2026-04-12 01:16 UTC
- 执行小点：`cycle_plan` #3（`research/quant_digests/2026-04-11_2238_microprice-obi-coint-perp-pairs-alpha.md`）
- 动作：按最小执行现实口径完成 fresh intake first-verdict，优先判定唯一 decisive blocker

## 本轮最小 honesty / execution 子检查
使用已落库 portability artifact：
- `reports/artifacts/literature/statarb_hft_repo_portability_summary_2026-04-11.csv`

在 `|z|>=2` 事件的 `15m signed spread-close mean (bps)` 上，做双腿 roundtrip 成本敏感度快检（每腿每侧成本 `c` bps，则 roundtrip 成本 `4c` bps）：

- AXS/FIL：`10.48 bps`
- ADA/HYPE：`5.95 bps`
- LINK/SOL：`2.69 bps`
- DOGE/HYPE：`2.55 bps`

成本扣减后（15m mean，bps）：
- `c=2.0`：AXS/FIL `+2.48`，ADA/HYPE `-2.05`，LINK/SOL `-5.31`，DOGE/HYPE `-5.45`
- 且唯一仍为正的 AXS/FIL 同时具备明显薄腿约束（AXS 24h quote volume 约 `7.48M`），不满足本轮“可执行优先”前提

## 结论（first verdict）
`microprice/OBI cointegrated perp pairs` 本轮 first-verdict 收口为 **`background/P0`**。

- 结论理由：在可回放 close-proxy 口径下，边际主要集中在薄流动性 pair；对更可执行的 majors-ish / 更厚腿组合，双腿执行成本已系统性吃尽边际。
- 锁定唯一 decisive honesty/execution blocker：**双腿执行成本吃尽边际**（而非协整/对齐泄漏）。

## runtime 写回要点
- `cycle_plan` #3 -> `status: done`
- `cycle_plan` #3 `result` 已写成：该题材成本后边际不足，收口到 `background/P0`
- `Fresh intake slot` 前移到下一个 pending 对象（same-expiry parity 题）
- `Background pool latest_parked` 更新为本对象
