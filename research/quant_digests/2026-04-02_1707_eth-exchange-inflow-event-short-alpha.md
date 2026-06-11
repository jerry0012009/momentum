# 别把 on-chain flow 只当链上噪音：这篇 arXiv 更该先测的是「ETH 交易所净流入冲击 × 1~6h bearish drift」事件驱动 raw alpha

- 时间：2026-04-02 17:07 UTC
- 类型：论文
- 主题标签：raw-alpha/single-asset/event-driven/on-chain/exchange-netflow/eth/usdt/mean-reversion-vs-drift/short-bias/1h/15m/5m/3m/1m/external-data/paper
- 证据类型：paper/fulltext/public-data-proxy
- 主题类型：raw alpha
- 基础 alpha：`ETH 净流入交易所` 代表更直接的卖出意图，论文里它对 **未来 1~6 小时 ETH 收益为负**；desk 化后可先做 **ETH exchange-inflow shock → short ETH perp** 的事件驱动策略
- 是否可独立复现：是（可用公开链上转账 + 交易所标签做近似复现；严格复刻仍受标签覆盖率约束）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 先回答一句：这篇东西的 base alpha 是什么？
这轮真正值得 intake 的 **base alpha** 很清楚：**当 ETH 大额净流入交易所时，后面 1~6 小时 ETH 更容易继续偏弱；这不是 filter，而是一条可独立做空、可独立回测、可独立风控的事件驱动 raw alpha。**

USDT 净流入交易所会给 BTC / ETH 带来短时正收益，这也有用；但对当前 desk 来说，**最值得先落地的主线不是“USDT risk-on gate”，而是更直接、更单资产、可直接下成完整策略的 `ETH inflow shock short`。**

---

## 1. 这次看了什么
这次看的是一篇能直接补进 raw alpha 素材池、而且和现有 digest 不重复的论文：**Yeguang Chi / Qionghua (Ruihua) Chu / Wenyan Hao 的 arXiv 预印本《Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets》**。

它不是在讲泛泛的“链上活跃度有信息”，而是把 **BTC / ETH / USDT 净流入交易所** 直接拿来预测 **未来 1、2、3、4、6 小时的收益和波动**。对 short-cycle desk 最值钱的，不是整篇都搬，而是把其中最硬的那条结论拆出来：

> **ETH 交易所净流入冲击，本身就可以做成 ETH 的事件驱动 short raw alpha。**

一句话核心结论：**ETH 被明显转进交易所时，接下来几小时 ETH 更容易继续走弱；这条关系在论文里比 BTC own-flow、更稳定，也比把 on-chain flow 只当宏观解释更能直接变成交易规则。**

一句话说明它怎么证明：**作者用 2017-12-16 到 2023-01-20 的链上净流入与价格数据，按 1/2/3/4/6 小时 horizon 做 in-sample / out-of-sample 回归与稳健性检验，发现 ETH net inflow 对未来 ETH return 的负向预测在所有这些 intraday horizon 上都成立。**

---

## 2. 为什么这轮值得写它
最近 digest 池里的 raw alpha 已经很多来自：
- CEX 盘口 / OFI / taker-flow
- pairs / stat-arb / basis / funding / options
- ETF / Polymarket / cross-market lead-lag

但**“公开链上转账 → 未来几小时收益”** 这种事件驱动 alpha 还没被单独拆成可执行策略壳。

这轮值得写它，原因有 4 个：

1. **base alpha 清楚**：不是“链上数据也许有帮助”，而是 `ETH inflow to exchanges -> later ETH returns weaker`；
2. **直接可交易**：它天然对应 `事件触发 → 下一根/下一组 5m/15m bar 入场 → 固定持有 / 反向退出`；
3. **和当前 desk 兼容**：虽然论文原始 horizon 是 `1~6h`，但完全可以下沉成 `15m` 执行与 `1m/3m/5m` timing；
4. **不是重复 old pairs/carry 主题**：它补的是我们现在相对缺的 **on-chain event alpha**，而不是再写一篇 cointegration / funding。

---

## 3. 主要来源

### 3.1 主来源论文
- **Authors / Year**: Yeguang Chi, Qionghua (Ruihua) Chu, Wenyan Hao / arXiv 2024，文稿版本标注 2025-06
- **Title**: *Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets*
- **Venue**: arXiv preprint
- **DOI**: `10.48550/arXiv.2411.06327`
- **Readable URL**: https://arxiv.org/abs/2411.06327
- **PDF URL**: https://arxiv.org/pdf/2411.06327
- **Repo URL**: 未找到作者官方复现仓库

