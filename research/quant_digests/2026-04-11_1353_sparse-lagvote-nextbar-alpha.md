# 别把这篇 2021 intraday crypto 论文只读成“LASSO 比 benchmark 强”：对 short-cycle desk，更该先测的是「sparse lag-vote × next-minute sign」这条 raw alpha

- 时间：2026-04-11 13:53 UTC
- 类型：2021 *The Journal of Prediction Markets* 论文摘要（Crossref + OpenAlex + journal / ScienceOpen article page）+ Binance USDⓈ-M `1m/3m/5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**用一小撮会快速失效的 lagged features（自身体量/波动/成交量 + 其他主流币的滞后收益特征）去预测下一分钟收益；只在预测值足够大时，按预测方向做 `next-bar` long/short，并用极短 time-box 出场。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/intraday/directional/sparse-signal/lasso/lagged-features/own-return/cross-asset/volume/volatility/next-bar/1m/3m/5m/binance-perpetual/paper/abstract/public-data/cost/risk
- 证据类型：论文摘要 + 本地 public-data portability probe

## 1. 这次看了什么
主论文是：

- **Lalwani, Vaibhav; Meshram, Vedprakash (2021)**
- **Title:** *Predicting Intraday cryptocurrency returns – A Sparse Signals approach*
- **Venue:** *The Journal of Prediction Markets*, Vol. 15, Issue 1
- **DOI:** `10.5750/jpm.v15i1.1840`
- **Readable URL:** <https://www.ubplj.org/index.php/jpm/article/view/1840>
- **ScienceOpen mirror / abstract page:** <https://www.scienceopen.com/document?vid=d8260931-fd27-431c-a910-e94015198a8a>
- **Repo URL:** 暂未见公开代码仓库

Crossref / OpenAlex / ScienceOpen 能稳定拿到的核心摘要是：

> 作者用一大组线性与非线性 predictor，对 **10 个主流加密货币的 1-minute ahead returns** 做 LASSO 预测；结果显示 **LASSO 的 out-of-sample 预测优于 benchmark**，而且被选中的 predictors **很 sparse，而且很 short-lived**。

这篇东西最容易被读成一句空话：

> `LASSO 在 minute 数据上有点用。`

但对我们 desk 真正有用的，不是“机器学习又赢了”，而是它明确给了一个 **可独立成策略的 raw alpha 骨架**：

> **不是持续持有某个慢频因子，而是每分钟重新问一次：当前有没有极少数、但仍然活着的 lagged signal，足够支持下一根方向单。**

一句话核心结论：

> **别把这篇 paper 只当 ML 比赛；更该先测的是「sparse lag-vote × next-minute sign」这条 1m raw alpha。**

一句话证明方式：

> **论文只给出“稀疏且短命”的抽象结论；我再补一个 Binance USDⓈ-M `1m` portability probe，把它翻成可交易壳：对 9 个 liquid futures 用 lagged return / vol / volume 特征做 rolling-ish Lasso，看 strongest predictions 在 `1m/3m/5m` 上是否真能留下 first-pass edge。**

## 2. 为什么这条线值得单独写，而不是并到泛化 ML / directional 主题里
它和已有材料不完全一样：

- 它**不是** “再来一个大而全特征工厂”；
- 它**不是** 典型 `5m/15m` 的趋势壳；
- 它也**不是** 横截面 top-bottom 因子先构造、再慢慢持有。

它真正要补的是另一类 short-cycle 原语：

> **信号本身很短命，所以持有期也必须很短；若拉长到 `3m/5m` 甚至做成宽松 cross-sectional long-short，edge 反而会被自己摊薄。**

所以它的 base alpha 很清楚：

> **下一分钟收益，可以被一小撮 lagged own/cross-asset features 条件化预测。**

这不是 overlay，不是 filter；它本身就是一个可以定义入场、出场和成本门槛的 directional raw alpha。

## 3. 论文里最该拿走的，不是“LASSO 有效”，而是这 3 个 hard takeaways
### 3.1 预测信号不是“很多都有一点用”，而是“少数特征短暂有用”
摘要里最重要的词不是 `LASSO`，而是：

- **sparse**
- **short-lived**

翻成人话：

> **不是市场里一直躺着一堆稳定 alpha 等你捡，而是每个时刻真正有信息量的特征可能只有几根。**

这对 desk 的启发很直接：

- 入场应更像 **strong-conviction threshold**，不是每根都上；
- 出场应更像 **1-bar / 3-bar time-box**，不是硬拖到 15m；
- 模型重心不该是追求复杂，而是追求 **能否稳定筛出当下那几根 still-alive predictors**。

### 3.2 这篇 paper 天然支持“下一根交易壳”，不支持“慢持有壳”
摘要里写的是 **1-minute ahead out-of-sample return forecasts**。

这句话交易上非常关键：

- 它要解决的是 **next bar sign / drift**；
- 不是 `1h` 级别风格暴露；
- 也不是周频/日频配置。

所以如果要搬到 desk，最自然的版本是：

1. 每分钟更新预测；
2. 只在 `|pred|` 超过阈值时开仓；
3. `1m` 后优先平，`3m` 是容忍上限，`5m` 已经应该高度怀疑 alpha decay。

### 3.3 它给的是“特征选择范式”，不是“万能 feature catalog”
这篇 paper 没有给我们一个可以死背的固定因子表；它给的是一种更接近 production 的思路：

> **同一套 feature 库里，真正该活跃的 predictor 会变化；重要的不是把 100 个特征全吃进去，而是让模型在当下只留下少数 still-alive 的那几个。**

这很适合 short-cycle desk，因为很多分钟级 alpha 的真实问题都不是“没有 feature”，而是：

- 特征太多，噪声更大；
- 上一周有用的 lag 这周未必还有用；
- 慢持有会把本来只活 1 根的 edge 拉成 3~5 根后归零甚至反转。

## 4. 本地 public-data portability probe：把“sparse and short-lived”翻成 Binance `1m` 可交易骨架
我做了一个非常克制的最小实验，只检验这条线最核心的 desk 版本能否活：

### 4.1 数据与设定
- 市场：**Binance USDⓈ-M perpetual**
- 资产：`BTCUSDT, ETHUSDT, BNBUSDT, XRPUSDT, ADAUSDT, SOLUSDT, DOGEUSDT, LINKUSDT, LTCUSDT`
- 频率：`1m`
- 窗口：最近约 **7 天**，约 **10080** 根 minute bars
- 有效样本（drop warmup 后）：训练约 **7012** 行，测试约 **3006** 行
- 特征池：约 **186** 个 lagged features，主要包括：
  - 各币种 `ret_l1/l2/l3/l5/l10/l15/l30`
  - 各币种 `mom_5/15/30/60`
  - 各币种 `rv_5/15/30/60`
  - 各币种 `volume-z style` 特征
  - 一个 equal-weight market feature block
- 模型：每个资产单独做 `LassoCV`
- 目标：预测 **next 1m return（bps）**
- 交易解释：只在 `|pred|` 进入该资产测试期 **top 10%** 时，按预测方向做 `next-bar` directional trade

本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_asset_summary_2026-04-11_v2.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_xs_summary_2026-04-11_v2.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_xs_quantile_summary_2026-04-11_v2.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_top_features_2026-04-11_v2.csv`

