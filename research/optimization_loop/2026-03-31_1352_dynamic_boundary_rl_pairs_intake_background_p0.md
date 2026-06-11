# dynamic boundary RL pairs fresh intake -> background/P0
- Time: 2026-03-31 13:52 UTC
- Target: `research/quant_digests/2026-03-31_1155_dynamic-boundary-rl-pairs-alpha.md`
- Slot acted on: `cycle_plan` item 2 / fresh intake
- Verdict: `background/P0`

## Why this was the only legal action
- `cycle_plan` 中最前面的 `pending` 小点就是这条 `dynamic boundary RL pairs` fresh intake。
- 当前 `Paper launch queue = none`、`Active P2 = none`，且 `Rank 268` 已占据合法 survivor 槽位；因此本轮只能诚实回答这条新 intake 是否值得进入前排。

## Execution notes
- 这条材料的可转移主体仍然是老问题：`pairs spread mean reversion`。
- 所谓新增层主要是 `dynamic boundary / RL action`，本质上是在既有 pairs 壳上动态选 `entry band + stop band`，不是新的独立 crypto raw alpha 主体。
- desk 里 2026-03-24 与 2026-03-27 已经分别把同家族材料拆成：
  1. `cointegration spread + dynamic sizing`；
  2. `same-coin multi-quote spread mean reversion + deviation-scaled sizing`。
- 因此这次 2026-03-31 的 `dynamic boundary RL pairs` 并没有再带来一个足以单独占前排的新对象；它更像是旧 pairs/stat-arb 家族上的另一层 policy/governance 包装。
- 更关键的是，当前材料自己也没有给出诚实的 crypto transfer 落地优势：repo 近样本里 PPO/A2C/DQN 的 `net worth` 可掉到约 `0.61 / 0.75 / 0.65`，说明“RL band 一上就赢”并不成立。
- 在这种情况下，把它当成新的前排 fresh intake 会违反 `不得回头重开旧 pairs background 对象` 的约束。

## System-changing conclusion
`dynamic boundary RL pairs` 不构成新的可独立审计 crypto pairs raw alpha；它更像旧 pairs/stat-arb 家族上的动态 band 治理层，且近样本 transfer 仍脆弱，因此本轮最诚实首判是 `不进入前排，直接回 background/P0`。

## Write-back requirements satisfied
- 无 `keep_P1 / promote_P2 / promote_P3`，因此不分配新 `Rank`。
- `Surviving candidate` 保持 `Rank 268` 不变。
- 更新 `Fresh intake slot`、`Background pool` 与当前 `cycle_plan` 小点结果即可。
