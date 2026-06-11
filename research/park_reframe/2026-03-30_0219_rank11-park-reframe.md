# 2026-03-30 02:19 UTC｜bot6 park-reframe｜Rank 11

## 0) 本轮选择
- 按 `bot6 park-reframe loop` 规则，本轮仍只处理 `Rank 1~37` 中已 `park` 的 1 条。
- `Rank 50+` 与 `80~110` 最近已连续覆盖；`1~24` 中又要尽量避开近 7 天刚复盘过的条目。
- `Rank 11` 上次复盘是 `2026-03-24 02:04 UTC`，已略超 7 天窗口；同时 3/28~3/29 新增的 `directional-change overshoot / abnormal-regime` 与 `thresholded directional state-machine` 旁证，让“事件驱动 final-verdict family”这条上位吸收线更清楚，因此本轮回看它是否还有诚实派生空间。

## 1) 原 rank 为什么 park？
原始审计来自：
- `research/optimization_loop/2026-03-16_2343_rank11-clean-replication-park.md`
- `research/park_reframe/2026-03-24_0204_rank11-park-reframe.md`

原 Rank 11（`Lo-style causal extrema pattern gate`）被 park，核心原因不是“差一个更聪明的确认层”，而是 trigger 本体就没有形成可复用主体 pocket：
- `mean_total_return ≈ -4.33%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 58.3`
- Light Stability Pack 四项一起 fail：
  - 时间稳定性：`1/3`
  - 参数稳定性：`0/5`
  - 跨标的稳定性：`0/3`
  - 成本/交易数稳定性：`0/4`

翻成人话：
- 这不是“确认层太粗”型失败；
- 而是 pattern trigger 自身在 15m BTC/ETH/SOL 上就没展现出够稳、够厚、够可迁移的主体 edge；
- 所以原 `park` verdict 的审计意义必须保留。

## 2) 它更像 hard park 还是 soft park？
**结论：仍是 `hard park`，而且比 2026-03-24 更确认。**

原因：
1. 原始 clean replication 的失败是全维度的，不是单一实现瑕疵；
2. 3/23 那批 `phase-state / FT-NFT / post-break router` 证据，已经说明新增信息更适合做共享 follow-up verdict；
3. 3/28~3/29 新增的 `Directional Change overshoot + abnormal-regime` 与 `thresholded directional state-machine` 更进一步把残余价值往 **event-driven verdict / abstain raw-alpha family** 上推，而不是往 `Rank 11` 这种旧 pattern trigger 上回流。

也就是说，新的可救信息不是在救 `Rank 11` 本体，而是在说明：
- 真正活下来的，是更上位的事件型判决骨架；
- 不是 `Lo-style causal extrema pattern` 这条旧触发再叠一层 router 就能诚实复活。

## 3) 有没有“可救信号”？
**有一点主题级可救信号，但没有 `Rank 11` 专属可救信号。**

可救的不是 `Rank 11` 本身，而是它旁边那类“break 后怎么判 continuation / failure / abstain”的语言：
- `2026-03-23_0312_ft-nft-killzone-postbreak-router.md`
- `2026-03-22_2028_dc-first-hit-followup-verdict-gate.md`
- `2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`
- `2026-03-29` 的 thresholded directional state-machine 旁证（已在近期 park-reframe 里被 Rank 33 吸收）

这些证据共同说明：
- post-break 路径判决未死；
- 但它更像给现有更强 setup 的 **event-driven final-verdict / abstain layer** 提供语言；
- 不是给一个已 hard-fail 的 pattern trigger 再包一层“也许能行”的二次守门。

## 4) 最值得改的唯一一刀是什么？
如果硬要写，唯一像样的一刀仍然只能是：
- **把 `Rank 11` 从 pattern gate 改写成 `pattern event -> event-driven final-verdict / abstain router`。**

但本轮结论是：**这刀现在也不诚实。**

原因：
- 这已经不是在修 Rank 11 的 trigger，而是在把它的残余语义整体上移到更通用的 event-driven verdict family；
- 一旦这么写，`Rank 11b` 会和近期更强、也更通用的 failure-routing / abstain / directional-change verdict 线高度重叠；
- 它不再保留足够独立、足够 queue-facing、足够单轴的 `Rank 11` 特有价值。

所以更诚实的答案是：
- **没有值得为 Rank 11 单独保留的新一刀。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

最终结论：`keep_park`

原因：
1. 原始 blocker 没被推翻；
2. 新证据继续往上位的 event-driven verdict / abstain family 汇聚，不往 Rank 11 回流；
3. 现在硬写 `Rank 11b`，本质是在把“pattern 本体失败”包装成“再叠一个 post-break router 也许能救”，不够诚实。

## 6) 本轮模板回答
- **原 rank 为什么 park？**
  - 因为 clean replication 后收益、时间、参数、跨资产、成本五个层面一起偏弱，trigger 本体没有形成可复用 edge。
- **更像 hard park 还是 soft park？**
  - `hard park`，而且比 2026-03-24 更确认。
- **有没有可救信号？**
  - 有主题级可救信号，但它属于更上位的 event-driven final-verdict / abstain family，不属于 Rank 11 专属救法。
- **最值得改的唯一一刀是什么？**
  - 若硬写，只能是 `pattern event -> event-driven final-verdict / abstain router`；但这刀对 Rank 11 已不诚实。
- **是否值得形成新的 derived hypothesis？**
  - 不值得，维持 `keep_park`。

## 7) 最小审计结论
- 原 `park` 保留；
- `Rank 11` 本轮仍读作 **hard park**；
- 而且比 2026-03-24 更确认：最近新增证据继续说明残余价值应上移到更通用的 event-driven verdict / abstain family，而不是诚实派生 `Rank 11b`。

## 8) 文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 9) Git
- 未 commit。
- 原因：只做最小必要文档改动；workspace 仍有大量无关脏文件，不安全混提。
