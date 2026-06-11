# 别把“走得更直”当成 15m continuation 奖励：`regression channel width` 暂时不适合升成 breakout-short / Fib / EMA-PSAR 的 shared gate
- 时间：2026-03-20 01:05 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/linear-regression/channel-width/path-cleanliness/continuation/filter/repo/crypto/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情代理快检（中等证据）

## 1. 这次看了什么
这轮主看 `fmzquant/strategies` 里两份和 **linear regression channel** 直接相关的实现：`Adaptive-Linear-Regression-Channel-Strategy` 与 `Linear-Regression`。我没有把它们当主信号照抄，而是只抽一个更贴当前 desk 的旁支问题：

> **breakout 前那段路，如果价格更贴近一条线性回归中轴、通道更窄，是不是更值得做 breakout-short follow-up / Fib retest_hold / EMA-PSAR continuation？**

## 2. 核心结论
1. **一句话核心结论：** 在当前 `15m` 代理口径下，`pre-break regression channel width` 还不适合被写成“三条线共享的 path-cleanliness gate”；**“越直越好”这件事，目前证据不成立。**
2. **一句话证明方式：** repo 给了 rolling regression line + deviation channel 的可编程骨架；我用 Binance Futures `BTC/ETH/SOL 15m`、最近 `120d`、`20-bar breakout + body_ratio>=0.40 + breakout_ext>=0.20 ATR` 的代理事件，对比 breakout 前 `12` 根的 `regression residual width / ATR` 与之后 `4-bar` continuation / reclaim 表现。
3. 聚合结果（全部事件，`n=1937`，按 width tercile 分桶，假设 round-trip 成本 `12bps`）：
   - **base**：`net12_mean = -6.03 bps/笔`
   - **low_width_clean**：`n=646`，`-11.87 bps/笔`
   - **mid_width**：`n=645`，`-5.57 bps/笔`
   - **high_width_noisy**：`n=646`，`-0.64 bps/笔`
4. 对当前最关心的 **breakout-short** 更明显：
   - **short base**：`n=1026`，`-4.13 bps/笔`
   - **short low_width_clean**：`n=312`，`-12.00 bps/笔`
   - **short high_width_noisy**：`n=383`，`+3.30 bps/笔`
5. 我还试了更“教科书式”的 clean gate：`slope 同向 + R²>=0.60 + low width`。结果更差：
   - **all aligned_clean**：`n=337`，`-14.62 bps/笔`
   - **short aligned_clean**：`n=159`，`-13.50 bps/笔`

## 3. 为什么和当前项目有关
这轮值得做，不是因为它能立刻贡献一个新 alpha，而是因为它在**阻止我们把一个看上去很优雅、其实未必有用的 gate，误接到三条收口线里**。

- **V3 final-verdict / breakout-short follow-up**：这是最直接的受益方。当前证据更像在说：**不要默认要求“breakout 前走势必须很干净”才允许 short follow-up。** 至少在这个代理里，这样做会把 short 侧继续走弱的机会先筛掉。
- **Fibonacci confirmation / retest_hold**：它提醒我们，`impulse quality` 不等于“回归线更直”。Fib 继续更该盯 `anchor honesty / depth / reclaim`，而不是贸然再加一个 regression-cleanliness 门。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 现在最怕的是再堆一个“听起来很合理”的过滤层。当前更诚实的结论是：**linear-regression width 先当诊断列，不要直接升成 admission。**

## 4. 可复刻的最小实验
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：`15m`（可平移到 `5m`）

### 4.2 最小实验口径
1. 沿用当前 `breakout-short` 或 `Fib retest` baseline 的原始触发；
2. 只额外记录 `reg_width_atr = regression_residual_std / ATR14`（lookback 先用 `12`）；
3. 不要直接当 hard veto，先做三臂对照：
   - A：无 gate
   - B：`low_width_clean` only
   - C：`mid/high width` only（尤其 short）
4. 首轮只看 4 个指标：
   - `post_cost_expectancy`
   - `fail_back_inside_4bars`
   - `trade_count_retention`
   - `asset_consistency`

如果 `low_width_clean` 在 OOS 下仍系统性更差，就把这条正式降级成 **diagnostic-only feature**，别再把它包装成 shared gate。

## 5. 风险与保留意见
- 来源是 **工程 repo**，不是论文；
- 本轮只是 `4-bar` 代理，不是完整持仓生命周期；
- `high_width_noisy` 在 short 侧较好，并不等于“越乱越好”，更像是在当前 breakout 定义下，**低 width 不是值得额外奖励的条件**；
- `BTC` short 三桶都仍为负，所以现在最多只能说“别强推 clean gate”，还不能反过来说“高 width 就是新 alpha”。

## 6. 来源
1. **ChaoZhang. (2024). _Adaptive-Linear-Regression-Channel-Strategy_. GitHub / fmzquant/strategies.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/fmzquant/strategies/blob/master/%E4%B8%80%E7%A7%8D%E5%9F%BA%E4%BA%8E%E7%BA%BF%E6%80%A7%E5%9B%9E%E5%BD%92%E5%88%86%E6%9E%90%E7%9A%84%E9%87%8F%E5%8C%96%E4%BA%A4%E6%98%93%E7%AD%96%E7%95%A5Adaptive-Linear-Regression-Channel-Strategy.md>
   - Raw URL: <https://raw.githubusercontent.com/fmzquant/strategies/master/%E4%B8%80%E7%A7%8D%E5%9F%BA%E4%BA%8E%E7%BA%BF%E6%80%A7%E5%9B%9E%E5%BD%92%E5%88%86%E6%9E%90%E7%9A%84%E9%87%8F%E5%8C%96%E4%BA%A4%E6%98%93%E7%AD%96%E7%95%A5Adaptive-Linear-Regression-Channel-Strategy.md>
   - Repo URL: <https://github.com/fmzquant/strategies>
2. **ChaoZhang / LucemAnb. (2022). _Linear-Regression_ (`Linear Regression ++ [Lucem Anb]`). GitHub / fmzquant/strategies.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/fmzquant/strategies/blob/master/Linear-Regression.md>
   - Raw URL: <https://raw.githubusercontent.com/fmzquant/strategies/master/Linear-Regression.md>
   - Repo URL: <https://github.com/fmzquant/strategies>
3. **Binance Futures API. (Public). _Klines endpoint_.**
   - Readable URL: <https://fapi.binance.com/fapi/v1/klines>
4. **本地代理快检产物**
   - `reports/artifacts/quant_digests/regression_width_gate_proxy/events.csv`
   - `reports/artifacts/quant_digests/regression_width_gate_proxy/summary.csv`
   - `reports/artifacts/quant_digests/regression_width_gate_proxy/summary.json`
   - `reports/artifacts/quant_digests/regression_width_gate_proxy/short_asset_bucket_summary.csv`
