# Mt.Gox 交易级证据：先做“形态完成 + 颈线确认”，再谈 breakout continuation（对 breakout-short / retest_hold 的启发）
- 时间：2026-03-17 06:40 UTC
- 类型：论文
- 主题标签：breakout-short/confirmation/retest-hold/pullback/intraday/crypto
- 证据类型：论文证据（期刊全文可读，交易级数据）
- 证据强度提示：**中等偏强（真实交易数据强，但样本为早期 Mt.Gox，非现代永续合约）**

## 1. 这次看了什么
这次看的是：
- **Kevin Rink (2025)**
- **The role of technical chart patterns in the early Bitcoin market: intraday evidence from the Mt.Gox transaction dataset**
- Venue: **Financial Innovation**
- DOI: **10.1186/s40854-025-00763-2**
- Readable URL: https://link.springer.com/article/10.1186/s40854-025-00763-2

这篇不是“拿 OHLC 回测”的常见论文，而是直接用 Mt.Gox 的**交易级数据**看：技术形态信号出现时，真实交易行为和收益到底有没有变化。

## 2. 核心结论
- **一句话核心结论**：在早期 BTC 日内市场里，“形态完成后再做颈线确认”的信号，确实对应了更强的交易拥挤与更高的短持有收益，说明确认层不是装饰，而是实用门槛。
- **一句话证明方式**：作者基于约 **144 万笔交易 / 45,625 名交易者**（2011-04 至 2013-09），用 Lo et al. 的可编程形态识别（平滑 + extrema + 颈线突破）并做事件窗与回归检验，比较 signal vs non-signal 的成交与回报差异。
- 关键数据点（可直接记）：
  1) 买入信号附近，平均异常买卖量差约 **+0.53**；卖出信号约 **-0.61**（事件窗 ±6 小时）。
  2) 全样本里，signal trade 的日均 roundtrip return 约 **3.86%**，non-signal 约 **1.12%**。
  3) 控制变量后，signal trade 日均回报仍高约 **+3.07 个百分点**（显著）。

## 3. 为什么和当前项目有关（优先服务三条收口线）
这篇最直接服务的是：
1. **V3 breakout-short follow-up**：它支持“先确认再交易”的方向，但也提醒你——Mt.Gox 当时不能做系统化做空，**不能把 bearish volume 直接当 short alpha 证据**；short 侧仍应高门槛（continuation/failure 需额外 gate）。
2. **Fibonacci confirmation / retest_hold**：论文的“形态完成 + 颈线突破确认”与我们的 retest_hold 本质一致：**先等确认，再判断是否继续**。
3. **EMA / PSAR raw alpha focus**：更像角色分工证据——EMA/PSAR适合做状态过滤，形态/颈线更像触发与确认，不宜混成一个“万能主信号”。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
在 15m crypto 上，给 breakout 增加“颈线确认窗口”后，能降低 failure rate，并改善成本后收益质量；short 侧改善更依赖额外门控。

### 一个可计算定义
- 先做简化形态引擎：rolling extrema（可先不用完整 Lo 五形态，先做双底/矩形底近似）。
- 触发条件：
  - `pattern_complete = 1`
  - `neckline_break = close > neckline`（short 镜像）
  - `confirm = 未来12根里至少2根收盘保持在颈线外`（2-of-12，可做灵敏度）

### 最小回测切口
- 标的：BTC/ETH/SOL perpetual
- 周期：15m
- 样本：最近 180d
- 对照：
  1) 裸 breakout
  2) breakout + neckline confirm
  3) breakout + neckline confirm + retest_hold（回踩不破再进）
  4) short 侧再叠加 EMA gate（如 EMA50<EMA200）

### 先看 2~3 个指标
- `false_break_ratio`（突破后 X 根内回区间）
- `post_cost_return`
- `time_to_failure`（被打脸速度）

## 5. 风险与保留意见
- 样本是**早期 Mt.Gox**，市场结构、流动性、参与者构成都与今天永续市场不同。
- 论文强调的是“信号期交易行为与收益差异”，不是直接给出现代可部署参数。
- bearish 结果更多体现卖压与行为，不等于现代可稳定做空收益。

## 6. 来源
1. Rink, K. (2025). *The role of technical chart patterns in the early Bitcoin market: intraday evidence from the Mt.Gox transaction dataset*. Financial Innovation, 11(1), 106.
   - DOI: https://doi.org/10.1186/s40854-025-00763-2
   - Readable URL: https://link.springer.com/article/10.1186/s40854-025-00763-2
2. Lo, A. W., Mamaysky, H., & Wang, J. (2000). *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*. NBER Working Paper.
   - DOI: https://doi.org/10.3386/w7613
   - Readable URL: https://www.nber.org/papers/w7613
