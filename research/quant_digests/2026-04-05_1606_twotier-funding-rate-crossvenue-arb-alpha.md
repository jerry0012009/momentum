# 别把 funding spread 只当“看起来很肥的 carry”：这篇 2026 开放获取论文更值得先测的是「CEX lead × duration gate × cross-venue funding arbitrage」这条 raw alpha

- 时间：2026-04-05 16:06 UTC
- 类型：2026 *Mathematics* 开放获取全文（MDPI PDF）+ Crossref 元数据
- 主题类型：raw alpha
- 基础 alpha：**同一标的在不同永续合约交易所之间会出现可持续数分钟到数天的 funding rate 错位；做法是 long 低 funding venue、short 高 funding venue，赚 funding spread，本质上是 cross-venue / relative-value / carry arbitrage。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/relative-value/stat-arb/cross-venue/perp/perpetuals/cex-dex/1m/5m/15m/public-api/open-data/cost/reversal-risk/portfolio-construction
- 证据类型：开放获取全文里给出数据来源、归一化方法、阈值、portfolio simulation、forced-exit 规则、成本假设与 1m/5m/15m 鲁棒性检验；足够做最小复现

## 1. 先回答一句：base alpha 是什么？

**base alpha = cross-venue funding carry。**

翻成人话：

- 同一个币，在 A 交易所做多永续可能收钱，在 B 交易所做空永续可能付得更少，甚至反过来；
- 如果两边 funding rate 差得够大，理论上可以两边对冲价格风险，只赚 funding 差；
- 真正的挑战不是“有没有 spread”，而是：
  - 这个 spread 能不能撑得够久；
  - 进出场成本能不能覆盖；
  - funding 顺序会不会突然反过来，把 carry 变成反向亏损。

所以这不是一篇“市场结构综述”。它讨论的是一条能直接落地的 **carry / relative-value raw alpha**。

## 2. 为什么这轮值得写它？

如果先问一句：**它为什么比继续补 generic filter 更值得？**

答案很直接：

1. **它本身就是完整策略，不是附属 gate。**
   论文里有明确的：
   - entry threshold
   - exchange pairing
   - 持仓逻辑
   - forced exit
   - transaction cost
   - 风险调整后结果
2. **它天然适配我们的时间尺度。**
   论文主数据就是 **1 分钟 funding observations**，而且专门做了 **5m / 15m** 鲁棒性检验；这比那种只能硬从日频往下压的材料更像 short-cycle 研发素材。
3. **它补的是 raw alpha 素材池，不是解释性枝叶。**
   方向属于当前优先级较高的 `carry / funding / basis / relative value / stat-arb`。
4. **它把“看上去很大的 spread”为何赚不到，讲得很具体。**
   这对 desk 很重要，因为很多 funding 套利材料只会告诉你“有 200%+ APY”，却不告诉你：
   **round-trip 成本 + reversal risk 很可能把这条纸面 edge 吃光。**

## 3. 来源与论文信息

- **Author**：Petar Zhivkov
- **Year**：2026
- **Title**：*The Two-Tiered Structure of Cryptocurrency Funding Rate Markets*
- **Venue**：*Mathematics*
- **DOI**：`10.3390/math14020346`
- **Readable URL**：<https://www.mdpi.com/2227-7390/14/2/346>
- **PDF URL**：<https://www.mdpi.com/2227-7390/14/2/346/pdf?download=1>
- **DOI URL**：<https://doi.org/10.3390/math14020346>
- **Repo URL**：未见官方仓库

## 4. 这篇 paper 到底做了什么？

## 4.1 数据不是拍脑袋：26 家交易所、1 分钟频率、749 个 symbol

论文构建的数据集非常 desk-friendly：

- **26 家交易所**
  - 11 家 CEX
  - 15 家 DEX
- **749 个 symbol**
- **35.7 million 条 1 分钟 observations**
- 时间区间：**2025-11-08 ~ 2025-11-15**（连续 8 天）
- 只保留 **至少在 2 家交易所同时可交易** 的 symbol

