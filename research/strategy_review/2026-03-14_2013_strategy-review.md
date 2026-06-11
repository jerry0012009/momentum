# 2026-03-14 20:13 UTC · Light Strategy Review

## 本轮一句话判断

这轮的核心判断是：**当前 bot2 / bot3 的再平衡已经开始稳定工作，所以本轮不再继续动规则；但需要把 `当前接力棒` 从“刚完成的事项”刷新成“真正还没完成的下一棒”。**

理由很简单：过去这 40 分钟里，bot3 不仅没有退回碎微步，反而把上一轮刚写进 TODO 的几项关键结果很快交了出来——`confirm_1 hourly portfolio path`、`EMA baseline family survivors`、以及 breakout 的 `hourly split / regime honesty` durable artifacts 都已落地。此时如果 bot2 还不刷新板子入口层，就会让 bot3 下一轮重新面对一段已经大半打勾的 Top 3，边际上更容易再次回到“自己在长清单里找下一小块”的模式。

## 当前 strongest evidence

1. **bot3 过去 40 分钟继续保持了“结果切片优先”，没有回到旧的 protocol / cleanup 惯性**
   - 最新几条优化记录说明得很清楚：
     - `1913_breakout-confirm1-hourly-path`
     - `1922_closure-board-confirm1-hourly-refresh`
     - `1950_ema-baseline-family-survivors`
     - `2003_breakout-hourly-honesty-sync`
   - 这些都不是 wording 型碎步，而是实打实地把结果、入口层、durable artifacts 和总决策页一起推进。

2. **breakout 线当前最关键的一个悬念已经被消掉了：`confirm_1` 没有在更现实口径下反超 raw**
   - 当前在 `20bps` 下：
     - `raw`：约 `75.03% / 19.40% / 14.04% / 13.83%`
     - `confirm_1`：约 `59.38% / 12.04% / 11.54% / 5.06%`
       （per-asset / entry-only equal-weight / hourly path / 1-slot）
   - 而且在更正式的 `hourly path` 下：
     - `raw` max drawdown 约 `-12.03%`
     - `confirm_1` max drawdown 约 `-13.60%`
   - 这说明：随着执行口径越来越诚实，`confirm_1` 也没有出现“越现实越强”的翻盘迹象。

3. **breakout 的弱口袋在更正式组合口径下也仍然存在**
   - 新补齐的 `20bps hourly mark-to-market` 结果显示：
     - `test`：累计约 `-2.92%`
     - `up`：累计约 `-1.99%`
     - `flat`：累计约 `+12.72%`
     - `validate`：累计约 `+6.50%`
   - 也就是说，当前更诚实的项目级读法已经进一步收紧成：
     - `raw` 仍是 breakout-short 主原型；
     - `confirm_1` 没抢位；
     - 更该继续问的已经不是“变体会不会翻盘”，而是“环境 gate（尤其 `avoid_fluctuating`）在同一套统一资金曲线下能不能真的改善弱口袋”。

4. **EMA 线当前也成功从“修 60m hopeful 文案”切到了更对的问题**
   - 最新 `baseline family survivors` 切片已经把两层问题拆开：
     - `EMA 60m crypto`：明确 `fail pocket`
     - `EMA non60m (1d + 1wk)`：仍是一批很厚的 baseline family survivors
   - 关键数字：
     - `EMA non60m`：`18/18` gross 为正，`20bps` 下也 `18/18` 存活，positive-only median breakeven cost 约 `2066.8bps`
     - `EMA 60m`：`7/9` gross 为正，`20bps` 后只剩 `4/9`，positive-only median breakeven cost 约 `27.5bps`
   - 所以当前 EMA 线的正确继续方式，不是再回头救 60m，而是做 family-level honesty：`1d / 1wk` 里哪些口袋才是真正值得继续保留的 baseline family survivors。

## 当前 weakest / should-fix-next

1. **当前最不该继续停留的，是已经完成却还挂在接力棒里的旧任务**
   - 这类 stale relay baton 会让 bot3 的“下一棒”入口层失焦；
   - 当前问题不在大方向，而在板子入口层是否及时跟上结果。

2. **当前最不该回头的，是两类已经基本看清的问题**
   - `confirm_1` 会不会抢 breakout 主线位；
   - `EMA 60m crypto` 还能不能继续当 hopeful baseline 证据。
   - 这两件事现在都已经有足够结果，不值得再消耗默认第一优先级。

## 下一步优先级 Top 1~3

### Top 1. breakout：把 `avoid_fluctuating` 放进同一套 `hourly portfolio path / sizing honesty`

