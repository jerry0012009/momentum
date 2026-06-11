# 2026-04-02 18:54 UTC｜bot6 park-reframe｜Rank 36

## 0) 本轮选择
- 选定：`Rank 36 / recent-return sign vs history-drift honesty gate`。
- 原因：
  - 它属于 `Rank 1~37` 的已 `park` 条目；
  - 距上次 bot6 复盘已超过 `7` 天（上次为 `2026-03-24 10:27 UTC`）；
  - 最近新增了多条与 intraday clock / forecast / directional family 相关的新 digest，适合再判断一次：这些新证据到底是在“救 Rank 36”，还是把主题推向一条新的 raw-alpha family。
- 本轮目标不是推翻原 `park`，而是判断：**Rank 36 现在是否值得诚实派生成一条新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始证据来自：
- `research/optimization_loop/2026-03-17_1635_rank36_tsm_drift_intake.md`
- `research/optimization_loop/2026-03-17_1653_rank36-clean-replication-park.md`

原 rank 的主语不是“做一条新的时钟 alpha”，而是一个更便宜的 honesty gate：
- `recent_sign_only`
- `history_drift_only`
- `recent_and_drift_agree`

它想回答的是：某条 short-cycle sign/momentum 邻近线，究竟是在吃 **recent return 本身**，还是只是在吃 **更慢的 drift / beta**。

原 park 的核心原因非常直接：
- `recent_sign_only` 很差；
- `history_drift_only` 虽然“更不差”，但仍明显为负；
- `recent_and_drift_agree` 也没有把这条线救活；
- 三个 time buckets 都没给出可诚实继续投预算的 pocket。

关键原始数值（`6bps/side`）：
- `recent_sign_only`：`mean_total_return≈-53.20%`，`positive_asset_ratio=0/3`
- `history_drift_only`：`mean_total_return≈-18.13%`，`positive_asset_ratio=0/3`
- `recent_and_drift_agree`：`mean_total_return≈-49.58%`，`positive_asset_ratio=0/3`
- 主变体 `recent_and_drift_agree` 的 time buckets：
  - `bucket_1≈-32.91%`
  - `bucket_2≈-17.56%`
  - `bucket_3≈-8.41%`

所以原 verdict 不能改写：**Rank 36 被 park，不是因为“recent vs drift 这个问题没意义”，而是因为“把它写成 queue-facing sign honesty gate，并没有长成可推进 alpha”。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但比 3 月下旬时更偏硬。**

为什么还不是 pure hard park：
- 原 rank 至少留下一个真实信息：**raw recent sign 很容易和更慢的 drift / state 混在一起**；
- 这条“别把 contaminated sign 当 alpha” 的提醒本身没有过时。

为什么又更偏硬：
- 最近新增证据已经把“可交易的方向性主题”推向了更完整的 raw-alpha 家族；
- Rank 36 自身剩下的更像是**诊断层 / honesty check**，不是 queue-facing hypothesis；
- 如果硬写 `Rank 36b`，很容易只是把“解释变量诊断”伪装成“新策略提案”。

## 3) 有没有“可救信号”？
- **有，但很弱，而且更像诊断残余，不像可直接 queue 的重开线。**

还留下来的唯一可救信号大致是：
1. `history_drift_only` 明显比 `recent_sign_only` 少亏，说明“recent return contamination” 这个怀疑不是空的；
2. 也就是说，原 rank 至少诚实暴露了：**方向主题若想活，必须把 raw recent sign 的污染源拆开。**

但这条可救信号的问题在于：
- 它更像“不要怎么写”，
- 而不是“接下来该怎么写成一条新的窄策略”。

翻成人话：
- Rank 36 更像帮我们淘汰了一个坏写法；
- 它没有自然长出一个 bot2 可直接判断是否入板的单轴新提案。

## 4) 最近新证据有没有改变判断？
本轮主要参考的新证据：
- `research/quant_digests/2026-03-23_1828_intraday-double-clock-momentum-reversal-fullstack.md`
- `research/quant_digests/2026-03-24_0840_rolling-fpca-intraday-sign-alpha.md`
- `research/quant_digests/2026-04-01_2045_hour-of-week-xs-marketneutral-alpha.md`

这些新证据共同指向的不是“把 Rank 36 救回来”，而是：
- 真正更值得交易的方向主题，已经变成了**明确主语的 raw alpha**：
  - `double-clock open-impulse momentum + pre-close reversal`
  - `rolling-FPCA sign forecasting`
  - `hour-of-week 条件化 XS scheduler`
- 它们都不是在问“recent sign 会不会只是 drift 包装”；
- 它们是在直接定义新的、可下单的 directional / clock-conditioned raw alpha 家族。

也就是说，最新证据确实改变了主题判断，但改变的方向是：
- **把 Rank 36 的残余价值进一步降级成 diagnostic honesty note**；
- 同时把真正值得做的新东西，上移到别的 raw-alpha family。

所以这些新 digest **没有推翻** 原 `park`，反而进一步说明：
- Rank 36 的 residual value 更像“解释污染 / honest decomposition”；
- 真值得新开的，不是 `Rank 36b`，而是那些主语已经彻底换掉的新 family。

## 5) 最值得改的唯一一刀是什么？
**唯一还算诚实的一刀，只能是：把 Rank 36 从 queue-facing sign honesty gate，降级成“recent-return contamination / drift decomposition diagnostic note”。**

更具体地说：
- 不再试图把它包装成独立 alpha；
- 只把它当作后续 directional family intake 时的审计提醒：
  - raw sign 若没拆 contamination，默认不值得直接信；
  - 先问清楚是 clock edge、forecast edge，还是慢 drift 包装。

但这刀**不值得形成新的 `Rank 36b`**，因为：
1. 它本质上不是新的 queue-facing hypothesis；
2. 它更像研究 hygiene / honesty 规则；
3. 再命名一个 `Rank 36b`，只会把“诊断卡”误写成“候选策略卡”。

## 6) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` 的审计意义仍成立，不能改写；
2. 最近新增证据没有为 Rank 36 提供一个只改一刀、且仍以 Rank 36 为主语的窄派生方向；
3. 新证据真正支持的是别的 clock/forecast raw-alpha family，而不是旧 Rank 36 的自然重开；
4. Rank 36 唯一还诚实的残余，只是“recent sign 容易被 drift/clock/state 污染”的 diagnostic 提醒，不值得再 draft 一个名义上的 `Rank 36b`。

## 7) trade on / trade off（仅作为 why-not-draft 说明）
若未来还要用到它，最诚实的理解仍然只能是：
- `trade on`：把它当成 directional family 的 honesty decomposition 规则，避免把被污染的 raw recent sign 误判成可交易 alpha；
- `trade off`：它不再是 queue-facing setup，本身也不会直接产出可入板的新候选；若硬要把它策略化，极容易沦为“研究备注换壳”。

所以今天不应把它升级成新的 derived hypothesis。

## 8) 本轮结论
- `keep_park`
- 补充口径：`soft park，但更偏硬；最近新增的 double-clock / rolling-FPCA / hour-of-week 证据更像新的 clock-conditioned directional raw-alpha family，Rank 36 自身残余只够保留为 recent-sign contamination / drift-decomposition diagnostic note，不值得再派生 Rank 36b`

## 9) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动，且仓库长期存在与本轮无关的共享脏文件风险，避免混提。
