# 别把成交量只当确认层：这份 2025 新仓库更该先测的是「volume-weighted 横截面动量 + AVR flow hits」raw alpha，但 15m break-even 只在约 3.5 bps round-trip
- 时间：2026-03-25 02:20 UTC
- 类型：2025 GitHub 新仓库 + 近 5 年论文地基 + Binance Futures 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：横截面动量（`short-vs-long return spread`）乘以成交量/流动性强化后的强者延续
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-sectional/momentum/volume-weighted/flow-confirmation/abnormal-volume-ratio/binance/perp/cost/turnover/repo/paper/crypto/1m/3m/5m/15m
- 证据类型：工程仓库 + 论文证据 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“横截面强者恒强”，不是 volume filter 本身。**

主材料是 2025 仓库 `tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume`：它把 `77` 个 Binance 币种的短窗回报、长窗回报、波动标准化和短长成交量比拼成一个 **volume-weighted cross-sectional momentum** 分数，再用 `AVR`（abnormal volume ratio）做 flow confirmation，最后形成 long-only 组合。

## 2. 核心结论
- 这条线是**可独立复现的 raw alpha 候选**，因为 alpha 本体很清楚：`动量排序`；成交量只是把“谁更值得追”做再加权，而不是替代 alpha 本身。
- repo 的日频原始结果并不差：在 `2020–2025`、`77` 币、Binance 日线样本上，作者给出的最优组合是 `short=3 / long=150 / lag=11`，**gross Sharpe = 1.36**，相对 BTC 的 **alpha t-stat = 2.27**；walk-back 的 `2020–2023` 也还有 **Sharpe 1.29 / alpha t-stat 1.84**。
- 但我把 repo 语义直接映射到 **Binance Futures 15m**（`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/TRX`，`2025-11-01 ~ 2026-03-25`）后，结论变得更“desk 现实”：
  - **repo 风格 long-only 最优格点**（`sw=8 / lw=150 / lag=2`）在 **gross** 下还有 **Sharpe 2.32**、平均 **+0.209 bps/bar**；
  - 但按 **round-trip 10 bps** 扣成本后，变成 **Sharpe -4.27**、平均 **-0.385 bps/bar**；
  - 对应平均换手约 **0.119 notional/bar**，推回去算，**break-even round-trip cost 只有约 3.52 bps**。
- 我额外测了一个对称的 `long-short` 版本：gross 更高（**Sharpe 4.93**），但换手也更高，**break-even 也只到约 4.31 bps round-trip**，仍然很难覆盖常规 taker perp 成本。
- 翻成人话：**这条 alpha 本体大概率是有东西的，但它在短周期不是“方向不对”，而是“成本门太窄”。** 如果不能压低费用、降低换手，直接搬去 5m/15m perp 很容易被磨没。

## 3. 为什么和当前项目有关
- 它直接补的是我们当前更该累积的 **cross-sectional / relative value / raw alpha** 素材池，不是又回到 breakout / retest 老内循环。
- 它还提供了一个很有用的拆法：
  - alpha 本体：横截面动量排序
  - 增强层：`volume_short / volume_long`
  - confirmation：`AVR hits`（最近 5 根里至少 3 根异常放量）
  - execution 问题：换手与成本是否允许这条 alpha 留下净值
- 对 desk 来说，这很适合做成 **“先问 gross edge，再问 cost pocket”** 的快检模板，未来也能直接迁移到 `1m/3m/5m/15m` 的 multi-asset perp 研究框架里。

## 3.5 策略拆解（必填）
- 方向属性：横截面、多资产、默认 long-only；也可做 beta-hedged long-short 变体
- 基础 alpha：
  - `mu_short = rolling mean(ret, short_window)`
  - `mu_long = rolling mean(ret, long_window)`
  - `sigma = rolling std(ret, long_window)`
  - `base_score = sqrt(short_window) * (mu_short - mu_long) / sigma`
- volume/flow 增强：
  - `vol_signal = rolling_mean(qvol, short) / rolling_mean(qvol, long)`
  - `score = base_score * vol_signal`
- confirmation：
  - `AVR = qvol / rolling_median(qvol, 20)`
  - `AVR > 2` 记作一次强 flow hit
  - 最近 `5` 根里至少 `3` 次 hit 才允许保留该资产权重
