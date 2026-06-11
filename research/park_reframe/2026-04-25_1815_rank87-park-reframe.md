# 2026-04-25 18:15 UTC · Rank 87 park reframe review

- source rank: `Rank 87`
- verdict: `keep_park`
- review band: `80~110`
- why this one now:
  - 依当前轮转，`50+` 号段近几天已高频覆盖；本轮回到 `80~110`
  - `Rank 87` 在 `docs/PARK_REFRAME_QUEUE.md` 最近 `7` 天内未被 bot6 复盘
  - 它属于“时钟/流动性 gate”家族，最近又确实有新证据，但这些新证据更像把主题上移到新 raw-alpha / execution overlay 宿主，适合做一次低频收口判断

## 1) 原 rank 为什么 park？
`Rank 87 / volume-clock + CS spread interaction gate` 的原始 park 原因非常集中：

1. 2026-03-19 的 source intake 先给出的故事是对的半边——**固定 funding 时钟不是好锚点，volume-clock 至少比 fixed-clock 更贴真实活跃窗口**。
2. 但唯一那次最小 clean replication 也把 blocker 审计清楚了：
   - `baseline ≈ -28.85%`
   - `fixed_clock_gate ≈ -5.73%`
   - `volume_clock_gate ≈ -0.67%`
   - 看起来是“少亏”，但 `volume_clock_gate retention≈3.42%`，`positive_asset_ratio=1/3`
3. 也就是说，改善主要来自**极端砍样本**，而不是形成仍可交易、仍跨资产站得住的 shared gate。
4. 所以原 verdict 不是“时钟信息完全没用”，而是：**把它写成 queue-facing 的 `volume-clock + CS spread interaction shared gate` 这件事，本体不成立。**

## 2) 它更像 hard park 还是 soft park？
**结论：`soft park`，但比 3 月 19 日那次更接近 `hard park with consumed residual`。**

原因：
- 软的一面：主题本身没死。`volume-clock` 比 `fixed-clock` 更诚实，这一点仍成立。
- 硬的一面：最近新增证据没有把旧 Rank 87 这条“shared continuation gate”救回来，反而更清楚地说明：
  - 要么它该上移成新的 **UTC slot cost / routing overlay**；
  - 要么它该横移成新的 **same-clock recurring pocket raw alpha**；
  - 都不是 old Rank 87 这条对象边界。

## 3) 有没有“可救信号”？
**有，但都不足以诚实支撑 old Rank 87 再派生一个直接 queue-facing 的 `Rank 87b`。**

### 可救信号 A：old evidence 本身证明“真实 market clock”比固定时钟更像样
`2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md` 已证明：
- 每日最大 `30m` 成交窗口落在 `00/08/16 UTC` funding 锚点的比例很低；
- 所以“先找真实成交时钟，再谈 continuation”这个方向没错。

### 可救信号 B：4 月新证据把“时钟信息”进一步做实了
但做实的方式已经换壳：

1. `2026-04-02_0448_utc-slot-costmap-route-veto-overlay.md`
   - 新证据更像：**UTC slot = execution / routing / veto overlay**
   - 它服务的是 pairs、carry、breakout、lead-lag 等完整壳，不是 old Rank 87 那种 shared entry gate

2. `2026-04-14_1718_sameclock-xsmomentum-recurring-pocket-alpha.md`
   - 新证据更像：**same-clock recurring pocket = 独立 raw alpha**
   - 它甚至更偏横截面、relative-value、slot router，而不是单纯给现有 continuation setup 盖一层 allow/deny gate

所以“可救”的是主题，不是 old Rank 87 本体。

## 4) 最值得改的唯一一刀是什么？
**唯一自然的一刀：把 old `volume-clock + CS spread interaction gate` 继续降级为 `UTC slot cost / route veto overlay`。**

但这刀虽然单一，却有两个问题：
1. 它已经明显不是 old Rank 87 原来那种 `shared continuation gate` 身份，而是更上位的 execution overlay；
2. 4 月 2 日的新 digest 已经把这条路写成更完整、更一般化的宿主了，继续从 old Rank 87 再命名一个 `87b`，distinctness 很差。

换句话说：
- **single modification axis 是存在的；**
- **但它更像“主题迁移到新宿主”，不是 old rank 的诚实派生。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得；本轮维持 `keep_park`。**

理由：
1. old Rank 87 的原 blocker 没被推翻：改善仍高度依赖 retention 崩到不可交易。
2. 新证据虽然支持“时钟/流动性信息”继续有用，但最诚实的落点已经变成：
   - 新 raw alpha（same-clock recurring pocket），或
   - 新 execution overlay（slot cost map / route veto）。
3. 这两条都不该再伪装成 old Rank 87 的窄派生；否则只是把“旧 gate 失败”改写成“新壳重讲”。

## 6) trade on / trade off（如果硬要派生，唯一自然写法会是什么）
本轮**不正式 draft**，这里只做审计备注：

- trade on:
  - 保留“真实成交时钟比固定 funding 时钟更诚实”这一点
  - 把 `CS spread / activity state` 只用于 `size-down / veto / route choice`
- trade off:
  - 放弃 old Rank 87 的 queue-facing shared entry-gate 身份
  - 承认它更像 execution layer 或新的 same-clock raw-alpha 宿主前置条件

这也正是本轮不 draft 的原因：一旦这么写，它就已经不是 old Rank 87 了。

## 本轮结论
**`keep_park`**

一句话收口：
> `Rank 87` 仍更像 `soft park`，但已明显朝 `hard park with consumed residual` 收紧；最近新证据继续说明时钟/流动性信息是活的，但它救活的是新的 `same-clock raw alpha` 或 `UTC slot cost / routing overlay` 宿主，而不是足以再诚实派生 old `volume-clock + CS spread interaction gate` 的 `Rank 87b`。

## 文件/提交流水
- 本轮未改 `docs/TODO.md` 顶部排班。
- 本轮只更新：
  - `research/park_reframe/2026-04-25_1815_rank87-park-reframe.md`
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
- 本轮默认不做 commit；若后续需要 commit，应只做 selective commit。