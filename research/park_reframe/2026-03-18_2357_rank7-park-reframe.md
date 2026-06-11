# 2026-03-18 23:57 UTC · Rank 7 park reframe review

## Scope
- Source rank: `Rank 7 adaptive trend signal combination / state-weighted component vote`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 7 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_2145_rank4-park-reframe.md`
  - `research/park_reframe/2026-03-18_1725_rank25-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_2221_rank7-clean-replication-park.md`
  - `research/optimization_loop/2026-03-17_0524_rank7-honesty-recheck-park.md`
  - `research/quant_digests/2026-03-18_2354_one-regime-per-session-overlay.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It is a good `bot6` candidate because the original line did not die from a total lack of signal; it died because the only surviving pocket (`fixed_priority`) needed an absurdly high `no_trade_ratio≈98.6%`, while any honest attempt to make it tradable collapsed post-cost.
- A fresh digest now offers a narrower reinterpretation: **stop asking Rank 7 to be a direct blended entry vote, and instead let it choose which existing lane gets the session budget.**

## 1) 原 rank 为什么 park？
Rank 7 被 park，不是因为“EMA / combo / retest 这些部件完全没信息”，而是因为它把这些部件放在一起后，**没有形成一个既能交易、又能过成本与跨资产检查的可执行主策略**。

原 clean replication 关键证据：
- `fixed_priority`：`mean_total_return≈+2.33%`，`positive_asset_ratio=2/3`，但 `mean_no_trade_ratio≈98.60%`
- `state_weighted_vote`：`mean_total_return≈-21.75%`，`positive_asset_ratio=0/3`
- `equal_vote`：`mean_total_return≈-33.68%`，`positive_asset_ratio=0/3`
- 参数稳定性还是硬 fail：`0/5` 邻域配置为正

随后那次唯一允许的 cheap honesty recheck，已经把“再稍微放松一点会不会更可用”这条最自然救法消费掉：
- `EMA+combo` 几乎不改善交易密度；
- `EMA+retest / EMA+任一门` 虽把 `no_trade_ratio` 压到约 `21.1%`，但 `6~20bps` 下跨资产回报全部转负。

更直白地说：
- 原 Rank 7 不是完全没东西；
- 但它**不够诚实地作为 blended entry engine 存活**；
- “继续微调 vote / gate 去救 direct-entry 版本”这条路已经被审计消费掉了。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- `hard park` 的部分在于：作为一个直接下单的 `adaptive trend combo`，这条线已经该停了；
- `soft park` 的部分在于：它失败的核心不是变量全错，而是**角色错了**——把 lane selection / state preference 硬写成了统一 entry vote。

所以更诚实的读法是：
- 原 Rank 7 继续保留 `park`；
- 但它仍留下一个很窄的可救信号：**不同 continuation lane 不该同 session 混跑。**

## 3) 有没有“可救信号”？
**有，但可救信号不在“继续修 blended vote”，而在“把它降级成 session-level allocation overlay”。**

当前可救信号主要有三点：
1. 唯一没彻底崩掉的是 `fixed_priority`，说明某种“按优先级挑 lane”并非纯噪音；
2. 一旦把多个门放松到更可交易的密度，结果就一起转负，说明问题更像**同一段行情里多套时钟互相打架**；
3. 最新 digest 刚好给出一个更诚实的 desk 读法：**one-regime-per-session**，即让 continuation lane 和 retest lane 不要在同一段 session 里同时抢单。

翻成人话：
- 原 Rank 7 把“该选哪种节奏”写成了一个 bar-level 混合投票器；
- 更自然的剩余价值，也许是：**先判这一段 session 更像 continuation 还是 retest，然后只给其中一条 lane 预算。**

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：保留 Rank 7 的“lane preference / priority”核心想法，但把它从 `direct blended entry vote` 改成 `one-regime-per-session shared allocation overlay`。**

也就是：
- 不再让 `adaptive combo` 直接决定这一根 bar 要不要开仓；
- 改成给现有 lane 做 session 级分配：
  - 若前 1 小时更像 `continuation regime`，只放行 `breakout-short / EMA-PSAR follow-up`；
  - 若更像 `retest regime`，只放行 `Fib retest_hold`；
  - 若状态不清楚，则 `no-trade / half-size`。
- 第一轮只允许比较 `baseline vs continuation-only vs retest-only vs one-regime-per-session`；不能顺手偷带新的 entry 细节、exit、或第二层 regime stack。

为什么这是一刀而不是多轴大改：
- 核心问题没变，仍在处理“多套趋势/回踩结构怎么协调”；
- 没扩 universe，没换数据类型；
- 只改了它的**角色层级**：从直接入场投票，降级成 session 级资源分配规则。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 结论完整保留，尤其“direct blended entry 不够诚实”这点不推翻；
- cheap honesty recheck 已经把“再放松一点 direct-entry rules”这条最自然旧救法消费掉了；
- 最新 digest 给出的 reframe 很窄，而且正好对位原 blocker：**别再混成一个 entry 模型，改成 session 级 lane allocation。**

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 7b`
- `source_rank`: `Rank 7`
- `single modification axis`: `demote adaptive trend combo from direct blended entry vote to a one-regime-per-session shared allocation overlay across existing continuation vs retest lanes`
- `trade on`: `不再让 Rank 7 直接触发 bar-level 开仓；而是在每个 Asia / Europe / US session 的前 4 根 15m bar 先判 continuation vs retest，只放行一条主 lane：continuation 时仅允许 breakout-short / EMA-PSAR follow-up，retest 时仅允许 Fib retest_hold；不明确时 no-trade 或 half-size`
- `trade off`: `放弃“多个组件投票后直接形成统一入场引擎”的原 Rank 7 读法，换取更诚实的 session 级预算分配层；代价是它不再是独立 alpha，而且若 regime 定义太松，可能只是靠砍掉冲突单美化结果，因此第一轮必须只测 overlay 本身，不偷带新 entry / exit / 第二层 regime`
- `why now`: `原 Rank 7 clean replication 里唯一存活 pocket 依赖极端稀疏交易，而 honesty recheck 已证明只要把它调到更可交易，6~20bps 下跨资产收益就一起转负，说明 blocker 更像 lane conflict 而非单个部件失灵；最新 one-regime-per-session digest 又刚好提供了一个只改角色、不改主题的窄 reframe`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 7 itself.
It keeps the original `park` intact. The only new move is a narrower role downgrade: **`Rank 7b = stop treating adaptive trend combo as a direct blended entry model; test it only as a one-regime-per-session allocation overlay that decides which existing lane gets the session budget.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
