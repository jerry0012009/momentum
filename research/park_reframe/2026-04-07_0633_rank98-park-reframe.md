# 2026-04-07 06:33 UTC · Rank 98 park reframe

## 本轮范围与选择
- 本轮只复盘 `1` 条 parked rank。
- 按当前轮转，`50~79` 与 `80~110` 段都优先；其中 `Rank 98` 属于 `80~110`，且最近 `7` 天未见 bot6 对同一 rank 的复盘记录。
- 本轮不改 `docs/TODO.md` 顶部排班，不替 `bot2 / bot3` 分配新任务。

## 读到的最小必要材料
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`
6. `research/optimization_loop/2026-03-19_1953_rank98-fib-placebo-clean-replication.md`

## 原 rank 为什么 park
`Rank 98 / Fib placebo-zone honesty gate` 被 park 的核心原因很直白：

1. clean replication 没证明 `0.618` 比一批非 Fib placebo zone 更特殊；
2. `fib_exact -> fib_zone_015 -> fib_zone_030` 没有表现出“越像 Fib zone 越有增量”，反而 expectancy 轻微走弱；
3. `placebo_zone_mean` 在主口径下甚至出现 `positive_asset_ratio = 3/3`，说明这里更像 generic retrace geometry，而不是 `0.618` 的独立 ratio-edge；
4. 因此原研究真正被否掉的不是“所有回踩结构都没信息”，而是“把 Fib ratio 本身写成 queue-facing honesty gate”这件事站不住。

一句话：**被 park 的是 Fib ratio-edge，不是所有 retrace scaffold 语义。**

## hard park 还是 soft park
结论：**soft park，但对“Fib ratio-edge”这层原始主语已接近 hard park。**

- soft 的地方：`fib_exact` 本身并非完全失效，说明“回踩/回收几何”可能还残留一点结构信息；
- hard 的地方：这点残余并没有证明来自 `0.618` 本身，反而更像 placebo 也能得到的 generic retrace scaffold 效果。

所以原 `park` verdict 不能推翻；最多只能说它把残余价值收缩成了一个更弱、更泛化的结构线索。

## 有没有可救信号
有，但很弱，而且不是原命题里的那种“可救”。

### 可救信号
- `fib_exact` 不是全灭；
- `fib_zone` 与 placebo 对比说明：市场也许对“回踩几何 / retrace scaffold”有反应，而不是对 `0.618` 这个比值有反应。

### 不可救的部分
- 现在已经没有证据支持继续把 Fib ratio 当成独立 edge；
- 继续围绕 `0.382/0.5/0.618/0.786` 调 zone 宽度、换 ratio 组合，更像换壳重讲，不像诚实的新 hypothesis。

## 最值得改的唯一一刀
如果硬要保留残余价值，唯一诚实的一刀只能是：

**把 `Fib ratio-edge` 降级成 non-Fib 的 retrace scaffold / anchor-quality context，而不再把 ratio 本身当主语。**

也就是：
- trade on：保留“回踩后再决定是否放行”的结构语义；
- trade off：放弃“0.618 本身比 placebo 更有信息”的旧叙事。

## 是否值得形成新的 derived hypothesis
结论：**不值得；本轮维持 `keep_park`。**

原因有三：
1. 这条唯一可改轴太泛，已经不属于 `Rank 98` 原题的独特 residual；
2. 它和现有的 retrace / zone / Fib reclaim 家族高度重叠，继续派生大概率只是语义重命名；
3. 当前更诚实的做法，是承认 `Rank 98` 已完成它最重要的审计任务：证明 Fib ratio-edge 本身没有过 placebo honesty gate。

## 本轮结论（authoritative）
- `verdict`: `keep_park`
- `original verdict kept`: `park`
- `park flavor`: `soft park，但对原 Fib ratio-edge 读法已接近 hard park`
- `salvage signal`: `generic retrace scaffold / anchor-quality residual，非 Fib ratio-specific`
- `single modification axis if forced`: `demote Fib ratio-edge into non-Fib retrace scaffold context`
- `final judgment`: `残余过于泛化，且与既有 retrace / zone 家族高度重叠，不诚实再派生 Rank 98b`

## 对 queue 的最小写回
仅做两处最小更新：
1. 追加本轮日志到 `research/park_reframe/INDEX.md`
2. 在 `docs/PARK_REFRAME_QUEUE.md` 的 `Recently reviewed` 区追加 `Rank 98` 的本轮结论

## 备注
- 本轮未改 `docs/TODO.md`
- 本轮未新增 `derived_hypothesis_drafted`
- 当前 git 工作区存在大量与本轮无关的历史/并行脏文件（含大量 `research/optimization_loop/*`、`research/park_reframe/*` 未跟踪项），因此本轮不做 commit，避免混入无关变更；本轮仅做最小必要文件写回。
- 本轮目标是保留原 `park` verdict 的审计意义，而不是翻案
