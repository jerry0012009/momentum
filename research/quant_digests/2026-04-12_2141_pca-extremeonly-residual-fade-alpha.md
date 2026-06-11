# 别把这份 2026 crypto PCA stat-arb repo 只读成 Avellaneda-Lee 复刻：对 short-cycle desk，更该先测的是「top-residual extreme only × clock-matched s-score fade」这条 raw alpha

- 时间：2026-04-12 21:41 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/stat-arb/basket/pca/eigenportfolio/ou/residual/s-score/mean-reversion/cross-sectional/relative-value/top-extreme-only/clock-matched/binance-perpetual/5m/15m/repo/public-data/cost/risk
- 证据类型：2026 GitHub repo source audit（GitHub API + `README.txt` + `main.py` + `src/pca_engine.py` + `src/residual_model.py` + `src/ou_estimator.py` + `src/s_score.py` + `src/strategy.py` + `src/backtester.py`）+ 2010 *Quantitative Finance* 母体论文元数据 + Binance USDⓈ-M `5m/15m` public-data probe

- 主题类型：raw alpha
- 基础 alpha：先用 rolling PCA 把市场共同因子剥掉，再看各币 residual 的 OU 型均值回归；当某个币相对 basket 明显“过贵/过便宜”时，做 `short rich / long cheap`，赌的是**因子中性后的相对价值回归**，不是押市场方向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这轮我选的不是又一篇泛泛的 pairs 论文，而是一个很新的 repo：

### 主材料（repo）
- **Sophie Lan (2026)**
- **Title**：*crypto-pca-statarb*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL / Repo URL**：<https://github.com/sophie-lan/crypto-pca-statarb>
- **Repo metadata**：创建 / 最近 push 都是 **2026-03-04**

### 地基论文（不是本轮主角，但 repo 明确依它搭建）
- **Marco Avellaneda, Jeong-Hyun Lee (2010)**
- **Title**：*Statistical arbitrage in the US equities market*
- **Venue**：*Quantitative Finance*
- **DOI**：<https://doi.org/10.1080/14697680903124632>
- **Readable URL**：<https://doi.org/10.1080/14697680903124632>

这轮最值得 desk intake 的，不是“PCA 也能做 stat-arb”这句空话，而是下面这句更像交易语言的话：

> **不要把所有 residual dislocation 一股脑全做；对 short-cycle desk，更像真钱入口的是“只做最极端那一撮因子中性偏离”。**

也就是说，这轮虽然材料表面上是一个完整 PCA-OU book，但对我们更值钱的旁支，其实是：
- 保留它的 **PCA residual / OU / s-score** 信号骨架；
- 丢掉它“整本书都做”的直译思路；
- 先测 **top residual extreme only** 的快节奏相对价值 fade。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
很清楚，不需要硬猜：

> **基础 alpha = 因子中性后的 residual mean reversion。**

翻成人话：
1. 先用 PCA 提取市场共同波动；
2. 再把每个币对这些共同因子的暴露回归掉；
3. 剩下的 residual 若满足 OU 型回归，说明它更像“短暂失衡”而不是“新趋势”；
4. 当 s-score 太极端时，做相对价值回归。

所以它是：
- `raw alpha`
- `stat-arb / relative-value / basket mean reversion`
- 不是 filter
- 不是 regime
- 也不是纯 risk overlay

## 3. 为什么这轮值得写
### 3.1 它补的是“factor-neutral residual fade”这条素材，不是又一条普通 pair spread
最近研究池里 pairs / basket 已经不少，但很多还是：
- 先挑一对或几对资产；
- 再围绕某个固定 spread 做 admission；
- 本质上仍比较依赖 pair selection。

这份 PCA repo 的不同点在于：
- 它不是先指定 pair；
- 而是先从整个 basket 的共振里抽出主因子；
- 再看谁相对共同因子偏离得最夸张。

这对 desk 的价值是：
> **它给的是“先 market-neutral / factor-neutral，再抓 residual 回归”这条更通用的 stat-arb 原语。**

