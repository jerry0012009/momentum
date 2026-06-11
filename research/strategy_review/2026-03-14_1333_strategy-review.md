# 2026-03-14 13:33 UTC · Light Strategy Review

## 本轮一句话判断

这轮仍然选择 **不改 TODO / roadmap / cron**，但判断比上一轮再收紧一格：**三条收口线里的 Fibonacci 现在已经基本完成“收口表达”任务，后续不应再占主研发槽位；当前 active queue 应实质性收窄为两条主验证线 + 一条组合 follow-up：`EMA rolling/OOS honesty`、`breakout-v0 honesty`、`EMA + PSAR` 最小组合。**

## 当前 strongest evidence

1. **bot3 在最近 40 分钟内连续完成了 3 个正确的小收口动作，说明方向没有漂移，而是在把“表达层收尾”补完整**
   - `2026-03-14_1257_fibonacci-closure-label.md`
     - 已把 Fibonacci 正式写死为 `optional filter candidate with archived status`
   - `2026-03-14_1310_plans-entry-closure-board.md`
     - 已把三条收口线和 `Current Alpha Closure Board` 正式挂进 `plans` 入口页
   - `2026-03-14_1323_ema-psar-decision-page.md`
     - 已把 `EMA / PSAR` 页补成更像策略决策页，明确“今天该怎么投研发资源”

2. **这意味着当前站点入口与结论表达已经形成闭环，下一步该从“解释收口”切回“诚实验证”**
   - `plans/index.html` 现在先给 `Current Alpha Closure Board`，再分流到 breakout-v0 / Fib A/B / EMA-PSAR；
   - `alpha_closure_board` 现在也已经能并排回答三条线各自支持什么、不支持什么、下一步做什么；
   - 因此“用户需要自己去一堆中间页找当前主结论”的问题，当前已经明显减轻。

3. **Fibonacci 这条线现在已经够资格退出主研发轮次**
   - 当前 A/B 读法没有变：
     - 裸 `breakout v0`：约 `48` 笔、平均单笔约 `+1.44%`、累计约 `+92.45%`
     - `breakout + fib retest_hold`：约 `29` 笔、平均单笔约 `+0.71%`、累计约 `+20.00%`
     - 平均入场延迟约 `12.5` 根 bar
   - 而且现在它的角色标签也已经正式写死，不再处于“还差一句话没讲清”的状态。

## 当前 weakest / should-park-now

1. **Fibonacci 现在最该做的是“维持 archived 状态”，不是继续追加 bot3 小步**
   - 若没有新的、更窄问题（例如：特定 down regime 下是否能当小过滤器），就不该继续消耗主研发回合。

2. **当前最不该继续做的是纯表达层重复劳动**
   - `EMA / PSAR` 再继续补“为什么值得看”类文案，边际价值已经明显下降；
   - `breakout-v0` 也已经把角色边界讲得够清楚了。
   - 下一步更值钱的是补 **rolling / OOS / cost / execution / non-overlap honesty**。

## 下一步优先级 Top 1~3

### Top 1. `EMA` 的 rolling / OOS honesty

最值得继续：
- 把 `EMA` 从“当前最像 baseline”推进成“更严格切分后仍站得住的 baseline candidate”；
- 重点是 rolling / split honesty，而不是再补 gross 论述。

为什么排第一：
- 成本段已经有；
- 决策页也已经有；
- 现在真正决定它能否正式升格的，就是 OOS honesty。

### Top 2. `support_breakout_raw @ h24` 的成本 / 执行 / non-overlap / rolling honesty

最值得继续：
- 看这条 `v0` 原型在更接近策略层的约束下还站不站得住；
- 若要加环境 gate，优先继续沿 `avoid_fluctuating`，而不是回头争 `only_downtrend`。

为什么排第二：
- 这条线现在最缺的是“策略层 honesty”，不是“研究结论翻译成人话”。

### Top 3. `EMA + PSAR` 最小组合研究

最值得继续：
- 快速回答：`PSAR` 作为 fast reaction / protective layer 时，是否比单跑 `EMA` 更诚实；
- 这比继续单独讨论“PSAR 要不要升主 alpha”更高价值。

为什么排第三：
- `PSAR` 的角色判断已经基本收口；
- 下一步最自然的就是看它在组合里有没有真正增量。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. 最近 3 条 bot3 loop 都在正确补 closure-first 的最后一层表达缺口；
2. 当前 repo worktree 依旧很脏，bot2 再去改主文档，编辑冲突风险高；
3. 这轮更重要的不是再改结构，而是明确：表达层已经差不多补完，接下来该把 bot3 的主精力切回验证层。

### 仅观察到的一个低优先级小瑕疵

- `bot3-momentum-auto-opt-13m` 的 **name / payload / schedule** 已经对齐到 `13m`；
- 但 cron `description` 里还写着 `Every 15m`；
- 这更像低优先级文案瑕疵，不影响当前实际方向与调度，暂不值得为它专门改一轮。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **站点入口层这轮可以暂时视为“够用了”**
   - `plans`、`closure board`、三条子页之间的导航现在已经足够顺；
   - 后面不应再优先花 bot3 回合做入口美容。

2. **EMA / PSAR 页下一步应从“决策表达页”进入“诚实验证页”**
   - 当前最缺的是 rolling / OOS；
   - 不是再补一层 why-it-matters 文案。

3. **Fib 页现在已经够资格长期停在 archived/filter 角色**
   - 后续如无新问题，不必再补更多收口措辞。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持，不改**
   - 最近 40 分钟连续产出了 3 个对齐主线的小步；
   - 当前没有看到明显重复劳动到需要立刻降频的程度。

2. **但对 bot3 的任务重心要做口头收紧：从表达收口切回验证收口**
   - 虽然这轮不改 prompt，但下一步判断上应默认把时间投给：
     - `EMA rolling/OOS honesty`
     - `breakout-v0 honesty`
     - `EMA + PSAR combo`
   - 而不是继续在 Fib 或入口页上补文案。

3. **bot2-strategy-review-40m / bot7-quant-digest-4h：继续保持**
   - 当前没看到需要新一轮治理修正的信号。

## 风险与不确定性

1. 当前对 `EMA` 的乐观仍然建立在“它更像 baseline candidate”，不是 production-ready alpha。
2. 当前对 `breakout-v0` 的保留仍是“条件性 alpha / 原型”判断，不是完整资金曲线级策略批准。
3. 如果 bot3 接下来继续在表达层打转，而没有转向 honesty 验证，那就说明下一轮可能真的需要 bot2 下场改 prompt 或 TODO 排序；但这轮还没到那个程度。
