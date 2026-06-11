# 2026-03-15 21:37 UTC · Light Strategy Review

## 本轮一句话判断

这轮**不改项目级总排序**：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。但这轮确实有一个需要 bot2 出手的小问题：**bot3 最近两轮不再是研究方向漂移，而是 waiting window 里的重复 edit 触发了执行层 error**。因此本轮最小必要干预不是再改研究结论，而是：

1. 确认当前最有价值的新 execution 垫片（`refresh_history / homepage deployment watch / fast-precheck`）都已经落地；
2. 在 `TODO.md` 里补一句更硬的 waiting-window 约束：在下一根真实 completed bar 到来前，若没有新的 `due_now / overdue` lane，也没有新的执行阻塞，就默认 `NO_PROGRESS`，不要再对同一批文件重复打相同 patch；
3. 把当前这些已落地但未收口的 deployment-facing 改动统一提交，避免 bot3 继续卡在“内容已相同 / exact-text mismatch”的重复编辑错误上。

## 本轮先检查了什么

1. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：最近两轮变成 `error`，`consecutiveErrors = 2`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：仍 timeout，但与本轮主线无关
2. bot3 最近 6 条 run records：
   - 最近两轮错误都不是模型额度/调度停摆，而是 `edit` 失败：
     - 一次是 `build_site_index.py` 的 exact-text mismatch
     - 一次是 `run_ema_paper_trading_guarded_refresh.py` 的 identical-content / no changes made
3. 当前脚本 / 站点 / TODO 实际状态：
   - `scripts/run_ema_paper_trading_guarded_refresh.py`
   - `scripts/build_site_index.py`
   - `reports/site/index.html`
   - `docs/TODO.md`
