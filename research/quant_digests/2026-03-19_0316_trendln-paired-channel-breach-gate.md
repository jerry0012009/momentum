# 别把 trendline 只当“画线工具”：`paired-channel breach + reclaim-hold` 更像 breakout-short / Fib / EMA-PSAR 的 shared follow-up gate
- 时间：2026-03-19 03:16 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/trendline/channel/breach/reclaim/confirmation/filter/repo/crypto/15m
- 证据类型：仓库源码参数 + 工程迁移假设
- 证据强度提示：**中等**（规则清晰、可快速复现；但当前仍属 repo-based 假设，非论文 OOS 结论）

## 1. 这次看了什么
这次看的核心来源是 **Gregory Morse 的 `trendln` 仓库**。它不是直接给买卖信号，而是把“支撑/阻力线”拆成可计算对象：先找 extrema，再产出 support/resistance 候选线和线质量指标。对我们 desk 当前更值钱的旁支，不是再争论“线画得像不像”，而是把它压成一个 **15m 的 post-break follow-up gate**：

- 先有 `close-confirm breach`（突破/跌破必须收盘确认）
- 再看 `reclaim-hold`（是否快速回到线内并稳定）
- 最终作为三条收口线的 shared 允许/否决层

## 2. 核心结论
- **一句话核心结论：** 对 5m/15m 来说，趋势线层更适合做“突破后的真假分流”，而不是单根触发；先做 `paired-channel breach`，再做 `reclaim-hold`，比把 trendline 当裸 alpha 更诚实。
- **一句话说明它怎么证明：** `trendln` 默认已经把线搜索和线质量显式参数化（如 `window=125`、`errpct=0.005`、默认线搜索 `METHOD_NSQUREDLOGN`），说明它天然适合做“结构层/过滤层”，不是一键下单器。
- 直接可偷的 3 个硬参数/事实：
  1. 默认线搜索窗口 `window=125`（可近似映射到 15m 的 ~31h 结构窗口）；
  2. 默认斜率误差阈值 `errpct=0.005`；
  3. 仓库公开可复现（GitHub API：`692` stars、`164` forks，MIT 许可）。

## 3. 为什么和当前项目有关
这轮优先级是高的，因为它直接给三条收口线补“突破后路径质量”这一层：

- **`V3 final-verdict / breakout-short follow-up`**：
  breakout-short 最怕最后一脚假突破。`breach -> reclaim-hold` 可以把“穿线但迅速收回”的差交易先挡掉。
- **`Fibonacci confirmation / retest_hold`**：
  Fib 回踩本质是“守住结构”。paired-channel 的边界可以给 retest 增加“是否仍在可接受结构内”的第二重证据。
- **`EMA / PSAR raw alpha focus`**：
  EMA/PSAR 原始信号容易在噪音期反复翻面。把 trendline gate 放在信号后面，更像成本友好的 follow-up 过滤，而不是再堆一个同层 trigger。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
在 BTC/ETH/SOL 的 15m 上，`paired-channel breach + reclaim-hold` 能降低 false break，并提升三条线的成本后质量。

### 数据源与公开性
- 数据：交易所公开 OHLCV（Binance/Bybit，CCXT 可直接拉取）
- 公开性：公开市场数据，无私有 feed 依赖
- 更新频率：5m / 15m K 线
- 最小复现实验口径：固定 `BTC/ETH/SOL`，滚动 `120d`，next-bar-open 执行

### 最小规则（先做便宜版本）
1. **结构层（15m）**
   - 用因果 extrema 构建 support / resistance 配对通道（paired channel）
   - 只保留宽度稳定的 active channel（例如 `channel_width/ATR` 在阈值内）
2. **事件层**
   - `raw_breach`：close 真突破 outer line
   - `breach_plus_reclaim_hold`：突破后 `N=2~4` 根内，若快速收回通道内且继续贴近边界，则判为失败；未收回则保留
3. **接入三条线**
   - breakout-short：只在 `breach_plus_reclaim_hold` 通过时放行
   - Fib retest_hold：当回踩仍位于结构允许区间且未触发“快速收回失败”时放行
   - EMA/PSAR：从“直接触发”降级为“先触发，再过 channel follow-up gate”

### 第一轮评估指标（必须）
- `post_cost_expectancy`
- `false_break_ratio`（4~8 bars 内反向收回）
- `trade_retention`（避免靠砍单过多伪改善）

## 5. 风险与保留意见
- `trendln` 是结构检测仓库，不是为 15m perp 交易直接设计；迁移的是“分层思想+参数框架”，不是原策略收益承诺。
- 结构线存在时点/回看偏差风险：必须冻结因果 line（只用当时已确认 extrema），并坚持 next-bar-open 执行。
- 这条线应定位为 **shared follow-up filter**，不是替代 breakout/Fib/EMA-PSAR 的主信号。

## 6. 来源
1. **Morse, G. (2019, repo active updates visible in 2026 metadata)**. *trendln: Support and Resistance Trend lines Calculator for Financial Analysis*.
   - Venue: GitHub Repository
   - DOI: N/A（仓库）
   - Readable URL: https://github.com/GregoryMorse/trendln
   - Repo URL: https://github.com/GregoryMorse/trendln
   - License: MIT
2. **仓库说明中引用文章（实现解读）**
   - Morse, G. (2020). *Programmatic Identification of Support/Resistance Trend lines with Python* (Towards Data Science / Medium).
   - DOI: N/A
   - Readable URL: https://towardsdatascience.com/programmatic-identification-of-support-resistance-trend-lines-with-python-d797a4a90530
3. **本地映射文档（实现边界）**
   - `/root/clawd/jerry/momentum/docs/SIGNALS_TRENDLINE_BREAKOUT_NAVIGATOR.md`
