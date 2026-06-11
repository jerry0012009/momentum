# 2026-03-20 20:20 UTC · Rank 37 park reframe review

## 这轮看谁
- `Rank 37 / classic sparse TSMOM / own-past persistence pocket`
- 选择原因：
  - 属于 `Rank 25~49` 且已 `park` 的 queue-facing rank；
  - 最近 `7` 天内尚未被 `bot6` 复盘；
  - 它的失败形态有代表性：不是高频 sign-momentum，而是已经主动收窄成“更慢、更稀、少重叠”的 classic TSMOM 口径，所以值得低频确认一次：到底还有没有诚实的单轴可救。

## 原 rank 为什么 park
根据 `research/optimization_loop/2026-03-17_1717_rank37-clean-replication-park.md`：
- 最小 clean replication 已经故意把它收成 slow / sparse / no-overlap：
  - `slow_4h_sign_hold_4h`
  - `slow_12h_sign_hold_8h`
  - `slow_4h_12h_agree_hold_8h`
- 但在 `BTC/ETH/SOL 120d 15m`、`next-bar open + no-overlap`、`6bps/side` 下三臂仍然全部跨资产转负：
  - `slow_12h_sign_hold_8h ≈ -37.61%`
  - `slow_4h_sign_hold_4h ≈ -35.60%`
  - `slow_4h_12h_agree_hold_8h ≈ -35.24%`
  - `positive_asset_ratio = 0/3`
- 主变体时间桶虽出现 `bucket_3` 单段转正，但 `bucket_1 / bucket_2` 仍明显为负，说明它不是“稳定 slow pocket 被短样本掩盖”，而更像 **后段局部侥幸 + 全局仍不够诚实**。

翻成人话：这条线已经主动避开了“拿得太快、太密、太重叠”的常见借口，但仍然没有把 own-past persistence 救活，所以原 `park` 不是因为实现太粗，而是因为 **核心 pocket 仍然不够硬**。

## hard park 还是 soft park
- 结论：**偏 hard park。**

原因：
- 这不是“原始 high-turnover 动量先失败，slow-pocket 还没认真看”的情况；
- 恰恰相反，`Rank 37` 就是把 classic TSMOM 主体最自然的窄救法——`slow / sparse / no-overlap`——先认真跑过一遍以后，仍然被压回 `park`；
- 因而它比一般 soft park 更接近“主题主干已经被审计消费”。

## 有没有可救信号
- **有一点，但不够形成新的独立派生。**

仅剩的“可救味道”主要是两类：
1. `bucket_3` 有局部转正，说明 own-past persistence 不是完全没有任何时间 pocket；
2. `Rank 36 / TSM vs drift honesty gate` 至少说明“慢 drift 比 recent sign 更不差”，即问题并不只是参数太短。

但这些信号都不够支持再起一条新的 `Rank 37b`，因为：
- `Rank 37` 已经把“放慢、变稀、去重叠”这条最自然改单轴用掉了；
- `Rank 36` 又把“recent sign 其实只是 drift 近义包装吗”这层诚实门也补过了，结果同样没救回来；
- 最新 `2026-03-20 19:25` 的 OOS persistence digest 也更像是在提醒：**别把 persistence / recent winner 继续往独立主 alpha 上抬**，而应把确认与 overlay 留给现有 breakout / Fib / EMA-PSAR 主线。

所以，`Rank 37` 当前的“可救信号”更像主题背景噪音，还不到能落成 queue-facing 新假设的程度。

## 最值得改的唯一一刀是什么
如果硬要改，唯一还算诚实的一刀只能是：
- **把 standalone classic sparse TSMOM 再降级成一个更慢频的 shared side-bias / veto overlay，而不再让它自己直接发入场票。**

但这刀现在不值得写成 `Rank 37b`，原因很直接：
- 它已经和 `Rank 5b`（session impulse sizing）、`Rank 7b`（one-regime-per-session allocation）、`Rank 13b`（方向性 veto / sizing overlay）形成高语义重叠；
- 再写一个 `Rank 37b`，大概率只是在把“慢动量别单独交易，降级成 overlay”换个说法重新排队，而不是新增 genuinely unique 的单一主修改轴。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 最终 verdict：**`keep_park`**

原因：
- 原 `park` 审计意义应保留：`Rank 37` 已经证明“就算主动收成 slow / sparse / no-overlap，classic own-past persistence 在当前 15m crypto clean-room 里仍不够诚实”；
- 当前最自然的 reframe 方向并不独特，且已被 `Rank 36` 与现有 overlay 派生（`5b / 7b / 13b`）基本消费；
- 若此时再写 `Rank 37b`，更像 queue 膨胀，而不是提供 bot2 可直接判断是否入板的新主修改轴。

## 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为在已经收窄成 slow / sparse / no-overlap 的最小 clean replication 后，三档变体仍跨资产转负，只有零散时间 pocket，没形成可继续给预算的 own-past persistence 证据。
2. **更像 hard park 还是 soft park？**
   - 偏 `hard park`。
3. **有没有可救信号？**
   - 只有很弱的时间 pocket / drift-relative 信号，但不够支撑新的 queue-facing 假设。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能再降级成更慢频 shared side-bias / veto overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 37b`？**
   - 因为最自然的改单轴（slow / sparse / no-overlap）已被原 Rank 37 消费，而再往下的 overlay 化又与 `Rank 5b / 7b / 13b` 高度重叠，不够独特。

## 对 queue 的最小写回
- `docs/PARK_REFRAME_QUEUE.md`：只新增一条最近复盘记录；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 不新增 `Rank 37b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：工作区有大量无关脏文件，当前只做最小必要文本改动，避免混提。
