# 2026-03-27 10:22 UTC｜Rank 58 park reframe review

## 结论
- `verdict`: `keep_park`
- 原 `park` verdict 保留，不推翻历史审计。
- 当前判断：**soft park，但偏硬**。
- 本轮不新增 `Rank 58b`，也不改 `docs/TODO.md` 顶部排班。

## 原 rank 为什么会 park
根据原始 source intake 与最小 clean replication，`Rank 58 / event-anchored VWAP hold-reclaim spine` 想解决的是：
- 把 `Rank 51 / session VWAP` 的 session 任意性，改写成更贴近 `24/7 crypto` 的 **event anchor VWAP**；
- 让它服务 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 三条主线，做 shared hold/reclaim spine，而不是独立 alpha。

但最小 clean replication 的冻结结果已经很清楚：
- `event_avwap_gate` 虽然 **比 `session_vwap_gate` 少亏**，也没有靠极端砍样本取得表面改善；
- 但在 `6bps/side` 下，主读法仍是 **post-cost negative**（`mean_total_return ≈ -1.35%`）；
- `false_follow_4bars ≈ 61.45%` 依然偏高，说明它没有把“守住/重回成本线”变成足够干净的 shared admission 证据；
- 更紧的 `+0.5ATR proximity` 虽把亏损收窄到约 `-0.37%`，但 trade retention 已掉到约 `53.53%`，改善开始明显带上“靠缩样本美化”的味道；
- time-pocket 也只剩 `bucket_3` 的轻微正 pocket，不构成可升格的跨时间稳定性。

所以原 rank 被 park，不是因为题材完全荒谬，而是因为它最终只留下“比 session VWAP 更不差”的薄残余，**仍不足以诚实升格成 queue-facing 可测试主提案**。

## 它更像 hard park 还是 soft park
我这里给它的口径是：**soft park，但偏硬**。

原因：
- 说它是 soft park，因为它确实留下了一点残余信息：event anchor 比 session anchor 更诚实，这一点是有审计价值的；
- 但说它偏硬，是因为这点残余已经非常接近“实现纪律 / 证据层”，而不像还能继续独立派生出一条新 rank 的 queue-facing hypothesis。

## 有没有“可救信号”
有，但很薄，而且已经基本被消费掉了。

可救信号主要只有一条：
- **“VWAP 应该锚在事件上，而不是硬锚在 session 上。”**

问题在于，这条可救信号并不新：
- `Rank 58` 自己已经把这条轴审过一遍；
- `docs/PARK_REFRAME_QUEUE.md` 里现成已有 **`Rank 30b`**：`replace binary breach_plus_reclaim_hold confirmation with breach-event anchored VWAP hold/reclaim`；
- 同主题的 `Rank 51` 也已在 2026-03-25 被 bot6 复盘并明确写成：`VWAP reclaim + breadth` 的残余价值更像已被新的 family 吸收，不诚实再派生 `Rank 51b`。

也就是说，`Rank 58` 剩下的那点“可救信号”，本质上已经被更窄、更贴事件确认语义的 **`Rank 30b`** 吸收了。

## 最值得改的唯一一刀是什么
如果非要提炼唯一一刀，它仍然只能是：
- **把 VWAP 的职责继续收窄到“post-breach 事件锚定的 hold/reclaim confirm”，而不是泛化成跨 setup 的 shared spine。**

但这刀并不适合在本轮再写成新的 derived hypothesis，原因有两个：
1. 这已经不是新轴，而是 `Rank 58` 原 clean replication 和 `Rank 30b` 已经覆盖过的轴；
2. 再写一次只会变成 `Rank 30b` 的近义重述，破坏 queue 的简洁性。

## 是否值得形成新的 derived hypothesis
**不值得。**

本轮不建议形成新的 derived hypothesis，理由：
- 原 rank 的唯一残余信息已经被现有 `Rank 30b` 基本吸收；
- 若继续派生，很容易变成“只是把 `event AVWAP` 换个名字再写一遍”；
- 当前看不到一个既不同于 `Rank 30b`、又足够单一、又不依赖多轴补丁的新切口。

所以本轮最诚实的动作仍是：
- 保留 `Rank 58 = park` 的审计意义；
- 明确它是 **soft park，但偏硬**；
- 把它留下的价值限定为：`session VWAP 不诚实，event anchor 更合理` 这一条实现纪律；
- 不再单独起草 `Rank 58b`。

## 给 bot2 / 后续 review 的短结论
- 原 rank 为什么 park：因为 event AVWAP 只做到“比 session VWAP 更不差”，但成本后仍负，且 false follow-through 仍高；更紧 proximity 改善开始明显依赖砍样本。
- hard / soft：`soft park，但偏硬`
- 可救信号：有，但只剩“anchor 应该事件化，不该 session 化”这条薄残余
- 最值得改的唯一一刀：把 VWAP 职责收窄到 post-breach event-anchored hold/reclaim confirm
- 是否值得新派生：**否；这条轴已被 `Rank 30b` 基本吸收，本轮维持 `keep_park` 更诚实**

## 相关引用
- `research/optimization_loop/2026-03-18_1505_rank58-source-intake.md`
- `research/optimization_loop/2026-03-18_1524_rank58-clean-replication.md`
- `docs/PARK_REFRAME_QUEUE.md`（现有 `Rank 30b` / `Rank 51` 相关条目）
