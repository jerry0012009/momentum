# 2026-04-17 23:03 UTC｜bot6 park-reframe｜Rank 36

## 0) 本轮选择
- 选定：`Rank 36 / recent-return sign vs history-drift honesty gate`
- 轮转说明：近期 `50+`、`80~110`、`1~24` 都已覆盖；本轮按规则回到 `25~49`。
- 选择原因：
  - `Rank 36` 上次 bot6 复盘是 `2026-04-10 22:23 UTC`，本次已跨过 `7` 天窗口；
  - 4 月 12 日与 4 月 14 日又新增了更贴近该主题的旁证，适合复查它是否还能诚实派生出新的窄 reframe。

## 1) 原 rank 为什么 park？
原 `park` verdict 保留。

根据：
- `research/optimization_loop/2026-03-17_1635_rank36_tsm_drift_intake.md`
- `research/optimization_loop/2026-03-17_1653_rank36-clean-replication-park.md`

原 Rank 36 想回答的是一个很便宜的 honesty 问题：
- `recent_sign_only`
- `history_drift_only`
- `recent_and_drift_agree`

它不是一条完整 raw alpha，而是用来检查：
> 15m 上看起来像 own-past momentum 的东西，到底是在吃 recent sign，还是只是在吃更慢的 drift / horizon 污染。

原始 clean replication 给出的结论很硬：
- `recent_sign_only` 明显为负；
- `history_drift_only` 虽“更不差”，但仍明显为负；
- `recent_and_drift_agree` 也没把它救活；
- `time buckets` 三桶都没有给出值得继续投预算的 pocket。

关键数值（`6bps/side`）：
- `recent_sign_only ≈ -53.20%`
- `history_drift_only ≈ -18.13%`
- `recent_and_drift_agree ≈ -49.58%`
- `recent_and_drift_agree` 三个 time buckets 也全负。

所以原 rank 被 park，不是因为“污染拆解问题没意义”，而是因为：
> **把它写成 queue-facing honesty gate，并没有长成独立可推进的交易主语。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`keep_park`，且已从 4 月 10 日那轮的“soft park（偏硬）”进一步收紧到 `hard park with consumed residual`。**

原因：
1. 4 月 11 日 `bot3` 已把它的 fresh-intake 首判收口为 `background / P0 / contamination diagnostic only`；
2. 之后新增证据继续说明，方向主题若还有 residual value，真正值得开的都是新的 raw-alpha / router 宿主；
3. Rank 36 自身剩下的角色只够做“别把污染过的 recent sign 误写成 alpha”的诊断提醒，不再构成可独立执行主语。

## 3) 有没有“可救信号”？
- **有，但只剩诊断层可救信号，不再是可派生的交易主语。**

唯一还成立的信号仍是：
- `history_drift_only` 比 `recent_sign_only` 少亏，说明污染怀疑不是空的；
- 也就是：**raw recent sign 很容易把 drift / path-shape / clock pocket / cross-asset beta 一起混进去。**

但这类信号只是在告诉我们“别怎么写”，没有自然长成“应该怎么单独交易”。

## 4) 最近新证据有没有改变判断？
本轮补读的新证据主要是：
- `2026-04-12_0152_btc-confirmed-alt-tsmom-alpha.md`
- `2026-04-12_0244_predicted-cidr-trough-peak-intraday-alpha.md`
- `2026-04-14_1718_sameclock-xsmomentum-recurring-pocket-alpha.md`
- `2026-04-14_2321_sparsejump-trendreversal-activity-router.md`

它们共同给出的方向，不是“把 Rank 36 救回来”，而是把方向主题继续外流到更清楚的新宿主：

### a) `BTC-confirmed alt TSMOM`
- 把 residual 写成 **cross-asset confirm 的 alt own-trend raw alpha**；
- 主语已经变成 `alt own-trend + BTC confirm`，不再是 `recent sign vs drift honesty gate`。

### b) `predicted CIDR trough -> subsequent peak`
- 把 residual 写成 **next-day intraday path-shape forecast**；
- 真正在交易的是 `predicted trough/peak timing`，不是 recent sign contamination 检查。

### c) `same-clock winners-minus-losers recurring pocket`
- 把 residual 写成 **same-clock cross-sectional recurring-pocket raw alpha**；
- 这里真正有信息的是 `clock pocket + cross-sectional continuation`，不是 Rank 36 的 own-past honesty 主语。

### d) `sparse-jump trend/reversal × activity/attention router`
- 把 residual 写成 **shared regime/router**；
- 真正重要的是 `trend/reversal + activity + attention` 的状态分流，而不是“recent sign 是否被 drift 污染”这一诊断卡。

合在一起看，新增证据进一步说明：
> **Rank 36 的 residual value 只够作为 contamination / decomposition reminder；真正值得开的，是新的 cross-asset / path-shape / same-clock / state-router family。**

## 5) 最值得改的唯一一刀是什么？
**唯一还诚实的一刀，仍然只是：把 Rank 36 彻底降级成“recent-sign contamination / decomposition diagnostic note”。**

也就是：
- 不再尝试把它包装成独立 alpha；
- 只把它当作后续方向性 intake 的审计提醒：
  - recent sign 是否只是 drift 包装；
  - recent sign 是否只是 path-shape / same-clock pocket / cross-asset confirm 的影子；
  - 先拆污染，再决定该进哪个 family。

但这刀**不值得写成 `Rank 36b`**，因为它不是新的 queue-facing hypothesis，而只是研究 hygiene 规则。

## 6) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` 的审计意义没有被推翻；
2. 4 月 12~14 日新增证据没有提供一条仍以 Rank 36 为主语、且只改一刀的诚实窄派生；
3. 新证据真正支持的，是新的 raw-alpha / router family，而不是旧 Rank 36 的自然重开；
4. 若现在硬写 `Rank 36b`，本质是在把“诊断提醒”伪装成“交易候选”。

## 7) 单轮审查模板回答
### 原 rank 为什么 park？
因为 `recent_sign_only / history_drift_only / recent_and_drift_agree` 三档在 `BTC/ETH/SOL 15m` 上都没站住，且 time buckets 全负；它证明了污染问题存在，但没长成可推进 alpha。

### 它更像 hard park 还是 soft park？
现在更像 **`hard park with consumed residual`**。

### 现有证据里是否存在“可救信号”？
有，但只剩诊断层：recent sign 很容易混入 drift / path-shape / clock pocket / cross-asset beta。

### 最值得改的唯一一刀是什么？
把它彻底降级成 `contamination / decomposition diagnostic note`。

### 是否值得形成新的 derived hypothesis？
**不值得。**

## 8) 本轮结论
- `keep_park`
- 补充口径：`原 park 保留；Rank 36 已从 4 月 10 日那轮的 soft park（偏硬）进一步收紧到 hard park with consumed residual。4 月 12~14 日新增的 BTC-confirmed alt TSMOM / predicted CIDR trough→peak / same-clock XS momentum recurring pocket / sparse-jump trend-reversal router 证据继续说明：方向主题若还有信息，应被重写成新的 cross-asset / path-shape / same-clock / state-router family，而不是从旧 Rank 36 再诚实派生 Rank 36b。`

## 9) 文件动作
- 新增：本轮日志
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## 10) commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动，避免混入无关脏文件。
