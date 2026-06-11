# 别把“刚破线”就算 breakout-short / retest_hold 确认：`penetration / channel width × ATR percentile` 更像 15m 的 shared admission layer
- 时间：2026-03-19 08:46 UTC
- 类型：GitHub + 本地快速复核
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/donchian/penetration/atr-percentile/confirmation/admission/filter/repo/crypto/15m
- 证据类型：repo 代码规则 + 公开行情快检（中等证据）

## 1. 这次看了什么
这轮主看 **Zelprog (2025) 的 `SignalPro-TV` 仓库**。我没有把它整套 `EMA200 + Supertrend + Donchian + RSI` 指标照搬，而是只抽其中一个更适合当前 desk 的旁支想法：
**不要把“刚刚越过边界”当成 breakout confirmation，而是先看这次穿越到底有多深（penetration），并且只在 ATR 处于可交易分位时承认它。**

repo 里的核心定义很直接：
- `breakout_strength_short = (prev_low - close) / donchian_range`
- 再叠加 `ATR percentile rank >= threshold`

换成人话：**不是问“有没有破”，而是问“破得够不够像真的，而且是不是发生在有展开空间的波动环境里”。**

## 2. 核心结论
- **一句话核心结论：** 对 15m 来说，`penetration` 单独拿出来不够；**`penetration × ATR context`** 才更像能服务 breakout-short / Fib retest_hold / EMA continuation 的 admission layer。
- **一句话说明它怎么证明：** repo 给了清楚的可编程规则；本地用 Binance Futures 15m（BTC/ETH/SOL，各 1500 bars）做快检后，short 侧只有在“穿透深度 + ATR 分位”同时存在时，继续走弱的统计才明显改善。

快检（short，4-bar 口径）摘要：
1. **Baseline breakdown**：`n=233`，win4 `44.21%`，avg_ret4 `-0.0447%`，4-bar reclaim `79.40%`
2. **`penetration >= 0.05 + ATR percentile >= 40`**：`n=85`，win4 `54.12%`，avg_ret4 `+0.0211%`，reclaim `65.88%`
3. **只有 penetration，不加 ATR**：`n=158`，win4 `43.04%`，avg_ret4 `-0.0579%` —— 说明“破得更深”本身不够，容易只是情绪化最后一脚
4. **只有 ATR，不加 penetration**：`n=123`，win4 `53.66%`，avg_ret4 `+0.0139%`
5. 更严版本 **`penetration >= 0.10 + ATR >= 40`**：`n=59`，win4 `57.63%`，reclaim `57.63%`，但交易数继续下降

我对这轮主题的判断是：它比另起一个新方向更值，因为它直接在修当前三条收口线的共同毛病——**把“碰线/过线”写得太便宜、太二元。**

## 3. 为什么和当前三条收口线有关
- **V3 final-verdict / breakout-short follow-up**：很适合改写成“先破前低，再要求穿透深度和 ATR context 过线，才允许 follow-up”，减少末端追空。
- **Fibonacci confirmation / retest_hold**：Fib 回踩不是碰到位就算守住；更诚实的写法是：回抽后重破/重站时，要有**足够深的离开幅度**，否则只是 level 附近抖动。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 本身给方向或翻面，但 admission 可以再加一层“离开均线/PSAR 的距离质量”筛选，角色更像 cost-survival layer，而不是替代主触发。

## 4. 下一步怎么测（5m/15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 首轮样本：BTC / ETH / SOL，滚动 180d（IS）+ 60d（OOS）

### 4.2 最小可复现实验口径
先做 **short-only**，别急着 long/short 同权：
1. 用当前 breakout-short / Fib / EMA-PSAR baseline 产出原始 short 信号；
2. 对每个信号计算：
   - `penetration_short = (trigger_level - close) / recent_range`
   - `atr_rank = percent_rank(ATR14, 100 bars)`
3. 只保留 `penetration_short >= {0.03, 0.05, 0.10}` 且 `atr_rank >= {40, 50}` 的组合；
4. 把它先当 **admission / sizing layer**，不要一上来就改主触发逻辑。

优先看 3 个指标：
- `post_cost_expectancy`
- `false_follow_ratio`（4 bars 内被拉回 trigger level 上方）
- `trade_count_retention`

过线建议（相对 baseline）：
- `false_follow_ratio` 下降 ≥10%
- `trade_count_retention` ≥35%~50%
- `post_cost_expectancy` 不恶化，最好转正

## 5. 风险与保留意见
- 这个 repo 还是偏“开发中的 TradingView 指标”，不是成熟回测论文；
- 当前快检只看了 3 个币、1500 根 15m bar、4-bar 前瞻，证据强度中等；
- 从快检看，**long 侧没有同样干净**，所以当前不建议做成双向统一 admission；
- 若最后发现 edge 主要来自 ETH，而 BTC/SOL 不稳，就应降级成资产特异 overlay，而不是全市场共享规则。

## 6. 来源
1. **Zelprog. (2025). _SignalPro-TV_. GitHub Repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/Zelprog/SignalPro-TV>
   - Repo URL: <https://github.com/Zelprog/SignalPro-TV>
2. **核心实现文件：`indicator.pine`**
   - Readable URL: <https://github.com/Zelprog/SignalPro-TV/blob/main/indicator.pine>
   - Raw URL: <https://raw.githubusercontent.com/Zelprog/SignalPro-TV/main/indicator.pine>
3. **参数与设计说明：`parameters.pine` / `Claude.md`**
   - <https://github.com/Zelprog/SignalPro-TV/blob/main/parameters.pine>
   - <https://github.com/Zelprog/SignalPro-TV/blob/main/Claude.md>
4. **本地快速复核（公开行情）**
   - 数据源：Binance Futures Klines API
   - API URL: <https://fapi.binance.com/fapi/v1/klines>
   - 结果文件：
     - `reports/artifacts/literature/tmp_signalpro_breakout_strength_quickcheck_15m_1500bars_20260319.csv`
     - `reports/artifacts/literature/tmp_signalpro_breakout_strength_summary_15m_1500bars_20260319.csv`
