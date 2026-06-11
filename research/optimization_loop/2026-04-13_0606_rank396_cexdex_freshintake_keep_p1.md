# Rank 396｜cexdex funding-arb shell｜fresh intake first verdict（keep_P1）

- 时间：2026-04-13 06:06 UTC
- 执行轮次：bot3 13m auto
- 对象：`research/quant_digests/2026-04-13_0435_cexdex-fundingarb-shell.md`
- 结论：`keep_P1`（分配新正式 Rank：`396`，进入 Surviving candidate）

## 本轮最小检查（含 1 条 honesty / execution realism）

1) 复核现成 portability artifact：
- 文件：`reports/artifacts/literature/funding_cexdex_binance_probe_2026-04-13_summary.csv`
- 在 `funding>=1bps/8h` 口径下：`events=84`，`weighted_mean_gross_bps=+0.5931`，扣 `8bps round-trip` 后 `weighted_mean_net8_bps=-7.4069`，`weighted_winrate_net8=0`。
- 这说明 same-venue（Binance perp-spot）便携版当前不具备费后可交易性，不可直接当作“稳定 carry”。

2) honesty / execution realism 最小子检查：
- 当前证据仅到 public K 线 + funding 历史，仍缺少 cross-venue 可执行链路（同时间戳可成交 quote、对冲腿真实成交代理、withdraw/gas/bridge 时延与成本）的一体化净边际验证。
- 因此“论文摘要中的高收益”不能外推为本 desk 可执行 edge。

## first-verdict 决策

- 不直接打回 `background/P0`：因为该对象提供的是完整 raw-alpha 壳（funding + basis + hedge leg + 风险框架），且 single-venue 否决已经明确把研究焦点收敛到 cross-venue differential 是否能覆盖全摩擦。
- 也不升 `P2`：当前缺唯一 decisive blocker 的验证闭环。

### 唯一 decisive blocker（已锁定）

> **缺少“跨 venue、时间对齐、全摩擦（fee+slippage+gas/withdraw/bridge+latency）后仍为正”的可执行净边际证据链。**

在该 blocker 未被一次最小 follow-up 打穿前，不进入 P2/P3。

## 对 runtime 的直接影响

- 新增正式身份：`Rank 396`
- 层级：fresh intake first verdict -> `keep_P1`
- 槽位迁移：进入 `Surviving candidate slot`（下一步只能做 1 次最小 follow-up，目标即验证上述唯一 blocker）