### 3.2 公开可得的数据近似路径（用于 desk 最小实验，不是论文官方数据声明）
1. **Whale Alert API docs**
   - URL: https://developer.whale-alert.io/documentation/
   - 用途：抓取大额链上转账事件，先做 exchange-inflow 事件流近似
2. **Etherscan 标签页 / label cloud**
   - URL: https://etherscan.io/labelcloud
   - 用途：定位 ETH / USDT 交易所标签地址，给 inflow 事件做 exchange mapping
3. **ETH / USDT 链上明细页（Etherscan）**
   - URL: https://etherscan.io/
   - 用途：校验转账时间戳、金额、目标地址

> 这轮没有硬找一个“和论文完全同口径”的 GitHub 策略 repo 来凑数。原因很简单：**真正值钱的是论文给出的那条可交易关系本身**，不是随便找个 on-chain dashboard repo 贴上去冒充实现。

---

## 4. 论文真正证明了什么

### 4.1 数据与方法
- 样本期：**2017-12-16 到 2023-01-20**
- 资产：**BTC / ETH / USDT**
- 频率：**1h / 2h / 3h / 4h / 6h**
- 核心解释变量：**净流入交易所（net inflow = inflow - outflow）**
- 核心被解释变量：未来收益、未来波动
- 检验方式：single-variable + double-variable predictive regressions，并做 in-sample / out-of-sample robustness

翻成人话：作者不是在做复杂模型，而是在问一个很朴素也很 desk-friendly 的问题：

> **“某种币被明显转进交易所时，后面几个小时，它自己和别的核心币会怎么走？”**

### 4.2 对 desk 最有价值的几个硬结论

#### 结论 A：ETH 净流入，对 ETH 收益是稳定负预测
论文正文明确写到：
- **ETH net inflows negatively predict ETH returns across all intraday intervals of 1, 2, 3, 4, and 6 hours**
- 作者给的量化例子是：**US$1 million 的 ETH 净流入，预测下一小时 ETH 收益约 `-1.70%`**

别纠结这个数值是否会在今天的交易环境里原样复现；真正重要的是：
- **符号明确：负号**
- **区间稳定：1~6h 都成立**
- **交易含义直接：可以做成 short-alpha，而不是只当解释变量**

#### 结论 B：USDT 净流入，更像短时 risk-on 干粉
论文发现：
- **USDT net inflows positively predict ETH and BTC returns，尤其在 1h / 2h 上显著**
- 作者给的量化例子：**USDT 净流入 US$100m，预测下一小时 ETH 收益约 `+0.11%`，BTC 收益约 `+0.065%`**

这个分支也有价值，但更适合作为：
- ETH short 的否决条件
- 或另开一条 `USDT inflow long BTC/ETH` sibling alpha

#### 结论 C：BTC own-flow 对 BTC return 没有 ETH 那么稳
论文同时写到：
- BTC net inflows 对 BTC returns **大多缺少稳定预测力**
- 只有 **4h horizon** 比较像正向关系

所以对 intake 排序来说，**先做 ETH，不先做 BTC** 是更理性的。

#### 结论 D：ETH inflow 不只是预测跌，还预测后续 volatility 走低
作者还发现：
- ETH net inflows 对 ETH volatility 也多为负预测
- 给出的量化例子：**US$1 million 的 ETH net inflow，预测未来 2 小时 ETH volatility 约 `-0.37%`**

翻成人话：**这不像“暴跌前高波动”；它更像“卖压进交易所 → 先跌一段 → 后面进入更低波动的压价/稳定阶段”。**

这很适合 desk 化成：
- `event short + fixed hold`
- 而不是依赖“大波动继续放大”的 breakout 壳

---

## 5. 对我们最该 intake 的，不是整篇 paper，而是这条主策略

### 主 intake：ETH exchange-inflow shock short
如果只保留一条最值得进研究池的 raw alpha，我会保留：

> **当 ETH 交易所净流入出现显著冲击时，在下一根可执行的 `5m / 15m` bar 做空 ETH perp，持有 `1~3h`，优先测 fixed-hold 与简单反向退出。**

### 为什么它比 USDT inflow long 更适合先做主 digest
1. **方向更单纯**：ETH inflow 本身就是 ETH 的卖出意图代理；
2. **资产映射更直接**：不用先判断“USDT inflow 最终买的是 BTC 还是 ETH”；
3. **结论更稳定**：论文里 ETH own-flow 负预测跨 1~6h 都成立；
4. **更像完整 raw alpha**：不是先有一个 risk-on 宏观判断再找交易标的，而是 `事件 -> 标的 -> 方向` 一步到位。

