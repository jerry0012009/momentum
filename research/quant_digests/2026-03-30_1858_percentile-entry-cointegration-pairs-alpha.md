# 别把短周期 pairs 继续写成固定 σ 阈值：这篇 2025 LUT thesis 更该先测的是「percentile-entry × cointegration spread MR」完整 raw alpha
- 时间：2026-03-30 18:58 UTC
- 类型：2025 LUT thesis 全文 PDF + 本地全文抽取 + 表格级结果复核
- 主题类型：raw alpha
- 基础 alpha：**经 cointegration 筛出的 crypto pair，其 spread 在分钟级偏到分布尾部后会向均值回归；而对重尾、偏斜 spread，更合适的不是固定 ±2σ 触发，而是 percentile-entry + mean-cross exit。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/percentile-threshold/threshold-governance/binance/usdt/3m/5m/15m/paper/public-data/cost
- 证据类型：全文证据（thesis）+ 表格级结果复核 + desk 化迁移

## 1. 这次看了什么
主看这篇：

1. **Micke Metsälä (2025). _Pairs trading performance in cryptocurrency markets_. Bachelor’s thesis, LUT University.**
   - Readable URL：`https://lutpub.lut.fi/handle/10024/168939`
   - PDF URL：`https://lutpub.lut.fi/bitstream/handle/10024/168939/bachelorsthesis_Metsala_Micke.pdf?sequence=3`

先把 **base alpha** 说清楚：

> **这次主角不是 filter，不是 regime，也不是“pairs 研究综述”。真正的 raw alpha 是：筛出 cointegrated pair 后，spread 偏到尾部就做均值回归，而且 minute crypto spread 更适合用 percentile 触发，而不是照抄 ±2σ。**

这轮我没有把 2026 的 *Pairs Trading in Crypto*（Stoikov et al.）当主 digest，不是因为主题不强，而是当前可稳定拿到的主要是 Crossref 摘要；反过来，这篇 2025 LUT thesis 虽然不是顶刊，但**全文可读、样本口径完整、3m/5m/15m 直接贴 desk、entry/exit/sizing/cost 都写清楚**，对本轮 intake 更有用。

一句话核心结论：

> **在 short-cycle crypto pairs 里，真正值得先复现的不是“distance vs cointegration”这个老问题本身，而是“cointegration + percentile-entry + mean-cross exit”这条完整策略骨架。**

一句话它是怎么证明的：

> **作者用 Binance 378 个可做空 USDT 资产、71253 个 pair、200 天 formation + 200 天 trading、并把 10bps 交易成本直接扣进回测，逐个比较 3m/5m/15m 下的 distance 与 cointegration。**

## 2. 核心结论
先给结论，不绕：
- **主题类型：raw alpha**
- **基础 alpha：cointegrated spread 的尾部偏离回归**
- **是否可独立复现：是**
- **是否可直接落地完整策略：是**

这篇东西最值钱的不是“pairs 在 crypto 里也能赚钱”这么泛，而是下面四点：

1. **它给的是完整策略，不是只有入场信号。**
   - formation：200 天
   - trading：200 天
   - pair selection：distance 用 SSD，cointegration 用 OLS + ADF
   - entry：spread 进入上/下 **0.5% 尾部**
   - exit：spread 回到**自身平均值**附近，不是死等 0-cross
   - sizing：按 hedge ratio 分配 `1000` 单位资本
   - cost：每笔交易 `0.1%`

2. **对 crypto minute spread，percentile 阈值比 ±2σ 更像可用模板。**
   论文明确解释：crypto pair spread 往往偏斜、重尾，直接拿标准差做阈值，可能会让某些 pair 几乎没机会，或把极端值当常态。作者改成：
   - **最高 0.5% spread** 触发一侧
   - **最低 0.5% spread** 触发另一侧
   - 回到**均值**就平仓

