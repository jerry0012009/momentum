# 别把这两份 2026 prediction-market repo 只读成链上博彩脚本：对 short-cycle desk，更该先测的是「late-lock pool imbalance × payout-aware EV switch」这条完整 raw alpha

- 时间：2026-04-04 14:55 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` / `src/index.ts` / `src/lib.ts` / `src/strategy.ts` / `src/config.ts`）+ PancakeSwap Prediction 官方 docs
- 主题类型：raw alpha
- 基础 alpha：**在公开可见的 `5m` prediction round 里，用 bull/bear 池子金额推导赔率，再用超短线方向估计（recent rounds momentum / streak reversal / 外部现货微动量）计算每一侧的净期望值，只在 `EV > fee + gas + safety margin` 时于 lock 前最后十几秒下注。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/prediction-market/binary/late-lock/pool-imbalance/payout-skew/expected-value/momentum/streak-reversal/contrarian/crowding/bsc/pancakeswap/bnb/btc/eth/5m/repo/docs/public-data/cost/risk
- 证据类型：repo 源码证据 + 官方机制文档

## 1. 先回答一句：base alpha 是什么？

**base alpha = 公开池子不平衡（crowding / implied odds）和超短线方向概率之间的错配。**

更直白一点：
- 市场已经把 `bullAmount / bearAmount` 摆在链上；
- 这等于给了你一个**实时赔率**；
- 如果你能用最近几轮结果、streak、或者外部现货 `1m/3m` 微动量，估出一边真实胜率高于赔率隐含门槛，下注本身就是一条可独立运行的 raw alpha。

它不是 filter，也不是 overlay；**它本身就是带固定出场时钟的完整交易。**

## 2. 为什么这轮值得进研究池？

这不是又一篇“breakout / pairs / funding 老题材”的边角料，而是一条**还没在当前 digest 池里重复出现的完整短周期 alpha 家族**：
- **交易对象**：PancakeSwap Prediction 的 `BNB/BTC/ETH` `5m` round；
- **数据公开**：池子金额、round 状态、lock/close 规则都公开；
- **出场天然固定**：到期结算，不存在“什么时候平仓”模糊地带；
- **最小实验快**：抓取 round 数据就能回放，远比许多链上高频题材容易起步。

如果现在继续补一篇普通 pairs / maker / time-of-day 题材，边际新增信息未必比这条更高。

## 3. 两份 repo 各自提供了什么可复用部件？

### 3.1 `mooncitydev/crypto-prediction-bot`：给你 **赔率侧 / crowding 侧**

这份 repo 的核心不是“自动下注脚本”本身，而是三件事：

1. **下注时点非常晚**  
   `src/index.ts` 里把等待时间写成 `281500 ms`，也就是一轮 `300s` 的 `5m` round 里，大约在 **lock 前 18.5 秒** 才做决策。

2. **直接读取 bull / bear 池子金额**  
   然后在最后十几秒，用 `bullAmount` 和 `bearAmount` 判断 crowding。

3. **明确把 crowding 写成规则**  
   repo 提供了 `Against` 与 `With` 两种风格：
   - `Against`：逆着 crowding 做；
   - `With`：顺着 crowding 做；
   - `src/lib.ts` 里还用了一个**5:1 ratio 门槛**作为 regime 切换线索。

也就是说，这份 repo 最值钱的不是“脚本会发交易”，而是它把 **late-lock crowding / payout skew** 变成了可执行壳。

### 3.2 `madewithai/pancakeswap-prediction-bot`：给你 **方向概率估计侧**

这份 repo 更像一个简化版短线概率模型：
- `LOOKBACK_ROUNDS=20`
- 最近 round 权重衰减 `0.95`
- `MIN_EDGE_SCORE=0.58`
- `STREAK_REVERSAL_THRESHOLD=3`
- 可加 `COOLDOWN_ROUNDS_AFTER_LOSS`
- `MAX_BET_BNB` 控制单轮暴露

它提供的关键信息是：
- 可以把最近 `N` 轮 bull/bear outcome 压成一个**超短线方向概率**；
- 当出现连续 `3` 轮以上单边 streak 时，可以切到**streak reversal** 模式；
- 风险层至少有 cap / cooldown 这种最小壳。

这正好补上前一个 repo 缺的那半边：**不是只看赔率，而是要估概率。**

## 4. 真正适合 desk 的读法：不是“跟 crowd / 反 crowd”二选一，而是 **赔率感知后的 EV switch**

这是这轮最值得拿走的 reframing。

### 4.1 先把赔率写清楚

PancakeSwap 官方 docs 给了 3 个关键机制：
- 每轮 **`5 分钟`**；
- 平台 fee **`3%`**；
- 结算看 **Chainlink lock/close price**，且文档写明更新间隔**最高可到约 20 秒**。

如果当前轮：
- bull 池 = `B`
- bear 池 = `R`
- total = `T = B + R`

那么下注某一侧的**赢时总回收倍数**，近似就是：
- `gross_mult_bull = 0.97 * T / B`
- `gross_mult_bear = 0.97 * T / R`

于是 break-even 胜率门槛就是：
- `p*_bull = 1 / gross_mult_bull`
- `p*_bear = 1 / gross_mult_bear`

### 4.2 这几个数字非常关键

假设当前 crowding 是 `4:1`：
- 若你买 **少数一侧**，赢时回收约 `0.97 * 5 = 4.85x`，break-even 胜率只需 **`20.6%`**；
- 若你买 **多数一侧**，赢时回收约 `0.97 * 1.25 = 1.2125x`，break-even 胜率却要 **`82.5%`**。

若 crowding 到 `5:1`：
- 少数侧 break-even 胜率约 **`17.2%`**；
- 多数侧 break-even 胜率约 **`85.9%`**。

这说明什么？

**Prediction market 不该只问“谁更可能赢”，而要问“谁的赔率错得更厉害”。**

所以最适合 desk 的版本不是：
- 永远顺 crowd；或
- 永远反 crowd；

而是：

> **先看 payout skew，再决定这轮该做 majority continuation、minority fade，还是直接 skip。**

## 5. 能不能直接落地成完整策略？可以。

### 5.1 Entry（入场）

**推荐 desk 版最小规则：**

1. round 进入最后 `15~20s`；
2. 抓当前 `bullAmount / bearAmount`；
3. 用最近 `20` 轮结果（或外部 `1m/3m` 现货微动量）估 `p_bull / p_bear`；
4. 分别计算：
   - `EV_bull = p_bull * 0.97 * T / B - 1`
   - `EV_bear = p_bear * 0.97 * T / R - 1`
5. 只有当 `max(EV_bull, EV_bear) > gas + tie_buffer + safety_margin` 时才下注；
6. 若两边都不够，直接 skip。

### 5.2 Exit（出场）

- **固定到期结算**，没有 discretionary exit；
- 这反而是优点：研究上更干净。

### 5.3 Sizing（仓位）

先别搞复杂 Kelly，直接用：
- 固定 stake；
- 或 `stake = min(max_cap, base_size * clipped_EV)`；
- 单轮 cap 建议先照 repo 的保守口径，控制在小额 `BNB` 暴露。

### 5.4 Risk（风控）

最小必备：
- `max bet per round`
- `cooldown after loss`
- lock window 禁入
- pending oracle / round 状态异常禁入
- 连续 `N` 轮亏损暂停
- 明确禁止在网络拥堵导致 tx 容易迟到时追单

### 5.5 Cost（成本）

至少要扣：
- 平台 **3% fee**
- BSC gas
- tie 风险（文档写明 **tie 时 house 赢**）
- oracle / transaction timing 风险

## 6. 对 `1m / 3m / 5m / 15m` desk 的关系

这条 alpha 的**主战场就是 `5m`**，不是硬往 perp 上伪装迁移。

更合理的映射是：

### 6.1 直接交易层
- 直接做 PancakeSwap Prediction `5m` round；
- BTC / ETH / BNB 都能独立实验；
- 这是最干净的主实验。

### 6.2 衍生 confirm / veto 层
如果未来要服务 perp desk，可以把它变成：
- `5m round` 最后十几秒的 pool imbalance / implied odds，作为 BTC/ETH/BNB perp 的一个 crowding confirm；
- 但这属于**二级用途**，不是本轮主结论。

换句话说：**这轮主题本身就是 raw alpha，不需要靠“服务别的 alpha”来证明价值。**

## 7. 这两份 repo 的保留意见

### 7.1 `mooncitydev` repo 的规则实现有明显逻辑粗糙处
`src/lib.ts` 里的 `isAgainstBet` / `isWithBet` 写法并不优雅，存在“ratio 条件和下注方向混在一起”的问题，不能原样当成 desk 级信号逻辑。

但这不影响它提供最关键的两件资产：
- **late-lock timing**
- **public pool imbalance → executable shell**

### 7.2 `madewithai` repo 的概率模型过于轻量
- 只看最近 rounds 的 bull/bear outcome；
- 没有把 payout side 真正并入 EV；
- 也没有外部行情、盘口或 gas 条件。

但它非常适合当我们第一版 `p_hat` 的 baseline。

## 8. 下一步怎么测（直接可排队）

### 实验 A：赔率感知 vs 非赔率感知
对比三组：
1. 只顺 crowd
2. 只反 crowd
3. `EV-aware switch`（推荐主实验）

看：
- win rate
- EV / round
- round-level Sharpe
- 连续亏损段长度

### 实验 B：crowding 分桶
按 `max(B/R, R/B)` 分桶：
- `1.0~1.5`
- `1.5~2.5`
- `2.5~4.0`
- `4.0~5.0`
- `>5.0`

看不同桶里：
- minority side 是否更容易有正 EV
- majority side 何时仍值得追
- 是否存在稳定的 skip 区间

### 实验 C：概率模型 baseline
用三套最小 `p_hat`：
1. 20-round decay momentum（照 repo）
2. 3-round streak reversal（照 repo）
3. 外部现货 `1m/3m` return sign + volatility gate

目标不是一开始追最强模型，而是先看**赔率侧本身有没有信息承接空间**。

### 实验 D：时点敏感度
比较下注时间：
- lock 前 `60s`
- `30s`
- `20s`
- `15s`
- `10s`

验证 late-lock crowding 是否真的更有信息量，还是只是 tx fail 更高。

### 实验 E：跨品种可移植性
分别对：
- `BNBUSD`
- `BTCUSD`
- `ETHUSD`

看哪一类 round：
- crowding 更极端
- break-even gap 更大
- net EV 更稳

## 9. 结论

如果只把这些 repo 当“prediction betting bot”，价值其实很低。

但如果把它们重读成：
- 一份负责给你 **实时 crowding / payout skew**，
- 一份负责给你 **简化版超短线胜率估计**，
- 然后在 lock 前最后十几秒做 **EV-aware switch**，

那它就是一条**可独立复现、可直接交易、而且非常短周期**的 raw alpha。

对当前研究池来说，这个主题的新增信息密度，明显高于再补一篇普通 breakout / pairs 派生 digest。

## 10. 来源

1. **Gavrilov, E. (2026). _crypto-prediction-bot_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/mooncitydev/crypto-prediction-bot`  
   - Repo URL: `https://github.com/mooncitydev/crypto-prediction-bot`

