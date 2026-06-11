# 别把「美股时段横截面反转」直接搬到大币 perp：这份 2026 新仓库更该先测的是 `US-session reversal` 的可迁移边界
- 时间：2026-03-24 12:35 UTC
- 类型：2026 GitHub 新仓库 + 经典论文地基 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：在美股开/收盘邻近窗口，做横截面 losers-vs-winners 的短时反转（cross-sectional mean reversion / relative value）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/cross-sectional/relative-value/us-session/intraday/reversal/transfer-test/cost/crypto/1m/3m/5m/15m/repo/paper
- 证据类型：仓库实现 + 论文地基 + 本地最小快检（可复现）

## 1) 先回答：这篇东西的 base alpha 是什么？
**base alpha = `US-session` 时段的横截面短时反转**：
- 先按信号窗收益给币种排序；
- 做多最弱分位（losers），做空最强分位（winners）；
- 在后续 30~90 分钟持有，赚“冲击后回归”的均值回复。

这不是纯 filter，而是可以单独跑的 raw alpha（entry/exit/多空/成本链路完整）。

## 2) 这次看了什么
主材料（新仓库）：
- **BNeillDickey (2026), _intraday-crypto-reversal-project_（GitHub）**
  - 核心实现放在 `Intraday_Crypto_Reversal_Project.ipynb`
  - 给了完整框架：
    - entry：按信号窗收益做横截面排名（long losers / short winners）
    - exit：固定持有窗（如 close-window: 16:15–17:00 ET）
    - sizing：等权、日度重排
    - risk/liquidity：time-varying ADV 过滤
    - cost：commission + spread + impact 三段成本

论文地基（仓库内引用）：
- Heston, Korajczyk, Sadka (2010) intraday cross-section
- Gao, Han, Li, Zhou (2018) market intraday momentum

## 3) 一句话结论 + 它怎么证明
**一句话结论：** 这条 raw alpha 值得保留在素材池，但要加一条“迁移边界”红线：它在中小币现货的 US-session 更像 alpha，在当前大币 perp 短周期口径里更像不可交易噪声。  
**一句话证据：** 新仓库给出完整策略与成本瀑布，我用 Binance 公共数据做最小迁移快检后，15m 与 5m 都是负的（成本后更差），说明“同一逻辑跨市场并不自动成立”。

关键数据点：
1. **仓库报告（spot crypto, close-window）**：测试段 gross Sharpe **5.85**，gross alpha **24.0 bps/day**（但作者也强调 impact 很重）。
2. **本地迁移快检（Binance 永续，12 个高流动币，15m，近 120 天）**：
   - close-window 反转：gross **-0.69 bps/day**，net(按 8bps roundtrip) **-8.69 bps/day**，gross/net Sharpe **-0.53 / -6.66**。
3. **同口径 5m 快频快检（8 个高流动币，近 45 天）**：
   - close-window 反转：gross **-0.38 bps/day**，net **-8.38 bps/day**，gross/net Sharpe **-0.58 / -12.59**。

## 4) 对当前短周期（1m/3m/5m/15m）的可用读法
- `15m`：
  - 可以当 **raw alpha 候选**，但优先在“更接近仓库假设”的宇宙（中小币、spot、US-session）验证；
  - 对大币 perp，当前证据偏负，先别直上。
- `5m`：
  - 目前迁移结果更差，默认先当“失败样本”记录，除非后续加微观结构过滤后翻正。
- `1m/3m`：
  - 不建议直接主跑；先作为 execution 层试验（如延迟、冲击、参与率）用来解释为何 5m/15m 失效。

## 5) 最小可复现实验（本轮已跑）
### 数据源（公开可得）
1. **Binance USDⓈ-M Futures Klines API**
   - URL: `https://fapi.binance.com/fapi/v1/klines`
   - 公开性：公开接口（无需 key）
   - 更新频率：支持 `1m/3m/5m/15m` 等
2. **GitHub 仓库 notebook**
   - `https://github.com/BNeillDickey/intraday-crypto-reversal-project`
   - 公开性：公开仓库

### 最小实验口径
- 15m（120 天）：12 个高流动 perp（BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC/TRX/BCH）
- 5m（45 天）：8 个高流动 perp
- 信号与持有：
  - close-window：`15:30–16:00 ET` 信号，`16:15–17:00 ET` 持有（5m 版本做 `16:05–16:35 ET`）
  - morning-window：`09:30–10:00 ET` 信号，`10:15–10:45 ET` 持有
- 组合：横截面分位 long/short（多空等权、日度重排）
- 成本：最小诚实口径先用 **8 bps roundtrip/day**（固定）

## 6) 这次本地产物
- `reports/artifacts/quant_digests/session_xs_reversal_probe_20260324/summary.json`
- `reports/artifacts/quant_digests/session_xs_reversal_probe_20260324/close_daily.csv`
- `reports/artifacts/quant_digests/session_xs_reversal_probe_20260324/morning_daily.csv`
- `reports/artifacts/quant_digests/session_xs_reversal_probe_20260324/close_daily_5m.csv`
- `reports/artifacts/quant_digests/session_xs_reversal_probe_20260324/session_xs_reversal_probe.py`

## 7) 风险与解释（为什么会“仓库强、迁移弱”）
1. **市场结构错位**：仓库的“有效区”更接近中小币 spot 的流动性与参与者结构；大币 perp 更接近高效率市场。  
2. **alpha 与容量耦合**：这类反转常依赖“可被冲击但未被完全套利”的资产段，迁移到高流动大币可能被直接抹平。  
3. **成本模型差异**：固定 8bps 只是最小诚实近似，若再加真实冲击/滑点，结论只会更保守。

## 8) 下一步怎么测（具体）
1. **做“同市场复刻”对照**：按仓库方法转到 Binance spot + 中小币 + ADV 过滤，先确认原始边是否能重现。  
2. **做“宇宙分层”**：同一规则按流动性分层（top / mid / tail ADV）分别测，画出 alpha-容量边界。  
3. **做“反转 vs 动量”双臂**：同窗口下比较 reversal 与 momentum，避免把时段效应误判为单一方向。  
4. **做执行门控最小集**：加入 participation cap、最大可交易名义、单次冲击上限，再看是否仍为负。

## 9) 来源（paper / repo）
1. **BNeillDickey (2026). _intraday-crypto-reversal-project_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project  
   - Repo URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project

2. **Heston, S. L., Korajczyk, R. A., & Sadka, R. (2010). _Intraday Patterns in the Cross-Section of Stock Returns_. Journal of Finance.**  
   - Venue: Journal of Finance  
   - DOI: `10.1111/j.1540-6261.2010.01573.x`  
   - Readable URL: https://doi.org/10.1111/j.1540-6261.2010.01573.x  
   - Repo URL: N/A

3. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market Intraday Momentum_. Journal of Financial Economics.**  
   - Venue: Journal of Financial Economics  
   - DOI: `10.1016/j.jfineco.2018.05.009`  
   - Readable URL: https://doi.org/10.1016/j.jfineco.2018.05.009  
   - Repo URL: N/A

4. **Svogun, I., & Bazán-Palomino, W. (2022). _Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?_. Journal of International Financial Markets, Institutions and Money.**  
   - Venue: JIMFIM  
   - DOI: `10.1016/j.intfin.2022.101601`  
   - Readable URL: https://doi.org/10.1016/j.intfin.2022.101601  
   - Repo URL: N/A
