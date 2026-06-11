# Rank 386 — SOL retail-vs-top account divergence fresh intake first-verdict（keep_P1）

- 时间：2026-04-12 05:27 UTC
- 执行器：bot3
- 对象：`research/quant_digests/2026-04-12_0440_sol-retailtop-account-divergence-alpha.md`
- 结论：`keep_P1`（分配正式 `Rank 386`，进入 Surviving candidate slot）

## 本轮最小复核（统一口径）
基于现有 portability artifact：
- `reports/artifacts/literature/lsr_account_divergence_probe_2026-04-12/summary.csv`
- `reports/artifacts/literature/lsr_account_divergence_probe_2026-04-12/detail.csv`

对 `SOLUSDT` 的 `spread_z = z(log(globalLSR),48)-z(log(topLSR),48)` 做 long-only 触发复核：
- `spread_z < -1.5`：`n=197`，`30m mean=+13.45 bps`，`60m mean=+16.29 bps`，按 roundtrip `8 bps` 后分别约 `+5.45 / +8.29 bps`
- `spread_z < -2.0`：`n=106`，`30m mean=+14.88 bps`，`60m mean=+31.01 bps`，net 约 `+6.88 / +23.01 bps`
- `spread_z < -2.5`：`n=64`，`30m mean=+16.14 bps`，`60m mean=+48.88 bps`，net 约 `+8.14 / +40.88 bps`

first-verdict 口径下，成本后边际为正，未触发 `background/P0` 所需的“单一决定性致命缺陷”。

## honesty / execution realism 最小子检查（本小点允许的 1 条）
检查项：排除“账号分层标签未来信息泄漏”作为主 blocker。

结论：本策略直接使用 Binance 同步发布的 `globalLongShortAccountRatio` 与 `topLongShortAccountRatio` 当期观测值构造 spread；标签并非回填的未来分类字段。当前未发现“由标签定义本身导致的前视泄漏”证据，因此**不构成**本轮 decisive blocker。

## 本轮判定
- 决策：`keep_P1`
- Rank：分配下一个未使用整数 `Rank 386`
- 系统认知更新（一句话）：
  - `Rank 386`：SOL retail-more-short-than-top divergence 在统一 8bps 摩擦口径下仍保留正净边际，且未发现标签前视泄漏证据，first-verdict 保持 `P1` 并进入 survivor 唯一 follow-up 阶段。

## 下一步（不在本轮执行）
按 survivor 唯一预算做 1 次最小 decisive follow-up，优先验证该边际是否仅集中于短样本单一波动段。