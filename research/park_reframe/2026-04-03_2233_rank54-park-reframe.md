# 2026-04-03 22:33 UTC · Rank 54 park reframe

## Selected rank
- `Rank 54`
- selection note: 本轮继续遵循 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，并优先避开最近 `7` 天已被 bot6 单独复盘的条目。`Rank 54` 自 `2026-03-18` clean replication 压回 `park` 后，尚未被 bot6 单独复盘；同时 2026-04-03 新增了直接相关的 `rolling POC / value-area displacement` digest，适合判断一次：这条新证据是在救旧的 `LVN rejection + POC acceptance shared gate`，还是只是在把 volume-profile 主题外流成新的单资产 raw-alpha family。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_1104_rank54-source-intake-guard-passed.md`
- `research/optimization_loop/2026-03-18_1135_rank54-clean-replication-park.md`

原 `Rank 54` 被 park 的原因没有变：它把 **LVN rejection + POC acceptance** 写成可服务 `ema_pullback_long / breakdown_reclaim_short` 的 shared confirmation gate，但最小 clean replication 证明，这条 acceptance 层一旦按 desk 的 `signal close -> next-bar open -> no-overlap` 口径执行，几乎只剩“把样本砍到没有交易”的 veto 语义，而不是可部署的 queue-facing gate。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `6bps/side`）：
- `breakdown_reclaim_short + lvn_rejection_plus_poc_acceptance`：`mean_total_return ≈ 0.00%`, `positive_asset_ratio = 0/3`, `mean_trades = 0.0`, `trade_count_retention = 0.00%`
- `breakdown_reclaim_short + lvn_rejection`：`mean_trades ≈ 0.33`，仍不足以形成可交易 admission
- `ema_pullback_long + lvn_rejection`：跨资产 `mean_total_return ≈ +1.40%`，但 `positive_asset_ratio = 1/3`，`trade_count_retention ≈ 22.45%`

翻成人话：
- `POC acceptance` 这层不是完全没信息；
- 但它留下的主要效果是**极窄 sample veto**，不是足够稳的 shared confirmation；
- 因此原 `park` 的审计意义必须保留：失败对象是“把 volume-profile acceptance 写成现有 base setup 的 queue-facing gate”，不是 volume-profile / POC 主题整体死亡。

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 hard park：
1. 原 clean replication 至少说明，比起直接让 base archetype 裸跑，`LVN rejection` / `acceptance` 一类结构在 long 侧确实留下了一点“少犯错”语义；
2. 新增的 volume-profile 旁证表明，`POC / value-area` 这类锚点并非零信息主题。

为什么又已明显偏硬：
1. 原 `acceptance gate` 读法在 clean replication 里已经被审计得很清楚：改善主要来自极端降频，甚至直接退化成零交易；
2. 最近最强新证据不再支持“把 acceptance 再收窄成 Rank 54b gate”，而是把主语改写成**单资产 rolling POC displacement raw alpha / feature family**；
3. 若现在硬写 `Rank 54b`，很容易模糊原审计边界，把“shared gate 失败”偷换成“volume-profile 主题未死”。

## Any salvage signal?
有，但更像“主题外流”，不是旧 rank 自身还能诚实窄救。

本轮最 relevant 的新旁证：
- `research/quant_digests/2026-04-03_2224_poc-valuearea-fill-sanity-alpha.md`

这条 digest 给出的关键信号是：
1. 真正更像样的主语不是 `LVN rejection + POC acceptance gate`；
2. 而是 **rolling POC / value-area displacement 本身**，也就是“价格偏离近期成交量重心后，向 POC / value area 回摆”的单资产 raw alpha / feature family；
3. 同时，这条 digest 还额外钉死了一个重要事实：repo headline 的大部分好看表现高度依赖乐观 fill，换成 `next-open` 后只剩很薄的毛边，更像 feature 候选而不是现成可上线策略。

换句话说：
- 可救信号存在；
- 但救的是 `rolling POC displacement / value-area excursion` 这条新 family；
- 不是旧 `Rank 54 / shared acceptance gate`。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向是：

> **replace shared LVN rejection + POC acceptance gate with a standalone rolling POC displacement / value-area excursion raw-alpha host**

也就是：
- 不再把 volume-profile acceptance 写成 `ema_pullback_long / breakdown_reclaim_short` 的 shared confirm；
- 只承认 `distance_to_POC / POC_drift / value-area excursion` 这类价量锚点特征本身，再单独测试它们在单资产 MR / stretch-veto / exhaustion 里的作用。

但这刀本轮**不够诚实地属于 `Rank 54`**，因为：
1. 它已经把主语从 `shared confirmation gate` 换成了 `single-asset raw alpha / feature family`；
2. 它不再保留旧 rank 的职责层；
3. 若硬写成 `Rank 54b`，本质是在借新 family 的名字替旧 gate 续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 54b`：
1. 原 `park` verdict 没被推翻；
2. 新增最强证据在把 volume-profile 主题推向新的 `rolling POC displacement / value-area excursion` raw-alpha family，而不是支持旧 shared-gate residual；
3. 原 rank 剩下的残余价值更像“acceptance 过严时会把样本砍空”的审计教训，而不是可 bot2 直接认领的新窄 gate；
4. 若后续 bot2 要认领，更诚实的做法应是直接认领新的 volume-profile raw-alpha / feature intake，而不是挂回 `Rank 54` 名下。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；最近新增的 rolling POC / value-area displacement 证据说明，Rank 54 的残余价值更像新的单资产 volume-profile raw-alpha / feature family，而不是旧 LVN rejection + POC acceptance shared gate 的诚实窄派生，不足以 draft Rank 54b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。
