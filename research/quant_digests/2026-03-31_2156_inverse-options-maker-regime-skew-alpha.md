# 别把这份 2026 options 新仓库只读成通用撮合骨架：对 desk 更该先测的是「inverse options maker spread-capture × regime widen × inventory skew」这条可直接落地的 raw alpha

- 时间：2026-03-31 21:56 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/options/market-making/spread-capture/inventory-skew/regime/circuit-breaker/delta-neutral/deribit/btc/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：2026 GitHub 新仓库 `README.md` + `strategies/market_making/hawkes_mm.py` + `strategies/market_making/integrated_strategy.py` + `research/risk/circuit_breaker.py` source audit + 经典做市论文地基 + Deribit BTC options 公开 live snapshot

- 主题类型：raw alpha
- 基础 alpha：**双边挂单赚 bid-ask spread**，再用 `inventory skew + regime widening + circuit breaker` 尽量把 adverse selection 和库存爆仓压住
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主材料不是论文 headline，而是一份更新很新的 GitHub repo：**signorloops (2026), _crypto-options-research-platform_**。

如果只把它读成“又一个 options 研究工程脚手架”，那价值一般；但如果按当前 desk 的口径去拆，它其实给了一条我们最近素材池里还不算多的 **完整 raw alpha**：

> **不是去赌 BTC 下一根涨跌，而是在 BTC 期权簿里做两边报价，赚 spread；方向性风险不靠押方向赚钱，而靠库存倾斜、波动分档、熔断/降杠杆来控制。**

这条线对 `1m / 3m / 5m / 15m` 很友好，因为它天然就是高频/短周期逻辑：
- 信号更新是逐笔/逐秒的；
- 但最小实验完全可以先压成 `1m` 特征栏 + `5m/15m` 风险汇总；
- 而且它不是“只有入场没有出场”的概念卡，仓库把 `quote / skew / regime / circuit breaker / hedge` 都写出来了。

## 2. 核心结论
### 2.1 先说结论
这篇东西的 **base alpha 很清楚**：

**base alpha = 期权簿上持续存在的双边价差本身。**

也就是说，这不是 filter，不是 overlay，也不是“预测信号外面再包一层风控”；
它本体就是：
1. 在还算健康的 order book 上双边挂价；
2. 尽量拿到 maker spread；
3. 用库存/波动/风控状态决定你要不要继续报、报多宽、向哪边歪。

### 2.2 仓库里真正有价值的，不是“会报单”，而是它把完整策略骨架写出来了
从源码看，这份 repo 至少把下面这些关键信号/参数冻结成了可执行状态：

- `IntegratedStrategyConfig.base_spread_bps = 20.0`
- `inventory_limit = 10.0`
- `gamma = 0.1`
- `max_skew_bps = 50.0`
- `regime_spread_multipliers = {LOW: 0.8, MEDIUM: 1.0, HIGH: 1.5}`
- circuit breaker 的 spread multiplier：`NORMAL 1.0 / WARNING 1.5 / RESTRICTED 2.0 / HALTED 不报价`
- circuit breaker 的仓位缩放：`NORMAL 1.0 / WARNING 0.5 / RESTRICTED 0.1`
- 风险阈值默认值：`daily loss warning 5% / daily loss halt 10% / drawdown warning 8% / max drawdown 15% / cooldown 300s`

翻成人话：
这不是“教你用某个指标判断波动高低”的说明文，
而是一份已经把 **entry / exit / sizing / risk / cost 假设** 拼得比较完整的 market-making 策略骨架。

### 2.3 当前公开 BTC options 盘口，确实给了 maker edge 的土壤，但也暴露出 repo 默认参数偏乐观
我拿 Deribit 公开 API 做了一个很小的 live snapshot（BTC options）：

- **857** 个合约有双边报价
- 在 `mid >= 0.001 BTC premium` 的筛选后，仍有 **788** 个双边合约
- 这些合约的 **quoted spread / option mid**：
  - 中位数约 **384.1 bps**
  - `p75 ≈ 988.6 bps`
  - `p90 ≈ 1557.5 bps`