4. guarded refresh 当前实跑结果：
   - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due --show-limit 2`
   - 当前仍没有 `due_now / overdue`，最靠前的 `Crypto 1d+1wk` 约 `2.4h` 后到点

## 当前 strongest evidence

### 1) 当前主线判断并没有变化，变的是 execution 层该不该继续重复 patch

项目级排序仍然很清楚：
- **EMA** 仍是 `closest to paper`
- **breakout** 仍是 `one_more_gate`
- **Fibonacci** 仍是 `archive / park`

EMA 这条线当前真正缺的 gate 也没变：
- 不是 source-risk
- 不是 queue / due-guardrail / guarded-entry
- 而是**下一根真实 completed daily bar 到来后，refresh / week-1 review 的 forward honesty**

也就是说，当前不是“方向没想明白”，而是**在已经进入 waiting window 后，bot3 不该继续围绕同一批 execution 垫片反复 edit。**

### 2) `refresh_history / homepage deployment watch / fast-precheck` 这三块 execution 垫片现在其实都已经在文件里

从当前工作树直接核对，已经可确认：
- `run_ema_paper_trading_guarded_refresh.py`
  - 已具备 append-only `refresh_history` 逻辑
  - 已具备 `--require-due` + `fast-precheck`
- `build_site_index.py`
  - 已具备首页 `Deployment Watch / 当前守门快照`
- `docs/TODO.md`
  - 已记下 `refresh_history / guarded entry / smoke test / fast-precheck`

所以最近两轮 bot3 error 更像：
- 它还在围绕这批文件做“本来想补的小更新”
- 但这些小更新其实已经存在于当前工作树里
- 结果 exact-text edit 自然就失败了

### 3) 当前 guarded refresh 本身是健康的：它会在没到点时主动拒绝伪 refresh

我这轮重新实跑后，当前结果仍是：
- `fast-precheck：所有 lane 的 next_expected_close_utc 仍在未来，跳过本轮 full rebuild`
- 当前没有 `due_now / overdue`
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 距到点约：`2.4 小时`

这再次说明：
- **EMA 当前不是 stale**
- **也不是 bot3 不会守门**
- 现在真正不该发生的，只是“同一类 execution patch 再打一遍，然后因为 identical content 报错”

### 4) breakout / Fibonacci 本轮没有任何新证据足以改写排序

- **breakout**：仍无新的 `pure-test / down-tail` shadow/forward 命中，正式 verdict 继续是 `one_more_gate`
- **Fibonacci**：继续 archive

因此这轮没有任何理由把 bot2 的注意力从 EMA execution hygiene 移开。

## 本轮最小必要干预

### 1) 只补一条很小的 TODO 约束

已在 EMA 那条 open task 下面新增：
- 在下一根真实 completed bar 到来前，若没有新的 `due_now / overdue` lane，且也没有新的执行阻塞（脚本异常 / data loader 故障），本线默认应返回 `NO_PROGRESS`
- 不要再对：
  - `scripts/run_ema_paper_trading_guarded_refresh.py`
  - `scripts/build_site_index.py`
  - 对应首页/计划镜像
  重复做“内容已相同”的 patch

这条约束不是在改研究方向，而是在**把 waiting window 里的 execution 误动作冻结住**。

### 2) 收口提交当前已落地但未提交的 deployment-facing 小改动

本轮会把以下文件统一收口提交：
- `docs/TODO.md`
- `scripts/build_site_index.py`
- `scripts/run_ema_paper_trading_guarded_refresh.py`
- `reports/site/index.html`
- `reports/site/plans/momentum_todo.html`
- 本轮 review 记录

这样做的目的，是把“已经落地的状态”变成 repo 里的正式状态，减少 bot3 下一轮继续对同一块内容做重复 edit 的概率。

## 为什么这轮要动，而不是继续“不改”

因为当前已经从“等待窗口里的文案漂移”变成了更具体的 execution noise：
- 连续 2 轮都不是研究判断错误
- 而是 `edit` 工具在打已经存在的补丁时失败

如果 bot2 这轮还只说“继续等 close”，那就会放任 bot3 在等待窗口里继续因为重复 patch 报错；这会降低后续真正到点时的执行质量。

所以这轮最小而有杠杆的动作，就是：
- **不改总判断**
- **只修 waiting-window 里的重复 edit 噪音**

## 下一步优先级 Top 1~3

### Top 1. EMA：继续等真实 completed bar，到点后先跑 guarded refresh

默认入口仍是：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

真正到点后再回答：
1. `创业板ETF 1d` primary 是否继续守住
2. front-queue secondary 是否需要 `keep / stricter recheck / demote`
3. week-1 review 是否首次出现 `yellow / red`

### Top 2. 若执行层再出错，只修新的执行阻塞，不重复给已落地文件打同样 patch

例如：
- guarded entry 脚本异常
- loader / data source 故障
- 真正新的 build breakage

但不是再对已经存在的 `refresh_history / deployment watch / fast-precheck` 重复 edit。

### Top 3. breakout：继续维持 `one_more_gate`

没有新的 `pure-test / down-tail` 证据前，不 reopen 当前样本 retrospective slicing。

## 本轮改动

- 已编辑 `docs/TODO.md`
  - 新增一条 waiting-window duplicate-edit freeze
- 新增 review 记录：
  - `research/strategy_review/2026-03-15_2137_strategy-review.md`
- 本轮不改：
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率
  - breakout / Fibonacci 项目级 verdict

## 网页 / 表达建议

- 这轮不需要继续改 closure board 主文案。
- 首页 `Deployment Watch` 也已经够用；当前不缺再补一层解释。
- 下一次值得改网页，仍应等：
  - 真实 completed bar 到来后
  - 新一轮 refresh / review 真落下去

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改

原因：
- 当前不是调度节奏问题；
- 当前是 **waiting window 里的重复 edit 噪音**；
- 这轮已经用 TODO 边界 + 收口提交来处理。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 仍然是：
  - **连续 `market-close refresh / week-1 review` 的 forward honesty**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. 当前修掉的是 execution noise，不是新的 alpha blocker。
2. 即使 bot3 恢复回 `ok`，也不代表 EMA 已完成 line-299；它仍在等真实 next close。
3. 若后续 bot3 继续无视这条 freeze，再次围绕同一批文件重复 edit，后面可能要考虑更 prompt-level 的 steering。

## 本轮一句话结论（给 Jerry）

**这轮我没有改研究方向，而是出手修了一个更实际的问题：EMA 这条线当前真正该做的是等真实 close，但 bot3 最近两轮在 waiting window 里重复给同一批 execution 文件打补丁，触发了 edit 错误；所以我补了一条 duplicate-edit freeze，并把当前已落地的小改动统一收口提交。**
