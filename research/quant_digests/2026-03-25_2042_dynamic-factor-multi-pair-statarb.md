# 别把 pairs 继续只做成“两条线的 z-score”：这篇 2021 动态因子论文更该先测的是「共同市场因子剥离后的多腿 stat-arb」raw alpha
- 时间：2026-03-25 20:42 UTC
- 类型：2021 开放获取论文（全文 PDF 可读）+ Binance Futures 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**一篮子币的价格里若同时存在 `1 个共同 I(1) 市场因子 + 1 个可均值回归的 stationary 相对价值因子`，就可以在剥离共同市场腿后，做“多空半篮子”的 market-neutral relative-value/stat-arb**；也就是，不再只盯某一对 spread，而是交易“第二因子偏离会回去”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/multi-asset/pairs/dynamic-factor/cointegration/market-neutral/stationary-factor/15m/5m/binance/perpetual/paper
- 证据类型：全文论文证据 + 本地公共数据快检

> 先回答 base alpha：**这不是 filter，不是纯解释层。base alpha 就是“共同市场腿之外，第二个相对价值因子会均值回归”，因此可做 market-neutral 多腿 long-short。** 这轮值得写，不是因为我们又缺一篇 pairs，而是因为最近 intake 已有 `distance / Hurst / dynamic cointegration / stable pair selection`，但还少一张更上层的 **“pair → basket / pair → factor residual”** 迁移卡。

## 1. 这次看了什么
主来源是：
- **Gianna Figá-Talamanca, Sergio Focardi, Marco Patacca (2021), _Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages_, Decisions in Economics and Finance**

这篇文章最值钱的地方，不是“又一次证明 crypto 可以做 pairs”。真正有用的是：

1. **作者不是先挑一对币再硬做 spread**；
2. 而是先把一篮子币拆成 **共同市场因子 `f1`** 和 **相对价值因子 `f2`**；
3. 只有当 `f2` 是 stationary、且与 `f1` 相关性够低时，才开 market-neutral 多腿组合。

对当前 desk 来说，它补的是一个很明确的相邻缺口：
- 我们最近已经有不少 **pairs 选对 / spread 入场 / Hurst / dynamic cointegration**；
- 但还缺一篇把思路往上提一级的：**不要只问“哪一对最好”，而要问“这一篮子里有没有一个共同 market leg + 一个可回归的 residual leg”**。

也正因为这样，它和最近的 raw alpha 积累直接相关：
- 不是再内循环某个 breakout / retest 形状；
- 而是在 **relative-value / stat-arb 素材池** 里新增一条更接近 desk 组合化落地的骨架。

## 2. 论文到底给了什么
### 2.1 一句话核心结论
**如果一篮子 crypto 价格可被 `1 个共同 integrated factor + 1 个 stationary factor` 描述，那么真正可交易的 alpha 不是“某对价差看起来偏了”，而是“stationary 第二因子会回去”，因此可以做多腿 market-neutral 组合。**

### 2.2 作者怎么做
论文用的是 **BTC / ETH / LTC / XMR** 四币篮子，日频样本覆盖：
- 估计窗口：滚动 **3 年**（`1096` 个日频观测）
- OOS 交易期：**2019-01-01 到 2019-11-30**

作者先估计动态因子模型，把价格写成：
- `f1`：共同市场因子（integrated）
- `f2`：相对价值因子（stationary，前半段样本成立）

然后把每个币的价格按第一因子载荷 `βi1` 做缩放：
- `p*_i,t = p_i,t / βi1`

在这个缩放空间里，不同币之间的 spread 主要受第二因子 `f2` 驱动。接着作者：
1. 用模型做 **1-step ahead forecast**；
2. 把币按 **forecasted scaled price** 排序；
3. **short 预测最贵的一半，long 预测最便宜的一半**；
4. 只在预测组合价值相对当前组合价值偏离足够大时交易（`c * σ_v` no-trade band）。

换成人话：
- 不是“只做 BTC-ETH 一对”；
- 而是每次都在篮子里 **自动找贵腿和便宜腿**；
- 市场共同上涨/下跌那条腿尽量被剥离，只留下相对错位的回归。

## 3. 3 个关键数据点
1. **因子结构本身不是永久成立。** 论文摘要和正文都写得很清楚：在 **2019 年 8 月底前**，这篮子币更像 `1 integrated + 1 stationary`；此后转成 **两个 integrated 因子**，也就是原先那条可回归 residual leg 不再稳定。  
2. **交易结果上，交易阈值 `c=0.20` 是论文里的成本后更优点。** Table 6 显示，2019 OOS 期在 `c=0.20` 时：  
   - 交易次数：**222**  
   - 考虑 `0.10%` 交易费后的净累计收益（`G*`）：**3032.97**  
   - 对比 `c=0.00` 的 `3031.17`，说明 **不是交易越频繁越好，no-trade band 很重要**。  
