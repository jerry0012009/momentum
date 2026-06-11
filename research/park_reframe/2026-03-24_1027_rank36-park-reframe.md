# 2026-03-24 10:27 UTC · Rank 36 park reframe review

## 这轮看谁
- `Rank 36 / recent-return sign vs history-drift honesty gate`
- 选择原因：
  - 属于 `Rank 1~37` 已 `park` 条目；
  - 最近几轮 `bot6` 主要在别的 rank 上轮转，这条线距离上次复盘已相对更久；
  - 2026-03-23~24 新增了两类方向性新证据，值得低频确认一次：
    1. `2026-03-23_1828_intraday-double-clock-momentum-reversal-fullstack.md`
    2. `2026-03-24_0840_rolling-fpca-intraday-sign-alpha.md`
  - 这两类证据都在提醒：短周期方向性主题未死，但更像**新的 raw-alpha 家族**，未必是原 `Rank 36` 这条 honesty-gate 线的可救单轴。

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

翻成人话：这条线已经证明，`recent sign` 不是被 `drift` 稍微校正一下就能活；慢一点的 `history drift` 虽然没那么差，但也远没到值得继续给预算的程度。

## 它更像 hard park 还是 soft park
- 结论：**偏 hard 的 soft park。**

原因：
- 还留有一点点“慢状态比快状态更诚实”的残余信息，所以不是纯粹无意义；
- 但这点残余信息已经弱到不足以支撑独立 queue-facing 候选；
- 原线主问题不是实现粗糙，而是题目本身太像“解释性 honesty check”，不像可独立交易或可独立 admission 的窄策略骨架。

## 有没有“可救信号”
- **有，但它更像指向新 family，不像在救 Rank 36 本身。**

### 1) 来自 2026-03-23 的 double-clock 证据
`2026-03-23_1828_intraday-double-clock-momentum-reversal-fullstack.md` 说明：
- 短周期方向性 edge 若成立，更像**固定时钟的 open-impulse momentum + pre-close reversal 双腿**；
- 这是完整 raw alpha，不是“recent sign vs drift”的 honesty gate 微调。

对 `Rank 36` 的含义：
- 说明“方向性主题未死”；
- 但它把可交易信息重新落在**session clock / event clock** 上，而不是 `recent_sign_only` 或 `history_drift_only` 这种慢快收益符号对照。
- 换句话说，若要重开，更像另开新 rank，而不是给 `Rank 36` 再补一层解释。

### 2) 来自 2026-03-24 的 rolling-FPCA 证据
`2026-03-24_0840_rolling-fpca-intraday-sign-alpha.md` 说明：
- 下一段方向可预测这件事，若真有 edge，更像来自**函数形态 / rolling forecast / confidence 分桶**；
- 这同样是新的 direction raw-alpha skeleton，不是原 `Rank 36` 的“recent sign 与 drift 谁更诚实”再换一版阈值。

对 `Rank 36` 的含义：
- 进一步证明“方向预测”值得研究；
- 但它要求的唯一主修改轴，已经不再是 `Rank 36` 可承受的一刀，而是改成另一套 feature family / 建模骨架；
- 这会直接破坏原 `park` verdict 的审计意义，不适合被包装成 `Rank 36b`。

## 最值得改的唯一一刀是什么
如果硬要保留与原线的血缘关系，唯一还算诚实的一刀只能是：
- **把 `recent-sign vs drift` 从 standalone honesty gate 改写成一个更慢频的 side-bias / abstain overlay，仅在既有 setup 已触发时才决定 allow / veto。**

但这刀当前**不值得立项**，因为：
1. 它仍然没有来自原线自身的强 pocket；
2. 新证据真正支持的是 `clock alpha` 或 `forecast alpha`，不是这个 overlay；
3. 继续 overlay 化后，会与现有 `Rank 5b / 7b / 13b / 21b` 一类 shared layer 提案明显重叠。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 最终 verdict：**`keep_park`**

## trade on / trade off（仅作为“不立项”的澄清）
如果有人硬要把它写成派生假设，理论上的那唯一一刀会是：
- `trade on`：现有 setup 已触发，且慢频 drift side-bias 与 setup 同向时才 allow
- `trade off`：setup 已触发，但 drift side-bias 反向或缺失时 abstain / veto

但本轮明确判断：**这还不配进入 queue 作为新的 derived hypothesis**，因为证据并不指向这条 overlay 本身，而是指向别的 direction raw-alpha family。

## why now
- 因为 2026-03-23~24 新证据可能让人误以为：“既然短周期方向性又有论文/新 digest 支持，那 `Rank 36` 可以顺手救一下。”
- 本轮的作用，就是把这层误会切干净：
  - **方向性主题可以继续研究；**
  - **但不等于原 `Rank 36` 值得派生 `Rank 36b`。**

## suggested initial state
- 不适用；本轮不是 `derived_hypothesis_drafted`。

## 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 `recent_sign_only / history_drift_only / recent_and_drift_agree` 三档最小 honesty 对照在成本后全部跨资产为负，时间桶也没有形成稳定 pocket。
2. **它更像 hard park 还是 soft park？**
   - 偏 hard 的 soft park。
3. **有没有“可救信号”？**
   - 有，但信号在指向新的 `clock alpha / forecast alpha` 家族，不在救原 `Rank 36`。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能降级成慢频 side-bias / abstain overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 36b`？**
   - 因为新证据要求的不是同主题单轴微调，而是另一套 raw-alpha 骨架；硬写成 `36b` 会推翻原 `park` 的审计边界，也会与现有 overlay 提案重叠。

## 对 queue 的最小写回
- `docs/PARK_REFRAME_QUEUE.md`：仅追加一条最近复盘记录；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 不新增 `Rank 36b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：`git status --short | wc -l = 2878`，工作区无关脏文件过多，不适合安全 selective commit；本轮仅做最小必要文本改动。
