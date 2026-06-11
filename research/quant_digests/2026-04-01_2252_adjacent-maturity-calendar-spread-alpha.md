# 别把这份 2026 calendar-spread repo 只读成“慢频 carry 备忘”：对 short-cycle desk，更该先测的是「adjacent-maturity ratio dislocation × carry normalization」这条 futures curve raw alpha
- 时间：2026-04-01 22:52 UTC
- 类型：2026 GitHub repo source audit（`README.md` + repo 内 `Crypto_Carry_and_Term-Structure_Arbitrage.pdf`）
- 主题类型：raw alpha
- 基础 alpha：相邻到期合约的 calendar spread 在“绝对 spread 看起来差不多、但按剩余天数归一后明显不一致”时，做期限结构相对价值回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/carry/term-structure/calendar-spread/adjacent-maturity/futures-curve/btc/eth/cme/binance-delivery/okx-futures/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：工程经验 / repo 自带研究总结

## 1. 这次看了什么
看的是 GitHub 仓库 **mikehyland-quant/cme-crypto-calendar-spreads**。它不是在讲常见的 spot-perp basis，而是在讲 **相邻到期 futures 之间的相对 carry 错价**：作者用 BTC / ETH futures 的月历差（calendar spread）做 term-structure relative value，认为市场经常把不同剩余期限的 spread 用“差不多的绝对美元值”去报价，忽略了时间价值应按天数缩放。

repo README 给出的核心设定很清楚：
- 研究对象：作者声称为 **2024–2025** 期间实际部署的 BTC / ETH futures calendar-spread 套利；
- 关键期限结构：月度 crypto futures 常出现 **28 天** 和 **35 天** 两种相邻期限差；
- 理论关系：`35 / 28 ≈ 1.25`，也就是 **35d spread 理论上应比 28d spread 多约 25% carry**；
- 当市场把这两类 spread 报得几乎一样时，就出现 relative-value 错价。

## 2. 核心结论
- 这份材料真正值得 intake 的，不是“crypto 长期有 contango”这个老结论，而是更可交易的一层：**adjacent-maturity spread ratio 的均值回归**。
- 作者给出的 trade shell 很完整：当 `35d spread / 28d spread` 明显偏离理论比值时，做 **long 4 × 35d spreads / short 5 × 28d spreads**，用 `4:5` 比例去大致匹配时间暴露。
- 入场条件不是主观判断，而是三段式：
  1. **equal absolute spread pricing**（两个 spread 的绝对价格过于接近）；
  2. **2–3σ deviation from theoretical ratio**；
  3. **implied carry divergence**。
- 出场条件也比较像完整策略，而不是一句“等它回归”：
  - 回到理论 band；
  - carry 归一；
  - time decay 吃到后兑现；
  - 临近到期前 roll / 强制管理。
- repo 给了 3 个很有价值的硬数字：
  - **35/28 ≈ 1.25** 是整个策略的理论锚；
  - **Full 15 Months：CAGR 8%，Sharpe 1.4，Max DD -6.5%**；
  - **Last 6 Months：CAGR 18%，Sharpe 4.0，Max DD -0.7%**。

## 3. 为什么和当前项目有关
最近 intake 里已经有不少：
- spot-perp carry / funding；
- pairs / cointegration / OU fade；
- cross-sectional momentum / reversal；
- microstructure directional alpha。

但 **“期限结构内部的 relative-value carry”** 还很少被单独当成一条 raw alpha 卡来写。

它值得现在补进素材池，原因有 3 个：
1. **base alpha 很清楚**：不是 filter，也不是 macro 解读，而是“不同期限的 spread 没按时间定价”这一类 raw alpha；
2. **方向风险更干净**：比 spot-perp carry 更接近 curve relative value，理论上比单边 carry 更低 beta；
3. **能接到 short-cycle execution**：虽然信号持有期偏天级 / 周级，但 entry / exit / 风控完全可以下沉到 `15m/5m`，用来做更精细的入场和滑点控制。

如果要回答“为什么它比继续补 another pairs 变体更值得”：因为当前池子里 pairs / funding 已经不少，但 **calendar-spread / futures-curve raw alpha 仍是相对空白的一栏**。

## 3.5 策略拆解（必填）
- 方向属性：relative value / stat-arb / carry / market-neutral-ish
- 基础 alpha：相邻期限 futures spread 的 **days-to-expiry 归一关系失真**；短天期和长天期的 spread 没按 `时间比` 定价
- regime：默认只在 contango 常态或至少非极端 backwardation 期启用；遇到全曲线反转先降权或停机
- filter / veto：
  - 只交易流动性最好的相邻期限；
  - 要求 ratio 偏离达到 `2–3σ`；
  - 期限剩余天数过短（临近交割）时禁新开；
  - 若 funding / borrow / 交易费把 carry gap 吃掉，则 veto
- risk / sizing / execution overlay：
  - 用 `4 × 35d vs 5 × 28d` 这类 time-matched ratio 做基础 sizing；
  - 单腿 notional / spread DV01 / expiry bucket cap；
  - pre-expiry roll cutoff；
  - `5m/15m` 子 bar 分批进出，避免一把吃穿盘口

## 4. 可复刻的最小实验
### 4.1 先回答：怎么把它映射到我们 desk
这条 alpha 不是典型 `1m` 主信号，但完全可以服务短周期 desk：
- **信号层**：看 futures curve relative value；
- **执行层**：用 `15m/5m` 监控 ratio 偏离、盘口厚度、滑点和 exit band；
- **风险层**：用子 bar 细分分批成交和 pre-expiry unwind。