## 5. first verdict：这条线**不是**“全市场横截面因子”，更像“asset-specific 的 1m sparse sign shell”
### 5.1 好消息：至少有些主流合约上，Lasso 确实选出了少量特征，而且 top-decile signal 不是纯噪声
最干净的两个 first-pass 结果是：

- **BTCUSDT**
  - nonzero features：**6**
  - OOS corr：约 **0.050**
  - top-decile `|pred|` 事件数：**301**
  - signed next-1m return：约 **+0.66 bps**
  - 胜率：约 **58.8%**
- **LTCUSDT**
  - nonzero features：**11**
  - OOS corr：约 **0.055**
  - top-decile 事件数：**301**
  - signed next-1m return：约 **+1.24 bps**
  - 胜率：约 **50.2%**

LINK / SOL 也有轻微正值，但幅度更弱；ETH / DOGE 反而转负。

这组数说明两件事：

1. **“sparse” 不是空话**：有些合约确实只剩 5~11 个非零特征；
2. **edge 是分资产的**：不是所有币都会一起亮。

### 5.2 更重要的坏消息：一旦你把它硬拉成宽松 XS book，`3m/5m` 很快衰减甚至翻负
我额外做了一个很朴素的 cross-sectional top-bottom 版本：

- 每分钟按各资产预测值排序；
- long top 3 / short bottom 3；
- 看未来 `1m/3m/5m` 的均值表现。