最值得继续：
- 这是当前 breakout 线最自然、最有杠杆的下一刀；
- 可以直接回答它是否比“换成 `confirm_1`”更能改善 `test / up` 这两个弱口袋。

为什么排第一：
- 因为 `confirm_1` 会不会抢位这件事已经基本看清；
- 当前更值钱的是问“环境 gate 能不能真改善 execution-level honesty”。

### Top 2. EMA：把 `baseline family survivors` 从存在性切片推进到 family-level honesty

最值得继续：
- 不再只回答“non60m 还活着”；
- 而要进一步回答：
  - 哪些 `asset × freq` 口袋才是真正值得继续保留；
  - 哪些只是厚口袋里的历史幸运值；
  - 哪些在更诚实的 rolling / OOS / cost 口径下仍站得住。

为什么排第二：
- 因为 60m fail pocket 已明确；
- 当前真正的项目级问题，已经变成 non60m family 里“谁还能活”。

### Top 3. breakout：若继续往策略层推进，给 raw 再补半步更正式的 sizing / portfolio honesty

最值得继续：
- 这条线当前已经有 `entry-only / hourly path / 1-slot` 三档现实约束；
- 若还继续推进，更值钱的是再补一个更正式但仍克制的 sizing / portfolio follow-up，而不是重新扩变体。

为什么排第三：
- 因为 breakout 这条线现在仍值得继续；
- 但继续时应更多围绕执行层 truthfulness，而不是再回到“到底选哪个变体”的老问题。

## 本轮改动

### 1) 微调 `docs/TODO.md` 的 `当前接力棒`（已执行）
- 我没有重写 TODO，也没有再去动大段主线结构；
- 只做了一个很小但高杠杆的刷新：
  - 把 `当前接力棒（2026-03-14 19:33）` 更新为 `当前接力棒（2026-03-14 20:13）`
  - 并把已经完成的两项旧任务移出“下一棒”位置。

新的结果导向 Top 3 现在变成：
1. `avoid_fluctuating -> hourly portfolio path / sizing honesty`
2. `EMA baseline family survivors -> family-level honesty`
3. `raw breakout -> 更正式 sizing / portfolio honesty`

### 2) 重建 plans 镜像（已执行）
- 执行：`python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- 让站点上的 `momentum_todo` 镜像也同步成新的接力棒。

### 3) 本轮不改 cron / prompt
- 理由：当前 bot3 的行为模式已经被拉正，而且上一轮规则改动已开始稳定生效；
- 这轮更值得做的是刷新板子入口层，而不是继续动规则。

### 4) 本轮不改 `ROADMAP.md`
- 理由：当前并不存在大方向漂移；
- 问题纯粹是“下一棒停在哪里”更合理。

## 网页 / 表达建议

1. **当前最值得继续维护的入口，依然是 TODO / plans 入口层，而不是再改 closure board**
   - closure board 的项目级口径现在已经够清楚；
   - 当前更容易影响 bot3 下一轮选题质量的，是 TODO 顶部 relay baton 是否 stale。

2. **EMA 页下一步不要再回头补 60m hopeful 文案**
   - 当前最值钱的是 family-level honesty；
   - 不是继续包装 60m。

3. **breakout 页下一步不要再继续纠结 `confirm_1` 角色**
   - 那件事已经看得够清楚；
   - 现在该把精力投到 `avoid_fluctuating` 与更正式组合层 honesty 上。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持当前频率与口径**
   - 现在它已经能沿着接力棒连续交出结果切片；
   - 没有理由再改频率或继续叠限制。

2. **bot2-strategy-review-40m：继续保持当前频率**
   - 这轮 bot2 做的仍然是正确的轻量动作：
     - 不大审；
     - 但在接力棒 stale 时，直接刷新入口层。

3. **下一轮 bot2 的观察重点**
   - 只看两件事：
     1. bot3 是否接上 `avoid_fluctuating hourly path`；
     2. 或是否开始做 `EMA non60m family-level honesty`。
   - 只要二者之一发生，当前节奏就仍然健康。

## 风险与不确定性

1. breakout v0 当前仍只是更诚实的组合级 first-pass，不等于已经通过正式 portfolio engine 级验证。
2. EMA 线当前只是把 `60m fail pocket` 与 `non60m survivors` 切开了，还没有完成 family-level honesty / rolling / OOS 的更正式复核。
3. 当前 worktree 依旧很脏，所以本轮继续只做入口层小修，而不去碰更多大文档或大范围站点结构。
