# 别把多空仓位默认写成 50/50：AdaptiveTrend 的 `70/30` 更像 breakout-short / Fib / EMA-PSAR 共用的 position-sizing overlay
- 时间：2026-03-19 17:01 UTC
- 类型：论文（arXiv 近 5 年）
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/position-sizing/risk-overlay/long-short/asymmetry/cost-survival/paper/crypto/15m
- 证据类型：论文证据（预印本，待同行评审）

## 1. 这次看了什么
这轮看的是 **Thanh Nguyen-Van (2026)** 的论文 *Systematic Trend-Following with Adaptive Portfolio Construction*。我不拿它当“6h 趋势 alpha 模板”直接照搬，而是抽一个更适合我们 desk 的旁支：

> **多空仓位不应机械 50/50；在 crypto 的结构性正漂移里，`long/short` 更值得做成可调的风险覆盖层（allocation overlay）。**

## 2. 核心结论
1. **一句话核心结论**：对当前 5m/15m desk，更值得先测的不是再加一个新触发器，而是给三条收口线统一加一个“方向预算旋钮”（`λ_long`），避免把 short 侧权重默认拉到和 long 同级。  
2. **一句话证明方式**：论文在 `2022-2024`、`150+` 个加密永续、含成本 OOS 回测里，对比了不同配置；其报告的主配置（含动态 trailing stop + 月度筛选 + 非对称配比）表现显著优于传统基准。  
3. 关键数据点（论文报告值）：
   - `Sharpe = 2.41`，`Max Drawdown = -12.7%`，`Calmar = 3.18`（OOS 2022-2024）；
   - `70/30`（long/short）相对 `50/50` 报告 `+0.29` Sharpe 改善；
   - 参数敏感性里 `λ ∈ [0.60, 0.80]` 存在较宽稳定区，不是只在单点参数才成立。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：short 侧本来更容易遇到 squeeze 和急反，仓位预算不应与 long 对称。`λ_long` overlay 可以把“允许 short 但不重仓”规则化。  
- **Fibonacci confirmation / retest_hold**：Fib 多数是顺趋势回踩确认，long 侧往往承担更高通过率；用非对称预算可减少“同质量 setup 却被 short 配置拖累净值”的问题。  
- **EMA / PSAR raw alpha focus**：EMA/PSAR 当前最缺的不是再堆一个 entry 条件，而是成本后生存。先调仓位侧重，通常比继续加硬门更便宜。  

> 若问“为什么它比继续抠单条触发细节更值”：因为它是**三线共享**、可快速落地、且不会和现有触发逻辑冲突的上层风险旋钮。

## 4. 可复刻的最小实验（5m/15m）
### 4.1 数据与公开性
- 数据源：本地已有 Binance Futures 15m OHLCV + 三条线事件日志（已有 artifacts）；
- 公开性：公开可得（Binance 公共行情接口）；
- 更新频率：15m（可镜像到 5m）；
- 本轮定位：**position-sizing / risk overlay**，不是逐根 15m 主信号。

### 4.2 最小实验口径（先做这一版）
1. 固定三条线既有 trigger，不改 entry/exit 规则；
2. 只改组合层预算：
   - A: `50/50`（long/short 对称）
   - B: `60/40`
   - C: `70/30`
   - D: 自适应 `λ_long`（按最近 20 交易日 long/short 成本后 expectancy 比例，裁剪到 `[0.55,0.80]`）
3. 统一成本：`6/10/15 bps` 三档；
4. 先看 4 个指标：
   - `post_cost_portfolio_expectancy`
   - `max_drawdown`
   - `short_tail_loss_p95`
   - `capital_utilization_stability`

## 5. 风险与保留意见
- 该论文是 **arXiv 预印本**，尚未同行评审；
- 论文主频率是 `6h`，我们目标是 `5m/15m`，必须先做本地最小实验再决定是否上升优先级；
- 文中“月度参数重估”若实现不严谨容易引入 look-ahead，需要严格时间切分；
- 结论应理解为“仓位分配层可能带来增益”，不是在证明某条 entry 信号天然更强。

## 6. 来源
1. **Nguyen-Van, T. (2026). _Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets_. arXiv (cs.CE).**  
   - DOI: `10.48550/arXiv.2602.11708`  
   - Readable URL: <https://arxiv.org/abs/2602.11708>  
   - Full Text (HTML): <https://arxiv.org/html/2602.11708v1>  
   - PDF: <https://arxiv.org/pdf/2602.11708>  
   - Repo URL: `N/A（论文页面未给公开代码仓）`
2. **方法地基（引用）**：Moskowitz, Ooi, Pedersen (2012). *Time Series Momentum*. Journal of Financial Economics.  
   - DOI: `10.1016/j.jfineco.2011.11.003`  
   - URL: <https://www.sciencedirect.com/science/article/pii/S0304405X11002613>
