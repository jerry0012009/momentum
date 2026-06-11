# bot3 执行日志（Active P2 admission）
- 时间：2026-04-12 18:54 UTC
- 执行槽位：Active P2 slot
- 对象：`Rank 391 / BTC dominance slope × strongest/weakest alt switch`
- 对应小点：`cycle_plan #1`

## 本轮执行小点
按同一可交易口径完成 `effectiveness + cross-asset + time` 三轴补齐，并补 1 条最小 honesty/execution realism 检查，输出单一出口结论。

## 新证据（会改变系统认知）
数据源：
- `reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_detail.csv`
- `reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_alt_frequency.csv`
- 本轮汇总：`reports/artifacts/literature/rank391_p2_admission_summary_2026-04-12.json`

### 1) effectiveness（成本后口径）
- `1.0 bps one-way`：`cumret +1.47%`，`Sharpe 0.33`，`MDD -6.50%`
- `1.5 bps one-way`：`cumret -0.17%`，`Sharpe 0.02`，`MDD -7.49%`
- `2.0 bps one-way`：`cumret -1.78%`，`Sharpe -0.29`，`MDD -8.47%`

结论：该 alpha 在 `~1.5bps` 附近已接近零边际并转负，当前仍未形成“可稳态落地的成本后正收益缓冲”。

### 2) time stability（子区间稳定性）
- 月度（`1.5bps`）共 7 个月，仅 3 个月为正；最差月约 `-2.55%`，最好月约 `+3.40%`
- 半样本（`1.5bps`）：前半 `-1.59%`，后半 `+1.44%`

结论：时间稳定性呈显著漂移与阶段依赖，尚不足以支持直接进 `P3`。

### 3) cross-asset（币种贡献集中度）
- alt 侧活跃暴露占比：DOGE `20.16%`、SOL `17.06%`、XRP `13.95%`、ETH `13.31%`、BNB `9.17%`
- 集中度 `HHI ≈ 0.115`（中等，不是单币极端垄断，但明显偏向 DOGE/SOL/XRP）

结论：cross-asset 不是致命集中崩坏，但收益解释确实偏向少数高 beta alt，需与成本阈值联动观察。

### 4) honesty / execution realism（最小核验）
- 非零换仓时点集中在 `00:00 / 06:00 / 12:00 / 18:00 UTC`（6h 轮换栅格），符合 `15m state -> 6h tradable refresh` 的执行壳设定；未见逐 bar 追单式错配。
- 但在更保守的 `1.5bps one-way` 成本口径下，净值已接近零并微负，说明真实可执行性仍由“能否长期压低有效成本”单点决定。

## 出口结论（单一）
`Rank 391`：`keep_P2`。

## 唯一剩余 blocker（已锁定）
`唯一 decisive blocker = 成本阈值鲁棒性未过`：在 admission 成本口径提升到 `1.5bps one-way` 后，收益已由正转近零/微负，尚不足以支持直接 `promote_P3`。

## 下一步约束
后续若继续保留在 P2，必须只围绕该唯一 blocker 做一次收口验证（不再扩轴）；若仍不能证明 `>=1.5bps` 下稳定为正，应执行 `drop_to_background` 或明确 re-scope，而非开放式续测。
