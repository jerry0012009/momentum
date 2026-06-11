# 别把 PSAR flip 延迟成 shared admission：`pre-flip SAR dot reclaim` 在 15m 更像 long-side 可选滤层，不是 EMA / PSAR raw alpha 的默认开火键
- 时间：2026-03-20 03:54 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：ema/psar/raw-alpha/pre-flip-dot/reclaim/continuation/asymmetry/admission/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 代理快检（公开行情）

## 1. 这次看了什么
这轮主看 GitHub 镜像仓库 **hasnocool / tradingview-pine-scripts** 里的脚本 **`BT-SAR Ema, Squeeze, Volatility`**。它给了 PSAR 两种完全不同的读法：不是只有 `SAR Flip` 直接开仓，还可以等 `SAR Breakout`——也就是 **先出现 flip，再在 `nBars` 窗口里，等价格重新穿回“flip 前最后一个 SAR dot”** 才算真正放行。这个旁支思路很贴近我们现在的 `EMA / PSAR raw alpha focus`：问题不是“PSAR 能不能翻面”，而是“翻面后要不要再过一道 continuation admission”。

## 2. 核心结论
- **一句话核心结论**：对 15m crypto，`pre-flip SAR dot reclaim` 暂时不适合升格成 EMA/PSAR 的 **shared 默认 admission layer**；它最多更像一个 **long-side 可选滤层**，而不是多空对称的统一开火键。
- **一句话它怎么证明**：仓库源码把 `SAR Breakout` 明确写成“flip 后 `nBars` 内重穿 pre-flip SAR dot”的状态机；我用 `BTC/ETH/SOL perp 15m 近 120 天` 做了一个只保留 `EMA100` 趋势过滤的代理快检，结果显示它在 **long 侧只略降 fail-rate，但显著减频，short 侧反而更差**。
- 仓库里最值得偷的，不是整套 `PSAR + squeeze + volatility` 配方，而是这个 **“把 flip 改写成 delayed reclaim”** 的状态机表达：
  - `SAR Flip`：`close[1] < SAR[1]` 且 `close > SAR`；
  - `SAR Breakout`：flip 发生后，在 `nBars` 内要求出现 `open < pre_flip_dot && close > pre_flip_dot`（short 镜像）。
- 本地代理快检（`BTC/ETH/SOL`，`15m`，近 `120d`，`EMA100` 过滤，`nBars=4`，看后续 `4 bars` signed return）里：
  - **long 侧**：`reclaim_long` 事件数只有 `286`，约为 `flip_long 689` 的 **42%**；fail-rate 从 **11.1% 降到 8.0%**，但 win-rate 从 **50% 降到 42%**，4-bar 中位数从 **0.0 bps** 变成 **-6.9 bps**。
  - **short 侧**：`reclaim_short` 只有 `293` 次，约为 `flip_short 776` 的 **38%**；同时均值从 **+3.9 bps** 变成 **-8.2 bps**，几乎没有保留成 shared short gate 的理由。
- 这说明它更像一种 **“筛掉一部分假 flip、但代价是显著减频和不稳定右尾”** 的写法；对当前 desk，更合理的定位不是“替代 PSAR flip 的统一 admission”，而是：
  1. 先只在 long continuation 侧做小范围对照；
  2. short 侧优先当 `veto / not-recommended branch` 处理；
  3. 若要继续留它，必须和 repo 里的 `squeeze/volatility` 过滤一起验，不要单独神化这一个 state transition。

## 3. 为什么和当前项目有关
这题直接服务当前高权重主线 `EMA / PSAR raw alpha focus`，而不是另开支线。我们最近一直在问：PSAR 到底是 `raw trigger`、`follow-up gate`、还是 `structure anchor`？这轮的答案更具体了——**把 PSAR flip 再延迟成 `pre-flip dot reclaim`，并不会自动让 raw alpha 变诚实**。它对 long 也许能做一点“少做错单”的过滤，但还不够证明自己值得成为默认层；对 short 则更像该尽快否掉的派生假设。

## 4. 可复刻的最小实验
### 研究假设
`pre-flip SAR dot reclaim` 不是 EMA/PSAR 多空共享 admission layer；它最多可能只对 long 侧 continuation 有条件成立。

### 一个可计算定义
- 先定义 bullish flip：`close[1] < sar[1] && close > sar`；bearish flip 镜像；
- 记录 `pre_flip_dot = sar[1]`；
- 在 flip 后 `N` 根内（建议 `N ∈ {2,4,6}`）只在出现：
  - long：`open < pre_flip_dot && close > pre_flip_dot`
  - short：`open > pre_flip_dot && close < pre_flip_dot`
  时放行；否则不交易；
- 再分别叠加 `EMA side`、`squeeze release`、`volatility spike`，看它是独立有效，还是必须靠其他 filter 才能活。

### 最小回测切口
- 资产：`BTC/ETH/SOL` perp
- 周期：`15m`
- 样本：近 `180d`，至少做 `120d train + 60d test`
- 对照三臂：
  1. `PSAR flip + EMA side`（baseline）
  2. `PSAR pre-flip reclaim + EMA side`
  3. `PSAR pre-flip reclaim + EMA side + squeeze/volatility filter`（只先测 long）

### 最先看 3 个指标
1. `post_cost_return`
2. `trade_count / positive_asset_ratio`
3. `4-bar fail-rate`（或 `eventual flip-back rate`）

## 5. 风险与保留意见
- 这轮证据主体是仓库源码，不是学术论文；更像工程假设拆解，不是正式文献结论。
- 本地快检刻意只保留了 `EMA100` 过滤，没有把 repo 里的 `squeeze`、`volatility oscillator`、RR/固定止盈止损一并复刻，所以它更像 **状态机快筛**，不是完整策略回测。
- long 侧 aggregate mean 略高于直接 flip，说明它可能带一点右尾筛选效应；但中位数、胜率、事件数都更差，**现在还不能把这种“右尾抬高”误读成稳健 alpha**。

## 6. 来源
1. hasnocool. (accessed 2026). *tradingview-pine-scripts* — mirrored TradingView strategy collection.  
   - Authors: hasnocool（镜像仓库维护者）  
   - Year: N/A  
   - Title: tradingview-pine-scripts  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/hasnocool/tradingview-pine-scripts>  
   - Repo URL: <https://github.com/hasnocool/tradingview-pine-scripts>
2. Credsonb / M4TR1X_BR attribution in mirrored file. (accessed 2026). *BT-SAR Ema, Squeeze, Volatility* (`BT-SAR Ema, Squeeze, Volatility.pine`).  
   - Authors: attribution in file shows `Credsonb` / `M4TR1X_BR`  
   - Year: N/A  
   - Title: BT-SAR Ema, Squeeze, Volatility  
   - Venue: GitHub code file  
   - DOI: N/A  
   - Readable URL: <https://raw.githubusercontent.com/hasnocool/tradingview-pine-scripts/main/BT-SAR%20Ema%2C%20Squeeze%2C%20Volatility.pine>  
   - Repo URL: <https://github.com/hasnocool/tradingview-pine-scripts>
3. Binance. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data*.  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>  
   - Repo URL: N/A
4. 本轮 desk 代理快检结果：  
   - Artifact CSV：`reports/artifacts/quant_digests/psar_preflip_reclaim_proxy_2026-03-20.csv`
