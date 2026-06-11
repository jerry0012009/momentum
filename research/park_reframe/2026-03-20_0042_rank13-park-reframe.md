# 2026-03-20 00:42 UTC — Rank 13 park reframe review

- source rank: `Rank 13 / partial-moment asymmetry TSMOM gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `derived_hypothesis_drafted`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 13 被 park，不是因为“方向性不对称风险”这个主题彻底没价值，而是因为它被写成了 **standalone sign-momentum + partial-moment risk gate** 之后，结果太硬、太差：

- `2026-03-17 00:38 UTC` 的 clean replication 里，primary variant `pm_guard_100 @ 6bps/side` 跨资产约为：
  - `mean_total_return ≈ -71.90%`
  - `positive_asset_ratio = 0/3`
  - `mean_max_drawdown ≈ -75.70%`
- 对照基线 `baseline_sign_mom` 约 `-78.35%`，说明它只是“没那么糟”，不是“已经像样”；
- `Light Stability Pack` 四项一起 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数稳定性 `0/5 positive configs`
  - 跨标的稳定性 `0/3 positive assets`
  - 成本稳定性 `0/4 positive cost levels`

所以原 Rank 13 的 authoritative park 应继续保留：**被审计否掉的是“partial-moment asymmetry gate 作为独立 15m crypto sign-momentum rescue line”这层写法。**

## 2) 它更像 hard park 还是 soft park
我把它判成 **soft park**。

原因不是原 verdict 不硬，而是它失败得很集中：
- 失败的是“把 partial-moment / asymmetry 直接绑在 standalone sign-momentum alpha 上”；
- 不等于“方向性上行/下行波动拆分这一类信息永远不能做 shared gate”。

换句话说，**原 Rank 13 更像角色放错了，不像主题已经被彻底判死。**

## 3) 有没有“可救信号”
有，且主要来自最近新增的旁支证据，但它只支持一个更窄的角色：

### 可救信号 A：`RS+ / RS-` 方向性拆分把同主题收敛成了 shared directional veto / sizing gate
`2026-03-19 03:43 UTC` 的 digest《`RS+ / RS-` 非对称拆分，更像 breakout-short / Fib / EMA-PSAR 的方向性 veto + sizing gate》给出的读法，比原 Rank 13 诚实很多：
- 不再问“这层 asymmetry 能不能单独救活 sign-momentum”；
- 改问“最近上行半方差 / 下行半方差的不对称，能不能帮助现有 setup 做方向错配 veto / half-size”。

这和原 Rank 13 用的是同一主题：**都在问‘上涨造成的波动’和‘下跌造成的波动’是不是该被区别对待。**

### 可救信号 B：同主题的新 clean replication 已留下一点可继续观察的 shared-gate 信号
同一旁支后续已经形成 `Rank 81 / RS+/RS- realized-semivariance asymmetry gate`，其 source-intake card 当前结论是：
- `guard-passed / admit_to_clean_replication_queue`
- clean replication 后为 `keep_P1`

这不是“已经证明有效”，但至少说明：**当 asymmetry 主题被降级成 shared overlay，而不是 standalone alpha 时，它不像原 Rank 13 那样一上来就被审计成彻底硬死。**

所以可救信号存在，但只支持“降级职责”这一刀，不支持重开原 Rank 13。

## 4) 最值得改的唯一一刀
**唯一修改轴：把 standalone partial-moment asymmetry TSMOM gate，改写为 `RS+/RS- realized-semivariance` directional veto / sizing overlay。**

只改这一刀，不同时做这些事：
- 不继续让它自己决定 long/short 方向；
- 不偷带新的 entry skeleton；
- 不顺手把 exit / holding period / universe 一起换掉；
- 不把它扩成第二层 multi-score stack。

更直白地说：
- 原 Rank 13：asymmetry 是这条线自己的主引擎；
- 新提案：asymmetry 只负责判断“现有 setup 此刻是不是方向错配、要不要 veto / half-size”。

## 5) 是否值得形成新的 derived hypothesis
**值得。**

原因：
1. 原 `park` 结论已经非常清楚，没必要推翻；
2. 最近新增证据不是“再调 threshold”，而是**把同主题降级到更诚实的 shared overlay 角色**；
3. 修改轴足够单一，bot2 后续可以直接判断要不要把它当 fresh-intake 不足时的 queue-only 候补。

因此本轮结论是：**`derived_hypothesis_drafted`**。

## 6) Derived hypothesis draft（供 bot2 后续判断是否入板）
- proposed_rank: `Rank 13b`
- source_rank: `Rank 13`
- status: `derived_hypothesis_drafted`
- single modification axis: `demote standalone partial-moment asymmetry TSMOM gate into an RS+/RS- realized-semivariance directional veto / sizing overlay`
- trade on:
  - 不再根据 `sign(momentum) + partial-moment guard` 自己直接开仓；
  - 只在现有 `breakout-short / Fib retest_hold / EMA-PSAR continuation` setup 触发时，额外计算最小版 `RS+ / RS-` 非对称分数（第一轮优先用 trailing 5m->15m 聚合窗口）：
    - long setup 若 `RS-` 明显占优，则 `half-size / veto`
    - short setup 若 `RS+` 明显占优，则 `half-size / veto`
    - 双侧都很高时统一视作过热/混乱区，优先 `half-size / veto`
  - 第一轮只测 `baseline vs asymmetry_veto vs asymmetry_halfsize`，不偷带第二层 regime / exit / trigger 变化。
- trade off:
  - 放弃“partial-moment asymmetry 本身就是一条可独立交易 / 可独立 rescue 的 TSMOM 线”的原 Rank 13 读法，换取更诚实的 shared directional risk-layer 角色；
  - 代价是它不再是独立策略，而且若阈值过严，可能只是靠砍交易数美化结果，因此第一轮必须只测 `veto / sizing` 本身，不偷带新 trigger / exit / universe 漂移。
- why now:
  - 原 Rank 13 clean replication 已经把 standalone sign-momentum + partial-moment guard 这条路审计得很清楚：收益、回撤、时间、参数、跨标的、成本六个角度一起偏负；
  - 但 `2026-03-19` 新增的 `RS+/RS- realized-semivariance asymmetry` digest 与后续 `Rank 81` 旁支 clean replication，又把同主题收敛成一条更窄、且没有推翻原 park 的 shared directional overlay 读法；
  - 所以现在值得保留一条 queue-only 的 `Rank 13b`，但默认不直接写回 `TODO`。
- suggested initial state: `source intake / clean replication next`

## 7) 本轮结论
- 原 Rank 13 为什么 park：作为 standalone sign-momentum + asymmetry guard，post-cost 收益与稳定性都被审计成硬负；
- 它更像：`soft park`
- 可救信号：有，但只剩 `RS+/RS-` directional veto / sizing overlay 这一条窄角色线；
- 最值得改的唯一一刀：**降级成 shared directional veto / sizing overlay**；
- 本轮最终结论：`derived_hypothesis_drafted`

## 8) 文件与提交流程说明
- 本轮只更新 `research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md` 与本日志；
- 默认不改 `docs/TODO.md` 顶部排班；
- 本轮未做 git commit：`git status` 显示工作区存在大量与本轮无关的脏文件，当前不适合安全地 selective commit。