3. **cointegration 在 3m / 5m / 15m 都比 distance 更稳。**
   全样本汇总：
   - cointegration 平均净利润：**12.5%**
   - distance 平均净利润：**10.96%**
   - cointegration 平均最大回撤：**-1.16%**
   - distance 平均最大回撤：**-2.36%**
   - cointegration 波动：**2.51%**
   - distance 波动：**2.82%**

4. **对 desk 最有用的不是照搬“哪些 pair 最赚钱”，而是照搬“怎么选 pair、怎么定阈值、怎么核算成本”。**
   论文里很多优胜 pair 带有明显 2024 小币风格（例如 `REZ/OMNI/RVN/KMD/DYM` 一类），这部分不能原样照抄进实盘；但它的**策略骨架**很适合拿来做 liquid-perp universe 的最小复现。

## 3. 为什么和当前项目直接相关
这轮选它，是因为它满足当前 bot7 的高优先级标准：

1. **raw alpha 很清楚。**
   不是“pairs 可以当 filter”，而是**spread 尾部回归**本身就是可交易的 alpha。

2. **它是完整策略，不是半成品。**
   现在素材池里有很多 pairs / relative-value 主题，但并不是每篇都把 `entry / exit / sizing / cost` 一起讲透。这个材料恰好给了完整 skeleton。

3. **时间框架正好贴着 desk。**
   它直接跑的是 **3m / 5m / 15m**，不是日频论文硬迁移。

4. **它补的是一个很具体的缺口：threshold governance。**
   我们最近 intake 了不少 pairs / same-underlier / basket stat-arb，但“**spread 用什么阈值触发更诚实**”这个问题，还没有被单独钉牢。这里给了一个非常适合最小实验的答案：
   **固定 σ 阈值未必好，percentile 阈值更稳。**

需要诚实补一句：
- 这篇虽然用 minute bars 选信号，但**平均持有期仍是多天级别**（约 12~17 天）；
- 所以它不是“1m 高频 scalper 教程”；
- 它更像一条**能在 3m/5m/15m 上触发、但持仓可能跨天**的 short-cycle pairs raw alpha 骨架。

这并不削弱它的价值，反而告诉我们下一步该测什么：
**alpha 是否主要集中在入场后的前 1~3 天，能否把多天持有压缩成更 desk-friendly 的持仓上限。**

## 3.5 策略拆解（必填）
- 方向属性：**pairs / stat-arb / relative-value / mean reversion**
- 基础 alpha：**cointegrated spread 尾部偏离后的回归**
- regime：
  - 更适合有稳定相对关系、流动性尚可、借贷/short 可行的 pair；
  - 不适合临时壳币、极端新闻币、已脱锚或强叙事切换中的 pair。
- filter / veto：
  - 先过 `cointegration + ADF`；
  - 再过流动性与 shortable 约束；
  - desk 版还应加：最小成交额、最大价差、借贷可用性、funding/borrow veto。
- entry：
  - 不是固定 `±2σ`；
  - 用 formation 期 spread 分布的 **top 0.5% / bottom 0.5%** 做入场阈值。
- exit：
  - spread 回到其**平均值**就平，不是必须等 0-cross。
- sizing：
  - 论文用 `1000` 单位资本，按 hedge ratio 分配两腿仓位；
  - desk 版应改成 volatility / ADV / impact-aware sizing。
- risk / cost：
  - 论文已计入 `10bps` 交易成本；
  - 没有 stop-loss；
  - desk 版必须补：`max-hold`、`MAE stop`、`liquidity stop`、`spread regime break`。

## 4. 论文里真正值得复现的部分
### 4.1 数据与实验口径
论文样本并不花哨，但非常适合复现：
- 交易所：**Binance**
- 资产：**378 个可 margin short 的 USDT 计价币种**
- 组合数：**71253 个 candidate pairs**
- 时间范围：**2023-07-07 ~ 2024-11-18**
- 频率：**3m / 5m / 15m**
- 观测点数：
  - `3m`: **240001**
  - `5m`: **144000**
  - `15m`: **48000**