- 若只看按 `OI + volume` 排前的 **top-30** 较液态合约：
  - spread 中位数仍有 **312.9 bps（相对 option premium）**
  - 绝对 spread 中位数约 **68.4 USD premium**

这说明两件事：
1. **maker spread capture 不是空想**——盘面上确实有肉；
2. 但 repo 默认的 `20 bps` base spread 更像**研究/回测起点**，离真实 live 盘口还有距离。

对 desk 来说，最值得偷的不是“20bps 这个数”，而是：

> **先把 empirical spread floor 接上，再测试 inventory skew / regime widen / circuit breaker 这三层是否真能保住 spread capture。**

## 3. 为什么和当前项目有关
这轮任务默认优先补 **可独立复现且能直接落地成完整策略的 raw alpha**。这条线值得进池，原因很直接：

1. **它是完整 raw alpha，不是辅助层。**
   edge 就来自 order book spread capture，本体清楚。
2. **它补的是当前池子里相对少的一类短周期素材。**
   我们最近 raw alpha 很多是 `basis / funding / pairs / XS / lead-lag`；
   但 **options maker 型 raw alpha** 还不算多。
3. **它天然适配 1m/3m/5m。**
   因为 quoting / cancel / hedge 本来就比 15m 更快。
4. **它可以独立落完整策略。**
   不是只给一个 signal，再让我们自己脑补仓位/风控；源码已经把这些部件写出来了。

所以这轮不继续补一篇 generic filter，而改补这条 raw alpha，是合逻辑的：
它直接扩的是 **可部署的短周期素材池**。

## 3.5 策略拆解（必填）
- 方向属性：BTC options 双边做市 / spread capture / 尽量 delta-neutral
- 基础 alpha：`quoted_spread_capture`
- regime：`volatility_state + trade_intensity/Hawkes intensity + circuit_breaker_state`
- filter / veto：只在双边足够深、mid premium 不太小、近端活跃合约中报价；高波动毒流/熔断状态下停报或只报一侧
- risk / sizing / execution overlay：库存倾斜、delta hedge、OI/depth 限额、warning/restricted 状态缩仓与加宽 spread

## 4. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = option book 的 bid-ask spread 本身，而不是“预测 BTC 下一根方向”。**

换句话说：
- `inventory skew` 不是 alpha 本体；
- `regime widening` 不是 alpha 本体；
- `circuit breaker` 也不是 alpha 本体；

它们都是为了让 **spread capture 这条 raw alpha** 在真实盘里少死一点。

## 5. 对 desk 更有价值的重读方式
这份 repo 最值得我们 intake 的，不是“它也用了 Hawkes / Avellaneda-Stoikov 术语”，而是下面这条 **更适合 desk 的旁支想法**：

### **先把 empirical spread floor 接到 options maker shell 上**
也就是：
- alpha 本体仍是 maker spread capture；
- 但别直接照抄 repo 的默认 `20bps`；
- 先用公开盘口统计 `不同期限 / 不同 delta / 不同活跃度` 的真实 spread floor；
- 再让 `inventory skew + regime + CB` 去决定在这个 floor 之上加多少。

这比直接讨论“repo 里的 Hawkes 模块是不是最优”更值钱，
因为它能更快做成 `1m / 3m / 5m` 最小实验。

## 6. 怎么把它落成完整策略
### 6.1 第一版最小 desk 读法
- 标的：Deribit BTC options，先只做 **短中端到期（例如 7~35 DTE）** 的活跃合约
- 合约筛选：
  - `mid premium >= 0.001 BTC`
  - 双边报价都存在
  - OI / volume 排名前若干
- 报价中枢：option mid 或 microprice
- 报价宽度：
  - `max(empirical_spread_floor, base_spread × regime_mult × CB_mult)`
- skew：
  - 用库存 + 近端 realized vol + trade intensity 推 reservation price
- 对冲：
  - 用 BTC perp/spot 做 delta hedge
