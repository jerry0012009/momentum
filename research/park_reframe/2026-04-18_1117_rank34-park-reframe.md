# 2026-04-18 11:17 UTC · Rank 34 park reframe revisit

- source rank: `Rank 34 / chip-distribution trapped-holder reclaim / winner-ratio gate`
- current authoritative verdict: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Why this rank this round
- 本轮遵循用户口径，回到 `Rank 1~37` 的已 `park` 条目中低频挑 1 条。
- `Rank 34` 虽在 `2026-04-12` 刚复盘过一次，尚未满 `7` 天；但 `2026-04-18` 又新增了更贴主题的 auction-structure 新证据（尤其 `POC / value-area / LVN`），因此这次复看是为了确认：这些新证据是在救旧 `Rank 34`，还是进一步证明它该停留在 `park`。
- 这条线的审计边界本来就很清楚：问题不在阈值微调，而在 `synthetic shares / turnover` proxy 的 honesty。适合用新证据再做一次“宿主是否已经迁移”的判断。

## Files read this round
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-12_0125_rank34-park-reframe.md`
- `research/optimization_loop/2026-03-17_1222_rank34-clean-replication-park.md`
- `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`

## 1) 原 rank 为什么 park？
原 `Rank 34` 被 park 的主因没有变化：
**edge 过度依赖 `synthetic shares / turnover` 这类很难诚实冻结的库存代理。**

原 clean replication 给出的关键事实仍然成立：
- `raw_baseline @ 6bps/side` 三资产均值约 `-7.38%`，base line 本身就不成立；
- 看起来最好的 `chip_cost_reclaim` 只在 `conservative anchor` 下成立：
  - `mean_total_return ≈ +18.14%`
  - `positive_asset_ratio = 3/3`
- 但一旦把假设放宽：
  - `neutral @ 6bps`：虽然均值还勉强可看，但 `positive_asset_ratio` 已掉到 `1/3`
  - `aggressive @ 6bps`：均值转成明显负值
- 成本拉到 `15~20bps` 后，即使 `conservative anchor` 的 pocket 也明显退化。

所以旧 rank 被 park，不是因为“库存/套牢盘”这层市场语言完全没信息，而是因为：
**可交易结论高度寄生在 assumptions-sensitive proxy 上。**

## 2) 它更像 hard park 还是 soft park？
本轮判断：**更像 hard park，且比 4 月 12 日那轮更接近 hard park with consumed residual。**

原因：
1. blocker 在 explanatory variable 本身，不在 entry/exit 表层；
2. 最好看的 pocket 始终依赖最保守、也最容易美化的 anchor；
3. 4 月 18 日新增证据没有提升旧 proxy 的 honesty，反而把主题推向更直接的 `auction profile / POC / LVN` 原始宿主。

若勉强保留一点 soft 成分，也只剩：
- `conservative anchor` 下曾出现过正 pocket；
- 说明“库存拥挤 / trapped-holder reclaim”这类直觉并非完全空想。

但这点 soft 成分已经不够支撑新的 queue-facing reframe。

## 3) 有没有“可救信号”？
**有主题级可救信号，但没有属于旧 `Rank 34` 本体的可救信号。**

`2026-04-18_0049_auction-profile-poc-lvn-shell.md` 反而把方向说得更清楚：
- 若 `volume-profile / inventory-anchor` 主题还有信息，更诚实的主语是：
  - `value-area re-entry -> POC mean reversion`
  - `LVN traverse -> next acceptance zone continuation`
- 这些信号直接使用 `POC / VAH / VAL / LVN` 这种 auction 结构对象；
- 不再需要旧 `Rank 34` 那套 `synthetic shares / winner-ratio / turnover` 代理来“猜库存”。

也就是说：
- **主题仍有 residual value；**
- **但真正可救的宿主已经迁到更直接的 auction-structure raw-alpha family。**

它救的是主题，不是旧 `Rank 34`。

## 4) 最值得改的唯一一刀是什么？
如果只允许保留一条唯一主修改轴，最诚实的一刀仍然只能写成：

**把 `chip-distribution trapped-holder reclaim` 从可执行 15m gate，降级成离线 inventory/crowding context note。**

也就是：
- 不再让它自己决定 allow/deny 或 next-bar entry；
- 只把它保留为一种背景解释变量，用来帮助理解更直接的 `auction-profile / POC / LVN` 主宿主。

但这也正是本轮不值得 draft 新派生的原因：
- 一旦降到这个层级，它已经不再是 bot2 可直接判断是否入板的 queue-facing hypothesis；
- 它没有解决旧 proxy 的 honesty 问题，只是把它边缘化；
- 更重要的是，4 月 18 日新证据给出的更好做法不是“旧 proxy 降级继续留着”，而是**直接改写成新的 auction-structure 宿主**。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得；本轮维持 `keep_park`。**

理由：
1. 原 `park` verdict 的审计意义仍然很强，没必要推翻；
2. 新证据没有修复 `synthetic shares / turnover` proxy 的 assumptions sensitivity；
3. 若现在硬写 `Rank 34b`，大概率会滑向“换变量 + 换宿主”的多轴大改；
4. 更诚实的做法是承认：旧 `Rank 34` 的 residual 已进一步被新的 `auction profile / POC / LVN` raw-alpha 宿主吸收，而不是还值得以旧 rank 名义重开。

## 6) 审计式 trade on / trade off（仅用于说明为什么不 draft）
### single modification axis
- `demote chip-distribution trapped-holder reclaim from executable gate into offline inventory-context evidence only`

### trade on
- 保留原 rank 对“库存拥挤 / 套牢盘重夺”直觉的审计痕迹；
- 不再要求它自己给出 bar-level trigger；
- 允许它只作为背景解释层存在。

### trade off
- 它不再是 queue-facing hypothesis；
- 没有修复旧 proxy 的核心 honesty 问题；
- 很容易沦为事后解释变量，而不是可复现实验对象；
- 与 4 月 18 日新增的 `auction profile / POC / LVN` 新宿主相比，信息表达更弱、更绕。

## Final verdict
**`keep_park`**

- 原 `park` verdict 保留；
- `Rank 34` 本体更像 `hard park`，且 residual 已更接近被新宿主消费；
- 当前“可救信号”属于更直接的 `auction-structure raw-alpha family`，而不是旧 `Rank 34` 足以诚实派生出的 `Rank 34b`；
- 因此本轮不 draft 新的 derived hypothesis。

## Queue impact
- `docs/PARK_REFRAME_QUEUE.md`：仅在 `Recently reviewed` 追加一条 `Rank 34 / keep_park` 简记；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 默认不改 `docs/TODO.md` 顶部排班；
- 不新增 active reframe candidate。

## Commit note
- 本轮只做最小必要文档改动。
- 工作区存在与本轮无关的脏文件，因此不做 selective commit，避免混提。