结果非常直白：

- **1m**：均值约 **+0.006 bps**，几乎贴地
- **3m**：均值约 **-0.047 bps**
- **5m**：均值约 **-0.116 bps**

换句话说：

> **这条线更像“下一分钟 directional micro-edge”，而不是可直接拉长成 `3m/5m` 的广义横截面书。**

这反而和论文里的 `short-lived` 完全一致。

### 5.3 目前更像“只做 strongest minute signals”，而不是“每分钟满仓轮动”
如果把预测值按分位数做得更宽（例如每分钟都拿 top20% / bottom20%），结果也不漂亮：

- `1m` 有一点点正均值（约 **+0.069 bps**）
- 但 `3m/5m` 还是转负

所以这条线真正的可交易版本，不应是：

> `每分钟都做一个横截面轮动组合`

而更应是：

> **只拿 strongest minute forecast，做 very short hold directional shell。**

## 6. 哪些特征真的会被选中？从 top features 看，它不像“纯趋势”，更像“own-lag MR + cross-coin slow context”
从 `...top_features_2026-04-11_v2.csv` 看，最有意思的是：

### 6.1 BTC 的 strongest sparse set
BTC 被选中的前几项大致是：

- `BTCUSDT_ret_l1`：**负**
- `ADAUSDT_ret_l1`：**负**
- `SOLUSDT_mom_60`：**正**
- `XRPUSDT_rv_5`：**正**
- `SOLUSDT_ret_l10`：**正**

翻译一下：

> **BTC 的 next-minute sign，不像纯粹 trend-follow；它更像“自身体内 1-lag 反打 + 其他大币慢一点的 state/context 修正”。**

### 6.2 LTC 的 sparse set 更像“本币短反打 + cross-coin context”
LTC 前几项包括：

- `BNBUSDT_ret_l1`：**负**
- `LTCUSDT_ret_l3`：**负**
- `XRPUSDT_mom_60`：**正**
- `SOLUSDT_ret_l10`：**正**

这也很像：

> **快的那部分是短 lag mean reversion；慢的那部分是 cross-coin state confirmation。**

所以如果要把这条线翻成 desk 语言，更接近：

> **`very short-horizon sign fade / sign-confirm hybrid`，而不是单纯的 momentum 或单纯的 reversal。**

## 7. 这条线真正适合怎么落地
### 7.1 它适合做单资产 minute shell，不适合先做宽松 market-neutral 轮动
按当前 probe，最合理的第一版不是 cross-sectional long-short，而是：

- 只选 `BTC / LTC / 也许再加 LINK` 这类 first-pass 还活着的合约；
- 每个合约独立训练 / 独立 admission；
- 只做 `|pred|` 最大那部分分钟；
- 默认 **1m 出场**，`3m` 只是容忍延迟，不是默认持有期。

### 7.2 这条 alpha 的形状更像“预测强度阈值”而不是“方向本身无脑跟”
当前结果里，最值钱的不是平均 OOS corr 有多大，而是：

> **当预测值强到某个分位阈值时，next-minute signed bps 是否抬起来。**

这说明 production 版更该重视：

- `|pred| threshold`
- 单位时间最多开仓次数
- 预测值随时间衰减后的快速平仓
- 交易成本后剩余边际

### 7.3 如果要继续往 `3m/5m` 搬，先别想持有更久，先想如何把 1m signal 聚合成 burst
现在的 portability probe 已经告诉我们：

- 简单“多拿几根”没有用；
- 直接拉长持有期会把 edge 摊平；
- 真正该做的，是 **minute-level conviction burst aggregation**，例如：
  - 连续 2~3 根都给同向强预测才进；
  - 或者 `pred spike + liquidity ok + spread ok` 才进；
  - 而不是单纯把持有期变长。

