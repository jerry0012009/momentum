# 高频 crypto 里的 EMA 原始 alpha：裸均线信号有边，但成本一扣就容易归零
- 时间：2026-03-15 05:32 UTC
- 类型：论文
- 主题标签：trend / momentum / ema / crypto / cost / raw-alpha
- 证据类型：论文全文（open-access）

## 1. 这次看了什么
这次看的是：
- **Fenghua Wen, Jinyue Wang, George W. S. Schryen, Sha Wang, Shouyang Wang (2022)**
- **Reversal and Momentum in Moving Average Trading Rules of Cryptocurrencies**
- Venue: **Journal of Risk and Financial Management**
- DOI: **10.3390/jrfm15080336**

论文不是专门研究 EMA 一条线，而是更基础也更重要的一问：**高频 crypto 里，均线家族的“原始 alpha”到底有没有，能不能扣完成本后还活着？**

## 2. 核心结论
- **结论 1：裸均线顺势信号 pre-cost 有边，但它更像“原始 alpha 线索”，不是可直接拿去实盘的独立策略。** 作者用 **近 3 亿条 tick-by-tick 数据、11 个代表性币种、覆盖约 80% 总市值** 检验后发现：**momentum moving average rules 在原始收益上优于 contrarian moving average rules**。
- **结论 2：一旦把交易成本算进去，这条边基本会被吃掉。** 论文明确写到：**不管是 momentum 还是 contrarian 的 moving average rules，超额收益在考虑 transaction costs 后都消失。**
- **结论 3：问题不只是“参数没调好”，而是高频均线信号本身高度依赖局部自相关与成交环境。** 作者专门强调：高频收益自相关会随时间显著变化；某段时间偏顺势，另一段时间可能转成偏反转，所以固定一套均线逻辑容易失效。

## 3. 为什么和当前项目有关
这篇对当前三条收口线里，**最直接服务的是 `EMA / PSAR raw alpha focus`**。

一句话翻成人话：**EMA 这类均线结构可以继续留在系统里，但更适合当方向过滤、状态特征、trade suppression 规则，而不是急着把“裸 EMA 交叉/排序”当最终 alpha。**

这也会反过来帮助另外两条线：
- 对 `V3 breakout-short follow-up`：如果裸均线边际本来就脆，那 breakout-short 更该把 EMA 当 **regime gate**，而不是当独立入场理由。
- 对 `Fibonacci confirmation / retest_hold`：更合理的分工是 **EMA 给方向，retest / fib 给确认**，而不是让任一组件单独扛 alpha。

## 4. 可复刻的最小实验
### 研究假设
在 15m crypto 里，**EMA raw alpha 单独跑很可能成本后不稳；把 EMA 从“入场主引擎”降级成“方向过滤/不开仓条件”后，反而更可能有价值。**

### 最小对照
- 资产：BTC / ETH / SOL perpetual
- 周期：15m
- 样本：最近 180d

做三组对照：
1. **raw-EMA**：`EMA20 > EMA50` 做多，`EMA20 < EMA50` 做空
2. **EMA-as-filter**：只把 `EMA20 > EMA50` 用作方向过滤，真正触发交给现有 breakout / retest_hold 规则
3. **EMA+trade-suppression**：在第 2 组基础上，再加一条“不在低波动压缩或高噪声区交易”的简单抑制规则

### 先看哪 2 个指标
- `post_cost_return`
- `return_per_trade`

如果 raw-EMA 的 `trade_count` 很高、`return_per_trade` 很低，而 filter 组成本后明显更稳，就说明这篇论文在你这条 15m 主线里是对的。

## 5. 风险与保留意见
- 论文研究的是 **moving average rules**，不是专门只做 EMA；所以它给的是“均线家族原始 alpha”层面的约束，不是某个 EMA 参数的直接答案。
- 这是高频 crypto 证据，但不等于你的交易所、手续费、滑点、资金费率条件下一定同样成立。
- 它最值得复用的是**角色判断**：均线更像底层状态/方向特征，而不是默认独立策略。

## 6. 来源
1. Wen, F., Wang, J., Schryen, G. W. S., Wang, S., & Wang, S. (2022). *Reversal and Momentum in Moving Average Trading Rules of Cryptocurrencies*. Journal of Risk and Financial Management, 15(8), 336.
   - DOI: https://doi.org/10.3390/jrfm15080336
   - Readable URL: https://www.mdpi.com/1911-8074/15/8/336
   - PDF: https://www.mdpi.com/1911-8074/15/8/336/pdf?download=1
