# Strategy Review (bot2)

Time: 2026-03-26 17:59 UTC

## 本轮一句话判断
当前前排顺序很清楚：`Rank 183` 继续留在 `Paper launch queue`，`Rank 186` 是唯一明确 `Active P2`，`Rank 187` 是唯一 survivor；因此本轮 `cycle_plan` 必须先做 `Rank 186 admission`，再做 `Rank 187` 的唯一 follow-up，最后才轮到具体 fresh intake（本轮切到 `Rank 96` 与 `Rank 101` 两条 park reframe residual）。

## 1) 先读 policy + state 后的结论
- policy 默认顺序仍是：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。
- 当前前排状态在改写前已是：
  - `Paper launch queue = Rank 183 / cbeth-eth-rolling-fair-basis-mr`
  - `Fresh intake slot = seesaw negative lead-lag alt basket（completed / park）`
  - `Surviving candidate slot = Rank 187 / BTCUSDT 15m late-session path-shape swing`
  - `Active P2 slot = Rank 186 / CME expiry postfix short BTC`
- 前排对象没有无 rank 情况：`Rank 183`、`Rank 186`、`Rank 187` 都已有正式 `Rank`，无需补号。
- 因而本轮最高优先级不是再围着 `Rank 183` 做伪 handoff，也不是跳过前排去追新的 digest，而是：
  1. 先让 `Rank 186` 进入第一轮 P2 admission；
  2. 再对 `Rank 187` 用掉那唯一一次 survivor follow-up；
  3. 只有前两项已诚实排在最前后，才用剩余预算补具体 fresh intake。

## 2) 最近 repo / optimization_loop / strategy_review 证据
### Repo 状态
- `git status --short` 仍是大量未跟踪 artifacts / reports / scripts。
- 这些只当最近工作痕迹，不可反向改 policy，也不能据此把 background pool 旧候选自动拉回前排。

### 最近 `research/optimization_loop/`
1. `2026-03-26_1721_rank186_survivor_followup_promote_p2.md`
   - `Rank 186` 已完成 survivor 唯一 follow-up，并正式升入 `Active P2`。
   - 当前 exact object 已收窄为：`last Friday 16:00 London` 月度 CME 到期后，在 Binance `spot / perp` 上做 `post 60~120m short BTC`。
2. `2026-03-26_1744_rank187_intraday_curve_shape_intake_keep_p1.md`
   - `1633` 已不再是待判 fresh intake，而是已收口成 `Rank 187` survivor。
3. `2026-03-26_1757_seesaw_negative_leadlag_alt_basket_park.md`
   - 最新 fresh intake 已完成首判并 `park`，因此当前 `Fresh intake slot` 没有新的 survivor 锁。
4. `2026-03-26_1247_rank183_p3_handoff_ready.md`
   - `Rank 183` 已完成最小 `P3 handoff` 收口，当前是 queue/handoff 对象，不再是开放式 admission。

### 最近 `research/strategy_review/`
- `2026-03-26_1717_strategy-review.md` 当时正确地把 `Rank 186` survivor follow-up 放在最前；随后运行态已经变化：
  - `Rank 186` 已于 `17:21 UTC` 升入 `Active P2`；
  - `1633` 已于 `17:44 UTC` 升成 `Rank 187` survivor；
  - `1555` 已于 `17:57 UTC` 完成首判并 `park`。
- 所以本轮排班必须承认：
  - 当前唯一明确 `Active P2` 是 `Rank 186`；
  - 当前唯一 survivor 是 `Rank 187`；
  - 若切回 fresh intake，不能再回头重排已处理过的 `1633 / 1555`，而应从 policy 允许的下一来源里选具体对象。

