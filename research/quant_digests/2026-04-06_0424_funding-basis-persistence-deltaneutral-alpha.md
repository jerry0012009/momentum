# 别把 funding 继续只读成“谁最肥就空谁”：这份 2026 新 repo 更该先测的是「funding/basis dislocation persistence × delta-neutral carry」这条完整 raw alpha
- 时间：2026-04-06 04:24 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md`）+ dYdX funding 官方文档 + Binance Futures 公共 API 文档 + 2024 arXiv 理论地基
- 主题类型：raw alpha
- 基础 alpha：**delta-neutral carry / stat-arb**；当 perp 相对现货（或相对低 funding 对手腿）出现 **正 funding + 正 basis 的可交易偏离** 时，做 `long hedge leg / short rich-funding leg`，靠 **funding 收益 + basis 回归** 赚钱；反向侧则在可借券/可做空现货或跨 venue hedge 成立时对称执行
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/delta-neutral/stat-arb/spot-perp/perp-perp/persistence-horizon/sign-flip/zscore/liquidity-gate/dydx/binance/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 研究骨架 + 官方机制文档 + 理论/实证论文 grounding

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = `rich funding leg` 相对 `hedge leg` 的可持续错价。**
> 更直白地说：不是去赌方向，而是去赚 **“perp 太贵/太热，短期内 funding 会继续付、basis 最终会回”** 这件事本身。

## 1. 这次看了什么，为什么这轮值得写它
这轮主看 4 份材料：

1. **Menger Wen / hanqihang / collaborators (2026). _Deep-Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates_. GitHub repository.**
   - Readable URL：`https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
   - Repo URL：`https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
   - 关键信息：虽然仓库目前更像 proposal / design doc，不是完整回测引擎，但它把 **funding spread / basis deviation / rolling z-score / funding sign reversal / volatility / liquidity** 这套因子壳一次性点全了，而且明确把问题定义成 **“net of trading costs 之后，哪些 funding dislocation 值得做、该持有多久”**。
2. **dYdX Operations (官方文档). _Default funding rates on dYdX_.**
   - Readable URL：`https://help.dydx.trade/en/articles/166992-default-funding-rates-on-dydx`
   - 关键信息：dYdX 默认 **每分钟采样 funding premium、每小时结算 funding**；funding 本质上就是 perp 与 index 偏离的机制化转译，所以它天然适合被拆成 **短周期 state variable**。
3. **Songrun He, Asaf Manela, Omri Ross, Victor von Wachter (2024 draft; first draft 2022). _Fundamentals of Perpetual Futures_. arXiv working paper.**
   - DOI：`10.48550/arXiv.2212.06888`
   - Readable URL：`https://arxiv.org/abs/2212.06888`
   - HTML / full text：`https://arxiv.org/html/2212.06888v5`
   - 关键信息：作者给 perpetual futures 建了 **random-maturity no-arbitrage benchmark**，并报告：crypto perp 相对理论锚的 **mean absolute deviation 约 60%~90% 年化**；基于这个偏离做的简单 arbitrage strategy，在 BTC perpetual 上 **Sharpe 约 1.8（高成本零售）到 3.5（低成本做市）**。
