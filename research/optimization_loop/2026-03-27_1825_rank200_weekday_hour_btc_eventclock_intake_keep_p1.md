# Rank 200 / weekday-hour Bitcoin event-clock alpha intake：先记 keep_P1，不直接升 P2

- 时间：2026-03-27 18:25 UTC
- 对象：`research/quant_digests/2026-03-27_1555_weekday-hour-bitcoin-eventclock-alpha.md`
- 新分配 Rank：`200`
- 本轮动作：fresh intake
- 结论：**`Rank 200 / BTC weekday-hour sparse short schedule` 首轮 intake 完成：现有论文页 + Binance `1h` quick check 说明“少数固定弱 weekday-hour 后做 BTC 4h short”确实像可复验的 raw alpha pocket，但当前证据仍主要停留在单资产、单 venue、单持有窗的稀疏时钟袋，不足以直接当成可独立部署的完整 schedule 母策略，因此本轮记 `keep_P1`，进入 survivor 做一次便宜但诚实的 follow-up。**

## 为什么不是直接升 P2
1. **独立 pocket 明确，但母策略广度不够。**
   - digest 里的最强结果，本质上集中在“训练样本最弱的少数 weekday-hour 桶，在测试样本里做 `4h short` 仍有正净值空间”。
   - 这说明它不是空洞的日历故事；但也说明 edge 目前更像 **sparse pocket**，而不是一条已经证明可稳定滚动部署的全天候 schedule。
2. **当前 transfer check 维度还偏窄。**
   - 现有本地产物显示：测试期如果把最强 + 最弱桶都拼成稀疏 `1h` schedule`，只有约 `+3.29 bps/active bar`；
   - 真正厚的部分来自 `neg / hold=4h`：`129` 次事件、约 `+20.54 bps/event` gross，按 `8 bps` round-trip 粗扣后仍约 `+12.54 bps/event`。
   - 但这仍主要来自 **BTC 单资产 + Binance Spot + 单一 hold window**，还没回答它到底是“独立可部署策略”，还是“适合作为 event-clock veto / overlay 的时间袋”。
3. **论文证据级别仍偏 intake。**
   - 本轮摘要主要基于开放文章页 / RePEc 摘要 + 本地 quick check，并非完整 replication。
   - 对 fresh intake 来说，这已经足以判断“值得留在前排继续看一次”；但还不够支撑直接上 P2。

## 本轮改变了什么系统认知
- 以前：这条线可能只是普通 weekday / weekend calendar anomaly。
- 现在：更准确的说法是——**它更像 `BTC only` 的少数固定弱时段 `4h short` pocket，可作为独立 raw-alpha 候选继续验一次，但暂时不应吹成完整 schedule 母策略。**

## 建议的唯一 survivor follow-up（供下一步使用）
只做一次最小 decisive follow-up，目标不是继续讲故事，而是回答唯一关键问题：

> 这条 edge 在更诚实的 desk 口径下，仍像“可独立 paper 的 sparse scheduler”，还是应降级成其他策略的 event-clock veto / overlay？

优先检查：
1. `4/8/12 bps` 成本梯度下的稳定性；
2. rolling refresh 后弱桶是否持续存在，而不是训练窗口偶然命中；
3. Binance spot 与更贴近执行口径（perp 或更细粒度）之间是否大致同向；
4. 是否只有极少数孤立桶在赚钱，且轻微参数改动即坍塌。

若 survivor follow-up 证明它在这些口径下仍保留净后空间且不是单点脆弱袋，可升 `P2`；否则用尽 survivor 预算后移回 background。

## 关键引用数值
来自 `reports/artifacts/quant_digests/dayofweek_hourly_event_clock_20260327/`：
- `summary.json`：测试期稀疏 schedule 约 `+3.29 bps/active bar`、`53.88%` 胜率；
- `hold_grid_test.csv`：`neg, hold=4h` 约 `+20.54 bps/event` gross，`53.49%` 胜率；
- 这支持“弱时段 short pocket 存在”，但不支持直接把它写成全天稳定 schedule。
