# PCA common-factor residual overextension × zero-cross fade — fresh intake first verdict (`background/P0`)

- 时间：2026-04-21 22:49 UTC
- 对象：`research/quant_digests/2026-04-21_2120_pca-eigenportfolio-residual-fade-alpha.md`
- 槽位：Fresh intake slot（conditional fresh intake；第 1 项已收口 `background/P0`，因此本轮执行第 2 项）
- 结论：`background/P0`

## 本轮只回答的最小 decisive blocker
验证 digest 自己点名的 frontier：`15m parent residual fade` 在 **更高 entry band / 更慢 exit / 更长 hold** 下，能否把原先 “gross positive but net negative” 的薄边，转成至少一个 **非单币、非单窗** 的 after-cost pocket。

## 使用证据
1. 现成 digest artifacts：
   - `reports/artifacts/quant_digests/pca_statarb_probe_summary_2026-04-21.csv`
   - `reports/artifacts/quant_digests/pca_statarb_probe_detail_2026-04-21.csv`
2. 本轮最小 frontier 扫描：
   - `reports/artifacts/quant_digests/pca_statarb_frontier_scan_2026-04-21.csv`
3. 复用脚本骨架：
   - `tmp_pca_statarb_probe.py`

## 关键结果
### 1) digest 原始 probe 先验
原始 `15m/5m` probe 虽都有 gross 正边：
- `15m`: `trade_count=580`, `gross_mean_bps/trade=+2.28`, `net_mean_bps/trade=-5.72`, `avg_hold≈1.38 bars`
- `5m`: `trade_count=494`, `gross_mean_bps/trade=+1.07`, `net_mean_bps/trade=-6.93`, `avg_hold≈1.45 bars`

说明 base alpha 方向感存在，但默认 `entry/exit` 明显太快，统一 `8bps` 后单笔厚度不够。

### 2) 本轮 frontier 扫描没有把它救成可保留 survivor
对 `15m parent residual fade` 扫描：
- `entry_z ∈ {2.0, 2.5, 3.0}`
- `exit ∈ {0.5 回中性带, 0 轴, opposite-cross}`
- `max_hold ∈ {8,16,32}`
- 统一 roundtrip cost：`8bps`

最优 after-cost 组合是：
- `entry_z=2.0`, `exit=opposite-cross`, `max_hold=8`
- `trades=509`
- `gross_mean_bps=+3.92`
- `net_mean_bps=-4.08`
- `avg_hold≈6.66 bars`
- `pos_symbols=3`
- `pos_months=0`

其余更慢 exit / 更高 band 也没有翻正：
- `entry_z=2.0`, `exit=0`, `max_hold=8/16/32`：`net_mean_bps≈-5.31`
- `entry_z=2.5`, `exit=0.5`, `max_hold=8/16/32`：`net_mean_bps≈-6.34`
- `entry_z=3.0`, `exit=0.5`, `max_hold=8`：`gross` 已经转负，`net_mean_bps≈-8.55`

### 3) 非单窗条件也没过
这轮样本都落在最近单一 `2026-04` 窗口，frontier 表里 `pos_months=0`；即便某些 symbol（如 `XRP` / `DOGE`）在个别参数下有正均值，也没有形成至少两个时间窗共同支撑的 after-cost pocket。

## first verdict
`PCA common-factor residual overextension × zero-cross fade` 没有在本轮允许的最小 frontier（更高 entry band / 更慢 exit / 更长 hold）里，把 digest 中的薄 gross edge 转成统一 `8bps` 成本后仍为正、且不是单币/单窗支撑的 after-cost pocket；因此它当前更像可服务其他 RV / stat-arb 研究的 shared parent signal / selector，而不是值得前排保留的独立 fresh intake，本轮直接收口 `background/P0`。

## 对 runtime 的直接影响
- Fresh intake 当前对象完成 first verdict：`background/P0`
- 不分配新 Rank（未达到 `keep_P1`）
- Fresh intake 槽按 cycle_plan 条件切到下一条：`research/quant_digests/2026-04-21_2154_passivbot-forager-grid-bounce-alpha.md`
