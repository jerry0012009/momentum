# Rank 175 / fomc-event-clock-veto-size-down-overlay — fresh intake 首判（keep_P1）

- 时间：2026-03-26 02:07 UTC
- 对象：`research/quant_digests/2026-03-26_0106_fomc-event-clock-veto-size-down-overlay.md`
- 结论：**keep_P1，不升 P2**
- 正式 Rank：**175**

## 这轮只回答一个问题
这条 `FOMC event clock veto + size-down overlay`，是否值得作为新的前排候选保留？

回答：**值得保留到 P1，但当前证据不支持把它写成独立 raw alpha，更不支持直接升 P2。**

## 为什么保留
1. **它解决的是共享执行风险，不是又一条伪方向信号。**
   digest 已把对象说清楚：`scheduled FOMC release` 的已知时点，会系统性抬升短时波动与成交，最先受冲击的是 fill quality、slippage 与 adverse selection。对 short-cycle desk 来说，这是真问题，不是宏观叙事装饰。
2. **这条线可以独立复现，而且服务现有多个策略家族。**
   它天然能挂到 breakout / momentum、mean reversion、maker / taker execution 三类栈上，属于共享 overlay，而不是只能服务某个孤立因子的专用补丁。
3. **骨架已经足够完整，值得消耗唯一一次 survivor follow-up。**
   现在已有明确的 `soft gate / hard gate / cooldown / re-arm` 框架，也有 Fed 日历与 Binance 公共数据支撑“事件窗确实不同于普通时段”。这已经超过一句话灵感，值得进一次前排 follow-up。

## 为什么这轮不升 P2
1. **它不是独立 alpha，对象形态就不该直接按 raw alpha admission 处理。**
   当前最诚实的定位是 `shared event-risk overlay`。如果没有清楚回答“接到哪些现有策略后，真实改善的是回撤/成交质量/尾部损失中的哪一项”，现在就升 P2 会把对象写歪。
2. **目前证据证明的是“事件窗存在”，还没证明“overlay 接入后净效果稳定可部署”。**
   digest 给了事件前后波动与成交量放大的证据，但还没有 `with gate vs without gate` 的真实 A/B 结果；这一步才是决定它能否进更高层级的关键。
3. **唯一便宜 follow-up 也很明确。**
   下一步不该继续泛泛补宏观文献，而只该回答一个问题：把这条 `event-clock veto / size-down / re-arm` 接到现有一类 short-cycle 策略后，是否能在不明显伤害基线收益的前提下，改善回撤、成交质量或尾部损失。

## 本轮改变的系统认知
**Rank 175 / fomc-event-clock-veto-size-down-overlay 值得以前排 P1 身份保留的，不是任何 FOMC 后方向交易故事，而是 `scheduled FOMC release -> shared risk overlay / veto + size-down + re-arm` 这条可复用的 event-clock 骨架；当前仍未证明可直接升入 P2。**

## Runtime 落点
- `Fresh intake slot`：本轮首判完成
- `Surviving candidate slot`：切换为 `Rank 175 / fomc-event-clock-veto-size-down-overlay`
- `followup_budget_remaining`：`1`
- 本轮未创建 `Active P2`，也未触发 `P2 -> P3`
