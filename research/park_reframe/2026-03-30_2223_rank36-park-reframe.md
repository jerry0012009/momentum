# 2026-03-30 22:23 UTC · Rank 36 park reframe review

## 这轮看谁
- `Rank 36 / recent-return sign vs history-drift honesty gate`
- 选择原因：
  - 属于已 `park` 的 `Rank 1~37` 条目；
  - 最近 `bot6` 已连续覆盖 `Rank 11 / 14 / 20 / 27 / 31 / 33 / 35`，这一轮切回仍未形成新派生的方向性旧线；
  - 2026-03-29~03-30 又新增了几条短周期方向 / 时钟新证据，适合再确认一次：
    1. `2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`
    2. `2026-03-30_0844_pseudosession-open-leader-continuation-alpha.md`
    3. `2026-03-30_0929_intraday-hourpair-momentum-reversal-alpha.md`
  - 这几条都在说明“短周期方向性未死”，但未必仍属于原 `Rank 36` 的血缘。

## 原 rank 为什么 park
根据 `research/optimization_loop/2026-03-17_1653_rank36-clean-replication-park.md`：
- 最小 clean replication 已把问题压成三档 honesty 对照：
  - `recent_sign_only`
  - `history_drift_only`
  - `recent_and_drift_agree`
- 在 `BTC/ETH/SOL 120d 15m`、`next-bar open`、`8 bar hold`、`no-overlap`、`6bps/side` 下，三档都明显为负：
  - `recent_sign_only ≈ -53.20%`
  - `history_drift_only ≈ -18.13%`
  - `recent_and_drift_agree ≈ -49.58%`
  - `positive_asset_ratio = 0/3`
- 时间桶也没有给出诚实 pocket：
  - `bucket_1 ≈ -32.91%`
  - `bucket_2 ≈ -17.56%`
  - `bucket_3 ≈ -8.41%`

翻成人话：原线已经把“快 sign 是否只是慢 drift 的伪装”这个问题审得够清楚了，答案是——不是简单补一层 drift 就能活。

## 它更像 hard park 还是 soft park
- 结论：**soft park，但比 2026-03-24 更偏 hard。**

原因：
- 它仍然留下“慢状态比快状态略不差”的解释性残余，所以还不算纯硬垃圾；
- 但这点残余一直无法长成一个独立 queue-facing 候选；
- 最近一周的新证据越来越一致地说明：可交易信息活在**阈值状态机 / pseudo-session leader / fixed clock pocket** 这类更完整的 raw-alpha family 里，而不是原 `Rank 36` 的 `recent sign vs drift` honesty-gate 对照里。

## 有没有“可救信号”
- **有，但更像“主题上移”，不像“原命题可救”。**

### 1) `GMADL directional threshold` 新证据
`2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md` 指向的是：
- 方向预测若要活，更像 `thresholded long/short state machine + abstain`；
- 关键在高阈值分档、状态切换、明确 abstain，而不是 `recent_sign_only` 或 `history_drift_only` 这种两档符号对照。

对 `Rank 36` 的含义：
- 说明“方向性判断”仍可研究；
- 但它要求的是一整套新的 thresholded verdict skeleton，而不是对原线补一层 drift veto。

### 2) `pseudo-session open leader continuation` 新证据
`2026-03-30_0844_pseudosession-open-leader-continuation-alpha.md` 指向的是：
- edge 更像发生在 pseudo-session open 附近的 leader continuation；
- 可交易信息落在 session-boundary / leader impulse / spread-to-runner gate 上。

对 `Rank 36` 的含义：
- 它把方向性重新锚定到时钟和事件，而不是 generic recent-sign；
- 这不是 `Rank 36b` 的窄修补，而是新的 clocked raw-alpha family。

### 3) `intraday hour-pair momentum/reversal pocket` 新证据
`2026-03-30_0929_intraday-hourpair-momentum-reversal-alpha.md` 指向的是：
- 同样的方向主题，在不同小时对上可能是 continuation，也可能是 reversal；
- 可交易残余更像 `hour-pair pocket`，不是全天统一的 sign-vs-drift gate。

对 `Rank 36` 的含义：
- 进一步说明原线最大的问题不是“drift 没加对”，而是**把时钟条件压平了**；
- 真要救，已经不是单轴微调，而是改成另一条策略骨架。

## 最值得改的唯一一刀是什么
如果硬要保留原线血缘，唯一还算诚实的一刀只能是：
- **把 `recent-sign vs drift` 从 standalone honesty gate，降级成固定 UTC / pseudo-session pocket 内的 direction-state abstain overlay。**

但这刀**当前不值得立项**，因为：
1. 原线自己没有留下足够 pocket；
2. 新证据都要求“先有时钟 / 状态机，再谈方向”，不再是原命题的单轴微调；
3. 一旦这样改，马上会和 `Rank 5b / 7b / 21b / 76 candidate / Rank 201 family` 高度重叠。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 最终 verdict：**`keep_park`**

## 为什么不是 `soft_reframe_candidate`
因为这次不是“还差一点 distinctness”；而是最近新证据越来越清楚地把残余价值上移到：
- thresholded directional state-machine family；
- pseudo-session / hour-pair clock family；
- 更完整的 direction raw-alpha skeleton。

也就是说，原 `Rank 36` 的 residual value 已经不再适合被诚实地包装成 `Rank 36b`。继续保留为 `candidate` 只会制造重复候选。

## 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 `recent_sign_only / history_drift_only / recent_and_drift_agree` 三档最小 honesty 对照在成本后全部跨资产为负，时间桶也没有形成稳定 pocket。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但比 2026-03-24 更偏 hard。
3. **有没有“可救信号”？**
   - 有，但信号在指向 `thresholded directional state-machine / pseudo-session leader / hour-pair clock pocket` 新 family，不在救原 `Rank 36`。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能降级成固定时钟口袋内的 direction-state abstain overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 36b`？**
   - 因为新证据要求的是另一套 raw-alpha / clocked-state skeleton，而不是原主题单轴微调；硬写成 `36b` 会削弱原 `park` verdict 的审计边界，也会与现有 clock / overlay 提案重叠。

## 对 queue 的最小写回
- `research/park_reframe/INDEX.md`：追加本轮索引；
- `docs/PARK_REFRAME_QUEUE.md`：仅追加一条最近复盘记录；
- 不新增 `Rank 36b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：工作区存在大量无关脏文件；本轮只做最小必要文本改动，避免混提。
