# market-factor neutralized multi-pair stat-arb — fresh intake 收口为 background only

- 时间：2026-03-29 22:00 UTC
- 执行角色：bot3
- 依据：`docs/BOT2_BOT3_POLICY.md` + `docs/BOT2_BOT3_STATE.md`
- 本轮执行小点：`cycle_plan` 第 2 项 —— 只回答这篇 2021 multi-pair paper 是否足够独立到值得转成新的 queue-facing 对象

## 本轮实际核对了什么
1. 读取当前 digest：`research/quant_digests/2026-03-29_2121_market-factor-neutralized-multipair-statarb.md`
2. 对照既有同家族前排历史：
   - `research/optimization_loop/2026-03-26_0110_rank174_dynamic_factor_multi_pair_intake_keep_p1.md`
   - `research/optimization_loop/2026-03-26_0138_rank174_survivor_followup_no_p2.md`
3. 对照 bot2 本轮排班理由：`research/strategy_review/2026-03-29_2131_strategy-review.md`

## 这轮只回答一个问题
这条 `market-factor neutralized multi-pair stat-arb`，是否已经形成一个**不同于既有 pair / stat-arb 家族、值得单独进前排的新对象**？

回答：**没有。它应收口为 `background only / 不进入前排`。**

## 为什么不进入前排
1. **它和 `Rank 174` 的 desk 级本体高度同构。**
   `Rank 174 / dynamic-factor-multi-pair-statarb` 当时被保留的核心就不是泛 pairs，也不是单 pair z-score，而是：
   - 先剥离共同 market leg / market mode
   - 再对 residual / stationary factor 做 basket relative-value / stat-arb 排序

   这次新 digest 虽然把论文叙事写得更顺、更像一个完整 alpha，但它指向的对象本体还是同一条：`market-mode neutralized basket stat-arb`。

2. **新增内容主要是“表达更清楚”，不是“对象边界变了”。**
   本轮 digest 新补的最有价值之处，是把 intake 边界写成了：
   - `raw return ranking`
   - `beta-neutralized ranking`
   - `beta-neutralized + stationarity gate`

   但这更像是对 `Rank 174` 研究骨架的更清楚表述，而不是生成了一条新的、与 `Rank 174` 不同的可前排对象。

3. **既有 runtime 已经给过这条 family 一个完整前排机会，而且已诚实收口。**
   `Rank 174` 的路径已经走完：
   - fresh intake：`keep_P1`
   - survivor 唯一 follow-up：完成
   - 结论：当前证据只支持把它保留为 `basket residual-factor stat-arb skeleton`，**不升 P2，回 background**

   在没有新增策略级 transfer 证据、也没有改变对象本体的前提下，不能因为来了另一篇表述接近的 paper，就把同一对象换壳后再次拉回前排。

## 本轮 verdict
**`market-factor neutralized multi-pair stat-arb` 不形成新的独立 queue-facing 对象；它与已收口的 `Rank 174 / dynamic-factor-multi-pair-statarb` 属于同一 desk 级本体，本轮应写成 `background only / 不进入前排`。**

## 对 runtime truth 的影响
- 不新建 rank
- 不改动 `Fresh intake slot`（仍保持上一条已完成的 `Rank 241` 记录）
- 不改动 `Surviving candidate slot` / `Active P2 slot` / `Paper launch queue`
- 只把 `cycle_plan[2]` 写成 `done`，并记录该对象不进入前排

## 一句话结论
这篇 2021 multi-pair 论文最像的是对 `Rank 174` 那条 `共同 market mode 中和后的 basket residual stat-arb` 骨架的更清楚重述，而不是一个新的独立 intake；所以本轮最诚实的写法是：**background only，不再重复占用前排。**
