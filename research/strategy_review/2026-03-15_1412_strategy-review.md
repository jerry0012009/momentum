# 2026-03-15 14:12 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实不是研究方向变化，而是：**bot3 刚才的“停跑”根因已确认是额度耗尽，不是 cron/wiring 故障；补额度后已恢复，并且恢复后没有空转，而是继续把 EMA 线往更接近真实 shadow/paper 启动的方向推进。** 因此当前项目级排序不变：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。

## 本轮先检查了什么

1. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：已恢复为 `lastRunStatus = ok`，`consecutiveErrors = 0`；
   - `bot2-strategy-review-40m`：正常；
   - `bot7-quant-digest-4h`：正常。
2. bot3 掉线原因复核：
   - 连续 4 次失败都不是调度失灵，而是模型侧 `403 auth`（套餐/额度耗尽）；
   - 补额度后手动 kick 一次，bot3 已恢复运行。
3. 最近研究推进：
   - `2026-03-15_1235_breakout-scope-verdict.md`
   - `2026-03-15_1344_ema-day0-kickoff-ledger.md`
   - `2026-03-15_1400_ema-day0-launch-seed-rows.md`
   - `2026-03-15_1405_ema-week1-review-scorecard.md`
4. `docs/TODO.md` 当前 deployment 路线与 admission 排位。

## 当前 strongest evidence

### 1) bot3 本身已经恢复，不需要误把“配额事故”当成研究方向问题

- 本轮最关键的运维事实是：bot3 的“没定时运行”只是**触发后被模型额度拦住**。
- 这说明当前不需要改 cron 结构，也不需要误判成 bot3 prompt / job wiring 漂移。
- 更重要的是：恢复后 bot3 并没有只写一条 `NO_PROGRESS`，而是继续产出了新的 EMA deployment-facing 结果。

### 2) EMA 线又连续往前推进了 3 步，离真实 shadow/paper 更近

恢复后的连续新产出是：
- `13:44`：`EMA day-0 kickoff checklist / ledger template`
- `14:00`：`EMA day-0 launch seed rows`
- `14:05`：`EMA first weekly review scorecard / red-yellow-green protocol`

这三步的意义是：
- EMA 现在不只停留在 `candidate spec / operating spec / monitoring board / runbook`；
- 它已经进一步补到了：
  1. **day-0 怎么开账**
  2. **开账当天先建哪几行**
  3. **第一周怎么 review、怎么 keep/demote/stop**

也就是说，EMA 的 deployment 位置已经更像 **Step 3 完整态，随时可进入 Step 4 的 0 真资金 shadow/paper 记账**。

### 3) breakout 线的主 verdict 这轮不需要再改

`2026-03-15_1235_breakout-scope-verdict.md` 已经把当前最硬口径写死：
- 仍是 `shadow-admission candidate / one_more_gate`
- 更诚实的 scope 是 `up-flat biased conditional alpha`
- 不是 `near-down protective policy`
- same-sample retrospective slicing 已基本榨干，下一次有效推进必须来自新的 `forward / shadow pure-test/down-tail` 证据

因此这轮不应因为 bot3 事故而反向去折腾 breakout 的项目级排序或 prompt 主轴。

## 当前 weakest / should-park lines

1. **Fibonacci**：继续保持 `park / archive`，没有任何理由在当前阶段抢资源。
2. **breakout 的同样本 micro-slicing**：当前更该视为“已接近榨干”的动作类型；除非出现新的 forward/shadow 命中，否则不值得继续切更细。

## 下一步优先级 Top 1~3

### Top 1. EMA：直接进入 `0` 真资金 shadow/paper 记账启动

当前最值得推进的不是再补近义 board，而是按已完成链条真正开始：
- kickoff checklist
- ledger template
- day-0 seed rows
- first-week review scorecard

换句话说，**EMA 现在更该从“研究对象”切到“开始运行的 shadow baseline”**。

### Top 2. breakout：保持 `one_more_gate`，等待新的 forward / down-tail 证据

当前更诚实的动作是：
- 不再继续在同一段历史样本里补近义 retrospective micro-slices；
- 只有拿到新的 `pure-test / down-tail` 命中，才继续推进 admission。

### Top 3. 监控 bot3 配额，而不是立刻改 cron 结构

这次事故说明 bot3 的高频 + 大上下文 token 消耗确实很容易打穿额度。
当前最小合理动作是：
- 先继续观察恢复后是否稳定；
- 若再出现同类 403，再优先做 **降耗收紧**（prompt/context 负担），而不是先动调度结构。

## TODO / roadmap / web / cron：这轮改不改

### 这轮不改 `docs/TODO.md`

原因：
- 当前 TODO 的 deployment 路线与 admission 排序仍然和最新证据一致；
- EMA 线恢复后继续沿正确路径推进，没有出现方向漂移；
- breakout 线的 scope verdict 也已经足够清楚。

### 这轮不改 cron 频率

原因：
- bot3 本轮事故是**额度问题，不是节奏问题**；
- 补额度后已恢复，且恢复后最新 run 已重新变成 `ok`；
- 现在立刻改频率，容易把“外部配额事故”误治成“项目调度设计错误”。

### 这轮不改主网页口径

原因：
- `alpha_closure_board` 当前的 admission 排序仍正确：
  - `EMA = closest to paper`
  - `breakout = one_more_gate`
  - `Fibonacci = park`
- 真正值得做的下一次网页变化，不是再写解释，而是**等 EMA 真正开始 shadow/paper 记账后，把 day-0 / week-1 状态接回 board**。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的，不再是 admission 说明书，而是**真正开始运行的 shadow/paper ledger**。
  - 更准确地说：它已经非常接近从 `Step 3` 进入 `Step 4`。

- **needs one more gate：support_breakout_v0**
  - 当前最缺的仍是新的 `forward / pure-test / down-tail` honesty 证据；
  - 不是组合层 wording，也不是再切同样本小片。

- **park / archive：Fibonacci**

## 风险与不确定性

1. 若 bot3 再次触发 403，这轮“不改 cron”的判断就要复核；但那时仍应优先考虑降耗，而不是默认改结构。
2. EMA 虽已非常接近真实 shadow/paper，但**尚未开始真实前瞻记账**；因此现在仍不能把它写成“已完成 paper trading admission”。
3. breakout 若未来真的拿到新的 pure-test/down-tail 命中，这轮“先冻结 same-sample slicing”的态度也需要重新放松。

## 本轮一句话结论（给 Jerry）

**bot3 已从配额事故中恢复，而且恢复后继续把 EMA 线推进到了可直接启动 day-0 / week-1 shadow 记账的状态；所以本轮最合理的项目判断仍是：先把 EMA 真正跑起来，breakout 继续维持 `one_more_gate`，不要因为刚才那次 403 误动 TODO 或 cron 主结构。**
