# CTREND 多时域技术状态聚合 × 横截面强弱排序 fresh intake -> background/P0

- 时间：2026-04-21 05:34 UTC
- 对象：`CTREND 多时域技术状态聚合 × 横截面强弱排序`
- 类型：fresh intake first verdict
- 结论：`background/P0`

## 本轮执行的小点
按 `cycle_plan` 第 2 项，对 `research/quant_digests/2026-04-21_0405_cttrend-xs-techstack-alpha.md` 做 fresh intake first verdict；只补 1 个最小 decisive blocker：确认这条线在当前 `5m/15m` liquid majors 里是否还能留下可独立承接的 short-cycle pocket，还是已经清楚只是 ranking/router 线索而非 front raw alpha。

## 读取到的现成证据
- digest：`research/quant_digests/2026-04-21_0405_cttrend-xs-techstack-alpha.md`
- artifact：`reports/artifacts/quant_digests/cttrend_lite_majors_15m_summary_2026-04-21.csv`
- artifact：`reports/artifacts/quant_digests/cttrend_lite_majors_5m_summary_2026-04-21.csv`
- artifact：`reports/artifacts/quant_digests/cttrend_lite_majors_meta_2026-04-21.json`

## 最小 decisive blocker 复核
本轮不再扩展第二条子任务，只接受 digest 已给出的最小可复算 portability probe：
- universe：`16` 个 liquid majors（`BTC/ETH/SOL/XRP/DOGE/BNB/ADA/LINK/AVAX/LTC/BCH/DOT/TRX/SUI/HBAR/AAVE`）
- 频率：`15m`、`5m`
- score：`cttrend_lite`（多期限收益、均线相对位置、量能状态、波动扩张、`RSI14` 的横截面 percentile rank 平均）
- 组合：每根 bar 做多 top3、做空 bottom3
- 检查口径：next `1` bar / next `3` bars long-short spread

### 1) `15m` 裸 top-vs-bottom 已经没有 short-cycle after-cost pocket
`cttrend_lite_majors_15m_summary_2026-04-21.csv`：
- `ls_next1`: `n=2491`, `avg_bps≈-0.486`, `t≈-1.231`, `hit_rate≈45.7%`
- `ls_next3`: `n=2491`, `avg_bps≈-0.264`, `t≈-0.387`, `hit_rate≈46.7%`

也就是说，最直接的 `15m` 横截面 strongest-vs-weakest continuation 迁移本身就没有留下 gross pocket；统一成本后只会更差，不存在可诚实保留的 front-slot raw alpha。

### 2) `5m` 结果更差，显示它不是一个可直接缩频的分钟级 continuation alpha
`cttrend_lite_majors_5m_summary_2026-04-21.csv`：
- `ls_next1`: `n=2991`, `avg_bps≈-0.679`, `t≈-2.916`, `hit_rate≈43.6%`
- `ls_next3`: `n=2991`, `avg_bps≈-1.335`, `t≈-3.343`, `hit_rate≈44.3%`

`5m` strongest/weakest 的后续表现不只是“赚不够成本”，而是连 gross 都偏反向，说明 naive 的多时域技术状态聚合在当前 liquid majors short-cycle 上更像会撞上短窗回吐/均值回归，而不是形成可直接承接的 continuation edge。

### 3) 这条线当前更像 router / ranking layer，而不是独立 front raw alpha
当前最小 blocker 已足够回答本轮问题：
- digest 自己给出的 minute-level portability probe 在 `15m/5m` 均未保住正的 top-vs-bottom spread
- 没有任何 recent short-cycle pocket 被证明在统一成本后仍有独立余量
- 现有可见价值只剩“也许可以给别的 raw alpha 做 confirmation / veto / symbol selection”的 ranking 用法

因此它不满足 fresh intake front-slot 的保留标准；继续把它当成独立 raw alpha 只会重复烧时间。

## verdict
`CTREND 多时域技术状态聚合 × 横截面强弱排序` 的 fresh intake first verdict 已诚实收口：digest 自带的 `cttrend_lite` portability probe 在当前 liquid majors 上，`15m` 的 top3-vs-bottom3 在 next `1/3` bars 仅有约 `-0.49/-0.26bps`，`5m` 进一步恶化到约 `-0.68/-1.34bps`，说明这条线在当前 short-cycle 口径下连裸 gross continuation spread 都没保住；现有价值更像 ranking/router 提示层，而不是可独立承接的 front raw alpha，因此本轮直接收口 `background/P0`。
