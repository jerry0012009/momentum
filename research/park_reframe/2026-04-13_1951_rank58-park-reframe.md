# 2026-04-13 19:51 UTC · Rank 58 park reframe review

## Scope
- Source rank: `Rank 58 / event-anchored VWAP hold-reclaim spine`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，4 月 9 日新增的 `anchor-open displacement × session VWAP continuation` 证据，是否足以让 Rank 58 再诚实派生一条新的窄 reframe hypothesis。**

## Why this rank this round
- 按 `bot6` 当前轮转，默认仍优先 `Rank 50+`，且最近几轮已覆盖 `51/52` 与多条低号 rank，本轮补看 `Rank 58` 符合轮转节奏。
- `Rank 58` 上次 park-reframe 是 `2026-04-04 09:24 UTC`，已超过最近 `7` 天回避窗口。
- 这轮有明确新旁证：
  - `research/quant_digests/2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md`
- 真正要回答的是：**这条新证据是在救活旧的 shared event-anchored VWAP spine，还是其实已经把 VWAP / anchor 主题上移成一个新的 session-anchor raw-alpha 宿主。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-18_1524_rank58-clean-replication.md`
  - `research/park_reframe/2026-04-04_0924_rank58-park-reframe.md`
  - `research/quant_digests/2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 58` 的 blocker 这轮没有被推翻。

最小 clean replication 的主读法：
- `event_avwap_gate`
  - `mean_total_return ≈ -1.35%`
  - `positive_asset_ratio ≈ 44.44%`
  - `mean_trades ≈ 20.78`
  - `trade_count_retention ≈ 93.68%`
  - `false_follow_4bars ≈ 61.45%`
- 对照 `session_vwap_gate`
  - `mean_total_return ≈ -2.51%`
  - `positive_asset_ratio ≈ 22.22%`
- 更紧的 `event_avwap_gate + 0.5ATR proximity`
  - `mean_total_return ≈ -0.37%`
  - `mean_trades ≈ 11.44`
  - `trade_count_retention ≈ 53.53%`

time-pocket 也只有最后一段留下薄 pocket：
- `bucket_1 ≈ -1.05%`
- `bucket_2 ≈ -0.71%`
- `bucket_3 ≈ +0.54%`

翻成人话：
- `event anchor` 确实比 `session anchor` 更诚实；
- 但它仍然没有把三条 base setup 的 shared hold/reclaim spine 做成足够稳定的 post-cost admission layer；
- 更紧 proximity 的改善也开始明显带上“砍样本减亏”的味道。

所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**这轮仍读作 `soft park`，但比 4 月 4 日那轮更接近 hard。**

为什么还不是 hard park：
- `VWAP / anchor` 主题本身没有死；
- 原 clean replication 已证明 `event anchor > session anchor`，说明这不是完全没信息的变量。

为什么更接近 hard：
- 它留下的残余已经越来越不像一个独立 queue-facing reframe；
- 4 月 9 日的新证据把主语进一步改写成 **anchor-open displacement × session VWAP continuation 的 raw alpha**；
- 也就是说，最近新增证据救活的是“anchor session 的 primary trigger”，不是旧 Rank 58 这种横跨多条 setup 的 shared spine 角色。

## 3) 现有证据里是否存在“可救信号”？
**有，但它更明显是在支持新的 session-anchor / VWAP continuation raw-alpha 宿主，而不是支持 `Rank 58b`。**

### 可救信号 A：anchor + VWAP 主题仍然有信息
`2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md` 的核心信息是：
- 若 session open 之后先出现超出 same-minute 常态波动的 displacement，
- 且价格位于 session VWAP 同侧，
- 后续更像继续扩展，而不是立刻均值回归。

### 可救信号 B：它和 Rank 58 确实共享“anchor + VWAP + continuation”语义
这说明原 Rank 58 不是完全读错方向；
但问题在于，新证据的主语已经变成：
- **以 anchor-open displacement 为 primary trigger 的 session continuation raw alpha**。

而 Rank 58 原本的主语是：
- 给 `EMA / Fib / breakout` 三条已有 setup 加一个 shared `event-anchored VWAP hold/reclaim spine`。

这两者已经不是同一层。

## 4) 最值得改的唯一一刀是什么？
**如果硬要保留唯一一刀，最诚实的一刀不是继续打磨 shared VWAP spine，而是把主语收缩成：只交易 `anchor-open displacement` 之后、且价格仍在 anchor VWAP 同侧的 continuation pocket。**

也就是：
- 不再让 VWAP 充当三条 base setup 的共享 hold/reclaim spine；
- 只保留“anchor session 已经跑出异常位移，且仍站在 VWAP 强侧”这一件事。

但这恰恰说明它已经**不再是 Rank 58 的窄 reframe**：
- 它把角色从 `shared admission spine` 改成了 `primary session-anchor trigger`；
- 更像新的 raw-alpha family intake，而不是 `Rank 58b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
1. 原 `park` blocker 没被化解：作为 shared event-anchored VWAP spine，它仍未提供足够稳定的 post-cost 增量；
2. 4 月 9 日的新证据支持的是更上位的 `anchor-open displacement × session VWAP continuation` raw-alpha 宿主，不是旧 Rank 58 的 shared spine 写法；
3. 若现在硬写 `Rank 58b`，实质上是在把“新的 session-anchor raw alpha”误包装成“旧 rank 的窄 reframe”，审计上不诚实。

## 6) trade on / trade off 怎么读？
本轮不新增派生，只做审计式复述：

- `trade on`：
  - 原 Rank 58 若还保留任何残余价值，只能读成一句很窄的话：**锚点应该是事件/会话位移，而不是全天平均时钟；VWAP 更适合服务已启动的位移过程。**
- `trade off`：
  - 一旦把它写得足够有效，往往就会演变成“只做 anchor-open displacement 后的 primary continuation”；
  - 这时你得到的就不再是 shared spine，而是另一个独立 raw alpha；
  - 也就不该再算作 `Rank 58b`。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 4 月 4 日那轮更接近 hard`

## Minimal audit note
本轮不重开 `Rank 58`，也不新增 `Rank 58b`。

更诚实的记录是：**4 月 9 日新增的 `anchor-open displacement × session VWAP continuation` 证据，说明 anchor / VWAP 主题本身仍值得作为新的 session-anchor raw-alpha family 研究；但它并没有把原 `Rank 58` 的 shared event-anchored VWAP hold/reclaim spine 写法变成可诚实再派生的窄修改轴。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：共享工作区存在大量与本轮无关的脏文件与未跟踪产物，当前不适合安全 selective commit。
