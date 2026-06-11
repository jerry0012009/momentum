# Rank 67 park reframe review

- 时间：2026-03-25 02:55 UTC
- 对象：`Rank 67 / regime-matrix shared-state gate`
- 原始结论：`park / evidence pool`
- 本轮结论：`keep_park`
- 是否保留原 park 审计意义：`是`

## 为什么这次看 Rank 67
- 按 `PARK_REFRAME_QUEUE` 当前规则，优先低频看 `Rank 50+` 的 queue-facing parked 条目。
- 最近 7 天的 `research/park_reframe/INDEX.md` 未见对 `Rank 67` 的复盘记录，符合“优先换别的”原则。
- 这条线主题上靠近环境/状态门控，理论上最容易被误写成“好像还能救”；因此值得单独确认它到底还有没有诚实的一刀。

## 原 rank 为什么 park
基于 `research/optimization_loop/2026-03-18_2130_rank67-regime-matrix-park.md`：
- 原假设是把 `30m` 的 `Trend / Expansion / Compression / Mean Reversion` 四态，作为 `ema_psar_long / fib_retest_long / breakout_short` 三条线的 shared allow/deny gate。
- 最小 clean replication 的结果里，`no_MR` / `trend+exp` 确实让若干 setup “少亏”或对 `fib_retest_long` 有局部改善，但改善的主要来源是**砍样本太狠**：
  - `ema_psar_long` retention 约只剩 `16.2%~21.0%`
  - `fib_retest_long` retention 约 `15.2%`
  - `breakout_short` retention 约 `17.0%~26.1%`
- `fib_retest_long` 是唯一相对干净的改善臂，但不足以支撑“这是一套三条主线共用的 shared state language”。
- `breakout_short` 在 `trend+exp` 下虽然少亏，但 `false-break / false-hold 4bars rate` 反而从 `61.70%` 升到 `72.22%`，说明 continuation 质量并没有被稳定修好。
- `compression_to_expansion_breakout` 在该最小代理口径下几乎没有形成可比样本，说明这条最像“可救独门臂”的路径也没有站住。
- 所以原始 `park` 的含义很明确：**不是 regime 主题完全没信息，而是把它包装成三条线共享的统一硬 gate，不诚实。**

## 它更像 hard park 还是 soft park
**结论：偏 hard 的 soft park。**

原因：
- 说它 `soft`，是因为 regime / environment 主题本身并没有被证伪；它仍有“环境解释力”的残余直觉。
- 说它“偏 hard”，是因为最自然的可救写法——把环境层降级成更窄的 allow/deny——其实已经被更诚实、边界更清楚的近邻提案基本消费：
  - `Rank 25b`：把 30m 4-state regime 加到 `EMA+Donchian breakout` 上，只服务单一 breakout family；
  - `Rank 21b`：把 broader market regime 降级成 low-frequency extremity risk overlay；
  - `Rank 9b`：把 regime-switch stack 改写成 asymmetric veto，而不是三 setup 共用语言；
  - `Rank 19b` / `25c` 等也都在把“环境信息”压回更窄职责层。
- 换句话说，**Rank 67 最自然的 rescue 方向并不是完全不存在，而是已经被更窄、更诚实的候选们分拆吸收了。**

## 有没有可救信号
**有，但很弱，而且不构成新的独立派生理由。**

仅存的“可救信号”主要有两点：
1. `fib_retest_long` 在 `no_MR` / `trend+exp` 下有相对干净改善，说明“上层环境许可”并非纯噪声；
2. 原始 quant digest 里对 4-state regime matrix 的最好读法，本来就不是让它直接决定 entry，而是回答“什么时候该做、什么时候别做”。

但这些信号已经不新了，而且都更适合落到**已有单家族 reframe**里：
- 如果想救 breakout family，`Rank 25b / 25c` 更窄；
- 如果想救 broader regime veto，`Rank 21b / 9b` 更诚实；
- 如果想救 compression -> expansion，这又更像单独 setup family，而不是回头给 `Rank 67` 续命。

因此本轮判断：**可救信号存在，但更像“支持已有派生的背景证据”，不是 Rank 67 自己再长出一个新编号的理由。**

## 最值得改的唯一一刀是什么
如果硬要说唯一还值得保留的一刀，那就是：

**把“shared 4-state gate for three families”降级为“single-family environment allow/deny layer only”。**

但这刀并不值得再以 `Rank 67b` 的形式重写，因为：
- 它本质上已经被 `Rank 25b` 更明确地占位；
- 再起一个 `Rank 67b`，只会和现有 queue 里的 regime / breakout context 候选重复；
- 会稀释原 `Rank 67 = 统一 shared state language` 被 park 的审计结论。

## 是否值得形成新的 derived hypothesis
**不值得。**

原因：
- 原始 blocker 没变：一旦把它写成“三条线共用的 shared gate”，就主要靠大幅砍样本来显得更好；
- 最自然的一刀已被 `Rank 25b / 21b / 9b` 等近邻候选吸收，不存在新的唯一主修改轴；
- 最近也没有新的外部证据把 `4-state regime matrix` 从“环境解释层”升级成“值得重新 queue 的独立窄假设”。

## 本轮最终结论
- `final_status = keep_park`
- `original verdict kept = park`
- 简述：`Rank 67` 仍应保留为一条“统一 shared state language 过宽、过度靠砍样本美化”的审计案例；它留下的残余价值已经被更窄的 `Rank 25b / 21b / 9b` 一类提案消费，当前不诚实再派生 `Rank 67b`。

## 对队列文件的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引。
- `docs/PARK_REFRAME_QUEUE.md`：仅在 `Recently reviewed` 追加一条 `Rank 67 / keep_park` 简记。
- 不改 `docs/TODO.md` 顶部排班。
- 不新增 `derived_hypothesis_drafted` 条目。

## 备注
- git 工作区存在大量与本轮无关的脏文件；本轮仅做 park-reframe 所需最小文本更新，不混提其他变更。