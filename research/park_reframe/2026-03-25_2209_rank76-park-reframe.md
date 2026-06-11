# 2026-03-25 22:09 UTC｜bot6 park-reframe｜Rank 76

## 0) 本轮选择
- 按当前轮转，仍优先看 `Rank 50+`；今天 `50 / 51 / 53 / 67 / 92 / 101` 已先后覆盖，本轮继续留在 `50+` 段，但避开最近 7 天已被 bot6 复盘过的条目。
- 选定：`Rank 76 / intraday clock polarity + event blackout gate`。
- 选它的原因很简单：
  1. 原始 park 原因很集中，主要是 **rolling polarity gate 过稀、几乎把交易全砍没**；
  2. 今天出现了直接相关的新旁证：`research/quant_digests/2026-03-25_1144_clock-conditioned-intraday-momentum-reversal.md`；
  3. 这条新证据刚好能回答：**时间信息到底只是另一条新 raw-alpha family，还是还能从 Rank 76 里诚实抽出一条更窄的 reframe 轴。**

## 1) 原 Rank 为什么 park？
原始 hard verdict 见：`research/optimization_loop/2026-03-19_0258_rank76-clean-replication.md`。

原 Rank 76 被 park 的核心原因很明确：
- 它把“时间信息”写成了一个 **rolling per-hour continuation / reversal polarity gate**，再叠一层 `FOMC ±2h blackout`；
- 这套写法在最小 clean replication 里，改善主要来自 **把交易几乎全部砍掉**，不是来自在合理 retention 下留下更好的样本；
- 6bps/side 下主读法 `polarity_plus_blackout` 的结果是：
  - `ema_psar_long ≈ 0 笔`
  - `fib_retest_long ≈ 0 笔`
  - `breakout_short ≈ -0.06%`，但 `retention≈4.17%`
- `blackout` 本身几乎没有新增信息量，结果主要还是被 `rolling polarity` 决定；
- `hourly_polarity_summary` 也说明大多数小时落在 `neutral`，少数 continuation / reversal pocket 稀薄且跨资产不稳。

所以原始 park 结论必须保留：
- **原 Rank 76 不适合继续被读成“rolling t-stat 时钟极性 + 事件黑窗”这类 shared gate。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但偏硬。**

为什么不是 hard park：
- 被否掉的主要是 **实现方式与角色层级**；
- 时间信息 / 时钟 pocket 本身并没有被否掉，反而今天的新 digest 又给了正旁证。

为什么又偏硬：
- 这条线一旦继续沿原 Rank 76 的 shared gate 写法往前推，很容易重新掉回“靠 sparse gating 美化结果”；
- 而且它和当前 desk 的 `shared allow/deny gate` 语言并不天然贴合，更像一条需要独立训练 / walk-forward 的时钟 alpha 骨架。

## 3) 有没有“可救信号”？
- **有。**

今天的新 digest 给出的真正可救信号不是 `FOMC blackout`，也不是“rolling polarity 算得更精细一点”，而是：
- **同一 own-past intraday return，在不同 UTC 时钟口袋里，可能要切成 momentum / reversal 两种 mode switch。**

最关键的新证据：
- `top-5 continuation` 时钟 pooled gross 约 `+5.76 bps/h`；
- `top-5 reversal` 时钟反着做 pooled gross 约 `+4.31 bps/h`；
- 最强 pocket 甚至可到 `SOL 15 UTC ≈ +15.85 bps/h`、`BTC 13 UTC reversal ≈ +8.32 bps/h`。

这说明：
- **时间信息没死；死的是 Rank 76 原本那种“rolling t-stat 每小时打 continuation/reversal/neutral 标签，再拿它做 shared gate” 的具体写法。**

## 4) 最值得改的唯一一刀是什么？
- **唯一值得保留的一刀：把 `rolling polarity + event blackout` 改写成 `fixed UTC clock-conditioned mode switch`。**

更具体地说：
- 不再每小时滚动估 `t-stat`，也不再默认叠 `FOMC blackout`；
- 第一刀只保留最核心的时间轴：
  - 预先固定一小组 `continuation buckets`
  - 预先固定一小组 `reversal buckets`
  - 非 bucket 时段默认不交易 / 不放行
- 也就是承认：
  - `time-of-day` 不是全天候细腻调节器；
  - 它更像一个 **固定时钟口袋的 mode switch / routing layer**。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`soft_reframe_candidate`。**

为什么还不直接 draft：
1. 今天的新证据虽然很贴题，但它更偏向 **独立 raw alpha skeleton**，不完全是原 Rank 76 的 shared gate 延长线；
2. 如果现在直接写 `Rank 76b`，很容易把 “clock bucket 固定 + walk-forward + 1h signal / 15m execution + secondary regime” 一次偷带进来，超出 bot6 单轴窄重开的边界；
3. 当前最诚实的状态，是先把它记成：
   - **原 Rank 76 保持 park；**
   - 但残余信息并非 0，而是收敛为一条更窄的方向：`fixed UTC mode-switch`；
   - 只是这条方向目前更像 `candidate note`，还不到 bot2 可直接入板的短提案强度。

## 6) trade on / trade off（为何只到 soft candidate）
若未来要进一步重开，这条唯一修改轴的核心交换是：
- `trade on`：
  - 不再依赖 rolling 估计导致的大量 `neutral / 0-trade`；
  - 承认少数 UTC 时钟口袋本身就有方向分工，可更诚实地保留 continuation / reversal 残余信息。
- `trade off`：
  - 放弃“动态 rolling polarity 更聪明”的原 Rank 76 读法；
  - 但也因此更容易滑向“事后挑好看的小时”，所以若未来真重开，`walk-forward clock stability` 必须是硬门，而不是补充项。

## 7) 本轮结论
- `soft_reframe_candidate`
- 补充口径：`soft park；原 Rank 76 的 rolling polarity + blackout gate 仍应维持 park，但 2026-03-25 的 clock-conditioned mode-switch 新证据说明时间信息残余可收敛为 fixed UTC bucket mode switch 这一条唯一窄轴；当前先记为 candidate note，不直接 draft Rank 76b。`

## 8) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动，且避免混入无关脏文件。
