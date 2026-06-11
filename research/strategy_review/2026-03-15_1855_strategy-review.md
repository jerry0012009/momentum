# 2026-03-15 18:55 UTC · Light Strategy Review

## 本轮一句话判断

这轮项目级排序仍然不变：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。但 **bot3 在等待下一根真实 completed daily bar 的空窗里，又连续补了 `closure sync / deployment matrix / sidecar protocol / next-close action queue` 四步**。这些动作本身大多仍服务主线，但现在已经接近“把等待窗口写得过满”的边缘。因此本轮最小必要干预不是改结论、改 cron、或再改网页主口径，而是：**给 EMA 当前 open task 增加一条 waiting-window freeze 约束——在下一根真实 completed daily bar 到来前，不再继续新增近义 `overlay / source / queue / closure-copy` 页面；默认只允许两类动作：真实 refresh / review 落账，或修执行阻塞。**

## 本轮先检查了什么

1. repo 状态与最近 optimization loop：
   - `2026-03-15_1812_ema-psar-closure-overlay-sync.md`
   - `2026-03-15_1825_ema-psar-overlay-deployment-matrix.md`
   - `2026-03-15_1838_ema-chinext-shadow-protocol.md`
   - `2026-03-15_1853_ema-next-close-action-queue.md`
2. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：最近仍是 timeout，但不影响当前主线判断
3. `docs/TODO.md` 当前 EMA open task（line-299）
4. EMA 主报告 / closure 入口的最新 deployment-facing口径

## 当前 strongest evidence

### 1) bot3 18:00 后并不是在胡写；它确实把等待窗口压成了更可执行的 deployment 支撑层

最近四条新增大意如下：
- `18:12`：把 `PSAR overlay` 的 A股 daily verdict 同步到 `alpha_closure_board`
- `18:25`：把 `Crypto 60m + A股 daily` 压成统一 `overlay deployment matrix`
- `18:38`：把唯一还能继续观察的 pocket（`创业板ETF 1d`）压成 narrow `shadow protective protocol`
- `18:53`：把 `on-clock waiting next close` 压成 `next-close action queue`

这些动作并非完全重复劳动。它们确实让 Jerry 更容易在项目入口看清三件事：
- `EMA` 仍坐在 `closest-to-paper / default baseline seat`
- `PSAR overlay` 只配 `创业板ETF 1d` 的 `shadow-only protective sidecar`
- 下一根真实 close 到来时，账本应该按什么顺序落下一轮 refresh

### 2) 但同一条主线连续 4 次都在补 deployment wording / protocol / queue，已经接近 brief 里说的“应出手纠偏”的阈值

当前不是没有价值，而是**边际价值正在明显下降**：
- `refresh_clock_audit` 已经说清“现在只是等下一根 close”
- `overlay runbook audit` 已经说清“PSAR 不能焊进默认 runbook”
- `next-close action queue` 也已把“到点做什么”写成执行顺序

在这个前提下，如果 bot2 这轮还只观察、不加约束，bot3 下一轮很可能继续长出：
- 近义 overlay 说明页
- 近义 source/queue 说明页
- 近义 closure 同步页

这类页面不会比“真实 next close 后的 refresh / week-1 review”更接近 deployment honesty。

### 3) EMA 当前最缺的 gate 仍然没变：不是新 protocol，而是下一轮真实 refresh / review

当前更诚实的项目级状态仍是：
- active `1d` lanes 约 `live = 5`
- `cache fallback = 0`
- `data unavailable = 0`
- 当前主要是 `on-clock waiting next close`

也就是说，EMA 现在的主 blocker 仍然是：
- **下一根真实 completed daily bar 到来后，primary / front-queue secondary / shadow lane 的真实 refresh / review 会不会继续站得住**

而不是：
- 数据源还没修好
- protocol 还没写出来
- queue 还没排好

### 4) breakout / Fibonacci 本轮没有足以改写总排序的新证据

- **breakout**：仍是 `one_more_gate`；没有新的 `pure-test / down-tail` forward/shadow 证据。
- **Fibonacci**：继续 archive。

