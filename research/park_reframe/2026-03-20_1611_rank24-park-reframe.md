# 2026-03-20 16:11 UTC · Rank 24 park reframe review

## 这轮看谁
- `Rank 24 / trend regime filter / trend-strength-over-noise gate`
- 选择原因：
  - 属于 `Rank 1~37` 已 `park` 条目；
  - 最近 `7` 天内未被 `bot6` 复盘；
  - 这条线的失败形态比较典型：不是“完全没想法”，而是很像一个**角色错位**的旧候选，值得低频确认一次是否还有窄 reframe 空间。

## 原 rank 为什么 park
根据 `2026-03-17_0549_rank24-clean-replication-park.md`：
- 最小 clean replication 下，`baseline_mtf`、`trend_regime_default`、`stricter_trend_threshold`、`stricter_regime_score` 在 `6bps/side` 下都仍是负收益；
- 最好的 `stricter_trend_threshold` 也只是把亏损收窄到约 `-9.81%`，`positive_asset_ratio` 仍只有 `1/3`；
- 时间桶里虽有零散正 pocket，但没有形成可跨资产复用的稳定 pocket；
- 参数邻域没有给出能升格的稳定平台；
- 成本从 `10/15/20bps` 继续恶化，说明它不是“差一点就能上桌”，而是 **regime 过滤本身没有把这条 15m 线救活**。

翻成人话：它确实比最粗的 baseline 少亏一点，但主要停在“没那么差”，没有进到“够诚实、够稳、值得继续给预算”的层级。

## hard park 还是 soft park
- 结论：**偏 soft park，但不是值得立刻再派生的 soft park。**

原因：
- `Rank 24` 的失败不像纯数据错误或实现粗糙；
- 但它也不是“一刀就快救活”的状态，因为最自然的单轴改写——把 standalone regime filter 降级成 shared allow/deny / veto / size-down 层——这条路，最近几天其实已经被近邻证据基本消费掉了。

## 有没有可救信号
有，但很弱，而且已经被旁支证据吸收得差不多：
1. 原始 clean replication 里，`stricter_trend_threshold` 比 baseline 少亏，说明“环境过滤”这个主题本身不是完全没信息；
2. 但最近更贴 desk 的旁支已经把“regime / environment 只做 shared 角色、不做独立 alpha”这条路走得更清楚：
   - `Rank 9b`：把 regime-switch stack 降级成 `EMA(RSI)` asymmetric shared veto；
   - `Rank 21b`：把 market risk-on/off 降级成 daily sentiment-extremity shared risk overlay；
   - `Rank 25b`：把 environment 许可层收窄成 `30m 4-state regime matrix allow/deny gate`；
   - `2026-03-20 10:28` digest 还明确提示：`ADX<18 + BB/RSI extreme` 只够当 `skip / size-down`，不够直接升级成 shared range handoff；
   - `2026-03-20 13:22` digest 也把家族座次写得更死：`breakout/filter` 更像主触发，`EMA/PSAR` 更像确认/风控位，避免继续让泛 regime 主题抢主位。

所以，`Rank 24` 的“可救信号”并不是没有，而是**已经被更窄、更新、更贴 desk 的旁支版本承接了**。

## 最值得改的唯一一刀是什么
如果硬要改，唯一还算诚实的一刀仍然是：
- **把 standalone trend regime filter 再降一级，只保留成 shared allow/deny / size-down 层，而不是独立入场候选。**

但这刀现在不值得再单独起一个 `Rank 24b`，因为：
- 它与现有 `Rank 9b / 21b / 25b` 的语义重叠太高；
- 再写一个 `Rank 24b`，大概率只是把“环境层”换个说法重复排队，而不是提供新的唯一主修改轴；
- `2026-03-20` 当天的新 digests 也没有给出 `Rank 24` 专属、尚未被消费的新证据。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 最终 verdict：**`keep_park`**

原因：
- 原 `park` 审计意义应保留：`Rank 24` 已经被证明“不足以作为 15m 独立候选”；
- 当前最自然的 reframe 方向并不独特，已经被近邻 queue-only 派生（`9b / 21b / 25b`）和最近 regime digests 基本覆盖；
- 若这时再写 `Rank 24b`，更像 queue 膨胀，而不是新增 genuinely verdict-changing 的窄假设。

## 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为 clean replication 下只是少亏，没有形成跨资产、跨时间、跨参数、跨成本仍可升格的稳定 pocket。
2. **更像 hard park 还是 soft park？**
   - 偏 `soft park`。
3. **有没有可救信号？**
   - 有一点，但主要已经被更近的新旁支证据吸收。
4. **最值得改的唯一一刀是什么？**
   - 降级成 shared allow/deny / size-down environment layer。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 24b`？**
   - 因为这条最自然的改单轴已经被 `Rank 9b / 21b / 25b` 和最近 regime/range digests 基本消费，再单列只会重复排队。

## 对 queue 的最小写回
- `docs/PARK_REFRAME_QUEUE.md`：只新增一条最近复盘记录；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 不新增 `Rank 24b`；
- 不改 `docs/TODO.md` 顶部排班。

## Git / 提交
- 本轮未提交。
- 原因：`git status --short | wc -l = 1906`，工作区有大量无关脏文件，不适合安全混提；本轮仅做最小必要文件改动。
