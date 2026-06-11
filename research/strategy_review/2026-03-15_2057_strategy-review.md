# 2026-03-15 20:57 UTC · Light Strategy Review

## 本轮一句话判断

这轮**不改项目级总排序，也不再改 TODO 主结构**。当前最诚实的项目判断仍然是：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。本轮最重要的新事实是：**20:17 之后 bot3 既继续守住 waiting-window freeze，没有重新长近义 deployment 页；同时又把首页 hero 口径同步成当前真实优先级。** 这意味着当前系统已经同时满足两件事：

1. 执行层不会在没到点时伪造 EMA refresh；
2. 网页总入口也不再把三条线平均推进，而是直接把 `EMA -> breakout -> Fibonacci` 的真实 deployment 顺序写出来。

因此本轮最合理的动作，不是继续改 TODO，而是确认：**现在真正缺的仍是下一根真实 completed daily bar，而不是新的 protocol / queue / source / closure 文案。**

## 本轮先检查了什么

1. repo 状态与最近 optimization loop：
   - `2026-03-15_2026_homepage-priority-sync.md`
   - `2026-03-15_2035_no-progress.md`
   - `2026-03-15_2049_no-progress.md`
2. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：最近仍是 timeout，但与本轮主线判断无关
3. `docs/TODO.md` 当前 EMA open task（line-299）与最新守门补充
4. 首页 `reports/site/index.html` 与 `scripts/build_site_index.py` 当前 hero 口径

## 当前 strongest evidence

### 1) waiting-window freeze 继续生效，而且 bot3 没有重新漂回近义 deployment 页

20:17 之后最关键的行为序列是：
- `20:26`：做了一次 `homepage priority sync`
- `20:35`：明确 `NO_PROGRESS`
- `20:49`：再次明确 `NO_PROGRESS`

这说明 bot3 并没有无视边界继续长新的 `overlay / source / queue / closure-copy` 近义页。它在这个窗口里只做了一类仍算高杠杆的小动作：**把首页入口表达同步到当前真实优先级**；之后就继续老老实实承认“没到真实 close，不伪造 refresh”。

### 2) `homepage priority sync` 这次是有价值的入口表达收口，不是新的方向漂移

`2026-03-15_2026_homepage-priority-sync.md` 做的事情很克制，但很有用：
- 把首页 hero 从旧的“closure-first 平铺三条线”改成现在更诚实的 deployment 优先级：
  - `EMA baseline family（closest to paper）`
  - `support_breakout_v0（one_more_gate）`
  - `Fibonacci（archived / optional filter）`