3. **策略在 regime 失效后会主动停机。** 论文 Fig. 6/7 附近明确写到：**2019-09 之后基本不再交易**，因为 Johansen/相关性检查显示“单一共同 market leg + 单一 stationary residual leg”这个假设不再成立。也就是说，这条线天然不是 always-on。

## 4. 为什么它对当前短周期 desk 有价值
### 4.1 它服务的是哪类 raw alpha
- 分类：**relative-value / stat-arb / market-neutral raw alpha**
- 不是：
  - 单对 cointegration z-score 的再包装
  - 低频宏观 overlay
  - 纯解释型因子文献

### 4.2 它补的是我们最近还缺的一块
最近 pairs / stat-arb 线已经有：
- `distance-first 选对`
- `Hurst anti-persistence`
- `dynamic cointegration`
- `stable pair selection funnel`

但这些大多还停在：
- **先找 pair，再找 entry**

这篇更重要的 side branch 是：
- **先问整篮子有没有一个稳定 residual factor，再决定如何做多腿组合**

也就是把研究对象从：
- `pair selection problem`

往上抬成：
- `basket construction + residual extraction problem`

这对 desk 很实际，因为短周期 perp 上真正容易卡住的，常常不是“entry 不够花”，而是：
- beta 没剥干净
- pair 太少导致 idiosyncratic 噪音太大
- 频繁换 pair 带来额外换手

## 5. desk 化后的完整策略骨架
### 5.1 角色拆解（必填）
- 方向属性：market-neutral / relative-value / stat-arb
- 基础 alpha：第二相对价值因子 `f2` 的均值回归
- regime：只有当 `f1` 像市场腿、`f2` 像 stationary residual，且两者低相关时才允许交易
- filter / veto：
  - `ADF(f1) > 0.05`
  - `ADF(f2) < 0.05`
  - `|corr(f1, f2)|` 足够低
  - `half-life` 不要过短/过长
  - funding / spread / volume 异常时 veto
- sizing / risk / cost：
  - long-short gross 固定到 `1.0`
  - 单币权重 cap
  - 单 sector cap
  - 默认 maker / passive-first，不要 bar-close taker 硬冲

### 5.2 最小可执行版本
1. 选 `6~12` 个流动性最好的 perp；
2. 在 rolling window 上对 **log price level** 做动态因子/PCA proxy；
3. 提取 `f1`（共同 market leg）和 `f2`（relative-value leg）；
4. 只有当 `f2` 通过 stationarity gate 时才生成信号；
5. 按 `forecasted scaled price` 或 `β2/β1` 暴露，把篮子分成贵腿和便宜腿；
6. `short` 贵腿半篮子，`long` 便宜腿半篮子；
7. 用 `c * σ_v` 或 `|z_f2|` 控制 no-trade band；
8. 测 `1 bar / 2 bars / 4 bars` 持有与成本生存线。

## 6. 本地最小快检：把论文翻成 perp desk proxy 之后，边有多厚？
我做了一个**很诚实、但不是 faithful replication** 的最小版 proxy：
- 数据：Binance USDⓈ-M Futures 公共 `15m` K 线
- 样本：`2026-02-01 18:59 UTC ~ 2026-03-25 20:44 UTC`
- 篮子：`BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT`
- 代理方法：rolling `PCA(2)` on log prices + `AR(1)` on factor scores + `ADF` gate
- gate：`ADF(f1)>0.05`、`ADF(f2)<0.05`、`|corr(f1,f2)|<0.18`、`0<=phi2<1`
- 执行：按第二因子暴露做 de-meaned long-short，gross=1

### 6.1 结果先说结论
**这条线在当前 15m perp proxy 上，毛边几乎是平的；一上真实成本就不行。**

### 6.2 关键数字
1. **gate 触发很少。** 在 `3847` 根可交易 `15m` bar 里，只开机 **181 根（约 4.7%）**。这和论文一致：它更像 regime-sensitive residual trade，不是全天候策略。  
2. **1-bar 持有，毛边仅微正。** 不计成本时，累计 log return 约 **+0.00085（约 +0.085%）**，年化 Sharpe proxy 仅 **0.22**。  
3. **一加成本立刻转负。** 同口径下：  
   - `2 bps`：累计约 **-1.25%**  
   - `6 bps`：累计约 **-3.93%**  
   - 命中率从毛收益的 **50.3%** 掉到 `6 bps` 下的 **42.5%**  