2. **Repo source files used in this digest (`mooncitydev/crypto-prediction-bot`)**  
   - README: `https://raw.githubusercontent.com/mooncitydev/crypto-prediction-bot/master/README.md`  
   - Main: `https://raw.githubusercontent.com/mooncitydev/crypto-prediction-bot/master/src/index.ts`  
   - Shared lib: `https://raw.githubusercontent.com/mooncitydev/crypto-prediction-bot/master/src/lib.ts`

3. **madewithai / Ricardicus (2026). _pancakeswap-prediction-bot_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/madewithai/pancakeswap-prediction-bot`  
   - Repo URL: `https://github.com/madewithai/pancakeswap-prediction-bot`

4. **Repo source files used in this digest (`madewithai/pancakeswap-prediction-bot`)**  
   - README: `https://raw.githubusercontent.com/madewithai/pancakeswap-prediction-bot/main/README.md`  
   - Main loop: `https://raw.githubusercontent.com/madewithai/pancakeswap-prediction-bot/main/src/index.ts`  
   - Strategy: `https://raw.githubusercontent.com/madewithai/pancakeswap-prediction-bot/main/src/strategy.ts`  
   - Config: `https://raw.githubusercontent.com/madewithai/pancakeswap-prediction-bot/main/src/config.ts`

5. **PancakeSwap Docs. (accessed 2026-04-04). _Prediction_.**  
   - Venue: Official documentation  
   - DOI: N/A  
   - Readable URL: `https://docs.pancakeswap.finance/play/prediction`  
   - Notes used: `5m` round frequency, `3%` fee, Chainlink lock/close oracle, tie/settlement rules, BNB/BTC/ETH supported markets.
