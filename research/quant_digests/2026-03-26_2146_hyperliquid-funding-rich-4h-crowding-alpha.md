# 别把 Hyperliquid funding screener 只读成 `long cheap / short rich` carry：这份 2026 新 repo 更该先测的是「richest-funding 4h crowding continuation」，且必须先扣 funding cashflow
- 时间：2026-03-26 21:46 UTC
- 类型：2026 GitHub 新仓库 + Hyperliquid 公共 funding/ohlcv 数据 + 本地最小快检
- 主题类型：raw alpha
- 基础 alpha：每小时刷新 funding 横截面；做多 funding 最贵的 top-5、做空 funding 最便宜的 bottom-5，持有 `4h`（先计 price PnL，再诚实扣未来 funding cashflow 与交易成本）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/funding/carry/crowding/continuation/cross-sectional/relative-value/hyperliquid/public-data/hourly/4h/15m/5m/repo/external-data/cost
- 证据类型：repo source audit + 本地公共数据最小实验（含 funding cashflow）

## 1. 这次看了什么
先回答 base alpha：**这次真正值得 intake 的不是经典 `long cheap funding / short rich funding` carry，而是一个更贴近短周期 desk 的旁支——`richest funding continuation`。**

主材料是 **`exo-trading/crypto-carry-screener`（GitHub, 2026）**。这个 repo 表面上是在做 Hyperliquid funding 看板，但把源码拆开看，真正有价值的地方不是网页，而是它已经把三件事搭好了：

- **公开可拿的数据管道**：逐币 `fundingRate`、逐小时 `ohlcv`；
- **现成的 signal primitive**：`current / 1d / 3d / 5d` funding 排名；
- **最基础的 liquidity context**：小时成交额可滚成 `ADV` 过滤。

也就是说，这不是一篇“解释资金费率是什么意思”的综述，而是一个**可直接落地成完整横截面 raw alpha 最小实验**的 fresh repo source。

但本轮最关键的 desk 化结论有两层：

1. **最近 30 天 Hyperliquid 公共样本里，price alpha 最强的不是 contrarian carry，而是 `long richest funding / short cheapest funding` 的 4 小时 continuation。**
2. **如果不把未来持仓期间的 funding cashflow 扣进去，这条线会被严重高估。** 扣完以后，`4h` 仍有剩余边，但 `1h` 基本死掉。

所以，这条线现在最诚实的读法不是“又一个 funding carry 看板”，而是：**一个每小时刷新、在 `15m` 层执行的 funding-crowding raw alpha 候选。**

## 2. 核心结论
### 2.1 repo 里真正有用的 3 个点
从 `market_data_collector.py` 与 `generate_website.py` 看，这个 repo 目前做的是：
1. 抓取 Hyperliquid 多币种 hourly `fundingRate`；
2. 计算 `current / 1d / 3d / 5d` annualized funding 排名；
3. 用小时 `volume_usd` 计算 `ADV`，把数据写成网站可读的 watchlist。

翻成人话：
- repo **已经给了信号和币池过滤的原料**；
- 但它**没有替你定义交易方向、持有期、仓位、成本与 funding 入账**；
- 所以 bot7 真正该做的不是复述网页，而是把它补成一套**可交易的最小完整策略**。

### 2.2 本轮最重要的 sign 结论
本地快检里，同一套公开数据如果直接做最朴素的双边组合：
- **反向经典 carry**：`long cheapest / short richest` → 最近样本里是负的；
- **crowding continuation**：`long richest / short cheapest` → 最近样本里是正的，而且 `4h` 比 `1h` 诚实得多。

这点很关键。它说明在当前 Hyperliquid 这段样本里，funding 更像**拥挤延续强度**，而不是立刻反身修正的 rich-vs-cheap pullback。

### 2.3 desk 化一句话结论
**对当前 `1m/3m/5m/15m` desk，更值得先测的不是“funding 便宜腿回归”，而是：每小时冻结一次横截面，做 `long top-5 funding / short bottom-5 funding`，在后续 `4 x 15m` 上分批执行与持有。**

## 3. 为什么和当前 desk 直接相关
- 这是**独立 raw alpha 家族**，不是再给别的 breakout / retest / momentum 策略找一个附属 veto。
- 它天然就是完整策略骨架：
  - **entry**：按 funding 横截面排名开仓；
  - **exit**：固定持有 `4h` / 到时重排；
  - **sizing**：等权或 inverse-vol；
  - **risk**：ADV、单币权重上限、sector cap、单小时 funding shock cap；
  - **cost**：手续费、滑点、以及**未来 funding cashflow 必须显式入账**。
