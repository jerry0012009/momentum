# Rank 263 / skip-last-bar 8h~16h XS momentum — fresh intake 首判（keep_P1）

- 时间：2026-03-30 22:34 UTC
- 执行者：bot3 13 分钟自动执行
- 对应 cycle_plan 小点：`skip-last-bar 的 8h~16h XS momentum`
- Source digest: `research/quant_digests/2026-03-30_2055_skip-lastbar-xs-momentum-alpha.md`
- Object: `skip-last-bar 8h~16h XS momentum`
- Verdict: `keep_P1`
- Assigned rank: `Rank 263`

## 本轮回答的唯一问题
这条对象是否已经足够说明它是独立、完整、值得继续前排推进的 raw alpha skeleton，还是说它本质仍只是 7 币窄样本上的 repo 教学现象，不值得进入 survivor？

本轮结论是：**它已经足够构成独立对象，因此分配 `Rank 263` 并记为 `keep_P1`；但还不够直接升 `P2`。**

## 为什么它值得进入前排，而不是直接回 background
1. **主语是清楚且可独立复现的。**
   这条对象不是泛“4h reversal vs momentum”综述，而是明确的：
   - 跳过最近 1 根 `4h` bar；
   - 用更早 `8h~16h` 横截面强弱做 `rank → demean → normalize` 多空；
   - 持有下一段 `4h`；
   - 依赖的是 recent-bar exclusion 之后留下来的 continuation pocket。

2. **entry / exit / sizing / cost 骨架已经齐了。**
   digest 已经把它写成完整策略骨架：
   - `entry`: `skip-last-bar` 后按更早 `8h/12h/16h` 收益做横截面排序；
   - `exit`: 默认持有下一段 `4h` 后全部平掉；
   - `sizing`: rank-demeaned-normalized，截面净敞口接近 0；
   - `cost`: 已给出 turnover 对应的粗略 break-even one-way cost（约 `3.4~4.4 bps`）。
   它已经超过“概念现象”，足够成为独立 raw alpha 候选。

3. **它提供的是对现有 XS momentum 家族有区分度的实现细节。**
   真正值钱的不是“更长动量更好”，而是 **recent 1 bar 往往承载 reversal contamination，剥掉之后 `8h~16h` 才更像 continuation pocket**。这和泛 stale-return/简单动量卡不是同一个命题。

## 为什么本轮不能直接升 P2
1. **当前样本仍然过窄。**
   公开复跑只覆盖 `BTC/ETH/ADA/BNB/XRP/DOT/MATIC` 这 7 个币，且是 spot-like 公共数据口径；这足以证明 skeleton 存在，但还不足以证明放到 desk 可承载 universe 后仍稳健。

2. **成本包络只是“值得继续问”，不是 admission 证据。**
   digest 给出的 `8h/12h/16h` 粗略 break-even one-way cost 约 `3.4 / 3.8 / 4.4 bps`，说明它不是一上成本就立刻归零的玩具；但这仍只是窄 universe + repo 复跑层的一阶估计，没把 perp funding、真实流动性过滤、maker/taker 混合、recent-shock veto 后的触发密度讲清楚。

3. **真正决定能否进 P2 的问题仍没回答。**
   对 desk 来说，关键不是 repo 本身是否成立，而是：
   > 当 universe 切到 `Binance / OKX / Bybit` 可承载的 perp / liquid-major，并显式扣 turnover 成本与 recent-shock veto 后，这条 skip-last-bar XS momentum 是否还保留可重复的成本后 pocket？

因此最诚实的首判是：**先 `keep_P1`，并把唯一 survivor follow-up 用在 `perp / liquid-major` transfer 上，而不是直接升 `P2`。**

## 改变系统认知的一句话
**Rank 263 / skip-last-bar 8h~16h XS momentum 首判为 `keep_P1`：这不是泛 momentum 教学图，而是一条“剥掉最近 1 根 4h 反转污染后再交易更早横截面强弱”的独立 raw alpha skeleton；但当前证据仍停在 7 币 spot-like 样本与粗略几 bps 成本包络，尚不足以直接进入 `P2 admission`。**

## 留给 survivor 的唯一问题
只回答这一句：

> 当 universe 收缩到 `Binance / OKX / Bybit` 可承载的 perp / liquid-major，并显式加入流动性过滤、recent-shock veto、`0/2/4/6 bps` 成本档后，`skip-last-bar + earlier 8h~16h XS strength` 是否仍保留足够触发密度与成本后边际？

如果答案是肯定的，下一步应 `promote_P2`；如果 edge 主要只存在于窄 spot-like 样本，换到 desk-feasible universe 后明显塌缩，就应在 survivor 轮后直接回 `background/P0`。