4. **把持有拉到 4 bars（约 1 小时）也还不够。** `2 bps` 下累计约 **-1.36%**，`6 bps` 下约 **-4.04%**。说明这里的问题不是“只差一个更长 hold 就自动翻正”，而是 **当前 4 币 / 15m / 频繁重算** 的 desk transfer 还太薄。

### 6.3 这组快检最值得记住的不是“失败”，而是失败长什么样
它说明：
- **raw alpha 本体是有明确形状的**：共同 market leg 剥离后做 residual MR；
- 但 **naive short-cycle transfer 不成立**：4 币篮子太小、15m 更新太快、换手太贵；
- 所以第一刀不该是继续花哨 entry，而是把它收窄到：
  - 更大 basket
  - 更慢 rebalance
  - 更严格 no-trade band
  - 更便宜 execution

## 7. 这条线现在该怎么放进研究池
我的判断：**值得保留，而且属于 raw alpha / 完整策略骨架；但当前更诚实的标签应是“中频 residual stat-arb skeleton，可往 `15m signal → 1h 持有` 迁移”，而不是立刻写成 `5m/15m bar-by-bar taker alpha`。**

换句话说：
- **该进池**，因为它补的是 `pair → basket` 这块缺口；
- **不该过度吹**，因为当前短周期直接 transfer 明显先被成本打掉。

## 8. 下一步怎么测
1. **把 4 币扩到 8~12 币。** 论文价值不在单对，而在“共同腿 + residual 腿”；篮子太小，会把很多 idiosyncratic 噪音误当成第二因子。  
2. **把持有频率降一档。** 第一优先不是 `5m`，而是：`15m 信号生成 + 1h / 2h 持有`，或干脆 `1h` re-estimation。  
3. **把 no-trade band 做成主角。** 直接复刻论文的精神：比较 `c=0 / 0.1 / 0.2 / 0.3`，而不是默认每次都调仓。  
4. **加入 perp desk 真成本。** 至少做 `2 / 4 / 6 bps round-trip`、maker-fill ratio、funding carry 偏移；否则会重复“毛收益看着有、净收益全没”的假象。  
5. **把 regime 失效写成显式停机规则。** 论文最有价值的不是“收益有多大”，而是它诚实承认：当第二因子不再 stationary，就该停机。短周期版也应加：`ADF fail / half-life drift / corr spike` 即停。  
6. **和已有 pairs intake 做 A/B。** 下一轮最值得的不是孤立重跑，而是拿它直接对比：
   - `dynamic cointegration pairs`
   - `Hurst anti-persistence pairs`
   - `stable pair selection funnel`
   看 basket residual 模型是否能在 turnover / capacity / cost 上更优。

## 9. 风险与保留意见
- 这是 **2021 论文**，不算最新，但它解决的是“结构骨架”问题，不是 headline 新鲜感问题。  
- 论文是 **日频 spot 四币**；我这里是 **15m perp 四币 proxy**，所以只能把本地快检当 desk transfer 审计，不能当论文复现。  
- 当前最小快检已经很清楚：**不要把这条线硬写成 5m/15m bar-close taker 策略。**  
- 若后续在 `8~12` 币、`1h` 持有、强 no-trade band 下仍过不了 `2~4 bps`，这条线就该留在“有结构美感，但不够短周期”的 research shelf，而不是继续消耗执行预算。

## 10. 来源
1. **Figá-Talamanca, G., Focardi, S., & Patacca, M. (2021). _Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages_. Decisions in Economics and Finance, 44, 863–882.**  
   - DOI: `10.1007/s10203-021-00318-x`  
   - Readable URL: `https://link.springer.com/article/10.1007/s10203-021-00318-x`  
   - PDF URL: `https://link.springer.com/content/pdf/10.1007/s10203-021-00318-x.pdf`  
   - Repo URL: `未见作者官方开源实现`  
2. **Binance Developers – USDⓈ-M Futures Kline/Candlestick Data**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 11. 本地产物
- `reports/artifacts/quant_digests/dynamic-factor-multi-pair-statarb_20260325_2042/proxy_summary.csv`
- `reports/artifacts/quant_digests/dynamic-factor-multi-pair-statarb_20260325_2042/factor_state_rows_15m.csv`
- `reports/artifacts/quant_digests/dynamic-factor-multi-pair-statarb_20260325_2042/meta.json`
