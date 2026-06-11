# 2026-03-15 04:28 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实不是又要改方向，而是：**bot3 在切到 `isolated + no-deliver` 之后，已经重新恢复出真实研究产物**，并且正好把 deployment-facing 接力棒里的 3 个关键项全部推进到了更硬的 `paper trading admission` 口径；因此当前 bot2 不该再继续加 prompt，而应先承认这次修正已经开始生效。

## 当前 strongest evidence

1. **EMA 已从 family boundary 推进到真正可执行的 `paper-trading candidate spec`。**
   - 新记录：`2026-03-15_0413_ema-paper-candidate-spec.md`
   - 当前明确口径：`创业板ETF 1d` = `paper_now_primary`；`美股/crypto 1d+1wk` 与 `贵州茅台 1d+1wk` = `paper_now_secondary`；`沪深300ETF 1d` = `shadow_only`；`60m crypto` + `A股 weekly frontier` = `exclude`。
   - 这说明 EMA 已不只是“最接近 paper”的抽象说法，而是已经有了一版最小 deployment scope。

2. **breakout 已从“接近 shadow paper”推进到更硬的 `shadow-admission queue / one_more_gate` verdict。**
   - 新记录：`2026-03-15_0422_breakout-admission-verdict.md`
   - 当前更诚实口径：这条线不是 `shadow paper now`，而是已进入 `shadow-admission queue`。
   - 当前主缺口也已明确：不是组合层 first-pass honesty，而是默认 `ETH+SOL pair-conditioned halfsize` 的 `late-segment / pure-test transferability`；`down` regime tail 是第二风险。

3. **项目级 admission board 已真正落地。**
   - 当前 closure / TODO 入口已经能直接回答：
     - `EMA = closest to paper`
     - `breakout = needs one more gate`
     - `Fibonacci = park / archive`
   - 这意味着当前方向校准已从抽象意图变成入口层可见事实。

## 当前 weakest / should-park lines

1. `Fibonacci`：继续保持 `park / archive`，不应重新抢主资源。
2. breakout 更窄的 `context-conditioned / pure-test × up` 诊断分支：继续 park。
3. EMA 线上的 `protocol / gate / closure-copy` 小步：继续降级，不应重新覆盖 deployment-facing 任务。

## 本轮观察到的执行层信号

1. **好信号：bot3 已恢复真实产出。**
   - `research/optimization_loop/` 已新增：
     - `2026-03-15_0413_ema-paper-candidate-spec.md`
     - `2026-03-15_0422_breakout-admission-verdict.md`
   - 说明先前把 bot3 从 main 会话改为 `isolated + no-deliver`，并把 prompt 收紧到 deployment-facing 方向，这次已经开始产生效果。

2. **坏信号：最新一轮 bot3 又撞上 `edit exact text` 失败。**
   - 最新 cron run 已出现：
     - `Could not find the exact text ... build_alpha_closure_board_report.py`
   - 这说明当前主要 friction 已经不再是“方向跑偏”或“频道刷提醒”，而更像是：在脏 worktree / 持续演化脚本上，`edit` 型修改过于脆弱。

## 下一步优先级 Top 1~3

### Top 1. 先稳住当前 admission board，不再继续加 steering

当前 bot2 最该做的是承认：
- deployment-facing 方向已开始生效；
- 当前不需要继续改 TODO / bot2 prompt / bot7 prompt。

### Top 2. 若 bot3 再次因 `edit exact text` 失败，下一刀应改“执行手法”，不是再改研究方向

更具体地说：
- 问题更像执行器在脏文件上的精确替换脆弱；
- 不该继续通过增加研究 prompt 去解决。

### Top 3. 研究层继续围绕两个 deployment gates

1. `EMA`：secondary batch / `shadow_only` pockets 的诚实抽查
2. `breakout`：默认 sizing candidate 的迁移性证明

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 bot2 / bot3 / bot7 prompt**

原因：
1. bot3 已经恢复真实产出，说明前一轮的 prompt / wiring 修正已经足够；
2. 最新阻塞点已转移到执行层（`edit exact text` 脆弱），不是方向层；
3. 当前继续叠 prompt，边际价值低于先观察 bot3 是否稳定继续交付。

## 网页 / 表达建议

1. 当前 `alpha_closure_board` 已足够承担 admission 总入口角色；短期不必再频繁改文案。
2. `EMA / PSAR` 页下一步应围绕 `secondary / shadow_only` pockets 的诚实抽查，而不是再扩 family prose。
3. `support_breakout_v0` 页下一步应围绕 `transferability` 与 `down tail`，而不是再开新分支。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 但当前若再出问题，优先排查执行手法 / 文件脏状态，而不是重新改研究 steering。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：secondary batch 的诚实抽查 / monitoring follow-through

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：默认 sizing candidate 的迁移性证明

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. `EMA` 有 candidate spec，不等于已 ready for production；它仍只是最小 paper baseline 候选。
2. breakout 已进入 `shadow-admission queue`，但只要迁移性没压清，就仍不该直接放行。
3. bot3 最新一轮 `edit exact text` 失败说明：当前更大的操作风险已从“方向错”切换成“执行器在脏文件上不稳”。
