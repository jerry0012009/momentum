# Rank 268 survivor follow-up — moving-band basket stat-arb × 线性 inventory shell

- 时间：2026-03-31 14:51 UTC
- 执行轮次：bot3 auto 13m
- 对应 cycle item：`Rank 268 / moving-band basket stat-arb × 线性 inventory shell`
- 结论：`background/P0`

## 本轮只回答的事
`Rank 268` 作为当前唯一合法 survivor，在受控 crypto universe 下做最小 clean-room replication 后，是否还能保留独立可审计的 after-cost 净边；若不能，就要用尽唯一 follow-up 并退出前排。

## 本轮执行
我没有硬抄论文里的凸优化搜索器，也没有偷渡美股日频结果，而是做了一个**保守的、可审计的 proxy replication**：

- 市场：Binance USDⓈ-M futures
- 周期：`15m`
- 受控 universe：`BTC/ETH/BNB/SOL/XRP/DOGE`
- 样本：最近约 `90d`
- 训练 / 换篮节奏：滚动 `30d` 训练、`1d` 重新选 basket
- basket 搜索：只允许 `3/4` 腿、`zero-sum`、等权正负号组合
- 交易壳：`moving midpoint + rolling std`，`entry |z|>0.75`，`exit |z|<0.15`，线性 inventory shell
- 成本：统一按 `4 bps/side` one-way 扣减
- 对照：同宇宙、同 cadence 下的 `best pair z-score` 近邻基线

产物：
- `reports/artifacts/rank268_survivor_followup_20260331_1451/summary.csv`
- `reports/artifacts/rank268_survivor_followup_20260331_1451/window_results.csv`
- `reports/artifacts/rank268_survivor_followup_20260331_1451/meta.json`
- `reports/artifacts/rank268_survivor_followup_20260331_1451/cache/*.csv`

## 最小 replication 结果
### 1) moving-band basket proxy
- `59` 个日度 OOS 窗口
- `sum_test_gross_sum ≈ +0.0523`
- `sum_test_net_sum ≈ -0.1795`
- `win_rate ≈ 23.7%`
- `mean_test_turnover ≈ 9.83`

### 2) best pair z-score 对照
- `59` 个日度 OOS 窗口
- `sum_test_gross_sum ≈ -0.0217`
- `sum_test_net_sum ≈ -0.2453`
- `win_rate ≈ 33.9%`
- `mean_test_turnover ≈ 9.48`

### 3) 与既有 PCA residual 基线的关系
此前已存在的 `PCA residual + OU` 最小快检（`reports/artifacts/quant_digests/pca_ou_statarb_probe_20260324_1103/summary.csv`）显示：
- gross 有小幅正边，
- 但在 `4 bps one-way` 下净值同样被成本打穿。

因此，这轮 `Rank 268` follow-up 最诚实的新信息不是“basket 比所有近邻都强到足以升级”，而是：
**它在受控 crypto majors 上确实比普通 pair 近邻更接近可用，但 after-cost 仍明显不成立，且没有强到足以压过我们已知的 PCA residual 成本断崖。**

## Verdict
`Rank 268` 的唯一 survivor follow-up 已用尽。当前最诚实结论是：

- 它**没有**在受控 crypto universe 下复现出足够可信的 after-cost 净边；
- 虽然 proxy basket 结果比 pair 对照略好，但仍明显为负，说明当前保留下来的更多是“研究框架价值”，不是可升级的前排交易对象；
- 因此本轮应把 `Rank 268` **移回 `background/P0`**，而不是继续占用前排预算。

## 会改变系统认知的一句话
`Rank 268` 的 moving-band basket proxy 在 Binance 15m liquid majors 上虽比 pair 近邻稍好，但统一 `4 bps/side` 后仍明显为负，未能证明独立可迁移的 after-cost 净边；唯一 survivor follow-up 已用尽，故本轮正式退出前排并回 `background/P0`。