## 8. 策略拆解（必填）
- 方向属性：single-asset directional（可并行跑多个 asset）
- 基础 alpha：sparse lagged-feature forecast of next-minute return
- regime：优先流动性最好、点差稳定、手续费/滑点可控的 majors；不建议先在长尾 alt 上泛化
- filter / veto：`|pred|` 不到阈值不做；spread / taker cost / funding boundary / 异常波动分钟不做
- risk / sizing / execution overlay：按 `|pred|` 分层 sizing；`1 bar` 默认 time-stop；连续亏损分钟触发 cooldown；总成交频率设上限防 churn

## 9. 为什么它和当前 desk 直接相关
这条线很适合补当前素材池里的一个缺口：

- 我们已经有很多 **明确结构型 raw alpha**：pairs、basis、funding、OFI、cross-venue lead-lag；
- 但还缺一种更原子的 **“下一分钟 directional conviction engine”**。

它的价值不只是独立交易，也能服务别的 alpha：

- 给 breakout / MR / OFI 信号做 **minute-level confirmation**；
- 给 multi-asset execution 做 **asset selection**；
- 给已有 directional shell 提供 **entry veto / delay / speed-up**。

但基于这轮 probe，我会明确把它定位为：

> **raw alpha 本体可独立存在，但更适合先做成“ultra-short directional shell”，不是先做 broad XS factor。**

## 10. 可复刻的最小实验
### 数据源 / 公开性 / 更新频率
- 论文元数据 / 摘要：Crossref、OpenAlex、ScienceOpen、期刊 article page（公开可读）
- 行情：Binance USDⓈ-M public klines（公开）
- 更新频率：可做到 `1m`

### 最小研究假设
> 若下一分钟收益真的只受少量、短命的 lagged predictors 影响，那么在 liquid majors 上，Lasso 这类稀疏模型应能筛出少量 nonzero features；在 strongest prediction bucket 里，future `1m` signed return 应显著好于 0，而这类 edge 在 `3m/5m` 上会明显衰减。

### 最小回测切口
1. 先只做 `BTCUSDT / LTCUSDT / LINKUSDT`
2. 频率只做 `1m`
3. 特征先限于：
   - own ret lags
   - top-3 majors cross ret lags
   - short RV
   - volume-z
4. 交易壳：
   - `|pred| >= 90% quantile` 入场
   - 默认持有 `1m`
   - 若下一根预测反向则提前翻/平
   - friction ladder 先扣 `2 / 4 / 6 bps`

## 11. 下一步怎么测
这条线下一步别做大，先做准：

1. **把成本真扣进去**
   - 当前 probe 还是 close-to-close proxy
   - 下一步要改成 bid/ask / taker fee / queue realism
2. **改成 rolling refit / online update**
   - 现在还是训练/测试切分版
   - 若它真是 short-lived，rolling refit 会比静态分割更合理
3. **只保留 high-signal assets**
   - 当前看更像 `BTC/LTC/少数 majors` 有 first-pass edge
   - 别急着全市场铺开
4. **测试 burst admission，而不是更久持有**
   - `single spike` vs `2-bar confirmation`
   - `pred spike + spread veto`
   - `pred spike + OFI 同向`

如果 executable 版本在 BTC/LTC 这类高流动合约上，扣完 `2~4 bps` 后 strongest 1m 信号仍是正的，这条线就能进入 clean replication；如果一上真实成交成本就塌，那它仍然值得保留为 **minute-level confirmation / veto layer**，而不算白做。

## 12. 来源
1. **Lalwani, V., & Meshram, V. (2021). _Predicting Intraday cryptocurrency returns – A Sparse Signals approach_. The Journal of Prediction Markets, 15(1).**
   - DOI: <https://doi.org/10.5750/jpm.v15i1.1840>
   - Journal page: <https://www.ubplj.org/index.php/jpm/article/view/1840>
   - ScienceOpen abstract page: <https://www.scienceopen.com/document?vid=d8260931-fd27-431c-a910-e94015198a8a>
2. **Crossref metadata / abstract**
   - <https://api.crossref.org/works/10.5750/jpm.v15i1.1840>
3. **OpenAlex metadata / abstract**
   - <https://api.openalex.org/works/https://doi.org/10.5750/jpm.v15i1.1840>
4. **本地 portability artifacts**
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_asset_summary_2026-04-11_v2.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_xs_summary_2026-04-11_v2.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_xs_quantile_summary_2026-04-11_v2.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/sparse_intraday_lasso_probe_top_features_2026-04-11_v2.csv`
