# 2026-04-03 17:51 UTC · Rank 12 park reframe

## Selected rank
- `Rank 12`
- selection note: 本轮按 `Rank 1~37` 的 parked rank 低频轮转处理，优先避开最近 `7` 天内已复盘条目。`Rank 12` 上次 bot6 单独复盘是 `2026-03-19 20:19 UTC`，已超过 7 天；同时它属于旧的 `S/R zone + context` parked 线，近两周又出现了更多 `zone persistence / retest memory / post-break verdict` 旁证，适合再判断一次：这些新证据是在支持新的 `Rank 12c`，还是只是在确认既有 `Rank 12b` 已经把可救残余吸收得差不多了。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-17_0011_rank12-clean-replication-park.md`
- `research/park_reframe/2026-03-19_2019_rank12-park-reframe.md`

原 `Rank 12` 被 park 的原因没有变：它把 **averaged support/resistance zone + context** 写成一条可直接承担 `15m` 入场职责的 standalone entry skeleton，但 clean replication 已经把这条主体审计成不够厚、不够稳。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `1 ATR stop`, `2 ATR target`, `8-bar time stop`, `6bps/side`）：
- `winner_variant = averaged_zone_context_gate`
- `mean_total_return ≈ -4.34%`
- `positive_asset_ratio = 1/3`
- Light Stability Pack 四项全 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数稳定性 `0/5 configs positive`
  - 跨标的稳定性 `1/3 assets positive`
  - 成本稳定性 `0/4 cost levels positive`

翻成人话：
- 原问题不是“换一组更好的 zone 参数就能活”；
- 而是 **averaged zone + context 自己当 entry alpha** 这件事没有形成足够诚实的 post-cost 主体；
- 因此原 `park` 的审计意义必须保留：失败对象是“让 Rank 12 自己承担 standalone zone-entry 角色”，不是 `S/R zone` 主题整体死亡。

## Hard park or soft park?
- 本轮判断：`soft park，但更偏硬`

为什么仍不是 hard park：
1. 原 rank 至少说明“单线位”不如“zone + context”更接近问题本体；
2. `Rank 12b` 已经证明，S/R 主题里仍有一条诚实残余：把它降级成 shared quality gate，而不是继续让它自己下单；
3. 因而主题并非零信息，只是角色已经被审计收缩。

为什么现在比 3 月 19 日更偏硬：
1. 最近新增旁证没有再给出第二条独立、同样诚实的窄修改轴；
2. 新证据要么继续强化既有 `Rank 12b` 的 `zone quality / persistence` 读法，要么已经把主题外流到 `post-break verdict / follow-up router`，不再诚实属于 `Rank 12`；
3. 所以对 `Rank 12` 而言，唯一还诚实的一刀已经基本固定，就是既有 `Rank 12b`，不值得再往下派生 `Rank 12c`。

## Any salvage signal?
有，但主要是**确认既有 Rank 12b，而不是生成新的派生轴**。

本轮最 relevant 的旁证：
- `research/quant_digests/2026-03-19_1912_volume-weighted-sr-persistence-gate.md`
- `research/quant_digests/2026-03-20_0640_freshness-weighted-retest-memory-gate.md`
- `research/quant_digests/2026-03-23_0312_ft-nft-killzone-postbreak-router.md`

这些证据合起来说明：
1. `S/R` 真正留下的信息，更像 **zone quality / freshness / persistence**；
2. 但一旦再往前走到 `freshness decay`、`FT/NFT 双路由` 这类读法，主语就已经从 `zone quality` 变成了 **post-break follow-up verdict skeleton**；
3. 换句话说，可救信号仍在，但最诚实的宿主不是新的 `Rank 12c`，而是：
   - 要么留在既有 `Rank 12b`（shared quality gate）；
   - 要么直接归入更共享的 breakout / retest follow-up family。

## Single best cut
如果只保留唯一一刀，本轮答案没有变化：

> **demote standalone averaged support/resistance zone + context entry into a volume-weighted zone-persistence shared quality gate**

也就是既有 `Rank 12b`。

为什么本轮不再提出新的一刀：
1. `freshness-weighted retest memory` 看起来像新轴，但本质是在 `Rank 12b` 内继续细化 `zone quality`，更像实现边界，不够独立；
2. `FT/NFT post-break router` 虽然很强，但它的主语已经是 post-break verdict，而不是 `S/R zone` 本身；
3. 因而若硬写 `Rank 12c`，很容易变成在既有 `12b` 上偷叠第二轴，或者借更共享的新 family 给旧 rank 续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 12c`：
1. 原 `park` verdict 没被推翻；
2. 原 rank 的唯一诚实修改轴仍只是既有 `Rank 12b`；
3. 最近新增旁证不是在提供新的单轴，而是在继续把同主题分流到 `zone quality implementation details` 或 `post-break verdict family`；
4. 所以更诚实的结论是：**保留 Rank 12 的 park 审计意义，同时承认它的 residual value 已基本被既有 Rank 12b 吸收。**

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但更偏硬；S/R 主题仍有 residual value，但唯一诚实修改轴仍只是既有 Rank 12b（volume-weighted zone-persistence shared quality gate）；最近新增的 retest-memory / post-break verdict 证据不足以再诚实派生 Rank 12c`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。