这意味着所需数据并不神秘：

- 数据源：交易所 API
- 更新频率：分钟级
- 类型：funding rate、funding interval、Open Interest rank、timestamp
- 公开性：公开可抓

对我们来说，这比“需要买昂贵数据库”的主题更容易进最小实验。

## 4.2 论文先做了一件很重要的小事：把不同交易所 funding 周期统一到 8h 口径

因为不同交易所 funding 结算周期不同：

- 1h
- 4h
- 8h

如果直接拿原始 funding 数字横比，会出错。

论文先把所有 funding rate **线性归一化到 8 小时等价口径**：

- 1h funding × 8
- 4h funding × 2
- 8h funding × 1

然后才比较 venue 之间的 funding spread。

这个细节很关键，因为 desk 真要做这条策略，**第一步就不能把不同周期 funding 混着比**。

## 4.3 他们定义的 raw alpha 很直白：赚 funding spread，不赌方向

论文定义的 spread：

```text
Spread(s,t) = 同一 symbol 在所有 venue 中的最高 funding - 最低 funding
```

然后做 **delta-neutral**：

- 在 **最低 funding** 的 venue 做多
- 在 **最高 funding** 的 venue 做空
- 两边名义仓位相同

也就是：

> 不赌币价方向，赌的是 funding 错位会在一段时间内持续存在。

这就是一条很标准的 **cross-venue carry / funding arb raw alpha**。

## 5. 论文里最值得记住的结果

## 5.1 spread 确实很多，但并不等于都能赚

先看纸面机会：

- 论文把 **`Spread >= 20 bps (8h equivalent)`** 定义为 economically significant opportunity
- 这个阈值大约对应 **219% annualized APY**
- 样本里有 **665,251 条** observation 达到这个门槛，占 **17.1%**
- 这些机会里：
  - **84% 是 CEX-DEX 配对**
  - **16% 是 CEX-CEX**
  - 几乎没有 DEX-DEX

这已经告诉我们两件事：

1. 真正的大错位主要出现在 **中心化 vs 去中心化** 之间；
2. funding spread 大量存在，不代表能直接印钱。

## 5.2 市场是“两层结构”：CEX 领涨领跌，DEX 跟着调

论文最核心的市场结构结论是：

- **CEX-CEX funding correlation 平均 0.246**
- **DEX-DEX 平均 0.153**
- CEX 的 integration 约比 DEX **高 61%**
- Granger causality 上，**所有显著信息流都是 CEX → DEX，反向 0 次**
- 这个方向性在 **1m / 5m / 15m** 下都还成立

翻成人话：

> funding 这件事不是各 venue 平等定价；多数时候是 **CEX 先动、DEX 后跟**。

这对实盘很重要，因为它直接给了我们一个不只是“看到 spread 就上”的改进方向：

- **优先做 CEX-DEX spread**
- 并把 **CEX 端 funding / 价差信号** 当成 leader
- DEX 端更多当 lagging leg / execution leg

## 5.3 不是所有超大 spread 都值钱；duration 比 headline APY 更重要

论文最实用的一句其实不是“最大 spread 2401 bps”，而是这句：

> 对 $10,000 每边的头寸，若 spread 只有 **20 bps**，那每分钟只赚大约 **$0.042**，要撑 **5263 分钟（约 3.7 天）** 才只够覆盖一轮约 **$220** 的 round-trip 成本。

这句话直接把很多 funding 套利幻觉打碎了。

也就是说：

- 20 bps 看起来很夸张；
- 但如果持续时间不够长，仍然不够吃掉手续费和滑点；
- 因此这条 alpha 的关键不是“只看 spread 大”，而是：
  **spread 大 × 维持够久 × 不要太快反转。**

## 5.4 论文 portfolio simulation 的结论很诚实：能赚，但没你想得那么稳

论文对 top 20 opportunities 做了 delta-neutral portfolio simulation：

