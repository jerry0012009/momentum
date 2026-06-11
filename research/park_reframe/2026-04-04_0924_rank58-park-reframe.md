# 2026-04-04 09:24 UTC — Rank 58 park reframe review

## 本轮选择
- 按 `bot6` 轮转，当前仍优先 `Rank 50+`；最近 7 天已复盘 `50/51/52/54/57/62/67/79/84/87/101/103` 等条目，因此本轮补看 **`Rank 58`**，避免继续重复同一批近期 rank。
- `Rank 58 / event-anchored VWAP hold-reclaim spine` 上次低频复盘是 `2026-03-27`，已超过 7 天；且过去 24 小时新增了更直接的 VWAP 相关旁证，值得再判断一次它是否还能诚实派生新窄轴。

## 读集
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1505_rank58-source-intake.md`
- `research/optimization_loop/2026-03-18_1524_rank58-clean-replication.md`
- `research/park_reframe/2026-03-27_1022_rank58-park-reframe.md`
- `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`

## 原 rank 为什么 park
原 `Rank 58` 想做的是：
- 把 `VWAP` 从 session 锚点改成 **event anchor**；
- 让它服务 `breakout_short / Fib retest_hold / EMA-PSAR continuation` 三条主线，充当 shared `hold / reclaim spine`；
- 也就是说，它不是独立 alpha，而是“这次事件以后，新库存成本线有没有被守住”的统一确认层。

但最小 clean replication 的冻结结果已经很清楚：
- `event_avwap_gate` 虽然比 `session_vwap_gate` 更不差，但主读法仍是 **成本后负收益**：`mean_total_return ≈ -1.35%`
- `false_follow_4bars ≈ 61.45%` 仍高，说明它没把 shared hold/reclaim 做成足够干净的 admission 证据
- 更紧的 `+0.5ATR proximity` 只把亏损收窄到约 `-0.37%`，但 `trade_count_retention ≈ 53.53%`，改善已经明显带上“靠砍样本美化”的味道
- time-pocket 只剩 `bucket_3` 的轻微正 pocket，不构成可升格的跨时间稳定性

翻成人话：
**原 Rank 58 的问题不是“event anchor 比 session anchor 更差”，而是“即便换成更诚实的 event anchor，它也仍然不够强，撑不起三条 setup 共用的 shared spine 角色”。**

## 它更像 hard park 还是 soft park
**结论：`soft park`，但现在比 3/27 那轮更偏硬。**

为什么仍算 soft park：
- `VWAP` 主题本身没死；
- `event anchor 比 session anchor 更诚实` 这一点仍有审计价值。

为什么又更偏硬：
- 它留下的唯一残余，越来越不像一个独立 queue-facing 假设；
- 最近新证据把 VWAP 主题继续外流到两个更诚实的宿主：
  1. 既有 `Rank 30b` 这类 **post-breach event-anchored hold/reclaim confirm**；
  2. 新出现的 **`VWAP-EMA directional-change trend shell`**（`2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`）。

也就是说，`Rank 58` 剩下的不是“还能再写一个 58b”，而是“VWAP 变量该去哪一层更合适”。

## 有没有可救信号
**有，但已更明显地不属于 `Rank 58` 本体。**

本轮能看到的可救信号只有一条：
- **VWAP 主题仍然有信息，但更适合做更窄的事件确认宿主，或直接进入新的 trend-shell raw-alpha 宿主。**

最近新增旁证进一步把这点钉死：
- `2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md` 说明，VWAP 更自然的角色可以是 `VWAP-EMA` 状态变量的一部分，去服务 directional-change / trend-shell 主语；
- 而 `2026-04-04 00:38 UTC | Rank 51` 的最新低频复盘也已把相邻 `session VWAP reclaim + breadth` 的残余价值收口为：**VWAP 主题正在外流到 event-anchored hold/reclaim 宿主或 VWAP-EMA trend shell**。

所以可救的不是：
- 再写一个“跨三条 setup 共用的 shared VWAP spine”；

而是：
- 承认 VWAP 该继续退到更具体的宿主里。

## 最值得改的唯一一刀是什么
如果只保留 **1 条唯一主修改轴**，本轮最值得改的一刀仍然是：

**把 `Rank 58` 从“跨 setup 的 shared event-anchored VWAP spine”继续收窄成“只服务单一宿主的 post-event hold/reclaim confirm”，默认更接近既有 `Rank 30b` 这类 breach-event host，而不是继续横向服务 EMA / Fib / breakout 三线。**

但这刀本轮**不值得再单独写成新的 `Rank 58b`**，因为：
1. 这不是新轴，而是对既有 `Rank 30b` 的重复记账；
2. 最近新证据同时把另一部分 VWAP 残余抬升到 `VWAP-EMA trend shell`，说明 `Rank 58` 继续当中间层宿主的必要性更弱；
3. 若现在硬写 `Rank 58b`，会模糊原 `park` verdict 的审计边界。

## 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

原因：
- 原 `park` blocker 没被推翻：作为 shared event-anchored hold/reclaim spine，它仍未给出足够稳定的 post-cost 增量；
- 唯一诚实修改轴已被既有 `Rank 30b` 基本吸收；
- 最近新增的 `VWAP-EMA` trend-shell 旁证又把 VWAP 主题进一步外流到更上位的新宿主，不再适合绑回 `Rank 58` 血缘里。

## 模板回答
1. **原 rank 为什么 park？**
   - 因为 event-anchored VWAP 虽比 session VWAP 更诚实，但作为三条 setup 共用 shared spine 仍成本后为负、false follow-through 仍高，且更紧 proximity 改善明显依赖砍样本。
2. **更像 hard park 还是 soft park？**
   - `soft park`，但比上次复盘更偏硬。
3. **有没有可救信号？**
   - 有；但更像 VWAP 主题应继续退到更具体的 event host 或 VWAP-EMA trend shell，而不是救原 `Rank 58` 本体。
4. **最值得改的唯一一刀是什么？**
   - 把 shared event-anchored VWAP spine 继续收窄成单一宿主的 post-event hold/reclaim confirm。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。

## 最小审计结论
- 保留原 `park` verdict；
- `Rank 58` 本轮仍记为 **`keep_park`**；
- 它留下的不是值得新写 `Rank 58b` 的独立残余，而是应继续由既有 `Rank 30b` 与新出现的 `VWAP-EMA trend shell` 各自承接的 VWAP 主题残余。

## Git
- 本轮只做 park-reframe 所需最小文本更新；不改 `docs/TODO.md`，不做混合提交。
