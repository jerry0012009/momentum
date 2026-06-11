# 别先问 EMA 哪组最赚，先问它怎么亏：1m BTC 里，裸 MA 能赢 Sharpe，但保护性阈值层更擅长压回撤
- 时间：2026-03-15 21:46 UTC
- 类型：论文
- 主题标签：ema / drawdown / confirmation / btc / intraday
- 证据类型：论文全文（期刊页全文可读）

## 1. 这次看了什么
这次看的是：
- **Paolo De Angelis, Roberto De Marchis, Mario Marino, Antonio Luciano Martire, Immacolata Oliva (2021)**
- **Betting on bitcoin: a profitable trading between directional and shielding strategies**
- Venue: **Decisions in Economics and Finance**
- DOI: **10.1007/s10203-021-00324-z**

这篇最值得当前项目吸收的，不是它那个 Kim barrier 交易框架本身，而是它给了一个非常实用的评估提醒：**短线 crypto 里，裸方向信号未必输，但保护性阈值层往往更擅长“少亏一点”。**

## 2. 核心结论
- **结论 1：裸 MA 在短预测窗里可以拿到更高 Sharpe，但不代表它就是更好的交易骨架。** 论文用 **2019 年 BTC 1 分钟数据、共 483,826 条观测** 做实验，对比了作者的保护性边界策略、MA 规则、MACD 和随机振荡器。作者明确写到：在 **60 分钟和 90 分钟** 预测里，**MA(10)** 给出最高 Sharpe；在 **120 分钟** 预测里，**MA(120)** 最好。作者解释得也很直白：MA 阈值会更贴着预测路径走，所以平均回报更容易被做高。
- **结论 2：但如果你把“怎么亏”也算进去，结论就不一样了。** 文中同时强调：**their proposal always ensures the lowest loss, highlighting its safeguarding role**。也就是：作者的保护性边界策略虽然不一定把收益推到最高，但**最大回撤（MDD）始终最低**。
- **结论 3：短线里，confirmation / threshold layer 有没有价值，不能只看收益，要看它是否真的买到了“亏损压缩”。** 论文最后给的判断不是“我们每项都赢”，而是：**把 MDD 与 WR（win ratio）放在一起看，他们的策略是成功且有前景的。** 这句话翻成人话就是：**如果你加了一层确认/阈值，结果只是把交易变少、收益变低，却没有明显压住回撤，那这层确认就不值钱。**
- **结论 4：不同 horizon 下，风险偏好会改变你对策略的判断。** 文中写得很清楚：在 **90 分钟** 预测里，作者策略和 MACD 都给出负收益，风险偏好更强的投资者可能会转向随机振荡器；但在 **120 分钟** 预测里，尽管作者策略的 Sharpe 不占优，它在**控制 losses** 上依然“outstanding”。

## 3. 为什么和当前项目有关
一句话核心结论：**对 `EMA / PSAR raw alpha focus` 来说，下一步不是继续只比收益，而是把“回撤压缩效率”升格为一等指标。**

一句话证明方式：**同一份 1m BTC 实验里，裸 MA 可以赢 Sharpe，但保护性边界策略持续赢 MDD；论文最终把“低损失 + 还不错的 WR”当作核心卖点。**

它对三条收口线的帮助分别是：
1. **`EMA / PSAR raw alpha focus`**：别只比哪组 EMA 参数更赚钱，也要比哪组在成本后更能压 MDD。
2. **`Fibonacci confirmation / retest_hold`**：确认层的价值，不是“让图更好看”，而是**是否真的减少深亏与假触发**。
3. **`V3 breakout-short follow-up`**：short-side 策略尤其不该只看收益尖峰，更该优先审计最大回撤和 win ratio 的变化。

## 4. 可复刻的最小实验
### 研究假设
在 15m crypto 里，**裸 EMA 方向规则可能在收益上不差，但“带轻量保护层”的版本更可能在 MDD 上明显更稳。**

### 最小对照
- 资产：BTC / ETH / SOL perpetual
- 周期：15m
- 样本：最近 180d

做三组：
1. **raw-EMA**：`EMA20 > EMA50` 做多，`EMA20 < EMA50` 做空
2. **EMA+threshold**：在第 1 组上，加 `distance_to_EMA50 > x * ATR` 才允许触发
3. **EMA+retest_hold**：在第 1 组上，只接受“离开均线带后回踩不失守”的入场

### 先看哪 3 个指标
- `post_cost_return`
- `max_drawdown`
- `win_ratio`

### 判断口径
如果第 2 / 3 组只是让收益下降，却**没有显著改善 MDD 或 WR**，那确认层就不值得留；
如果收益少掉一点，但 **MDD 明显下降、WR 不恶化**，那它才像“保护性确认层”，值得保留。

## 5. 风险与保留意见
- 这篇研究的是 **2019 年 BTC 1m**，而不是你当前的 15m 多资产框架；迁移的是**评估逻辑**，不是参数。
- 作者明确说明：**没有考虑 CfD 的 transition / financial costs**，所以不能把它的收益比较直接拿来当真实净值结论。
- 它最值得复用的不是策略细节，而是一个筛选准则：**别只问 alpha 高不高，也要问它亏损形状好不好。**

## 6. 来源
1. De Angelis, P., De Marchis, R., Marino, M., Martire, A. L., & Oliva, I. (2021). *Betting on bitcoin: a profitable trading between directional and shielding strategies*. Decisions in Economics and Finance.
   - DOI: https://doi.org/10.1007/s10203-021-00324-z
   - Readable URL: https://link.springer.com/article/10.1007/s10203-021-00324-z