## 3) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
- **是，非空。**
- 当前唯一对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`。
- 它已经处于 `handoff-ready`，本轮不应再把它重写成新的开放式研究。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 是两条具体 park reframe residual：**
  1. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
  2. `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`
- 理由：
  - 近期新 digest 里，`1035 / 1633 / 1555 / 0950 / 1505` 这批最近对象都已被处理完；
  - 当前前排仍有更高优先级的 `P2 + survivor` 动作，所以 fresh intake 只能放在后半段；
  - 一旦切回 fresh intake，policy 要求必须指定具体对象；最近可用且允许的下一来源就是 `research/park_reframe/INDEX.md` 中的 `soft_reframe_candidate`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **不值得。**
- 上一条 fresh intake 是 `seesaw negative lead-lag alt basket`（`2026-03-26_1555...`），已在 `2026-03-26_1757_seesaw_negative_leadlag_alt_basket_park.md` 被明确首判为 `park`。
- 当前最诚实 pocket 只剩 `BTC+ETH 5m leader shock top20% -> 反向做 SOL/XRP/DOGE/ADA/LINK basket，持有 3 根 5m`，但 follower-only gross 只有 `+1.64 bps/trade`，spread 版更薄，且迁到 `15m` 直接翻负。
- 因此它没有拿到 `keep_P1`，也就不配占用 survivor 那唯一一次 follow-up。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。当前明确 `Active P2` 是 `Rank 186 / CME expiry postfix short BTC`。**
- 它当前离 **`P3` 最近**，不是 `P1` 或 `P0`。
- 原因：
  - `Rank 186` 已在 survivor follow-up 里拿到会改变层级的证据：`placebo + pre-ramp` 对齐后，spot/perp 上的 `post 60~120m` 负漂移仍然明显；
  - 这说明对象已经不再只是“有点意思”的 P1 线索，而是一个接近 paper 值得继续 admission 的 exact-time event strategy；
  - 当然它还没到 bot2 必须直接兜底升 `P3` 的地步，因为 `effectiveness / cross-asset / time / parameter / honesty` 五项 admission 还没正式补齐；
  - 但若只看出口方向，它显然更接近 `promote_P3`，而不是 `re-scope 回 P1` 或 `drop 到 P0`。

## 4) Rank / front-slot 合规检查
- `Paper launch queue`: `Rank 183`（已有正式 rank）
- `Surviving candidate slot`: `Rank 187`（已有正式 rank）
- `Active P2 slot`: `Rank 186`（已有正式 rank）
- 当前前排对象没有无 rank 情况；无需补新的整数 `Rank`。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的改写
本轮只更新了 `BOT2_BOT3_STATE.md`，没有改 policy / brief / operating card / auto loop / cron prompt。

新的 `cycle_plan` 按 policy 默认顺序改写为：
1. `Rank 186 / CME expiry postfix short BTC`：第一轮 `Active P2` admission（先回答 effectiveness + spot/perp cross-asset stability 是否已足够接近 `P3`）
2. `Rank 187 / BTCUSDT 15m late-session path-shape swing`：survivor 唯一 follow-up（只回答 `promote_P2` 或 `park_to_background`）
3. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
4. `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`

这么排的原因是：
- `P3`: `Rank 183` 已 handoff-ready，没有新的最小 queue/handoff 动作；
- `P2`: `Rank 186` 是当前最靠近出口的前排对象，必须先处理；
- `P1`: `Rank 187` 拿着 survivor 唯一 follow-up 锁，优先级高于新的发现；
- 只有把 `P2 / P1` 诚实排进当前轮前部后，剩余预算才允许切回 fresh intake；
- 近期新 digest 已暂时处理完，所以本轮 fresh intake 合理切到 `park_reframe/INDEX.md` 中最近的 `soft_reframe_candidate`，并且直接写明具体对象，而不是留空泛占位句。

## 6) P3 / handoff 兜底检查
- 本轮不存在“desk review 已清楚表明某个 `Active P2` 足够直接进 paper trade，但 bot3 尚未升级”的明确情形。
- `Rank 183` 的兜底升级责任此前已完成，并已同步到 `Paper launch queue`。
- `Rank 186` 虽更接近 `P3` 而不是 `P1/P0`，但当前还未到必须由 bot2 直接改写成 `P3` 的程度；本轮更诚实的动作是先排它的第一轮 admission，而不是硬升。

## 7) 一句话结论
**当前 queue 仍非空，但真正占前排执行权的是 `Rank 186` 的 P2 admission 与 `Rank 187` 的 survivor 唯一 follow-up；只有这两项已诚实排在前面后，才轮到 `Rank 96 / Rank 101` 两条具体 fresh intake。**
