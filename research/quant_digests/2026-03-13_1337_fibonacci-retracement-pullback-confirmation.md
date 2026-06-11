# Pullback 不是“回就接”：Fibonacci 回撤位更像确认层，而不是单独 alpha
- 时间：2026-03-13 13:37 UTC
- 类型：论文
- 主题标签：pullback / support-resistance / confirmation / breakout / trend
- 证据类型：论文全文（open-access PDF）

## 1) 这次看了什么
这次看的是：
- **Ikhlaas Gurrib, Mohammad Nourani, Rajesh Kumar Bhaskaran (2022)**
- **Energy crypto currencies and leading U.S. energy stock prices: are Fibonacci retracements profitable?**
- Venue: **Financial Innovation**
- DOI: **10.1186/s40854-021-00311-8**

论文做的事很直接：把 Fibonacci 回撤位（23.6/38.2/50/61.8/78.6）当交易系统，和 buy-and-hold 比；再看“Fibonacci + price crossover（50-day MA）”是否更好。

## 2) 核心结论（面向当前 5m/15m 主线）
- **结论 1（最重要）**：Fibonacci 回撤位本身可以生成交易，但更像**结构确认层**，不是稳定可独立依赖的 alpha 主体。论文里虽然出现了不少高总收益个股，但整体 **Sharpe / Sharpe per trade 普遍偏低**，稳定性不足。
- **结论 2（直接对应你关心的“1~3 根确认”）**：作者明确统计了“当前回撤位被突破前，1/2/3 天内是否先突破其他位”，发现**连续回撤位突破主要集中在 1 天内**，往后（2、3 天）显著减少。这本质上支持：突破后确认窗口要短，不要无限等待。

## 3) 论文是怎么支持这些结论的
- 样本：
  - 10 只 S&P 1500 能源股（KMI/XOM/CVX/COP/...）
  - 4 个“能源相关 crypto”（SNC/POWR/GRID/TSL）
  - 日频，2017-11 到 2020-01
- 规则（Fibonacci-only）：
  - uptrend：上穿 23.6% 做多；下破 61.8% 平/反
  - downtrend：下破 23.6% 做空；上穿 61.8% 平/反
  - 期末强制平仓
- 额外规则：再叠加 50-day MA crossover
- 评估：total return、average risk、Sharpe、Sharpe per trade，并和 buy-and-hold 对照

论文中的结果要点：
- Fibonacci-only 下，很多能源股总收益为正（文中给出约 **4% 到 177%** 区间），且整体上优于若干 buy-and-hold 个体。
- 但 Sharpe 指标多数很低，说明“有收益不等于有稳定风险收益比”。
- 叠加 50-day MA crossover 后，交易次数明显减少，整体没有显著改善，部分标的几乎无交易信号。
- 对回撤位“连续突破”的统计显示：**1-day 前序突破最常见，2-day/3-day 明显变少**。

## 4) 为什么这篇对当前项目有价值
你现在重点是 crypto 5m/15m 的 **breakout / pullback / confirmation**。这篇最可迁移的是结构，不是参数：

1. **把回撤位当“确认层”而非“进场层”**
   - 先用趋势/动量给方向；
   - 再用回撤位判断“回踩是否有效”；
   - 避免“只因摸到某个位就开仓”。

2. **确认窗口应该短**
   - 论文的 1/2/3 天比较，可以映射成 15m 的 1/2/3 bar（或 2/4/6 bar）确认实验。

3. **警惕“交易次数过少导致指标失真”**
   - 论文里 crypto 部分就出现了“交易太少 + Sharpe 异常值”的问题。

## 5) 下一步怎么测（最小可执行实验）
### 目标
验证：在 15m crypto 上，Fibonacci 回撤位作为 pullback/breakout 的确认层，是否能降低假突破并改善回撤。

### 实验设计（先做最小版）
- 资产：BTC/ETH/SOL perpetual
- 周期：15m
- 方向层（固定，不在这轮优化）：`EMA50 > EMA200` 只做多，反之只做空
- 事件层：取最近 `N=48` 根（12h）局部 swing high/low，计算 23.6/38.2/50/61.8 回撤位

#### 四组对照
1. **baseline**：裸 pullback entry（触及 38.2 或 50 就入场）
2. **confirm-1bar**：触位后下一根仍站回有利方向才入场
3. **confirm-2of3**：触位后 3 根内至少 2 根收盘支持方向
4. **retest-hold**：先破位，再回踩 38.2/50 不失守才入场

### 关键指标
- `post_cost_return`
- `max_drawdown`
- `false_break_ratio`
- `time_to_invalidation`（入场后几根被打脸）

### 成功判据（先定门槛）
- 相对 baseline：
  - `false_break_ratio` 至少下降 10%
  - `max_drawdown` 至少下降 10%
  - `post_cost_return` 不显著劣化（>-5%）

## 6) 风险与保留意见
- 论文主样本是能源股 + 能源 crypto（且日频），不是主流 BTC/ETH 的 5m/15m 高频环境。
- 文中策略未做我们实盘需要的完整成本建模（手续费/滑点/资金费率）。
- 某些标的收益和 Sharpe 有异常值，核心原因是**交易太少**与期末强制平仓导致指标不稳。
- 因此最安全的用法是：**吸收“确认层结构”与“短窗口确认”思想，不照搬参数。**

## 7) 来源
1. Gurrib, I., Nourani, M., & Bhaskaran, R. K. (2022). *Energy crypto currencies and leading U.S. energy stock prices: are Fibonacci retracements profitable?* Financial Innovation, 8, 8.
   - DOI: https://doi.org/10.1186/s40854-021-00311-8
   - Readable URL: https://jfin-swufe.springeropen.com/articles/10.1186/s40854-021-00311-8
   - PDF: https://link.springer.com/content/pdf/10.1186/s40854-021-00311-8.pdf