也就是说，**alpha 本体偏慢，但执行与风控完全可以 short-cycle 化**。

### 4.2 数据源、公开性、更新频率、最小口径
repo 本身像是 CME-style 月度合约研究，但对我们做最小实验，不必卡死在 CME 数据：
- **优先公开数据源**：Binance Delivery / COIN-M quarterly、OKX Futures、Bybit dated futures（若有相邻可交易期限）
- **公开性**：交易所公开 market data 可获取
- **更新频率**：book / ticker 通常秒级，kline 可直接取 `1m`
- **最小实验口径**：
  1. 找同一标的的最近两个有流动性的 dated futures；
  2. 每 `5m/15m` 计算各 calendar spread 的年化 carry 或 days-normalized spread；
  3. 对 ratio 做 rolling z-score；
  4. 偏离大时开 `long rich-cheap normalized leg / short overrich normalized leg`；
  5. 回到理论 band、接近 expiry cut-off、或 carry 正常化时平。

### 4.3 最小可跑规则
- Universe：先只做 BTC / ETH
- Sampling：先用 `5m`；太脏再退到 `15m`
- Signal：
  - `spread_i = futures_i - futures_{i-1}` 或直接对相邻合约价差做天数归一；
  - `ratio = normalized_longer_gap / normalized_shorter_gap`
- Entry：
  - `ratio_z <= -2` 或 `>= +2`；
  - 同时要求理论 carry gap 扣完 fee 仍为正；
  - 盘口深度满足最小 notional
- Exit：
  - `|ratio_z| < 0.5`；
  - 或达到固定 carry capture；
  - 或距离近腿到期不足 N 天强平
- Cost：
  - maker/taker 两套；
  - 至少做 `5/10/15/20 bps` friction ladder；
  - 必须单独记 legging risk 与 roll cost

## 5. 先测什么，不先测什么
### 先测
1. **days-normalized spread ratio 是否真有稳定回归**；
2. 在 Binance / OKX dated futures 上，这种偏离是否经常出现；
3. costs 后是否还剩可观 annualized carry；
4. `5m` vs `15m` 监控谁更稳。

### 不先测
- 不先上复杂曲线拟合；
- 不先优化一堆期限组合；
- 不先把它和 spot inventory / Korean listing premium 混成一锅；
- 不先把 repo 的 15 个月结果直接当可复制事实。

第一关应该只回答一句：**在公开可拿的 dated futures 上，期限归一后的 spread ratio 错价有没有稳定回归，且 fee 后还有没有肉。**

## 6. 风险与误区
- 这类 alpha 的最大风险不是方向，而是 **曲线 regime 突变**：从稳定 contango 切到 backwardation 后，理论比值本身可能需要重估。
- 看起来 market-neutral，但仍有：
  - legging risk；
  - expiry roll risk；
  - 流动性分层；
  - 交易所合约规格差异。
- repo 里的绩效更像作者总结，不是标准论文回测披露；**不能把 `Sharpe 4.0` 直接当成外推预期**。
- 若我们最后只能在极少数到期窗口里看到信号，那它更像 **容量受限但高质量的 niche raw alpha**，不是 24/7 主引擎。

## 7. 下一步怎么测
我会按下面顺序推进 first verdict：
1. **先做数据可得性检查**：确认 Binance / OKX 当前能否稳定拿到相邻 dated futures 的 `1m` kline / ticker / book；
2. **构造最小 ratio 面板**：对 BTC / ETH，生成 `normalized spread ratio` 的 `5m/15m` 时序；
3. **先只做无方向 beta 的 band-reversion**：`z=2/2.5/3` 三档入场，`z=0.5/1.0` 两档出场；
4. **补 friction ladder**：maker / taker、单边 5/10/15/20 bps、再加一次 roll slippage 假设；
5. **看是否值得进入 clean replication**：
   - 若 trade count 太少或 cost 后死掉 → park；
   - 若 ratio 回归清楚但容量小 → 留作 niche carry bucket；
   - 若 `15m` 下也稳 → 再考虑扩到多期限 / 多 venue。

## 8. 来源与复现线索
- Mike Hyland (GitHub, 2026), *Crypto Carry and Term-Structure Arbitrage*（repo 标题与 README）
- Repo URL：<https://github.com/mikehyland-quant/cme-crypto-calendar-spreads>
- Readable URL：<https://github.com/mikehyland-quant/cme-crypto-calendar-spreads>
- Full PDF（repo 内研究稿）：<https://github.com/mikehyland-quant/cme-crypto-calendar-spreads/blob/main/Crypto_Carry_and_Term-Structure_Arbitrage.pdf>
- 主要可见字段：
  - sample 口径：README 写明 **live calendar-spread arbitrage strategy deployed across BTC and ETH futures during 2024–2025**
  - strategy shell：**Long 4 × 35-day spreads / Short 5 × 28-day spreads**
  - entry shell：**equal absolute spread pricing + 2–3σ deviation + implied carry divergence**
  - performance snapshot：**Full 15 Months CAGR 8%, Sharpe 1.4, Max DD -6.5%; Last 6 Months CAGR 18%, Sharpe 4.0, Max DD -0.7%**
- DOI / Venue：**未见正式期刊 DOI；当前更应把它视为 repo research paper / engineering note，而不是已发表论文**

## 9. 一句话带走
如果要把这份材料变成 desk 能跑的实验，我会把它定义成：**“不要再只盯 spot-perp；去测 futures curve 内部、按剩余天数归一后会不会出现可持续回归的 calendar-spread 错价。”**
