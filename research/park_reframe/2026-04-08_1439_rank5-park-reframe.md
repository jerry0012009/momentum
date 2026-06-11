# 2026-04-08 14:39 UTC｜bot6 park-reframe｜Rank 5

## 0) 本轮选择（为什么是 Rank 5）
- 按当前轮转，`50+` 与 `80~110` 最近已连续覆盖；本轮回到 `1~24` 段。
- `Rank 5` 属于已 `park` 的 `Rank 1~37`，且上次 bot6 正式复盘是 `2026-03-23 19:41 UTC`，已超过 7 天。
- 本轮只回答：在既有 `Rank 5b` 之外，最近新证据是否足以再派生一条新的窄 reframe hypothesis。

## 1) 原 Rank 为什么 park？
原始审计结论来自 `research/optimization_loop/2026-03-16_2149_intraday-tsmom-session-park.md`，核心问题不是“session clock 完全没信息”，而是 **原 Rank 5 把 session 前段收益硬写成了尾段直接跟单**，结果在诚实口径下不成立：
- 方向：`net_return_bps = -6528.34`
- 成本后：`cost_survival_floor = fail`，`0/4` 个成本档为正
- 交易数不是问题：`mean_trades ≈ 145`，不是靠样本太稀才失败
- 时间桶也没有留下可接受的稳定 pocket：`20bps_watch = -48.55%`
- 分资产没有留下可独立认领的 clean pocket

所以原 verdict 必须继续保留：**direct session-tail intraday TSMOM 不成立。**

## 2) 它更像 hard park 还是 soft park？
**仍然更像 soft park，但对“原版 direct tail-trade 读法”已经很接近 hard park。**

原因：
- 软的部分在于：`session-aware / open-impulse` 主题本身没有被彻底杀死；
- 硬的部分在于：原 Rank 5 的主语——“前段动了，尾段直接跟”——已经被原审计、外部 probe、后续复盘反复否掉。

## 3) 现有证据里有没有“可救信号”？
有，但**可救信号仍然停留在既有 `Rank 5b` 和更上位的新 family 之间，没有收敛成新的 `Rank 5c`。**

### 已有可救信号（旧）
- `2026-03-19` 的 park-reframe 已经把唯一诚实残余收敛成 `Rank 5b`：
  - 不再直接交易 session 尾段；
  - 只把 `first-30m impulse quality` 降级成 shared continuation gate / sizing layer。

### 新增旁证（本轮重看）
- `2026-03-23` 的 double-clock 旁证已经说明：session clock 如果要重开，更像一条 **open-impulse momentum + pre-close reversal** 的完整双腿 raw-alpha family，而不是 `Rank 5` 本体的窄修改轴。
- `2026-04-08` 新增的 digest 又进一步把主题往“更独立的时钟型 raw alpha”外推：
  - `same-clock after-hours loser-bounce × regular-hours winner-follow`
  - `rest-of-window impulse × close-pocket continuation`

这些新证据的共同点是：
- 都说明“时钟/时段信息还活着”；
- 但它们的主语已经变成 **独立的 session router / close-pocket / same-clock raw alpha**；
- 而不是原 Rank 5 还能再切出一刀、继续挂在 `park residual` 名下。

## 4) 最值得改的唯一一刀是什么？
**唯一还诚实的一刀，仍然是既有 `Rank 5b`，没有变化。**

即：
- 把 `direct session-tail intraday TSMOM entry`
- 降级成
- `first-30m impulse-quality shared continuation gate / sizing layer`

本轮没有看到比这更窄、且仍能合法挂在 `Rank 5 residual` 名下的单一修改轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因很简单：
1. 原 Rank 5 的 direct tail-trade 已被审计清楚，不能翻案；
2. `Rank 5b` 已经吃掉了它唯一自然、最诚实的 residual；
3. 最近新证据继续抬升的是更上位的 session-clock raw-alpha family，而不是新的窄 `Rank 5c`；
4. 如果现在再硬起草 `5c`，很容易变成“借新 family 的故事，回头替旧 rank 续命”，这不诚实。

## 6) trade on / trade off（仅保留 queue-level 判断）
- **trade on**：保留一个很克制的判断——时钟信息没死，且在 `open impulse`、`close pocket`、`same-clock router` 这类更独立的 raw-alpha 主语里仍然值得追。
- **trade off**：但这已经明显超出 `Rank 5 residual` 的边界；继续从 Rank 5 身上挤新的 reframe，只会把“旧 residual”和“新 family intake”混在一起。

## 7) 本轮结论（authoritative）
- verdict: `keep_park`
- original_rank_verdict_kept: `park`
- park_type_read: `soft park`（但对原版 direct tail-trade 读法已接近 hard）
- rescue_signal_exists: `yes`
- rescue_signal_read: `仍只到既有 Rank 5b；更新证据更像把主题外推到新的 session-clock raw-alpha family`
- single_best_modification_axis: `unchanged; keep Rank 5b only`
- derived_hypothesis_needed_now: `no`

## 8) 文件与提交流水
- 已更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
- 默认不改：`docs/TODO.md`
- 本轮未做 git commit：仓库当前存在无关脏文件 / 未跟踪文件，按最小改动原则跳过，避免混提。
