# 2026-03-15 18:06 UTC · Light Strategy Review

## 本轮一句话判断

这轮**不改项目级总排序，也不再动 TODO 主结构**。当前最诚实的项目判断仍然是：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。而且 bot3 最近这一小时给出的新增信息并不是“又多写了一层近义 closure-copy”，而是两件更 deployment-facing 的真信息：

1. **EMA live ledger 目前是在正常等待下一根 completed daily bar，而不是停转。**
2. **PSAR overlay 在 A股 daily runbook 里目前只配 shadow/protective 观察位，不应焊进默认 runbook。**

因此这轮最合理的动作不是继续改 TODO、cron 或网页主口径，而是明确：**当前下一步仍然要等真实 market-close refresh / week-1 review；不要把等待 close 的空窗误判成 bot3 跑偏，也不要把 PSAR overlay 误写成默认 admission patch。**

## 本轮先检查了什么

1. repo 状态与最近 optimization loop：
   - `2026-03-15_1717_ema-refresh-clock-audit.md`
   - `2026-03-15_1720_no-progress.md`
   - `2026-03-15_1737_ema-baseline-comparator.md`
   - `2026-03-15_1805_ema-overlay-runbook-audit.md`
2. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：最近一轮 `status=error`，错误不是研究方向问题，而是一次 `edit exact-text mismatch`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：最近一轮 timeout，但不影响本轮主判断
3. `docs/TODO.md` 当前 deployment-facing EMA 剩余动作
4. `alpha_closure_board` 与 EMA 主报告当前 admission / runbook 口径

## 当前 strongest evidence

### 1) bot3 这轮并没有跑偏；“没有新推进”本身就是正确推进

`17:17` 的 `ema-refresh-clock-audit` 把当前状态压得很清楚：
- active `1d` lanes 约 `5/5` 都是 `on_clock_waiting_next_close`
- `Crypto-1d` 下一根 completed bar 约在 `2026-03-16 00:00 UTC`
- `A股-1d` 约在 `2026-03-16 07:00 UTC`
- `美股-1d` 约在 `2026-03-16 20:00 UTC`
- `week-1 review` 最早约在 `2026-03-22 17:16 UTC`

随后 `17:20` 的 `NO_PROGRESS` 其实是合理动作：当前没有新的真实 completed bar，如果这时候硬写“下一轮 refresh 结果”，那才是伪 forward。

所以这轮必须明确一点：
**bot3 这小时没有拿到新的前瞻结果，不代表它没对齐主线；相反，它这次选择不伪造不存在的结果，本身就是对齐了当前 deployment honesty。**

### 2) EMA 当前最缺的 gate 仍然是“连续真实 refresh / week-1 review”，不是新的 spec 页

前几轮已经把：
- day-0 snapshot
- first-refresh queue
- first-refresh delta
- all active daily snapshot
- refresh continuity
- dependency audit
- Eastmoney live source

都补齐了。现在最新 clock audit 又证明：
- source-risk 已基本拆掉；
- 账本也没有 stale；
- 当前真正缺的就是**等下一根真实 completed daily bar，然后继续把同一张 live ledger 往前写。**

也就是说，这轮最有价值的新信息不是“EMA 又多接近 paper 了一点”，而是：
**它现在已经到了必须按市场时钟等真实新 bar 的阶段。**

### 3) PSAR overlay 当前只能写成 shadow/protective 候选，不能写成默认 runbook patch

`18:05` 的 `ema-overlay-runbook-audit` 继续压实了一个很关键的 deployment-facing 边界：
- `创业板ETF 1d`（primary）上，`EMA + PSAR exit overlay` 在 `8` 个 holdout 里约 `75%` 改善，median net20 delta 约 `+2.00pp`
- 但 `沪深300ETF 1d`（shadow）上，仅约 `25%` 改善，median net20 delta 约 `-1.51pp`
- 合并后 overall 改善占比约 `50%`，median net20 delta 约 `-0.38pp`
- 当前 verdict 已明确写成：`mixed_shadow_only_not_default`

这条证据的意义不是“PSAR 没价值”，而是：
- 它可以继续作为 `primary shadow protective` 候选观察；
- 但还不足以焊进当前 A股 daily 的默认 runbook；
- 更不能拿它当 promotion patch 去替 `沪深300ETF 1d` 洗白。

### 4) breakout / Fibonacci 本轮没有任何新证据足以改写总排序

