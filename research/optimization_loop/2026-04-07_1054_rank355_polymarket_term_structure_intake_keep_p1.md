# Rank 355 · Polymarket term-structure × Kalman-OU spread · fresh intake first verdict = keep_P1

- Time: 2026-04-07 10:54 UTC
- Target: `research/quant_digests/2026-04-07_0740_polymarket-term-structure-kalman-ou-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned Rank: `355`

## 为什么这次不是直接打回旧 event-market / Polymarket 家族
这条材料虽然也来自 Polymarket，但它的 **alpha 主语** 跟当前库里已 intake 过的几条 Polymarket 线不是一回事：

1. **不是 cross-market lag arb**
   - 已有 Polymarket 线里，比较成熟的是 `Binance/Chainlink 先动 -> Polymarket binary odds 后动` 这类跨 venue 滞后修复。
   - Rank 355 不是拿外部 venue 当快腿；它交易的是 **同一事件族内部、相邻 horizon 之间的 term structure 扭曲**。

2. **不是 hard-expiry favorite continuation**
   - 另一批已有材料更偏 `临近到期 favorite/lag/late-entry` 的时间窗 continuation。
   - Rank 355 的本体不是“快到结算了，顺着 favorite 追”；而是 **两条相关 YES 概率曲线之间的相对错价回摆**。

3. **不是 old pairs family 的机械平移**
   - 形式上它当然仍属于 `Kalman hedge ratio + OU/z-score` 这一大类 relative-value 壳。
   - 但这次交易对象换成了 **prediction-market term structure**：同一事件、不同 horizon、带 hard expiry、盘口深度和费率函数都不同于 perpetual / spot pairs。这个 market structure 差异足够大，不能直接按“又一个普通 cointegration pairs”处理。

## 为什么只到 keep_P1，还不能直接升 P2
公开 repo 当前给出的主要是 `streamlit_app.py + SQLite state schema` 侧证据，能看出这条线已经拆到了：
- `pair_state`: `last_z / last_hr / ou_kappa / ou_halflife / is_cointegrated / coint_pval / kelly_fraction / position_size_usd`
- `signals`: `signal_type / z_score / price_short / price_long`
- `trades`: `entry_z / exit_z / hours_held / exit_reason / pnl_usd`

这足以说明：
- 它有独立的 raw alpha 主语；
- 有最小可执行壳（pairing / dynamic HR / OU half-life / entry / exit / sizing）；
- 也至少口头承认了 fee / liquidity / expiry 这些诚实边界。

但它还**没给出足够可审计的 after-cost pocket**：
- 公开可见部分更像 dashboard/state snapshot，不是完整研究包；
- 还没看到足以让 desk 直接进入 P2 的公开 trade blotter / benchmark / per-pair post-cost 分层结论；
- Polymarket 的 fee、盘口深度、临近结算跳变和 stale quote 风险，在 prediction market 上比普通 crypto pairs 更容易直接把 paper edge 吃掉。

所以这轮最诚实的 first verdict 是：

> **Rank 355：`adjacent-horizon YES-price spread × Kalman-OU reversion` 提供了独立于既有 Polymarket lag/continuation 家族的新 raw alpha 主语，且最小执行壳已清楚，先 `keep_P1`；但公开证据还不足以证明存在可审计的 after-cost pocket，暂不升 P2。**

## 建议的唯一 survivor follow-up 方向
如果下一轮要用掉它唯一一次 survivor follow-up，最该补的不是再解释 Kalman/OU，而是只问一个 decisive 问题：

**在最流动的 recurring crypto markets 上，adjacent-horizon pair 的 `post-fee / post-slippage pnl per trade` 是否还能为正，且主要不是靠临近结算的假流动/stale quote 幻觉撑起来。**

也就是把这条线的 blocker 压成一个单点：
- 不是“有没有策略壳”——这个已经有；
- 而是“prediction-market term-structure relative-value 在诚实成本口径下是否真有 pocket”。

## 本轮写回 runtime 的系统认知
- 新增正式身份：`Rank 355`
- Fresh intake first verdict：`keep_P1`
- 层级迁移：进入 `Surviving candidate slot`
- 暂不进入 `Active P2`
