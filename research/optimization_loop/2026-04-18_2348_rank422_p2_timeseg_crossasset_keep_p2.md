# Rank 422 P2 admission：time stability / cross-asset stability

- Time: 2026-04-18 23:48 UTC
- Target: `Rank 422 / 21:00–23:00 UTC fixed-window drift`
- Action: 只执行本轮 `P2 admission` 的 time stability / cross-asset stability 主结论轮；把已确认的 `EW5(BTC/ETH/SOL/BNB/DOGE)` + `21:15 delay-one-bar` 版本压到跨阶段与单币分布上，直接回答这条 time-of-day alpha 是否仍像一个跨阶段、非单段样本驱动的 after-cost pocket。

## 使用的现成 artifact
- `reports/artifacts/quant_digests/2026-04-18_tod_21_23_utc_probe_events.csv`
- `reports/artifacts/quant_digests/2026-04-18_tod_21_23_utc_probe_summary.csv`
- 上一轮 admission 前置：`research/optimization_loop/2026-04-18_2254_rank422_survivor_followup_promote_p2_basket_childentry.md`

## 最小检查
本轮不再重做同一维度的 gross 证明，只回答两件事：
1. `EW5` 是否主要靠单一时间段/少数月份支撑；
2. 单币层是否出现“只有 1~2 个币真有效，其余只是陪跑”。

### 1) time stability：不是全年每段都一样强，但不是单月幻觉
把 `EW5` 的日度 `21:15 -> 23:00` gross bps 序列按时间顺序切成 4 个等长分段（约各 `91` 天）：

- Segment 1: `mean ≈ +14.40bps/day`，`win_rate ≈ 47.3%`
- Segment 2: `mean ≈ +13.99bps/day`，`win_rate ≈ 64.8%`
- Segment 3: `mean ≈ +23.44bps/day`，`win_rate ≈ 64.8%`
- Segment 4: `mean ≈ +5.05bps/day`，`win_rate ≈ 55.4%`

结论：
- 强度明显有阶段波动，最近一段显著变弱；
- 但四段 **均值仍全部为正**，没有出现后半程系统性翻负；
- 月度层面共 `13` 个月里 `12` 个月均值为正，唯一显著负月为 `2025-10 (-6.66bps/day)`；`2026-03` 也已压到几乎走平（`+0.18bps/day`）。

因此它不能被描述成“稳定匀速”的全天候口袋，但也不是只靠最近某一小段样本硬撑出来的单段幻觉；更像 **存在 regime 起伏的 recurring session pocket**。

### 2) cross-asset stability：不是单币撑起，五个币都保留正向均值
`EW5` 单币总体均值 / 胜率：

- `BTC`: `+10.10bps/day`，`win_rate ≈ 54.5%`
- `ETH`: `+17.43bps/day`，`win_rate ≈ 57.8%`
- `SOL`: `+13.39bps/day`，`win_rate ≈ 58.4%`
- `BNB`: `+12.51bps/day`，`win_rate ≈ 59.7%`
- `DOGE`: `+17.55bps/day`，`win_rate ≈ 56.7%`

再看四段分层均值：
- `BTC`: `[+11.78, +8.19, +19.22, +1.30]`
- `ETH`: `[+20.88, +17.66, +24.44, +6.84]`
- `SOL`: `[+5.01, +15.19, +25.72, +7.69]`
- `BNB`: `[+12.30, +17.63, +15.73, +4.47]`
- `DOGE`: `[+22.02, +11.26, +32.09, +4.95]`

结论：
- 没有出现“去掉某 1 个币后其余全塌”的集中度问题；
- 最近一段的确整体走弱，但 **五个币在四段里仍全部保持正均值**；
- `BTC` 最近段仅 `+1.30bps/day`，说明这条线并不该被包装成纯 BTC 稳定时钟；更合理的承接对象仍是 `EW5` basket，而不是退回单币叙事。

## admission 结论
这轮 `time stability / cross-asset stability` 已给出会改变系统认知的答案：

- `Rank 422` 不是只靠单一币或单一月份撑起来的假 pocket；
- 但它也已经暴露出 **明显 regime-sensitive** 特征：最近一段仍为正，却已显著降速；
- 因此，当前最诚实的结论还不是直接 `promote_P3`，而是 **保留在 `P2`，把下一步唯一最小 blocker 收敛到固定 scheduler + 更现实 friction 下的 execution realism**。

## verdict
`Rank 422` 的 `EW5 + 21:15 delay-one-bar` 在四段时间切片与五币分布下仍保持全段、全币正均值，说明它不是单月/单币幻觉；但最近阶段已明显降速到薄正，当前更像 `regime-sensitive recurring session pocket` 而非已经无需再问 execution realism 的稳固 paper candidate，因此本轮主结论为 `keep_P2`，下一步只应补固定 scheduler + realism 的最小出口检查。