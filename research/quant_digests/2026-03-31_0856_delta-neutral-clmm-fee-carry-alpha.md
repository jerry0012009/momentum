# 别把这篇 2024 Ledger 论文只读成 DeFi 对冲：对 desk 更该先测的是「delta-neutral CLMM fee harvest × futures carry」完整 raw alpha
- 时间：2026-03-31 08:56 UTC
- 类型：2024 *Ledger* 开放获取全文 PDF + 表格级 hedge 细节抽取 + Uniswap v3 / Deribit 公开数据映射
- 主题类型：raw alpha
- 基础 alpha：**先用集中流动性在窄价带里吃 swap fee，再用期权静态复制 + short future / perp 把方向风险尽量剥掉，把 PnL 重心从“赌价格”改成“赚 fee + carry”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/liquidity-provision/market-neutral/fee-harvest/carry/clmm/uniswap-v3/options/futures/perpetual/wbtc/usdc/btc/eth/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：全文方法 + 经验示例组合表 + 资本占用/收益情景 + 风险管理约束

## 1. 这次看了什么
这次主看的是 **Martin G. Hürtgen & Felix M. Schlütter (2024), _Market Neutral Liquidity Provision in Concentrated Liquidity Pools_**, 发表在 *Ledger*。

如果只说一句人话，这篇东西真正值得进我们短周期研究池的，不是“DeFi LP 也能被数学化”，而是：

> **它把原本很像裸多 gamma / 裸多方向暴露的 CLMM fee-harvest，改造成一条能独立复现、且更接近 desk 风格的 market-neutral fee-carry 策略。**

这不是纯解释文，也不只是 overlay。**base alpha 很清楚：价格短时间内如果主要留在工作带宽附近，LP 会吃到 fee；再把 delta / margin 方向暴露拿期权和 futures 尽量中和，剩下的就是 fee income + carry income。**

和昨晚那篇 `τ-reset` 裸 LP digest 不同，这篇的重点不是“怎样更积极地重置带宽赚更多 fee”，而是：

> **怎样把 fee-harvest 这条 raw alpha，包进一个更像中性 carry sleeve 的完整策略壳。**

## 2. 核心结论
- **这是完整策略，不是局部过滤器。** 论文明确给了 LP 区间、hedge 结构、资本占用、收益口径、风险管理和现实限制，不是“有个想法你自己补全”。
- **alpha 本体不是方向预测，而是带内成交费密度。** 只要价格主要在工作区间里来回走，LP 就收 fee；hedge 的作用是把方向和 collateral 风险尽量削掉，而不是替代 alpha。
- **这条策略本质上是 `fee harvest + futures carry` 的双收益源。** 文中明确写到：short future / short perp 往往还能赚 contango / funding，净卖期权一侧甚至还会先收到期权权利金。
- **但它不是“白拿中性收益”。** 真正的大坑是资本效率：你以为自己部署的是 `$48.6k` LP，实际上整套组合在论文示例里要占掉 `$211.6k` 资本，绝大头是 short options margin 和其对冲保证金。
- **所以最值得 desk 先偷的，不是论文里的连续期权积分推导，而是它给出的完整交易壳：**
  1. 选窄 CLMM 区间；
  2. 部署 LP；
  3. 用少数几个 strikes 近似复制 LP payoff；
  4. 用 short future / perp 对冲 BTC 计价的 margin；
  5. 持有期间盯 margin、funding、带内停留率和 fee density。

一句话概括：

> **这篇 paper 对 desk 最有价值的，不是“证明 CLMM 能 hedge”，而是把“被动做市 fee-harvest”包装成一条可移植到短周期 book 里的 delta-neutral carry strategy。**

## 3. 为什么和当前项目直接相关
最近素材池里，direction、pairs、basis、funding 都已经很密，LP 方向也已经有一篇 `τ-reset` 裸带策略。但我们还缺一张更像真实交易台组件的卡：

- 不是纯裸 directional LP；
- 不是只讲 execution 或 microstructure；
- 而是**完整的“中性 fee-carry sleeve”**。

这张卡正好补这个空位。

它和当前 desk 的关系很直接：
1. **raw alpha 清楚。** 吃的是带内成交费密度，而不是假装自己在预测 K 线方向。  
2. **完整策略壳齐全。** 有 entry / exit / sizing / risk / cost。  
3. **能映射到 `1m/3m/5m/15m`。** 不是用这些 bar 去预测下一根涨跌，而是用它们去做 band occupancy、fee density、funding path、margin stress 的最小实验。  
4. **和已有裸 LP digest 形成互补。** `τ-reset` 更像积极吃 fee 的 raw alpha；这篇更像给这条 alpha 加上一层可交易台落地的 neutralization shell。

