# 别把这份 2025 stat-arb repo 只读成“组合课设”：对 short-cycle desk，更该先拆的是「BTC-beta-neutral residual loser-bounce basket」这条 raw alpha

- 时间：2026-04-17 22:57 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `Stat Arb in Crypto.pdf` + `Reversal - Time Horizon.ipynb`）+ Binance USDⓈ-M public-data portability probe（`15m` / `5m`）
- 主题类型：raw alpha
- 基础 alpha：**先把各币对 BTC 的 beta 暴露扣掉，再对“超出 BTC 系统因子以外”的短窗残差收益做横截面反转：买 residual losers，卖 residual winners。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / relative-value / mean-reversion / beta-neutral / residual-return / loser-bounce / market-neutral / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 源码 + bundled PDF + public-data probe

## 1) 这次看了什么
- **Maintainer**：gm-clara
- **Year**：2025（repo 持续更新到 2025-09）
- **Title**：*Statistical Arbitrage in Cryptocurrencies*
- **Venue / Type**：GitHub repo
- **Readable URL**：<https://github.com/gm-clara/Stat-Arb-in-Crypto>
- **Repo URL**：<https://github.com/gm-clara/Stat-Arb-in-Crypto>
- **关键材料**：
  - README：<https://raw.githubusercontent.com/gm-clara/Stat-Arb-in-Crypto/main/README.md>
  - Notebook：<https://github.com/gm-clara/Stat-Arb-in-Crypto/blob/main/Reversal/Reversal%20-%20Time%20Horizon.ipynb>
  - PDF：<https://github.com/gm-clara/Stat-Arb-in-Crypto/blob/main/Stat%20Arb%20in%20Crypto.pdf>

先把 **base alpha** 说清楚：

> **不是“跌得多就抄底”这么粗糙，而是“先把 BTC 大盘 beta 解释掉，再去抓各币自己的 idiosyncratic overreaction”。**

repo 的 Time Horizon Reversal notebook，本质是在做一条 **BTC-beta-neutral、横截面、市场中性、短窗 mean reversion raw alpha**，不是单纯 filter，也不是 portfolio decoration。

## 2) repo 里真正值得继承的部分
### 2.1 用人话翻译源码
`Reversal - Time Horizon.ipynb` 的核心步骤是：
1. 先算每个币相对 BTC 的 rolling beta；
2. 得到 residual return：`resid_i = ret_i - beta_i * ret_BTC`；
3. 交易信号取负号：`signal_i = -resid_i`，也就是 **buy residual losers / sell residual winners**；
4. 横截面 rank 后做 demean，变成 dollar-neutral book；
5. 再做 EMA smoothing 和归一化，落成 fully-invested market-neutral 组合。

一句话核心结论：

> **这份 repo 最值钱的不是“4H backtest 很漂亮”，而是它把“BTC 中性化后的横截面反转”写成了一条很干净的 raw alpha 母板。**

一句话证明方式：

> **它不是靠主观故事，而是直接用残差收益、横截面 rank、market-neutral 权重和 out-of-sample 回测把这条线跑出来。**

### 2.2 repo 自带结果为什么值得看，但不能照单全收
repo 自带的 4H out-of-sample（2024~2025）结果相当亮眼：
- net cumulative return 约 **`305.21%`**
- annualized return 约 **`96.65%`**
- Sharpe 约 **`1.90`**
- Information Ratio 约 **`1.65`**
- max drawdown 约 **`-25.94%`**

但要诚实：
- 那是 **4H resample**；
- 成本假设是 `20 bps`，但 turnover 很低；
- 能不能转译到我们更关心的 `5m / 15m`，必须单独验。

## 3) 为什么和当前 desk 有关
这题值得 intake，不是因为它给了又一个慢频组合，而是因为它补的是一条我们一直需要的 raw alpha 母板：

1. **它属于 cross-sectional / relative-value / mean-reversion**，能平衡最近过密的 funding / basis / pairs 叙事；
2. **base alpha 清楚**：不是泛泛“市场中性”，而是 `BTC-beta-neutral residual reversal`；
3. **公开数据就能做最小实验**：Binance 公共 klines 足够先给 first verdict；
4. **就算短周期不直接赚钱，也能反推出 desk 该不该继续做 residualization / beta-neutral ranking 这条线。**