对当前 desk 来说，这个口径最大的优点是：
**不需要稀缺外部数据，直接用公开 K 线 + 可做空清单就能开第一轮。**

### 4.2 pair selection 怎么做
作者不是随手挑几对币，而是：
- distance 路线：挑 **25 个 SSD 最小**的 pair；
- cointegration 路线：先 OLS 回归取残差，再做 ADF，挑 **25 个 ADF 统计量最强**的 pair。

翻成人话就是：
- distance 更像“历史价格形状接近”；
- cointegration 更像“spread 本身更接近平稳、可回归”。

这也是为什么它更适合做 raw alpha 主体，而不只是辅助过滤层。

### 4.3 最值得抄的不是 headline，而是阈值设计
论文第 3.7 节其实比 headline 更值钱。

作者明确反对机械照搬 `±2σ entry + 0-cross exit`，理由很简单：
- crypto spread 分布常常不对称；
- 某些 pair 几乎碰不到 +2σ；
- 用标准差会让交易机会不稳定；
- percentile 阈值更 rank-based，对 heavy-tail / skew 更稳。

对 desk 而言，这个分支想法的价值甚至**高于**“cointegration 比 distance 强”这个 headline：

> **因为 distance/cointegration 只是 pair selection，percentile-entry 才直接决定信号触发密度、胜率结构和成本后存活率。**

## 5. 关键实证结果
### 5.1 按频率看：cointegration 全部胜出，15m 收益最高，5m Sharpe 最好
论文 Table 9 / Table 10 最值得先记住的是这几组数字：

#### Cointegration
- `3m`：平均净利润 **9.94%**，波动 **1.98%**，平均开仓时长约 **12 天**
- `5m`：平均净利润 **13.19%**，波动 **2.58%**，平均开仓时长约 **15 天**
- `15m`：平均净利润 **14.38%**，波动 **2.97%**，平均开仓时长约 **17 天**
- Sharpe：文中指出 **5m / 15m** 最高，约 **3.31 / 3.35**

#### Distance
- `3m`：平均净利润 **10.60%**
- `5m`：平均净利润 **11.29%**
- `15m`：平均净利润 **10.99%**
- `3m` 平均最大回撤最差，约 **-2.7%**

这组结果翻成人话：
- 如果只想先做最稳的 baseline，**cointegration 明显比 distance 更像主路线**；
- 如果在 `5m` 和 `15m` 之间选：
  - **15m 更像收益优先**
  - **5m 更像风险调整后更顺手的起点**

### 5.2 Top pair 结果给了两个提醒
cointegration 侧：
- `3m`：`RVNUSDT-KMDUSDT` **23.27%**，`CRVUSDT-STRKUSDT` **20.84%**
- `5m`：`RVNUSDT-KMDUSDT` **27.12%**，`RDNTUSDT-OMNIUSDT` **21.09%**，`FUNUSDT-OMNIUSDT` **18.42%**
- `15m`：`DYMUSDT-OMNIUSDT` **26.53%**，`KMDUSDT-RVNUSDT` **23.33%**

distance 侧也有不错个例，比如：
- `5m`：`REZUSDT-PHAUSDT` **22.06%**，`REZUSDT-WRXUSDT` **21.96%**，`DCRUSDT-OMNIUSDT` **18.65%**

但这里最该学的不是“RVN/KMD 很神”或“REZ/PHA 很神”，而是两个提醒：

1. **小币 pair 容易好看，但实盘可承载性很可疑。**
2. **太接近的 wrapper pair 反而可能几乎没肉。**
   文中多次提到：
   - `WBTCUSDT-BTCUSDT`
   - `WBETHUSDT-ETHUSDT`
   这类 pair 波动和回撤都很低，但收益也接近没有。

这对 desk 很关键：
> **最稳的 pair 不一定最值钱；太“完美锚定”的 pair，往往只剩薄 spread，成本后没边。**

## 6. desk 化后的最小实验
这篇最适合直接变成一个 4 叉对照实验，而不是写完就放进 archive：