## 3.5 策略拆解（必填）
- 方向属性：**market-neutral liquidity provision / fee-harvest / carry raw alpha**
- 基础 alpha：**价格短周期主要停留在集中流动性工作带内时，LP 能持续赚 swap fee；再通过 options + futures 把方向和 collateral 风险中和，把 PnL 主要保留在 fee 与 carry 上。**
- regime：**更适合高成交、双边来回、非单边失控、funding 不极端转负的阶段。**
- filter / veto：**单边加速行情、带外停留时间持续偏高、funding 持续转负、gas / execution 成本过高、options 流动性太差、margin 利用率过高时 veto。**
- risk / sizing / execution overlay：**按 LP notional 先反推所需 option margin 与 future margin，再决定是否值得部署；不是“先配 LP 再说”。**

## 4. 3 个关键数据点
1. **论文示例里，LP 本体价值只有 `$48,612`，但完整 market-neutral 组合的初始资本占用是 `$211,556`。** 也就是大约 **4.35x LP notional**。这直接说明：这条策略的第一性问题不是有没有 alpha，而是资本效率够不够。  
2. **作者用 42 天到期、4 个 strike（`59k / 63k / 66k / 69k`）就做出了有效近似 hedge。** 这很关键：它告诉我们第一轮 desk 实验不必追“连续 strike 理论最优”，少量离散 strike 就能先跑 first verdict。  
3. **净卖期权一侧先收到 `0.586 BTC` 权利金；论文情景分析还给出：若 annualized funding = `10%`、annualized LP fee = `5%`，则对部署资本的年化收益约为 `9%`。** 但作者同时也明确提示：若 funding 转负，组合收益可能直接转负。

再补两条有用的现实约束：
- 文中写明 **Deribit 的最小合约规模让这套 hedge 大致只适合 `$25k+` 级别 LP**；太小仓位会被最小合约粒度直接卡死。  
- 期权保证金本身以 BTC 计价，因此**保证金还要再用 future / perp 做美元化对冲**，这也是资金占用暴涨的主要来源。

## 5. 最值得 desk 先偷哪一段
最值得先拿来做最小实验的，不是全套连续复制理论，而是这条简化版完整壳：

> **窄带 CLMM fee harvest × 少量离散 strikes 近似 hedge × short perp/future hedge margin collateral。**

为什么这段最值钱？因为它把原本容易写成“DeFi 学术推导”的东西，翻译成了 desk 可执行语言：

- **entry：** 选择 pool、fee tier、价带；
- **positioning：** 部署 LP notional；
- **neutralization：** 按近似 Greeks / payoff 结构上 options + future；
- **holding PnL：** 盯 fee、funding、carry；
- **exit / reset：** 带外停留过长、margin 压力过大、funding 翻负或临近到期时退出/重建。

这已经不是“一个旁支 idea”，而是**完整 raw alpha 候选**。

## 6. 可复刻的最小实验
### 6.1 数据源、公开性、更新频率
如果要做这条卡，数据必须明确写清：

- **Uniswap v3 pool 数据**：WBTC/USDC 或 ETH/USDC 公开 swap events、pool state、tick、liquidity、fee tier。  
  - 公开性：公开可得  
  - 更新频率：事件级 / 区块级，可聚合到 `1m/3m/5m/15m`
- **Deribit options / futures / perpetual 数据**：公开 option chain、mark price、funding、future basis。  
  - 公开性：公开可得  
  - 更新频率：分钟级 / 实时 API
- **辅助成本数据**：gas、链上 swap volume、带内停留率、perp funding。  
  - 公开性：公开可得  
  - 更新频率：分钟级 / 事件级

### 6.2 最小可复现实验口径
第一轮不要复刻论文全套连续积分近似，直接做 desk 版简化：

1. **池子选择**：先只做 `WBTC/USDC` 或 `ETH/USDC` 高流动性池，不铺全市场。  
2. **工作带定义**：围绕当前 mid 设一个固定宽度 band（例如最近 `N` 分钟 realized vol 映射出的对称带）。  
3. **LP 部署**：固定 dollar capital 部署 CLMM。  
4. **对冲近似**：
   - 先不用满连续 strike；
   - 只用 `2~4` 个 strikes 近似 LP payoff；
   - 再用 short perp / future 对冲 margin collateral 的 base-coin 暴露。  
5. **退出 / 重建**：
   - 价格连续带外停留超过阈值；
   - funding 连续转负；
   - margin utilization 超阈值；
   - option maturity 接近到无法继续维持时，退出或重建。  
6. **比较基准**：
   - 裸 LP（不 hedge）  
   - 只 short perp 的粗糙 delta hedge  
   - options + future 完整近似 hedge  