## 3.5) 策略拆解（必填）
- 方向属性：**横截面 / 相对价值 / 逆势**
- 基础 alpha：**BTC-beta-neutral residual loser-bounce / winner-fade**
- regime：**更适合 residual shock 真有“单币偏离”含义的时段，不适合纯市场单边挤压时硬做**
- filter / veto：**只做 residual 绝对值够大的一端；可加成交额、news、单腿独立催化 veto**
- risk / sizing / execution overlay：**market-neutral gross cap、EMA smoothing、cost ladder、time stop、腿间成交同步控制**

## 4) 最小可复现实验（本轮已跑）
### 数据源
- Binance USDⓈ-M Futures `klines` API
- URL：<https://fapi.binance.com/fapi/v1/klines>
- 公开性：公开可得
- 更新频率：按 bar 更新

### 本轮口径
- universe：`BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, DOGEUSDT`
- `15m`：近 `180d`
- `5m`：近 `45d`
- 公共脚本：`reports/artifacts/quant_digests/2026-04-17_betaneutral_residual_reversal_probe.py`

### 关键数据点
#### 15m：有 gross edge，但成本线很薄
best-net 配置（`beta_window=48`, `residual>|q95|`, `ema=24`）结果：
- 平均 **gross `+0.132 bps/bar`**
- 平均 **net `-0.235 bps/bar`**（按 round-trip `8 bps`）
- 平均 turnover `0.0458`
- 累计 gross 约 **`+24.29%`**，累计 net 约 **`-34.05%`**
- 对应 break-even 成本大约只有 **`2.88 bps` round-trip**

#### 5m：更接近成本线，但仍未过线
best-net 配置（`beta_window=96`, `residual>|q98|`, `ema=36`）结果：
- 平均 **gross `+0.0348 bps/bar`**
- 平均 **net `-0.0810 bps/bar`**（按 round-trip `8 bps`）
- 平均 turnover `0.0145`
- 累计 gross 约 **`+4.40%`**，累计 net 约 **`-10.16%`**
- break-even 成本约 **`2.41 bps` round-trip**

人话：

> **短周期 transfer 后，这条线还没死成纯噪音——gross 仍是正的——但它已经被摩擦压成“只有超低费率/更好执行”才可能活的 pocket。**

## 5) 风险与保留意见
- repo 本体是 `4H` 组合，不是为 `5m/15m` 直接写的；本轮只是 portability probe。  
- 当前结果说明：**alpha 本体还有信息，但 production 生死线已经从“信号对不对”转成“能不能把 round-trip 压到 ~2.5bps 附近”。**  
- 这条线不适合被伪装成单腿方向策略；它更像 **market-neutral basket / router / residualization module**。  
- 如果遇到单币独立消息、listing、funding/liq stress，beta-neutral 残差并不等于可回归，必须有 veto。  

## 6) 下一步怎么测（最重要）
1. **不要继续裸跑全市场**，先缩到 `ETH/SOL/BNB/XRP/DOGE` 这类活跃腿，BTC 只做 hedge leg。  
2. **先测“更极端 residual 才开仓”**：`q98~q99 residual shock`，而不是中等偏离也做。  
3. **把 `15m signal` 和 `5m execution` 分层**：高一级定义 residual shock，低一级找更省摩擦的腿间成交。  
4. **加 execution realism**：maker share、分腿滑点、news veto、同币 cluster gross cap。  
5. **先输出 friction ladder**：`1 / 2 / 3 / 4 / 6 / 8 bps`，因为这题当前最关键的问题已经不是方向，而是成本门槛。  

## 7) 本轮产物
- `research/quant_digests/2026-04-17_2257_btcbetaneutral-residual-reversal-basket-alpha.md`
- `reports/artifacts/quant_digests/2026-04-17_betaneutral_residual_reversal_probe.py`
- `reports/artifacts/quant_digests/2026-04-17_betaneutral_residual_reversal_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-17_betaneutral_residual_reversal_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-17_betaneutral_residual_reversal_probe_portfolio_timeseries.csv`

## 8) 来源
1. gm-clara. (2025). *Statistical Arbitrage in Cryptocurrencies*. GitHub repo.  
   Readable URL: <https://github.com/gm-clara/Stat-Arb-in-Crypto>
2. `Reversal - Time Horizon.ipynb`（repo notebook）: <https://github.com/gm-clara/Stat-Arb-in-Crypto/blob/main/Reversal/Reversal%20-%20Time%20Horizon.ipynb>
3. `Stat Arb in Crypto.pdf`（repo bundled report）: <https://github.com/gm-clara/Stat-Arb-in-Crypto/blob/main/Stat%20Arb%20in%20Crypto.pdf>
4. Binance USDⓈ-M Futures Klines API（public）: <https://fapi.binance.com/fapi/v1/klines>
