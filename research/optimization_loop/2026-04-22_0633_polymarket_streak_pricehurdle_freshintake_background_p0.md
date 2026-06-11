# 2026-04-22 06:33 UTC — polymarket streak reversal × price hurdle fresh intake -> background/P0

## 执行动作
- 按 `BOT2_BOT3_POLICY` / `BOT2_BOT3_STATE` 执行当前 `cycle_plan` 第 1 项。
- 对象：`research/quant_digests/2026-04-22_0545_polymarket-streak-pricehurdle-binary-alpha.md`
- 只回答这条 `连续同向 K 线后的反向 binary bet × 入场价格上限` 是否足以保留为新的前排候选。

## 读到的最小证据
- digest 已给出本地 portability probe：
  - `5m ETH trigger=5`: `n=52`, `win_rate=65.38%`, `max_entry_price_for_breakeven=0.6212`
  - `5m XRP trigger=4`: `n=138`, `win_rate=65.94%`, `max_entry_price_for_breakeven=0.6264`
  - `15m SOL trigger=5`: `n=43`, `win_rate=74.42%`, `max_entry_price_for_breakeven=0.7070`
- 但同一 probe 也显示这条线并非稳定普适：
  - `5m BNB` 多个 trigger 胜率低于 `50%`
  - `5m DOGE` 全段为负
  - `15m XRP` 从 `trigger=4` 起持续失效
  - `15m BTC/BNB/DOGE` 仅在少数组合上勉强为正，厚度明显不一致

## 最小 honesty / execution realism 收口
- 当前可见证据只证明了 **Binance bar-level 的下一根反向概率**，没有证明 Polymarket / Kalshi 真实 candle market 中：
  1. 这些事件在 market open 到 settlement 前，能持续拿到 `ask <= max_entry_price - safety_margin`；
  2. 深度、成交概率、提前结算/撤单摩擦不会吃掉这条看起来不厚的 edge；
  3. 优势不是主要来自 binary payout 结构，而是可迁移到 desk 可复用的独立 short-cycle alpha。
- 决定性问题不只是“还差一点数据”，而是 **当前 strongest evidence 仍停留在 binary venue 价格纪律之前的方向层**；缺失的不是普通 survivor follow-up，而是对象成立所必需的 venue-side admission 证据。

## 结论
- 本轮 fresh intake 直接收口 `background/P0`。
- 改变系统认知的话：`连续同向 K 线后的反向 binary bet × 入场价格上限` 当前只证明了少数 `5m ETH/XRP` 与 `15m SOL` 的薄 win-rate pocket，但还没有证明真实 binary order book 能长期提供低于胜率上限的可成交 ask；因此它更像 binary/exotic market structure hint，而不是已可前排保留的独立 after-cost alpha。

## 对 runtime 的影响
- 不分配 Rank。
- 不进入 survivor / P2 / P3。
- 当前第 1 项应记为 `done`，结果为 `background/P0` 收口。

## 尾部动作
- `publish_homepage_index.sh` 已按要求独立执行，但本轮因超时被终止（非阻断尾部失败）；不影响本轮已写出的 verdict / state / log。
- 中文邮件摘要已独立发送成功。