### 3.2 它比“整本书照搬”更有价值的地方，恰恰是让我们看清了该删什么
这类 repo 最容易犯的错，就是直接把论文口径 whole-book 搬到短周期 perp：
- 全 universe 同时开很多腿；
- 换手高；
- 看起来 market-neutral，实际上把执行噪音也一起抱回来了。

我这次最重要的结论反而是：
- **literal full-book 直译版不值得直接上线；**
- **但 extreme-only 旁支值得继续深挖。**

这正符合你给的灵活规则：
> 不必死抄 headline；repo 里更适合 desk 的旁支，可以单独拎出来。

## 4. repo 到底实现了什么
这份 repo 的价值很高，因为它不是“讲思路”，而是把整条链写全了。

### 4.1 `src/pca_engine.py`：rolling PCA 因子提取
repo 在每个时间点：
- 先取过去 `240` 小时窗口；
- 对 universe 做 log return 标准化；
- 在相关矩阵上做 PCA；
- 取前两个主成分；
- 形成 factor return / eigenportfolio。

翻成人话就是：
> **先把“市场一起涨一起跌”和“第二层共同波动”抽出来。**

### 4.2 `src/residual_model.py`：每个币回归到前两主成分上
repo 对每个 token 做：
- `r_i = beta0 + beta1 * F1 + beta2 * F2 + eps_i`
- 再把 `eps_i` 去均值后保留成 residual series。

这一步定义得很重要：
- alpha 不是原始 return 的回归；
- alpha 是 **剥掉共同因子后的 idiosyncratic 偏离**。

### 4.3 `src/ou_estimator.py` + `src/s_score.py`：把 residual 变成可交易阈值
repo 没停在“有 residual”这一步，而是继续：
- 对 residual 累积过程 `X_t` 拟合离散 OU；
- 估 `kappa / m / sigma_eq`；
- 再算 `s = (X_t - m) / sigma_eq`。

这比直接 z-score spread 更像一个可迁移的 desk 组件，因为它回答的是：
- 不是“偏了多少”；
- 而是“偏离相对它自己的平衡波动到底有多夸张”。

### 4.4 `src/strategy.py`：完整开平仓阈值已经写好
repo 默认阈值：
- open long：`s <= -1.25`
- open short：`s >= 1.25`
- close long：`s >= -0.75`
- close short：`s <= 1.0`

这说明它不是只给研究信号，而是已经给出：
- entry
- exit
- 持仓状态机

### 4.5 `src/backtester.py`：但它默认没把费用问题当核心敌人
README 直接写了：
- **不计 transaction costs / slippage**
- 假设按 hourly close 完美成交

这恰恰是 desk 读它时最该警惕的地方：
> **信号骨架可取，whole-book 执行假设不可照搬。**

## 5. 最小 public-data probe：真正值得 desk 先测的，是 extreme-only 分支
为了避免只做 repo 读后感，我用 Binance USDⓈ-M 公共 `klines` 做了一个 portability probe。

