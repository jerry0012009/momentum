# 2026-03-24 06:38 UTC · Rank 153 / liquidation consensus cascade fresh intake

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 本轮路径：`Fresh intake`
- 本轮动作：只做 **1 个主点 + 1 个紧邻子点**

## 0. 判路
- `Paper launch queue = none`
- `Surviving candidate slot = none`
- `Active P2 slot = none`
- `Fresh intake slot = open`
- 因此按 authoritative policy/state，本轮合法主动作是：认领 1 条新的候选并压成可验证的 intake 卡。

## 1. 本轮主点
### 主点
- **`Rank 153 / liquidation consensus cascade continuation alpha`**

这轮选择它，而不是继续翻旧 interrupt/reserve 的原因：
1. 它是新的 **standalone raw alpha**，不是旧链路残留维护；
2. 有完整可翻译的 entry/exit/risk 骨架，能直接进入 desk 的 first-verdict 缩版；
3. 它补的是 `crowding -> forced flow` 家族，和近期 lead-lag / basis / xs 线互补。

## 2. 紧邻子点
### 紧邻子点：下一轮最小 decisive verdict 应如何收紧？
结论：**只允许做 1 次 BTC/ETH 缩版 first verdict，不扩成全市场。**

冻结口径：
- symbols：`BTC / ETH`
- signal：`5m`
- hold：`15m / 30m`
- compare：`funding+OI` vs `funding+OI+cluster`
- exits：`continuation` vs `reversal`
- costs：`6 / 12 / 20 bps round-trip`
- metrics：`event_count / mean_net_bps / MFE / MAE`

## 3. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 2/3`
- `recommended_action = keep_P1`
- `main_weakness = cluster 增益与成本后生存性仍未被本地 clean replication 证实`

## 4. 本轮交付
- artifact：`reports/artifacts/literature/scout_rank153_liquidation_consensus_cascade_source_intake_card.csv`
- page：`reports/site/reading/repo_scout/rank153_liquidation_consensus_cascade_source_intake.html`

## 5. 一句话结论
`Rank 153` 值得进入 fresh intake 队列，但当前最诚实位置仍是 **keep_P1 的 raw-alpha 候选**；下一轮只配拿一次缩版 A/B + 成本压力 first verdict。
