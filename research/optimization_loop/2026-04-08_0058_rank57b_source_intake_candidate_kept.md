# 2026-04-08 00:58 UTC · Rank 57b source-intake decision

## Target
- `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
- object under judgment: `breakout-family-local pre-break compression admission` (`Rank 57b` drafted hypothesis)

## Why this step existed
当前 `cycle_plan` 第 4 项要求判断：这条从 `Rank 57` park 后收窄出来的派生，是否已经足够拿到**正式 fresh first verdict**，还是仍应停留在 `source-intake candidate`。

这一步不是重新审 `Rank 57` 原 shared-gate 结论；原结论保持不变。要回答的只有一件事：

> 现在手上的材料，是否已经把 `baseline breakout_short vs compression-admission` 的单轴 A/B、trade retention 口径、以及宿主边界压到足够清楚，能让这条派生正式进入 front-slot fresh intake？

## Materials checked
1. `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
2. `research/quant_digests/2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`
3. `research/park_reframe/INDEX.md`

## What is already clear
现有材料已经把下面这些事说清：
- 原 `Rank 57` 失败的是 **TTM squeeze release 作为跨 setup shared gate** 的读法，不是“压缩主题永远无效”。
- 残余信息主要集中在 `breakout_short`，不是 `ema_psar_long / fib_retest_long / breakout_short` 三条线共用。
- `2026-03-30` 的 `bottom-quartile BB compression breakout` digest 给了同方向旁证：压缩主题更像 **breakout family 的局部 admission / participation 语义**，而不是 shared gate。
- 因而，把 `Rank 57` 收窄成
  `breakout-family-local pre-break compression admission`
  这条修改轴，本身是诚实的。

## What is still missing
但要把它从 `source-intake candidate` 升成正式 fresh intake，还差最关键的一层：

### 1) 还没有单轴 clean-room A/B
当前只有概念上很清楚的改写：
- baseline: `breakout_short`
- modified: `breakout_short + pre-break compression admission`

但还没有看到正式冻结的最小 A/B：
- 同一宿主、同一成本口径、同一出场骨架；
- 唯一改动只允许是 `pre-break compression admission`；
- 明确报告 `post-cost return / trade count / trade retention / hit-rate or loss-shrink effect`。

没有这层，当前还只是“像一个值得测的派生问题”，不是“已经足够拿 fresh first verdict 的 front-slot 对象”。

### 2) compression 定义仍是 drafted，不是冻结实验口径
现有文字里提到：
- `trailing BB-width bottom-quartile`
- 或 `squeeze-on`

这已经足够形成研究方向，但还不够形成一个正式 fresh intake 对象，因为第一轮要测的口径还没冻结成唯一版本。当前仍属于：
- 主题清楚；
- 但 implementation axis 还没有收紧到单一实验问题。

### 3) 宿主边界仍偏描述性
现有材料已经说明“只保留 breakout family-local 角色”，但还没完全冻结：
- 是否只限 `breakout_short`？
- 是否默认排除 long-side breakout 版本？
- 是否明确禁止叠加 `200SMA / volume spike / funding / 新 exit` 第二轴？

park-reframe 文档的语言已经**接近**这些边界，但还没到可以直接给 fresh verdict 的“冻住版本”。

## Decision
### Verdict
- `remain source-intake candidate`

### Why
翻成人话：
- 这条派生 **已经不是空想**，而且修改轴是诚实的；
- 但它现在仍是“一个被写清的待测问题”，不是“一个已经压成 front-slot fresh intake 的对象”。

要进入正式 fresh intake，至少还需要：
1. 冻结唯一 compression 定义（例如只保留 `trailing BB-width bottom-quartile`）；
2. 冻结唯一宿主（默认 `baseline breakout_short`）；
3. 给出唯一单轴 A/B 口径，并明确 trade retention。

在这三件事没落库之前，直接给 fresh first verdict 会太早。

## Result sentence for runtime
- `Rank 57b：breakout-family-local pre-break compression admission 的修改轴已清楚，但 baseline breakout_short vs compression-admission 的单轴 A/B、trade retention 口径与宿主边界仍未冻结，因此本轮维持 source-intake candidate，不进入正式 fresh intake`

## State impact
- 不改 `Paper launch queue / Fresh intake slot / Surviving candidate slot / Active P2 slot`
- 只收口当前 `cycle_plan` 第 4 项

## Final note
这不是把它打回 background，也不是否认它有研究价值；只是现在还不到拿正式 `fresh first verdict` 的时点。更诚实的位置仍然是：`source-intake candidate`。