### 5.1 数据口径
- 数据源：Binance Futures public `fapi/v1/klines`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT / DOGEUSDT / BNBUSDT`
- 频率：
  - `15m`：样本 `2025-10-01` 到 `2026-04-12 21:15 UTC`
  - `5m`：样本 `2026-02-01` 到 `2026-04-12 21:15 UTC`
- 口径：
  - `15m` 用 `240` bars，约等于 repo 的 `60h` lookback
  - `5m` 做 **clock-matched** 移植，用 `720` bars，仍约 `60h` lookback
- 公开性：完全公开可抓
- 更新频率：分钟级 / 5 分钟 / 15 分钟可直接刷新

产物已落地到：
- `reports/artifacts/literature/pca_residual_ou_probe_summary_2026-04-12.csv`
- `reports/artifacts/literature/pca_residual_ou_events_15m_2026-04-12.csv`
- `reports/artifacts/literature/pca_residual_ou_events_5m_2026-04-12.csv`
- `reports/artifacts/literature/pca_residual_ou_scores_15m_2026-04-12.csv`
- `reports/artifacts/literature/pca_residual_ou_scores_5m_2026-04-12.csv`

## 6. probe 结果怎么读
### 6.1 先说坏消息：literal full-book 15m 直译版明显不过线
我先按 repo 的 opening / closing 阈值，做了一个“全书都做”的 15m 直译版快测。

结果：
- gross 平均收益约 **`-0.09 bps/bar`**
- gross 累计约 **`-15.55%`**
- 平均换手约 **`0.163x/bar`**
- 若按 **`8bp round-trip`** 粗算，净平均约 **`-0.74 bps/bar`**
- 若按 **`12bp round-trip`** 粗算，净平均约 **`-1.07 bps/bar`**

这句要说得很直接：

> **PCA residual 这套东西不是没 alpha；但“看到 dislocation 就整本书一起上”这件事，在 short-cycle perp 上先被换手打死了。**

### 6.2 再说真正值钱的部分：extreme-only 事件口径在 5m 上是正的
我把 probe 改成更 desk 化的分支：
- 每个时点只看 **最贵** 与 **最便宜** 那两端 residual；
- 只有当 `richest s >= 1.25` 且 `cheapest s <= -1.25` 时，才记一次事件；
- 做 `long cheap / short rich`；
- 看未来固定窗口的相对收益与 s-score 收缩。

#### 5m（clock-matched 720-bar lookback，向前看 24 bars ≈ 2h）
- 事件数：**`7,613`**
- 命中率：**`55.8%`**
- 平均 pair return：**`+2.64 bps`**
- 中位数 pair return：**`+3.33 bps`**
- 平均 `|s|` 收缩：**`0.347`**
- 中位数 `|s|` 收缩：**`0.318`**

翻成人话：
> **把 repo 直译成 whole-book 不行，但只做最极端 residual，5m 上已经看到比较像样的回归味道。**

### 6.3 15m 不是完全没东西，但强度明显更弱
#### 15m（240-bar lookback，向前看 8 bars ≈ 2h）
- 事件数：**`6,762`**
- 命中率：**`52.5%`**
- 平均 pair return：**`-0.27 bps`**
- 中位数 pair return：**`+1.34 bps`**
- 平均 `|s|` 收缩：**`0.315`**
- 中位数 `|s|` 收缩：**`0.284`**

这说明：
- `15m` 上 **“偏离会收一点”** 仍然存在；
- 但如果直接拿它当 taker-first alpha，本体强度还不够；
- 更像 **低频控制组 / maker-first / veto 后执行层**，而不是第一落点。

### 6.4 哪些方向最像可继续追的 pair pocket
从事件样本看，5m 上更值得继续拆的 cheap-vs-rich pocket 包括：
- `XRP cheap / SOL rich`：平均约 **`+20.18 bps`**
- `ETH cheap / SOL rich`：平均约 **`+12.38 bps`**
- `SOL cheap / BNB rich`：平均约 **`+10.51 bps`**
- `BNB cheap / BTC rich`：平均约 **`+6.72 bps`**
- `XRP cheap / DOGE rich`：平均约 **`+6.06 bps`**

这也提示一个很实际的方向：
> **PCA 不是为了“全市场一起做”，而是更适合先做 residual ranking / 极端口袋挖掘器。**

## 7. desk 应该怎么落这题
### 7.1 不要把它理解成“PCA whole-book strategy”
更好的 desk 读法是：
- PCA = 去掉共同因子的预处理层
- residual OU = 把相对价值失衡量化成统一 s-score
- extreme-only = 真正的交易层

也就是说，这题最像的是：
> **cross-sectional relative-value alpha router**

而不是“又一个学术组合回测器”。

### 7.2 当前最合理的落点是 `5m first, 15m control`
我会这样安排：
- **`5m`**：主实验层。先测 extreme-only / top-k residual fade。
- **`15m`**：控制组。看它能不能作为低换手版本，或者当 execution veto 之后的降频层。
- **`1m / 3m`**：暂时别一上来就压，因为这题本身不是 order-book alpha，本体更像分钟级 relative-value，不是 sub-second microstructure 信号。

### 7.3 这题真正服务的 raw alpha 是什么
如果要用一句话给研究池标注，我会写：

> **factor-neutral residual mean reversion / basket stat-arb**

而其中最先该复现的，不是 whole-book，而是：
- `top1 cheap vs top1 rich`
- 或 `top2 / bottom2` 的 market-neutral fade
- 再叠资产重叠约束与成本门槛

## 8. 可直接落地的最小策略壳
下面这版已经够当实盘前的 research shell：

### 8.1 universe
- 先从 `6~12` 个高流动 major perps 开始
- 第一版就用：`BTC / ETH / SOL / XRP / DOGE / BNB`

### 8.2 signal
- rolling window：保持 **时钟长度**，不是死守 bar 数
  - `5m`：`720 bars`（约 `60h`）
  - `15m`：`240 bars`（约 `60h`）
- PCA：前 `2` 个主成分
- residual：每币对 `F1/F2` 回归后的 `eps`
- OU：按 repo 口径估 `m / sigma_eq`
- s-score：`s = (X_t - m) / sigma_eq`

### 8.3 entry / exit
- entry：
  - 只在 `richest >= 1.25` 且 `cheapest <= -1.25` 时触发
  - 先做 `top1 rich / top1 cheap`
- exit：
  - 未来 `24 x 5m` / `8 x 15m` 之内，`|s|` 回到 `0.5~0.75` 内就平
  - 或 richest / cheapest 方向被下一名替代时强平
  - 或 time-stop 到点强平

### 8.4 sizing
- 默认 equal-dollar / equal-risk 两腿各 `0.5 gross`
- 同资产不允许同时出现在超过 `1` 个活跃 basket pair 里
- 单对 gross cap + portfolio gross cap 要独立设

### 8.5 risk / cost
- 必须显式测：`4 / 8 / 12 bp round-trip`
- 如果未来版本是 maker-first，可再单列 `2~4 bp` 档
- 若 BTC 出现强单边趋势 / market beta 爆发，优先做：
  - 降仓
  - 延后开仓
  - 或直接 veto whole-book，只保留最极端一对

## 9. 下一步怎么测
这轮必须继续往下做，而且方向已经很明确：

1. **从 event study 升级到 stateful pair book**
   - 先只做 `top1 cheap / top1 rich`
   - 再测 `top2/bottom2`
   - 对比 `1.25 / 1.5 / 1.75 / 2.0` 阈值

2. **把“固定 2h 持有”换成真正的 s-score exit**
   - `|s|` 回到中性区立即平
   - 加 `time-stop`
   - 看 turnover 能不能明显降下来

3. **做成本敏感性**
   - `4 / 8 / 12 bp RT`
   - maker-taker 混合成交假设
   - 明确在哪个成本档还活着

4. **做 regime split**
   - 按 BTC 1h trend strength / cross-sectional dispersion / realized vol 分层
   - 验证是不是“趋势太强时 residual fade 容易被压扁”

5. **做 pocket mining，而不是盲目扩大 universe**
   - 先盯 `XRP↔SOL / ETH↔SOL / SOL↔BNB / BNB↔BTC / XRP↔DOGE`
   - 看它们是否稳定成为“PCA 极端口袋”

## 10. 一句话结论
这份 2026 PCA repo 值得进研究池，但不是因为它的 whole-book 回测壳能直接照搬；真正该拿走的是：

> **把 PCA residual / OU / s-score 当成“因子中性相对价值温度计”，然后只做最极端那一对。**

对当前 short-cycle desk，我会把它归类成：
- **能独立复现的 raw alpha**：是
- **能直接落地完整策略**：是，但应落地成 `extreme-only residual fade`，不是 repo 默认 whole-book 直译版

## 11. 关键来源
- Repo：<https://github.com/sophie-lan/crypto-pca-statarb>
- Repo README：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/README.txt>
- `main.py`：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/main.py>
- `src/pca_engine.py`：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/src/pca_engine.py>
- `src/residual_model.py`：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/src/residual_model.py>
- `src/ou_estimator.py`：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/src/ou_estimator.py>
- `src/s_score.py`：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/src/s_score.py>
- `src/strategy.py`：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/src/strategy.py>
- `src/backtester.py`：<https://raw.githubusercontent.com/sophie-lan/crypto-pca-statarb/main/src/backtester.py>
- Avellaneda & Lee (2010)：<https://doi.org/10.1080/14697680903124632>
