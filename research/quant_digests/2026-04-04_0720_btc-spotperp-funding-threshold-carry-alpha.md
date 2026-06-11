# 别把 crypto carry 继续写成“正 funding 就一直收”：这份 2025 repo 更值得先测的是「BTC 单 venue spot-perp carry × 负 funding 阈值离场 / 再开仓」完整 raw alpha
- 时间：2026-04-04 07:20 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `Strategy.ipynb` + repo 原始数据）+ 2023/2024 crypto carry 论文链路校对
- 主题类型：raw alpha
- 基础 alpha：当 BTC perp 预期/已实现 funding 为正时，做 `long spot + short perp` 收 funding；当 funding 转负且负到足以吃掉一次平仓/重开成本时，暂时退出，待 funding 恢复非负后再开回 delta-neutral carry
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/spot-perp/same-underlier/delta-neutral/single-venue/btc/binance/threshold-veto/re-entry/5m/15m/3m/1m/repo/paper/public-data/cost/risk
- 证据类型：开源 notebook + repo 附带原始数据 + carry 论文摘要/论坛摘要

## 1. 这次看了什么
这轮我没继续找“跨 venue 扫最肥 funding”的复杂版本，而是故意回到一个**更容易做最小实验**的 carry 原型：

- **Aidasvenc (2025), _funding-rate-trading_**, GitHub repo  
  - README 标题：_Crypto Carry Trade Analysis Using Perpetual Futures_  
  - 关键材料：`Strategy.ipynb`、repo 自带数据文件 `data/Bitcoin 2019-09-10`
- **Zhenzhen Fan, Feng Jiao, Lei Lu, Xin Tong (2023)**, _Risk-Return Relation of Cryptocurrency Carry Trade_, SSRN Electronic Journal, DOI: `10.2139/ssrn.4361410`
- **Zhenzhen Fan, Feng Jiao, Lei Lu, Xin Tong (2023/2024 version)**, _The Risk and Return of Cryptocurrency Carry Trade_, SSRN / seminar abstract lineage, DOI: `10.2139/ssrn.4666425`

我这次要 intake 的，不是“crypto carry 是否存在”这个大命题，而是一个更适合我们 desk 的**可快速复现 branch idea**：

> **把单 venue spot-perp carry 从“永远持有”改成“负 funding 超过 round-trip 成本预算就离场，恢复后再开回”。**

这东西的好处是：
- raw alpha 很清楚；
- 公开数据全都有；
- 可以直接写成完整策略；
- 对 `5m / 15m` desk 很友好，因为信号慢、执行快。

## 2. 这条东西的 base alpha 到底是什么
先用一句话说透：

> **base alpha = 同标的、delta-neutral 的 funding carry。**

也就是：
- perp funding 为正：说明多头愿意付钱给空头；
- 做 `long spot + short perp`，把方向风险尽量对冲掉，主要赚 funding；
- 但不是傻拿到底——如果 funding 转负，而且负到已经足够覆盖一次平仓 + 未来重开成本，那就先退出；
- 等 funding 恢复非负，再重新建回 carry 头寸。

所以这不是 filter，也不是 overlay 伪装货；它本身就是一条**可独立复现的 carry raw alpha**。

## 3. 为什么这条分支比继续写“跨市场大而全 carry”更值得先测
因为它是更干净的最小原型。

和最近那些 multi-venue / ranking / routing 版本比，这个题的优势反而是简单：
1. **标的一条腿就够**：先只看 `BTCUSDT spot + BTCUSDT perp`
2. **数据全公开**：Binance spot/perp K 线、funding history、mark price 都能拿
3. **逻辑闭环完整**：
   - entry：正 funding 时开 `long spot + short perp`
   - exit：负 funding 且超过阈值预算时平
   - re-entry：funding 恢复非负时再开
   - sizing：固定美元 notional 或波动率归一
   - risk：basis 偏离、腿价差、资金占用、借币/费率上限
   - cost：spot + perp 双腿 taker/maker fee
4. **非常适合 5m/15m 执行研究**：signal 不需要逐根 bar 重算，但执行完全可以放到 `1m/3m/5m/15m`

如果这条最简单的单 venue carry shell 都活不下来，后面再叠 venue routing、cross-sectional carry、funding z-score，只会更乱，不会更清楚。

## 4. repo 和论文到底给了哪些硬信息

### 4.1 学术地基：crypto carry 本身不是假命题
Fan 等人的 carry 论文链路里，公开摘要/摘要页给了两组很关键的数字：

- ZUEL 论坛摘要版本写的是：  
  - **annualized return = `43.4%`**  
  - **Sharpe = `0.74`**
- DuckDuckGo 指向 Bohrium 的摘要片段写的是：  
  - **annualized return = `49.3%`**  
  - **Sharpe = `0.81`**

两版数字略有差异，说明版本可能更新过；但方向一致：

> **long high-interest crypto / short low-interest crypto 的 carry，在截面上确实能形成正的 long-short 回报。**

