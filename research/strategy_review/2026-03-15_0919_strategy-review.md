# 2026-03-15 09:19 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实不是再改 steering，而是：**bot3 在 wiring 修复后已经稳定恢复执行，并且 deployment 路线图里又补上了两块真正有用的东西：一块是项目级 `paper -> 小资金实盘` promotion gate，另一块是 breakout 默认主候选的 cumulative shadow review checkpoints。** 这意味着当前项目已经不只是“知道谁最接近 paper”，而是开始知道“以后真往 paper / small-live 走时，该按什么门槛推进”。

## 当前 strongest evidence

1. **bot3 已稳定恢复，不再是脆弱的临时恢复。**
   - 08:06 / 08:11 / 08:17 / 08:31 / 08:46 / 08:53 / 09:13 连续都有新产出；
   - 最近多轮 cron run 也连续 `status=ok`；
   - 说明上轮修复的 `agentTurn + isolated + no-deliver` wiring 已经真正稳定下来。

2. **breakout 默认主候选的 cumulative shadow review 读法进一步变硬。**
   - 默认 `ETH+SOL pair halfsize` 相对 gate-only，从首个触发日起算：
     - `5d`：约 `+1.04pp`
     - `10d`：约 `+0.53pp`
     - `15d`：约 `+3.24pp`
     - `20d`：约 `+3.95pp`
   - 也就是说，尽管 non-overlap `5d` blocks 不是单调稳定，但 cumulative shadow review checkpoints 当前 `4/4` 仍都没有翻回 gate-only 下方。
   - 这让 breakout 默认主候选的更诚实口径进一步收敛成：
     - **local blocks 会起伏，但 cumulative shadow review 目前仍站得住**。

3. **mixed-tail overlay 的位置也更清楚了。**
   - mixed-tail overlay 自己的 cumulative checkpoints 约也是 `4/4` 为正：
     - `+0.55pp / +0.57pp / +0.59pp / +0.19pp`
   - 但 edge 到 `20-day` 已经很薄；
   - 再结合此前 non-overlap `5d/10d` forward 与 target-pocket honesty 仍是 split verdict，mixed-tail 更诚实的位置仍是：
     - `shadow-only mixed gate`
   - 它仍不该替代默认 `pair halfsize` 主候选。

4. **项目级 `paper -> small-live` promotion gate 已补齐。**
   - 新增 `promotion gate v1` 后，项目现在不只会说：
     - `closest to paper / one_more_gate / park`
   - 还会明确说：
     - paper 至少跑多久；
     - drawdown guardrail 是什么；
     - 什么情况 freeze promotion；
     - small-live 资金上限是多少；
     - 触发什么条件就必须 rollback。
   - 这是很关键的 deployment-facing 收口，不是装样子的“快要上实盘”幻觉。

5. **EMA 的 ranking 仍稳定，但其下一步更明确地变成了 `runbook`。**
   - `EMA baseline family` 仍是 `closest to paper`；
   - `沪深300ETF 1d` 仍是 `positive_but_not_promotable / stay shadow`；
   - 现在更像该继续补的，不是更多 board，而是把现有 `candidate / operating / monitoring` 真接成 `paper-trading runbook`。

## 当前 weakest / should-park lines

1. `Fibonacci`：继续 `park / archive`。
2. breakout 的 `blunt pure-down overlay`：可以继续视为已被否掉的错误捷径。
3. EMA 再扩 entry-layer board：继续降级；当前更该补 runbook / shadow rules。

## 下一步优先级 Top 1~3

### Top 1. breakout：继续沿默认 `pair-conditioned halfsize` 主候选推进最后一道 gate

当前最该继续的是：
- 默认主候选本身的更长 forward / shadow honesty；
- 不要让 mixed-tail 附加 gate 继续吸走主资源。

### Top 2. EMA：把 `candidate spec / operating spec / monitoring board` 真接成 `paper-trading runbook`

现在 EMA 离部署最近，但还差一块非常关键的“真执行”桥梁：
- 数据源与刷新频率
- 记账口径
- promote / demote 规则
- kill switch / rollback
- 什么时候把 secondary 降回 shadow

### Top 3. 项目级：把 `promotion gate v1` 后续接入实际 shadow review 节奏

现在 gate 已经写出来了，下一刀更值得做的是：
- 让未来 EMA / breakout 真进入 paper 时，能按同一 review cadence 对照执行；
- 避免 gate 只停留在 closure board 上。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 bot2 / bot3 / bot7 prompt**
- **本轮不改 project-level ranking / verdict**

原因：
1. bot3 当前已恢复并稳定执行；
2. breakout / EMA 当前主线都没有重新跑偏；
3. 当前更高价值动作是把 deployment 读法讲清，而不是再次改 steering。

## 网页 / 表达建议

1. `alpha_closure_board` 当前短期最值得固定的口径是：
   - `EMA = closest to paper, next step = runbook`
   - `breakout = one_more_gate, default candidate still pair halfsize`
   - `mixed-tail = shadow-only`
   - `promotion gate v1` 已就位

2. `support_breakout_v0` 页面当前最值得保留的 deployment 读法是：
   - default candidate 的 cumulative shadow review checkpoints `4/4` 仍为正；
   - mixed-tail gate 虽没塌，但 edge 很薄，仍只配当 `shadow-only mixed gate`。

3. `EMA / PSAR` 页面下一步不该再追求“更完整介绍”，而应开始向 runbook / shadow operating rules 迁移。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 当前不需要再改 wiring / prompt；
   - 更该继续沿 breakout 主候选 gate 与 EMA runbook gap 推进。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`paper-trading runbook / shadow operating rules`，以及 `shadow-only pocket` 的更长 promotion honesty

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：默认 `pair-conditioned sizing` 的迁移性证明
  - 当前 deployment queue：
    - `default pair halfsize = keep / default candidate`
    - `mixed-tail overlay = shadow-only mixed gate`
    - `blunt pure-down overlay = reject blunt patch`
  - 当前更硬读法：
    - local blocks 不单调；
    - 但 default candidate 的 cumulative shadow review checkpoints 当前 `4/4` 仍为正

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. breakout 默认主候选虽然 cumulative review 仍为正，但真正最难的 `down-tail / pure-test honesty` 仍未被彻底解除。
2. mixed-tail overlay 虽未塌，但其 edge 已很薄，若后面继续深挖，很容易稀释默认主候选主线。
3. EMA 若迟迟不把现有候选体系接成真正 runbook，就会一直停留在“最接近 paper，但永远不真正开始 shadow”的状态。
