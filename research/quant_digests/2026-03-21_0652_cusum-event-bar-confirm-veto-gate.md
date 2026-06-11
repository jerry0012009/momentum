# 别把 15m 的确认层固定在整根时间 bar：`CUSUM event bar` 更像 breakout-short / Fib / EMA-PSAR 的 market-activity confirm-veto gate
- 时间：2026-03-21 06:52 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/cusum/information-driven-bars/event-bar/confirm-veto/chop/regime/filter/paper/crypto/1m/15m
- 证据类型：论文证据（Financial Innovation）

## 1) 这次看了什么
这轮继续沿着 **Grądzki, Wójcik, Lessmann (2025)** 的 Financial Innovation 论文《Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning》往下挖，但**这次故意不重复讲 triple-barrier verdict**，只抽更适合当前三条收口线的另一条旁支：**别把 15m 的确认层死绑在固定时间 bar 上，而是用 `CUSUM / information-driven bar` 先问一句——市场有没有真的沿目标方向“走出一段像样的事件流”**。

## 2) 核心结论（先说人话）
- **一句话核心结论：** 对 5m/15m desk 来说，`CUSUM event bar` 更像“市场真的动起来了没”的确认层，而不是新的主 alpha。
- **一句话证明方式：** 论文用 Binance 2018-01~2023-06 tick data，比了 time bars、volume bars、dollar bars、range bars、CUSUM，再看交易后绩效；结果显示 **CUSUM 比固定 time bars 更稳定地把模型推到可交易区间**。
- 在 **ETH next-bar** 设置里，`CUSUM 2%` 年化净收益 **33.8%**、Sharpe **1.00**，`CUSUM 3%` **40.2% / 1.28**；而 `1h time bar` 是 **-51.2% / -2.22**，`12h` 也只有 **-1.2% / -0.20**。
- 在 **BTC next-bar** 设置里，`CUSUM 2%` 也仍是少数为正的组合：年化净收益 **10.2%**、Sharpe **0.43**；对应 `1h time bar` 是 **-36.6% / -2.29**。
- 论文正文还强调：**CUSUM 2% 在四个主配置里全部为正，3% 也有 3/4 为正；dollar bars 基本全线很差，volume bars 偶有亮点但不稳定。** 这更像在告诉我们：**该先过滤“有没有真实事件流”，而不是继续迷信固定 15m close。**

## 3) 为什么这轮值得优先做
它不是偏题，反而正好卡在三条收口线共同的痛点上：
1. **V3 breakout-short / follow-up**：很多假跌破不是方向错，而是跌破后没有继续形成同向事件流；
2. **Fib confirmation / retest_hold**：很多“守住”只是时间上没破，但也没有出现真正的反推事件；
3. **EMA / PSAR raw alpha**：它们现在最大问题不是“能不能再多加一个指标”，而是**信号后有没有真实 path continuation**。

所以这篇更像一个 **shared confirm-veto layer**：先不改 entry，本轮先改“什么叫真的开始走”。

## 4) 对当前项目的落地映射
最值得测的不是“把整套策略改成 event bars”，而是先做一个轻量 admission gate：
- **breakout-short**：跌破后，用 1m close 构造 directional CUSUM；若先出现 `down-event`，再保留 short；若先出现 `up-event` 或长时间不出事件，判为 veto / weak follow-up。
- **Fib retest_hold**：回踩区后，若 first event 先向反弹方向出现，再算 hold-quality 通过；否则别急着把“没破”当确认。
- **EMA / PSAR**：reclaim / pre-flip 后，只有在 latency budget 内等到同向 CUSUM event，才允许保留 raw-alpha 候选，否则更像 overlay 场景。

可把它写成统一字段：`event_confirm ∈ {same_dir_first, opp_dir_first, no_event_timeout}`。

## 5) 最小可复现实验
**数据源**：Binance USDT perpetual 1m + 15m K 线（公开可得）。

### 实验 A：只做 gate，不改原 entry
- 对象：现有 `breakout-short / fib-retest / ema-psar` baseline；
- 做法：entry 规则保持不变；入场触发后，只额外观察未来 `N=3` 根 15m（或 45 分钟）内的 1m directional CUSUM；
- 门槛：先试 `θ = {0.4, 0.6, 0.8} * ATR15m%`，不要生搬论文里的日内外层 2%/3%；
- 标签：`same_dir_first / opp_dir_first / no_event_timeout`。

### 实验 B：先看最关键的 4 个数
- `same_dir_first rate`
- `opp_dir_first rate`
- `no_event_timeout share`
- 通过 gate 后的 `post-cost expectancy`

### 实验 C：只问它有没有帮助三条线收口
- 若 breakout-short 的失败主要集中在 `opp_dir_first`，优先补 **fake-break reclaim veto**；
- 若 Fib 主要死在 `no_event_timeout`，优先补 **hold 后 continuation confirmation**，别再只看触位；
- 若 EMA/PSAR 只有少数 regime 才有 `same_dir_first` 优势，就继续把它们放在 **overlay / confirm**，而不是急着叫 raw alpha。

## 6) 风险与保留
- 论文主实验是 tick data + 深度学习，我们这里只借 **sampling / event confirmation 思路**，不是搬它的收益表。
- `CUSUM` 阈值很容易变成新自由度，所以第一轮必须盯 **参数平原**，别只报最优点。
- 事件流 gate 更像 **confirm-veto layer**，默认不该单独升格成主触发器。
- 如果 1m 数据质量或延迟处理不好，`no_event_timeout` 可能只是数据问题，不一定是真无 continuation。

## 7) 来源
1. **Grądzki, P., Wójcik, P., & Lessmann, S. (2025). _Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning_. Financial Innovation.**  
   - Authors: Przemysław Grądzki; Piotr Wójcik; Stefan Lessmann  
   - Year: 2025  
   - Title: Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning  
   - Venue: Financial Innovation  
   - DOI: <https://doi.org/10.1186/s40854-025-00866-w>  
   - Readable URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w>  
   - PDF URL: <https://link.springer.com/content/pdf/10.1186/s40854-025-00866-w.pdf>  
   - Table 2 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/2>  
   - Table 3 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/3>  
   - Table 4 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/4>  
   - Table 5 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/5>
2. **Binance Developers / Binance public market data.**  
   - Data source: Binance tick / kline market data  
   - Publicity: 公开可得  
   - Update frequency: 可到 tick / 1m 级别  
   - Readable URL: <https://data.binance.vision/>  
   - Futures Kline API URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

## 8) 下一步怎么测（一句话）
先别再给三条线堆新指标：直接把现有 15m entry 后的 45 分钟改成 `same_dir_first / opp_dir_first / no_event_timeout` 三分法，看看 **CUSUM event-confirm** 能不能先把 breakout-short 的假延续、Fib 的“假守住”、以及 EMA/PSAR 的伪 continuation 过滤掉。