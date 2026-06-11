# 2026-03-15 22:17 UTC · Light Strategy Review

## 本轮一句话判断

这轮**不改项目级总排序，也不再改 TODO / cron 主结构**。当前最诚实的项目判断仍然是：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。相比上一轮，这轮最重要的新事实不是研究结论变化，而是：**bot3 在修掉 waiting-window 里的重复 edit 噪音后，已经连续回到 `ok`，并且后续几轮都老老实实给出 `NO_PROGRESS`，没有重新漂回近义 deployment-page 写作。** 这说明当前系统已经回到健康状态：研究方向没变，执行噪音也暂时压住了，下一步仍该由真实 completed daily bar 触发，而不是由 bot2 再改文案触发。

## 本轮先检查了什么

1. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：仍 timeout，但与本轮主线判断无关
2. bot3 最近 5 条 run records：
   - 两次旧 error 都是重复 edit 噪音（已在上一轮修掉）
   - 之后手动补触发 run 已恢复成 `ok`
   - 最新正常 run 摘要明确写的是：
     - `无法形成有效推进：EMA 还没到下一根真实 daily close（Crypto 1d 约 1.9 小时后），breakout 旧样本也无新翻案入口`
3. 最近 optimization loop：
   - `2026-03-15_2140_no-progress.md`
   - `2026-03-15_2154_no-progress.md`
   - `2026-03-15_2207_no-progress.md`
4. `docs/TODO.md` 当前 EMA open task 与 waiting-window duplicate-edit freeze 约束
5. 当前 guarded refresh / homepage / plans 状态

## 当前 strongest evidence

### 1) bot3 已经从“重复 edit 报错”回到健康等待状态

上一轮最值得修的点，是 bot3 在 waiting window 里围绕同一批 execution 文件反复 edit，结果触发：
- `build_site_index.py` exact-text mismatch
- `run_ema_paper_trading_guarded_refresh.py` identical-content / no changes made

这轮最关键的新事实是：
- 手动补触发后，bot3 已恢复成 `lastRunStatus = ok`
- `consecutiveErrors` 也已回到 `0`
- 后续最近几轮没有继续在同类文件上重复打补丁，而是直接给出 `NO_PROGRESS`

换句话说：
**当前系统不是“研究主线迷路”，而是已经从 execution noise 里爬出来了。**

### 2) 最近 3 条优化记录都在健康地承认“还没到真实 close”

最近三个新文件：
- `21:40` 左右：`2026-03-15_2140_no-progress.md`
- `21:54` 左右：`2026-03-15_2154_no-progress.md`
- `22:07`：`2026-03-15_2207_no-progress.md`

它们的共同含义很简单：
- EMA 当前还没有新的真实 daily close
- breakout 也没有新的 `pure-test / down-tail` 翻案入口
- 所以这轮不伪造 forward 结果，就是最诚实的推进方式

这和前几轮的守门逻辑是完全一致的：
- guarded refresh 只在 `due_now / overdue` 才应继续
- 没到点就返回 `NO_PROGRESS`

### 3) EMA 当前最缺的 gate 仍然没变：还是下一轮真实 refresh / week-1 review

这轮并没有出现任何足以改写 EMA deployment gate 的新证据：
- 当前 active `1d` lanes 仍约 `live = 5`
- `cache fallback = 0`
- `data unavailable = 0`
- guarded refresh / due guardrail / refresh history / homepage deployment watch 都已到位

所以现在真正缺的仍然不是：
- source-risk
- queue / due guardrail
- guarded refresh entry
- homepage priority sync

而是：
- **真实 completed daily bar 到来后，primary / front-queue secondary / shadow lane 的 refresh / review 会不会继续守住。**

### 4) breakout / Fibonacci 本轮没有任何新证据足以改写排序

- **breakout**：仍是 `one_more_gate`；最近几轮没有新的 `pure-test / down-tail` shadow/forward 命中。
- **Fibonacci**：继续 archive。

所以这轮没有任何理由把资源从 EMA 主线移开，或重新平均推进三条线。

## 本轮最小必要干预

### 这轮不改 `docs/TODO.md`

原因：
- 上轮加的 `duplicate-edit freeze` 已经起作用；
- bot3 当前已恢复到健康等待状态；
- 最近 3 条 `NO_PROGRESS` 正说明它没有继续对同一批 execution 文件乱动。

再继续加 TODO 约束，只会把已经恢复健康的 waiting window 重新复杂化。

### 这轮不改 closure board / 首页主排序

原因：
- `EMA = closest to paper`
- `breakout = one_more_gate`
- `Fibonacci = park`

首页 hero 与 closure board 当前都已经和这个判断对齐。

### 这轮不改 cron 频率

原因：
- 当前 bot3 不是停跑；
- 也不是继续 execution error；
- 最近状态是 `ok -> ok -> ok`，只是市场时钟还没给出新的 close。

## 为什么这轮“不改”反而更合理

因为当前最容易犯的错，是看到 bot3 已经从错误里恢复，就忍不住继续加新的 steering 条款。

但本轮最新证据恰恰说明：
- 研究主线没变；
- execution noise 已压住；
- waiting window freeze 继续生效；
- bot3 也已经学会在没到点时只返回 `NO_PROGRESS`。

也就是说，当前系统真正需要的已经不是更多治理，而是：
**等真实 completed bar 来触发下一轮 refresh / review。**

## 下一步优先级 Top 1~3

### Top 1. EMA：继续等真实 completed bar，到点后先跑 guarded refresh

默认入口仍是：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

到点后继续回答三件事：
1. `创业板ETF 1d` primary 是否继续守住
2. front-queue secondary 是否需要 `keep / stricter recheck / demote`
3. week-1 review 是否首次出现 `yellow / red`

### Top 2. 若执行层再出错，只修新的执行阻塞

例如：
- guarded entry 脚本异常
- loader / data source 故障
- 真正新的 build breakage

但不要再对已经落地的 `refresh_history / deployment watch / fast-precheck` 重复打补丁。

### Top 3. breakout：继续维持 `one_more_gate`

没有新的 `pure-test / down-tail` 证据前，不 reopen 当前样本 retrospective slicing。

## 本轮改动

- 新增 review 记录：
  - `research/strategy_review/2026-03-15_2217_strategy-review.md`
- 本轮明确**不改**：
  - `docs/TODO.md`
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 首页 hero / deployment watch 也已经够用：
  - 当前优先级已写直
  - 当前守门状态也已写清
- 下一次值得改网页，仍应等：
  - 真实 completed bar 到来后
  - 新一轮 refresh / review 真落下去

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改

原因：
- 当前不是调度问题；
- 当前也不是 execution noise 继续发散；
- 当前系统已经回到正确的 `waiting for next close` 状态。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. 当前恢复的是 execution 健康度，不是新增 alpha 证据本身。
2. 即使最近几轮重新回到 `ok`，也不代表 EMA 已完成 line-299；它仍在等真实 next close。
3. 若后续 bot3 再次回到重复 edit 噪音，这轮“不改”的判断需要复核。

## 本轮一句话结论（给 Jerry）

**这轮最重要的新事实不是研究方向变了，而是 bot3 已经从 waiting-window 里的重复 edit 噪音里恢复过来，并且后面几轮都老老实实 `NO_PROGRESS`；所以这轮我不再加新的治理条款，继续等真实 next close。**
