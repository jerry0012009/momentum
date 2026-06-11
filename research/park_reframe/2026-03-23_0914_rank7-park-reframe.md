# 2026-03-23 09:14 UTC · Rank 7 park reframe

## 本轮对象
- `source_rank`: `Rank 7`
- 原题：`adaptive trend signal combination / state-weighted component vote`
- 本轮结论：`derived_hypothesis_drafted`
- 原 `park` verdict：**保留，不推翻**

## 为什么原 Rank 7 会 park
原 Rank 7 被 park，不是因为“趋势组件拼接”这个大方向完全没剩东西，而是因为它作为 **direct blended entry engine** 不够诚实：
- clean replication 里唯一没彻底塌掉的是 `fixed_priority`，但它依赖 `mean_no_trade_ratio≈98.60%` 的极端稀疏度；
- 更像原题本体的 `state_weighted_vote / equal_vote` 在 `6bps/side` 下分别约 `-21.75% / -33.68%`，`positive_asset_ratio=0/3`；
- 随后的 cheap honesty recheck 已把“稍微放松一点 direct-entry 规则是否就能变可交易”这条最自然旧救法消费掉：
  - `EMA+combo` 几乎不改善交易密度；
  - `EMA+retest / EMA+任一门` 虽把 `no_trade_ratio` 压到约 `21.1%`，但 `6~20bps` 下跨资产收益一起转负。

所以原 Rank 7 被 park 的真正原因很集中：**它不适合作为统一的 bar-level 混合投票入场器。**

## 这更像 hard park 还是 soft park
- 结论：**`soft park`**。
- 理由：
  - 作为 direct blended entry，原线已经该停；
  - 但失败更像“角色写错了”，不是变量主题彻底归零；
  - 这也是为什么之前已经形成过 `Rank 7b`：把它降级成 session-level lane allocation overlay。

## 有没有可救信号
有，而且这次的新信号和 `Rank 7b` 不是同一刀。

### 已有可救信号
- 原 `fixed_priority` 至少说明：**不是所有 lane/状态都该同权混跑**。
- `Rank 7b` 已经把这条残余信息改写成 `one-regime-per-session` 的 session 级 allocation overlay。

### 本轮新增可救信号
- `2026-03-23 07:35` 的 `ewmac-breakout-bandpass-not-highest-score-wins` digest 给出新的、更窄的旁证：
  - 在 15m breakout 事件里，`align_score` **中段**优于两端极值；
  - “分数越高越该追”并不成立，极端高分反而更像 late-chase；
  - 更诚实的角色不是 hard-positive gate，而是 **band-pass admission / sizing**。

这对 Rank 7 的启发是：
**原 Rank 7 也许不该继续做“谁票多谁开仓”的 blended vote，而更像一个连续对齐分数；其中段可放行/满仓，极端尾部反而该降仓或 veto。**

## 最值得改的唯一一刀
**唯一主修改轴：把 Rank 7 从 `direct blended entry vote` 改写成 `mid-score band-pass continuous alignment overlay`。**

换成人话：
- 不再让 adaptive combo 自己直接决定这一根 bar 要不要开仓；
- 保留现有 setup（`breakout-short / Fib retest_hold / EMA-PSAR continuation`）负责真正触发；
- 只在 setup 已触发时额外计算最小版 combo-alignment score；
- 第一轮只测三臂：
  1. `baseline`
  2. `mid-score full-pass`（中段放行）
  3. `tail-size-down / tail-veto`（极低分与极高分都降仓或 veto）
- 不偷带 session allocation、新 exit、第二层 regime stack、外部数据或新 trigger。

## 是否值得形成新的 derived hypothesis
- 结论：**值得。**
- 原因：
  - 这条新轴与已存在的 `Rank 7b` 不同；
  - `7b` 解决的是 **session 内 lane allocation**；
  - 本轮新轴解决的是 **组合分数的角色误读**：别把“更强对齐”直接当更该追，而是把它改成 `band-pass continuous positioning`；
  - 新证据是最近新增的，而且正对原 Rank 7 的一个残余问题：原 blended vote 不是只能二元 allow/deny，也许更适合连续分档。

## bot2 可直接判断是否入板的短提案
- `proposed_rank`: `Rank 7c`
- `source_rank`: `Rank 7`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `demote adaptive trend combo from direct blended entry vote to a mid-score band-pass continuous alignment overlay`
- `trade on`: `保留 breakout-short / Fib retest_hold / EMA-PSAR continuation 原始触发；只在 setup 已触发时额外计算最小版 combo alignment score，并先测 baseline vs mid-score full-pass vs tail-size-down/tail-veto。中段分数放行，极低分默认 veto，极高分优先视作 late-chase 风险并 size-down / veto。`
- `trade off`: `放弃“分数越高越该追、组件投票可直接形成统一 entry”的原 Rank 7 读法，换取更诚实的分档 admission / sizing 角色；代价是它不再是独立 alpha，而且若改善只来自大幅砍单，也应快速压回 park。`
- `why now`: `原 Rank 7 的 direct-entry 读法已经被稀疏度与 honesty recheck 审计清楚；而 2026-03-23 的 EWMAC band-pass 新证据又刚好说明“中段优于极端尾部”，为 Rank 7 提供了一条不同于 7b 的单轴角色改写。`
- `suggested initial state`: `source intake / clean replication next`

## 本轮最终判断
- 保留原 `Rank 7 = park / evidence pool` 的审计意义；
- 但新增一个**不同于 7b 的窄派生**：`Rank 7c`；
- 更准确地说：原 Rank 7 不值得复活；值得复活的是它里面那条被收窄为 `band-pass continuous positioning` 的角色层残余信息。

## Git
- 本轮只做最小必要文档更新；未做 commit。
- 原因：工作区可能存在无关脏文件，当前不适合安全地 selective commit。
