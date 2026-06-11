# 2026-03-15 14:52 UTC · Light Strategy Review

## 本轮一句话判断

这轮最值得做的不是再重写 admission 排位，而是**防止 EMA 线继续在 deployment-facing 文档层原地打转**。bot3 已恢复正常，最近一轮仍在稳定产出；但恢复后的新增结果已经连续推进到 `runbook / kickoff / seed rows / week1 review / recheck queue`，边际价值开始下降。**因此本轮的最小必要干预不是改 cron，也不是改总排序，而是把 TODO 明确往“EMA 真正启动首个 0 真资金 shadow/paper ledger”推一步。**

## 本轮先检查了什么

1. repo 状态与最近产出：
   - 最新 optimization loop：
     - `2026-03-15_1430_ema-secondary-recheck-queue.md`
     - `2026-03-15_1444_breakout-freeze-sync.md`
     - 再往前是 `1405 week1 review / 1400 day0 seed rows / 1344 kickoff ledger`
2. cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：正常
3. `docs/TODO.md` 当前 admission / deployment 路线
4. `alpha_closure_board` 当前首页口径

## 当前 strongest evidence

### 1) bot3 仍在正常服务主线，不需要改 cron

- bot3 本轮前一次“停跑”已经确认只是额度耗尽；
- 现在最新 run 已恢复成 `ok`，说明当前不需要误把外部配额事故当调度设计错误来改。

### 2) EMA 线已经连续补到 deployment 规格的后半段

最近连续产出链条已经是：
- `runbook`
- `day-0 kickoff checklist / ledger template`
- `day-0 launch seed rows`
- `first weekly review scorecard`
- `secondary backstop recheck queue`

这说明 EMA 现在最缺的，不再是“再多一张规范表”，而是**把这些规范真落成前瞻账本的第一份记录**。

### 3) breakout 线这轮新增的是 freeze sync，不是新 overturn evidence

- `2026-03-15_1444_breakout-freeze-sync.md` 做的事情是把当前样本的 freeze verdict 再同步到 TODO / closure / plans；
- 这本身是合理的收口，但也说明 breakout 当前没有新的 `pure-test / down-tail` forward 证据；
- 因此 breakout 当前最诚实的位置仍然是：
  - `one_more_gate`
  - `up-flat biased conditional alpha`
  - same-sample slicing 已冻结，等新的 shadow / holdout 命中再说

## 本轮最小必要干预

### 只做 1 个小调整：重排 TODO，把 EMA 从“继续写 spec”推到“开始记账”

已在 `docs/TODO.md` 新增并置顶 deployment-facing 下一步：

- `EMA：按 day-0 launch seed rows 真正启动首个 0 真资金 shadow / paper ledger snapshot（不要再继续新增近义 spec 页）`

这条调整的目的很明确：
- 不改 admission 排序；
- 不改 cron；
- 不改 closure board 主口径；
- 只是在 bot3 连续几轮已经补足 enough runbook scaffolding 后，给出一个**更高杠杆、更接近 Step 4** 的下一步。

## 为什么这轮要动，而不是继续“观察”

因为当前已经满足 prompt 里的典型触发条件：
- 同一条主线（EMA）连续多轮主要在补 `protocol / board / queue / review`；
- 这些动作虽然不是纯废话，但已经开始接近近义 deployment scaffolding；
- 如果 bot2 这轮还只说“继续 EMA”，很容易让 bot3 再写一轮差不多的 spec 页。

所以这轮最有杠杆的小干预，就是把下一步从“继续设计如何运行”改成“真的留下第一份 forward ledger 记录”。

## 下一步优先级 Top 1~3

### Top 1. EMA：启动首个 `0` 真资金 shadow/paper ledger snapshot

这是当前最值得推进的动作。目标不是再写规范，而是：
- 把 11 条 seed rows 真落到账本里；
- 留下一份首个 day-0 / day-1 snapshot；
- 让 `monitor_status / review_action / data_health` 首次进入真实前瞻记录。

### Top 2. breakout：保持 freeze verdict，不再回到 same-sample micro-slicing

除非拿到新的 `pure-test / down-tail` forward/shadow 证据，否则当前不值得继续在同一段历史里切片。

### Top 3. bot3：继续保持 13m，不改节奏，只观察是否稳定

当前没有证据支持改 cron；如果再出问题，也应优先先看 quota / token 负担，而不是先改调度。

## 本轮改动

- 已编辑 `docs/TODO.md`
  - 新增 EMA 下一步真实动作：`start first shadow/paper ledger snapshot`
- 本轮不改：
  - `alpha_closure_board` 主排序
  - `bot3 / bot2 / bot7` cron 频率
  - breakout 项目级 verdict

## 网页 / 表达建议

- 这轮不需要再改 closure board 主文案。
- 下一次真正值得改网页，是当 EMA 真的开始 shadow/paper 记账后，把：
  - `day-0 started`
  - `first snapshot recorded`
  - `week-1 review pending`
  这种运行态回写到入口页，而不是继续补解释页。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改

原因：
- 当前偏差不是节奏不对，而是**下一步动作类型**需要从 spec/queue 切到 actual shadow ledger。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺 gate：不再是 `paper spec / monitoring spec`，而是**首个真实 shadow ledger snapshot**
- **needs one more gate：support_breakout_v0**
  - 当前最缺 gate：新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. EMA 即使开始记账，也仍只是进入 Step 4 的开始，不等于已经通过 paper admission。
2. 若 bot3 下一轮继续忽略新 TODO 而回去写近义 spec，后续可能要再做 prompt-level steering。
3. breakout 若突然出现新的 forward 命中，这轮“冻结 same-sample slicing”的态度需要重新放松。

## 本轮一句话结论（给 Jerry）

**当前最该继续的不是再给 EMA 补一张说明书，而是让它真的开始留下第一份 shadow/paper 前瞻账本；所以这轮我只做了一个小而关键的 TODO 重排，把 bot3 从“继续写 spec”往“开始记账”推了一步。**