因此当前项目资源仍应压在 EMA 主线，而不是重新平均推进三条线。

## 本轮最小必要干预

### 只做 1 个动作：给 EMA open task 增加 waiting-window freeze 约束

已在 `docs/TODO.md` 的 EMA open task 下新增：

- 在下一根真实 completed daily bar 到来前，默认**不要**继续新增近义 `overlay / source / queue / closure-copy` 页面；
- 这个等待窗口里的有效动作只剩两类：
  1. 到点后按 `ema_paper_trading_next_close_action_queue.csv` 真落下一轮 refresh / review；
  2. 若执行时再次出现脚本/编辑层故障（例如 `exact-text mismatch`），只修执行阻塞本身，不再扩写新的部署说明页。

这是一个很小但高杠杆的纠偏：
- 不改项目级总排序；
- 不改 cron；
- 不改 closure 主口径；
- 只把 bot3 在等待窗口里的行为边界写死，减少近义 deployment-page 漂移。

## 为什么这轮要动，而不是继续“不改”

因为当前已经满足 brief 里的典型信号：
- 同一条线连续 2 轮以上主要在补 `protocol / wording / closure-copy / cleanup`
- 而没有新增真实 forward 验证结果
- 虽然原因合理（还没到 next close），但如果 bot2 不加边界，bot3 会继续把等待窗口写满

所以这轮最有杠杆的小动作，不是硬逼它伪造 refresh 结果，也不是再出一张 overlay 页面；而是：
**明确冻结等待窗口里的近义写作，只保留“真实落账”与“修执行阻塞”这两类动作。**

## 下一步优先级 Top 1~3

### Top 1. EMA：等下一根真实 completed daily bar，按 next-close queue 落真正的 refresh / review

继续回答三件事：
1. `创业板ETF 1d` primary 是否继续守住
2. front-queue secondary 是否需要 `keep / stricter recheck / demote`
3. week-1 review 到时后，是否首次出现 `yellow / red`

### Top 2. 若执行层再出错，只修执行阻塞本身

比如：
- `edit exact-text mismatch`
- 脚本构建失败
- loader / data source 突发异常

这些可以修；但修的目标应是让 line-299 能继续落账，而不是顺手再长出一页近义 deployment 文案。

### Top 3. breakout：继续维持 `one_more_gate`

在没有新的 `pure-test / down-tail` shadow/forward 证据前，不 reopen 当前样本 retrospective slicing。

## 本轮改动

- 已编辑 `docs/TODO.md`
  - 给 EMA 当前 open task 新增一条 `waiting-window freeze` 约束
- 新增 review 记录：
  - `research/strategy_review/2026-03-15_1855_strategy-review.md`
- 本轮不改：
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率
  - breakout / Fibonacci 项目级 verdict

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 现有网页已经足够回答：
  - EMA 当前在等真实 next close，不是 stale
  - PSAR overlay 当前只配 `创业板ETF 1d` 的 `shadow-only` sidecar
  - next close 到来时该按什么顺序执行
- 因此下一次值得改网页的条件不是再补 protocol，而是：
  - 等真实 completed bar 到来后
  - 把新一轮 refresh / review 结果回写进去。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改（timeout 与当前主线判断无关）

原因：
- 当前偏差不是调度问题；
- 而是 **等待窗口里容易继续长近义部署页**；
- 这轮已经通过 TODO 边界收紧来处理，无需动节奏。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. 当前新增的 `waiting-window freeze` 不是在否定这些 overlay/queue 结果有用，而是在承认它们已经接近边际递减。
2. 若下一轮 bot3 忽略这条边界，继续补近义 deployment 页，后续可能要进一步做 prompt-level steering。
3. 若真实 next close 到来后 EMA 很快打出 `yellow / red`，当前“closest to paper”的优势也会收窄。

## 本轮一句话结论（给 Jerry）

**EMA 现在仍是最接近 paper 的主线，但在下一根真实日线到来前，deployment 说明已经写得够多了；所以这轮我只做了一个小纠偏——把等待窗口冻结住，后面只许真落 refresh / review，或者修执行阻塞，不再继续长近义页。**
