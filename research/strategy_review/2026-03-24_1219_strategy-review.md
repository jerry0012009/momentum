# Strategy Review (bot2)

Time: 2026-03-24 12:19 UTC

## 本轮一句话判断
`Rank 154 / Crypto-Stat-Arb` 已经达到 bot2 兜底直推 `P3` 的门槛：当前前排没有别的 `P3/P2/P1` 压力，而这条线虽存在 2022 负段与 `trade_buffer≈5%` 甜点依赖，但 repo 本身就是跨资产 crypto perp 横截面骨架，effective return 明显为正，same-day / funding 记账乐观修正后仍能存活，未见致命 honesty / execution flaw；因此本轮不再继续开放式 `keep_P2`，直接写入 `Paper launch queue`。

## 1) 必检输入

### Policy / state 先读结论
- policy 仍要求固定按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 当前 runtime state（改写前）显示：
  - `Paper launch queue = none`
  - `Fresh intake` 最近一条仍是 `ryanczm/Crypto-Stat-Arb`，已正式分配 `Rank 154`
  - `Surviving candidate slot = none`，唯一一次 follow-up 已在 2026-03-24 09:50 UTC 用完并把对象升到 `P2`
  - `Active P2 slot = Rank 154 / Crypto-Stat-Arb`
  - `p2_consecutive_keep_p2 = 2`，且最近两条 axis 已经是 `time stability`、`honesty / execution realism`
- policy 还明确规定：若 desk review 已清楚表明 `Active P2` 足够值得进入 paper trade / paper launch，而 bot3 尚未升级，bot2 必须直接把它推进到 `P3 / Paper launch queue` 或对应 handoff 路径，不得继续排成开放式研究。

### Repo 状态
- repo 依旧很脏，但只作 evidence 背景，不反向改 policy。
- 本轮仍遵守硬约束：只更新 `docs/BOT2_BOT3_STATE.md`；不改 policy / brief / operating card / auto loop / cron prompt。

### 最近 `research/optimization_loop/`
按时间倒序读取的关键结果：
1. `2026-03-24_1046_crypto-stat-arb-p2-honesty-execution.md`
   - 把 `same-day close` 假设修正成更诚实的 `lagged weights + lagged funding` 后，`combined` 仍约 `CAGR 42.8% / Sharpe 1.27 / MDD -28.5%`。
   - `15bps` 与 `20bps` 下也未被打穿；主要脆弱点是 `trade_buffer` 不能过松或过紧。
2. `2026-03-24_1018_crypto-stat-arb-p2-time-stability.md`
   - 年度切片里 `2022` 明确转弱，说明它不是平滑到“研究完美”的组合。
   - 但跨年并未失真到接近零，说明不是一次性样本幻觉。
3. `2026-03-24_0950_crypto-stat-arb-followup-promote-p2.md`
   - 上一条 fresh intake 的唯一一次 follow-up 已有效兑现，并直接从 `P1` 升到 `P2`。
4. `2026-03-24_0922_crypto-stat-arb-fresh-intake.md`
   - 原始 intake 已确认这是一个可 clean-room 重写、带 funding / fee / buffer 的 crypto perp 横截面组合骨架。

### 最近 `research/strategy_review/`
1. `2026-03-24_1159_strategy-review.md`
   - 已明确指出当前唯一该收口的是 `Rank 154` 的 `P2` 出口判断，而不是回头拉旧候选，也不是直接切回 fresh intake。
2. `2026-03-24_1156_strategy-review.md`
   - 已把当前轮定性为 `P2 exit decision`，且禁止继续沿 `time / honesty` 轴做第三次开放式 `keep_P2`。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **改写前：否，原本为空。**
- **改写后：是，现已非空。**
- 证据：本轮 desk review 已将 `Rank 154 / Crypto-Stat-Arb` 直接写入 `P3 / Paper launch queue`。

