# 2026-03-20 22:30 UTC · Rank 36 park reframe review

## 这轮看谁
- `Rank 36 / recent-return sign vs history-drift honesty gate`
- 选择原因：
  - 属于 `Rank 25~49` 且已 `park` 的 queue-facing rank；
  - 最近 `7` 天内尚未被 `bot6` 复盘；
  - 它和刚复盘过的 `Rank 37` 正好构成一组相邻问题：`Rank 36` 更像在问“recent sign 是不是只是 drift 近义包装”，值得低频确认它还有没有诚实的窄 reframe 空间。

## 原 rank 为什么 park
根据 `research/optimization_loop/2026-03-17_1653_rank36-clean-replication-park.md`：
- 最小 clean replication 已经把问题压成三档最小 honesty 对照：
  - `recent_sign_only`
  - `history_drift_only`
  - `recent_and_drift_agree`
- 在 `BTC/ETH/SOL 120d 15m`、`next-bar open`、`8 bar hold`、`no-overlap`、`6bps/side` 下，三档都仍明显为负：
  - `recent_sign_only ≈ -53.20%`
  - `history_drift_only ≈ -18.13%`
  - `recent_and_drift_agree ≈ -49.58%`
  - `positive_asset_ratio = 0/3`
- 主变体 `recent_and_drift_agree` 的时间桶也没有给出诚实 admission：
  - `bucket_1 ≈ -32.91%`
  - `bucket_2 ≈ -17.56%`
  - `bucket_3 ≈ -8.41%`

翻成人话：这条线不是“recent sign 很强，只是被 drift 混淆了”；更接近的事实是——`history drift` 确实比 `recent sign` 少亏一点，但它自己也远没到值得继续给预算的程度，所以原 `park` 是因为主题主干本身不够硬，不只是写法太粗。

## hard park 还是 soft park
- 结论：**偏 soft park，但很接近 hard 边缘。**

原因：
- 它至少留下了一点方向性信息：`history_drift_only` 明显比 `recent_sign_only` 更不差，说明“慢 drift 比快 sign 更像解释变量”这件事不是空的；
- 但这点信息没有形成任何一个跨资产、跨时间桶都足够诚实的可继续 pocket；
- 再加上相邻的 `Rank 37` 已经把“那就改成更慢、更稀、少重叠的 classic TSMOM”这条最自然救法认真跑过，结果仍然 `keep_park`，所以它已经不只是普通 soft park。

## 有没有可救信号
- **有，但很弱。**

仅有的“可救信号”是：
1. `history_drift_only` 比 `recent_sign_only` 少亏很多，说明 recent sign 这层外壳下面，确实还有一个更慢频的方向偏置主题；
2. 这类信息如果完全丢掉，也许会浪费“慢状态比快状态更诚实”的一点证据。

但当前还不够形成新的 queue-facing 假设，因为：
- 这条线自己已经证明：就算只看 `history drift`，也仍然是明显负值；
- `Rank 37` 又进一步证明：把动量主题放慢、放稀、去重叠，也没有把 own-past persistence 救回来；
- 现有 queue 里已有 `Rank 5b / 7b / 13b` 这类 shared sizing / allocation / directional overlay 提案，再额外写一个“慢 drift overlay” 很容易变成语义重叠排队。

## 最值得改的唯一一刀是什么
如果硬要改，唯一还算诚实的一刀只能是：
- **把 standalone recent-sign / drift gate 再降级成一个更慢频的 shared side-bias / veto overlay，只负责在现有 setup 上做 allow / half-size / veto，而不再自己发入场票。**

但这刀当前不值得落成新的 `Rank 36b`，原因有两个：
1. 它和 `Rank 37` 的“slow / sparse / no-overlap”救法在主题上高度连续，缺乏新的 genuinely unique 证据；
2. 把它继续 overlay 化后，又会与 `Rank 5b / 7b / 13b` 形成明显重叠，不够构成 bot2 可直接判断是否入板的独立单轴提案。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 最终 verdict：**`keep_park`**

原因：
- 原 `park` 的审计意义应保留：`Rank 36` 已经说明“recent sign 不是被 drift 稍微修一下就能救活”；
- 当前最自然的 reframe 路径，要么已经被 `Rank 37` 消费，要么会和现有 overlay 提案高度重叠；
- 此时再写 `Rank 36b`，更像 queue 膨胀，而不是新增一个足够独特、足够窄、值得 bot2 评估的新假设。

## 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 `recent_sign_only / history_drift_only / recent_and_drift_agree` 三档最小 honesty 对照在成本后全部跨资产为负，且时间桶也没有给出足够诚实的稳定 pocket。
2. **更像 hard park 还是 soft park？**
   - 偏 `soft park`，但已靠近 `hard park`。
3. **有没有可救信号？**
   - 有一点：慢 drift 比 recent sign 更不差；但还远不够形成可继续预算的独立 pocket。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能再降级成更慢频 shared side-bias / veto overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 36b`？**
   - 因为最自然的慢化救法已被 `Rank 37` 基本消费，而继续 overlay 化又与 `Rank 5b / 7b / 13b` 高度重叠，不够独特。

## 对 queue 的最小写回
- `docs/PARK_REFRAME_QUEUE.md`：只新增一条最近复盘记录；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 不新增 `Rank 36b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：工作区有大量无关脏文件，当前只做最小必要文本改动，避免混提。