- sizing / weighting：
  - `tanh(score)` 压缩极端值
  - 截面归一化到 1.0 notional
  - repo 默认是 **long-only**（只保留正分数）
- execution：
  - repo 通过 `lag_shift` 模拟延迟执行
  - 短周期映射时，真正要命的不是是否 next bar 执行，而是 **是否能把换手压到费用线以下**

## 4. 可复刻的最小实验
- 研究假设：
  1) 横截面动量在 crypto 里依然成立；
  2) volume weighting 不是装饰，而是把“有流动参与的强者”从纯价格 winner 里筛出来；
  3) 但短周期成败主要取决于换手能否压过成本。
- 一个适合 `15m` 的最小切口：
  - 数据源：Binance Futures `fapi/v1/klines`（公开可得，15m 实时更新）
  - universe：先做 `10~20` 个高流动性 USDT perp
  - score：直接按 repo 公式先做 bar-close 版本
  - benchmark：先比 equal-weight perp basket，再比 BTC
- 最先看 4 个指标：
  1) `gross Sharpe`
  2) `net avg bps/bar` 或 `net avg bps/trade`
  3) `avg turnover / bar`
  4) `break-even round-trip bps`
- 这次本地最小快检已经给出一个非常明确的 desk 结论：
  - alpha 在 **gross** 下存在；
  - 但短周期版本的**成本容忍度只有 3.5~4.3 bps round-trip**，远比常规 taker perp 更苛刻。
- **下一步怎么测：**
  1) 先不改 alpha，先改换手：把 bar-bar 重平衡改成 `30m/60m`、或设置 `weight-delta threshold`，看 break-even 能否抬到 `6~8 bps`；
  2) 把 `short/long qvol ratio` 与 `same-clock RVOL / percentile volume shock` 做 A/B，验证 volume 应该做“乘数”还是“veto”；
  3) 对 long-only 版加一个最小 beta 对冲（如对冲 BTC 或 market basket），看能否保留 gross edge 同时减少“顺风 beta 假繁荣”。

## 5. 风险与保留意见
- repo 原始结果是**日频 long-only 组合**，并不是直接为 `5m/15m` perp 写的执行模板。
- 15m 映射快检表明，这条线最容易被误读成“信号不行”；但更真实的说法是：**信号在 gross 下还可以，问题主要出在 turnover / fee / slippage。**
- 如果后续只有在极低成本、maker 优先、或者低频重平衡条件下才成立，就应诚实把它定位为：
  - `低费率/低冲击 pocket alpha`
  - 或者 `cross-sectional sleeve`，而不是普适的高频主策略。

## 6. 来源
1) tim7park. (2025). *Crypto-Stat-Arb-CX-Momentum-x-Volume*（GitHub repository）.
   - Repo URL: `https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume`
   - Readable URL: `https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume/blob/main/README.md`
   - Key notebook URL: `https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume/blob/main/CX_MomXVol_StatArb.ipynb`

2) Huang, Z.-C., Sangiorgi, I., & Urquhart, A. (2024). *Cryptocurrency Volume-Weighted Time Series Momentum*. SSRN Electronic Journal.
   - DOI: `10.2139/ssrn.4825389`
   - Readable URL: `https://doi.org/10.2139/ssrn.4825389`

3) Fičura, M. (2023). *Impact of Size and Volume on Cryptocurrency Momentum and Reversal*. SSRN Electronic Journal.
   - DOI: `10.2139/ssrn.4378429`
   - Readable URL: `https://doi.org/10.2139/ssrn.4378429`

4) Fieberg, C., Liedtke, G., Metko, D., & Zaremba, A. (2023). *Cryptocurrency factor momentum*. Quantitative Finance.
   - Venue: `Quantitative Finance`
   - DOI: `10.1080/14697688.2023.2269999`
   - Readable URL: `https://doi.org/10.1080/14697688.2023.2269999`

5) Binance Futures API Docs（公开市场数据）
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

6) 本地最小快检 artifact（2026-03-25）
   - `reports/artifacts/quant_digests/volume_weighted_xs_momentum_probe_20260325/summary.json`
   - `reports/artifacts/quant_digests/volume_weighted_xs_momentum_probe_20260325/grid_net10bps.csv`
   - `reports/artifacts/quant_digests/volume_weighted_xs_momentum_probe_20260325/best_net10bps_returns.csv`