### Q2. 本轮 `fresh intake` 是什么？
- **`ryanczm/Crypto-Stat-Arb`，即 `Rank 154`。**
- 证据：`Fresh intake slot.latest_result` 与 `source_record` 仍指向 `research/optimization_loop/2026-03-24_0922_crypto-stat-arb-fresh-intake.md`；它仍是最近一条真正进入当前运行槽位的 fresh intake。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且已经用掉，并且用得对。**
- 证据：`research/optimization_loop/2026-03-24_0950_crypto-stat-arb-followup-promote-p2.md` 明确显示这次 follow-up 直接把对象从 `keep_P1` 推进到 `P2`，不是低杠杆补测。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **改写前：存在，就是 `Rank 154 / Crypto-Stat-Arb`。**
- **它离 `P3` 最近，而且本轮已被直接推进到 `P3`。**
- 原因：
  - `cross-asset` 维度并非空白：该 repo 本身就是 top-30 Binance perpetual universe 的横截面多空骨架，不是单资产玩具。
  - `effectiveness` 维度已经够形成 paper-trade 级判断：在更诚实的 lagged 口径下依然保有显著正边，而不是轻微擦边。
  - `parameter` 维度虽然显示 `trade_buffer≈5%` 甜点，但这更像 implementation sweet spot，而不是“一改参数就全灭”的致命脆弱；按 policy，`P3` 门槛不是研究完美，而是“足够值得进入 paper trade / paper launch，比较有可能成型，且没有明显致命 honesty / execution 问题”。
  - 当前并不存在明确的 `P2 -> P1 re-scope` 唯一路线，也没有足够证据要求直接 `P0`。

## 3) 本轮为何直接 `P2 -> P3`
本轮 desk review 的核心判断是：
- 这条线的主要 admission 问题已经被收敛，而不是继续发散：
  - `time stability`：确认有 regime 依赖，但并未证明边际虚假；
  - `honesty / execution realism`：确认 same-day close 偏友好，但修正后仍 survive；
  - `effectiveness`：修正后仍有足够厚的正边；
  - `cross-asset`：策略定义天然是 crypto perp 横截面组合，而非单资产特例；
  - `parameter`：5% buffer 是甜点，但还没到“一离开这个点就策略失效”的 fatal 程度。
- 因此若继续把它停在 `P2`，就属于 policy 禁止的“应该升 P3 却继续开放式研究”。
- 更诚实的下一个动作不是再做 admission，而是进入 `P3 / Paper launch queue`，把剩余不确定性放到 paper 阶段验证，而不是继续消耗前排研究槽位。

## 4) rank 合规检查
- 本轮前排对象唯一需要 rank 的是 `Rank 154 / Crypto-Stat-Arb`。
- 它已持有正式 `Rank 154`，因此无需补 rank。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
已做以下 authoritative writeback：
1. `Paper launch queue`
   - 从 `none` 改为 `Rank 154 / Crypto-Stat-Arb`
   - 明确 latest_result：bot2 在本轮 desk review 里直接完成 `P2 -> P3` 兜底升级
2. `Active P2 slot`
   - 清空为 `none`
   - latest_result 改为：`Rank 154` 已由 bot2 直接升级到 `P3`
3. `cycle_plan`
   - 改成以 `P3 handoff` 为第一优先级
   - 在当前无 `Active P2` / `Surviving candidate` 的情况下，把下一轮默认主资源切回新的 fresh intake
   - 明确保留 `Background pool` 不得自动 reopen

## 6) 当前轮 cycle_plan（改写后）
1. `Paper launch queue（Rank 154 / Crypto-Stat-Arb）`
   - 补齐最小 `P3 handoff` 包：`source record`、`latest admission record`、paper launch 入口/脚本/页面落点、最小 rollback / review 说明
2. `Fresh intake slot`
   - 因当前已无 `Active P2` 与 `Surviving candidate`，下一轮恢复 fresh intake，认领 1 个新的 raw alpha / repo，并直接回答 `park / keep_P1`
3. `Background pool`
   - 继续只作 evidence 存档，不得自动把旧候选拉回前排

## 7) 本轮实际改动
- 更新：`/root/clawd/jerry/momentum/docs/BOT2_BOT3_STATE.md`
- 新增：`/root/clawd/jerry/momentum/research/strategy_review/2026-03-24_1219_strategy-review.md`

## 8) 一句话结论
**`Rank 154 / Crypto-Stat-Arb` 已不应继续停留在 `P2`：它有真实瑕疵，但这些瑕疵更适合进入 paper launch 阶段验证，而不是继续占用 admission 槽；因此本轮 bot2 已按兜底权限把它直接推进到 `P3 / Paper launch queue`。**
