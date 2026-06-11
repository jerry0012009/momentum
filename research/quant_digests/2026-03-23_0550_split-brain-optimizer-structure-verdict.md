# 别把 EMA / PSAR raw alpha 的坏分数直接判成“没边”：这份新 repo 更值钱的是把 `structure verdict` 和 `parameter tuning` 拆开
- 时间：2026-03-23 05:50 UTC
- 类型：GitHub 仓库（research harness / optimizer）
- 主题类型：overlay
- 基础 alpha：breakout / fib / ema-psar 等既有结构（参数与结构拆分评估）
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/raw-alpha/optimizer/walk-forward/parameter-search/repo/crypto/5m/15m
- 证据类型：工程证据（公开代码 + README 架构说明）

## 1. 这次看了什么
这次不再补一个新形态，而是看 **dietmarwo (2026)** 的 `autoresearch-trading`：它最适合我们 desk 的旁支，不是“自动挖圣杯”，而是**先把连续参数从结构 verdict 里剥出去**，避免把 `EMA / PSAR / breakout / retest` 的坏表现误判成“这个想法本身没边”。

## 2. 核心结论
- **一句话核心结论：** 对当前三条收口线，下一步更该先测的不是再拍脑袋改阈值，而是用 `固定结构 + 自动调连续参数 + 严格 walk-forward`，先判断到底是“结构不行”还是“参数猜错了”。
- **一句话说明它怎么证明：** 该 repo 把 LLM 负责的离散逻辑（用哪些指标、怎么组合）与优化器负责的连续参数（窗口、阈值、等待条数）拆开，再用滚动 OOS score 回喂结构优劣。
- repo README 里给出的工程强点很适合 desk 快筛：**99 个 `@njit` 指标/工具函数** 已覆盖 `EMA / ADX / PSAR / Supertrend / Donchian / ATR / VWAP` 等核心组件，不用先自己补一遍研究脚手架。
- README 还声称在 numba + `fcmaes/BiteOpt` 下可做到 **10,000+ 次 strategy eval / 秒**，且 **4 个 ticker 的一次优化约 1 秒**（16-core AMD 9950X）；这意味着它更像 `first verdict` 引擎，而不是慢速大回测平台。
- 对当前主线最重要的启发是：**EMA / PSAR raw alpha 现在最怕“错杀”**——如果直接用手工阈值做 verdict，很容易把本来只是参数不对的 skeleton 当成结构性死亡；而 breakout-short / Fib retest 也有同样问题。

## 3. 为什么和当前项目有关
- 对 `EMA / PSAR raw alpha focus`：这是最直接的帮助。它能先回答“EMA-only、EMA+ADX、EMA+PSAR fail-safe、EMA+Donchian handoff”到底谁在 OOS 里还有边，而不是继续靠人工微调。
- 对 `V3 final-verdict / breakout-short follow-up`：很多 follow-up gate 的争议，其实是 timeout / penetration / wait-bar 这些连续参数没被诚实搜索；先把参数交给优化器，更容易看出 structure 是否真的有效。
- 对 `Fibonacci confirmation / retest_hold`：Fib 线经常被 `zone 宽度 / bounce 窗口 / reclaim 容差` 搅乱。把这些从“人工感觉”改成“固定结构下的连续搜索”，能更快看清 retest_hold 到底是 confirmation 还是 placebo。

## 3.5 策略拆解（必填）
- 方向属性：方法层 / research harness，本身不直接定义方向
- 基础 alpha：EMA continuation、breakout follow-up、Fib retest_hold skeleton 之一
- regime：由 walk-forward 各折 OOS 生存情况反推，不先偷塞固定 regime 结论
- filter / veto：若某结构在最优连续参数下仍 OOS 不稳，则直接 veto 该结构，而不是继续手改参数
- risk / sizing / execution overlay：第二阶段再加；第一阶段先固定简单成本与仓位，避免 overlay 掩盖结构 verdict

## 4. 可复刻的最小实验
### 研究假设
把“结构”和“连续参数”拆开后，当前三条线里至少有一条会出现**比手工阈值更诚实的 OOS verdict**；特别是 `EMA / PSAR raw alpha`，可能是“参数错杀”而非“结构归零”。

### 一个可计算定义
做 4 个固定 skeleton，只让优化器搜连续参数：
1. `EMA stack`
2. `EMA + ADX gate`
3. `EMA + PSAR fail-safe`
4. `Donchian breakout + EMA context`

统一搜索参数：`ema_fast / ema_slow / adx_th / psar_step / psar_max / breakout_window / wait_bars / stop_atr / tp_atr`。

### 最小回测切口
- 标的：BTC / ETH / SOL perpetual
- 周期：15m（必要时补 5m 执行价）
- 样本：近 180d
- 评估：rolling walk-forward，固定手续费 + 简单滑点
- 对照：`人工默认参数` vs `自动优化连续参数`

### 第一轮先看
- OOS post-cost expectancy
- positive-fold ratio
- parameter stability（最优参数是否乱跳）
- structure rank stability（哪种 skeleton 在不同折里仍靠前）

## 5. 风险与保留意见
- 这是工程 repo，不是同行评审论文；优势是快验证，不是学术证明。
- 优化器会放大过拟合风险，所以必须把 `walk-forward + cross-asset + fold stability` 写成硬约束，不能只看 best run。
- README 的吞吐数字来自作者自报硬件环境；对我们更重要的是“相对足够快做 first verdict”，不是照搬绝对速度。
- 这条线是**研究方法增强**，不是新 alpha 本体；若最后发现所有 skeleton 在最优参数下仍 OOS 不活，那也应诚实判 dead，而不是继续炼。

## 6. 来源
1. **dietmarwo (2026). _autoresearch-trading_. GitHub Repository.**
   - Authors / Year / Title / Venue: dietmarwo / 2026 / autoresearch-trading / GitHub Repository
   - DOI: N/A
   - Readable URL: https://github.com/dietmarwo/autoresearch-trading
   - Repo URL: https://github.com/dietmarwo/autoresearch-trading
   - README URL: https://raw.githubusercontent.com/dietmarwo/autoresearch-trading/master/README.md
2. **dietmarwo. _fast-cma-es / fcmaes_. GitHub Repository.**
   - Authors / Year / Title / Venue: dietmarwo / 2026 / fast-cma-es / GitHub Repository
   - DOI: N/A
   - Readable URL: https://github.com/dietmarwo/fast-cma-es
   - Repo URL: https://github.com/dietmarwo/fast-cma-es
3. **Binance USDⓈ-M Futures Market Data API（用于最小实验的数据口径）**
   - 数据源：Binance Developers
   - 公开性：公开可得
   - 更新频率：分钟级
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
