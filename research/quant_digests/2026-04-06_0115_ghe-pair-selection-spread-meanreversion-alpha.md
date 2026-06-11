# 别把 Hurst 继续只当 regime gate：这篇 2025 *Computational Economics* 论文更该先测的是「GHE 选对 × spread mean reversion」pairs raw alpha
- 时间：2026-04-06 01:15 UTC
- 类型：2025 *Computational Economics* 论文（Springer 摘要页）+ 2024/2025 companion papers 元数据 + GitHub 工程骨架 + Binance 公共 `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：pairs / stat-arb / relative-value 的 spread mean reversion；`GHE / Hurst` 在这里首先用于 **pair formation / pair ranking / admission**，不是事后加的一层宏观 filter
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/generalized-hurst-exponent/ghe/hurst/pair-selection/admission-layer/threshold/orf/binance/crypto/5m/15m/paper/repo/public-data/cost/risk
- 证据类型：论文证据（主论文摘要级 + companion paper 摘要级）+ repo 工程骨架 + 本地最小 portability probe

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = `spread 偏离后向均值回归` 的 pairs / stat-arb raw alpha。**
> 这轮最值钱的不是把 Hurst 当抽象状态分数，而是把它前移成 **pair selection / pair ranking / entry admission** 的一部分：先选更像会回归的 pair，再做 spread z-score 交易。

## 1. 这次看了什么，为什么这轮值得写它
这轮主看 4 份材料：

1. **José Pedro Ramos-Requena & Mahmut Bağcı (2025). _Analysis Pairs Trading Strategy Applied to the Cryptocurrency Market_. *Computational Economics*.**
   - DOI：`10.1007/s10614-025-11149-y`
   - Readable URL：`https://link.springer.com/article/10.1007/s10614-025-11149-y`
   - DOI URL：`https://doi.org/10.1007/s10614-025-11149-y`
   - 关键信息（摘要页可见）：作者用 **generalized Hurst exponent (GHE)** 做 pairs trading，样本跨 **2022~2023**，并明确写出 **out-of-sample** 也验证了稳健性；相较 **Distance / Correlation / Cointegration** 三类 pair selection baseline，GHE 方法表现更好。
2. **Mahmut Bağcı & Pınar Kaya Soylu (2025). _The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms_. *Computational Economics*.**
   - DOI：`10.1007/s10614-025-10958-5`
   - Readable URL：`https://doi.org/10.1007/s10614-025-10958-5`
   - 关键信息（Crossref 摘要）：对 **50 个 crypto-assets** 构建 HFPT 数据集，输入特征包括 `mean / variance / skewness / kurtosis / VaR / correlation`，并把 pair 分成 `positive / weak / negative correlation` 三组；**Random Forest** 是最稳的 threshold 区间分类器，且 **2024-01~2024-02** test set 也能工作。
3. **Mahmut Bağcı & Pınar Kaya Soylu (2024). _Classification of the optimal rebalancing frequency for pairs trading using machine learning techniques_. *Borsa Istanbul Review*, 24, 83–90.**
   - DOI：`10.1016/j.bir.2024.12.004`
   - Readable URL：`https://doi.org/10.1016/j.bir.2024.12.004`
   - 关键信息：同一研究线继续把 **rebalancing cadence / ORF** 拉出来单独治理，说明这条线并不只是“选对 pair”，而是默认你后面还要把 **阈值 + cadence + 风险治理** 一起补全。
4. **sharathStack (GitHub). _Statistical-Arbitrage-Pairs-Trading-Engine_.**
   - Repo URL：`https://github.com/sharathStack/Statistical-Arbitrage-Pairs-Trading-Engine`
   - 关键信息（README）：给出了一个很像 desk 第一版工程骨架的实现顺序：`EG/Johansen -> OU/HL -> Hurst regime -> z-score entry/exit -> portfolio correlation cap`。

这轮值得写它，原因很简单：

- 最近一篇 digest（`2026-04-05_1852_pairs-orf-rebalance-governor.md`）补的是 **overlay / cadence governor**，不是 raw alpha；
- 现在更该补的是 **这条 pairs 研究线本身的 alpha 主体**；
- 而这篇 2025 论文给的不是“又一个 generic pairs”，而是 **pair formation 本身往 anti-persistence / roughness 方向前移** 的版本；
- 对当前 desk 来说，这比继续只写某个事后 veto 更像可复现素材池里的真东西。

## 2. 一句话核心结论 + 它是怎么证明的
### 一句话核心结论
**别把 Hurst 只放在 entry 后面当 filter；对 short-cycle desk，更值得先测的是：用 `GHE / Hurst` 先挑出更像会回归的 spread，再做 beta-hedged z-score mean reversion。**

