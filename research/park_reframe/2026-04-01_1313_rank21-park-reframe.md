# 2026-04-01 13:13 UTC — Rank 21 park reframe review

## Context
- Loop: `bot6 park-reframe`
- Scope this round: revisit exactly one parked rank without overturning the original `park` verdict
- Selected rank: `Rank 21 / market risk-on/off regime gate`
- Selection reason:
  - 当前轮转里，`50+` 与 `80~110` 号段最近 7 天已连续覆盖多条（`Rank 79 / 84 / 101 / 67`），本轮按轮转回到 `1~24`
  - `Rank 21` 距离上次 `bot6` 复盘已超过 7 天
  - 它已有清楚的原始 `park` 审计文件与既有派生提案 `Rank 21b`，适合低频复核“这条残余值是不是还值得单独留在 queue 里”

## What the original rank was trying to do
- 把 `market risk-on/off` 写成一个 **15m 同频 shared regime gate**
- 原读法是：根据 `market_risk_2of3 / 3of3` 之类的状态，逐根决定现有 setup 是否 allow / deny

## Why Rank 21 was parked originally
原始审计文件：
- `research/optimization_loop/2026-03-17_0412_rank21-clean-replication-park.md`

核心原因很简单：
- 主变体 `market_risk_2of3 @ 6bps/side` 仍然是 `mean_total_return ≈ -25.01%`
- `positive_asset_ratio = 0/3`
- `10bps/side` 继续恶化到约 `-39.22%`
- 时间稳定性 `0/3 positive buckets`
- 参数邻域最佳也只有约 `-17.06%`

更直白地说：
- 它证明了“risk-on/off 同频 gate 比 baseline 少亏一点”
- 但没证明“15m 逐根 risk-on/off gate 本身是可推进的 queue-facing edge”
- 所以原结论保持为 `park` 是对的

## Hard park or soft park?
**当前更像：`soft park`，但对原始 Rank 21 读法已经偏硬。**

为什么还不是彻底 hard park：
- `risk sentiment / risk state` 这个主题本身没有完全死掉
- 低频风险状态影响仓位与确认强度，仍然是可信的交易语言

为什么比普通 soft park 更硬：
- 原始失败点已经很清楚，不是“参数还没调到”
- 原 rank 的唯一诚实残余，其实早就被收窄成 `Rank 21b`
- 最近 7 天并没有出现能再新增第二条独立修改轴的新证据

## Is there any salvage signal?
**有，但仍然只有一条，而且不是新的。**

最可信的可救信号，仍是 2026-03-20 的：
- `research/quant_digests/2026-03-20_0249_fng-extremity-risk-overlay.md`

它说明的不是“Fear & Greed 能预测下一根方向”，而是：
- 极端情绪日未来路径波动更大
- 方向并不稳定可预测
- 更诚实的落点是 `size-down / veto / stricter confirmation`

也就是说，Rank 21 唯一还留得住的信息，仍然是：
- **market risk-on/off 不适合做 15m 同频方向 gate**
- 但可以降级成 **日级 sentiment-extremity risk overlay**

问题在于：
- 这条残余并不新
- 它已经被现有 `Rank 21b` 完整吸收
- 最近新增的很多 desk 线索反而把注意力继续推向 `1m/3m` raw alpha / microstructure family，而不是再给这类低频 shared overlay 额外开第二条 queue 项

## The single best cut
如果现在还要保留唯一一刀，答案仍然不变：

- **single modification axis:** `demote standalone market risk-on/off regime gate into a daily sentiment-extremity shared risk overlay`

也就是：
- 不再让 `market_risk_2of3 / 3of3` 逐根决定 15m allow / deny
- 保留现有 setup 原始触发
- 只在 `Fear & Greed <= 25` 或 `>= 75` 的极端日做 `size-down / stricter confirmation / veto`

但也正因为如此，本轮不再新增第二个派生：
- 这条唯一诚实修改轴已经存在，名字就叫 `Rank 21b`
- 现在再写 `Rank 21c` 只会重复，不会增加新的决策价值

## Is a new derived hypothesis worth drafting?
**不值得。**

原因：
1. 原 `park` verdict 必须继续保留；
2. 唯一可救信号仍然只是既有 `Rank 21b`；
3. 最近没有出现足够新的、独立的、单轴的新证据，去支持再起一个 `Rank 21c`；
4. 当前 desk 的新增信息更偏向新的短周期 raw-alpha family，不值得在这里继续膨胀 queue。

## Trade on / Trade off of the residual idea
这里只是解释为什么“不再新 draft”，不是新增提案。

### Trade on
- 让低频情绪极端日只负责 `risk overlay`
- 更贴合交易摩擦与尾部风险，而不是假装能逐根预测方向
- 与现有 setup 的职责边界更清楚

### Trade off
- 它不再是独立 gate / 独立 alpha
- 改善很可能主要体现在回撤与左尾，而不是 headline return
- 如果只是靠大幅砍单变好，仍应快速压回 `park`
- 更重要的是：这条 residual 已被 `Rank 21b` 消费完，再开新编号只会重复

## Direct answers required by bot6 brief
- **原 rank 为什么 park？**
  - 因为 clean replication 清楚显示：`15m` 同频 `market risk-on/off` gate 虽比 baseline 少亏，但在收益、跨标的、时间稳定性、成本抬升后表现上都不过线。
- **它更像 hard park 还是 soft park？**
  - `soft park`，但对原始 shared gate 叙事已明显偏硬。
- **有没有“可救信号”？**
  - 有，仍然是“极端情绪更像低频 risk overlay，而非逐根方向 gate”。
- **最值得改的唯一一刀是什么？**
  - 把 standalone `market risk-on/off` gate 降级成 `daily sentiment-extremity shared risk overlay`。
- **是否值得形成新的 derived hypothesis？**
  - **不值得。** 因为这条唯一诚实残余已经被既有 `Rank 21b` 吸收，最近没有新证据支持第二个派生。

## Final verdict
- **Final verdict:** `keep_park`
- Original `park` verdict remains intact
- Current reading: `soft park`，但原始 `15m` 同频 gate 读法已明显偏硬
- Existing residual queue item `Rank 21b` remains the only honest narrow reframe; this round drafts nothing new

## Queue action
- Keep `Rank 21` parked
- Keep existing `Rank 21b` unchanged
- Do **not** draft `Rank 21c`
- Do **not** change top-level `docs/TODO.md` scheduling

## File-change / commit note
- This round only updates the park-reframe log, index, and queue
- No selective commit was made because the task only required minimal documentation updates, and the shared workspace may contain unrelated dirty files