- 同时把首页最短判断也压直：
  - `EMA` 的下一步不是继续补 board，而是到点后跑
    `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - `breakout` 仍只能按 `up-flat biased conditional alpha / one_more_gate` 读
  - `PyTrendline v3` 只留作历史证据包，不再挂成 active 主任务

这一步的价值不在于新增 alpha 证据，而在于减少 Jerry 在首页层面的判断摩擦：现在只看首页，也能立刻知道**谁最该继续、谁只是 one-more-gate、谁已归档**。

### 3) EMA 当前最缺的 gate 仍然没变：还是下一轮真实 refresh / week-1 review

尽管这轮新增了首页 hero 同步，EMA 的 deployment blocker 并没有变化：
- active `1d` lanes 仍约 `live = 5`
- `cache fallback = 0`
- `data unavailable = 0`
- guarded refresh entry + due guardrail 也都已就位

所以当前最缺的仍然不是：
- 首页口径
- source-risk 说明
- queue / guardrail / smoke test 文案

而是：
- **真实 completed daily bar 到来后，primary / front-queue secondary / shadow lane 的 refresh / review 会不会继续守住。**

### 4) breakout / Fibonacci 本轮没有任何新证据足以改写排序

- **breakout**：仍是 `one_more_gate`；当前样本 same-sample freeze 后也没有新的 `pure-test / down-tail` forward/shadow 命中。
- **Fibonacci**：继续 archive。

所以这轮没有任何理由把资源从 EMA 主线移开，或重新平均推进三条线。

## 本轮最小必要干预

### 这轮不改 `docs/TODO.md`

原因：
- line-299 当前 open task 已经足够准确；
- `waiting-window freeze` 仍有效；
- `homepage priority sync` 解决的是入口表达，不是任务边界漂移；
- 再继续改 TODO，只会把“现在该等真实 close”重新包装成新的治理问题。

### 这轮不改 closure board 主排序

原因：
- `EMA = closest to paper`
- `breakout = one_more_gate`
- `Fibonacci = park`

本轮都没有变。

### 这轮不改 cron 频率

原因：
- 当前 bot3 不是停跑，也不是重新文案漂移；
- 最近状态仍是 `ok`；
- 当前真正限制来自市场时钟，不是调度节奏。

## 为什么这轮“不改”反而更合理

因为当前最容易犯的错，是看到 bot3 又补了一次网页入口同步，就忍不住继续改 prompt / TODO / protocol。

但本轮最新证据恰恰说明：
- freeze 还在生效；
- bot3 知道什么时候该停；
- guarded entry 已经把“没到点别伪刷”压成单命令守门入口；
- 首页 hero 也已经同步成当前真实优先级；
- 当前系统缺的不是表达层，而是**真实 close 后的新一轮 forward refresh / review**。

所以这轮最合理的动作不是再收紧，而是确认：
**等待状态已经足够健康，且入口表达也已跟上；下一步该由真实 completed bar 触发，而不是由 bot2 再改一层文案触发。**

## 下一步优先级 Top 1~3

### Top 1. EMA：到点后先跑 guarded entry，再沿同一张 live ledger 落真正 refresh / review

默认入口仍是：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

之后继续回答三件事：
1. `创业板ETF 1d` primary 是否继续守住
2. front-queue secondary 是否需要 `keep / stricter recheck / demote`
3. week-1 review 到时后，是否首次出现 `yellow / red`

### Top 2. 若执行层再出错，只修执行阻塞本身

例如：
- `exact-text mismatch`
- build / loader / data source 故障
- guarded entry 本身的脚本异常

但修的目标仍应是让 line-299 能继续落账，而不是顺手再扩写新的部署说明页。

### Top 3. breakout：继续维持 `one_more_gate`

在没有新的 `pure-test / down-tail` shadow/forward 证据前，不 reopen 当前样本 retrospective slicing。

## 本轮改动

- 新增 review 记录：
  - `research/strategy_review/2026-03-15_2057_strategy-review.md`
- 本轮明确**不改**：
  - `docs/TODO.md`
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率
- 但顺手确认并收口当前仍未提交的 deployment-facing 小改动：
  - `docs/TODO.md` 中关于 `due_guardrail + guarded_refresh` 的最新补充
  - `scripts/build_site_index.py` 的首页 hero 优先级同步
  - `reports/site/index.html` 的首页静态页更新

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 当前网页结构已经足够回答：
  1. EMA 当前在等真实 next close，不是 stale
  2. breakout 当前仍是 `one_more_gate`
  3. Fibonacci 已归档
  4. 首页 hero 也已不再把三条线平均推进

下一次真正值得改网页，仍应等：
- 真实 completed bar 到来后
- 新一轮 refresh / review 真落下去

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改（timeout 与当前主线判断无关）

原因：
- 当前不是调度问题；
- 也不是 bot3 又开始文案漂移；
- 当前系统已经更像进入了正确的 `waiting for next close, but homepage already synced` 状态。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. `homepage priority sync` 是入口表达同步，不是新的 alpha 证据；不能把它误读成 EMA 又向 admission 前进了一大步。
2. 若下一轮 bot3 又重新回到近义 deployment-page 漂移，这轮“不改”的判断需要复核。
3. 若真实 completed bar 到来后 EMA 很快出现 `yellow / red`，当前“closest to paper”的优势也会收窄。

## 本轮一句话结论（给 Jerry）

**这轮最值得记的不是又多了一页研究，而是系统已经同时做到两件事：一方面 bot3 不会在没到点时伪造 EMA refresh，另一方面首页也终于把 `EMA -> breakout -> Fibonacci` 的真实优先级写直了；所以这轮我不再改 TODO，继续等真实 next close。**
