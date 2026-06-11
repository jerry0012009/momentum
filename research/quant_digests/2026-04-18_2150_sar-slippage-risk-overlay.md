# 别把 Sepper (2026) 只读成“交易所风控论文”：对 short-cycle crypto desk，更该先拆的是「Slippage-at-Risk 入场否决 / 降杠杆 / size-down」这层 shared execution overlay

- 时间：2026-04-18 21:50 UTC
- 类型：2026 arXiv working paper 全文（HTML）
- 主题类型：overlay
- 基础 alpha：**任何高换手、会被流动性与冲击成本直接杀死的 raw alpha**——尤其是 `1m/3m/5m/15m` 的 breakout / continuation / liquidation-follow / cross-sectional router / pairs spread entry；这篇 paper 更适合拿来做 **execution veto / leverage gate / tail-risk sizing**，而不是包装成新的主 alpha
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（更像 shared overlay，但已经足够直接落地到现有多条策略线上）
- 主题标签：overlay / execution / slippage / liquidity-risk / order-book / concentration / leverage / risk / admission / veto / size-down / perpetual-futures / hyperliquid / 1m / 3m / 5m / 15m / paper / fulltext / public-data
- 证据类型：论文全文框架 + 论文内 Hyperliquid 实证结果

先回答 base alpha：**能答清，但它不是 paper 自己生成的新 raw alpha。**
这篇东西服务的母体 alpha 很明确：
- breakout / continuation
- liquidation-follow / event-driven push
- cross-sectional router
- funding / basis / pairs 这类需要在薄书里进出的高换手策略

它真正给 desk 的价值不是“再发明一个方向信号”，而是：

> **先问一句：这会不会在当前 order book / 流动性集中度 / tail slippage 条件下，明明信号对了，但一进去就被冲击成本和流动性抽干？**

如果会，那这轮该做的不是“追”，而是：
- 不入场；
- 降杠杆；
- 降 size；
- 或把这次信号只保留给最深、最厚、最不脆的那几个标的。

这也是我这轮愿意接受一个 `overlay` 而不是继续硬补 `raw alpha` 的原因：
**今天素材池里 raw alpha 已经补得很密，但跨 alpha 通用、可直接管住 execution/cost/risk 的 shared overlay 反而稀缺。SaR 这篇正好补这块。**

---

## 1. 这次看了什么
主来源：
- **Author：** Otar Sepper
- **Year：** 2026
- **Title：** *Slippage-at-Risk (SaR): A Forward-Looking Liquidity Risk Framework for Perpetual Futures Exchanges*
- **Venue：** arXiv working paper
- **DOI：** `10.48550/arXiv.2603.09164`
- **Readable URL：** <https://arxiv.org/abs/2603.09164>
- **HTML：** <https://arxiv.org/html/2603.09164v1>
- **PDF：** <https://arxiv.org/pdf/2603.09164>
- **Repo URL：** 未见公开策略仓库

我这轮实际使用的是：
1. arXiv 摘要页；
2. arXiv HTML 全文；
3. 论文内 Section 7 / 8 的经验结果与实现指南。

---

## 2. 用人话讲，这篇 paper 在讲什么
作者想修正一个很常见但很致命的问题：

> 大家老是在用“历史波动”衡量风险，但真正把 short-cycle 策略打死的，很多时候不是历史收益分布，而是 **你现在这笔单打进去，盘口到底接不接得住**。

它把这个问题压成一个前瞻指标：

- **SaR(α)**：横截面 slippage 分位数——比如 `SaR(0.95)=3%`，意思是 95% 的 token 在作者设定的压力清算口径下，滑点不超过 3%。
- **ESaR(α)**：尾部 token 的平均滑点——不是只看门槛，而是看最差那撮到底有多疼。
- **TSaR$(α)**：尾部 token 的总美元滑点暴露——把“疼不疼”和“仓位多大”一起算进去。

然后 paper 还加了一层很关键的东西：

### 2.1 不是只有“深度”，还要看“深度是不是假厚”
两本 order book 看上去都能接住你的单，未必一样安全：
- 一本是 100 个做市商各挂一点；
- 一本是 2 个大号做市商撑着；

表面深度一样，但后者一旦有人撤单，真实 slippage 会突然恶化。

所以作者再加了**流动性集中度惩罚**：
- 用 `HHI` / `N_eff` / `CR1` 去看是谁在供 liquidity；
- 如果书很集中，就在原始 slippage 上打 haircut；
- 得到 concentration-adjusted slippage，再去算 SaR / ESaR / TSaR。

翻成人话：

> **不是只看书厚不厚，还要看这本书是不是“看起来厚、其实脆”。**

这对做 crypto 短周期的人很重要，因为很多你最想追的 bar：
- 正好发生在波动扩大时；
- 正好发生在小币 / 尾部币 / 事件驱动时；
- 正好发生在 market maker 撤单、深度塌陷时。

这时信号再漂亮，execution 也可能是假的。

---

## 3. 为什么它更适合写成 overlay，而不是 raw alpha
因为它解决的问题不是“方向对不对”，而是：

> **这个方向单，值不值得在现在这本书里做。**

