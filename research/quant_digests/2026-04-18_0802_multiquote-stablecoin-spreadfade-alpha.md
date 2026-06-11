# 别把 Yang, Malik (2024) 只读成“多币种配对优化”：对 short-cycle crypto desk，更该先拆的是「同一 underlier 的多报价残差回归」这条 raw alpha

- 时间：2026-04-18 08:02 UTC
- 类型：2024 *International Journal of Financial Studies* 论文全文（MDPI 可读页 via r.jina.ai）+ Crossref DOI 元数据 + Binance Spot `1m/5m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**同一个资产（如 BTC / ETH）在不同报价货币上的理论同价关系会短暂偏离；当某一报价腿相对同 underlier 的其他报价腿被“错抬/错压”后，后续更容易向理论平价回归**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（论文给了 `screening + entry/exit + multivariate allocation`；desk 迁移版也能给出 `spread 定义 + z-score 阈值 + cooldown + cost gate + maker/taker 执行壳`）
- 主题标签：raw-alpha / relative-value / stat-arb / pairs / same-underlier / multi-quote / stablecoin / law-of-one-price / spread-zscore / mean-reversion / market-neutral / maker-first / binance-spot / 1m / 5m / paper / public-data / cost / risk
- 证据类型：paper full text + DOI metadata + public-data portability probe

先回答一句：**这篇东西的 base alpha 是什么？**

不是“优化分配器”，也不是“风险控制补丁”。它的 base alpha 很直接：

> **同一个 underlier 的多报价腿，本来应该锚在同一个理论价格附近；当某一条报价腿相对其他报价腿走偏，且偏离幅度超过短窗常态后，后面更容易先回到平价。**

所以这轮我把它归成 **raw alpha / relative-value / stat-arb / mean reversion**，不是 filter。

---

## 1. 这次看了什么
主来源论文：
- **Authors：** Hongshen Yang, Avinash Malik
- **Year：** 2024
- **Title：** *Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform*
- **Venue：** *International Journal of Financial Studies*, 12(3), 77
- **DOI：** `10.3390/ijfs12030077`
- **Readable URL：** <https://www.mdpi.com/2227-7072/12/3/77/>
- **Readable mirror：** <https://r.jina.ai/http://www.mdpi.com/2227-7072/12/3/77>
- **DOI URL：** <https://doi.org/10.3390/ijfs12030077>
- **Crossref metadata：** <https://api.crossref.org/works/10.3390/ijfs12030077>
- **Repo URL：** 无公开官方 repo

论文原始设定，不是我们最熟的“BTC 对 ETH”那类 pairs，而是：
- 以 **同一加密资产（文中主例是 ETH）** 为锚；
- 看它对 **USD / CAD / GBP / EUR** 等多个 fiat quote 的报价；
- 先筛掉相关性 / 协整性弱的 quote；
- 再对多条 quote-spread 同时监控；
- 当多个 spread 一起给出信号时，不是拍脑袋分仓，而是用一个 **risk-return bi-objective optimization** 去分配资金。

翻成人话：
**它做的不是“哪个币涨跌”，而是“同一个东西被不同报价腿定出略不一样的相对价格时，去收那点回归。”**

这对我们 desk 的真正启发，不是照抄 fiat quote，而是：
> **把“同 underlier 多报价”迁移成 crypto 里更好拿、更新更快、可直接做最小实验的 stablecoin 多报价残差。**

所以我额外做了一个 Binance Spot portability probe，用公开 `klines` 去测：
- `BTCUSDT` vs `BTCFDUSD` + `FDUSDUSDT`
- `BTCUSDT` vs `BTCUSDC` + `USDCUSDT`
- `ETHUSDT` vs `ETHFDUSD` + `FDUSDUSDT`
- `ETHUSDT` vs `ETHUSDC` + `USDCUSDT`

相关 artifacts：
- `reports/artifacts/quant_digests/2026-04-18_multiquote_spreadfade_probe.json`
- `reports/artifacts/quant_digests/2026-04-18_multiquote_spreadfade_1m_events.csv`
- `reports/artifacts/quant_digests/2026-04-18_multiquote_spreadfade_1m_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_multiquote_spreadfade_5m_events.csv`
- `reports/artifacts/quant_digests/2026-04-18_multiquote_spreadfade_5m_summary.csv`

---

## 2. 一句话核心结论
**这篇 paper 的 desk 版最值钱分支，不是“多目标优化”本身，而是 `same-underlier multi-quote spread fade` 这条 raw alpha；迁到 Binance 稳定币多报价后，`1m/5m` 上确实还能看到稳定的超短回归，但点数很薄，明显更像 `maker-first / 低费率 pocket`，不是普通 taker-taker 粗暴可吃的厚边。**

---

## 3. 论文里真正该保留的 alpha 骨架
### 3.1 原 paper 的信号骨架
论文把思路拆成两层：
1. **screening**：先找相关且协整的报价腿，避免把天然不该收敛的腿塞进桶里；
2. **trading**：对每一对 quote spread 做标准化，超过开仓阈值就开，回到平仓阈值就关。

文中的信号定义很直白：
- spread = 两条 **log price** 的差；
- 再做标准化（z-score）；
- `z > open_threshold × std` 时开；
- 回到 `close_threshold × std` 时平。

也就是说，alpha 本体很朴素：
**偏了就收，不是趋势跟随。**

### 3.2 真正让它和普通 pairs 不一样的地方
不是“也用了 z-score”，而是：
- 它把 **同一 underlier 的多条 quote** 放进一个 bucket；
- 多个 spread 同时亮灯时，不是每对各开各的，而是回到 **资产粒度** 统一分配本金；
- 用 `lambda` 这个风险偏好参数，在收益和波动之间做 trade-off。

翻成人话：
**它关心的不只是“哪条 spread 偏了”，还关心“同一时刻好几条 spread 都偏了时，钱该先打到哪几条腿上”。**

这对 short-cycle desk 很有用，因为我们自己在做 relative value 时，也经常不是缺信号，而是缺：
- 冲突信号怎么合并；
- gross exposure 怎么控；
- 哪些腿只是重复表达同一个错价。

---

## 4. 论文结果里，最值得记住的 4 个数字
论文主样本是 `ETH` 对多法币 quote，在 2020–2022 的 bull + bear 全周期里测试。对我们最 relevant 的是它给了 **5min** 口径：

### 4.1 full-cycle：5min 下，基准 risk 偏好 `lambda = 1`
- **OTT 年化收益：15.49%**（`TC = 0.1%`）
- 对照 **Distance Method：0.60%**

也就是：
**不是只比 buy-hold 好看，而是比传统 distance pairs baseline 强很多。**

### 4.2 bull market：5min 下 `lambda = 1`
- **OTT 年化收益：36.75%**（`TC = 0.1%`）
- 同条件下 **DM：19.89%**

### 4.3 bear market：5min 下 `lambda = 1`
- **OTT 年化收益：4.99%**（`TC = 0.1%`）
- 同期 buy-hold：**-61.84%**

这点特别重要，因为它说明这条线本质上是：
**收相对错价，不是押市场方向。**

### 4.4 费用敏感性非常高
论文自己也承认：
- 只要把交易成本从 `0.0%` 换成 `0.1%`；
- 高频版本收益几乎能被腰斩。

这对我们反而是好事，因为它提醒得很诚实：
> **这类 edge 有没有，不光看 spread 会不会回归，还要看你到底拿什么方式成交。**

---

## 5. desk 迁移：为什么我不主推“fiat quote 复刻”，而主推“stablecoin 多报价残差”
如果照论文原样做：
- 你得拿到多个 fiat quote 的同步可交易数据；
- 还要处理 fiat 自身波动、外汇交易摩擦、跨市场执行细节；
- 对我们当前 `1m/3m/5m/15m` 快速实验，并不是最短路径。

但如果把同样逻辑迁到：
- `BTCUSDT` / `BTCFDUSD` / `BTCUSDC`
- `ETHUSDT` / `ETHFDUSD` / `ETHUSDC`
- 再加 `FDUSDUSDT` / `USDCUSDT`

那就变成一个很干净的可复现实验：

### 理论平价写法
以 `BTC-FDUSD` 为例：
- 理论上，`BTCFDUSD × FDUSDUSDT ≈ BTCUSDT`
- 所以可定义：

`spread_t = log(BTCFDUSD_t × FDUSDUSDT_t / BTCUSDT_t)`

如果这个 spread 突然偏大：
- 说明 `BTCFDUSD` 相对 `BTCUSDT` 偏贵，或 `FDUSD` quote 这条腿被抬高；
- 反过来做 fade，等它回平价。

这和 paper 完全同源，只是把 **法币 quote** 换成了 **稳定币 quote**。

---

## 6. public-data probe：当前真正值得记住的 3 个数据点
### 6.1 1m 口径：全样本已经能看到稳定回归，但很薄
样本：Binance Spot 公开 `klines`，近约 `8.3d`，滚动窗 `240` 根，入场条件 `|z| > 2`，并加 `10 bar cooldown` 去重。

组合级结果（四条腿合并）：
- 信号数：**1449**
- next `1` bar：**+2.19 bps**
- next `5` bars：**+2.29 bps**
- next `10` bars：**+2.33 bps**

这说明：
**回归是有的，但厚度不高。**

### 6.2 只做强信号（`|z|` 前 25%）会更像可交易 pocket
1m 强信号 bucket：
- `|z|` 阈值约 **2.55**
- 信号数：**363**
- next `1` bar：**+3.00 bps**
- next `5` bars：**+3.13 bps**
- next `10` bars：**+3.08 bps**

也就是说：
> **不是所有偏离都值得收，深一点的偏离更值钱。**

### 6.3 5m 口径也还活着，但依然是低摩擦游戏
样本：近约 `27.8d`，滚动窗 `96` 根，`4 bar cooldown`。

组合级结果：
- 全样本 `1205` 笔，next `3` bars：**+2.24 bps**
- 强信号 `302` 笔，next `3` bars：**+2.98 bps**
- 强信号 next `6` bars：**+2.91 bps**

这对 desk 的意义很明确：
**alpha 没死，但基本不像 taker-taker 该碰的边，更像 maker / rebate / 内部对敲效率高时才值得认真推进。**

---

## 7. 这条 alpha 现在该怎么分类
### 结论
我会把它归成：
- **raw alpha**：是
- **可直接落完整策略壳**：是
- **当前优先执行方式**：`maker-first relative-value pocket`

### 不是 filter 的原因
因为它回答得清楚：
- 买什么 / 卖什么：**买被错压的 quote 腿，卖被错抬的 quote 腿**
- 何时做：**spread z-score 超过阈值时**
- 何时平：**回归 close band / zero-cross / time stop**
- 如何分仓：**按 spread 深度或论文里的 multivariate optimizer 分配**

所以它不是“服务别的 alpha 的 veto”，它自己就是 alpha。

---

## 8. 最小可复现实验怎么做
### 8.1 数据源
- Binance Spot 公开 `klines`
- 标的：`BTCUSDT / BTCFDUSD / BTCUSDC / ETHUSDT / ETHFDUSD / ETHUSDC / FDUSDUSDT / USDCUSDT`
- 公开性：**公开可得**
- 更新频率：**1m / 5m bar 级**
- 最小实验口径：完全够用

### 8.2 最小信号定义
以任意 `underlier-quote` 组合定义：
- `spread_t = log(P_underlier_quote × FX_quoteUSDT / P_underlier_USDT)`
- `z_t = (spread_t - rolling_mean) / rolling_std`
- 当 `z_t > 2`：做空 spread
- 当 `z_t < -2`：做多 spread
- 平仓：`z` 回到 `0 ~ 0.5` 区间，或 `time stop`

### 8.3 最小策略壳
- **entry**：`|z| > 2`，且信号不在 cooldown 内
- **exit**：`z` 回归 close band / 最长持有 `3~10` bars
- **sizing**：先等权；下一轮再做 `abs(z)` 分层或 paper 的 `lambda` 风格优化
- **risk**：gross exposure cap、quote-leg concentration cap、stablecoin 单边暴露 cap
- **cost**：必须分 `maker-first`、`maker+taker`、`taker-taker` 三档单独核算

---

## 9. 风险与保留意见
### 9.1 这条边很薄，最怕费用和滑点
当前 probe 给的多是 **2~3 bps** 级别 gross edge。
如果你按普通 taker-taker 去打，两边手续费一扣，大概率直接没了。

### 9.2 `klines` 版本低估了执行难度
bar 数据只能证明“回归结构存在”；
但真正能不能吃到，取决于：
- top-of-book 深度
- 哪条腿先动
- 你能不能先挂在更贵/更便宜那条腿上等成交
- quote 之间是否存在系统性 fee / rebate 差异

### 9.3 这类 edge 很容易重复计数
如果没有 cooldown，同一次 quote 扭曲可能连续好几根都亮灯，回测会看起来过于丝滑。
所以这轮 probe 我已经先加了 cooldown；下一步还要继续做 cluster 去重。

### 9.4 不是所有 stablecoin quote 都一样可靠
`FDUSD`、`USDC`、`USDT` 各自有自己的流动性、费用和短时微脱锚特征。
所以这条 alpha 的本质，其实混合了两件事：
- 同 underlier 报价错位
- quote currency 自身的微小偏离

这不是坏事，但要明白它收的是 **相对错价**，不只是单纯的 underlier 预测。

---

## 10. 为什么它比继续找“泛泛 filter”更值得进池
因为它正好补的是我们当前最该补的那类东西：
- **raw alpha**，不是解释层；
- **relative-value / stat-arb**，不是又一条方向型 trend；
- **可公开数据快速复现**，不是要额外买数据才能开工；
- **能落完整策略壳**，不是只留一句“可做参考”。

更重要的是，它把 paper 里最值钱的思想，迁成了 desk 当前能马上试的形式：
**论文给理论骨架，stablecoin 多报价给最短实验路径。**

---

## 11. 下一步怎么测
下一轮不要再停留在 event-study，直接做这 4 件事：

1. **把 `event mean bps` 升级成真正双腿回测**  
   明确两条腿怎么成交、怎么配 notional、怎么记资金占用，别只看 spread 本身回归。

2. **补 execution ladder：maker-first / maker+taker / taker-taker**  
   这条线能不能活，核心不在“有没有 2~3 bps”，而在“你到底用什么方式吃这 2~3 bps”。

3. **加 portfolio conflict handling**  
   同一时刻多条 quote 腿一起偏时，先跑等权，再跑 paper 风格的 `lambda` 风险偏好分配，比较：
   - gross return
   - turnover
   - quote concentration
   - tail loss

4. **做 1m / 5m 的 quote-venue 分层**  
   先比较：
   - `FDUSD` 腿是否比 `USDC` 腿更厚；
   - `BTC` 是否比 `ETH` 更薄但更稳；
   - 强信号 bucket 是否能显著提高 net edge。

如果这四步跑完，`maker-first` 口径下还能保住正 net，
那它就不只是“paper 启发”，而是值得进下一轮 admission 的 **production-candidate raw alpha**。
