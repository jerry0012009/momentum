# bot3 optimization loop — hourly winner-rotation × cohort continuation — background/P0

- 时间：2026-04-23 13:04 UTC
- 执行对象：`research/quant_digests/2026-04-23_1215_hourly-winner-rotation-cohort-alpha.md`
- 对应 cycle_plan 小点：1
- 执行动作：fresh intake first verdict（只补 1 个最小 decisive blocker）

## 本轮要回答的唯一问题
`hourly winner-rotation × 4-asset cohort continuation` 是否在现实换手 / child-entry / 成本口径下，留下至少一个**非单 cohort、非单小时 lucky-run** 的独立 after-cost cross-sectional pocket；若没有，就必须直接收口 `background/P0`。

## 使用证据
- digest：`research/quant_digests/2026-04-23_1215_hourly-winner-rotation-cohort-alpha.md`
- artifact：`jerry/momentum/reports/artifacts/literature/intraday_rotation_repo_probe_summary_2026-04-23.json`
- artifact：`jerry/momentum/reports/artifacts/literature/intraday_rotation_repo_probe_15m_2026-04-23.csv`
- artifact：`jerry/momentum/reports/artifacts/literature/intraday_rotation_repo_probe_5m_2026-04-23.csv`

## 最小 decisive blocker 结果
结论：**没有通过**。

### 1) 15m 原版口径只剩极薄 gross，统一 `8bps round-trip` 后 70/70 组合全部转负
summary 显示：
- `15m combos = 70`
- `positive_combo_ratio = 0.0`
- `median_mean_net_bps = -7.0783`
- 最佳组合 `ETH/SOL/XRP/BNB`：
  - `mean_gross_bps = +3.0528`
  - `mean_net_bps = -4.9472`
  - `cum_net_pct = -21.47%`

这说明即便给它最有利的 ex-post 组合，repo 语义下的 hourly leader rotation 也只留下约 `+3bps/trade` 的薄 gross，远不够覆盖最小统一成本。

### 2) 5m 快一档连毛边都没有，不存在“child 层更好做”的兜底
summary 显示：
- `5m positive_combo_ratio = 0.0`
- `5m median_mean_net_bps = -10.6817`
- 最佳组合 `BNB/ETH/SOL/LINK`：
  - `mean_gross_bps = -0.2498`
  - `mean_net_bps = -8.2498`

因此这条线不能用“父层薄一点、子层执行更快会补回来”来保留 front slot；快一档口径本身就已是 fee trap。

### 3) 不是“少数组合能过费、只是中位数不行”；而是**全组合统一不过费**
`15m` csv 顶部 best combos 全部只有 `~+3bps` 级 gross，而 net 统一落在 `-4.95bps` 到更差；
`5m` csv 顶部 best combos 连 gross 都已经为负。

所以这次 blocker 不是“还差一个执行 realism 子检查”；系统认知已经足够收口为：
- 它当前没有留下独立、可排队的 after-cost winner-rotation pocket；
- 更像 `cross-sectional ranking/router` 底胚，而不是应占用 survivor 的 raw alpha 主语。

## Verdict
**fresh intake first verdict：`background/P0`**

一句会改变系统认知的话：
> `hourly winner-rotation × cohort continuation` 已完成 fresh intake first verdict 并收口 `background/P0`：当前 Binance majors portability 里，`15m` 原版 winner-rotation 最佳 4 币 cohort 也只有约 `+3.05bps/trade` gross、统一 `8bps` 后 70/70 组合全部转负，`5m` 快一档更是连最佳组合 gross 都为负，因此它没有留下非单 cohort、非单小时 lucky-run 的独立 after-cost pocket；当前只保留为 cross-sectional ranking/router 提示，不占用 survivor。

## 为什么本轮不升 `keep_P1`
按 cycle_plan success criterion，只有当“至少一个非单 cohort、非单小时 lucky-run 的 after-cost winner-rotation pocket 明显成立”才允许 `keep_P1`。
本轮最小 blocker 已直接否定该条件：
- `15m`：所有 cohort 统一不过费；
- `5m`：最佳 cohort 连 gross 都不成立；
- 因此不存在可诚实保留的 survivor 候选。

## 对 runtime 的直接影响
- 本小点写回 `done`
- `result` 写成上述 `background/P0` verdict
- 刷新 `Fresh intake slot.latest_result`
- 刷新 `Fresh intake slot.latest_result_record`
- 不分配新 Rank（因为未达到 `keep_P1`）