所以更诚实的 desk 定位是：

### 3.1 入场否决层（admission veto）
当你已有主信号：
- breakout
- continuation
- liquidation-follow
- pairs spread entry
- cross-sectional long-short router

先加一句：
- 如果 `SaR_adj` 太高；
- 或 `N_eff` 太低；
- 或 `CR1` 太高；
- 或 `TSaR$` 已经处在交易所/组合可承受区间上沿；

那这次别做，或者只做头部深度最好的标的。

### 3.2 降 size / 降杠杆层
不是只有做或不做。
更实用的是：
- `SaR_adj <= 3%`：正常 size；
- `3% < SaR_adj <= 5%`：size 打 0.5~0.7；
- `SaR_adj > 5%`：禁开新仓或只允许减仓。

### 3.3 shared router 层
对横截面 alpha 来说，它可以直接做标的过滤：
- 原本 20 个候选都能排分；
- 但执行前只保留 liquidity regime 合格的前若干个；
- 尾部薄书币种即使分高，也先不碰。

所以这篇 paper 的核心不是“预测价格”，而是：
**帮你把“理论 alpha”筛成“还能实际成交的 alpha”。**

---

## 4. 论文里最值得 desk 拿走的三件事

### 4.1 用 order book 当下状态做前瞻风险，而不是只看历史亏损
这点很朴素，但对短周期很实用。
VaR/ES 这种历史分布指标告诉你“过去容易怎么亏”；
SaR 告诉你“现在如果要打出去，会不会立刻吃到灾难性滑点”。

对 `1m/3m/5m/15m` 的策略，后者往往更接近真实死法。

### 4.2 用“流动性集中度”修正表面深度
paper 给了一个很 desk-friendly 的提醒：

- 同样是薄书，不一定都一样危险；
- 真正危险的是“少数 provider 支撑的薄书”；
- 这种书在 stress 时容易一起撤。

如果你以后只想保留一个近似 proxy，也值得保留：
- `N_eff`（有效 provider 数）
- `CR1`（最大 provider 占比）

就算拿不到链上地址级做市 attribution，也可以先拿**盘口分层深度集中度 proxy** 或 **top-level depth collapse proxy** 做替代实验。

### 4.3 对 desk 来说，`TSaR$` 比纯百分比指标更接近真实可用
paper 的 lead-lag 结果里，**TSaR$ 的预测性强于纯百分比 SaR**。
这很合理，因为 desk 真正痛的是：
- 滑点高，且
- 暴露也大。

所以如果只能保留一个组合层面的监控数，我会优先保留：
- 组合或交易所级 `TSaR$`
- 再辅以单标的 `SaR_adj`

一个看系统总压强，一个看单个候选能不能碰。

---

## 5. 论文里最关键的几个数
### 5.1 全样本结果：尾部流动性风险不是小毛病
论文用 `β = 0.10` 的压力清算口径，在 184 个 token 上算出：
- `SaR(0.95) = 2.84%`
- `SaR_adj(0.95) = 3.47%`
- `ESaR_adj(0.95) = 8.92%`
- `TSaR$_adj(0.95) = $127.4M`
- 尾部 token 数量：`9` 个（约 5%）
- 尾部 OI 占比：`2.3%`（`$196M / $8.51B`）

这里最值得 desk 记住的不是精确数值，而是关系：

> **表面看只有 5% 尾部币危险，但一旦把集中度算进去，adjusted slippage 会明显抬高，而且尾部总美元风险并不小。**

### 5.2 它确实是“提前变坏”的，不只是事后解释
论文在 6 小时滚动窗里做了 lead-lag correlation：
- `TSaR$(0.95)` 与未来 `12h` deficit 的相关性：`0.61`
- 与未来 `24h` deficit 的相关性：`0.42`
- 当期相关性：`0.84`

此外，作者给出的 Granger causality 结果：
- `TSaR -> Deficits`：`F = 8.47`, `p < 0.001`
- 反向 `Deficits -> TSaR` 不显著

翻成人话：

> **它不是“崩完以后回头一看当然危险”；而是在崩之前 6~24 小时就已经开始变差。**

这对我们 desk 非常关键，因为 overlay 是否值得接进生产，核心就看它能不能**提前 veto**。

### 5.3 2025-10-10 Hyperliquid 案例里，它给出的预警很早
论文里 case study 的关键数：
- `SaR_adj(0.95)`：从 `2.41%` 升到 `3.12%`（24h 内上升约 30%）
- `TSaR$_adj(0.95)`：从 `$89.2M` 升到 `$156.3M`
- 总深度：从 `$1,124M` 掉到 `$742M`，再在事件中打到 `$284M`
- 事件 peak 时 `TSaR$_adj(0.95)` 冲到 `$847.2M`
- 事前预测 vs 事中真实滑点拟合 `R² = 0.78`

还有一个非常有 desk 味道的点：
- 平均 `N_eff` 从 `8.7` 掉到 `2.8`
- `CR1` 升到 `0.51`
- peak 时 `73%` 的 token 落在 `N_eff < 3`

意思很简单：

