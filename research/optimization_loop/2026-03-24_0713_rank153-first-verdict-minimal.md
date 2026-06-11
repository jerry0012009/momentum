# 2026-03-24 07:13 UTC · Rank 153 / liquidation consensus cascade first verdict（minimal）

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 本轮路径：`Scout`
- 本轮认领动作：`TODO.md -> TRADING DESK BOARD -> Next 3 bot3 runs #1`
- 执行范围：只推进 **1 个主点 + 1 个紧邻子点**

## 0. 本轮主点
对 `Rank 153 / liquidation consensus cascade continuation alpha` 做一次最小 first verdict：
- symbols：`BTC / ETH`
- compare：`funding+OI` vs `funding+OI+cluster`
- exits：`continuation` vs `reversal`
- costs：`6 / 12 / 20 bps round-trip`
- metrics：`event_count / mean_net_bps / MFE / MAE`

## 1. 这轮实际交付
新增 runner：
- `scripts/build_rank153_first_verdict_minimal.py`

生成 artifact：
- `reports/artifacts/scout_rank153_liquidation_consensus_cascade_15m/sample_meta.csv`
- `reports/artifacts/scout_rank153_liquidation_consensus_cascade_15m/events.csv`
- `reports/artifacts/scout_rank153_liquidation_consensus_cascade_15m/trades.csv`
- `reports/artifacts/scout_rank153_liquidation_consensus_cascade_15m/asset_summary.csv`
- `reports/artifacts/scout_rank153_liquidation_consensus_cascade_15m/combo_summary.csv`
- `reports/artifacts/scout_rank153_liquidation_consensus_cascade_15m/scorecard.csv`
- `reports/artifacts/scout_rank153_liquidation_consensus_cascade_15m/summary.csv`

reader-facing 页面：
- `reports/site/factors/scout_rank153_liquidation_consensus_cascade_15m/report.html`
- `reports/site/reading/repo_scout/rank153_liquidation_consensus_cascade_first_verdict.html`

## 2. 冻结口径与诚实说明
这轮为了先回答 desk 的 first-verdict 问题，使用的是：
- 本地 `15m` bar cache
- 本地已缓存的 Binance `funding` / `5m OI` 数据（复用 `rank138` 先前落盘缓存）
- `cluster` 暂时不用真实 liquidation heatmap，而是用 **BTC/ETH 同向 45m shock 的 public-proxy 共振** 代替

因此，这轮结论只够回答：
- `park / keep_P1 / promote_P2`

**不够**宣称：
- 已完整复现 source repo 的 liquidation-cluster 逻辑
- 已证明真实 whale/liquidation cluster 对 alpha 有稳定增益

## 3. 最小结果
### 3.1 组合层（核心格）
- `funding+OI / continuation / 15m / 12bps`：`171` events，`mean_net_bps = -12.02`
- `funding+OI / reversal / 15m / 12bps`：`171` events，`mean_net_bps = -11.98`
- `funding+OI+cluster(proxy) / continuation / 30m / 12bps`：`20` events，`mean_net_bps = -2.36`
- `funding+OI+cluster(proxy) / continuation / 30m / 6bps`：`20` events，`mean_net_bps = +3.64`

### 3.2 直接 desk 结论
- 目前最优格并没有在 desk 指定的主压力格（`12bps`）上站住。
- `funding+OI` 本体在 `continuation` 与 `reversal` 上几乎等价地为负，说明这轮 public-data 版本还没证明出明确方向性 edge。
- `cluster(proxy)` 只在 `30m / 6bps` 这个较宽松角落出现正值，但一加到 `12bps` 就回到负值，且样本只有 `20` 个，不够诚实。

## 4. 简短 scorecard
- `usefulness = 0/3`
- `time_stability = 1/3`
- `cross_asset_stability = 2/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `recommended_action = park`
- `main_weakness = cluster 目前只是本地 public-proxy 共振替身，不是真实 liquidation heatmap；因此 first verdict 只够决定 keep_P1 / park`

## 5. 一句话 result
`Rank 153` 的最小 first verdict 已完成：在 BTC/ETH、continuation vs reversal、6/12/20bps 的固定口径下，当前 public-data 版 `funding+OI` 与 `funding+OI+cluster(proxy)` 都没能在 12bps 成本下给出足够诚实的正期望，因此本轮结论是 **park，而不是 keep_P1 / promote_P2**。
