# 别把 mean reversion 只留给 pairs：这份 2026 新仓库更适合先复现的是「多档 Envelope 单资产回归」完整策略骨架
- 时间：2026-03-23 19:42 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年文献地基 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：single-asset short-horizon mean reversion（价格短时偏离均线后回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/envelope/multi-band/scale-in/risk-manager/cost/repo/paper/binance/crypto/1m/3m/5m/15m
- 证据类型：仓库代码规则 + 配置参数 + 本地代理快检（可复现）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“短周期价格过度偏离均线后向均线回归”，不是 filter。**

本轮主看 2026 新仓库 **grantad/crypto-bot**。它不是“讲概念”的仓库，而是给了可落地策略骨架：
- entry：价格触发 `lower/upper envelope`（支持多档）
- exit：价格回到均线即平仓
- sizing：资金按 envelope 档位等分、逐档加仓
- risk：策略内 stop-loss + 会话级风险熔断器（最大亏损、最大连亏、最大交易数）
- cost：回测里显式计入 open/close fee

这条线对当前 desk 的价值在于：它是**可独立复现且可直接拆 entry/exit/sizing/risk/cost 的 raw alpha 候选**，可作为 `1m/3m/5m/15m` 的单资产回归基线模块。

## 2. 核心结论
- **一句话结论：** 多档 envelope 回归是能独立站住的 raw alpha 骨架，但参数不能机械照搬高周期默认值；必须做“周期重标定 + 成本后生存检验”。
- **一句话证据：** 仓库规则完整；我用 Binance 5m 公共数据做最小代理快检后看到：默认参数在短周期几乎不触发，但收紧阈值后出现可交易 pocket（集中在高波动币）。

最关键 3 个数据点：
1. **直接照搬仓库默认 `envelopes=[7%,11%,14%]` 到 5m**（BTC/ETH/SOL，各 1500 根）→ **0 笔成交**（信号过稀）。
2. 把阈值压到 `0.7%/1.1%/1.4%`（其余不变）后，`ALL_EQ` 仍是 **`-0.107 bps/bar`**（成本后为负）。
3. 再收紧到 `SMA=12, envelopes=[0.3%,0.5%,0.7%]`，`SOLUSDT` 出现 pocket：**`+0.096 bps/bar`、Sharpe `2.49`、Trades `124`**；但 BTC/ETH 仍未稳定转正。

## 3. 为什么和当前 desk 直接相关
- 它补的是 **raw alpha 池**（single-asset mean reversion），不是又一个解释层。
- 它天然是短周期友好结构：
  - 规则只依赖 OHLC（可直接映射 `1m/3m/5m/15m`）
  - 不依赖复杂特征或黑箱模型，复现门槛低
- 它还能和现有模块直接拼接：
  - 可单跑做 alpha leg
  - 可给 cross-sectional / stat-arb 作为“回归腿”对照基线

## 3.5 策略拆解（必填）
- 方向属性：单资产双向 mean reversion（long/short 都可）
- 基础 alpha：价格对滚动均线的短时过冲会回归
- regime：高波动但非单边挤压阶段更容易成立
- filter / veto：大事件窗口、盘口流动性骤降、连续 stop 区间可 veto
- risk / sizing / execution overlay：
  - 多档 envelope 逐档加仓，单档等权
  - `close@mean` + `stop-loss` + 会话级 risk breaker
  - 成本端需显式计入双边手续费与滑点；低边际优势场景优先 maker

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（主策略来源）：`grantad/crypto-bot` 仓库策略与配置（公开）
- 数据源 B（短周期代理快检）：Binance USDT-M Futures `klines`（公开 REST，无需 API key）
- 更新频率：支持 `1m/3m/5m/15m`（本轮用 `5m`）
- 最小实验口径：
  - 标的：`BTCUSDT/ETHUSDT/SOLUSDT`
  - 样本：最近 `1500` 根 `5m`
  - 信号：SMA + 多档 envelope 触发、回均线平仓
  - 成本：open `2bps`，close `5bps`（代理口径）

### 4.2 快检解读
- **默认参数不能直接下放周期。** 7%~14% 这种 1h 级阈值映射到 5m 后几乎不触发。
- **压缩阈值后仍需成本筛选。** 即使能触发交易，ALL_EQ 依然可能成本后为负。
- **更像“标的选择 + 参数治理”型 alpha。** 当前 pocket 主要出现在高波动币（本轮为 SOL），不是全市场普适。

## 5. 下一步怎么测（直接可执行）
1. **做跨周期稳定性表**：同一标的在 `1m/3m/5m/15m` 扫 `avg_period × envelope × max_hold`，看“参数平台”而非单点最优。  
2. **加 funding/OI veto 做二阶段**：先保留 raw alpha 主体，再测试 `funding_extreme` 与 `OI_jump` 能否降低连续止损段。  
3. **做执行可得性评估**：把 maker 占比、吃单占比、成交延迟加入成本，输出 `signal edge → tradable edge` 衰减曲线。  
4. **上实盘前门槛**：要求 OOS `net>0`、`Sharpe>0.8`，且在 `cost +50%` 压力下不翻负。  
5. **和现有 raw alpha 组合测试**：与 `XS reversal / residual MR / carry` 做低相关拼接，评估组合层边际贡献。

## 6. 风险与保留意见
- 本轮快检是“按仓库逻辑写的代理实现”，不是逐行复用原仓库引擎，结论应视为 intake 级证据。  
- 样本窗口短，且仅 3 个币；不能外推为“全币种通用”。  
- 单资产回归在强趋势挤压阶段容易连续亏损，必须配合 stop 与会话级熔断。

## 7. 来源
1. **grantad. (2026). _crypto-bot_. GitHub repository.**  
   - Repo URL: https://github.com/grantad/crypto-bot  
   - Readable URL: https://github.com/grantad/crypto-bot
2. **Dobrynskaya, V. (2023). _Cryptocurrency Momentum and Reversal_. The Journal of Alternative Investments.**  
   - DOI: `10.3905/jai.2023.1.189`  
   - Readable URL: https://doi.org/10.3905/jai.2023.1.189
3. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday Return Predictability in the Cryptocurrency Markets: Momentum, Reversal, or Both_. SSRN Electronic Journal.**  
   - DOI: `10.2139/ssrn.4080253`  
   - Readable URL: https://doi.org/10.2139/ssrn.4080253
4. **Fieberg, C., Liedtke, G., Metko, D., & Zaremba, A. (2023). _Cryptocurrency factor momentum_. Quantitative Finance.**  
   - DOI: `10.1080/14697688.2023.2269999`  
   - Readable URL: https://doi.org/10.1080/14697688.2023.2269999
5. **Binance Developers. _USDT-M Futures Kline/Candlestick Data_.**  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 8. 本地复现产物
- `reports/artifacts/quant_digests/envelope_reversion_20260323/summary.csv`
- `reports/artifacts/quant_digests/envelope_reversion_20260323/meta.json`