> **不只是“书变薄了”，还是“供书的人突然变得极少”，这时很多短周期策略该做的是刹车，不是兴奋。**

---

## 6. 把它 desk 化：怎么映射到 `1m / 3m / 5m / 15m`

### 6.1 它不该直接当逐 bar 主信号
这不是那种“5m 上穿就买”的 alpha。
更自然的接法是：
- `5m/15m` 负责方向与触发；
- `1m/5m` order book / depth / liquidity state 负责 veto；
- `SaR_adj / TSaR$ / N_eff proxy` 负责 size/risk 决策。

### 6.2 最适合先服务的几类母体 alpha
我会优先接到这些现有/近期 intake 上：

1. **breakout / continuation**
   - 波动最大、最容易冲进薄书；
   - 最需要 execution veto。

2. **liquidation-follow / shock continuation**
   - 信号往往正好发生在流动性最坏的时候；
   - 没有 slippage gate 很容易 gross 对、net 错。

3. **cross-sectional router**
   - 原始分数可以很强；
   - 但若尾部币太薄，实盘成交后 alpha 会被吞掉。

4. **pairs / basis / funding carry 的入场时机**
   - 虽然不是追方向，但开腿/平腿也受 order book 状态影响；
   - 可以用它 veto “价差对了但腿太脆”的时刻。

### 6.3 一个够小、够快的落地规则
先别上完整论文版本，先做一个 desk MVP：

- 对候选标的每 `1m` 刷一次：
  - top-N depth / book walk slippage proxy
  - depth collapse ratio（最近 `30m` vs 当前）
  - top-level concentration proxy（拿不到 provider attribution 时用盘口层 proxy 代替）
- 生成：
  - `single_name_slippage_score`
  - `cross_section_tail_score`
- 决策：
  - 若单标的分数超阈值：禁开 / 降 size
  - 若横截面 tail score 超阈值：整组策略风险降档

这已经足够形成第一版 production overlay。

---

## 7. 一个更适合我们 desk 的“诚实读法”
不要把这篇东西读成“交易所保险基金论文，离自己太远”。
更值得拿走的是：

> **对高换手 alpha 来说，很多所谓风控指标其实太慢；真正该放到执行前一跳问的，是‘当前这本书能不能承接我的策略逻辑’。**

也就是说，这篇 paper 对我们最好的用途，不是解释 Hyperliquid 怎么设计保险基金，而是变成一句朴素的执行问题：

- 这个信号是否只是在**最脆弱的时候看起来最诱人**？
- 如果是，那它该不该被 veto？

这句话本身就很值钱。

---

## 8. first verdict
### 8.1 值得进研究池，但定位必须老实
- **值得保留：是**
- **定位为 raw alpha：否**
- **定位为 shared execution/risk overlay：是**

### 8.2 为什么这轮它仍然值得写
因为今天 raw alpha intake 已经补了不少：
- cross-sectional momentum / reversal
- pairs / stat-arb / basis / funding
- microstructure continuation
- prediction-market structural arb

但这些 alpha 共同缺一层东西：

> **当市场正处在“alpha 最诱人、execution 最恶劣”的交叉区间时，谁来替我们踩刹车？**

SaR 正好给了一个更系统、更前瞻的答案。

---

## 9. 下一步怎么测
### 9.1 最小可复现实验（先不追 provider 级 attribution）
数据源：
- Binance / Bybit / Hyperliquid 公共 order book depth
- 公共 OI / volume / funding 数据

公开性：公开可得

更新频率：
- depth：秒级或更快
- OI/funding：分钟级 / 结算级

最小实验口径：
1. 选择 `BTC / ETH / SOL + 6~12` 个 liquid alts；
2. 每 `1m` 采一版 top-book ~ top20 depth；
3. 对固定 notional（例如 `$25k / $50k / $100k`）做 simulated book walk，算单标的 slippage proxy；
4. 计算：
   - 当前 slippage proxy
   - 最近 `30m` depth collapse
   - 横截面 `p90/p95` slippage
5. 把近期已有 alpha 信号（breakout / liquidation-follow / pairs entry / cross-sectional router）分成：
   - gate 通过
   - gate 不通过
6. 对比两组的：
   - next `15m/1h` gross return
   - 实盘可成交假设下的 net return proxy
   - 极端尾部亏损 / 最大 adverse excursion

### 9.2 最想先验证的两个问题
1. **对 breakout / continuation，SaR gate 能不能明显降低“gross 对、net 错”的交易？**
2. **对横截面 router，去掉 tail slippage 最差的那部分币后，组合 IR / PnL-to-turnover 会不会更好？**

### 9.3 如果第一轮有效，再往完整版推进
若 MVP 有效，再追加：
- provider concentration proxy
- `N_eff` / `CR1` 替代指标
- 组合层 `TSaR$` 风险降档规则
- 事件驱动时的动态杠杆上限

---

## 10. 一句话结论
**这篇东西不是给我们再造一条方向 alpha，而是给现有短周期 alpha 加一层“别在最脆的时候硬上”的 execution/risk governor；如果第一轮最小实验能证明它能稳定过滤掉 net 不划算的单子，它的实用价值会非常高。**