- 停报条件：
  - risk state = `HALTED`
  - 或 depth 突然塌掉 / spread 异常跳宽 / burst intensity 过高

### 6.2 这条线真正的 entry / exit 是什么
这类策略别用传统 directional 视角读：

- **Entry**：开始双边报价，或恢复报价
- **Exit**：停报 / 缩单 / 单边撤单 / 强制对冲 / 平库存

也就是说，完整策略不是“某价位做多某价位止盈”，而是：
- 什么时候可以报；
- 报多宽；
- 报多大；
- 偏买还是偏卖；
- 什么时候别再挣 spread，先保命。

## 7. 下一步怎么测
最小可执行实验，我建议直接做下面这版：

1. **数据**：拉 Deribit BTC options 公开 order book / trades / summary，先做 `1m` 特征栏；风险与净值按 `5m`、`15m` 汇总。
2. **Universe**：先限制在 `7~35 DTE`、`mid>=0.001 BTC`、`OI/成交额 top bucket` 的合约池。
3. **对照组**：
   - A：对称固定 spread 做市
   - B：`inventory skew only`
   - C：`inventory skew + regime widening`
   - D：`inventory skew + regime + circuit breaker`
4. **spread floor**：先用 rolling 盘口统计做 `p25 / p50 / p75` 三档 empirical floor，而不是直接信 `20bps`。
5. **hedge 规则**：
   - 每 `1m` 检查一次净 delta
   - 或当 `|net_delta|` 超阈值立即 hedge
   - hedge 标的先用 BTC perp
6. **成本口径**：
   - maker fill capture 先做 `25% / 50% / 75%` 三档
   - hedge taker cost 做 `1 / 2 / 4 bps` 三档
   - 再加 stale-quote cancel latency：`1s / 3s / 5s`
7. **风险约束**：
   - 直接沿用 repo 的 CB 初值：`5% warning / 10% daily halt / 8% DD warning / 15% max DD / 300s cooldown`
8. **核心指标**：
   - delta-hedged PnL
   - spread capture / hedge cost 比值
   - inventory half-life
   - adverse-selection loss
   - warning/restricted/halt 触发率
9. **先判生死，不急着精修**：
   - 如果 `C/D` 连固定 spread 基线都赢不了，就别急着做更复杂 Hawkes；
   - 如果 `D` 明显减小左尾，再考虑往 `3m/1m` 下钻。

## 8. 风险与局限
- **spread 宽不等于真能成交。** 报价有肉，不代表 fill quality 好。  
- **option premium bps 很容易看着夸张。** 所以邮件和评估里要明确“这是相对 option premium 的 spread，不是相对 underlying 的 bps”。  
- **公开 REST snapshot 只能做 very small sanity check。** 真正 backtest 还是要更细的 quote/trade 数据。  
- **inverse/coin-margined 计价和 Greeks 风险** 比现货/perp 更容易把 PnL 直觉搞歪。  
- **repo 默认参数更像研究起点**，不是 production-ready 配置。

## 9. 这次最值得记住的一句话
**别把 options 做市理解成“预测方向后顺便挂单”；它本体就是 spread capture，方向判断只是拿来少吃毒流、少积坏库存。**

## 10. 来源
1. **signorloops (2026). _crypto-options-research-platform_. GitHub repository.**  
   Venue：GitHub  
   DOI：无  
   Readable URL / Repo URL：https://github.com/signorloops/crypto-options-research-platform
2. **Avellaneda, M., & Stoikov, S. (2008). _High-frequency trading in a limit order book_. Quantitative Finance, 8(3), 217–224.**  
   DOI：`10.1080/14697680701381228`  
   Readable URL：https://www.tandfonline.com/doi/abs/10.1080/14697680701381228
3. **Deribit API docs — public market data / book summary.**  
   Readable URL：https://docs.deribit.com/
4. 本地 artifacts：
   - `reports/artifacts/quant_digests/deribit_btc_option_spread_snapshot_20260331.csv`
