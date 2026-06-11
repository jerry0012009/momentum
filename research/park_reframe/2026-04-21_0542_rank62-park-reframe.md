# 2026-04-21 05:42 UTC · Rank 62 park reframe

## 本轮结论
- 选定条目：`Rank 62 / continuation fail-fast overlay`
- 原 `park` verdict：**保留**
- 本轮 park-reframe 结论：**`derived_hypothesis_drafted`**
- 拟议派生：**`Rank 62b`**
- 唯一主修改轴：**把“全程共享 fail-fast overlay”收窄成“仅覆盖 entry 后前 2~3 根 bar 的 fail-fast 检查；若 trade 存活，再 handoff 到 slow exit（Donchian / Chandelier）”**

## 为什么这轮选 Rank 62
- 按 `bot6` 轮转规则，当前默认仍应优先看 `Rank 50~79` 的 parked rank。
- `Rank 62` 在最近 `7` 天内没有被 `bot6` 复盘记录命中，且目前 `docs/PARK_REFRAME_QUEUE.md` 里也没有对应的已起草 reframe 条目。
- 它的旧结论不是“主题彻底没信息”，而是**shared overlay 角色太粗**：在 `ema_psar_long` 上能减亏，但跨到 `fib_retest_long / breakout_short` 就不成立，因此适合检查是否还能收窄成一条更诚实的单轴派生。

## 原 rank 为什么 park
依据 `2026-03-18_1830_rank62-clean-replication-park.md`，原 Rank 62 被 park 的核心原因很集中：
1. `ema_psar_long` 上确实出现了一点“更快认错、缩小 loser size”的改善；
2. 但这层 fail-fast **没有跨 archetype 保持一致**：
   - 对 `fib_retest_long`：明显过早截断，`winner_truncation_rate` 很高；
   - 对 `breakout_short`：没有修复负 pocket；
3. `false_follow_through_4bars / 8bars` 并没有真正改善，说明它更像在改收益分布，而不是减少假延续；
4. `session VWAP` 在 24/7 crypto 上还有明显 session 任意性。

一句话说，原 Rank 62 不是被“fail-fast 完全没用”打死，而是被**“把 fail-fast 当成三条线全程共用 overlay”这层写法不诚实**打回 park。

## 它更像 hard park 还是 soft park
**更像 soft park。**

原因：
- hard park 的典型形态是主题本身已经被更上位 raw-alpha 宿主完全吸收，或唯一残余已被既有 reframe 消费；
- Rank 62 不是这样。它的失败点非常具体：**角色层级与时钟写法不对**，不是“快速认错”这件事本身完全无信息；
- 原 replication 反而给出了一条很清晰的负证据：问题主要来自 **全程快砍导致的 winner truncation**，这更像仍有 residual，但只能沿一个很窄的“持仓时钟重写”方向去救。

## 有没有“可救信号”
有，但只剩一条，而且必须很窄。

### 可救信号 1：原始 park 本身留下了 blocker 形状
- `ema_psar_long` 上 loser size 收缩，说明 fail-fast 对“entry 后立刻走坏”的识别并非完全无效；
- 真正坏的是它把这套快时钟一直拴到 trade 后半段，导致 `fib_retest_long` 的本来能走出来的单子被过早砍掉。

### 可救信号 2：`2026-03-18_2250_fast-entry-slow-exit-handoff-spine.md`
- 这篇 digest 提供的不是新 alpha，而是一条非常贴 Rank 62 blocker 的结构性线索：
  - **前段可以快检查；**
  - **活下来后不该继续全程用 fail-fast；**
  - 更诚实的写法是 handoff 给 slow Donchian / Chandelier 一类慢 exit。
- 这条证据和 Rank 62 的原失败点高度对齐：它不否定 fail-fast 的前段价值，只否定“全程共享快砍”。

## 最值得改的唯一一刀是什么
**唯一一刀：把 fail-fast 的职责限制在 entry 后前 2~3 根 bar 的 survival check；一旦 trade 存活，就切换到慢退出脊柱。**

