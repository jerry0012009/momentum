# 2026-04-09 21:03 UTC — fresh intake first verdict：kimchi premium hedged handoff shell -> background / P0

## 本轮执行对象
- target: `research/quant_digests/2026-04-09_0144_kimchi-premium-hedged-handoff-shell.md`
- action: 判断 `negative KRW premium accumulation × positive-premium handoff exit` 是否已足够压成一个 desk 可执行的 cross-market delta-neutral pocket，并检查收益是否主要来自 premium 回归而不是币价方向、韩国法币通道/对冲腿/提转与 funding 成本是否构成单一 decisive execution blocker

## 读到的最关键源码/材料
1. digest 本身已经把 repo 的核心壳拆出来：
   - `premium_calculator.py` 用 `KRW ask / USDTKRW / offshore perp bid` 计算韩盘 premium
   - `hedge_bot.py` 在 `premium <= -2%` 时做 `KRW spot long + offshore perp short`
   - `settings.py` 给出 `MAX_POSITION_USD=3000`、`POSITION_INCREMENT_USD=30`、分档 `PROFIT_STAGES`
2. 进一步回读 repo raw 文件后，结论更清楚：
   - `premium_calculator.py` 的 alpha 指标确实是同币种韩盘现货对离岸永续的相对价差，不是方向预测
   - `hedge_bot.py` 的持仓管理也确实是按 premium 阈值建仓/止盈，不是只写了监控
   - 但 README 的真正兑现路径写得很明白：要靠 **韩国交易所上架/入出金可用后，把现货转进韩国腿卖出，同时同步平掉海外空单** 来吃到韩盘 premium

## 最小诚实判断
### 1) 这条线的 raw alpha 是真的存在吗？
是，repo 的 raw alpha 不是“普通 basis 壳”，而是 **韩盘相对离岸的负 premium/低 premium 事件，后续向中性或正 premium 修复**。

### 2) 收益主要来自 premium 回归而不是币价方向吗？
在模型定义里是。因为 repo 明确要求 `spot long + perp short`，方向暴露理论上被对冲掉，留下的是同币种跨市场相对价差的修复。

### 3) 当前 first verdict 为什么不能给 `keep_P1`？
因为这条线的兑现并不只是“public-data 可观测 + offshore 可交易”这么简单；它高度依赖 **韩国法币/本地账户/提转状态/上币与入出金恢复窗口** 这些执行现实。

更具体地说，当前唯一会直接压死 desk 可执行性的 blocker 是：
- repo 的 profit realization 不是在同一离岸 venue 内完成的，而是要把现货腿真正带到韩国腿去卖出，或者至少要拥有可稳定操作的韩国本地法币通道；
- 若没有这个通道，`negative KRW premium accumulation` 只能变成“看见韩国相对便宜”，却无法诚实地把 `positive-premium handoff exit` 兑现成已实现 PnL；
- 这不是普通 fee 微调，也不是还能靠一次便宜 follow-up 补掉的小缺口，而是策略成立条件本身的一部分。

### 4) 这是不是已被现有 family 吸收？
没有完全被普通 `spot-perp basis` family 吸收，因为它的关键 edge 确实来自 **KRW 本地市场与离岸永续之间的 segmented premium**。但它也还没成熟到值得保留前排，因为决定成败的不是“premium 会不会回归”，而是“desk 是否真的拥有韩国兑现通道”。

## 本轮硬结论
**first verdict = `background / P0`，理由不是 alpha 不存在，而是 `positive-premium handoff exit` 依赖韩国法币/提转/本地账户通道，这在当前 intake 口径下构成单一 decisive execution blocker；因此它暂时不是一个可在 desk 侧诚实宣称可执行的独立 pocket。**

## 对 runtime 的直接影响
- 本条 fresh intake 不分配 Rank
- `cycle_plan` 当前小点应写为 `done`
- `Fresh intake slot` 应把最新结论写成：kimchi premium handoff shell 因韩国兑现通道这个单一 execution blocker 回到 `background / P0`
- 后续 fresh intake 顺位自然切到下一条 pending（`2026-04-09_0041_hyperliquid-xs-funding-carry-persistence-alpha.md`）

## 为什么这一步足够收口
这轮需要回答的不是“有没有更多数据能让故事更好看”，而是“有没有一个唯一、便宜、会改变结论的 blocker”。答案已经有了：
- 如果没有韩国本地可持续兑现路径，这条线就不是 desk-ready pocket；
- 如果未来用户明确提供韩国账户/法币/提转能力，才值得 reopen，而不是现在继续占前排预算。
