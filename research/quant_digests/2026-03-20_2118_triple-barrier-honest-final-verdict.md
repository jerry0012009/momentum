# 别把 15m 的 follow-up verdict 固定成“入场后 N 根涨跌”：`triple barrier` 更像 breakout-short / Fib / EMA-PSAR 的 honest final-verdict 层
- 时间：2026-03-20 21:18 UTC
- 类型：论文 + GitHub 仓库
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/triple-barrier/final-verdict/follow-up/time-barrier/pt-sl/labeling/event-driven/paper/repo/crypto/5m/15m
- 证据类型：论文证据（Financial Innovation）+ 工程证据（开源标签仓库）

## 1) 这次看了什么
这轮主看 **Grądzki, Wójcik, Lessmann (2025)** 的 Financial Innovation 论文《Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning》，再补一个可直接落地的开源实现仓库 `mchiuminatto/triple_barrier`。我这次**不认领论文 headline 的 DL alpha**，只抽一个更适合我们 desk 的旁支：**把 breakout / retest / EMA-PSAR 信号的“后续是否成立”改写成 `止盈 / 止损 / 时间` 三重边界判决，而不是死盯固定 N 根 15m bar 的涨跌。**

## 2) 核心结论（先说人话）
- **一句话核心结论：** 对 5m/15m 来说，`final-verdict` 更该问“先撞到 TP、SL，还是先超时”，而不是“第 3 根/第 4 根 K 线收哪儿”。
- **一句话证明方式：** 论文用 Binance 2018-01 到 2023-06 的 tick data，比了 time bars / volume bars / dollar bars / range bars / CUSUM，再比 `next-bar labeling` 与 `triple barrier`；结果显示 **Triple Barrier 明显比 next-bar 更像真实交易判决**。
- ETH 上，**CUSUM 2% + Triple Barrier** 的年化净收益 **91.6%**、Sharpe **1.42**，而 **CUSUM 2% + next-bar** 只有 **33.8%**、Sharpe **1.00**。
- BTC 上，同样是 **CUSUM 2%**，`Triple Barrier` 年化净收益 **20.4%**、Sharpe **0.51**，而 `next-bar` 是 **10.2%**、Sharpe **0.43**；改善没 ETH 大，但方向一致。
- 论文还给了一个很重要的 desk 提醒：**参数要按资产调**。MATIC 用 `CUSUM 2.5% + TB 5~6%` 可到 **129%~130%** 年化净收益；LINK 要放大到 `TB 8%` 才明显更顺。

## 3) 为什么这轮比继续乱开新题更值得做
它直接服务三条收口线里最需要“判后续”的那部分：
1. **V3 breakout-short final-verdict / follow-up**：最直接，能把“跌破后到底是续跌、止损、还是超时无效”写清楚；
2. **Fib retest_hold**：能把“守住”从一句主观描述，改成先到 TP 还是先失守 SL；
3. **EMA / PSAR raw alpha**：即使它们暂时更像 overlay，也需要一个统一的 post-entry honest verdict 层来判断是否真有 alpha，而不是只看几根 bar 后表面浮盈。

## 4) 对当前项目的落地映射
先把三条 baseline 的 entry 保持不变，只改 verdict：
- **时间边界**：`T ∈ {4, 8, 12}` 根 15m bar；
- **止损边界**：用入场时 ATR 或结构位，先试 `SL = 0.75~1.0 ATR`；
- **止盈边界**：先试 `TP = 1.0~1.5 ATR`，或保持与当前策略目标位一致；
- **标签**：`tp_first / sl_first / timeout`，并记录触发时间与触发原因。

映射建议：
- **breakout-short**：看 `sl_first` 是否主要来自“假跌破后快速收回”；若是，就能直接反推 veto/filter；
- **Fib retest_hold**：看 `timeout` 是否高发；若高，说明很多“守住”其实只是没死但也没走；
- **EMA/PSAR**：看 `tp_first` 是否只在某些 regime 才集中出现，否则别急着叫 raw alpha。

## 5) 最小可复现实验（只用公开 OHLCV 就能先做）
**数据源**：Binance USDT perpetual 5m/15m OHLCV（公开可得）；先不强依赖 tick。

### 实验 A：先把 verdict 改 honest
- 对象：现有 `breakout-short / fib-retest / ema-psar` 三条 baseline；
- 做法：保留原 entry，不改信号，只把结果标签从 `n-bar forward return` 改成 `tp/sl/timeout`；
- 先看指标：`tp_first rate`、`sl_first rate`、`timeout share`、`post-cost expectancy`。

### 实验 B：专门看 breakout-short follow-up
- 把 `timeout` 再细分成：`timeout_above_break`、`timeout_below_break`；
- 若很多失败单其实不是先止损，而是长时间不继续跌，那 V3 更该优化 **follow-up / time veto**，而不是继续堆方向因子。

### 实验 C：再上 event-driven 版
- 只有当实验 A 证明 triple-barrier 有信息量，才追加第二层：
- 对 breakout impulse 段做轻量 `CUSUM` 重采样，比较 `time-bar verdict` vs `event-bar verdict`；
- 若 event-bar 版更稳，再考虑升成 shared verdict harness。

## 6) 风险与保留
- 论文主实验是 tick 级 + DL + CUSUM，我们这里只借它的**判决框架**，不是直接搬收益数。  
- `TP/SL/T` 本身也会引入参数自由度，所以第一轮必须盯 **参数平原**，别只报最佳点。  
- 若 `timeout` 很多，不一定说明信号坏，也可能说明当前 TP 太贪；所以要联看 `MFE/MAE`。  
- 工程上，Triple Barrier 更像**研究与评估层**，不是自动等于 live execution 逻辑；别混为一谈。

## 7) 来源
1. **Grądzki, P., Wójcik, P., & Lessmann, S. (2025). _Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning_. Financial Innovation.**  
   - Authors: Przemysław Grądzki; Piotr Wójcik; Stefan Lessmann  
   - Year: 2025  
   - Title: Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning  
   - Venue: Financial Innovation  
   - DOI: <https://doi.org/10.1186/s40854-025-00866-w>  
   - Readable URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w>  
   - Table 4 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/4>  
   - Table 5 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/5>  
   - Table 7 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/7>
2. **mchiuminatto. _triple_barrier_. GitHub Repository.**  
   - Author/Org: GitHub user `mchiuminatto`  
   - Title: triple_barrier  
   - Venue: GitHub  
   - Readable URL: <https://github.com/mchiuminatto/triple_barrier>  
   - Repo URL: <https://github.com/mchiuminatto/triple_barrier>
3. **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data.**  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

## 8) 下一步怎么测（一句话）
先别再争“breakout-short 到底看后 3 根还是后 6 根”，直接把三条 baseline 全改成 `TP/SL/T` verdict 统计；如果 breakout-short 的改写后 `timeout share` 特别高，就优先把 V3 资源继续砸在 `follow-up / time veto`，而不是再加新方向因子。