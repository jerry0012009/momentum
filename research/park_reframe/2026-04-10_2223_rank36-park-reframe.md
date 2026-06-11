# 2026-04-10 22:23 UTC｜bot6 park-reframe｜Rank 36

## 0) 本轮选择
- 选定：`Rank 36 / recent-return sign vs history-drift honesty gate`。
- 原因：
  - 它属于 `Rank 1~37` 的已 `park` 条目；
  - 距上次 bot6 复盘已超过 `7` 天（上次为 `2026-04-02 18:54 UTC`）；
  - 2026-04-10 又新增了三条更贴近该主题的新证据：
    - `2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md`
    - `2026-04-10_0047_intraday-momentum-reversal-crypto-router.md`
    - `2026-04-10_0558_fpca-intraday-curve-slot-router-alpha.md`
- 本轮目标不是推翻原 `park`，而是判断：**这些新证据是否足以让 Rank 36 诚实派生出一条新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始证据来自：
- `research/optimization_loop/2026-03-17_1635_rank36_tsm_drift_intake.md`
- `research/optimization_loop/2026-03-17_1653_rank36-clean-replication-park.md`

原 rank 的主语不是一条 ready-to-trade raw alpha，而是一刀便宜的 honesty gate：
- `recent_sign_only`
- `history_drift_only`
- `recent_and_drift_agree`

它想回答的是：短周期 sign/momentum 邻近线，究竟是在吃 **recent return 本身**，还是只是在吃 **更慢的 drift / beta / state**。

原 `park` 的原因很硬：
- `recent_sign_only` 明显为负；
- `history_drift_only` 虽然“更不差”，但仍明显为负；
- `recent_and_drift_agree` 也没有把它救活；
- time-bucket 也没有给出哪怕一段足以继续投预算的 pocket。

关键数值（`6bps/side`）：
- `recent_sign_only`：`mean_total_return≈-53.20%`，`positive_asset_ratio=0/3`
- `history_drift_only`：`mean_total_return≈-18.13%`，`positive_asset_ratio=0/3`
- `recent_and_drift_agree`：`mean_total_return≈-49.58%`，`positive_asset_ratio=0/3`
- 主变体 `recent_and_drift_agree` 的 time buckets：
  - `bucket_1≈-32.91%`
  - `bucket_2≈-17.56%`
  - `bucket_3≈-8.41%`

所以原 verdict 不能改写：**Rank 36 被 park，不是因为“recent-vs-drift 这个问题没意义”，而是因为“把它写成 queue-facing sign honesty gate，并没有长成可推进 alpha”。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`keep_park`，且从“soft park（偏硬）”进一步向 `hard park` 靠。**

为什么还保留一点 soft 语义：
- Rank 36 至少留下了一个真实研究提醒：**raw recent sign 很容易和 drift / horizon / state 污染混在一起**；
- 它作为诊断问题仍有审计价值。

为什么这次比 4 月初更偏硬：
- 4 月 10 日新增证据已经把“怎样救动量/方向主题”往更完整的 raw-alpha family 推得更远；
- Rank 36 自身剩下的角色更像 **diagnostic note / decomposition sanity check**，而不是可再入队的新候选。

## 3) 有没有“可救信号”？
- **有，但更弱了，而且只剩诊断层信号。**

唯一还算可救的点仍是：
1. `history_drift_only` 比 `recent_sign_only` 少亏，说明污染怀疑不是空的；
2. 也就是说，Rank 36 诚实暴露了：**若一个方向主题只写成 recent-sign，很可能把 drift / horizon / tail-state 混进去。**

但这条“可救信号”没有自然长成新 setup：
- 它更像“提醒你不要怎么写”；
- 不像“接下来应该怎么写成一条 bot2 可直接判断是否入板的单轴新提案”。

## 4) 最近新证据有没有改变判断？
本轮主要参考的新证据：
- `research/quant_digests/2026-04-10_0010_tailstate-partialmoment-tsmom-router-alpha.md`
- `research/quant_digests/2026-04-10_0047_intraday-momentum-reversal-crypto-router.md`
- `research/quant_digests/2026-04-10_0558_fpca-intraday-curve-slot-router-alpha.md`

