# 别把 pairs 只写成 z-score 开平：这篇 2025 论文更值钱的是「cointegration 均值回归 + lookback/vol/stop」完整策略骨架
- 时间：2026-03-23 15:19 UTC
- 类型：近 5 年论文 + 作者开源仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：pairs / stat-arb / relative-value mean reversion（cointegration spread 偏离后回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/lookback/vol-filter/trailing-stop/cost/crypto/5m/15m
- 证据类型：论文题录/摘要 + 工程证据 + 本地快检（可复现）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的基础 alpha 不是“参数优化”本身，而是 cointegration spread 的均值回归。**

这次主看 **Rafael Baptista Palazzi (2025)** 的 *Trading Games: Beating Passive Strategies in the Bullish Crypto Market*，以及作者同步公开的 R 仓库 `trading-games-crypto`。对我们 desk 真正值钱的不是 headline“跑赢被动持有”，而是它把一条 **可以直接拆成 entry / exit / risk / cost 的 pairs 完整骨架**写出来了：
- spread 定义：`log(P_y) - gamma * log(P_x)`
- entry：`z-score` 超阈值开仓
- pair sizing：按 `gamma` 做 beta-neutral 权重
- risk：volatility filter + adaptive trailing stop + min holding period
- cost：交易成本直接入回测

## 2. 核心结论
- **一句话核心结论：** 对当前短周期 desk，更值得抄的不是“pairs 会不会均值回归”这种老答案，而是 **如何把这条 raw alpha 包装成一个成本诚实、风控完整、可以直接 first-verdict 的策略骨架**。
- **一句话证明方式：** 论文摘要给出样本与总体结论，作者 repo 直接公开了策略函数与参数语义；我又用 Binance 15m 公共数据做了最小快检，看这条骨架能不能往我们口径映射。

最值得记住的 3 个数据点：
1. 论文样本是 **10 个主流 crypto，2019-01 到 2024-05**。
2. 作者 repo README 报告该策略约有 **年化 Sharpe ≈ 2.0**、**年化收益 ≈ 71%**，且声称相对 buy-and-hold 与 momentum 更优。
3. 我这边把它压到 Binance **15m** 后，若做“全 pair 广撒网”，**28 个候选 pair 平均 gross 只有 +0.52 bps/bar，但 net 变成 -0.50 bps/bar**；说明这条 alpha 不是“全池自动赚钱”，而是**pair governance 很关键**。

## 3. 为什么和当前 desk 直接相关
- 这是 **独立 raw alpha 家族**，不是继续给 breakout/retest 找一个附件过滤层。
- 和当前 `1m/3m/5m/15m` 节奏兼容：pair 形成、z-score、退出、成本都能快速写成最小实验。
- 它比很多“只给 filter 不给 alpha”的材料更适合现在，因为这条线天然就是完整策略：
  - entry：`|z| > threshold`
  - exit：回归到中线 / 反向信号 / max-hold / trailing stop
  - sizing：beta-neutral 或 dollar-neutral
  - risk：vol veto、结构断裂停机、pair 下线
  - cost：双腿手续费 + 滑点 + 借贷/资金费率（若用 perp）

## 3.5 策略拆解（必填）
- 方向属性：relative-value / stat-arb / market-neutral
- 基础 alpha：当 cointegration spread 明显偏离自身滚动均值时，押注其向均值收敛
- regime：优先在 pair 关系稳定、波动未失控、流动性足够时启用
- filter / veto：事件窗口、波动爆表、相关结构断裂、pair 半衰期飘移时停机
- risk / sizing / execution overlay：按 `gamma` 中性配比、限制最大持有时长、显式计成本、优先 maker / 分批成交

## 4. 本地最小快检（Binance 公共数据）
### 4.1 数据与口径
- 数据源：Binance Spot 公开 klines
- 公开性：公开可得，无需私钥
- 更新频率：15m
- 样本：最近 `3000` 根 15m bars
- 币池：`BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK`
- 训练/测试：前 `60%` 估计 `gamma` 与 lookback，后 `40%` 看 OOS
- 粗成本：pair 层每次完整进/出按约 **16 bps round-trip** 的简化口径（实现中按 `position change` 计）

