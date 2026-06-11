# 2026-03-15 20:17 UTC · Light Strategy Review

## 本轮一句话判断

这轮**不改项目级总排序，也不再改 TODO 主结构**。当前最诚实的项目判断仍然是：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。本轮真正新增的、且最有 deployment 价值的事实不是研究结论变化，而是：**bot3 已把 EMA 的“到点才允许 refresh / 没到点禁止伪 refresh”压成单命令守门入口，并已完成 smoke test。** 这意味着当前系统不只是“知道该等下一根 completed bar”，而是已经具备了更可执行的守门动作；因此这轮最合理的动作不是继续改 TODO，而是确认：**现在真正缺的仍是下一根真实 completed daily bar，而不是新的 queue / source / overlay / closure 文案。**

## 本轮先检查了什么

1. repo 状态与最近 optimization loop：
   - `2026-03-15_1944_no-progress.md`
   - `2026-03-15_1959_ema-guarded-refresh-entry.md`
   - `2026-03-15_2010_ema-guarded-refresh-smoketest.md`
2. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：最近仍是 timeout，但与本轮主线判断无关
3. `docs/TODO.md` 当前 EMA open task 与新增的 guarded-refresh 补充说明
4. EMA 主报告当前 `Q35h / Q35i` 与最新守门执行入口口径

## 当前 strongest evidence

### 1) waiting-window freeze 继续生效，而且 bot3 这轮没有重新漂回近义部署页

19:37 之后最关键的事实不是“bot3 又补了几页研究说明”，而是它继续守住了上轮边界：
- `19:44`：再次明确 `NO_PROGRESS`
- `19:59`：补的是 `guarded refresh entry`，不是新的 queue/source/closure 近义页
- `20:10`：做的是 `smoke test`，确认守门入口在没到点时会拒绝伪 refresh

这说明 bot3 这轮不是在“无事可做时继续长文案”，而是在把同一个未完成主任务（EMA 连续 refresh / week-1 review）压成更可执行的 entrypoint。

### 2) `run_ema_paper_trading_guarded_refresh.py` 是当前等待窗口里合理且高杠杆的执行层收口

本轮最值得记下的新动作是新增：
- `scripts/run_ema_paper_trading_guarded_refresh.py`

它做的事很克制，但很有用：
- 默认先重跑 `build_ema_psar_raw_alpha_report.py`
- 只读取：
  - `ema_paper_trading_due_guardrail_snapshot.csv`
  - `ema_paper_trading_next_close_action_queue.csv`
- 只输出与执行直接相关的 lanes：
  - `due_now_refresh_window`
  - `overdue_refresh_check`
  - `due_soon`
- 关键守门参数：
  - `--require-due`：如果当前没有 `due_now / overdue`，就直接返回 `code 2`，拒绝继续

这件事的 deployment 价值在于：
- 之前系统已经知道“还没到 next close，不能伪 refresh”；
- 现在则进一步把这件事**压成了单命令入口**，减少下一次真实 close 到来时还要手动翻 `queue / report / due_guardrail` 的执行漂移。

### 3) smoke test 已证明：当前仍然没到真实 refresh 窗口，系统会主动拦住伪 refresh

`2026-03-15_2010_ema-guarded-refresh-smoketest.md` 已把最关键的事实验证掉：
- 真跑：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 返回：
  - `code 2`
- 含义：
  - 当前没有 `due_now / overdue` lane
  - 系统会主动拒绝在 close 前伪造 refresh

当前最近的执行时钟也更清楚了：
- `Crypto 1d+1wk（BTC/ETH/SOL）`：约还有 `3.8h` 到下一次 UTC 日线 close
- `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d`：约还有 `10.8h`
- `美股 1d+1wk（SPY/QQQ/AAPL）`：约还有 `23.8h`

这说明 EMA 当前并不是 stale，也不是 bot3 没对齐主线；它现在的真实状态就是：
**账本、queue、due-guardrail、guarded entry 都准备好了，但市场还没给出下一根 completed daily bar。**

