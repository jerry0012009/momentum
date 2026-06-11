# 2026-03-23 00:45 UTC · Rank 20 park reframe review

## Scope
- source rank: `Rank 20 price-volume divergence breakout filter`
- allowed output set: `keep_park / soft_reframe_candidate / derived_hypothesis_drafted`
- this round verdict: **`keep_park`**
- original verdict kept: **`park / evidence pool`**

## Why revisit Rank 20 this round
- 虽然 `Rank 20` 在最近 7 天内已经被 `bot6` 看过一次，但这次不是无证据重复复盘。
- 2026-03-22~23 新增的近邻证据，正好打在 `Rank 20b` 这条已起草 reframe 的实现边界上：
  - `2026-03-22_2258_bounce-polarity-not-shared-gate.md`
  - `2026-03-23_0031_caizongxun-hammer-engulf-retest-asymmetric-gate.md`
- 这两条新证据都在说同一件事：**量价/形态确认更像强烈的方向不对称 quality layer，而不是三线共享 hard gate。**
- 因此这轮值得做的，不是再起一个 `Rank 20c`，而是判断：`Rank 20b` 是否仍是唯一保留的窄 reframe，还是已经被新证据推翻。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-17_0326_rank20-price-volume-divergence-park.md`
- `research/park_reframe/2026-03-19_1539_rank20-park-reframe.md`
- `research/quant_digests/2026-03-19_0706_volume-price-interaction-admission-layer.md`
- `research/quant_digests/2026-03-22_2258_bounce-polarity-not-shared-gate.md`
- `research/quant_digests/2026-03-23_0031_caizongxun-hammer-engulf-retest-asymmetric-gate.md`

## 1) 原 rank 为什么 park？
原 `Rank 20` 被 park，不是因为“量价关系这个主题彻底没信息”，而是因为它被写成了 **standalone 的 breakout filter family**，结果在 clean replication 里直接失败：

- baseline `baseline_mtf_momentum @ 6bps/side`
  - `mean_total_return ≈ -38.69%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 570.7`
- 主变体 `pvd_break24_delta0.5_warn3 @ 6bps/side`
  - `mean_total_return ≈ -39.22%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 552.0`

而且 Light Stability Pack 也没有留下 pocket：
- 时间三桶全负：`0/3 positive buckets`
- 参数邻域没有转正
- 跨资产 `BTC/ETH/SOL` 全负
- 成本上升后继续恶化

翻成人话：
- 原 Rank 20 不是“差一点就能救”；
- 而是 **把 divergence warning 本身当主过滤器** 这件事，已经被审计成不成立。

## 2) 它更像 hard park 还是 soft park？
**仍然更像 `soft park`。**

原因：
- 原始 standalone 写法已经该停，这是硬的；
- 但这不等于量价交互主题彻底归零，因为 2026-03-19 的 `volume-price interaction` digest 已经给出一个更诚实的角色降级读法：
  - 不让它自己决定交易；
  - 只让它做 shared admission / sizing layer。

所以：
- `Rank 20` 本体仍该 park；
- 但它更像 **主题可留、职责降级** 的 soft park，而不是“以后完全不用再提量价交互”的 hard park。

## 3) 有没有“可救信号”？
**有，但不是新的一条。**

可救信号仍然集中在既有 `Rank 20b` 的那一刀：
- `2026-03-19_0706` 已经说明：别把 volume gate 写成单指标阈值，而应看 `price thrust × volume participation × absorption penalty` 这种 interaction；
- `2026-03-22_2258` 新证据说明：别把 retest 后那根同方向实体当 shared hard gate，它更像 late-chase；
- `2026-03-23_0031` 新证据进一步说明：`hammer/engulf` 的 pattern-confirmation 也明显偏 long-side quality，不适合直接共享到 breakout-short。

三条合起来的读法很清楚：
- **能留的不是“再加一种量价确认形态”**；
- 能留的是：`Rank 20b` 这种更宽、更克制的 interaction admission layer；
- 而且它必须接受 **明显的 setup/方向不对称**，不能再被写成“三条线统一 hard gate”。

## 4) 最值得改的唯一一刀是什么？
**仍然是旧的那一刀，不是新的第二刀。**

> 把 standalone `price-volume divergence breakout filter`，降级成 `volume-price interaction` shared admission layer。

这轮没有出现更值得替换它的唯一主修改轴。
相反，新证据是在提醒：
- 不要把这条线再次改写成 `bounce polarity gate`、`hammer/engulf gate`、或别的更窄 pattern gate；
- 那样只会把 `Rank 20b` 从“量价交互 admission layer”重新缩回“另一个 assumptions-sensitive 小硬门”。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

本轮不应新增 `Rank 20c`。

理由：
1. `Rank 20b` 已经把最自然、最诚实的单轴改写占住了：
   - 从 standalone 过滤器 → shared admission layer。
2. 2026-03-22~23 的新证据没有给出新的主修改轴；
   - 它们只是在收紧 `Rank 20b` 的边界：
   - **别把 interaction layer 又偷写成共享 pattern hard gate。**
3. 如果这轮硬起 `Rank 20c`，大概率只是把同一主题拆成更碎的 confirmation 审美，而不是更强的新假设。

## 6) 本轮结论
- `verdict`: **`keep_park`**
- `park_type_read`: **`soft park`**
- `derived hypothesis?`: **no new one**
- `existing reframe status`: **保留既有 `Rank 20b` 作为唯一主修改轴；本轮不新增 `Rank 20c`**

## Minimal audit note
- 原 `park` verdict 保持不动；
- 这轮新增证据没有推翻 `Rank 20b`，但明确了它的边界：
  - 更像 **interaction-based admission / sizing layer**；
  - 不像 `hammer/engulf`、`same-direction bounce body` 这类可共享 hard gate。
- 因此当前最诚实的写法是：
  - `Rank 20` 继续 park；
  - `Rank 20b` 继续是唯一保留的窄 reframe；
  - 本轮不再派生新 rank。

## Git
- 本轮只做最小必要文档更新。
- 未做 commit：工作区存在较多无关脏文件，当前不适合安全地 selective commit。