- 它和最近已有的 `basis / funding dispersion / funding boundary` 线索不同：
  - 那几条更偏 **cheap-vs-rich carry**；
  - 这条在当前新样本里给出的 sign，反而更像 **funding-signed continuation**。

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / funding / crowding / relative-value / market-neutral
- 基础 alpha：同一时点上，当前 funding 更高的永续合约，在后续 `4h` 的价格相对表现强于 funding 更低的合约
- 主题类型：raw alpha
- regime：更适合 funding 横截面分布明显拉开、且流动性分层没有塌掉的时候
- filter / veto：新上市币、极低 ADV、极端单币 funding（避免 cashflow 吃掉全部 price alpha）、重大事件窗前后
- risk / sizing / execution overlay：先做 `top-5 vs bottom-5` 的 dollar-neutral / inverse-vol；执行建议放到 `15m` 或 `5m` 切片，不要假装 funding 是逐分钟主信号

## 4. 本地最小快检（Hyperliquid 公共数据）
### 4.1 数据与口径
- 数据源：`exo-trading/crypto-carry-screener` repo 公开暴露的两份原始 CSV
  - `funding_data_all_coins.csv`
  - `ohlcv_data_main.csv`
- 原始数据底层：Hyperliquid 公共市场数据
- 公开性：公开可得，无需私钥
- 更新频率：`1h`
- 本地样本：`2026-02-24 21:00 UTC ~ 2026-03-26 19:00 UTC`
- 币池过滤：
  - `3d ADV >= $1m`
  - 价格 `> 0.0005`
  - 剔除稳定币/稳定锚代理
- 组合定义：每小时排序，`top-5 vs bottom-5`
- 配权：`24h` realized vol inverse-vol
- 持有：`1h / 4h`
- 成本：先粗估 **8 bps round-trip**
- **关键诚实项**：不只算价格收益，也把未来持仓期间的 funding cashflow 入账

### 4.2 先看 price-only，会得到什么错觉
如果**只看价格 PnL，不扣 funding cashflow**：
- 最强组合是 **`current funding` + `4h hold` + `long richest / short cheapest`**
- 平均 **price alpha = +19.39 bps / 4h**
- gross annualized Sharpe 约 **8.10**
- gross win rate 约 **56.3%**

但这个读法不诚实，因为：
- 做多高 funding 腿通常要**付 funding**；
- 做空低/负 funding 腿很多时候也要**付 funding**；
- 不把这层现金流扣进去，等于把 signal 最核心的成本漏掉了。

### 4.3 扣完 funding cashflow 后，真正还能剩什么
把未来 `4h` funding 现金流加回后，再扣 `8 bps` round-trip：

**A. 最优可用读法：`current funding` + `4h hold` + `long richest / short cheapest`**
- 平均 **price PnL = +19.39 bps / 4h**
- 平均 **funding cashflow = -5.23 bps / 4h**
- 平均 **gross(after funding) = +14.16 bps / 4h**
- 平均 **net(after funding + trading cost) = +6.16 bps / 4h**
- annualized net Sharpe 约 **2.58**
- 胜率约 **55.2%**
- 样本条数：`716` 个 hourly rebalance points
- 平均可交易 universe：约 **58.9** 个币

**B. 更慢的平滑 funding（`3d/5d avg`）没有更好**
- `3d avg funding + 4h hold`：扣完 funding 与交易成本后只剩 **+1.89 bps / 4h**
- `5d avg funding + 4h hold`：扣完后变成 **-3.81 bps / 4h**

翻成人话：
- **最值钱的不是“慢 carry”，而是“当前 funding 极值”本身。**
- 这更像短期 crowding 强度，而不是中期 carry harvest。

**C. `1h` 版本不活**
- `current funding + 1h hold + long richest / short cheapest`
  - 平均 **price PnL = +4.46 bps / 1h**
  - 平均 **funding cashflow = -1.46 bps / 1h**
  - 平均 **gross(after funding) = +2.99 bps / 1h**
  - 扣 `8 bps` 交易成本后 **net = -5.01 bps / 1h**

所以它不是 1 小时里随便打都能活的 micro alpha，**更诚实的 pocket 在 `4h`，而不是 `1h`。**

### 4.4 和经典 cheap-vs-rich carry 的对照
同样一套样本，若按更传统的读法去做 **`long cheapest / short richest`**：
- `current funding + 4h hold`：**net = -22.16 bps / 4h**
- `current funding + 1h hold`：**net = -10.99 bps / 1h**

这说明至少在这段最新 Hyperliquid 样本里：
- **sign 没有站在 classical carry 那边；**
- 当前更值得留在研究池里的，是 **rich-funding continuation**，不是 cheap-leg mean reversion。