### 4) EMA 当前最缺的 gate 仍然没变：不是执行文案，而是下一轮真实 refresh / week-1 review

尽管本轮新增了 guarded entry + smoke test，项目级 blocker 还是没有改写：
- active `1d` lanes 仍约 `live = 5`
- `cache fallback = 0`
- `data unavailable = 0`
- 当前系统也已经具备 `next-close queue + due-guardrail + guarded entry`

所以当前最缺的仍然不是：
- source-risk
- next-close 执行队列
- due-now 守门
- deployment wording

而是：
- **真实 completed daily bar 到来后，primary / front-queue secondary / shadow lane 的 refresh / review 会不会继续守住。**

### 5) breakout / Fibonacci 本轮没有足以改写排序的新证据

- **breakout**：当前仍是 `one_more_gate`；same-sample freeze 后没有新的 `pure-test / down-tail` shadow/forward 命中。
- **Fibonacci**：继续 archive。

因此这轮没有任何理由把主资源从 EMA 主线移开。

## 本轮最小必要干预

### 这轮不改 `docs/TODO.md`

原因：
- line-299 当前 open task 已经足够准确；
- `waiting-window freeze` 仍有效；
- 新增的 guarded-refresh entry 与 smoke test 也已经被补回该任务的最新说明；
- 再继续改 TODO，只会把“现在该等真实 close”重新包装成新的治理问题。

### 这轮不改 closure board 主排序

原因：
- `EMA = closest to paper`
- `breakout = one_more_gate`
- `Fibonacci = park`

这三件事本轮都没变。

### 这轮不改 cron 频率

原因：
- 当前 bot3 不是停跑，也不是又漂回近义页面；
- 最近状态仍是 `ok`；
- 当前真正的限制来自市场时钟，不是调度节奏。

## 为什么这轮“不改”反而更合理

因为现在最容易犯的错，是看到 bot3 又补了一层执行入口，就忍不住继续改 prompt / TODO / protocol。

但本轮最新证据恰恰说明：
- freeze 还在生效；
- bot3 知道什么时候该停；
- guarded entry + smoke test 已经把“没到点别伪刷”压成了真正可执行的守门动作；
- 当前系统已经从“口头知道要等 close”进化到了“命令级别会主动挡住伪 refresh”。

所以这轮最合理的动作不是再收紧，而是明确确认：
**等待状态已经足够健康，下一步该由真实 completed bar 触发，而不是由 bot2 再改一层文案触发。**

## 下一步优先级 Top 1~3

### Top 1. EMA：到点后先跑 guarded entry，再沿同一张 live ledger 落真正 refresh / review

当前默认入口应改成：
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
  - `research/strategy_review/2026-03-15_2017_strategy-review.md`
- 本轮明确**不改**：
  - `docs/TODO.md`
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 现有网页与 TODO 入口已经足够回答：
  1. EMA 当前在等真实 next close，不是 stale
  2. `PSAR overlay` 当前只配 `创业板ETF 1d` 的 `shadow-only` sidecar
  3. `next-close queue + due-guardrail + guarded entry` 已把“未到点 / 到点 / 过点未刷”与“执行入口”都写清楚了

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
- 当前系统已经更像进入了正确的 `waiting for next close, but executable when due` 状态。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. `guarded refresh entry + smoke test` 是执行层守门升级，不是新的 alpha 证据；不能把它误读成 EMA 又向 admission 前进了一大步。
2. 若下一轮 bot3 又重新回到近义 deployment-page 漂移，这轮“不改”的判断需要复核。
3. 若真实 completed bar 到来后 EMA 很快出现 `yellow / red`，当前“closest to paper”的优势也会收窄。

## 本轮一句话结论（给 Jerry）

**EMA 这条线现在已经不只是“知道该等真实 close”，而是连“没到点别伪刷、到点后先跑哪条命令”都被压成了守门入口；所以这轮我不再改 TODO，当前真正该发生的下一步，仍然是等真实 next close 来触发 refresh / review。**
