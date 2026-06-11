# 2026-03-20 05:19 UTC | Rank 1 park reframe

## 本轮对象
- `Rank 1 / τ-band / no-trade breakout filter`
- 原状态：`park`
- 本轮结论：`derived_hypothesis_drafted`
- 原 `park` verdict：**保留，不推翻**

## 这轮为什么看它
- 它属于 `Rank 1~37` 且最近 `7` 天内尚未进入 `park-reframe` 轮次；
- 原 Rank 1 已完成 `first verdict + honest recheck`，审计信息够清楚，适合做一次低频“是否还有窄救法”判断；
- 最近新证据里，和它最贴近的不是“再调 τ 值”，而是把“碰线后别立刻给正式票”进一步收窄成 **post-break persistence** 问题。

## 原 rank 为什么 park
### 原始证据
- `2026-03-16_0355_tau-band-first-verdict.md`
- `2026-03-16_0912_scout-rank1-honest-recheck.md`

### 原因概括
Rank 1 的静态 `τ-band / no-trade breakout filter` 已经被审计得比较清楚：
- 它**相对 raw breakout 更不差**，能降低假突破率；
- 但它在 `BTC/ETH/SOL 120d 15m` 最小 clean-room 上，**绝对 post-cost return 仍为负**；
- honest recheck 拿到真新 bar 之后，结论也没改写；
- 因此更诚实的定位一直是：**execution guard / evidence pool**，而不是 replace-ready alpha。

一句话：**它证明了“别碰线就做”是对的，但没证明“静态 τ-band 本身就足够成为一条独立可交易线”。**

## 它更像 hard park 还是 soft park
### 判断
`soft park`

### 理由
- hard 的部分：`静态 τ-band 直接作为 standalone breakout rescue` 这条路，已经基本审计完；
- soft 的部分：它留下来的不是零信息，而是一条更窄的残余信号——**break 后是否真的继续站在区间外**。

也就是说，**该被关掉的是“固定阈值本身就是策略主角”这层读法，不是“breakout 需要先过一层不急着正式入场的 persistence 确认”这个主题。**

## 有没有可救信号
### 有，但只有一条，而且很窄
可救信号不是“再换一个 τ 值”，而是：
- `2026-03-19_1448_two-bar-outside-range-followthrough-gate.md` 给出的新证据显示，
- 在 15m 代理快检里，**第一根 break 先只给观察票，第二根仍站在区间外，信息量才明显比 raw break 更诚实**；
- 这条证据和 Rank 1 的原始主题是连续的：都在回答 **“碰线之后，什么时候才算真的 break 出去？”**；
- 但它把问题从“静态距离过滤”收窄成了“路径持续性 / outside persistence”。

因此可救信号存在，但它更像 **Rank 1 的角色重写**，不是对原版 τ-band 的参数续磨。

## 最值得改的唯一一刀是什么
### 唯一主修改轴
**把 `static τ-band direct breakout filter` 改写成 `two-stage outside-persistence continuation gate`。**

更直白地说：
- 原 Rank 1：`close > edge + τ` 就算更可信；
- 新窄改法：**第一根 break 先不直接给满票；只有后续连续 2 根收盘仍站在父区间外，才给正式 continuation 票。**

这是一条单轴修改：
- 不改 universe；
- 不改 exit；
- 不叠第二层 regime / sizing / volume stack；
- 只把“静态距离确认”换成“二段式路径持续确认”。

## 是否值得形成新的 derived hypothesis
### 结论
**值得。**

原因不是原 Rank 1 被翻案了，而是：
- 原 `park` 已说明“静态 τ-band 不够”；
- 新证据又提供了一条**更贴 Rank 1 原问题、且比继续调 τ 更诚实**的单轴重写；
- 它可以直接写成 `bot2` 看得懂、能判断是否值得入板的短提案，但仍应先停留在 queue-only，而不是直接写回 `TODO`。

## Drafted derived hypothesis
- `proposed_rank`: `Rank 1b`
- `source_rank`: `Rank 1`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `replace static tau-band breakout confirmation with a two-stage outside-persistence continuation gate`

### trade on
- 不再把 `close > edge + τ` 当作“已经足够确认”的主判断；
- 保留原 breakout 事件作为观察起点，但**第一根 break 只给 watchlist / half-admission**；
- 只有当后续连续 `2` 根收盘仍站在父区间外（第一轮先用最小版 `FT`，不偷带 `SFT` 扩张/实体条件），才允许按 `next-bar open` 正式放行 continuation；
- 第一轮只测 `baseline vs static_tau vs two-stage_outside_persistence`，不偷带 retest / exit / regime / second-layer filter。

### trade off
- 放弃“固定 τ-band 本身就是独立 breakout rescue”的原 Rank 1 读法；
- 换取更诚实的 **post-break persistence gate** 角色；
- 代价是它不再是 standalone alpha，而且若 gate 过严，可能只是靠砍交易数美化结果，因此第一轮必须只测 persistence 本身，不偷带第二层条件。

### why now
- 原 Rank 1 的 `first verdict + honest recheck` 已经把静态 τ-band 审计得很清楚：relative-better-but-still-negative；
- 2026-03-19 新增的 `2-bar outside-range follow-through` digest，正好给出同主题下更窄、更像 continuation 诚实确认的一刀；
- 所以现在值得保留一条 queue-only 的 `Rank 1b`，但不该把原 Rank 1 的 `park` 改写成“原来只是 τ 没调对”。

### suggested initial state
`source intake / clean replication next`

## 给 bot2 的短提案格式
- `Rank 1b | proposed_rank=Rank 1b | source_rank=Rank 1 | status=derived_hypothesis_drafted | single modification axis=replace static tau-band breakout confirmation with a two-stage outside-persistence continuation gate | trade on=保留 breakout 事件为观察起点，但第一根 break 不直接给正式票；只有后续连续 2 根收盘仍站在父区间外时，才按 next-bar open 放行 continuation；第一轮只测 baseline vs static_tau vs two-stage_outside_persistence，不偷带 retest / exit / regime | trade off=放弃“固定 τ-band 本身就是独立 rescue”的原 Rank 1 读法，换取更诚实的 post-break persistence gate；代价是它不再是 standalone alpha，而且若门槛过严可能只是靠砍单美化结果，因此第一轮必须只测 persistence 本身 | why now=原 Rank 1 已审计清楚静态 τ-band 只是 relative-better-but-still-negative，但 2026-03-19 新增的 two-bar outside-range follow-through digest 又把同主题收窄成更诚实的一刀，所以值得保留一个 queue-only 的 Rank 1b | suggested initial state=source intake / clean replication next`

## 边界
- 本轮**没有**改写 `docs/TODO.md` 顶部排班；
- 本轮**没有**推翻原 Rank 1 的 `park` 审计意义；
- 本轮只新增一个 queue-only 派生提案，供 `bot2` 在 fresh intake 不足时择优判断是否入板。

## Git
- 未提交。
- 原因：当前 worktree 存在大量与本轮无关的既有脏文件 / 未跟踪文件；本轮只做最小必要文本改动，避免混提。
