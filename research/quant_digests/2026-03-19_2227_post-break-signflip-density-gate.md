# 别把 breakout 后“走得很顺”当成默认 continuation：`post-break sign-flip density` 更像 15m 的 hold-quality 读数
- 时间：2026-03-19 22:27 UTC
- 类型：论文 + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/post-break-path/sign-flip-density/continuation/failure/filter/paper/crypto/15m
- 证据类型：论文证据 + 公开行情代理快检

## 1. 这次看了什么
主参考是 **Jiang, Kelly, Xiu (2023)《(Re-)Imag(in)ing Price Trends》**：它的启发不是“再加一个指标”，而是提醒我们**路径形状本身就是信息**。这轮我把它翻成一个可快速复现的 15m 代理读数：`post-break sign-flip density`（突破后短路径里的方向切换密度）。

## 2. 核心结论
- **一句话核心结论**：在 15m breakout 里，“很顺滑（0~1 次方向切换）”并不天然更好；它在当前口径下反而更容易出现**8-bar 维度回吐**，不适合被当作默认 continuation 放行条件。
- **一句话证明方式**：用 Binance 公开 15m 数据（BTC/ETH/SOL，近 120 天）做统一 breakout 事件抽样后，按突破后 6 根的 `flip_count` 分桶，比较各桶的 continuation 命中、回到 broken level 比率和 8-bar 方向收益。

关键数据（样本 `N=1,940`）：
1. `high_flip(>=3)` 占比 **57.2%**，`low_flip(0~1)` 仅 **14.1%**（“超顺滑路径”本来就稀缺）。
2. `mean_ret8`：
   - `low_flip(0~1)`：**-0.062%**
   - `mid_flip(2)`：**+0.029%**
   - `high_flip(>=3)`：**+0.083%**
3. long 侧更明显：
   - `cont_hit_0.5ATR@8bars`：`low_flip` **63.7%** vs `high_flip` **78.2%**
   - `mean_ret8`：`low_flip` **-0.091%** vs `high_flip` **+0.002%**

翻成人话：我们过去直觉里“突破后越单边越健康”，在这组 15m 代理里并不成立；至少在 long continuation 上，**过于顺滑更像脆弱延续，不像可放心持有的延续**。

## 3. 为什么和当前项目有关
- **V3 final-verdict / breakout-short follow-up**：可把 `flip_density` 放到 follow-up 阶段做“持有质量读数”，而不是入场瞬间二元开关。
- **Fibonacci confirmation / retest_hold**：若 pre-retest 路径过顺且 `mean_ret8` 历史偏弱，可降低“摸位即确认”的权重，优先等二次确认。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续负责方向；`flip_density` 更适合做 post-break 管理层（减仓/缩持仓窗口/提高 re-test 确认阈值）。

## 4. 可复刻的最小实验
### 4.1 数据源与公开性
- 数据源：Binance USDⓈ-M Futures Kline（公开 API）
- 公开性：公开可得
- 更新频率：15m（可下沉到 5m 执行）

### 4.2 最小定义
- breakout：`close` 突破 `prev_high_20/prev_low_20`，且 `body_ratio>=0.40`、`extension>=0.20 ATR`
- `flip_count`：突破后 6 根 direction-adjusted return 的符号切换次数
- 分桶：`low(0~1)` / `mid(2)` / `high(>=3)`
- 评估：`cont_hit_0.5ATR@8bars`、`fail_back_inside@8bars`、`mean_ret8`

### 4.3 下一步怎么测
做一个很小的 A/B：
1. A 组（baseline）：现有 breakout/Fib/EMA-PSAR 规则；
2. B 组（overlay）：仅在 `flip_count in {2,3+}` 保持原持仓窗口；`flip_count<=1` 时缩短持仓或提高 retest 二次确认；
3. 先看三项：`post_cost_expectancy`、`false-follow-through rate`、`tail loss(5%)`。

## 5. 风险与保留意见
- 这轮是代理实验，不是完整策略 OOS；结论是“路径读数可用性”，不是“单因子已可交易”。
- `flip_count` 与波动水平、交易时段可能强相关，需与 session/regime 一起看，避免把时段效应误当形状效应。
- 结果显示 short 侧与 long 侧反应不完全对称，后续必须分侧建模。

## 6. 产物与留痕
- 事件明细：`reports/artifacts/quant_digests/post_break_signflip_density_proxy/event_log.csv`
- 分桶摘要：`reports/artifacts/quant_digests/post_break_signflip_density_proxy/bucket_summary.csv`
- 侧向摘要：`reports/artifacts/quant_digests/post_break_signflip_density_proxy/side_bucket_summary.csv`
- 快照：`reports/artifacts/quant_digests/post_break_signflip_density_proxy/summary_snapshot.json`

## 7. 来源
1. Jiang, Z., Kelly, B., & Xiu, D. (2023). *(Re-)Imag(in)ing Price Trends*. Journal of Finance.
   - Authors: Zikun Jiang; Bryan Kelly; Dacheng Xiu
   - Year: 2023
   - Title: (Re-)Imag(in)ing Price Trends
   - Venue: Journal of Finance
   - DOI: https://doi.org/10.1111/jofi.13268
   - Readable URL: https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268
   - Repo URL: N/A
2. Lo, A. W., Mamaysky, H., & Wang, J. (2000). *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*. NBER.
   - Authors: Andrew W. Lo; Harry Mamaysky; Jiang Wang
   - Year: 2000
   - Title: Foundations of Technical Analysis
   - Venue: NBER Working Paper
   - DOI: https://doi.org/10.3386/w7613
   - Readable URL: https://www.nber.org/papers/w7613
   - Repo URL: N/A
3. Binance. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data*.
   - Authors: Binance
   - Year: 2026
   - Title: Kline-Candlestick Data
   - Venue: Binance Developers
   - DOI: N/A
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - Repo URL: N/A
