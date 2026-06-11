# 2026-03-15 22:57 UTC · Light Strategy Review

## 本轮一句话判断

这轮**不改项目级总排序，也不再改 TODO / cron 主结构**。当前最诚实的项目判断仍然是：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。相比上一轮，这轮最值得记的新事实不是研究结论变化，而是：**EMA 线已经从“健康等待”进一步推进到“等待 + 账本续写审计已接回主报告”，而且最靠前的 `Crypto 1d+1wk` 现在已进入 `due_soon`（约 1 小时）窗口。** 这说明当前系统不只会在没到点时拒绝伪 refresh，也已经把“下一次真正到点后应先看什么”写清了。

## 本轮先检查了什么

1. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：正常
2. guarded refresh 当前实跑结果：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due --show-limit 3`
   - 当前仍无 `due_now / overdue`，但 `Crypto 1d+1wk` 已进入 `due_soon`，距下一次真实 close 约 `1.0h`
3. 最近 optimization loop：
   - `2026-03-15_2226_homepage-dynamic-clock.md`
   - `2026-03-15_2234_no-progress.md`
   - `2026-03-15_2254_ema-refresh-history-audit.md`
4. `docs/TODO.md` 当前 EMA open task 与最新 `refresh_history_audit` 补充
5. `EMA / PSAR Raw Alpha Focus Report` 当前新增的 `Q35j` / history audit 口径

## 当前 strongest evidence

### 1) EMA 这条线仍然没到真实 close，但已经进入“下一轮最先该看谁”的 due-soon 状态

这轮最直接的新执行信息来自 guarded refresh 实跑：
- 当前还没有 `due_now / overdue` lane；
- 但最靠前的 `Crypto 1d+1wk（BTC/ETH/SOL）` 已经进入 `due_soon`；
- 距下一次 UTC 日线 close 约 `1.0` 小时。

这意味着当前最重要的下一次有效推进触发点已经很明确：
- **下一轮若真的出现实质推进，最可能先发生在 `Crypto 1d+1wk` 的真实 close 后 refresh。**

### 2) `refresh_history_audit` 把“最新快照”与“append-only ledger 是否真的连续续写”正式分开了

`2026-03-15_2254_ema-refresh-history-audit.md` 这轮的价值，不是继续补 protocol，而是把 EMA 的 append-only 记账 honesty 再推进一格：
- `ema_paper_trading_refresh_history.csv` 现在已正式挂回主报告；
- 新增 `ema_paper_trading_refresh_history_audit.csv`；
- 每条 lane 现在都能直接看：
  - `rows_recorded`
  - `distinct_completed_bars`
  - `history_status`
  - `next_needed_to_advance`

当前 audit 给出的最关键结论是：
- active lanes 目前大多仍是 `seed_only_history`
- `rows_recorded = 1`

所以 line-305 的真正完成标准现在也更清楚了：
- **不是只看覆盖式 snapshot 有没有更新**；
- 而是下一次真实 close 到来后，`rows_recorded` 是否从 `1` 增到 `2+`，history ledger 是否真的开始连续续写。

### 3) waiting-window freeze 仍然有效，bot3 没有重新漂回近义 deployment-page 写作

22:17 之后的行为很克制：
- `22:26`：修的是首页动态时钟，属于 honest ops clock；
- `22:34`：明确 `NO_PROGRESS`；
- `22:54`：修的是 `refresh_history_audit`，直接服务 line-305 的 bookkeeping honesty。

它没有重新回去补：
- 近义 queue / source / closure-copy
- 也没有重新切 breakout 冻结样本

这说明前面几轮收紧出来的 steering 仍然在发挥作用：
- **当前 waiting window 里只保留与真实执行最接近的动作。**

### 4) breakout / Fibonacci 本轮没有任何新证据足以改写排序

- **breakout**：仍是 `one_more_gate`；没有新的 `pure-test / down-tail` shadow/forward 命中。
- **Fibonacci**：继续 archive。

所以这轮没有任何理由把主资源从 EMA 主线移开。

## 本轮最小必要干预

### 这轮不改 `docs/TODO.md`

原因：
- line-305 当前 open task 已经够准确；
- 最新 `refresh_history_audit` 补充也已经把“下一次到点后该看什么”写清楚；
- guarded refresh 仍健康地返回 `due_soon / not yet due`，没有出现新的 execution blocker。

再继续加 TODO 约束，只会把当前已经很清楚的等待状态重新复杂化。

### 这轮不改 closure board / 首页主排序

原因：
- `EMA = closest to paper`
- `breakout = one_more_gate`
- `Fibonacci = park`

首页 hero 与 closure board 当前都已经和这个判断对齐。

### 这轮不改 cron 频率

原因：
- 当前 bot3 不是停跑；
- 也不是 execution noise 重新发散；
- 当前真正限制仍是市场时钟，只是最靠前的 `Crypto 1d+1wk` 已从远期等待进入了 `due_soon`。

## 为什么这轮“不改”反而更合理

因为当前最容易犯的错，是看到 `due_soon` 临近，就忍不住继续改 protocol / TODO / queue wording。

但本轮最新证据恰恰说明：
- 守门入口健康；
- waiting-window freeze 仍有效；
- 首页动态时钟已就位；
- append-only history audit 也已接回主报告；
- 当前缺的真的只剩：**下一根真实 completed bar。**

也就是说，当前系统已经把“等到点之前该做的准备工作”做得差不多了；再继续治理，边际价值很低。

## 下一步优先级 Top 1~3

### Top 1. EMA：优先等 `Crypto 1d+1wk` 下一次真实 close，到点后先跑 guarded refresh

默认入口仍是：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

而且下一次到点后，默认不只看 snapshot，要优先看：
1. `Crypto 1d+1wk` 是否真的从 `seed_only_history` 变成 `rows_recorded >= 2`
2. `创业板ETF 1d` primary 是否继续守住
3. front-queue secondary 是否需要 `keep / stricter recheck / demote`

### Top 2. 若执行层再出错，只修新的执行阻塞

例如：
- guarded entry 脚本异常
- loader / data source 故障
- 真正新的 build breakage

但不要再对已经落地的 `refresh_history / deployment watch / fast-precheck / dynamic clock` 重复打补丁。

### Top 3. breakout：继续维持 `one_more_gate`

没有新的 `pure-test / down-tail` 证据前，不 reopen 当前样本 retrospective slicing。

## 本轮改动

- 新增 review 记录：
  - `research/strategy_review/2026-03-15_2257_strategy-review.md`
- 本轮明确**不改**：
  - `docs/TODO.md`
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- EMA 主报告和首页当前已经把三层信息都写齐了：
  1. 现在是不是到点（dynamic clock / due guardrail）
  2. 到点后先做什么（guarded refresh / next-close queue）
  3. 账本是否真的开始连续续写（refresh history audit）

下一次值得改网页，仍应等：
- 真实 completed bar 到来后
- 新一轮 refresh / history append / review 真落下去

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改

原因：
- 当前不是调度问题；
- 当前也不是 execution noise 重新发散；
- 当前系统已经回到正确的 `waiting for next close, with due-soon visibility` 状态。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
  - 但现在比上一轮更具体：下一次最优先的真实触发点，是 `Crypto 1d+1wk` 的下一根 completed bar
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. `refresh_history_audit` 只是把 bookkeeping honesty 讲清楚，不是新的 alpha 证据。
2. 即使 `Crypto 1d+1wk` 已进入 `due_soon`，也不代表 EMA 线已经完成 line-305；真正完成仍要看 next close 后 history 是否真的 append。
3. 若下一轮真正到点后仍没有 `rows_recorded` 增量，这轮“不改”的判断需要复核。

## 本轮一句话结论（给 Jerry）

**这轮最重要的新事实不是研究方向变了，而是 EMA 这条线已经从“健康等待”推进到“最靠前的 Crypto lane 已进入 due-soon，且 append-only history audit 也接回主报告”；所以这轮我不再改 TODO，继续等真实 next close，但下一轮该优先盯的对象已经更明确了。**