### 6.1 先做最小 universe
第一轮别上 378 个小币，先做：
- Binance / OKX / Bybit 上**流动性最好的 20~40 个 USDT perp 或 spot-shortable 币**；
- 排除 wrapper/stablecoin 镜像 pair；
- 排除日均成交额过低、盘口过薄、funding/borrow 异常的 pair。

### 6.2 直接做 2 × 2 对照
对每个频率 `3m / 5m / 15m`，跑四个版本：
1. distance + `±2σ / 0-cross`
2. distance + `percentile / mean-cross`
3. cointegration + `±2σ / 0-cross`
4. cointegration + `percentile / mean-cross`

这样第一轮就能回答最关键的问题：
**真正有用的是 cointegration，还是 percentile-entry，还是两者必须一起出现？**

### 6.3 先把持有期压缩测试掉
论文平均持有 12~17 天，和 desk 目标不完全一致。
所以必须额外加：
- `max_hold = 1d / 3d / 5d / 10d`
- 看 alpha 是否主要集中在入场后前 `N` 根 bar
- 记录 `MFE / MAE / time-to-mean`

如果利润大多在前 1~3 天已经实现，那它就 still 值得进 short-cycle 素材池；
如果必须长时间占资才有肉，那就降级成中短周期 stat-arb，而不是当前主线优先。

### 6.4 成本口径不要只扣 taker fee
论文只扣了 `10bps`，但 desk 版至少还要补：
- maker / taker 分拆
- funding（若用 perp）
- borrow / locate（若用现货融券）
- slippage / impact
- pair 断裂成本（停牌、脱锚、跳空）

## 7. 这轮最值得带走的结论
如果只留一句：

> **这篇材料最该进入素材池的，不是“crypto pairs 也能做”这种大结论，而是：在 3m/5m/15m 的 crypto pairs 里，先用 cointegration 选 pair，再用 percentile-entry / mean-cross 管 spread，比机械 `±2σ` 更像当前 desk 应该优先复现的完整 raw alpha。**

## 8. 下一步怎么测
按优先级直接排：

1. **先在 liquid universe 复刻论文骨架**
   - 资产：20~40 个高流动 USDT perp/spot-shortable
   - 频率：`5m` 为主，`15m` 做稳健基线，`3m` 做高强度补充

2. **先回答“阈值问题”，再回答“pair 问题”**
   - 第一轮就跑 `±2σ` vs `percentile`
   - 不要一上来把精力耗在更复杂的 pair clustering

3. **加持仓上限，检查 alpha 衰减前沿**
   - `1d / 3d / 5d / 10d`
   - 看 PnL 是否主要来自早期回归

4. **加 friction ladder**
   - `2 / 4 / 6 / 10 bps`
   - perp 版再加 funding
   - 看 survive 的 pair 数量与 trade count cliff

5. **最后再决定它在 desk 里的角色**
   - 若短持有压缩后仍活：留在 **raw alpha 主池**
   - 若必须长持有：降级为 **中短周期 stat-arb 子池**
   - 若只有 percentile 有效、cointegration 不关键：拆成 **shared threshold governance 组件**

## 9. 来源
1. **Metsälä, M. (2025). _Pairs trading performance in cryptocurrency markets_. LUT University Bachelor’s thesis.**
   - Authors：Micke Metsälä
   - Year：2025
   - Venue：LUT University
   - Readable URL：`https://lutpub.lut.fi/handle/10024/168939`
   - PDF URL：`https://lutpub.lut.fi/bitstream/handle/10024/168939/bachelorsthesis_Metsala_Micke.pdf?sequence=3`

2. **Stoikov, S., Xu, D., Shao, S., Wang, Y., Zhang, T., Hu, J. (2026). _Pairs Trading in Crypto_. SSRN.**  
   - 用途：**仅作最新方向 corroboration，不作为本轮主证据**（当前稳定拿到的主要是摘要级元数据）
   - DOI：`10.2139/ssrn.6188418`
   - DOI URL：`https://doi.org/10.2139/ssrn.6188418`
