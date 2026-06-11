# 别把 15m continuation 全天同权：Bitcoin intraday TSMOM 更像在提醒我们先做 `first-30m impulse quality` shared gate
- 时间：2026-03-19 04:26 UTC
- 类型：论文
- 主题标签：breakout-short / fibonacci / retest-hold / ema / psar / intraday / momentum / volume / volatility / continuation / confirmation / filter / paper / crypto / 15m
- 证据类型：论文证据（**可读全文 + DOI + accepted manuscript**）

## 1. 这次看了什么
这次主看 **Shen, Urquhart, Wang (2022)** 的 *Bitcoin intraday time-series momentum*（Financial Review）。这篇不是让我们把“日内前 30 分钟→最后 30 分钟”机械照搬到 15m，而是给了一个更适合 desk 的旁支：**先判“开段冲击质量（方向 + 量能 + 波动）”，再决定是否放行后续 continuation**。

## 2. 核心结论（可直接迁移）
- **一句话核心结论：** 不是所有 session 的 continuation 都值得做；当开段冲击同时伴随高成交/高波动时，后段延续显著更强。
- **一句话说明它怎么证明：** 作者用 BTC/USD（五大交易所）分钟级数据，检验开段收益对尾段收益的 IS/OOS 预测，并按开段 volume/volatility 分组比较强弱，再做 market-timing 与 utility 检验。
- 文中最值钱的数字（原文口径）：
  1. pooled 回归里，首段对尾段斜率约 **0.968**（Newey-West t≈**4.38**，R²≈**1.44%**）。
  2. OOS 预测里，`R^2_OOS` 约 **1.09%**（首段单因子），两信号合并可到 **1.61%**。
  3. 分组后，**高成交日**可到 R²≈**3.86%**，**高波动日**R²≈**2.83%**，明显强于低成交/低波动。
  4. utility 侧 CER：首段信号约 **5.95%/年**，双信号约 **8.09%/年**（相对历史均值基准）。

## 3. 为什么和三条收口线直接相关
1. **V3 breakout-short follow-up**：
   breakout-short 最怕“看起来破了但后续没人接力”。`first-30m impulse quality` 可以作为 continuation 放行阀：冲击弱（低量低波）先降级为观察或 veto。
2. **Fibonacci confirmation / retest_hold**：
   当开段冲击质量弱时，优先等待 retest_hold；冲击质量强时，可放宽“必须深回踩”约束，减少错过趋势腿。
3. **EMA / PSAR raw alpha focus**：
   EMA/PSAR 不再单独决定开仓，先过“冲击质量闸门”再给入场/仓位，目标是降低噪音翻面成本。

## 4. 可复刻的最小实验（5m/15m，下一步怎么测）
### 研究假设
在 15m 信号执行前加入 `first-30m impulse quality gate`，能在不明显损失交易数的前提下，降低 continuation failure 并提升成本后期望。

### 数据源（公开可得）
- Binance/Bybit perpetual 的 5m OHLCV（CCXT 可拉）
- 公开性：公开市场数据
- 更新频率：5m（可聚合到 15m）

### 最小可计算定义（先冻结一版）
以 8h funding session（00/08/16 UTC）为单位：
- `r_open30`：session 前 30 分钟收益（前 6 根 5m）
- `vol_z_open30`：前 30 分钟成交量 z-score（相对过去 30 个 session）
- `rv_open30`：前 30 分钟实现波动（5m 收益平方和）
- `impulse_score = sign(r_open30) * I(vol_z_open30>0) * I(rv_open30>q60)`

接入规则（shared gate）：
- long continuation 仅当 `r_open30>0` 且 `vol_z_open30>0` 且 `rv_open30>q60`
- short continuation 仅当 `r_open30<0` 且同上
- 不满足则 `half-size` 或 `veto`（两臂都测）

### 回测切口
- 资产：BTC/ETH/SOL perpetual
- 周期：信号 15m，底层特征 5m
- 样本：近 180d（再补 365d 稳健性）
- 执行：next-bar-open, no-overlap
- 成本：6/10/15 bps per side

### 第一轮先看 5 个指标
- `post_cost_expectancy`
- `continuation_failure_rate`（4~8 bars）
- `trade_count_retention`
- `MAE`
- `return_per_trade`

## 5. 风险与保留意见
- 原论文核心口径是“日内开段→尾段”，不是逐根 15m 连续交易；迁移的是**quality gate 思路**，不是原绩效复刻。
- 论文样本到 2020 年，且集中 BTC/USD；需在 perp、多币、近样本做再验证。
- 若 gate 过严，可能靠“少交易”换好看结果；必须同时汇报 `trade_count_retention`。

## 6. 来源
1. **Shen, D., Urquhart, A., & Wang, P. (2022). _Bitcoin intraday time-series momentum_. Financial Review, 57(2), 319–344.**
   - DOI: `10.1111/fire.12290`
   - Readable URL: `https://doi.org/10.1111/fire.12290`
   - Accepted manuscript URL: `https://centaur.reading.ac.uk/100181/`
   - Direct PDF URL: `https://centaur.reading.ac.uk/100181/3/21Sep2021Bitcoin%20Intraday%20Time-Series%20Momentum.R2.pdf`
   - Repo URL: `N/A`
2. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market intraday momentum_. Journal of Financial Economics, 129(2), 394–414.**
   - DOI: `10.1016/j.jfineco.2018.05.009`
   - Readable URL: `https://doi.org/10.1016/j.jfineco.2018.05.009`
   - Repo URL: `N/A`