### 一句话它怎么证明
- **主论文侧**：GHE-based pairs strategy 在 **2022~2023 crypto** 上，不只“能做”，而且 **相对 Distance / Correlation / Cointegration 三类 pair 选择法更优**，并写明 **out-of-sample 也成立**；
- **companion papers 侧**：作者后续又把 **threshold** 和 **rebalancing frequency** 单独拿出来做 ML 分类，说明他们默认的可交易对象并不是“任何 spread”，而是 **先选 pair，再治理阈值与 cadence**；
- **本地 probe 侧**：我用 Binance 公共 `5m/15m` 最近窗口做了一个 rolling Hurst proxy 快检，结果显示：**5m 某些 pair 上，低 H spread 确实更快回到中线；15m 则明显更混合，不能把 Hurst 当万能 greenlight。**

## 3. 这篇东西最值钱的 4 个点
### 3.1 这篇 paper 真正值钱的，不是“又一个 Hurst filter”，而是它把 Hurst 前移成 pair formation
很多 Hurst 相关材料容易被读成：
- 先有某个 alpha；
- 再拿 Hurst 去决定今天能不能开。

但这篇 2025 paper 更值钱的点是：

> **GHE 在这里不是“signal 后的 veto”，而是 pair selection / pair ranking 本身的一部分。**

翻成人话就是：
- 不是所有“高相关 / 能 cointegrate”的 pair 都一样；
- 更 rough、更 anti-persistent、历史上更像回归过程的那批 pair，才值得先进 active book；
- 这会把 alpha 的问题从“单次 entry 怎么调”前移到“pairbook 怎么构建”。

对 desk 的意义非常大，因为它服务的是 **raw alpha 主体**，不是纯 overlay。

### 3.2 这条研究线不是停在论文 headline：threshold 与 ORF companion papers 正好把完整策略缺的两块补上
只看主论文，容易觉得它还是有两个洞：
1. entry / exit 阈值怎么定？
2. 多久 rebalance / 多久 time-stop？

而 companion papers 刚好补了这两块：

- **threshold paper（2025）**：
  - 数据集来自 **50 个 crypto-assets**；
  - 用 `mean / variance / skewness / kurtosis / VaR / corr` 等特征预测 **OT range**；
  - 按 `positive / weak / negative corr` 先分组，再分类；
  - **RF classifier** 在 two/three/four-class 里最好；
  - 用 **2024 年 1~2 月** test set 做了验证。
- **ORF paper（2024）**：
  - 明确表明 pairs 不是只有“做不做”，还有“**多久动一次**”这个经常决定净值形状的隐藏状态；
  - 这正好和我们最近一篇 overlay digest 对上。

所以如果 desk 想把这条线变成完整策略，其实已经有一个很清楚的工程顺序：

1. **GHE / Hurst 构建 pairbook**
2. **spread z-score 做 raw alpha 入场**
3. **threshold model / heuristic 决定 entry band**
4. **ORF / HL bucket 决定 cadence / time-stop / refit 频率**

### 3.3 本地最小 probe：5m 的某些 pair 上，“低 H 再做回归”确实有 pocket；但 15m 更混合
我用 Binance Spot 公共数据，对 `BTC/ETH/SOL/BNB/XRP/DOGE` 六个大币，做了一个 **rolling Hurst proxy + spread z-score** 的最小实验：

- 数据：最近 `1200` 根 `5m / 15m` close
- pair：两两组合，共 `15` 对
- spread：`log(Pa) - beta * log(Pb)`
- 事件：`|z| >= 1.5`
- 回归判定：后续回到 `|z| <= 0.5`
- 观察窗：`5m` 给 `36` bars，`15m` 给 `24` bars
- Hurst bucket：
  - `anti`: `H < 0.45`
  - `neutral`: `0.45 <= H <= 0.55`
  - `persistent`: `H > 0.55`

最有信息量的一组结果是：

1. **`ETHUSDT__DOGEUSDT @ 5m`**
   - anti-persistent bucket：`206` 个事件，**`83.98%`** 在观察窗内回到 `|z|<=0.5`
   - persistent bucket：`19` 个事件，只有 **`21.05%`** 回归成功
   - median exit bars：**`13` bars vs `31.5` bars**
2. **`ETHUSDT__XRPUSDT @ 5m`**
   - anti bucket：`202` 个事件，回归命中 **`65.84%`**
   - median exit bars：**`13` bars**
3. **`SOLUSDT__BNBUSDT @ 5m`**
   - anti bucket：`247` 个事件，回归命中 **`62.35%`**
   - median exit bars：**`16` bars**