- 每边头寸：**$10,000**
- 强制平仓：**spread < 0 bps** 就退出
- round-trip 成本：
  - 流动性好：约 **$60**
  - 多数 illiquid 机会：约 **$220**`

结果：

- **只有 8/20（40%）** 在扣掉成本后仍为正收益
- **19/20（95%）** 最终出现 funding spread reversal pattern
- **12/20** 真正触发了 `spread < 0` 的 forced exit
- 最佳个例 **AIA**：约 **2 天净赚 $1,432.78**
- 全部 20 个组合的 **平均净 P&L 只有 $22**
- 平均 **Sharpe = -7.40**
- 最好的 AIA，**Sharpe 也只有 -2.73**

这说明什么？

> funding cross-venue alpha 不是“看见 spread 就开”的送钱机；
> 它更像一条 **筛选条件极其重要** 的 relative-value strategy。

## 5.5 机会主要集中在 CEX-DEX，不代表 DEX 一定更好做

论文里最常见的显著机会来自 **CEX-DEX**，但不要误读成“只要去 DEX 就有钱捡”。

因为 CEX-DEX 的另一个含义是：

- 结算机制不同
- 流动性深度不同
- 费用结构不同
- 执行与撤退的 friction 不同
- spread reversal 也更常见

论文实际上在提醒：

> **跨 venue carry 的上限来自结构分层，下限来自执行摩擦。**

## 6. 对我们的 short-cycle desk，正确读法是什么？

## 6.1 这是一条合格的 raw alpha，但不能只拿“高 APY”做选题理由

它能进入素材池，不是因为论文报了夸张 APY，
而是因为它给出了一条 **可测试、可执行、可失败** 的完整策略壳：

- 数据公开
- 时间粒度够细
- raw alpha 明确
- entry / exit / cost / risk 明确
- 还能自然映射到 `1m / 5m / 15m`

## 6.2 这条 alpha 更适合做成“spread × duration × venue-type gate”

如果只抄论文 headline，很容易变成：

- `Spread >= 20bps` 就上
- `spread < 0` 才走

这太粗。

更适合我们 desk 的读法是：

### Raw alpha 本体

- 做 **同标的跨 venue funding differential**
- long 最低 funding venue
- short 最高 funding venue

### 三个核心 gate

1. **Venue-type gate**
   - 优先 `CEX-DEX`
   - 次选 `CEX-CEX`
   - 暂不碰 `DEX-DEX`

2. **Duration / persistence gate**
   - 不只看瞬时 spread
   - 要看最近 `30m / 60m / 120m` 持续性
   - 也要看最近的 sign flip 次数

3. **Leader-lagger gate**
   - 若 CEX funding 先动、DEX 还没跟，才更像可做错位
   - 若已经同步收敛，别被高 headline APY 诱惑

换句话说：

> 这篇最该学的，不是“spread 大就能赚”，而是 **把 funding arb 做成一个需要 regime / duration / venue hierarchy 共同确认的 raw alpha 壳。**

## 7. desk 版最小可复现实验

## 数据源、公开性、更新频率、口径

- **数据源**：Binance / Bybit / OKX / Hyperliquid / Drift 等公开 API
- **公开性**：公开可得
- **更新频率**：1m 抓取 funding snapshot；按 venue 原始 funding interval（1h/4h/8h）记录
- **最小可复现实验口径**：全部换算成 **8h equivalent bps**，并保留每分钟横截面的 max/min venue

## 实验 1：只验证 spread persistence，不先看 PnL

**目标：** 先看 funding spread 是不是确实能在 `1m / 5m / 15m` 上维持到足以 cover 成本。

- universe：BTC / ETH / SOL / BNB / XRP + 5 个 mid-cap perp
- venues：2~4 家 CEX + 2 家 DEX
- 采样：1m 原始、5m/15m 聚合
- 指标：
  - `spread_8h_bps`
  - 持续高于阈值的连续分钟数
  - sign flip 次数
  - 由正转负的 reversal rate

**验收标准：**
- 若 `spread >= 20bps` 的大多数事件在扣掉 realistic fee 前就撑不过预估 break-even duration，这条线要么降优先级，要么必须抬 entry threshold。

## 实验 2：做最简单的完整策略，对比不同 entry threshold

对比三组：

1. `spread >= 20bps`
2. `spread >= 40bps`
3. `spread >= 20bps 且 最近60m内无 sign flip`

统一规则：

- long 最低 funding venue
- short 最高 funding venue
- 名义对冲
- exit：
  - `spread <= 5bps`
  - 或 `spread < 0`
  - 或 max holding `24h`

看：

- net PnL / trade
- holding time
- win rate
- reversal before breakeven 比例
- max concurrent positions

## 实验 3：加入论文最有价值的 desk 改写 —— `CEX lead × DEX lag`

这一步才是我认为最值得测的“旁支想法”。

**目的：** 不只赚 spread，而是只做更像“DEX 还没来得及跟”的那批错位。

做法：

- 只保留 `CEX-DEX` pair
- 如果最近 `5m / 15m` 内 CEX funding / 相关价格代理先动，DEX funding 仍滞后，则入场
- 若 DEX 已同步，放弃

可直接比较：

- plain spread arb
- spread + persistence gate
- spread + persistence + CEX-lead gate

如果第三组能明显提升：

- `PnL/trade`
- breakeven hit rate
- reversal 前平掉的概率

那这篇就不只是“又一篇 funding 套利”，而是真的给 desk 补进了一个 **可复用的 entry redesign**。

## 8. 我对它的判断

我的判断是：**值得进 raw alpha 池，但优先做“小范围、重成本、重持续时间”的验证版，而不是一上来铺很多 venue。**

原因：

1. **alpha 本体清楚**：cross-venue funding carry
2. **执行壳清楚**：归一化 spread、对冲开仓、forced exit、成本核算
3. **短周期映射自然**：1m 原始数据，5m/15m 鲁棒性已被论文摸过
4. **最值钱的不是 headline spread，而是 venue hierarchy + persistence**
5. **失败也很快能证伪**：只要发现 duration 盖不住成本，或者 reversal 太快，这条线立刻降级

如果要一句话总结：

> 这篇 paper 不该被读成“funding spread 很大”，而该被读成：**在 CEX 主导、DEX 滞后的两层市场里，只有持续够久、反转够慢的 cross-venue funding 错位，才配叫 raw alpha。**

## 9. 这轮建议直接开工的参数表

第一轮我会直接这样测：

- 频率：`1m` 原始计算，`5m / 15m` 出信号
- 标的：BTC / ETH / SOL / BNB / XRP / DOGE / ADA / LINK
- venue：Binance / Bybit / OKX / Hyperliquid / Drift
- funding 口径：统一到 `8h equivalent bps`
- entry：
  - `spread >= 30bps`
  - 且最近 `60m` 内累计在阈值上方时间 `>= 40m`
  - 且最近 `30m` 内 sign flip = 0
  - 且优先 `CEX-DEX`
- exit：
  - `spread <= 5bps`
  - 或 `spread < 0`
  - 或 max holding `12h / 24h`
- sizing：按 venue 可成交名义和手续费等级限仓
- 成本：双边 taker + 预估滑点 + 提现/链上成本（若需要真实跨 venue 调仓）

然后只回答 3 个问题：

1. `spread × duration` 能不能稳定 cover 成本？
2. `CEX lead` 能不能提高净胜率？
3. 哪个阈值区间（20 / 30 / 40bps）开始真正像 raw alpha，而不是噪声幻觉？

## 10. 来源链接

### Primary paper
- Zhivkov, P. (2026). *The Two-Tiered Structure of Cryptocurrency Funding Rate Markets*. *Mathematics*.
- DOI: <https://doi.org/10.3390/math14020346>
- Readable: <https://www.mdpi.com/2227-7390/14/2/346>
- PDF: <https://www.mdpi.com/2227-7390/14/2/346/pdf?download=1>

### Metadata
- Crossref record: <https://api.crossref.org/works/10.3390/math14020346>
