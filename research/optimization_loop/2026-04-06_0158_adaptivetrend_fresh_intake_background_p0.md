# Rank pending / AdaptiveTrend rolling-Sharpe trend basket fresh intake -> background/P0

- 时间：2026-04-06 01:58 UTC
- 对象：`research/quant_digests/2026-04-06_0144_adaptivetrend-rolling-sharpe-trend-basket-alpha.md`
- 槽位：Fresh intake
- 本轮动作：fresh intake first verdict
- 结论：`background / P0`

## 本轮为什么直接收口
这条对象**不是新的 distinct trend raw alpha 壳**，更像是把已有 `lagged-return continuation / TSMOM` 家族，用 `rolling Sharpe selection + ATR trailing stop + 70/30 allocation` 重新打包成一条更完整的组合模板。

换句话说：
- `rolling Sharpe selection` 更像 **admission / portfolio construction layer**，不是新的 alpha source；
- `ATR trailing stop` 更像 **exit / risk shell**，而不是决定性的新 entry source；
- 真正的 base alpha 仍然是熟悉的 **trend / momentum continuation**。

## 为什么这轮不进 `keep_P1`
按当前 desk 口径，这条对象最关键的短板不是“论文写得不完整”，而是：

1. **raw alpha distinctness 不够**
   - digest 自己也承认 base alpha 就是 `lagged-return continuation`；
   - 真正新增的主要是组合层、退出层、仓位分配层，而不是新的可独立命名的 raw alpha source。

2. **原文优势主要停留在 `H4/H6` 级别**
   - 文中最佳结果在 `H6`，而不是 desk 更关心的 `15m/5m`；
   - `15m` 在 digest 里仍然只是“更合理的 transfer check”，不是已被原文或现有证据证明的核心有效频率。

3. **论文的 edge 依赖多层包装一起工作**
   - monthly parameter optimization
   - rolling-Sharpe asset selection
   - asymmetric `70/30` allocation
   - dynamic trailing stop

   这些更像“把一个老趋势 family 调顺”的工程组合，不足以支撑“这是 distinct fresh intake，值得占用 survivor 唯一 follow-up 名额”。

4. **当前系统认知不会因它再前排而明显改变**
   - 我们已经知道趋势类东西在 crypto 可工作；
   - 这篇 paper 更像提供了一个可参考的 trend packaging 模板，而不是一个需要前排继续判真的新原型。

## 会改变系统认知的话
`AdaptiveTrend` 的新增价值主要是 `rolling Sharpe admission + ATR exit + 70/30 allocation` 这套 trend packaging，而不是新的 raw alpha source；在原文最佳证据仍集中于 `H4/H6`、`15m` 仅属待转译场景的前提下，本轮不授予 `keep_P1`，直接记为 `background / P0`。

## 对 runtime 的直接影响
- Fresh intake 本轮已诚实收口；
- 因未达到 `keep_P1`，**不分配 Rank**；
- 不占用 survivor 槽位；
- 后续只可作为趋势组合层/退出层参考材料留在 background pool，不自动回前排。