### sibling，不是主线：USDT inflow long risk
USDT inflow 分支当然值得保留，但我会把它放在第二顺位：
- 作为 `ETH inflow short` 的反向 veto
- 或开一个 `USDT inflow shock -> long BTC/ETH for 1~2h` 的 sibling 策略

---

## 6. 怎么 desk 化成一条完整策略

下面给的是**最小可落地版本**，不是声称已经验证过，而是为了让它能立即进入 first verdict。

### 6.1 交易对象
- 主标的：**ETHUSDT perp**
- 首选 venue：Binance / Bybit（后续可双 venue 交叉）
- 执行 bar：**15m 为主，5m 为精细 timing，1m/3m 只用于执行切片**

### 6.2 事件时钟
- 先把链上转账聚合成 **hourly ETH exchange net inflow**
- 在整点后拿到上一小时 inflow 读数
- 用 rolling 30d / 60d 小时级历史做 z-score 或 percentile

### 6.3 入场规则（第一版）
做空 ETH perp，当且仅当：
1. `ETH exchange net inflow zscore >= 2.0`
2. 事件小时结束后的第一根 `15m` bar 还未出现过度追空（例如：相对事件小时开盘的位移 `< 1.25 * ATR(15m, 20)`）
3. 同时 `USDT exchange inflow zscore < 1.5`，避免被强 risk-on 干粉抵消

翻成人话：
- 先要有**真的 inflow shock**；
- 再避免**已经跌完你才去追**；
- 最后不要在 **USDT 也同时猛灌进交易所** 时硬空。

### 6.4 出场规则（第一版）
先别搞复杂，直接做 3 组 time-stop：
- `4 x 15m`（1h）
- `8 x 15m`（2h）
- `12 x 15m`（3h）

再加一个最简单的 adverse exit：
- 若入场后任意 `5m` 收盘重新站上 **事件后首根 15m bar 高点 + 0.25 ATR(5m, 20)**，提前止损出场

为什么先这样：
- 论文 strongest message 是 **未来几小时偏弱**，不是说要抓整天趋势；
- 所以第一轮最应该测的是 **固定持有窗口**，而不是一开始就卷 trailing stop。

### 6.5 仓位与风险
- 单次事件风险预算：`0.35R ~ 0.50R`
- 仓位按 `1 / ATR(15m, 20)` 做 inverse-vol scaling
- 同方向 cooldown：同一币种 **4 根 15m bar 内只吃 1 次 inflow 事件**
- 若同一天出现 `>=3` 次极端 inflow shock，第三次开始半仓

### 6.6 成本处理
first verdict 必须直接上 friction ladder：
- 手续费：`4 bps / side`（保守）
- 额外冲击成本：`1 / 2 / 4 bps` 三档
- 全成本后看：
  - event count
  - net expectancy
  - average MAE / MFE
  - holding-window survival

> 如果一条事件驱动 alpha 过不了最基本的 `4+2 bps` 成本测试，就不要因为“论文里方向对了”而心软。

---

## 7. 和当前 `1m / 3m / 5m / 15m` desk 的关系

### `15m`
最自然。因为论文原始 horizon 是 `1~6h`，下沉成 `15m` 后，刚好能用 `4 / 8 / 12 / 24` bar 做持有窗口扫描。

### `5m`
最适合作为 execution 层：
- 决定是否已经跌过头
- 做 adverse exit
- 做冲击后的 first retrace short

### `1m / 3m`
不是拿来重定义 alpha 本体，而是拿来：
- 拆分进场滑点
- 做 event 后 15 分钟内的入场切片
- 看 market order / taker-flow 是否已经把主要下跌在事件确认前打完

换句话说，这条策略应该理解为：

> **hourly on-chain event alpha + 15m strategy shell + 5m/1m execution refinement**

而不是“1m 链上预测模型”。

---

## 8. 数据源、公开性、更新频率、最小可复现实验口径

### 8.1 数据源
对于 desk 最小实验，优先不追求论文级完美净流入口径，而是先做可复核近似：

1. **Whale Alert / 同类大额转账事件流**
   - 抓 ETH / USDT 向交易所标签地址的大额转账
2. **Etherscan 标签地址**
   - 给 Binance / Coinbase / Kraken / OKX 等热钱包做 entity mapping
