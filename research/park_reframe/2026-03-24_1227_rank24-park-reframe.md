# 2026-03-24 12:27 UTC · Rank 24 park reframe review

## 这轮看谁
- `Rank 24 / trend regime filter / trend-strength-over-noise gate`
- 选择原因：
  - 属于 `Rank 1~37` 已 `park` 条目；
  - 虽然最近 `7` 天内在 `2026-03-20` 已复盘过一次，但今天新增了更贴主题的新证据：`2026-03-24_1030_market-percentile-tsmom-state-alpha.md`；
  - 这份新 digest 不是在重复“regime 只当 filter”，而是在提示：**市场状态分位本身更像一条可独立运行的 raw alpha family**，值得回头确认 `Rank 24` 是否因此出现新的窄 reframe 空间。

## 原 rank 为什么 park
根据 `research/optimization_loop/2026-03-17_0549_rank24-clean-replication-park.md`：
- `baseline_mtf`、`trend_regime_default`、`stricter_trend_threshold`、`stricter_regime_score` 在 `6bps/side` 下全部仍为负；
- 最好的一档 `stricter_trend_threshold` 也只是把亏损收窄到约 `-9.81%`，`positive_asset_ratio` 仍只有 `1/3`；
- 时间桶虽有零散正 pocket，但没有形成可跨资产复制的稳定 pocket；
- 参数邻域没有给出稳定平台；
- 成本从 `10/15/20bps` 往上仍持续恶化。

翻成人话：`Rank 24` 不是完全没信息，而是**只做到“少亏一点”**，远没到“可诚实升格”的程度，所以原 verdict 把它压回 `park` 是对的。

## 它更像 hard park 还是 soft park
- 结论：**soft park**。

原因：
- 它不是纯噪声或实现事故；
- 但失败也不是因为只差一个小阈值就能活；
- 它更像把“市场状态/趋势状态”放错了职责层：原 Rank 24 试图把它写成 `15m` 上的 standalone regime filter 候选，结果信号太薄、收益不够、成本后站不住。

## 现有证据里有没有“可救信号”
- 有，但这次的新证据反而更明确地说明：**可救的不是原 Rank 24 这条写法，而是同主题应转去另一条 raw-alpha family。**

本轮关键新证据：`research/quant_digests/2026-03-24_1030_market-percentile-tsmom-state-alpha.md`
- 这份 digest 把“市场状态”写成了完整 raw alpha：
  - top-third 做多、bottom-third 做空、中间空仓；
  - 有自己独立的 entry / holding / cost 口径；
  - 本地快检显示 `15m` 可工作、`5m` 容易被成本吃掉。
- 这和 `Rank 24` 的核心差别很重要：
  - `Rank 24` 试的是 **trend regime filter / trend-strength-over-noise gate**；
  - 新 digest 指向的是 **market-percentile TSMOM state strategy**；
  - 前者更像“给别的 setup 当门禁”，后者更像“自己就是一条完整策略骨架”。

所以，所谓“可救信号”并不是 `Rank 24b` 应该继续写成某种更花的 gate；而是说：
- 市场状态这个主题没死；
- 但它在 desk 上更诚实的落点，已经偏向**独立 raw alpha 家族**，而不是继续给 `Rank 24` 这种旧 filter 变体加壳。

## 最值得改的唯一一刀是什么
如果只允许给一个唯一修改轴，本轮最值得写清楚的一刀其实是：
- **不要再把 market-state / trend-state 信息写成 standalone shared filter；改成 percentile-state TSMOM raw alpha skeleton。**

但这刀**不应作为 `Rank 24b`** 来写，原因很明确：
1. 这已经不是在“窄 reframe 原 Rank 24”，而是在换策略职责；
2. 它从 filter 变成 raw alpha，修改幅度已经超出 bot6 本轮允许的“保留原 park 审计意义、只提窄改单轴”的边界；
3. 若硬写成 `Rank 24b`，会模糊原 `park` 结论，让人误以为原 Rank 24 只是差一层实现，而不是**原角色定义本身就不对**。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 最终 verdict：**`keep_park`**

原因：
1. 原 `park` verdict 仍应保留：`Rank 24` 这条旧 filter 写法没有被新证据翻案；
2. 新证据支持的是另一条 raw-alpha family，不是原 Rank 24 的窄派生；
3. 若现在硬起一个 `Rank 24b`，会把“新 family intake”误装成“旧 park 救活”，不利于审计清晰度。

## trade on / trade off（为什么这次不立派生假设）
若勉强把新证据往 `Rank 24` 上套：
- trade on：能借“市场状态”主题保留一部分 trend-state 信息；
- trade off：会把 `filter -> raw alpha` 的角色跃迁伪装成窄 reframe，审计上不诚实，也会和 bot2/bot3 的 fresh intake 职责混线。

所以本轮更诚实的处理不是 draft，而是明确记账：
- `Rank 24` 继续 `park`；
- 市场状态分位这条新证据若要进入主流程，应以**新的 raw-alpha intake**身份被后续独立判断，而不是挂在 `Rank 24b` 名下。

## 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 clean replication 下只是少亏，没有形成跨资产、跨时间、跨参数、跨成本仍能成立的稳定 pocket。
2. **它更像 hard park 还是 soft park？**
   - `soft park`。
3. **有没有可救信号？**
   - 有，但指向的是新的 percentile-state raw alpha family，不是原 Rank 24 filter 写法本身可救。
4. **最值得改的唯一一刀是什么？**
   - 把 market-state 主题从 old filter 角色改写成独立 percentile-state TSMOM raw alpha skeleton。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；这已超出对原 Rank 24 的窄 reframe 边界。

## 对 queue 的最小写回
- `docs/PARK_REFRAME_QUEUE.md`：仅追加一条最近复盘记录；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 不新增 `Rank 24b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：`git status --short | wc -l = 2895`，工作区无关脏文件过多，不适合安全混提；本轮仅做最小必要文件改动。
