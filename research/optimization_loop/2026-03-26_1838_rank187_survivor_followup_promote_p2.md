# Rank 187 / BTCUSDT 15m late-session path-shape swing — survivor follow-up 收口（promote_P2）

- Time: 2026-03-26 18:38 UTC
- Target: `Rank 187 / BTCUSDT 15m late-session path-shape swing`
- Step type: survivor follow-up (the only decisive follow-up)
- Verdict: `promote_P2`

## 本轮只回答的问题
对 `Rank 187` 这条 exact pocket —— **`15m` 观察前 `8h` + `60d lookback` + `k=3` 最近邻 partial-day path-shape，若预测余下时段仍有更高 future max 则开 long，并按 predicted-max timing 平仓** —— 做最小 survivor follow-up：

1. 这条 edge 是否只依赖当前 `predicted-max exit` 这一种偶然翻译？
2. 如果换成更朴素的 exit 对照（`hold-to-EOD` / 固定持有），它是否仍保留正向可交易 pocket？
3. 若答案是肯定的，是否已足够从 `P1 survivor` 升入 `P2 admission`？

## 本轮方法（最小替代实现 / exit 对照）
沿用 intake 已锁定的 **同一组 entry**（`h32_k3`，18 笔交易，`BTCUSDT 15m`），不重开新 spec、也不扩写 path-shape 家族，只比较不同 exit：

- `predicted-max exit`（原始 pocket）
- `hold-to-EOD`
- `fixed hold 4 bars`
- `fixed hold 8 bars`
- `fixed hold 12 bars`

使用数据：
- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/selected_variant_trades.csv`
- `reports/artifacts/scout_rank76_intraday_clock_polarity_15m/btcusdt_feature_frame.csv`

## 结果
### 1) 原始 `predicted-max exit` 仍是最厚版本
同一组 18 笔 entry 上，重算结果与 intake 结论一致：

- `predicted-max exit`: `avg trade +0.499% gross`
- 扣 `6bps` round-trip 后：`+0.439% / trade`
- 平均持有：`50.6 bars`

说明原 pocket 不是读错；在当前 exact object 上，`predicted-max exit` 仍是最强翻译。

### 2) 但 edge 并不只靠这一个 exit 偶然成立
更关键的是：把 exit 换成更朴素的版本后，方向判断仍保留正值，而不是一换 exit 就塌。

- `hold-to-EOD`: `avg trade +0.234% gross`，`6bps` 后 `+0.174%`
- `fixed hold 4 bars`: `avg trade +0.167% gross`，`6bps` 后 `+0.107%`
- `fixed hold 8 bars`: `avg trade +0.242% gross`，`6bps` 后 `+0.182%`
- `fixed hold 12 bars`: `avg trade +0.197% gross`，`6bps` 后 `+0.137%`

这说明 `Rank 187` 至少有两层东西同时存在：
- **方向层**：晚些时候的 path-shape 确实在提示“余下时段更容易继续上摸”；
- **时机层**：`predicted-max exit` 只是把同一方向 edge 放大，而不是凭空制造利润。

### 3) 这已经足够越过 survivor 门槛
Survivor 这一轮要回答的不是“五维 admission 已全部完成没有”，而是：

> 这条 exact pocket 在做过一次便宜但诚实的替代实现 / exit 对照后，是否仍值得进入更正式的 `P2 admission`？

当前答案是 **是**，理由有三：

1. **不是单一 exit 偶然**：固定持有与 EOD 对照都仍为正；
2. **厚度并未被基础成本直接吃光**：最朴素替代 exit 在 `6bps` 后仍保留 `+10.7 ~ +18.2 bps/trade`；
3. **对象 scope 已经足够窄且可 admission 化**：它不是“FPCA/path forecasting 家族”，而是一个冻结到 `BTCUSDT 15m late-session path-shape swing` 的单一 pocket，下一步可以老老实实围绕 `effectiveness / cross-asset / time / parameter / honesty` 五项 admission 展开。

## 为什么本轮不是 park_to_background
当前确实还有明显限制：
- 只有 `BTC`；
- 样本只有 `18` 笔；
- 参数邻域还不算厚；
- `predicted-max exit` 本身仍偏 model-heavy。

但这些都属于 **P2 admission 应该回答的问题**，不是 survivor 阶段就足以把对象直接判死的 fatal flaw。

更直白地说：
- 如果对照后“一换 exit 就没了”，那应该 park；
- 但现在不是。当前看到的是：**原始 exit 最优，但更笨的 exit 也还活着。**

这就足够把它从 `keep_P1` 推进到 `promote_P2`。

## 冻结后的 P2 admission 对象
**Rank 187 = `BTCUSDT 15m late-session path-shape swing`**

冻结 spec：
- market: `BTCUSDT`
- bar: `15m`
- observation window: 前 `8h`（`32` 根 bars）
- lookback: `60d`
- similarity: `k=3` nearest-neighbor partial path shape
- entry: 仅当 implied remainder path 仍指向更高 future max 时开 `long`
- baseline exit for admission: `predicted-max timing`
- exit controls already checked: `EOD` / `hold 4` / `hold 8` / `hold 12`

## 下一步 admission 应该收敛到什么
既然 survivor 唯一 follow-up 已通过，下一步 `P2 admission` 不该再回头重复 exit 对照，而应围绕：

1. `effectiveness / expected return`：更完整净边与 trade density
2. `cross-asset stability`：ETH 是否有可复制 pocket，还是纯 BTC 单点
3. `time stability`：2025Q4 vs 2026Q1 是否被少数周段包办
4. `parameter stability`：`obs window / k / lookback` 附近是否有薄平原
5. `honesty / execution realism`：next-bar open、non-overlap、以及 model-heavy exit 的可执行近似

## 本轮结论（一句话）
**Rank 187 / BTCUSDT 15m late-session path-shape swing 的 survivor 唯一 follow-up 已诚实收口为 `promote_P2`：当前 edge 不只依赖 `predicted-max exit` 单点偶然，同一组 entry 在 `EOD` 与 `4/8/12-bar` 朴素 exit 对照下仍保留成本后正值，因此已足够进入正式 `P2 admission`。**
