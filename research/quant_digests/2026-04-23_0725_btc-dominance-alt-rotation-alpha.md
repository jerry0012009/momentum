# 别把 BTC 统治力轮动只读成“山寨季叙事”：对 short-cycle crypto desk，更该先拆的是「BTC vs alt basket 相对强弱切换」这条 raw alpha
- 时间：2026-04-23 07:25 UTC
- 类型：GitHub repo source audit（`README.md` + `strategies/crypto_advanced.py::BTCDominanceStrategy`）+ 既有 Binance public-data portability probe（`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_meta.json`）
- 主题类型：raw alpha
- 基础 alpha：`BTC 相对山寨币篮子的超额收益趋势`，决定做多 BTC/做空弱 alt，或做空 BTC/做多强 alt
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-asset / relative-value / rotation / btc-dominance / alt-season / 15m / 5m / repo / public-data / cost / risk
- 证据类型：工程经验 + public-data portability probe

## 1. 这次看了什么
看的是 2026 repo **zwmjj/kuant-strategies** 里的 `BTCDominanceStrategy`。它没有直接用“BTC Dominance 指标”，而是用一个更容易落地的代理：**BTC 收益减去 alt basket 等权收益**，再看这个相对强弱本身的短趋势，决定是站在 BTC 一边，还是站在 alt basket 一边。

## 2. 核心结论
- 这条线的 **base alpha 很清楚**：不是单币 trend，也不是纯 filter，而是 **BTC 与 alt basket 的相对强弱轮动**。
- repo 里的 clean-room 骨架也清楚：`excess = BTC_ret - alt_basket_ret`，对 `lookback` 窗的 excess 做累计，再看其 `sma_window` 平滑后的斜率；斜率上行就 **long BTC / short 最弱 alt**，斜率下行就 **short BTC / long 最强 alt**。
- 本地既有 portability probe（6 币 Binance proxy，`2025-10-01 ~ 2026-04-12`）显示，这条线在 **gross** 口径下有值得继续追的厚度：最佳连续配置 `top_alts=4, rebars=4` 时，约 `+0.1136 bps/bar`、Sharpe `2.16`、累计 `+22.37%`、MDD `-8.96%`。
- 但它现在**更像“可保留的 raw alpha 壳”而不是已过成本关的成品**：该最佳桶的 active ratio 约 `99.8%`、平均换手约 `0.178x/bar`，说明一旦按 perp 短周期真实费滑去扣，edge 很容易被磨薄。
- repo 里最值得借的不是“山寨季”叙事，而是 **relative-strength state → long/short basket routing** 这层骨架：它能自然衔接 desk 的 cross-sectional / relative-value / router 方向。

## 3. 为什么和当前项目有关
它和当前 `momentum` 主线的关系很直接：
- 它补的是 **raw alpha 素材池**，而且是最近 intake 里相对少见的 **cross-asset / rotation** 家族；
- 它不是只能服务单一形态，后面既可以接 breakout child execution，也可以接 funding/basis veto；
- 它给了一个很实用的拆法：**先判“BTC 主导还是 alt 主导”**，再在对应侧做 strongest/weakest basket，而不是对全市场一视同仁开 trend 或 mean reversion。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / rotation
- 基础 alpha：BTC 相对 alt basket 的超额收益趋势切换
- regime：BTC dominance rising vs alt-season proxy（由 excess trend direction 判）
- filter / veto：可补 `excess gap threshold`、成交额门槛、funding/basis 过热 veto
- risk / sizing / execution overlay：BTC leg 固定半仓、alt leg 等权分散；`rebars` 控制再平衡频率；优先 maker-first，必要时只在 5m 做 child execution

## 4. 可复刻的最小实验
- 研究假设：当 `BTC_ret - alt_basket_ret` 的短窗趋势继续朝同一方向走时，**BTC 与 alt basket 的轮动会在接下来 1~6 小时继续，而不是立刻均值回归**。
- 一个可计算定义：在 `15m` 上取 `lookback=32`，`excess_cum = rolling_sum(BTC_ret - mean(alt_ret), 32)`；再取 `trend = SMA(excess_cum, 8)`，用 `trend.diff()` 的符号定 regime。`trend.diff()>0` 时 long BTC / short 过去 32 bars 最弱 3 个 alt；反之 short BTC / long 最强 3 个 alt。
- 最小回测切口：`BTC/ETH/SOL/BNB/XRP/DOGE`，先做 `15m` parent，持仓/再平衡分别试 `4 / 8 / 24 bars`；统一 `next-bar open`、no-overlap、双边成本先看 `8/12bps`。
- 最该先看哪 1~2 个指标：`post-cost mean bps/trade`、`breadth（不是单一 alt 独占）`；第三优先再看 `turnover` 与 `active ratio`。

## 5. 风险与保留意见
- 这条线最大的坑不是“逻辑不清楚”，而是 **过于连续持仓 + 高频再平衡**，很容易 gross 好看、net 很差。
- repo 用的是日频/通用 research 框架思维，迁到 perp `5m/15m` 时，必须把 **费率、滑点、单边冲击、child execution** 单独补上。
- 目前已有 probe 还更像 **public-data portability check**，不是正式 clean replication；因此现在更诚实的结论是：**值得进入 raw alpha 池，但先别把它当已过 admission 的实盘策略。**

## 6. 来源
- zwmjj. (2026). `kuant-strategies`. GitHub repo.
- Repo URL: `https://github.com/zwmjj/kuant-strategies`
- Readable URL: `https://github.com/zwmjj/kuant-strategies/blob/main/strategies/crypto_advanced.py`
- Strategy file: `https://raw.githubusercontent.com/zwmjj/kuant-strategies/main/strategies/crypto_advanced.py`
- Local probe artifact: `reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_meta.json`