冻结成更可执行的话：
- 不改 base setup，不改方向，不改 universe；
- 只改 exit clock：
  1. `entry -> 前 2~3 根 bar`：允许 `ema_fail / atr_fail` 这类 quick failure check；
  2. 若未触发且顺向存活（第一轮可用“存活满 3 根 bar”或“浮盈达到 0.75 ATR”二选一固定），则**handoff** 到 `slow Donchian / Chandelier`；
  3. 第一轮只测 `baseline vs full fail-fast vs two-stage handoff`，不偷带新 regime / entry / sizing 第二轴。

## 是否值得形成新的 derived hypothesis
**值得。**

原因不是因为 Rank 62 已经被救活，而是因为：
- 原 park 的 blocker 已非常清楚；
- 仍有 residual signal，但只能沿一条唯一主轴表达；
- 这条主轴不会推翻原始 park，反而保留了原结论的审计意义：
  - 原 Rank 62 失败的是“全程共享 fail-fast overlay”；
  - 新草案只是在此基础上提出：**若 fail-fast 只做前段生死检查，而不是全程出场框架，是否能避免原先的 Fib winner truncation。**

## 新派生假设草案（bot2 可直接判断是否入板）
- `proposed_rank=Rank 62b`
- `source_rank=Rank 62`
- `status=derived_hypothesis_drafted`
- `single modification axis=demote full-lifecycle shared fail-fast overlay into a two-stage exit handoff: fail-fast only in the first 2~3 bars after entry, then hand off surviving trades to a slow Donchian/Chandelier exit spine`
- `trade on=保留原 breakout_short / fib_retest_hold / ema_psar_long 的 entry 与方向判断；只在入场后前 2~3 根 bar 内允许最小版 fail-fast（第一轮优先只测 ema_fail + atr_fail，不强绑 session VWAP）。若 trade 存活，则切到 slow exit（第一轮固定 Donchian 或 Chandelier，不双改），目标是保留“早认错”同时减少 Fib 这类 hold 型 setup 的 winner truncation`
- `trade off=放弃“同一套 fail-fast 规则全程管理三条线”的原 Rank 62 读法，换取更诚实的分段持仓时钟；代价是它不再是一个简单共享 overlay，而且若改善只来自更慢出场拖大回撤，或只修复单一 archetype，也应快速压回 park，因此第一轮必须 strict A/B：baseline vs full fail-fast vs two-stage handoff，不偷带 regime / size / new trigger`
- `why now=原 clean replication 已把 Rank 62 的真正 blocker 审计清楚：问题不是 quick failure check 完全无信息，而是 full-lifecycle fast exit 让 fib_retest_hold 出现严重 winner truncation；而 2026-03-18 的 fast-entry-slow-exit handoff digest 正好提供了与该 blocker 一一对应的窄重写路径`
- `suggested initial state=source intake / clean replication next`

## 本轮回答（按 bot6 固定模板）
1. **原 rank 为什么 park？**
   - 因为 full-lifecycle shared fail-fast 只能在 `ema_psar_long` 上减亏，跨 setup 不一致，并明显截断 `fib_retest_long` 的赢家。
2. **更像 hard 还是 soft park？**
   - 更像 `soft park`。
3. **有没有可救信号？**
   - 有，且只剩“前段 quick failure check 可能有用，但不该全程管理”这一条。
4. **最值得改的唯一一刀是什么？**
   - 改成 `前段 fail-fast + 存活后 handoff 到 slow exit` 的两段式 exit clock。
5. **是否值得形成新的 derived hypothesis？**
   - 值得，命名为 `Rank 62b`。
6. **trade on / trade off 怎么写？**
   - `trade on`：保留原 entry，只改 exit clock；
   - `trade off`：放弃全程快砍的简单共享 overlay，换取更诚实的分段持仓管理，但必须严防“靠更慢退出拖出纸面改善”的假修复。

## 文件与工作区说明
- 本轮只应最小更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - 本日志文件
- `git status` 显示工作区存在大量与本轮无关的历史脏文件，因此**不适合混做提交**；本轮默认只保留 selective write。