但 **`15m` 口径明显没 5m 那么整齐**：
- 有些 pair（如 `BTCUSDT__DOGEUSDT`）在 anti bucket 看起来不错；
- 也有不少 pair 在 persistent bucket 样本少、结果漂，甚至出现和直觉相反的局部结果；
- 这说明 **15m 上 Hurst 更适合做 pair ranking / admission / veto 的辅助变量，而不是单独拿来拍板。**

所以这轮本地 probe 给出的 desk 读法不是“低 H 必赚”，而是：

> **`5m` 上，low-H spread 更像值得先做的 pocket；`15m` 上，它更像一个需要和 cointegration / HL / 成本一起看的 admission feature。**

### 3.4 这条线最像 short-cycle desk 的地方：它天然允许“alpha 本体 + 旁支治理”拆开做
这篇 paper 的一个优点是：
- 你可以把它当一条完整 raw alpha；
- 也可以把其中若干部分拆成 desk 组件。

对应关系很清楚：

- **raw alpha 本体**：spread mean reversion
- **pair formation / ranking**：GHE / Hurst
- **entry governance**：threshold model
- **position / cadence governance**：ORF / HL bucket

也就是说，它不是那种“只有一个 headline 指标”的论文，而是很容易拆成：
- 先做最小 raw alpha；
- 再逐层加 companion 组件。

这对现在的素材池特别合适，因为：
- raw alpha 优先级高；
- 但 desk 也缺一套能配套落地的阈值 / cadence 组件；
- 这条线刚好两边都给了。

## 4. 为什么和当前项目直接相关
它直接服务当前 desk 已经在积累的这几类 raw alpha：

1. **pairs / cointegration spread mean reversion**
2. **cluster / residual relative-value alpha**
3. **需要做 pairbook / admission 层治理的 stat-arb 策略**

更重要的是，它和最近 digest 形成了一个很干净的研发顺序：

- `2026-04-05_1852_pairs-orf-rebalance-governor.md`：先补 cadence overlay
- **这篇**：把 raw alpha 主体补回来

所以这轮不是偏题，而是把“pairs 研究线”从 **overlay-only** 拉回到 **alpha body + overlay stack** 的完整状态。

## 4.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative-value / market-neutral
- 基础 alpha：spread 偏离后向均值回归
- pair formation：先按 `GHE / Hurst` 对候选 pairs 做排序，优先低 H / anti-persistent / rough spread
- trade-on：
  1. 通过相关性 / cointegration 基本筛选；
  2. GHE / Hurst 落在可交易区间；
  3. spread z-score 触发 `|z| >= z_entry`
- veto：
  - H / GHE 重新升到 persistence 区间
  - half-life 过长
  - cointegration / ADF 退化
  - 预估净边际覆盖不了成本
- sizing / risk：
  - beta-hedged 双腿
  - 由低流动性腿决定容量
  - 当 `H -> 0.5` 或 ORF 变长时 size-down
- exit：
  - `|z| <= z_exit`
  - time-stop（`1.25~1.5 x HL` 或 ORF bucket）
  - `|z|` 扩到 stop 带并伴随 stationarity 失效
- cost：
  - maker/taker + 滑点显式入账
  - 第一轮先跑 `4 / 8 / 12 bps` round-trip 三档

## 5. 给 desk 的最小可落地版本
### 5.1 第一版先别追 GHE 原论文全量复刻，先做 desk 版 proxy
第一版完全可以先用这套 desk proxy：

1. **Universe**：Binance / Bybit 前 `20~30` 个高流动 perp 或 spot
2. **Pair 预筛**：
   - `corr > 0.6`
   - `EG / ADF` 基本过线
3. **GHE / Hurst 排名**：
   - 用 rolling Hurst proxy 或 GHE 实现对 pair 排序
   - 每个 rebalance 只保留最低 H 的前 `K` 对
4. **Entry**：
   - `|z| >= {1.5, 2.0, 2.5}` 网格
   - 同时要求 `H < {0.40, 0.45, 0.50}`
5. **Exit**：
   - `|z| <= 0.5`
   - 或 `time-stop = min(1.5 x HL, ORF bucket)`
6. **Sizing**：
   - beta-hedged
   - low-ADV leg controller
   - `H` 越接近 `0.5`，仓位越小

### 5.2 这版为什么合理
因为这版已经把论文线里的 3 个最值钱部分都保住了：
- pair formation 不是随机；
- entry 不只是裸 z-score；
- cadence / hold time 不是拍脑袋。

## 6. 下一步怎么测（这轮最重要）
### 6.1 先测什么
直接做一个 **三层递进 A/B/C**：

1. **A = baseline pairs MR**
   - pair 只按 corr / cointegration 选
   - `|z| >= 2` entry
   - `|z| <= 0.5` exit