- **breakout**：当前仍是 `one_more_gate`，而且 same-sample retrospective slicing 已冻结；本轮没有新的 `pure-test / down-tail` shadow/forward 命中。
- **Fibonacci**：继续 archive。

所以这轮没必要把项目注意力从 EMA 主线移开。

## 当前 weakest / should-park lines

1. **Fibonacci**：继续 archive。
2. **breakout 的同样本 retrospective micro-slicing**：继续冻结；没新 forward 证据前不 reopen。
3. **EMA 的近义 refresh / source / closure-copy 页面**：在 clock audit 已说明“只是还没到下一根 close”之后，再补同类页面边际价值很低。

## 本轮最小必要干预

### 这轮不改 `docs/TODO.md`

原因：
- 当前 open task 已经足够准确：`沿同一张 live ledger 连续落下下一轮 market-close refresh / week-1 review 结果`
- `refresh_clock_audit` 已经把“为什么现在还没法继续写”说清楚；
- `overlay runbook audit` 也只是补充了 `PSAR` 当前在 runbook 里的边界，并没有改写项目级 priority。

### 这轮不改 closure board 主排序

原因：
- `EMA = closest to paper`
- `breakout = one_more_gate`
- `Fibonacci = park`

这三件事本轮都没有变。

### 这轮不改 cron 频率

原因：
- 当前 bot3 的主要阻塞不是频率不对，而是**真实 market-close 还没到**；
- 最近一次 bot3 `error` 也不是模型配额或调度失灵，而是一次 `edit exact-text mismatch`，属执行细节问题，不是策略方向问题。

## 为什么这轮不需要“为了有动作而硬做一刀”

因为当前最容易犯的错，恰恰是把“还没到 next close”误判成“需要再补一页 deployment 文案”。

如果 bot2 这轮继续出手改 TODO，很可能只会制造：
- 近义 refresh 说明页
- 近义 source 说明页
- 或把 `PSAR overlay` 过早包装成默认 runbook 部件

这些都不会提升下一步决策质量，反而会稀释当前已经很清楚的 deployment honesty。

所以这轮更好的动作是：
**明确说这轮不改，因为当前真正缺的是市场给出下一根真实 completed bar。**

## 下一步优先级 Top 1~3

### Top 1. EMA：等下一根真实 completed daily bar，继续同一张 live ledger 的 market-close refresh

重点还是三件事：
1. `创业板ETF 1d` primary 是否继续守住
2. front-queue secondary 是否需要 `keep / stricter recheck / demote`
3. week-1 review 到时后，是否首次出现 `yellow / red`

### Top 2. EMA：把 PSAR overlay 继续留在 `shadow protective` 观察位，不要提前焊进默认 runbook

当前 primary 有改善信号，但 overall 仍是 mixed；因此下一步若继续，也应是更窄的 shadow protocol，而不是默认接线。

### Top 3. breakout：继续维持 `one_more_gate`

在没有新的 `pure-test / down-tail` shadow/forward 命中前，不 reopen 当前样本 retrospective slicing。

## 本轮改动

- 新增 review 记录：
  - `research/strategy_review/2026-03-15_1806_strategy-review.md`
- 本轮明确**不改**：
  - `docs/TODO.md`
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- EMA 主报告已经足够回答两件关键事：
  1. 当前账本是在正常等待 next close，不是 stale
  2. `PSAR overlay` 目前只配 `shadow-only / protective observation`
- 下一次真正值得改网页，不是继续补同类说明，而是：
  - 等账本拿到下一根真实 completed bar 后
  - 把新一轮 refresh / review verdict 回写进去。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改（虽然最近一轮 timeout，但与当前主线判断无关）

补一句运维层判断：
- bot3 最近一轮 `error` 是一次 `edit exact-text mismatch`；
- 这更像执行细节错误，不是配额、调度、或研究方向漂移；
- 若只出现这一轮，不值得现在为它改 cron / 改主结构。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. 当前 clock audit 证明的是“按时等待 close”，不是“EMA 已通过 paper admission”。
2. `PSAR overlay` 在 primary 上有信号，不代表它已适合全 A股 daily 默认接线。
3. 若 bot3 的 `edit exact-text mismatch` 连续复发，再去修执行层手法才有意义；当前单次出现不值得过度反应。

## 本轮一句话结论（给 Jerry）

**这轮最重要的不是再改方向，而是承认 EMA 账本现在已经进入“按市场时钟等真实 next close”的阶段；同时把 PSAR overlay 的边界钉死为 shadow-only——所以这轮我不再改 TODO 主结构，只等下一根真实日线来决定下一步。**
