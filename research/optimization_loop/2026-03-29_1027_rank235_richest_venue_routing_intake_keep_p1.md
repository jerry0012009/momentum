# Rank 235 / richest-venue routing × hysteresis funding carry — fresh intake 首判（keep_P1）

- 时间：2026-03-29 10:27 UTC
- 执行者：bot3 auto 13m loop
- Source digest: `research/quant_digests/2026-03-29_0939_richest-venue-routing-hysteresis-carry-alpha.md`
- Object: `richest-venue routing × hysteresis funding carry`
- Verdict: `keep_P1`
- Assigned rank: `Rank 235`

## 本轮回答的唯一问题
这条对象是否真的提供了区别于泛泛 funding/carry filter 的完整 raw alpha 骨架，而且 alpha 核心是否真来自 `richest-venue routing`，而不是 repo headline 换皮？

本轮结论是：**是，但还只够 `keep_P1`，不够直接升 `P2`。**

## 为什么它不是旧 funding/carry 线的换皮
和当前已收口的几条近邻对象相比，这条线有一条明确且可检验的“新主轴”：

1. **它的核心不是“哪里 carry 大就去哪里”，而是 `先 route 到 richest venue，再用 anomaly + hysteresis 把 carry 兑现出来`。**
   digest 里最关键的不是 funding 数值本身，而是 repo 明确给了三层完整策略骨架：
   - `best_exch = argmax(funding across venues)`
   - `best_fr_z > z_entry` 才入场
   - `z_exit = 0 + min_hold = 24h` 才退出
   这已经不是泛泛 filter，而是完整的 entry / exit / hold / turnover 控制规则。

2. **它和 `Rank 184 / cross-venue cheapest-spot-richest-perp contango carry` 不同。**
   `Rank 184` 的 exact object 是 `long cheapest spot / short richest perp` 的 fee-adjusted contango spread 收敛；它的 blocker 是公开快照下 fee-adjusted spread 长期为负。
   这条新对象的 exact object 则是 **同一 spot 对冲腿固定后，比较 `Binance-only` 与 `richest-funding venue routing` 的净 carry 翻转**，主问题不再是 cheapest-spot rich-perp 的静态净价差，而是 **route 选择 + hysteresis hold 是否把 fee-negative carry 变成 fee-positive carry**。

3. **它和 `Rank 168 / venue-tier-duration-gated funding carry` 也不同。**
   `Rank 168` 保留的是“只有在 venue tier + duration gate 下才可能勉强成立”的窄版 carry skeleton；但那条线并没有把 `richest venue routing` 证明成 alpha 主体，只是把 spread 厚薄与持续时长当 survivorship 条件。
   这份新 digest 给出的结构性证据更强：repo 直接并排了 `Binance-only` 和 `cross-exchange`，而且 headline 的符号翻转正是由 **richest venue routing** 带来的，不是只靠“多 hold 一会儿”或“多加一个 gate”。

## 为什么本轮只能 keep_P1，不能直接升 P2
尽管结构上足够 distinct，但当前证据还不够把它推到 admission：

1. **repo headline 数字版本不一致。**
   digest 已明确记录，不同 notebook 里有 `Net CAGR 5.76% / 13.9% / 28.1%` 等不一致口径；因此现在最可信的是“方向性翻转和结构性因果”，不是可直接拿来 admission 的稳定收益数字。

2. **当前还缺一轮最小 clean follow-up，把 routing 与 hysteresis 的增量拆干净。**
   现在知道 `Binance-only` vs `cross-exchange` 有翻转，也知道 `min_hold` 是为对抗 fee drag；但还没用同一成本口径把三条手臂并排拆成：
   - A: `Binance-only`
   - B: `richest-venue routing, no hysteresis`
   - C: `richest-venue routing + hysteresis`
   若没有这一步，还不能诚实回答“净边到底主要来自 routing，还是来自延长持有减少 churn”。

3. **它目前更像一条很清楚的 P1 exact object，而不是已经够 admission 的 P2。**
   当前最诚实的动作，是保留这条 distinct skeleton，并把 survivor 的唯一 follow-up 预算留给一次最小 decisive split test，而不是直接把 repo headline 当 admission 证据。

## 改变系统认知的一句话
**Rank 235 / richest-venue routing × hysteresis funding carry 首判为 `keep_P1`：应保留的不是泛泛 funding carry，而是 `route 到 richest funding venue + anomaly z-score entry + hysteresis/min-hold exit` 这条会把单 venue fee-negative carry 翻成 cross-venue fee-positive carry 的 exact raw alpha。**

## 下一步（留给 survivor 唯一 follow-up）
只回答一个问题：

> 在统一成本与执行口径下，把 `Binance-only`、`richest-venue routing without hysteresis`、`richest-venue routing + hysteresis` 三条手臂并排后，净边的独立增量究竟主要来自 `richest-venue routing`，还是其实只是 `min_hold/hysteresis` 在减少 churn？

如果 routing 本身不能留下独立增量，就应在 survivor 轮后诚实收口，不再占前排。 
