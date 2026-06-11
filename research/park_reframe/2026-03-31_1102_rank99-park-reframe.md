# 2026-03-31 11:02 UTC — Rank 99 park reframe review

## 为什么这轮看 Rank 99
- 继续遵循 `bot6` 轮转：当前默认优先 `Rank 50+`，且最近 `7` 天内未见 `Rank 99` 的 `park_reframe` 复盘记录。
- `Rank 99 / CLV asymmetric admission layer` 属于典型的“原始主题不算荒谬、但很容易跟近邻 bar-quality / conviction family 重复讲故事”的条目，适合做一次低频复盘。
- 本轮只做 `park` 后审计，不改 `docs/TODO.md` 顶部排班，也不替 `bot2 / bot3` 分配新任务。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/quant_digests/2026-03-19_1623_zenoclaw-clv-asymmetric-admission-layer.md`
- `research/optimization_loop/2026-03-19_2053_rank99-clv-clean-replication.md`
- `research/optimization_loop/2026-03-19_2130_rank99-time-stability-park.md`
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/overall_summary.csv`
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/asset_summary.csv`
- `reports/artifacts/scout_rank99_clv_asymmetric_admission_15m/time_stability_summary.json`
- `research/quant_digests/2026-03-22_0858_breakout-bar-conviction-gate.md`
- `research/quant_digests/2026-03-19_2256_body-zone-reentry-honest-verdict.md`

## 1) 原 Rank 为什么 park？
原 Rank 99 想表达的是：
- 不再把 “strong candle close” 当口号；
- 把 `CLV(close-location value)` 规则化，作为三条主线（`breakout-short / Fib retest_hold / EMA-PSAR continuation`）都能复用的方向不对称 admission layer。

原始 intake 其实已经给出一个相当清楚的早期读法：
1. **short 侧有改善迹象。**
   - `short_baseline` 平均约 `-5.89bps`
   - `short_clv070` 改到约 `-2.36bps`
   - `short_clv080` 改到约 `-0.43bps`
   - `short_clv070_plus_volume` 约 `-1.21bps`，而且 `positive_asset_ratio = 2/3`
2. **long 侧没有跟上。**
   - `long_baseline` 约 `-12.61bps`
   - `long_clv070_only` 反而更差到 `-13.97bps`
   - long 真正少亏的是 `volume_only`，不是 `CLV-only`
3. 所以 clean replication 当时给的是：
   - **不是直接 park**，而是先留在 `keep_P1 / evidence_pool`，因为它至少说明了“strict CLV 对 short follow-up 可能有点帮助”。

但真正把它压回 `park` 的，是随后那次 **time stability**：
- `short_clv080` 只有 `1/3` 正桶；
- `short_clv070_plus_volume` 也只有 `1/3` 正桶；
- `long_volume_only` 与 `long_volume_plus_clv` 都是 `0/3` 正桶；
- `time_stability_summary.json` 直接收口：
  - **hard verdict = `park / evidence pool`**
  - 原因是：`short strict-CLV 只剩单一时间 pocket，long 侧各臂三桶全负`。

翻成人话：
**Rank 99 不是完全没信号，而是它一旦被写成三线共用的 shared admission layer，就会暴露出两个问题：short 改善只活在窄时间 pocket，long 侧则根本不支持“close near high = continuation 成立”这套读法。**

## 2) 它更像 hard park 还是 soft park？
我的判断：**`soft park，但现在已经很偏 hard`。**

为什么不是纯 hard park：
- `CLV / edge-close / bar-quality` 这个大主题并没有死；
- 原始 clean replication 至少说明：**short 侧 strict edge-close** 确实比 baseline 少亏；
- 这表示“decision bar 收在靠近 bar 边缘的位置”不是纯噪声。

为什么又说“很偏 hard”：
- 一做时间稳定性，这个 short 改善就只剩单一 pocket；
- long 侧不仅没支持，反而说明 `CLV-only` 方向上是错配的；
- 更关键的是，最近的新证据已经把这类残余价值上移到更宽、也更诚实的 `breakout bar conviction / body-defined verdict / breakout-short bar-quality` family，Rank 99 自己那种“三线共用的 asymmetric CLV layer”读法已经站不住了。

所以它不是“主题彻底无定义”的 hard park；但对 **Rank 99 这版写法本身** 来说，已经接近 hard enough。

## 3) 现有证据里有没有“可救信号”？
有，但只剩很窄的一条，而且主要在 short 侧。

### 可救信号
1. **short 侧 strict edge-close 仍有 residual**
   - `short_clv080` 接近打平；
   - `ETH` 与 `SOL` 上都有正均值 pocket；
   - 说明 “post-break 决策 bar 如果没有 close near the edge，就别急着相信 short follow-up” 这件事并非空想。
2. **最近的新 digest 也支持 bar-quality 主题还活着**
   - `2026-03-22 breakout-bar-conviction-gate`：把信息压缩成单根 breakout bar 的 `body% + edge-close` conviction；
   - `2026-03-19 body-zone-reentry-honest-verdict`：把后续失败判决边界改成更诚实的 body-defined zone；
   - 两者都在说：**真正活下来的，是 breakout-short 的便宜判决 / conviction 语义，而不是 Rank 99 原本那个跨三线 shared admission layer。**

### 但为什么说它不够救回 Rank 99
- 可救信号只明确支持 **short-side breakout conviction**，不支持 long continuation；
- 而且这条 residual 已经开始和更新的近邻家族重叠：
  - `single-bar breakout conviction`
  - `body-defined failure verdict`
  - 以及一类更窄的 breakout-short admission / veto 提案
- 也就是说：**有主题层残余，但越来越不像 Rank 99 自己独立该拥有的一条 queue-facing reframe。**

## 4) 最值得改的唯一一刀是什么？
如果一定要保留唯一主修改轴，最自然的一刀只剩：

**把 `CLV asymmetric admission layer` 从三线共用 shared gate，降级成 `breakout-short-only` 的 cheap edge-close conviction veto / admission。**

也就是：
- 不再服务 `Fib retest_hold` 与 `EMA continuation` 的 long lane；
- 不再把 `CLV` 当多空不对称但仍可共享的万能层；
- 只回答一个更窄的问题：
  - **breakout-short 决策 bar 若没有足够 edge-close（如 strict short-side CLV），是否应直接 veto / size-down？**

这是本轮唯一还算诚实的一刀。

## 5) 是否值得形成新的 derived hypothesis？
**本轮结论：不值得，维持 `keep_park`。**

原因有四个：
1. 原 `park` 的审计意义很强，不能推翻：
   - shared 版本已经被 time stability 清楚否掉；
2. 唯一可救信号只剩 `breakout-short-only` 的窄 residual，已经不再支持 Rank 99 原命题；
3. 最近新证据已经把这类残余价值迁移到更上位 / 更宽容器：
   - `breakout-bar conviction`
   - `body-defined failure / verdict`
   - 更一般的 breakout-short bar-quality family
4. 如果现在硬写 `Rank 99b`，大概率只是在重复说：
   - “把 CLV 从 shared layer 降级成 breakout-short 专用 conviction veto”
   但这条线和近邻 family 的重叠已经很重，独立存在的必要不够强。

换句话说：
- **不是完全没有可改轴；**
- 但它更像应被吸收到更新的 breakout-short conviction / verdict 家族里，
- **而不是再诚实地以 `Rank 99b` 单独立项。**

## 6) trade on / trade off（如果硬要派生会是什么）
本轮不 draft 新假设，但为了审计完整性，记录一下如果硬要派生，它会是什么：
- **trade on**：只在 `breakout-short` 已触发时，额外读取 strict short-side `CLV` 作为 cheap conviction veto / admission；默认不接 long，不接 shared multi-lane gate。
- **trade off**：彻底放弃 Rank 99 原本“bar-quality 可三线共用”的读法；而且这条窄轴与最近的 `breakout-bar conviction` / `body-defined verdict` 家族高度重叠，独立建新 rank 很容易变成重复 draft。

因此本轮选择：**记住这条残余语义，但不新开 `Rank 99b`。**

## 最终结论
- `Rank 99` 原 `park` verdict：**保留**
- 本轮状态：**`keep_park`**
- 一句话总结：
  - **Rank 99 更像 soft park，但现在已经很偏 hard；它唯一留下的 residual 只剩 breakout-short 的 strict edge-close / bar-quality 语义，而最近新证据已把这部分残余迁移到更上位的 breakout conviction / failure-verdict family，当前不诚实再派生 Rank 99b。**

## 队列写回
建议在 `docs/PARK_REFRAME_QUEUE.md` / `research/park_reframe/INDEX.md` 中登记为：
- `2026-03-31 11:02 UTC | Rank 99 | verdict=keep_park | original verdict kept=park | note=soft park，但已很偏 hard；原 Rank 99 的 CLV asymmetric shared admission layer 被 time-stability 审清：short strict-CLV 只剩单一时间 pocket、long 侧全负；其唯一残余已迁移到 breakout-short conviction / failure-verdict family，当前不诚实再派生 Rank 99b`

## Git / 风险备注
- 本轮只做最小必要文件改动。
- 当前工作区长期存在大量与本轮无关的脏文件；为避免混提，本轮不做 commit。
