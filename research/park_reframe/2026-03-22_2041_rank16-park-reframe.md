# 2026-03-22 20:41 UTC · Rank 16 park reframe review (revisit)

## Scope
- Source rank: `Rank 16 / ORB threshold + protective closing session gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，最近新增的 intraday 时段/量能/方向证据，是否值得把 Rank 16 再派生成新的窄 reframe（超出既有 `Rank 16b`）**

## Why revisit Rank 16 (7-day rule note)
- `Rank 16` 已在 `2026-03-18 06:29 UTC` 被 bot6 派生过 `Rank 16b`，按 7-day 规则正常不该频繁回头看。
- 本轮之所以允许低频复核，是因为最近又出现了几条**同主题但更偏实现边界**的新证据：
  - `2026-03-20_0823_intraday-sign-asymmetry-jump-fomc-gate.md`
  - `2026-03-20_0851_same-clock-intraday-rvol-volume-gate.md`
- 本轮的真实问题不是“要不要推翻原 park”，也不是“要不要重写 16b”，而是确认：**这些新证据会不会再打开一个 `Rank 16c`，还是只会让既有 `16b` 的实现纪律更清楚。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0159_rank16-clean-replication-park.md`
  - `research/park_reframe/2026-03-18_0629_rank16-park-reframe.md`
  - `research/quant_digests/2026-03-18_0549_session-range-active-hours-gate.md`
  - `research/quant_digests/2026-03-20_0823_intraday-sign-asymmetry-jump-fomc-gate.md`
  - `research/quant_digests/2026-03-20_0851_same-clock-intraday-rvol-volume-gate.md`

---

## 1) 原 rank 为什么 park？
原 `Rank 16` 被 park 的核心原因没有变：
- `raw_orb @ 6bps/side ≈ -35.11%`
- `confirm1_outside ≈ -7.51%`，但 `positive_asset_ratio=0/3`、`mean_trades≈154.7`
- `retest_hold ≈ -8.36%`
- `protective_close_overlay ≈ -21.50%`
- 参数邻域 `0/6` 为正，成本梯度持续恶化

翻成人话：
- **确认层**确实比裸 ORB 少亏；
- 但原始写法仍是**高频、跨资产全负、成本后继续塌**；
- `protective close` 也没有把它救活。

所以原始审计结论必须保留：**把固定 pseudo-open ORB 直接搬进 crypto 15m，这条 standalone 路线已经应当继续算 `park`。**

## 2) 它更像 hard park 还是 soft park？
**仍然更像 `soft park`。**

原因也没变：
- hard fail 的是原始 `pseudo-open ORB + protective close` 形状；
- soft 的部分在于：`confirm1_outside` 相对 `raw_orb` 的改善，说明问题更像出在 **session trigger 的定义与角色**，而不是“所有 intraday threshold / confirm 都没信息”。

但本轮补充一点：
- 这份 soft park 的残余信息量，当前仍然主要收敛在既有 `Rank 16b` 那条主轴上；
- 最近新证据更像给 `16b` 加 honesty guard，而不是再切出第二主轴。

## 3) 有没有“可救信号”？
**有，但仍然只够支撑 `Rank 16b`，不够再派生 `Rank 16c`。**

### 可救信号 A：active-hours / session-range 仍是最对位的一刀
`2026-03-18_0549_session-range-active-hours-gate.md` 仍然是最贴原失败形状的证据：
- crypto 15m 不该把全天 24h 同权；
- 与其围绕固定 pseudo-open 画 opening range，不如只在更有参与度的时段围绕 session high/low 看 break / retest / continuation。

这正是 `Rank 16b` 已经锁定的唯一主修改轴。

### 可救信号 B：intraday sign / no-jump/no-FOMC 更像附属 honesty guard
`2026-03-20_0823_intraday-sign-asymmetry-jump-fomc-gate.md` 有价值，但它更像在提醒：
- active-hours 内也不该默认“只做延续”；
- 某些 jump / event 时段应 blackout 或降权。

问题是：这并没有打开新的 Rank 16 母轴；它更像 `16b` 后续若真 clean replication 时，才应该加上的**direction-aware / event-aware guard**。

### 可救信号 C：same-clock RVOL 更像 volume 计量口径修正，不是新主轴
`2026-03-20_0851_same-clock-intraday-rvol-volume-gate.md` 提醒我们：
- 若 `16b` 后续想加 volume confirm，应该用 same-clock intraday RVOL，而不是 naive rolling SMA；
- 但这仍然只是**量能确认的口径修正**，不构成一个独立于 `active-hours session-range gate` 之外的新 reframe。

=> 所以本轮真实结论是：
- `Rank 16` 仍有可救信号；
- 但这些新增信号都只是把 **既有 `16b` 的实现边界写得更诚实**；
- 它们不足以再派生一条新的、独立的 `Rank 16c`。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然不变：保留 session-threshold / confirm 主故事，但把固定 pseudo-open ORB 改写成 active-hours session-range break/retest gate。**

也就是：
- 原 `Rank 16` 的唯一诚实窄派生，仍然是 `Rank 16b`；
- 新证据只说明若后续真做 `16b`，应额外注意：
  1. active-hours 内仍需防 jump / macro-event blackouts；
  2. volume confirm 要优先用 same-clock RVOL；
- 但这两点都不该升级成第二主轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- 原始 `park` 继续保留；
- 已起草的 `Rank 16b` 继续保留，且仍是唯一诚实的窄 reframe；
- 本轮新增证据不足以再写一个 `Rank 16c`。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
本轮不推翻 `Rank 16` 的原 park，也不新增 `Rank 16c`。
更诚实的记录是：**最近新增的 intraday sign / event / same-clock RVOL 证据，只会增强 `Rank 16b` 的实现纪律，不足以再切出新的唯一主修改轴。**

## Git
- 本轮只做最小必要文档改动；不做 commit（工作区存在无关脏文件，避免混提）。