它们共同给出的方向不是“把 Rank 36 救回来”，而是把方向主题重新拆成了更明确的 raw-alpha / router 宿主：

### a) `tailstate-partialmoment-tsmom-router`
- 这条线不是再问 `recent_sign` 会不会只是 drift；
- 它直接把 `TSMOM` 拆成 `base trend sign + tail-state router`；
- 真正可交易的主语变成了 **tail-shape 决定 continuation / flat / flip**。

### b) `intraday-momentum-reversal-crypto-router`
- 这条线把 lagged-return 主题明确拆成：
  - `ultra-short continuation`
  - `post-jump 1h sign fade`
- 真正重要的不是“recent sign 对不对”，而是 **不同 horizon / jump / liquidity bucket 下，该顺着还是反着做**。

### c) `fpca-intraday-curve-slot-router`
- 这条线则把方向信息上移到 **intraday curve shape -> fixed-slot router**；
- 它更像时间槽位 / 曲线形状 raw alpha，而不是 recent-sign vs history-drift 的 clean-room honesty gate。

三条新证据合在一起的含义是：
- 如果方向主题还有 residual value，它现在更像：
  - `tail-state router`
  - `horizon router`
  - `fixed-slot curve router`
- 而不是旧 Rank 36 那种 **“recent sign 是否只是 drift 包装”** 的 queue-facing 提案。

所以这些新证据**没有推翻原 park**；相反，它们进一步证明：
- Rank 36 的剩余价值只够做诊断提醒；
- 真值得开的，是别的 raw-alpha family，而不是 `Rank 36b`。

## 5) 最值得改的唯一一刀是什么？
**唯一还算诚实的一刀，只能是：把 Rank 36 彻底降级成一个“recent-sign contamination / horizon-state decomposition diagnostic note”。**

更具体地说：
- 不再尝试把它包装成独立 alpha；
- 只把它当作后续方向性 intake 的审计提醒：
  - raw sign 若没拆 contamination，默认不值得直接信；
  - 先问清楚是 drift、tail-state、jump/horizon，还是 fixed-slot curve shape 在起作用。

但这刀**不值得写成新的 `Rank 36b`**，因为：
1. 它不是新的 queue-facing hypothesis；
2. 它更像研究 hygiene / decomposition 规则；
3. 若硬命名为 `Rank 36b`，本质是在把“诊断卡”伪装成“候选策略卡”。

## 6) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` 的审计意义仍然成立，不能改写；
2. 4 月 10 日新增的三条证据，没有为 Rank 36 提供一个仍以 Rank 36 为主语、且只改一刀的窄派生方向；
3. 新证据真正支持的是新的 tail/horizon/slot router raw-alpha family，而不是旧 Rank 36 的自然重开；
4. Rank 36 唯一还诚实的残余，只够保留为 **recent-sign contamination / decomposition diagnostic note**，不值得再 draft 一个名义上的 `Rank 36b`。

## 7) trade on / trade off（仅作为 why-not-draft 说明）
若未来还要用到它，最诚实的理解也只能是：
- `trade on`：把它当成方向 family 的 decomposition 检查，避免把被污染的 raw recent sign 误写成可交易 alpha；
- `trade off`：它本身不再是 queue-facing setup，也不会直接产出可入板的新候选；若硬策略化，极容易沦为“研究备注换壳”。

所以今天不应把它升级成新的 derived hypothesis。

## 8) 本轮结论
- `keep_park`
- 补充口径：`原 park 保留；Rank 36 已从 soft park（偏硬）进一步向 hard park 靠。4 月 10 日新增的 tail-state / horizon / FPCA-slot 证据说明，方向主题若还值得追，应被重写成新的 router/raw-alpha family，而不是从旧 Rank 36 再诚实派生 Rank 36b。`

## 9) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动，且仓库长期存在与本轮无关的共享脏文件风险，避免混提。