4. **Binance USDⓈ-M Futures 公共 API 文档**
   - Funding history：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`
   - Mark price / index price：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price`
   - Open interest：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest`
   - 关键信息：这些都是 **公开可得、无需 key 的基础字段**，足够先做 `1m/5m -> funding horizon` 的最小实验。

这轮值得写它，原因很简单：

- 当前 `LEARNING_TRACK / FACTOR_BACKLOG` 里，方向层、breakout 层、确认层已经很多；
- desk 现在更该继续补的是 **raw alpha 素材池里另一个完全不同家族：carry / funding / basis / stat-arb**；
- 这份 2026 新 repo 虽然不成熟，但恰好给了一个很适合我们 desk 的读法：
  **别只按 funding 水平排序，而是把“会不会继续付、basis 会不会回、多久回、成本后还剩多少”一起建模。**

所以这轮不是去抄 repo 的深度学习 headline，而是把它里面最适合我们 desk 的那根主梁抽出来：

> **先落地一个 plain-vanilla、可复现、可成本化的 `funding + basis` delta-neutral raw alpha；ML 只作为第二阶段的 persistence ranker。**

## 2. 一句话核心结论 + 它是怎么证明的
### 一句话核心结论
**别把 funding 只当“越高越值得空”。对 short-cycle desk，更值得先测的是：用 `funding level + basis deviation + sign-flip veto + hold-horizon governance` 搭一个 delta-neutral carry shell，只在“偏离足够大、预计还能撑过下一到几次 funding、且成本后仍有 edge”的时候进。**

### 一句话它怎么证明
- **repo 侧**：把真正该看的变量写得很清楚——`funding spread / basis / z-score / sign reversal / liquidity / volatility`；这说明作者自己也知道 **高 funding 本身不等于好交易**；
- **官方机制侧**：dYdX 明确是 **分钟级 premium 采样 + 小时级 funding 结算**，Binance 也公开给出 `funding history / mark/index / OI`，所以这条线不是纸上谈兵，数据口径公开可拿；
- **论文侧**：He et al. 说明 perp 偏离不是零星噪音，而是足够大、足够 persistent、足够能支持净 alpha 的结构性现象。

## 3. 这份 repo 真正值钱的，不是 deep learning，而是它把 raw alpha 壳讲对了
### 3.1 repo 最值得抽出来的，不是模型名，而是问题定义
README 里最值钱的一句其实不是 “LSTM / Transformer”，而是这层意思：

> **高 funding rate 不自动等于可做套利，因为关键取决于：偏离会不会收、要持有多久、扣完 fees / slippage / gas 之后还剩不剩。**

翻成人话：
- 同样都是正 funding，
- 有些是 **快要反转**，你刚进去就拿不到下一笔 funding；
- 有些虽然 funding 高，但 **basis 已经过头、流动性很差、滑点太大**；
- 有些 funding 没那么夸张，但 **basis 与 premium 都在同向扩张且还没翻转**，反而更值得做。

这其实已经不是“单因子 carry”，而是一个 **完整 raw alpha 主体**。

### 3.2 repo 提到的 5 类变量，正好能翻译成 desk 版最小信号
README 里点到的变量包括：
- funding spread
- basis deviation
- rolling z-score
- funding sign reversal
- volatility / liquidity indicators

把它翻译成 desk 语言，其实就是：

1. **funding 本身有多肥**
   - `funding_t`
   - `annualized_funding_t`
2. **perp 现在相对 spot / index 偏得有多离谱**
   - `basis_t = mark / index - 1`
   - `premium_t = perp - index`
3. **这种偏离是平常波动，还是异常极值**
   - `z_funding`
   - `z_basis`
4. **偏离还在延续，还是快翻车了**
   - `funding_sign_flip`
   - `basis_slope`
   - `premium_acceleration`
5. **值不值得为了这点 edge 去成交**
   - `spread / depth / OI / volume / slippage proxy`

这 5 层凑在一起，已经足够做一个 **entry / exit / sizing / veto** 都齐的策略骨架。

### 3.3 dYdX 文档给的节奏，非常适合 1m 状态更新 + 5m/15m 交易决策
官方文档里有几个点对 short-cycle desk 特别重要：

- dYdX 默认 **每分钟** 形成 funding sample；
- **每小时** 结算 funding；
- funding 目的就是让 perp 回到 oracle / index 附近；
- funding 与 premium 是机制上直接相连的。

这意味着对我们来说，最自然的实验节奏不是：
- 非要在 funding 结算点才做一次决策；

而是：
- **用 `1m` 更新 state**（premium / basis / slope / OI / liquidity）；
- **在 `5m / 15m` bar close 决定要不要进、要不要续持**；
- **用下一次或下几次 funding tick 作为 payoff 事件**。

这正好适配当前 desk 的默认周期。

### 3.4 He et al. 给了最关键的理论底座：这不是“零风险 carry”，而是 random-maturity stat-arb
这篇 arXiv 最该被记住的不是复杂推导，而是两个 desk 结论：

1. **perpetual futures 的偏离确实够大**
   - 文中写到不同 crypto 上相对理论锚的 **mean absolute deviation 约 60%~90% 年化**；
2. **但它不是无脑送钱**
   - 因为你不知道市场什么时候回，
   - 交易有成本，
   - 持仓期间还要承受追加保证金、流动性冲击、继续偏离的风险。

这和 repo 的直觉正好对上：

> **正确问题不是 “今天 funding 高不高”，而是 “这笔 funding/basis 偏离值不值得拿、要拿多久、在我们这种成本下还有没有正 EV”。**

## 4. 适合当前 desk 的完整策略读法：先做 plain shell，再谈 ML persistence
我建议把这条线拆成两层：

### 4.1 第 1 层：plain-vanilla raw alpha shell（先做这个）
这是最小可复现、最适合先落地的一版。

#### 交易对象
优先两种：

**方案 A：单标的 spot-perp delta-neutral（最直观）**
- `long spot / short perp`：当 perp 太贵、funding 为正；
- `short spot / long perp`：当 perp 太便宜、funding 为负；
- 但第二种往往受限于现货可借性 / 借币成本，所以最小实验可先只做 **正 funding 一侧**。

**方案 B：同标的 perp-perp cross-venue carry（更对称）**
- 同一个 underlier，找 `高 funding venue` 和 `低 funding venue`；
- 做 `long cheap leg / short rich leg`；
- 更接近真正的双向 stat-arb，也更适合把“sign flip / persistence”做成持仓治理。

对当前 desk，我更推荐：
- **最小实验先做 A（spot-perp 正 funding 一侧）**；
- **desk 版扩展再做 B（cross-venue richest-vs-cheapest）**。

#### 交易频率
- 状态更新：`1m`
- 决策频率：`5m` 为主，`15m` 做更低 churn 版本
- payoff 观察窗：
  - dYdX 类小时 funding：看未来 `1~3` 次 funding tick
  - Binance 类 `8h` funding：看未来 `1` 次 funding tick + tick 前的 basis 回归

#### 基础信号
对每个 symbol / leg，计算：

- `basis_t = mark_t / index_t - 1`
- `z_basis_t = zscore(basis_t, L)`
- `funding_t = lastFundingRate or predicted funding`
- `z_funding_t = zscore(funding_t, Lf)`
- `sign_flip_t = 1{sign(funding_t) != sign(funding_{t-1})}`
- `liq_t = depth or spread or OI proxy`
- `rv_t = realized_vol`

然后构造一个 plain score：

`dislocation_score = w1 * z_funding + w2 * z_basis - w3 * sign_flip_risk - w4 * cost_proxy`

先别急着 ML，直接从 **规则版** 开始：
- `z_funding >= 1.5`
- `z_basis >= 1.5`
- `funding > 0`
- `sign_flip_risk = 0`
- `liq_t` 过门槛
- `expected_next_tick_carry - fees - slippage > 0`

满足时开 `long hedge leg / short rich leg`。

### 4.2 第 2 层：persistence / hold-time ranker（ML 可以放这里）
repo 真正适合被拿来做“旁支增强”的地方，是这个问题：

> **同样都满足 entry，哪一些值得持有到下一次 funding，哪一些其实只该拿 basis 回归，不该硬等 funding？**

这时再把 ML / LSTM / Transformer 放进来就合理了。

预测对象不要做成“明天涨跌”，而是做成更贴近交易的问题：
- 未来 `1` 个 funding tick 后的净收益是否 > 0
- 未来 `2~3` 个 funding tick 的累计净收益分位
- 下一窗口 funding 是否 sign flip
- basis 是否会先回归到中位而 funding 还没兑现

这比直接预测价格方向，更符合这条 alpha 的结构。

## 5. desk 版完整规则：entry / exit / sizing / risk / cost
下面给一版可以直接抄去做 first backtest 的规则壳。

### 5.1 Entry
以最小实验版 `long spot / short perp` 为例：

开仓条件：
1. `funding_t > 0`
2. `z_funding_t >= 1.5`
3. `z_basis_t >= 1.5`
4. 过去 `k` 个 `1m` 状态里，`basis_slope >= 0` 且未出现明显 `sign_flip`
5. `spread / slippage / fee` 估算后，
   `expected_edge = expected_funding_horizon + expected_basis_reversion - fees - slippage - borrow_cost > 0`
6. 流动性不过差：
   - spread 不在过去 30 天 top decile
   - OI 不在过去 30 天 bottom decile

对称负 funding 侧，仅在 **可借现货 / 可做反向 hedge / 或 cross-venue 对冲成立** 时启用。

### 5.2 Exit
任何一个满足就平：
1. `z_basis` 回到 `0.5` 以内
2. `funding` 出现 sign flip
3. 已吃到目标 funding tick 数（例如 `1~3` 次）
4. `basis` 继续朝不利方向扩张超过 `entry_basis + 1.0 * rolling_std`
5. 流动性恶化到 veto：spread / depth / OI 明显变差
6. 达到最大持有时长：
   - 小时 funding venue：`3h ~ 6h`
   - `8h` funding venue：`8h ~ 16h`

### 5.3 Sizing
先做最保守的 delta-neutral：
- 两腿名义金额 1:1 对冲；
- 单标的 notional = `min(vol_target_cap, OI_cap, depth_cap)`；
- 建议 first pass：
  - 单标的资金占用不超过组合 NAV 的 `10%~15%`
  - 单 venue 毛敞口不超过 `35%`
  - funding / basis 同家族总毛敞口不超过 `50%`

若要更 desk 化，可把仓位和 `expected_edge / expected_holding_hours / slippage` 绑定：

`size_i ∝ expected_edge_i / (vol_i * slippage_i)`

### 5.4 风险
这条线最需要防的不是方向，而是下面几件事：

1. **basis 继续扩张而不是回归**
2. **funding 结算前 sign flip**
3. **流动性变差，账面 edge 被滑点吃光**
4. **跨 venue / 现货腿执行不同步**
5. **借币、保证金、资金占用成本**
6. **交易所 / 结算 / 对手方风险**

所以别把它误读成“低波动无脑 carry”。它本质上仍是 **持有期随机的 stat-arb**。

### 5.5 成本
必须显式建模：
- 两腿手续费
- 吃单/挂单差异
- 盘口滑点
- 借币/融资成本
- 跨 venue 提现/调仓 friction（如果有）
- funding 兑现时点与实际持仓时间错位

如果不把这些写进去，回测会天然高估。

## 6. 它和当前 `1m / 3m / 5m / 15m` desk 的关系，到底在哪
这条 alpha 不是逐根 1m K 线方向预测，但它跟 short-cycle 完全不冲突：

### 6.1 `1m`
- 用来更新 premium / basis / slope / sign-flip risk / micro-liquidity
- 更像 state monitor

### 6.2 `3m / 5m`
- 是最自然的决策层
- 足够快，能在 funding tick 前做 admission / cancel / reduce
- 又不至于被 1m 噪音打爆

### 6.3 `15m`
- 更适合低 churn 版本
- 用于更稳的 `basis z-score + vol/liquidity gate`
- 也适合做 benchmark，对照 `5m` 是否只是多付了手续费

所以正确读法不是“funding 太低频，不适合短周期”，而是：

> **funding 是 payoff event；premium / basis / sign-flip / liquidity 才是分钟级 state。**

## 7. 最小可复现实验：先别做全市场，先把这 4 个 baseline 跑出来
### 数据源
优先公开可得：

1. **Binance USDⓈ-M**
   - `GET /fapi/v1/fundingRate`
   - `GET /fapi/v1/premiumIndex`
   - `GET /fapi/v1/openInterest`
2. **dYdX 官方 funding 机制 / 历史数据接口（若后续补 SDK）**
3. 如要 cross-venue，再补 Bybit / OKX / Hyperliquid 的公开 funding / mark / OI

### 更新频率与实验口径
- 原始状态：尽量 `1m`
- 聚合决策：`5m / 15m`
- 先做 `BTC / ETH / SOL` 三个大币
- 样本先取最近 `60~120` 天

### 先跑 4 个 baseline
**B0：level-only**
- 只按 funding 排序；
- 最肥的做 `long hedge leg / short rich leg`；
- 持有到下一次 funding tick。

**B1：funding + basis**
- 要求 `z_funding` 和 `z_basis` 同时极值；
- 其他不变。

**B2：B1 + sign-flip veto**
- 若 funding 或 premium 已出现翻转迹象，不开。

**B3：B2 + liquidity / OI gate**
- 过滤掉流动性差和 OI 过低样本。

### 主要评估指标
至少看：
- 每笔净收益（扣双边 fees / slippage）
- 胜率
- 平均持有时长
- funding 部分 vs basis 回归部分各贡献多少
- 最大不利偏移（MAE）
- 资金占用回报
- 正收益交易占比 / 正收益窗口占比

如果 B0 明显不行而 B2/B3 改善很大，那就说明 repo 这条“persistence / flip / liquidity”读法是真有料，不只是包装。

## 8. 我对这条线的当前判断
### 为什么它值得进研究池
1. **它是 raw alpha，不是纯 filter**
   - 不依赖 breakout、retest、trend 才能存在；
   - 自己就是一条可独立跑的 carry / stat-arb 策略。
2. **它和当前 desk 已积累的方向性 alpha 相关性大概率不高**
   - 这对组合层面很值钱。
3. **公开数据可拿，最小实验门槛低**
   - 不需要私有订单流，也不需要链上账户归因才能开始。
4. **repo 的可取之处恰好不是 headline，而是可执行变量表**
   - 这非常适合 digest：不抄结论，直接拆组件。

### 当前最大保留意见
1. 这个 repo 目前还是 **proposal / skeleton**，不是成熟回测框架；
2. 真正决定收益的，多半不是“模型多 fancy”，而是：
   - execution
   - hold horizon
   - sign flip detection
   - fee / slippage / borrow discipline
3. 若只做 Binance 8h funding，short-cycle 味道会弱一些；
   - 更适合配合 `1m state + 5m admission` 去做，
   - 而不是把自己误读成纯小时内 scalping。

## 9. 下一步怎么测（直接可执行）
这轮最推荐的 next step 不是继续搜更多论文，而是立刻做一个 **honest first backtest**：

### Step 1
先做 **单 venue、正 funding 一侧、spot-perp**：
- `BTC / ETH / SOL`
- `5m` 决策
- 事件窗 = 下一次 funding tick

### Step 2
跑四组对照：
- `level-only`
- `level + basis`
- `level + basis + sign-flip veto`
- `level + basis + sign-flip veto + liq/OI gate`

### Step 3
把 PnL 拆成三部分：
- funding 收入
- basis 回归收益
- 成本损耗

### Step 4
若 `B2/B3` 相对 `B0/B1` 明显抬升：
- 再做 **cross-venue richest-vs-cheapest** 版本；
- 再考虑把 repo 里那层 ML persistence ranker 加进来。

### Step 5
若发现 edge 主要来自 **basis 回归而不是 funding 本身**：
- 那就把这条线重新归类成 **basis MR raw alpha**；
- funding 只保留为 entry admission / hold governance。

这一步非常关键，因为它决定我们后面该把它放进 `carry` 家族，还是放进 `basis / relative-value` 家族。

## 10. 参考资料
1. **Menger Wen / hanqihang / collaborators. (2026). _Deep-Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates_. GitHub repository.**  
   - Readable URL：`https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`  
   - Repo URL：`https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
2. **dYdX Operations. _Default funding rates on dYdX_.**  
   - Readable URL：`https://help.dydx.trade/en/articles/166992-default-funding-rates-on-dydx`
3. **He, S., Manela, A., Ross, O., & von Wachter, V. (2024 draft; first draft 2022). _Fundamentals of Perpetual Futures_. arXiv working paper.**  
   - DOI：`10.48550/arXiv.2212.06888`  
   - Readable URL：`https://arxiv.org/abs/2212.06888`  
   - HTML / full text：`https://arxiv.org/html/2212.06888v5`
4. **Binance Open Platform. _Get Funding Rate History_.**  
   - Readable URL：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`
5. **Binance Open Platform. _Mark Price_.**  
   - Readable URL：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price`
6. **Binance Open Platform. _Open Interest_.**  
   - Readable URL：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest`
