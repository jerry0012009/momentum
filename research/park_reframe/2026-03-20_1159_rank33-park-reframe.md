# 2026-03-20 11:59 UTC · Rank 33 park reframe review

- source rank: `Rank 33 / endpoint NW + confirmed HL reclaim / causal swing persistence gate`
- final verdict: `keep_park`
- original verdict kept: `park / evidence pool`
- park type: `soft park`
- touched scope: `Rank 33` only

## 为什么这轮看 Rank 33
- 按 `bot6` 规则，这轮只处理 1 条已 `park` rank。
- `Rank 33` 属于 `Rank 1~37`，且最近 `7` 天内还没有进入 `park-reframe` 轮次。
- 它原始失败不是“完全没料”，而是典型的 **结构过滤更干净、但收益没有一起被救活**；这类 rank 最适合低频复盘一次，判断有没有单轴窄救法。

## 原 rank 为什么 park
原始 `Rank 33` 已完成 `source intake -> 最小 clean replication`，结论相当清楚：
- `raw_extrema_reclaim @ 6bps/side`：`mean_total_return≈-1.72%`、`positive_asset_ratio=1/3`、`mean_false_reclaim_ratio≈49.13%`
- `nw_hl_reclaim @ 6bps/side`：`mean_total_return≈-1.39%`、`positive_asset_ratio=1/3`、`mean_false_reclaim_ratio≈47.20%`
- `nw_hl_plus_highbreak @ 6bps/side`：`mean_total_return≈-8.51%`、`positive_asset_ratio=1/3`、`mean_false_reclaim_ratio≈20.07%`、`mean_no_trade_ratio≈98.71%`
- time-pocket 也不干净：主变体是典型 `bucket_1 负 / bucket_2 正 / bucket_3 负`

翻成人话：
- `endpoint NW + confirmed HL/LH` 的确让结构定义更干净、假 reclaim 率更低；
- 但它没有把这条线从 post-cost 负 pocket 里拉出来；
- 一旦再叠 `highbreak`，又明显滑向“靠砍样本换更好外观”。

所以原 verdict 被如实压回 `park / evidence pool`，不是因为“结构主题彻底没信息”，而是因为 **把它写成 standalone reclaim entry 这层角色不够诚实**。

## 它更像 hard park 还是 soft park
我把它归为 **`soft park`**。

原因：
- hard 的部分：`NW smoother + confirmed HL reclaim` 作为一条独立 queue-facing entry，当前已经基本审计完；
- soft 的部分：它留下来的残余信息更像 **上游结构测量 / anchor correction**，而不一定是主题本身完全无效；
- 也就是说，该被关掉的是“它自己就是独立 entry alpha”这层读法，而不是“confirmed extremum / confirmed swing 对后续 retest/failure 判断有帮助”这个更窄主题。

## 现有证据里有没有“可救信号”
有，但已经被近邻新证据基本消费，而且结果不够支持继续派生。

最自然的可救信号其实只有一条：
- **把 `NW + confirmed HL reclaim` 从 standalone entry，降级成更上游的 `confirmed extremum / honest anchor` 口径修正层。**

这条线最近已经被更贴题的新证据承接过：
1. `2026-03-19_2220_confirmed-extremum-honest-fib-anchor.md`
   - 明确指出：真正更有信息的，不是“NW 之后的 HL reclaim 自己开仓”，而是 **BMS 后先等 extremum 真正确认，再画 Fib / 再判 retest 深度**。
2. `2026-03-20_0054_rank103-clean-replication-park.md`
   - 这条近邻新线已经把最自然的救法正式落成 queue-facing 候选：`Rank 103 / confirmed extremum honest fib anchor`；
   - 结果是 admit rate 确实提高了，但 `proxy post_cost_expectancy` 仍约 `-4bps`，最终也被压回 `park / evidence pool`。

所以，`可救信号` 不是没有，而是：
- 已经被一条更窄、更诚实、且更贴原始 blocker 的近邻新线消费过；
- 消费结果不足以支持再从 `Rank 33` 派生一个新的 `33b`。

## 最值得改的唯一一刀是什么
如果只从主题连续性上讲，最自然的唯一一刀仍然是：
- **把 standalone `NW + confirmed HL reclaim` 改写成 `confirmed extremum / honest anchor` 上游口径修正层。**

但关键在于：
- 这刀已经被 `confirmed extremum honest fib anchor` 近邻实验实际执行；
- 而且执行后仍然没有形成足够诚实的 desk uplift。

因此，对 `bot6` 这轮来说，最值得做的不是再写一条 `Rank 33b`，而是：
- **承认 Rank 33 最自然的单轴救法已经被消费，当前不重复派生。**

## 是否值得形成新的 derived hypothesis
**不值得。**

原因：
1. 原 `park` 并不是因为“还没想到怎么把结构确认写得更诚实”；
2. 最自然的窄救法——`confirmed extremum / honest anchor`——已经由近邻 `Rank 103` 代打过；
3. 这条代打结果仍停留在 measurement correction，而没有升成可推进的 queue-facing candidate；
4. 如果现在硬写 `Rank 33b`，很容易滑向多轴改写（改 anchor、改 setup、改 long/short 非对称、改 failure verdict），这超出了 `bot6` 单轮只改一刀的边界。

## 本轮结论（按固定问题回答）
1. **原 rank 为什么 park？**
   - 因为它把结构定义做得更干净了，但没有把收益、跨资产、时间稳定性一起救活；加 `highbreak` 后更明显变成砍样本。
2. **更像 hard park 还是 soft park？**
   - `soft park`。
3. **有没有可救信号？**
   - 有，主要是“把它降级成 confirmed extremum / honest anchor 上游口径修正层”；但这条最自然救法已经被近邻 `Rank 103` 基本消费。
4. **最值得改的唯一一刀是什么？**
   - 把 standalone reclaim entry 改写成 confirmed-extremum anchor correction；但这刀已被验证过且未通过。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。

## 对 queue 的最小写回口径
- 保留 `Rank 33 = park / evidence pool` 的审计意义；
- 本轮只补一条 recently reviewed 记录；
- 不新增 `Rank 33b`，也不改 `TODO` 顶部排班。

## 相关证据锚点
- `research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`
- `research/quant_digests/2026-03-19_2220_confirmed-extremum-honest-fib-anchor.md`
- `research/optimization_loop/2026-03-20_0054_rank103-clean-replication-park.md`
- `reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_clean_replication.html`

## Git / 提交
- 本轮只做最小必要文件改动。
- 未做 commit；原因是当前工作区长期存在较多无关脏文件，本轮按要求避免混提。