2. **B = A + H/GHE ranking**
   - 每个训练窗只保留最低 H / GHE 的前 `K` 对
3. **C = B + threshold / ORF governance**
   - 对 pair 分 bucket，分别配不同 `entry_z / time-stop / refit cadence`

### 6.2 最小实验口径
- **数据**：Binance 或 Bybit 公共 `5m / 15m`
- **Universe**：前 `20~30` 个高流动币
- **walk-forward**：`train 45d / test 14d`
- **pair 选择**：train 内完成，禁止 test 反选
- **K 值**：`K ∈ {4, 8, 12}`
- **entry_z**：`{1.5, 2.0, 2.5}`
- **H cut**：`{0.40, 0.45, 0.50}`
- **输出**：
  - gross/net pnl
  - turnover
  - avg holding time
  - hit rate
  - stop-out ratio
  - pair churn
  - per-pair contribution

### 6.3 第一轮最该看什么结果
第一轮只回答 4 个问题：
1. **H/GHE ranking 能不能提高 pairbook 质量？**
2. **5m 是否明显优于 15m？**
3. **加 H/GHE 后 turnover 是下降还是只是少做了交易？**
4. **threshold / ORF governance 是改善净值，还是只是在少交易美化？**

## 7. 先别自嗨的风险
1. **主论文当前在本环境里仍然是摘要级证据。**
   - 我们拿到了 Springer 摘要页与 Crossref 元数据，但没有拿到全文逐表复核；
   - 所以这轮应视为高质量 intake，而不是 clean replication。
2. **本地 probe 用的是 rolling Hurst proxy，不是论文原始 GHE 全复刻。**
   - 作用是验证“desk 上能否先看见 pocket”，不是声称已 faithful 复现主论文。
3. **15m 结果是 mixed 的。**
   - 不应把 low H 当 15m 的万能 greenlight；
   - 更合理的定位是 pair ranking / admission feature。
4. **H/GHE 不能单独替代 cointegration / cost / execution。**
   - 它更像 pairbook 质量层，而不是独立交易引擎。

## 8. 这轮最值得记住的 desk 化结论
如果只记一句：

> **Hurst/GHE 在 pairs 里更该前移到“先选谁”而不是后移到“要不要做”；对 short-cycle desk，最该先测的是 `GHE/H ranking -> top-K pairbook -> beta-hedged z-score MR`，而不是继续把 Hurst 只写成事后 veto。**

再补一句更现实的：

> **从这轮本地 probe 看，`5m` 比 `15m` 更像这条线的第一落地点；`15m` 先当 admission / veto feature，比直接当主开火键更稳。**

## 9. 来源
1. **Ramos-Requena, J. P., & Bağcı, M. (2025). _Analysis Pairs Trading Strategy Applied to the Cryptocurrency Market_. Computational Economics.**
   - DOI：`10.1007/s10614-025-11149-y`
   - Readable URL：`https://link.springer.com/article/10.1007/s10614-025-11149-y`
   - DOI URL：`https://doi.org/10.1007/s10614-025-11149-y`
2. **Bağcı, M., & Kaya Soylu, P. (2025). _The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms_. Computational Economics.**
   - DOI：`10.1007/s10614-025-10958-5`
   - Readable URL：`https://doi.org/10.1007/s10614-025-10958-5`
3. **Bağcı, M., & Kaya Soylu, P. (2024). _Classification of the optimal rebalancing frequency for pairs trading using machine learning techniques_. Borsa Istanbul Review, 24, 83–90.**
   - DOI：`10.1016/j.bir.2024.12.004`
   - Readable URL：`https://doi.org/10.1016/j.bir.2024.12.004`
4. **sharathStack (2026). _Statistical-Arbitrage-Pairs-Trading-Engine_. GitHub repository.**
   - Repo URL：`https://github.com/sharathStack/Statistical-Arbitrage-Pairs-Trading-Engine`
   - 本地读过 README（公开直链）：`https://raw.githubusercontent.com/sharathStack/Statistical-Arbitrage-Pairs-Trading-Engine/main/README.md`
5. **Binance Spot API Docs — Kline/Candlestick Data.**
   - Readable URL：`https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`

## 10. 本地实验产物
- `reports/artifacts/quant_digests/ghe_pairs_portability_20260406/results.json`
- `reports/artifacts/quant_digests/ghe_pairs_portability_20260406/summary.csv`

其中最值得后续直接复看的 pair：
- `ETHUSDT__DOGEUSDT @ 5m`
- `ETHUSDT__XRPUSDT @ 5m`
- `SOLUSDT__BNBUSDT @ 5m`

它们不是 final answer，但非常适合做这条线的第一批 portability probe。