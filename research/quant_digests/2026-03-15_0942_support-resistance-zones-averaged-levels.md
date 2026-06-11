# 别把 retest_hold 当成“一根线”：长窗口 + 附近价位平均后的阻力区，比短窗口单点更有效
- 时间：2026-03-15 09:42 UTC
- 类型：论文
- 主题标签：support-resistance / breakout / retest / confirmation / zone
- 证据类型：论文全文（arXiv working paper）

## 1. 这次看了什么
这次看的是：
- **Tianshu Zhang, Hao Zhou (2024)**
- **What are Effective Support and Resistance Levels? Evidence from High and Low Prices**
- Venue: **arXiv working paper**
- DOI: **10.48550/arXiv.2407.15761**

这篇很适合当前两条收口线：`V3 final-verdict / breakout-short follow-up` 和 `Fibonacci confirmation / retest_hold`。它研究的不是“有没有支撑阻力”这种老问题，而是更实用的一步：**什么样的支撑/阻力构造更有效——短窗口还是长窗口，单点还是价位带（zone）？**

## 2. 核心结论
- **结论 1：长窗口支撑阻力比短窗口更有效。** 论文用 **24 个期货合约、2000–2023** 的长样本，对比了类似 **20 日 vs 100 日** 的历史高低点构造，结论是：**long-term SR 明显优于 short-term SR**。
- **结论 2：阻力位上破，比支撑位下破更可靠。** 作者明确写到：**resistance levels are more effective than support levels**。翻成人话：**向上 breakout 的延续性，在这份样本里比向下 breakdown 更稳定。** 这对你现在的 `breakout-short follow-up` 很值钱——短侧默认就该更谨慎，不能和 long 侧用同一强度假设。
- **结论 3：把附近多个价位平均成 zone，比执着一根“精确线”更有效。** 作者发现 **averaging nearby levels significantly enhances effectiveness**，尤其是 **averaged long-term resistance** 在回测里最好。也就是说：**市场记住的更像一个阻力带，不是一根像素级价位。**
- **结论 4：突破是否靠谱，还取决于通道宽窄和趋势背景。** 文中进一步指出：**crossover probabilities and returns vary across different historical price channels and market trends**。这说明 breakout / retest 不能脱离 channel context 单独看。

## 3. 为什么和当前项目有关
一句话核心结论：**确认层更该围绕“价位带 + 背景条件”设计，而不是死守一条线。**

一句话证明方式：**作者在多资产长样本上系统比较不同 SR 构造，并用 crossover backtest 看 returns / Sharpe / consistency。**

最值得复用的点有两个：
1. **给 `Fibonacci confirmation / retest_hold`**：别把 0.382 / 0.5 / 0.618 当精确触价点，更合理的是把它们和最近 swing highs/lows 合成一个 **retest zone**。
2. **给 `breakout-short follow-up`**：既然支撑下破在外部证据里天然更弱，那 short breakout 默认就该要求更严确认，比如 **更大的离带距离、更多 bar 站稳、或失败回抽不过 zone**。

## 4. 可复刻的最小实验
### 研究假设
在 15m crypto 里，**“zone-based confirmation” 会优于 “single-line confirmation”**；而 **short-side breakout** 需要比 long-side breakout 更严格的确认阈值。

### 最小对照
- 资产：BTC / ETH / SOL perpetual
- 周期：15m
- 样本：最近 180d

### 三组先测
1. **single-line**：用单一 swing high / low 或单一 fib 位做 breakout / retest 判定
2. **zone-avg**：把最近若干相邻 swing highs（或 fib 0.382/0.5/0.618）平均成一个 zone，中枢价作为确认带中心
3. **zone+context**：在第 2 组基础上，再按 channel width / EMA trend 分层，只在窄通道压缩后或顺趋势背景下接受 breakout

### short 侧额外约束
- long：`close > zone_high + 0.05*ATR` 即可候选
- short：要求 `close < zone_low - 0.10*ATR`，且 **2-of-3 bars** 仍在 zone 下方，才算有效 break

### 先看哪 2 个指标
- `false_break_ratio`
- `post_cost_return`

## 5. 风险与保留意见
- 论文样本是 **日频期货**，不是 crypto 15m；它更像结构原则证据，不是参数可直接照搬。
- 文中当前能可靠提炼的是“构造方式谁更好”，不是某个精确阈值。
- 这篇对 short-side 的含义尤其该保守使用：它提示“下破天然更弱”，但不等于 short breakout 完全没价值，只是默认要更严筛选。

## 6. 来源
1. Zhang, T., & Zhou, H. (2024). *What are Effective Support and Resistance Levels? Evidence from High and Low Prices*. arXiv working paper.
   - DOI: https://doi.org/10.48550/arXiv.2407.15761
   - Readable URL: https://arxiv.org/abs/2407.15761
   - PDF: https://arxiv.org/pdf/2407.15761