### 4.2 快检结果怎么读
**A. 广撒网版（28 个 pair，全池扫描）**
- 平均 **gross = +0.52 bps/bar**
- 平均 **net = -0.50 bps/bar**
- 最好的一对在 net 层也只有 **-0.16 bps/bar**

这说明：**pairs raw alpha 不是“拿一堆相关币做 z-score 就行”**。如果 pair formation 不严、成本处理不诚实，alpha 很容易只剩毛边。

**B. 收窄到更像样的 pair（固定 `lookback=192`, `z=0.7`）**
- `BTC-ETH`：**gross +0.49 bps/bar，net +0.25 bps/bar**，OOS 累计约 **+1.00%**
- `BNB-ADA`：**gross +1.12 bps/bar，net +0.80 bps/bar**，OOS 累计约 **+3.22%**

这组结果的读法是：
- **alpha 不是没有，但明显只活在少数 pair pocket 里；**
- repo 那套“动态 lookback + vol/risk overlay”的价值，恰恰在于帮你把“能做的 pair”与“不能碰的 pair”分开，而不是把所有 pair 一锅烩。

## 5. 下一步怎么测（可直接执行）
1. **先做 pair governance，不做全池平均。** 从 `BTC-ETH / BNB-ADA / SOL-LINK` 这类高流动性对开始。  
2. **三维网格先跑小的：** `lookback ∈ {64,128,192,256}` × `entry z ∈ {0.7,1.0,1.3}` × `exit z ∈ {0.0,0.2,0.4}`。  
3. **把 repo 的完整层补齐：** 在当前最优 pair 上逐个加入 `vol filter`、`max_hold`、`adaptive trailing stop`，看哪一层是真提升、哪一层只是减交易。  
4. **把 15m first verdict 通过的 pair 下钻到 5m / 3m。** 只下钻通过 15m 诚实门的 pair，不做全池盲扫。  
5. **显式画成本生存线：** 至少测 `8 / 16 / 24 / 32 bps round-trip` 四档，确认哪档开始失活。  

## 6. 风险与保留意见
- 论文正文页面当前被 Cloudflare 挡住；本轮对论文本身主要依赖 **Crossref 摘要 + 作者开源代码/README**，所以对论文细节不做超出可见证据的延伸解读。
- 作者 repo 的高收益结果是其样本与口径下的报告，不应直接外推到我们 15m crypto 生产口径。
- 本地快检已经表明：**全池平均不成立，局部 pair 才可能成立**。这条线若要进主池，必须附带严格 pair governance，而不是只保留 signal 本体。

## 7. 来源
1. **Palazzi, Rafael Baptista. (2025). _Trading Games: Beating Passive Strategies in the Bullish Crypto Market_. Journal of Futures Markets.**  
   - DOI: `10.1002/fut.70018`  
   - Readable URL: https://doi.org/10.1002/fut.70018
2. **Rafael Baptista Palazzi. (2025). _trading-games-crypto_. GitHub repository.**  
   - Repo URL: https://github.com/rafaelpalazzi/trading-games-crypto  
   - Readable URL: https://github.com/rafaelpalazzi/trading-games-crypto
3. **Palazzi, Rafael Baptista. (2024). _Trading Games: Beating Passive Strategies in the Bullish Crypto Market_ [Dataset]. Mendeley Data.**  
   - Readable URL: https://doi.org/10.17632/2kky7c6xkn.1

## 8. 本地复现产物
- `reports/artifacts/quant_digests/pairs_fullstack_probe_20260323/pair_summary.csv`
- `reports/artifacts/quant_digests/pairs_fullstack_probe_20260323/focused_pair_check.csv`
- `reports/artifacts/quant_digests/pairs_fullstack_probe_20260323/lookback_search.jsonl`
- `reports/artifacts/quant_digests/pairs_fullstack_probe_20260323/meta.json`
