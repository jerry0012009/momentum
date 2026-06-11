# 2026-03-25 00:58 UTC · fresh intake · JEBISMA Bitcoin buy/sell paper → park

## 本轮执行对象
- 来源类型：paper
- 对象：**Hartsa Fayi Yumna, M. Taufiq, Anisa Fitria Utami (2024)**
- 标题：**Technical Analysis for Buy or Sell Decisions in Cryptocurrency (Bitcoin)**
- 刊物：**Jurnal Ekonomi Bisnis Manajemen Akuntansi (JEBISMA), Vol. 2 No. 2, Dec 2024**
- 本轮目标：按 `Fresh intake slot` 要求，只做 1 个最小公开证据 + 本地快检，直接回答 `park / keep_P1`。

## 最小公开证据
从论文首页/摘要可直接提炼出的公开信息：
1. 论文核心不是新公式，而是把一组传统技术分析元素并列起来：**volume confirmation、价格站上 200-day moving average、chart pattern、breakout、support/resistance、Higher High / Higher Low**。
2. 摘要明确写的是**定性结论**：作者认为 `2022-06 ~ 2023-10` 这段 BTC 图表里，这些模式给出了偏强的 **buy** 结论。
3. 方法部分也明确写成 **qualitative / content analysis**，不是带 OOS / cost / no-overlap / programmable rules 的系统化回测。

翻成人话：这篇 paper 更像“把常见技术分析多头叙事整理成一篇定性 case write-up”，不是一条已经写清楚 honest execution 口径的新 raw alpha。

## 本地最小快检
### 口径
为了不空口判死，我用现有本地公共数据缓存做了一个**最小代理**，只回答它是否至少指向某种可交易的 trend-following 骨架：

- 数据：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/perp_cache/BTCUSDT__1825d__15m__perp.csv`
- 处理：把 `15m` BTCUSDT perp 聚成 UTC 日线
- long 代理信号：
  - `close > 200D MA`
  - `close > 前 20 日高点`
  - `day volume > 20D 平均成交量`
- short 代理信号（对照看 paper 是否真能支持 sell side）：
  - `close < 200D MA`
  - `close < 前 20 日低点`
  - `day volume > 20D 平均成交量`
- 执行：`signal day close -> next day open`，no-overlap，固定看未来 `5d / 10d` signed return

### 快检结果
#### long 代理
- 样本数：`31`
- 时间范围：`2021-10-06 ~ 2025-10-01`
- `mean_5d = +1.85%`
- `hit_5d = 61.3%`
- `mean_10d = +2.04%`
- `hit_10d = 54.8%`
- 无条件基线：
  - `mean_5d = +0.28%`
  - `mean_10d = +0.57%`

#### short 代理
- 样本数：`18`
- `mean_5d = +1.00%`（signed）
- `median_5d = -1.35%`
- `hit_5d = 38.9%`
- `mean_10d = +2.80%`（signed）
- `hit_10d = 55.6%`

## 解释
这组快检说明两件事：

1. **宽泛的“200D 趋势 + 突破 + 放量”长侧骨架，在 BTC 日线并不是完全没用。**
   - 所以不能因为 paper 写得泛，就说它指向的市场现象完全不存在。

2. **但这篇 paper 本身仍然不值得进入 `keep_P1`。**
   - 它没有给出足够清晰、可程序化、可 honesty 审计的 entry/exit/spec；
   - 它主要重复的是项目里已经大量存在的 breakout / trend / confirmation 常识层；
   - 对 short / sell side 没有给出同等强度、可复现的结构；
   - 当前前排更缺的是**新的 raw alpha family** 或至少**新的可编程 spec**，而不是再收一篇“传统技术分析拼盘在 BTC 上看起来偏多”的定性论文。

换句话说：**快检证明的是 generic trend-following 现象仍在，不是这篇 paper 自己提供了新的 durable alpha identity。**

## 结论
- verdict：**park**
- Rank：**不分配**（因为没有达到 `keep_P1`）
- 对前排系统的实际影响：**不占 survivor 名额，不进入 P2；Fresh intake slot 继续保持 `ready_for_new_intake`，下一轮应直接去认领下一个更像“新 raw alpha / 新可编程 spec”的 source。**

## 会改变系统认知的一句话
**JEBISMA 2024 这篇 BTC 买卖论文最多只是在本地快检里再次证明“宽泛 breakout+200D MA+放量的长侧骨架并非失效”，但它没有贡献新的可诚实程序化 spec，因此不能算新的 fresh survivor，直接 park。**