更重要的是，论坛摘要还明确说：
- carry 回报**不能被常见 crypto factors**（market、size、momentum、volatility、liquidity、downside risk、platform collapse risks）解释；
- 它和 fiat carry 也**没有显著一一映射**；
- 作者更倾向把一部分收益解释为**equity volatility risk premium** 的补偿。

对我们来说，这篇 paper 的意义不是拿它做 1m 主信号，而是确认：
**carry 这条原始 risk premium 是值得继续拆成短周期执行版本的。**

### 4.2 repo 自带数据非常适合先做最小实验
repo 附带的 BTC 数据文件覆盖：
- **起点：`2019-09-10 08:00:00`**
- **终点：`2024-05-15 08:00:00`**
- **总样本：`5133` 个 8h 观察点**

我对原始 funding 列做了快检，结果很直接：
- **正/非负 funding 占比：`87.1%`**
- **负 funding 占比：`12.9%`**
- **funding 中位数：`0.0001`（约 1 bp / 8h）**
- **25% 分位：`0.00004314`**
- **最小值：`-0.003`**
- **最大值：`0.003`**

这组数说明两件事：
1. BTC perp 在这段样本里大多数时间都适合做 `long spot + short perp`；
2. 真正会伤 carry 的，不是“没有正 funding”，而是**少数极端负 funding 窗口**。

所以 repo 里最值得 desk 抄的，不是 carry 本身，而是这句规则：

> **当负 funding 已经大到足以吃掉一轮 round-trip 成本预算时，别硬扛，先退出。**

### 4.3 repo 的阈值设计，本质上是在做“funding-budget veto”
`Strategy.ipynb` 的核心阈值 sweep 是：
- `thresholds = np.linspace(0.00004, 0.0001, 10)`

翻成人话就是：
- 当 funding 变负时，
- 如果这次负 funding 造成的损失已经大于一个预设预算（近似于一次平仓 + 日后重开成本），
- 那就先把 carry 拿掉；
- 不是永久放弃，只是等 funding 环境恢复后再回来。

这个写法非常 desk 化，因为它不是宏大叙事，而是很实在的 **cost-aware veto**。

### 4.4 我做的本地便携性快检：这条 veto 至少值得继续测
我用 repo 同一份 BTC 数据做了一个**快速 portability probe**：
- 沿用 notebook 的逻辑；
- 由于原始 `markPrice` 列有缺口，临时用 `Open BTCUSDT_PERP` 作为缺口替代，只拿来判断有没有继续研究价值，**不把这版 PnL 当 production 结论**；
- 固定 `X = 10,000`，`spot fee = perp fee = 1 bp`。

得到的结果是：
- **always-on 持有**：最终累计约 **`24,933.6`**
- **阈值 veto 版本**：最终累计约 **`25,283 ~ 25,373`**
- 粗看最优阈值在 **`0.0000933`** 附近
- 相比 always-on，多出大约 **`+439`**，也就是**约 `+1.8%` 的增益**
- 策略在样本中的激活占比仍然高，约 **`94.5% ~ 96.5%`**

这说明：
- 这不是“把 carry 关掉一大半”的悲观过滤；
- 它更像是**只在最不划算的负 funding 段落里短暂撤退**；
- 至少从最小实验角度看，值得继续深挖。

但我要强调一次：
> 这组快检数字的用途是“判断题值不值得继续做”，不是“宣布策略已验证”。

因为 markPrice 缺口、借币成本、真实 maker/taker fill、资金占用，都还没严肃纳入。

## 5. 对我们 `1m / 3m / 5m / 15m` desk 的意义
这条东西虽然 funding 节奏天然偏慢，但它依然是合格的 short-cycle 素材，原因是：

### 5.1 它是慢信号、快执行的 raw alpha
- **信号时钟**：funding 更新 / funding sign flip / funding budget breach
- **执行时钟**：`5m / 15m` 最自然，`1m / 3m` 可做更细的下单择时

也就是说：
- alpha 本体不是逐根 1m 乱跳；
- 但我们的实际开平仓、拆单、basis 监控、滑点 veto，全都可以放在短周期框架里。

### 5.2 它服务的是 carry 这类 raw alpha，而不是 filter 伪装
这条题最重要的定位是：
- 它不是“拿 funding 当 market filter”；
- 而是**funding 本身就是收益来源**；
- `threshold exit` 只是让这条 carry 更 net、更可活。

所以它完全符合这轮 intake 的优先级：
**完整策略 raw alpha > 纯解释型主题。**

## 6. 公开数据、更新频率、最小可复现实验口径

### 6.1 数据源
全部可以走公开接口：
- **Binance spot klines**
- **Binance perpetual klines / mark price**
- **Binance funding rate history**
- 若要更完整，再补：
  - 借币/现货融资成本
  - 资金费率结算时间点
  - maker/taker fee tier

### 6.2 更新频率
- funding：通常是 **8h** 结算/刷新主时钟
- spot/perp 价格：可拿 **1m** 甚至更细
- basis / slippage / microstructure veto：可以放在 **1m / 3m / 5m / 15m**