7. **核心指标**：
   - gross fee / net fee  
   - funding / carry contribution  
   - capital efficiency（PnL / deployed capital）  
   - band occupancy  
   - margin stress / liquidation distance  
   - 带外停留时间  
   - 到期前重建成本

### 6.3 如何映射到 `1m / 3m / 5m / 15m`
这条策略不是 bar-to-bar 方向预测，所以不能装成“15m 看涨因子”。更诚实的映射是：

- **`1m / 3m`：** 主时钟。看 band occupancy、fee density、funding drift、margin shock。  
- **`5m`：** 做 first verdict 最稳。很多 execution noise 会被压掉一点，但 still short-cycle。  
- **`15m`：** 更适合做 regime 面板：这个时段还适不适合开 neutral LP sleeve？  

也就是说，`15m` 在这里更像**开关层**，`1m/3m/5m` 才是**真实赚钱层**。

## 7. 这张卡最容易错在哪里
- **错法 1：** 把它当成 hedge overlay，而忽略它其实是一条完整的 fee-carry raw alpha。  
- **错法 2：** 只看 LP notional 收益，不看部署资本收益。资本效率差一截，策略评估就会完全失真。  
- **错法 3：** 只 hedge LP 本身，不 hedge options margin 的 base-currency 暴露。论文已经明确说这是大头。  
- **错法 4：** 忽略 option liquidity / minimum contract size，以为小资金也能精细复制。  
- **错法 5：** 把 funding 当恒正 carry。文中明确提醒：funding 转负时，这条策略会很难看。  
- **错法 6：** 用 `15m` K 线粗暴近似整套路径，却不记录带内停留和事件级成交。那样大概率只是在回测幻觉。

## 8. 为什么值得进研究池
它值得进池，不是因为它一定马上能成为主 book 最大仓位，而是因为它满足四个很少同时出现的条件：

1. **base alpha 清楚**：赚 fee density，不是假叙事。  
2. **完整策略闭环齐**：entry / hedge / carry / exit / risk 都有。  
3. **和现有素材池互补**：补的是中性 fee-carry，而不是再加一篇同质化 direction / pairs。  
4. **可快速 first verdict**：只要抓一个池、一个期权链、一个 perp 数据流，就能先判断“资本效率是否足以值得继续”。

对现在的 desk 来说，这张卡最大的意义是：

> **它把“裸 LP 赚手续费”升级成了“可交易台落地的 delta-neutral short-cycle carry sleeve”。**

## 9. 下一步怎么测
1. **先选一个单池单标的试点**：`WBTC/USDC` 或 `ETH/USDC`，不要多池并行。  
2. **先做简化 hedge，不做理论最优 hedge**：2~4 strikes + 1 条 short perp/future，先判定方向中和后 fee-carry 是否还能站住。  
3. **先盯 capital efficiency，而不是 gross fee**：第一优先指标改成 `net PnL / deployed capital`。  
4. **做 `1m/5m` 双时钟面板**：`1m` 看带内停留与 funding path，`5m` 看策略级净值与 stress。  
5. **单独做 funding-turn-negative 压力测试**：这条卡是否在 funding 变负时应自动降权或直接关停。  
6. **把它和昨日 `τ-reset` 裸 LP 卡做并排比较**：同样的 pool / 带宽下，看“裸 fee-harvest”与“neutral fee-carry”到底谁更适合 desk。

## 10. 来源与链接
1. **Hürtgen, M. G., & Schlütter, F. M. (2024). _Market Neutral Liquidity Provision in Concentrated Liquidity Pools_. Ledger, 9, 73–88.**  
   - Venue: *Ledger*  
   - DOI: <https://doi.org/10.5195/ledger.2024.389>  
   - Readable URL: <https://ledger.pitt.edu/ojs/ledger/article/view/389>  
   - PDF URL: <https://ledger.pitt.edu/ojs/ledger/article/download/389/281>  
   - Repo URL: N/A
2. **Adams, H., Zinsmeister, N., Salem, M., Keefer, R., & Robinson, D. (2021). _Uniswap v3 Core_. Whitepaper.**  
   - Venue: Uniswap Labs Whitepaper  
   - DOI: N/A  
   - Readable URL: <https://uniswap.org/whitepaper-v3.pdf>  
   - Repo URL: N/A
3. **Deribit Knowledge Base. _Futures_ / _Options_ / margin documentation.**  
   - Venue: Deribit KB  
   - DOI: N/A  
   - Readable URL: <https://www.deribit.com/kb/futures>  
   - Repo URL: N/A
4. **The Block / DeFiLlama historical funding & pool-yield references**（论文经验部分引用的数据来源）  
   - Venue: Public market data dashboards  
   - DOI: N/A  
   - Readable URL: <https://defillama.com/yields>  
   - Repo URL: N/A
