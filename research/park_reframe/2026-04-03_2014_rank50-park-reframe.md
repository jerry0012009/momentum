# 2026-04-03 20:14 UTC · Rank 50 park reframe

## Selected rank
- `Rank 50`
- selection note: 本轮继续遵循 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，且优先避开最近 `7` 天内已被 bot6 复盘的条目。`Rank 50` 自 `2026-03-18` clean replication 压回 `park` 后，尚未被 bot6 单独复盘；同时它位于 `50+` 优先号段，且与最近新增的 `close-confirmed CHoCH` / `turning-point confirmed continuation` 结构旁证存在主题邻近，适合判断一次：这些新证据是在救旧 `Rank 50`，还是只是在把“结构确认”主题继续外流到别的宿主。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_0738_rank50-source-intake-guard-passed.md`
- `research/optimization_loop/2026-03-18_0829_rank50-clean-replication-park.md`

原 `Rank 50` 被 park 的原因没有变：它把 **chanlun-pro / structural reclaim** 写成一条可同时服务 breakout / Fib / EMA-PSAR 的共享结构确认层，但最小 clean replication 证明，这条线虽然比最原始 `raw_breakout_retest` 少亏，却主要靠**大幅砍交易**换来，且 post-cost 仍明显为负。

冻结版关键结果（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `no-overlap`）：
- `raw_breakout_retest @ 6bps/side`: `mean_total_return ≈ -9.34%`, `mean_trades ≈ 82.3`
- `structural_reclaim @ 6bps/side`: `mean_total_return ≈ -4.85%`, `mean_trades ≈ 12.7`
- `structural_reclaim_plus_htf @ 6bps/side`: `mean_total_return ≈ -4.63%`, `positive_asset_ratio = 0/3`, `mean_trades ≈ 12.0`, `mean_false_reclaim_ratio ≈ 72.78%`, `mean_no_trade_ratio ≈ 87.14%`

翻成人话：
- “回踩后再 reclaim 结构”这个方向不是完全胡说；
- 但它留下的改善主要来自把交易切得极稀；
- 而且 `false reclaim` 比例很高，说明很多看似结构站回的时刻，本质只是噪音回抽；
- 因此原 `park` 的审计意义必须保留：**失败对象是“把 structural reclaim 写成 queue-facing、跨宿主可复用的共享确认 gate”这件事，不是结构确认主题整体死亡。**

## Hard park or soft park?
- 本轮判断：`soft park，但已明显偏硬`

为什么不是 hard park：
1. 相比 `raw_breakout_retest`，`structural_reclaim` 系列确实稳定少亏，说明“等待结构重获接受”至少比直接追 break 更接近主题本体；
2. `false_reclaim_ratio` 这类失败形状信息，说明这条线不是零信息，而是“信息大多落在失败判决上”。

为什么又已明显偏硬：
1. `positive_asset_ratio = 0/3`，说明它没有形成可部署 pocket；
2. `mean_no_trade_ratio ≈ 87.14%`，shared gate 角色主要靠极端降频成立；
3. 最近几轮 park-reframe 已经把相邻的结构确认残余分别分流到更诚实的宿主：
   - `Rank 31b`：false reclaim failure-followthrough
   - `Rank 53`：close-confirmed CHoCH / liquidity-sweep failure gate
   - `Rank 103`：confirmed extremum / honest anchor
4. 因而 `Rank 50` 再要重开，很容易只是重复这些相邻宿主已经吸收过的结构语义。

## Any salvage signal?
有，但更像“残余被别的宿主吸收”，不是 `Rank 50` 自己还值得诚实派生。

本轮最 relevant 的旁证：
- `research/quant_digests/2026-03-18_1017_close-confirmed-choch-compression-gate.md`
- `research/quant_digests/2026-03-31_2248_turning-point-confirmed-tsmom-alpha.md`
- `docs/PARK_REFRAME_QUEUE.md` 里既有的 `Rank 31b` / `Rank 53` / `Rank 103` 结论

这些证据合起来给出的关键信号是：
1. `Rank 50` 原始主题里真正留下的信息，不像“回踩 reclaim 本身就是共享入场键”；
2. 更像两条已经被别处吸收的残余：
   - **失败侧**：false reclaim / re-entry inside 之后的 failure-followthrough（已更诚实地落在 `Rank 31b` 一类宿主）；
   - **趋势侧**：confirmed turning-point / close-confirmed structure acceptance（最近更像新的 structure-aware trend raw-alpha family，已把 `Rank 53 / 103` 这类主题继续往外推）；
3. 换句话说，可救信号存在，但它们已经不再专属于 `Rank 50`。

## Single best cut
如果只保留唯一一刀，本轮最像样的改写方向会是：

> **replace shared structural-reclaim confirmation gate with a structure-acceptance / failure-verdict host**

也就是：
- 不再把 `structural_reclaim` 当成三条 base setup 的共享 admission；
- 只承认它在“结构是否被真正接受，还是只是短暂 reclaim 后重新掉回去”这一层还有信息量；
- 但这条一刀现在已经被更诚实的邻近宿主基本吸收：
  - 走 failure-followthrough，就是 `Rank 31b` 那一路；
  - 走 close-confirmed / turning-point continuation，则更像 `Rank 53 / 103` 旁边的新 structure-aware raw-alpha family。

所以这刀**有方向感，但不再值得以 `Rank 50b` 的名义单独 draft**。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这次不值得 draft `Rank 50b`：
1. 原 `park` verdict 没被推翻；
2. 原 rank 唯一还诚实的残余，不是新的 queue-facing admission，而只是“结构接受 / 失败判决”这一层信息；
3. 这层残余已经被邻近提案与新 family 更干净地吸收：继续挂在 `Rank 50` 名下，只会重复已有宿主；
4. 若现在硬写 `Rank 50b`，大概率会落入两种不诚实情况之一：
   - 要么偷换成 `Rank 31b` 式的 failure short；
   - 要么借 turning-point confirmed continuation 这种新 raw-alpha family 给旧 rank 续命。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已明显偏硬；Rank 50 的 residual value 更像 structure-acceptance / false-reclaim verdict 信息，而这条唯一诚实修改轴已基本被既有 Rank 31b 与相邻 close-confirmed / turning-point 结构宿主吸收，不足以再诚实派生 Rank 50b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动；且仓库长期存在共享脏文件风险，避免混提。