### 6.3 最小可复现实验
我建议第一版就做得很朴素：
1. 标的：`BTCUSDT` 单币先跑
2. 头寸：`long spot + short perp`
3. 入场：
   - funding 非负时持有；
   - 若刚从负 funding 转回非负，在下一根 `5m` 或 `15m` bar 重开
4. 离场：
   - 当前 funding 为负；
   - 且 `|negative funding| × notional > round-trip cost budget`
5. 成本：
   - spot fee
   - perp fee
   - 滑点
   - 资金占用 / 借币成本（如果现货融资或借币）
6. 评估：
   - gross / net carry
   - out-of-market 时间占比
   - missed positive funding
   - adverse basis move
   - break-even fee

这是一个完全可以在 `5m / 15m` desk 中快速落地的实验，不需要先上全市场截面。

## 7. 下一步怎么测

### Step 1：先把 repo 的数据口径补干净
优先处理：
- `markPrice` 缺口
- funding 时间戳对齐
- 现货与 perp 的 fee / borrow 假设

先别急着扩标的；把 BTC 这个最小壳跑通更重要。

### Step 2：做真正的 funding sign-flip event study
要回答的不是“carry 总体赚不赚钱”，而是：

> **负 funding 翻转段，到底会不会系统性吞掉继续持有的 carry 收益？**

建议把事件拆成：
- funding 从正转负后的 `1 / 2 / 3` 个结算窗
- funding 极端负值分位（如 bottom 5%、1%）
- 同时观察 basis 漂移与 spot-perp 腿价差

### Step 3：把阈值从固定值改成成本自适应
repo 现在更像固定预算；desk 版更该测：
- `threshold = k × expected round-trip cost`
- `threshold = maker/taker mix + spread proxy + borrow proxy`
- `threshold` 是否需要按波动/流动性分层

也就是把它从“魔法数字”改成**显式成本模型**。

### Step 4：扩到 ETH / SOL，但不要急着做 cross-sectional carry
如果 BTC 单币版本能活，再扩：
- `ETHUSDT`
- `SOLUSDT`

先看：
- 负 funding 频率
- 阈值最优区间
- re-entry 延迟敏感度

只有单币壳稳定后，再考虑截面高 carry / 低 carry 排名，否则会把 raw alpha 和执行噪音搅在一起。

### Step 5：最后再叠短周期执行 veto
等 carry 本体过了，再加：
- `1m/3m` spread widening veto
- funding 结算前后 5m 的冲击成本 veto
- 盘口薄时暂停重开
- 大 basis 跳变时只平不重开

顺序一定别反：
**先验证 carry 本体，再做 execution polish。**

## 8. 我当前的判断
我会把这条题放进研究池，而且优先级不低。

不是因为它多性感，而是因为它满足现在最缺的几个条件：
- **raw alpha 清楚**
- **完整策略闭环清楚**
- **公开数据容易拿**
- **可以今天就做最小实验**
- **还能作为更复杂 carry / basis / funding 策略的干净基线**

一句话说：

> **如果要给 short-cycle desk 补一条最容易复现的 carry 原型，这个“正 funding 持有、负 funding 超预算就退出”的 BTC 单 venue shell，很值得先做。**

## 9. 来源与复现入口
### 主 repo
- **Aidasvenc (2025)**, *funding-rate-trading*  
  - Repo URL: `https://github.com/Aidasvenc/funding-rate-trading`  
  - README: `https://github.com/Aidasvenc/funding-rate-trading/blob/main/README.md`  
  - Notebook: `https://github.com/Aidasvenc/funding-rate-trading/blob/main/Strategy.ipynb`  
  - Raw data: `https://raw.githubusercontent.com/Aidasvenc/funding-rate-trading/main/data/Bitcoin%202019-09-10`

### 学术链路
- **Zhenzhen Fan, Feng Jiao, Lei Lu, Xin Tong (2023)**, *Risk-Return Relation of Cryptocurrency Carry Trade*  
  - Venue: SSRN Electronic Journal  
  - DOI: `10.2139/ssrn.4361410`  
  - Readable URL: `https://doi.org/10.2139/ssrn.4361410`
- **Zhenzhen Fan, Feng Jiao, Lei Lu, Xin Tong (2023/2024 version)**, *The Risk and Return of Cryptocurrency Carry Trade*  
  - Venue: SSRN / seminar abstract lineage  
  - DOI: `10.2139/ssrn.4666425`  
  - Readable URL: `https://doi.org/10.2139/ssrn.4666425`
- **ZUEL seminar abstract page**（用于摘要数字校对）  
  - URL: `https://dtfe.zuel.edu.cn/szjsyxdjryw-szjsyw_xshd/szjsyxdjryw_cont_news/details-40035.html`

### 这篇 digest 的一句话结论
**这次最该 intake 的，不是“carry 赚不赚钱”的大叙事，而是「BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry」这个今天就能上 `5m/15m` 做最小实验的完整 raw alpha 壳。**
