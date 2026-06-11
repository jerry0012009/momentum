# 2026-03-15 19:37 UTC · Light Strategy Review

## 本轮一句话判断

这轮**不改项目级总排序，也不再改 TODO 主结构**。当前最诚实的项目判断仍然是：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。更重要的是，上轮加上的 `waiting-window freeze` 基本已经生效：bot3 在 18:55 之后先连续两轮明确给出 `NO_PROGRESS`，没有再继续扩写近义 `overlay / source / queue / closure-copy` 页面；随后新增的 `due-guardrail snapshot` 也仍属于执行层守门，而不是新的方向漂移。因此这轮最合理的动作不是再继续收紧 TODO，而是**明确确认：当前真正缺的仍是下一根真实 completed daily bar，而不是新的 protocol / deployment 文案。**

## 本轮先检查了什么

1. repo 状态与最近 optimization loop：
   - `2026-03-15_1905_no-progress.md`
   - `2026-03-15_1918_no-progress.md`
   - `2026-03-15_1935_ema-due-guardrail-snapshot.md`
2. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：仍是 timeout，但与本轮主线判断无关
3. `docs/TODO.md` 当前 EMA open task 与上轮追加的 `waiting-window freeze`
4. EMA 主报告最新 `Q35h / Q35i` 对 next-close / due-now 的执行守门口径

## 当前 strongest evidence

### 1) 上轮的 waiting-window freeze 基本生效了

18:55 之后最关键的事实不是 bot3 又写了多少页，而是：
- `19:05`：明确 `NO_PROGRESS`
- `19:18`：再次明确 `NO_PROGRESS`
- `19:35`：只补了一张 `due-now / overdue` 守门快照

这说明 bot3 当前并没有无视边界继续长近义 deployment 页，而是基本遵守了上轮要求：
- 没有新 completed bar 时，不伪造 EMA refresh / week-1 review；
- breakout 在现有样本拿不到新的 admission 级证据时，也不再回去切同一样本的 retrospective micro-slices。

### 2) `due-guardrail snapshot` 仍算执行层有效补丁，不算新的方向漂移

`2026-03-15_1935_ema-due-guardrail-snapshot.md` 的价值不是再回答“EMA 多接近 paper”，而是把执行层再守紧一格：
- `Q35h` 回答“到点后先做什么”；
- `Q35i` 进一步回答“什么时候已经不能继续写成 waiting，而该切成 due-now / overdue”。

当前最新读法大致是：
- `Crypto 1d+1wk`：`due_soon`，距下一次 close 约 `4.4h`
- `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d`：`waiting_not_due`，距下一次 close 约 `11.4h`
- `美股 1d+1wk`：`waiting_not_due`，距下一次 close 约 `1d`

这张快照虽然还是 deployment artifact，但它直接服务同一个 open task（line-299），而不是又拐回到新的 overlay/source/closure 文案分支。

### 3) EMA 当前最缺的 gate 没变：仍是下一轮真实 refresh / week-1 review

尽管 bot3 在等待窗口里补了最后一层 due guardrail，项目级 blocker 仍没有变化：
- active `1d` lanes 仍约 `live = 5`
- `cache fallback = 0`
- `data unavailable = 0`
- 当前主要是正常 `waiting next close`

所以当前最缺的仍然不是：
- source-risk
- protocol 设计
- next-close queue
- due-now 守门

而是：
- **下一根真实 completed daily bar 到来后，primary / front-queue secondary / shadow lane 的 refresh / review 会不会继续守住。**

### 4) breakout / Fibonacci 本轮也没有任何新证据足以改写排序

- **breakout**：当前仍是 `one_more_gate`；`scope verdict / current-sample freeze` 之后没有新的 `pure-test / down-tail` forward/shadow 命中。
- **Fibonacci**：继续 archive。

因此这轮没有任何理由把资源从 EMA 主线移开，或重新平均推进三条线。

