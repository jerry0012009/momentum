# 2026-03-29 14:19 UTC · Rank 16 park reframe review (revisit)

## Scope
- Source rank: `Rank 16 / ORB threshold + protective closing session gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，3/28 新增的 session-anchor intraday TSMOM 证据，是否值得把 Rank 16 再派生成一个新的窄 reframe（超出既有 `Rank 16b`）**

## Why revisit Rank 16 (7-day rule note)
- `Rank 16` 上一次 park-reframe 是 `2026-03-22 20:41 UTC`，仍在 7 天窗口内；按默认规则本不该频繁回头看。
- 这次仍允许低频复核，是因为 `2026-03-28_1304_session-anchor-itsm-liquidity-gate.md` 提供了**新的同主题证据**：
  - 它把“固定 pseudo-open ORB”进一步拆穿；
  - 同时又说明“锚点后首段方向 -> 下一段同向续动”在 crypto 里未必死，只是更像 **event/session-anchor raw alpha family**，而不是原 Rank 16 的 ORB 保护性收口写法。
- 本轮真实问题不是“推翻 Rank 16 的 park”，而是确认：**这条新证据会不会打开一个 `Rank 16c`，还是只会让既有 `Rank 16b` 的边界更清楚，甚至把残余信息量继续上移到更通用的 event-anchor family。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0159_rank16-clean-replication-park.md`
  - `research/park_reframe/2026-03-22_2041_rank16-park-reframe.md`
  - `research/quant_digests/2026-03-28_1304_session-anchor-itsm-liquidity-gate.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 16` 被 park 的底层原因没变：
- `raw_orb @ 6bps/side ≈ -35.11%`
- `confirm1_outside ≈ -7.51%`，但 `positive_asset_ratio=0/3`、`mean_trades≈154.7`
- `retest_hold ≈ -8.36%`
- `protective_close_overlay ≈ -21.50%`
- 参数邻域 `0/6` 为正，成本梯度继续恶化

翻成人话：
- 原始 pseudo-open ORB 的形状本身是错的；
- `confirm1_outside` 只是“少亏一点”，不是已经活过来；
- `protective close` 甚至把东西做得更差；
- 所以 **原审计结论必须保留：把固定 pseudo-open ORB 直接搬进 crypto 15m，不值得继续当 standalone 路线吃资源。**

## 2) 它更像 hard park 还是 soft park？
**仍然是 `soft park`，但比 2026-03-22 更偏硬。**

为什么还不是 hard park：
- `confirm1_outside` 相比 `raw_orb` 的大幅少亏，说明“session 触发 + 方向确认”这类语义本身不是完全没信息；
- 既有 `Rank 16b`（active-hours session-range break/retest gate）也已经把最自然的一刀抽出来了。

为什么这次又更偏硬：
- 3/28 新证据说明，真正可救的地方更像 **event/session-anchor raw alpha**，而不是“再替 Rank 16 加一个更聪明的 ORB 包装”；
- 也就是说，残余信息量虽然没死，但它已经进一步**上移到别的家族**，不太留在 Rank 16 自己身上了。

## 3) 有没有“可救信号”？
**有，但它更像支持既有 `Rank 16b` 的边界，或者干脆支持更上位的 event-anchor family；不够支持新的 `Rank 16c`。**

### 可救信号
`2026-03-28_1304_session-anchor-itsm-liquidity-gate.md` 最重要的启发是：
- crypto 里确实可能存在“锚点后首段方向 -> 下一段续动”；
- 但锚点应该来自 `00:00 UTC / funding / 美股现金开盘 / macro event` 这类**真实事件时钟**；
- 不该继续执着于 Rank 16 原版那种固定 pseudo-open ORB + protective closing 的写法。

### 为什么这不构成新派生
因为这条新证据最值得改的，不是 Rank 16 内部的第二刀，而是**把问题重写成另一条 family-level 题目**：
- 从“opening range break 是否配 protective close”
- 变成“真实锚点后的首段续动有没有 raw alpha，再叠 liquidity / continuity gate”

这已经不是 `Rank 16c` 该干的事了；它更像另一条 fresh intake / survivor family 的事情。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然不变：保留 session-threshold / confirm 主故事，但把固定 pseudo-open ORB 改成 active-hours session-range break/retest gate。**

也就是：
- 原 `Rank 16` 的唯一诚实窄派生仍然只是 `Rank 16b`；
- 3/28 新证据没有再打开第二主轴；
- 相反，它只进一步说明：若还想救这个主题，应该离开原 ORB 壳子，去做更真实的 active-hours / event-anchor 语义。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- 原始 `park` 继续保留；
- 已起草的 `Rank 16b` 继续保留，而且仍是唯一诚实的窄 reframe；
- `2026-03-28` 的 session-anchor ITS M 证据更像把残余价值继续上移到 event-anchor raw alpha family，而不是支持再写一个 `Rank 16c`。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park (leaning harder than 2026-03-22)`

## Minimal audit note
本轮不推翻 `Rank 16` 的原 park，也不新增 `Rank 16c`。
更诚实的记录是：**3/28 的 session-anchor intraday TSMOM 新证据，只会进一步确认既有 `Rank 16b` 的边界，并把 Rank 16 的残余信息量上移到更通用的 event-anchor raw alpha family；它不足以再形成一个属于 Rank 16 自己的唯一新修改轴。**

## Git
- 本轮只做最小必要文档改动；不做 commit（工作区存在大量无关脏文件，避免混提）。
