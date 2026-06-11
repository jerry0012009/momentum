# 别把这份 multi-venue futures repo 只读成 funding/carry 大杂烩：对 short-cycle desk，更该先测的是「same-expiry cross-venue basis differential × venue-close convergence」这条 raw alpha

- 时间：2026-04-11 00:50 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `docs/methodology.md` + `docs/venue_comparison.md` + `strategies/futures_curve/multi_venue_analyzer.py`）+ Binance COIN-M / Bybit inverse futures 公共 `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**同一标的、同一到期日的 futures 在不同 venue 上会出现 basis 错位；当 `basis_A - basis_B` 明显偏离自己的历史带宽时，做多便宜 venue 的同 expiry future、做空更贵 venue 的同 expiry future，等 cross-venue basis spread 回归。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/cross-venue/futures/basis/same-expiry/calendar-arbitrage/binance/bybit/btc/eth/5m/15m/repo/public-data/cost/risk
- 证据类型：工程经验 + repo 策略说明 + 公共数据 portability probe

## 1. 这次看了什么
主材料还是 **Tamer Atesyakar / `abailey81/Crypto-Statistical-Arbitrage`** 这套 repo，但这次不再读 `synthetic futures`，而是单独拎 repo 里更容易被忽略的一支：

- `docs/methodology.md` 明写 **Strategy B: Cross-Venue Basis**：`Exploit CME premium over Binance, or Binance quarterly vs Hyperliquid perpetual`
- `strategies/futures_curve/multi_venue_analyzer.py` 直接把它写成 **Cross-Venue Calendar Arbitrage**：
  - `Spread = Basis_A - Basis_B`
  - `P&L = (Entry_Spread - Exit_Spread) × Notional - Costs`
  - `Entry when |Z_Score| > 2.0 and Net_Spread > Costs`
- `docs/venue_comparison.md` 还给了很实用的 venue 成本表：calendar spread 在 CEX 的 break-even spread 约 `0.16%`。

一句话核心结论：

> **比起继续把 repo 读成“funding/carry 全家桶”，更值得先落地的是：同 expiry 的 futures 跨 venue basis 会出现可回归错位，这是一条比普通 perp 价差更干净、又比单 venue curve 更贴近实盘的 relative-value raw alpha。**

一句话证明方式：

> **repo 给了明确的 z-score / cost-aware basis spread 壳；我再用 Binance 与 Bybit 同到期季度合约做 `5m/15m` public-data probe，检查极端 spread 后未来 `15m/60m` 是否出现显著 spread-close。**

## 2. 为什么它值得单独写，而不是算旧题重炒
这条线和最近已经写过的几类东西都不一样：

- 它**不是** `perp-perp` 的纯跨所瞬时价差回归；这里两条腿都带**相同到期日**，所以 carry / expiry 已被钉住，噪音更少。
- 它**不是** `adjacent-maturity calendar spread`；那条看的是**同 venue 不同期限**，这条看的是**同期限不同 venue**。
- 它也**不是** `synthetic future` 替代；那条在比较 `dated future vs cheap perp carry`，这条更像 **same-expiry carrier mispricing**。

所以它的 base alpha 很清楚：

> **law-of-one-price 在 crypto futures venue 之间并不总成立；同 expiry 的 basis spread 会围绕某个相对稳定区间波动，极端时更容易向中位带回归。**

这就是 raw alpha，不是 filter / regime / overlay。

## 3. repo 里最值得拿走的，不是“多 venue 很复杂”，而是这 3 个可执行零件
### 3.1 信号定义很干净
`multi_venue_analyzer.py` 给的核心不是 fancy ML，而是最朴素的 cross-venue spread：

- `Basis_A - Basis_B`
- rolling `z-score`
- 只在 `Net_Spread > Costs` 时动手

这跟 desk 真正要的东西很一致：先看**有没有错价**，再看**扣成本后还有没有肉**。

### 3.2 它天然带 venue 选择，而不是默认所有 venue 平权
repo 额外给了 venue score：

- funding advantage
- liquidity score
- cost score

这很关键，因为同样是 spread-close，`Binance vs Bybit` 和 `Binance vs 某个更薄的 venue` 不是一个游戏。alpha 本体可以一样，但 **execution likelihood** 完全不同。

### 3.3 它适合 short-cycle desk 的原因，不是持有期短，而是 admission 很快
这种 cross-venue basis 交易，本体未必每根 `1m` 都有信号；但它非常适合拿 `5m / 15m` 做：

- spread 监控
- entry admission
- time-stop / mean-revert exit
- venue-staleness veto

也就是说：**alpha 本体是 relative-value，short-cycle 的价值在于更快识别“错位真的在关”还是只是坏报价。**

## 4. 本地 portability probe：Binance / Bybit 同到期季度 futures 上，这条线有没有 first verdict？
我用公开可抓的同 expiry 交割合约做了最小快检：

- Binance COIN-M：`BTCUSD_260626`、`ETHUSD_260626`
- Bybit inverse futures：`BTCUSDM26`、`ETHUSDM26`
- 统一 spot 锚：Binance spot `BTCUSDT / ETHUSDT`
- 频率：`5m` 与 `15m`
- 定义：
  - `basis_v = (F_v / S - 1) × 365 / DTE`
  - `basis_spread = basis_bybit - basis_binance`
  - 同时记录可交易意义更强的 `price_spread_bps = (F_bybit / F_binance - 1) × 10000`
- 信号：`price_spread_bps` 的 rolling z-score，取 `|z| >= 2`
- 指标：未来 `15m / 60m` 的 **signed spread-close bps**（正值表示朝均值回归）

### 4.1 5m 口径的 first verdict
`reports/artifacts/literature/crossvenue_sameexpiry_futures_basis_probe_summary_2026-04-11.csv` 显示：

- **BTC**
  - `5m` 中位绝对 price spread 约 `4.98 bps`
  - `p95` 约 `15.74 bps`
  - 中位 basis spread 约 `+16.27 bps annualized`
  - 当 `|z|>=2` 时，未来 `15m / 60m` signed spread-close 约 `+18.06 / +23.20 bps`
  - 胜率约 `96.7% / 100%`
- **ETH**
  - `5m` 中位绝对 price spread 约 `11.26 bps`
  - `p95` 约 `33.38 bps`
  - 中位 basis spread 约 `+48.16 bps annualized`
  - 当 `|z|>=2` 时，未来 `15m / 60m` signed spread-close 约 `+29.03 / +35.42 bps`
  - 胜率约 `83.6% / 98.2%`

### 4.2 15m 口径也没塌
同一份 summary 里，`15m` 直接做 signal 也还成立：

- **BTC 15m signal**：未来 `15m / 60m` signed spread-close 约 `+17.04 / +22.39 bps`
- **ETH 15m signal**：未来 `15m / 60m` signed spread-close 约 `+30.84 / +40.70 bps`

这说明它不是只能在最噪的 `1m` 上勉强成立；至少在 `5m / 15m` 的 close-proxy 下，**same-expiry cross-venue spread-close** 还有 first-pass 生命迹象。

## 5. 但这轮最该记住的不是“数字很好看”，而是它很可能仍被 close-proxy 高估
这里必须诚实：

- 当前 probe 用的是 **candle close proxy**，不是同步可成交 bid/ask；
- 没有显式处理两腿先后成交、排队失败、单腿滑点、手续费层级；
- inverse futures 的 contract spec 与美元张数也还没做资金占用统一换算。

所以这些数字**不能直接当 production PnL**。

更合理的读法是：

> **若连 close-proxy 下都看不到 spread-close，那这条线可以直接淘汰；现在看到的是它在 public bar 数据下还有明显回归倾向，因此值得进下一轮 executable-BBO 检验。**

## 6. 为什么它和当前 desk 直接相关
这条线的价值不只是一条新 alpha，还在于它能补当前素材池里的一个缺口：

- pairs / stat-arb 我们已有很多，但多数是**不同资产**；
- funding / carry 我们也有不少，但多数是**perp-vs-spot** 或 **perp-vs-perp**；
- 这条是更靠近传统期货 desk 思维的：**同 expiry、同 underlier、不同 venue 的 basis close**。

如果这条能活，它就很适合当：

- crypto futures RV sleeve
- carry desk 的 admission layer
- cross-venue quote-routing 的上层信号

## 6.5 策略拆解（必填）
- 方向属性：relative value / stat-arb / market-neutral-ish
- 基础 alpha：同 expiry cross-venue futures basis differential mean reversion
- regime：只在流动性正常、距离到期仍足够远、venue health 正常时启用
- filter / veto：`|z|` 不够大不做；`net spread <= fees+slippage` 不做；stale quote / API 异常 / funding 结算窗口不做
- risk / sizing / execution overlay：maker-first 优先；两腿 notional 配平；限制单 venue gross；设置 `time stop + spread stop + venue incident kill-switch`

## 7. 可复刻的最小实验
### 数据源 / 公开性 / 更新频率
- Binance COIN-M futures：公开 REST
- Bybit inverse futures：公开 REST
- Spot anchor：公开 REST
- 更新频率：至少可做到 `1m`，本轮先用 `5m / 15m`

### 最小研究假设
> 当同标的同 expiry futures 的 cross-venue `price_spread_bps` 偏离 rolling 带宽 `2σ` 以上时，未来 `15m ~ 60m` 更可能向均值回归，而不是继续单边扩张。

### 最小回测切口
- 资产：BTC / ETH
- 标的：`260626` 季度合约
- 频率：`5m` 与 `15m`
- 指标优先看两项：
  1. `signed spread-close bps`
  2. `executable cost ladder` 后是否仍为正

## 8. 下一步怎么测
下一步不要急着扩 universe，我会先做 3 件最值钱的事：

1. **把 close proxy 升级成 executable BBO**
   - 同步抓 Binance / Bybit best bid/ask
   - 分开算 `taker+taker`、`maker+taker`、`maker+maker` 三套净 edge
2. **把持仓改成真正的 one-trade-at-a-time shell**
   - `|z|>=2` 入场
   - `|z|<=0.5` 或 `60m` time stop 出场
   - 显式扣 `4/8/12 bps` friction ladder
3. **扩到 BTC/ETH 的近季与次季**
   - 检查这是不是只对当前 `260626` 有效
   - 还是一种可复用的 same-expiry futures RV 结构

如果 executable 版本在 `maker+taker` 下仍能留下正的 `15m/60m` spread-close，那这条线就值得进入 clean replication 队列；如果一上 bid/ask 就塌，那它更适合当 **venue-staleness / dislocation monitor**，而不是独立交易壳。

## 9. 来源
- Tamer Atesyakar. *Crypto-Statistical-Arbitrage* (GitHub repo).
  - Repo URL：`https://github.com/abailey81/Crypto-Statistical-Arbitrage`
  - README：`https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/README.md`
  - Methodology：`https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/docs/methodology.md`
  - Venue comparison：`https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/docs/venue_comparison.md`
  - Multi-venue analyzer：`https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/strategies/futures_curve/multi_venue_analyzer.py`
- 本地 portability artifacts：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/crossvenue_sameexpiry_futures_basis_probe_summary_2026-04-11.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/crossvenue_sameexpiry_futures_basis_probe_detail_2026-04-11.csv`