## 本轮最小必要干预

### 这轮不改 `docs/TODO.md`

原因很明确：
- 上轮追加的 `waiting-window freeze` 已经起作用；
- bot3 当前没有再次明显漂向近义 deployment-page 写作；
- `due-guardrail snapshot` 也仍属于 line-299 的执行守门，不需要再追加新的限制条目。

再多改一刀，反而会把“当前真正缺的是下一根真实 close”这个简单事实，重新包装成复杂 prompt 治理问题。

### 这轮不改 closure board 主排序

原因：
- `EMA = closest to paper`
- `breakout = one_more_gate`
- `Fibonacci = park`

本轮都没有变。

### 这轮不改 cron 频率

原因：
- 当前 bot3 并不是停跑，也不是继续乱跑；
- 最近状态是 `ok`，而且新增产物与当前主线仍一致；
- 当前真正的限制来自市场时钟，不是调度节奏。

## 为什么这轮“不改”反而更合理

因为当前最容易犯的错，就是在已经冻结住等待窗口漂移后，又为了“每轮都得做点什么”继续去改 TODO / prompt / protocol。

但本轮最新证据恰恰说明：
- freeze 已经基本生效；
- bot3 现在知道什么时候该停；
- 唯一新增的 `due-now / overdue` 守门，也仍然是执行层有用补丁，而不是新的叙事枝杈。

所以这轮最好的动作不是再收紧，而是明确说：
**当前系统已经处在对的等待状态，下一步该由真实 completed bar 触发，而不是由 bot2 继续改文案触发。**

## 下一步优先级 Top 1~3

### Top 1. EMA：等下一根真实 completed daily bar，按 `next-close queue + due-guardrail` 落真正 refresh / review

重点仍是三件事：
1. `创业板ETF 1d` primary 是否继续守住
2. front-queue secondary 是否需要 `keep / stricter recheck / demote`
3. week-1 review 到时后，是否首次出现 `yellow / red`

### Top 2. 若执行层再出错，只修执行阻塞本身

例如：
- `exact-text mismatch`
- build / loader / data source 故障

但修的目标仍应是让 line-299 能继续落账，而不是顺手再扩写新的部署说明页。

### Top 3. breakout：继续维持 `one_more_gate`

在没有新的 `pure-test / down-tail` shadow/forward 证据前，不 reopen 当前样本 retrospective slicing。

## 本轮改动

- 新增 review 记录：
  - `research/strategy_review/2026-03-15_1937_strategy-review.md`
- 本轮明确**不改**：
  - `docs/TODO.md`
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 现有网页已经足够回答：
  1. EMA 当前在等真实 next close，不是 stale
  2. `PSAR overlay` 当前只配 `创业板ETF 1d` 的 `shadow-only` sidecar
  3. `next-close queue + due-guardrail` 已经把“到点/未到点/过点未刷”的执行边界写清楚

下一次真正值得改网页，仍然应等：
- 真实 completed bar 到来后
- 新一轮 refresh / review 真落下去

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改（timeout 与当前主线判断无关）

原因：
- 当前不是调度问题；
- 也不是 bot3 又开始文案漂移；
- 当前系统更像已经进入了正确的 `waiting for next close` 状态。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. `due-guardrail snapshot` 是执行守门补丁，不是新的 alpha 证据；不能把它误读成 EMA 又往 admission 迈进了一大步。
2. 若后续 bot3 又重新回到近义 deployment-page 漂移，这轮“不改”的判断需要复核。
3. 若下一根真实 completed bar 到来后 EMA 很快出现 `yellow / red`，当前“closest to paper”的优势也会收窄。

## 本轮一句话结论（给 Jerry）

**上轮加上的 waiting-window freeze 基本已经生效：bot3 这轮没有继续乱长近义页，只补了一个执行层 guardrail；所以这轮我不再动 TODO，当前真正该发生的下一步，还是等真实 next close 来触发 refresh / review。**