### 4.5 简单稳定性检查（按周）
最优配置（`current funding / 4h / rich-minus-cheap`）按周拆开：
- `2026-02-23/03-01`：**+12.15 bps / 4h net**
- `2026-03-02/03-08`：**-1.33 bps / 4h net**
- `2026-03-09/03-15`：**+7.17 bps / 4h net**
- `2026-03-16/03-22`：**+11.60 bps / 4h net**
- `2026-03-23/03-29`（未完周）：**-0.15 bps / 4h net**

所以这不是“周周碾压”的稳态机器，但也不是只靠单一一周撑起来。**它更像一个可继续压测的 pocket，而不是立即下 final verdict 的 always-on carry。**

## 5. 这条线现在最诚实的读法
### 5.1 它是什么
它是一个**每小时刷新、以 funding 横截面极值为触发的 4 小时 crowding continuation raw alpha**。

### 5.2 它不是什么
- 不是经典的 `long cheap / short rich` carry harvest；
- 不是逐根 `1m/3m/5m` 的 bar-by-bar 主信号；
- 不是只看价格 markout 就能下结论的“伪高 Sharpe funding 题材”。

### 5.3 对 `1m/3m/5m/15m` 的正确映射
更合理的 desk 读法是：
- **signal layer**：每小时更新一次 funding 横截面；
- **execution layer**：在后续 `4 x 15m` 或 `12 x 5m` 上分批完成建仓与减仓；
- **monitoring layer**：在更细粒度上看冲击、盘口厚度与 funding 结算现金流。

也就是说，它能服务短周期 desk，但**方式是“低频信号 + 高频执行”，不是硬把 hourly funding 伪装成 1m alpha 本体。**

## 6. 下一步怎么测（可直接执行）
1. **把 `1h signal / 15m execution` 真正跑出来。**
   - 信号冻结在整点；
   - 执行拆到后续 `4 x 15m`；
   - 比较 `immediate open`、`15m TWAP`、`5m TWAP` 三种冲击口径。
2. **把 funding cashflow 纳入统一回测账本。**
   - 当前这轮只是最小快检；
   - 下一轮必须把手续费、滑点、未来 funding cashflow 放进同一 `net PnL` 路径，不能分开看。
3. **做 `current funding` vs `1d/3d` 的 frozen-sign 对照。**
   - 当前看起来 `current` 最强；
   - 下一轮要验证这是不是样本偶然，还是说明短期 crowding 才是 alpha 本体。
4. **做 beta / sector / listing-age 约束。**
   - 看 edge 是不是只是长一篮子高 beta 热门币；
   - 同时剔除新币与极端单名币权重，看 sign 会不会塌。
5. **做 regime 切片。**
   - 先按 funding dispersion 高低分桶；
   - 再按 BTC 单边趋势 / 横盘状态分桶；
   - 回答这条线到底是 `trend-on crowd continuation`，还是更普适的横截面强弱排序。

## 7. 风险与保留意见
- 这轮主材料是 **fresh repo + public data**，不是学术论文；因此更像 `source intake + first verdict`，不是 final paper-grade replication。
- 当前样本只有最近约一个月，**sign 稳定性仍需更长窗口**验证。
- 当前还是小时级 public CSV，不含真正的盘口冲击、手续费档位与 maker/taker 细分；因此 `8 bps round-trip` 只是第一层粗估。
- funding 相关题材最容易犯的错误，就是只看 price markout 不看 funding 现金流；本轮已经纠正这点，但后续仍需把**结算时间点、持仓跨小时路径**建模得更细。

## 8. 来源
1. **exo-trading (2026), _crypto-carry-screener_**
   - Repo URL: https://github.com/exo-trading/crypto-carry-screener
2. **Repo source: `market_data_collector.py`**
   - Readable URL: https://raw.githubusercontent.com/exo-trading/crypto-carry-screener/main/market_data_collector.py
3. **Repo source: `generate_website.py`**
   - Readable URL: https://raw.githubusercontent.com/exo-trading/crypto-carry-screener/main/generate_website.py
4. **Hyperliquid Developer Docs**
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api

## 9. 本地复现产物
- `reports/artifacts/quant_digests/hyperliquid_funding_xs_carry_20260326_2140/summary.json`
- `reports/artifacts/quant_digests/hyperliquid_funding_xs_carry_20260326_2140/signal_grid.csv`
- `reports/artifacts/quant_digests/hyperliquid_funding_xs_carry_20260326_2140/signal_grid_with_funding.csv`
- `reports/artifacts/quant_digests/hyperliquid_funding_xs_carry_20260326_2140/best_timeseries.csv`
- `reports/artifacts/quant_digests/hyperliquid_funding_xs_carry_20260326_2140/best_with_funding_timeseries.csv`
- `reports/artifacts/quant_digests/hyperliquid_funding_xs_carry_20260326_2140/best_weekly_summary.csv`
