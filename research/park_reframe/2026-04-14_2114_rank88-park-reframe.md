# 2026-04-14 21:14 UTC — Rank 88 park reframe review

- 时间：2026-04-14 21:14 UTC
- 对象：`Rank 88 / macro-event blackout + size-down risk overlay`
- 本轮结论：`keep_park`
- 原 `park` verdict：保留，不推翻

## 本轮为什么看 Rank 88
- 轮转上，近两天 `50~79` 与部分低号 rank 已连续覆盖；本轮切回 `80~110` 号段。
- `Rank 88` 上次 park-reframe 复盘是 `2026-03-31`，已超过 `7` 天，符合低频复查要求。
- 4 月上旬之后又新增了两组直接相关的新证据：
  - `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`
  - `research/quant_digests/2026-04-13_0156_infra-vs-reg-shock-voloverlay.md`
- 本轮要回答的不是“宏观事件还有没有用”，而是：**这些新证据会不会让旧的 `Rank 88` 诚实地长出一条新的窄 reframe。**

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-03-31_0035_rank88-park-reframe.md`
- `research/optimization_loop/2026-03-19_1149_rank88_macro_event_overlay_intake.md`
- `research/optimization_loop/2026-03-19_1201_rank88-clean-replication-park.md`
- `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`
- `research/quant_digests/2026-04-13_0156_infra-vs-reg-shock-voloverlay.md`

## 1) 原 rank 为什么 park？
原 `Rank 88` 被 park 的原因没有变化：
- 它把 `FOMC / CPI` 等 scheduled macro event 写成了一个 **`15m` 三条 setup 共用的 generic `blackout / size-down / hybrid` overlay**；
- 最小 clean replication 已经审计清楚，这层 shared overlay **覆盖太稀、改善太弱、也没有跨 lane 增量**。

原始 replication 的关键事实仍然成立：
- `pm1h_trade_share≈0.81%`，说明核心事件窗只覆盖极少数交易；
- `size_down_0.5x`、`blackout[-1h,+1h]`、`hybrid` 都没有把 post-cost 结果拉回 baseline 之上；
- `ema_psar_long / fib_retest_long / breakout_short` 没有任何一条被明确修好。

所以原 park 审计结论仍是：
> **失败的不是“macro event timing 完全没信息”，而是“generic 15m shared blackout/size-down overlay”这版 Rank 88 写法不诚实。**

## 2) 它更像 hard park 还是 soft park？
本轮判断：**`soft park`，但比 3 月 31 日那轮更接近 hard。**

原因：
- 主题本身没死，scheduled macro event 仍然值得写进 desk；
- 但 4 月新增证据没有把旧 Rank 88 救回 shared overlay，反而继续把残余价值往两个别的宿主上迁移：
  1. **announcement-time event-driven raw alpha**（事件后第一段真实 impulse + pre-event sentiment gate）；
  2. **shock-type-aware risk overlay**（infrastructure vs regulatory shock 的 volatility / veto / size-down 层）。

换句话说：
- 对“macro event 有信息”这件事，仍是 soft；
- 对“Rank 88 这版 generic shared blackout/size-down overlay”，已经更接近 hard。

## 3) 现有证据里有没有“可救信号”？
**有，但都是主题级残余，不再像 Rank 88 自己的 rank-level 可救信号。**

### 可救信号 A：宏观事件更像 event-driven raw alpha，而不是纯 blackout
`2026-04-05` 的 digest 把最重要的一点说得更清楚了：
- 真正值得先 trade 的不是“event 前先停机”，而是 **announcement 后第一段真实 impulse**；
- `pre-event sentiment` 更像 admission / amplitude gate，而不是方向按钮。

这条证据的含义是：
- macro timing 没死；
- 但它救活的是 **event-time raw alpha shell**，不是旧 `Rank 88` 的 generic blackout overlay。

### 可救信号 B：不同坏消息更该改变的是 risk template，不是 shared blackout
`2026-04-13` 的 digest 又把另一层说清楚：
- infrastructure shock 与 regulatory shock 的 return channel 未必显著分开；
- 但 volatility / fragility / execution deterioration 的后果可以差很多；
- 所以更值得写的是 **shock-type-aware volatility veto / size-down overlay**。

这条证据的含义是：
- macro / event 主题仍有强残余；
- 但这层残余更像 **event taxonomy risk overlay**，而不是旧 `Rank 88` 那种把不同宏观事件混成一个固定时间黑窗的 shared 读法。

## 4) 最值得改的唯一一刀是什么？
如果硬要从旧血缘里保留“唯一最值得改的一刀”，本轮唯一还算诚实的表达是：

> **把 generic `macro-event blackout + size-down` 改成 event-type-specific execution / risk overlay；第一落点优先是 `scheduled macro impulse` 与 `infra-vs-reg shock` 分开处理，而不是继续把不同事件混成同一个 fixed blackout window。**

但这刀本轮**不值得 draft 成 `Rank 88b`**，因为：
1. 这已经不是对原 `Rank 88` 的窄修，而是在换主语；
2. 它天然会拆成至少两条不同宿主：`event-driven raw alpha shell` 与 `shock-type risk overlay`；
3. 若继续挂在 `Rank 88` 名下，只会模糊原 `park` verdict 的审计边界。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论仍是 `keep_park`。**

原因：
- 原 `park` blocker 没被推翻；
- 新证据没有说明“旧 generic blackout overlay 只差一刀”；
- 相反，新证据继续说明：
  - 一部分 residual 应上移到 **announcement-time raw alpha**；
  - 另一部分 residual 应重写成 **shock-type-aware risk overlay**；
- 这两条都不再是诚实的 `Rank 88b`。

## 6) 按模板直答
1. **原 rank 为什么 park？**  
   因为 `15m` 三线共用的 generic `blackout / size-down / hybrid` overlay 覆盖极少、post-cost 没改善，也没有修好任一 archetype。

2. **它更像 hard park 还是 soft park？**  
   `soft park`，但比 3 月 31 日那轮更接近 hard。

3. **有没有“可救信号”？**  
   有，但属于主题级残余：一条流向 announcement-time raw alpha，另一条流向 shock-type risk overlay；都不再像旧 Rank 88 本体可救。

4. **最值得改的唯一一刀是什么？**  
   把 generic macro blackout 改成 event-type-specific execution / risk treatment，不再混写成同一个 fixed blackout window。

5. **是否值得形成新的 derived hypothesis？**  
   不值得。

## 最终结论
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 3 月 31 日那轮更接近 hard；4 月新增证据继续说明 macro/event 主题仍有信息，但它救活的是 announcement-time raw alpha shell 与 shock-type-aware risk overlay，而不是旧 Rank 88 的 generic 15m shared blackout/size-down 写法，因此当前不诚实 draft Rank 88b。`

## 对 queue 的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引；
- `docs/PARK_REFRAME_QUEUE.md`：只追加一条最近复盘记录；
- 不新增 `Rank 88b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮不做 commit。
- 原因：共享工作区仍有大量无关脏文件；本轮只做最小必要文档更新，避免混提。
