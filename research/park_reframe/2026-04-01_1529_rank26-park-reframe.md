# 2026-04-01 15:29 UTC — Rank 26 park reframe review

## Context
- Loop: `bot6 park-reframe`
- Scope this round: revisit exactly one parked rank without overturning the original `park` verdict
- Selected rank: `Rank 26 / regime_triplet state gate`
- Selection reason:
  - 当前轮转里，`50+` 与 `80~110` 号段最近 7 天已连续覆盖（`Rank 79 / 84 / 101`），随后已回看 `1~24` 的 `Rank 21`
  - 因此本轮顺延到 `25~49` 号段
  - `Rank 26` 距离上次 `bot6` 复盘已超过 7 天，且它是少数“原始 pocket 不差、但 rescue budget 已经基本耗尽”的 parked rank，适合低频复核“是否还值得再派生一刀”

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- prior park-reframe logs:
  - `research/park_reframe/2026-03-18_1314_rank26-park-reframe.md`
  - `research/park_reframe/2026-03-21_1008_rank26-park-reframe.md`
  - `research/park_reframe/2026-04-01_1313_rank21-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0656_rank26-regime-triplet-paper-candidate.md`
  - `research/optimization_loop/2026-03-17_0724_rank26-ethsol-recheck-park.md`
  - `research/quant_digests/2026-03-20_0249_fng-extremity-risk-overlay.md`

## What the original rank was trying to do
- 把 `regime_triplet` 写成一个 **strict entry gate**：
  - `baseline multi-tf momentum` 先给方向
  - 只有 `long=up_regime / short=down_regime` 才允许真正开仓（`strict_up_down`）
- 也就是说，它不是单纯做 risk overlay，而是把 regime state 直接放在“是否允许 entry”这一层

## Why Rank 26 was parked originally
原始审计并不弱，这也是它当初会被推进到 `P2` 的原因：
- full-scope（BTC/ETH/SOL）下，`strict_up_down @ 6bps/side ≈ +14.65%`
- `positive_asset_ratio = 2/3`
- `mean_trades ≈ 141`
- `10bps/side ≈ +2.44%`

但 genuinely verdict-changing 的最小诚实检查做完后，结论变了：
- 只保留 `ETH+SOL-only` 后，`15bps/side ≈ +2.29%`，却只剩 `1/2` 资产为正
  - `ETH ≈ +9.89%`
  - `SOL ≈ -5.31%`
- `20bps/side ≈ -11.17%`
- `15bps` 时间桶仍有明显破口：
  - `bucket_1 ≈ -8.44%`
  - `bucket_2 ≈ +1.56%`
  - `bucket_3 ≈ +2.45%`

翻成人话：
- Rank 26 不是“完全没东西”
- 但它已经被最自然、最诚实的 rescue（剥掉弱腿）审过一遍了
- 审完之后，仍然不足以形成干净的 `P3 narrow paper pilot`
- 所以原始 `park` verdict 必须保留

## Hard park or soft park?
**当前仍是 `soft park`，但已经比 3 月中下旬更偏硬。**

为什么不是 hard park：
- 原始 full-scope pocket 确实存在，不像纯噪音
- `regime state` 主题本身也没有被完全证伪

为什么比普通 soft park 更硬：
- 最自然的一次 narrow rescue（`ETH+SOL-only`）已经被消费掉
- 后续唯一诚实的残余改写，其实也已经被 `Rank 26b` 吸收
- 最近新增证据并没有再给出第二条独立、比 `veto-only overlay` 更可信的新轴

## Is there any salvage signal?
**有，但仍然只有一条主线：把 strict gate 降级成 veto-only overlay。**

最可信的残余信号不是“继续缩 universe / 继续挑资产”，而是：
- 原 rank 的失败形状更像 **职责层放错了**
- `regime_triplet` 可能更适合当“坏环境别硬上”的 veto 层
- 不太像适合继续当“好环境才能上”的 strict entry gate

这点与既有证据是对齐的：
- 2026-03-21 那轮 bot6 已经据此起草了 `Rank 26b`
- `2026-03-20_0249_fng-extremity-risk-overlay.md` 也给了同方向的新旁证：
  - 低频情绪 / 风险状态更诚实的落点，是 `size-down / veto / stricter confirmation`
  - 不是逐根方向 gate，更不是新 alpha 本体

但问题也同样明确：
- 这条可救信号 **并不新**
- 它已经被现有 `Rank 26b` 完整吸收
- 最近并没有出现足够新的外部/内部证据，去支持再写一个 `Rank 26c`

## The single best cut
如果现在还保留唯一一刀，答案仍然只有这一条：

- **single modification axis:** `demote strict up/down entry gate into an asymmetric veto-only regime overlay`

具体含义：
- 不再要求 `long 必须 up_regime / short 必须 down_regime` 才 allow
- 保留现有更强的 base setup 去触发 entry
- `regime_triplet` 只负责否决明显坏环境：
  - long 遇到 `down_regime` veto
  - short 遇到 `up_regime` veto

但这也正好解释了为什么本轮不再起新编号：
- 这条唯一诚实修改轴已经存在，名字就是 `Rank 26b`
- 现在再写 `Rank 26c` 只会重复，不会增加新的决策价值

## Is a new derived hypothesis worth drafting?
**不值得。**

原因：
1. 原 `park` verdict 仍然必须保留；
2. 原 rank 最自然的窄救法（剥弱腿）已经做过，且不够干净；
3. 当前唯一可信残余已经被既有 `Rank 26b` 吸收；
4. 最近没有新的、独立的、足够强的单轴证据，支持继续派生 `Rank 26c`。

## Direct answers required by bot6 brief
- **原 rank 为什么 park？**
  - 因为它虽然在 full-scope 下给过 pocket，但经最小诚实 recheck（`ETH+SOL-only`）后，在更高 friction 与时间稳定性上仍不过线，不足以诚实升到 `P3`。
- **它更像 hard park 还是 soft park？**
  - `soft park`，但已明显偏硬；因为最自然的一次 rescue 已经被消费。
- **有没有“可救信号”？**
  - 有：`regime_triplet` 更像 veto-only shared overlay，而不是 strict entry gate。
- **最值得改的唯一一刀是什么？**
  - 把 `strict_up_down` 改写成 `asymmetric veto-only regime overlay`。
- **是否值得形成新的 derived hypothesis？**
  - **不值得。** 因为这条唯一诚实残余已经被既有 `Rank 26b` 吸收，最近没有新证据支持 `Rank 26c`。

## Final verdict
- **Final verdict:** `keep_park`
- Original `park` verdict remains intact
- Current reading: `soft park`，但原始 strict entry-gate 读法已明显偏硬
- Existing residual queue item `Rank 26b` remains the only honest narrow reframe; this round drafts nothing new

## Queue action
- Keep `Rank 26` parked
- Keep existing `Rank 26b` unchanged
- Do **not** draft `Rank 26c`
- Do **not** change top-level `docs/TODO.md` scheduling

## File-change / commit note
- This round only updates the park-reframe log, index, and queue
- No selective commit was made because the task only required minimal documentation updates, and the shared workspace may contain unrelated dirty files