3. **CEX 价格数据**
   - Binance / Bybit ETHUSDT perp `1m/5m/15m` klines

### 8.2 公开性
- 链上转账本身：**公开可得**
- 交易所标签：**公开可查，但覆盖不完美**
- 论文原始净流入数据库口径：**未必完全公开**

所以这里最诚实的说法是：

> **可以公开近似复现，适合先做 first verdict；若 first verdict 过关，再考虑补更完整的地址簇与商业标签数据。**

### 8.3 更新频率
- 链上转账：近实时 / 分钟级
- 标签地址：静态 + 低频更新
- CEX 行情：秒级 / 分钟级

### 8.4 最小实验口径
先做最小、不自欺的版本：

#### 实验 1：ETH inflow shock 事件研究
- 采样：过去 `60~180` 天
- 事件：`ETH inflow zscore >= 1.5 / 2.0 / 3.0`
- 观察窗口：后续 `4 / 8 / 12 / 24` 根 `15m`
- 输出：平均累计收益、hit rate、MAE、MFE、事件数

#### 实验 2：加一个“别追太晚” veto
- 若事件确认时，ETH 已相对事件小时开盘跌超 `1.25 ATR(15m,20)`，跳过
- 看是否提升 expectancy / 降低 MAE

#### 实验 3：USDT inflow 做 sibling / veto
- 对比三组：
  1. 只看 ETH inflow short
  2. `ETH inflow - USDT inflow` differential score
  3. ETH inflow short + USDT extreme risk-on veto

如果 differential score 明显更稳，再考虑把它升为正式版本；否则保留最朴素的 ETH 主策略。

---

## 9. 我最建议先测的 5 个假设

1. **`ETH inflow zscore` 的有效阈值可能不是越高越好**
   - 极端大事件可能已经被盘口提前 price in；
   - `z >= 2` 可能比 `z >= 3` 更有风险收益比。

2. **最优持有时间可能在 `1~2h`，而不是拖到 `6h`**
   - 论文证明 1~6h 都有预测力；
   - 但对 perp 执行来说，alpha 可能在前半段最浓。

3. **USDT inflow 更适合作为 veto，不一定适合和 ETH inflow 做线性合成**
   - 因为它更像买盘干粉，不是 ETH 自身卖压；
   - 它可能适合做“不要空”的条件，而不是 alpha 主体。

4. **事件后 first 15m retrace short，可能优于事件确认当刻直追**
   - 这条最值得在 `1m/3m/5m` 上测；
   - 如果成立，会大幅改善成本后生存率。

5. **Binance / Bybit 的反应速度可能不同**
   - 若链上事件先被某个 venue price in，跨 venue execution 也会影响生存率。

---

## 10. 风险与失败模式

1. **标签质量风险**
   - 交易所热钱包更新、归集地址变动，会让 netflow 失真。

2. **时间戳风险**
   - 区块确认时间、归集延迟、批量打包，会让“事件发生时刻”不够干净。

3. **样本集中在极端日**
   - 这类信号可能主要赚 2022 风险事件，不代表平时也稳定。

4. **过度追空风险**
   - 论文里的方向关系，不等于你在所有事件确认点追进去都能赚钱。

5. **BTC 复制风险**
   - 论文已经提示 BTC own-flow 没 ETH 稳，所以不要一上来平移到 BTC。

---

## 11. 为什么我把它归类成 raw alpha，而不是 filter / overlay
因为它已经能闭环写成：
- **事件**：ETH inflow shock
- **标的**：ETH perp
- **方向**：short
- **持有**：1~3h（先测）
- **风险**：ATR + cooldown + cost ladder
- **扩展**：USDT inflow veto / sibling

这不是“链上情绪帮助你理解市场”，而是**链上事件本身就是进场键**。

---

## 12. 下一步怎么测
只给一个最务实的 next step：

1. **先做 ETH，不做 BTC**；
2. **先做 event study，不先做复杂回测器**；
3. **先用公开标签地址近似，确认有没有 post-event bearish drift**；
4. **第一轮只扫 `15m` 上的 `4/8/12/24` bar 累计收益**；
5. **若 `ETH inflow short` 在 `4+2 bps` 成本后仍有正 expectancy，再补 `5m retrace entry` 与 `USDT veto`。**

我会把这条主题的当前结论压缩成一句话：

> **对 short-cycle desk，这篇 paper 最值得先抄的不是“on-chain data 有信息”，而是“ETH 交易所净流入冲击本身就能做成一条 15m 执行、1~3h 持有的事件驱动 short raw alpha”。**
