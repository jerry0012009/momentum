# 别把 crypto pairs 继续只做静态 z-score：这份 2026 新 repo 更该先抄的是「5m cointegration pair + graduation + daily throttle」完整 stat-arb 操作系统

- 时间：2026-03-31 11:25 UTC
- 类型：2026 GitHub 新仓库（README + selection / execution / daily guard 核心源码细读）
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/graduation/risk-overlay/daily-throttle/bybit/perpetual/5m/15m/repo/live-results/cost/execution
- 证据类型：仓库（README + 4 个核心源码文件 + 自带 execution 导出）
- 主题类型：raw alpha
- 基础 alpha：对 cointegrated perp pairs 做 spread z-score 均值回归交易，只让通过统计检验且最近实盘/回测表现达标的 pairs 升级进 live book，再叠加日内 profit-lock throttle 与 daily stop
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次不是再补一个“pairs 也能做”的概念卡，而是补一个 **能直接拆成 production skeleton 的 2026 repo**：

- 作者把系统拆成 **selection layer + execution layer + daily guard**；
- 信号不是抽象地说“价差回归”，而是落成了 **5m 更新、5m 半衰期、分级 pair 池、分块下单、逐日节流**；
- README 里给了作者自报的 live test 指标（`2025-06 ~ 2025-11`）：
  - `704` 笔交易
  - `64.6%` 胜率
  - `Profit Factor = 1.22`
  - `Balance return = 35%`
  - `Max drawdown = -4.36%`

最重要的是：这份仓库虽然 **不是开箱即跑**（缺 DB schema / config / credentials），但它已经把 desk 真正关心的 5 件事写清楚了：

1. **pair 什么时候能进 live 池**
2. **entry 到底用什么阈值**
3. **仓位怎么随流动性和 beta 变化**
4. **什么条件平仓**
5. **日内赚了/亏了以后，系统如何自动降速或停机**

## 2. 先回答：这篇东西的 base alpha 是什么？
这篇东西的 **base alpha 很清楚**：

- 对两条高相关 perp 价格序列估一个 **hedge ratio**；
- 构造 **spread = P1 - beta × P2**；
- 当 spread 的 **z-score 偏离足够大** 时，做 **short rich leg / long cheap leg**；
- 持有到 spread 回到中线、PnL 命中阈值、或 cointegration 失效。

所以它不是单纯 filter，也不是只有风险管理。  
**核心 alpha 本体就是 cointegration spread mean reversion。**

repo 真正有价值的旁支，在于它把这个 raw alpha 外面又包了两层 desk 很缺的可复现组件：

- **pair graduation / admission layer**
- **daily throttle / daily stop overlay**

## 3. 为什么它值得进当前 desk 的研究池
当前池里已经有不少 pairs / stat-arb 题材，但很多还停留在：

- 只讲 pair formation
- 只讲 z-score entry
- 只讲某个 fancy filter（copula / Kalman / graph）
- 很少把 **entry / exit / sizing / risk / concurrency / daily governance** 一次说全

这份 repo 的价值恰好在于：

1. **它仍然是 raw alpha**，不是“pairs 旁边的一层 gate”；
2. **它给的是完整 operating system**，而不是单点 feature；
3. **它天然服务 5m / 15m**：
   - selection 以 `5m` bar 刷新
   - 监控循环 `30s`
   - 进出场采用 chunked execution
   - hold horizon 由 spread half-life 决定
4. **它很适合 desk 做最小实验**：先不用追求全自动 pair discovery，先用一个小 pairbook 就能开始跑。

## 4. repo 里最值得先抄的，不是“cointegration”四个字，而是三层结构
### A. Pair 质量层：不是所有 z-score 都配进 live
selection 端先在 `5m` 上更新 pair 状态：

- 用 OLS 估 **hedge ratio**
- 计算 spread、z-score、半衰期 `HL`
- 计算 cointegration 检验：
  - `ADF`
  - `p-value`
  - `Hurst`

核心统计门槛来自源码：

- `ADF <= -2.9`
- `p-value <= 0.05`
- `Hurst <= 0.45`
- `HL > 0`
- `|last_spread| < 1.2 × hl_spread_med`

这其实已经不是“看到价差大就上”，而是：
**只有看起来真的像均值回复 spread 的 pair，才有资格进入 execution 候选池。**

### B. Graduation 层：pair 要先证明自己最近还能赚钱
`SQL-DB-Stat-upd-5.py` 里还有一层特别 desk 化的东西：**pair level assignment**。

repo 会基于最近 `60d`、最多 `30` 笔交易的统计，把 pair 打成 `Level_0 / 1 / 2`：

- `Level_30 = L2` 条件：
  - `n >= 15`
  - `win_rate >= 0.55`
  - `reward_risk >= 1.1`
  - `Expect_30 = 1`
- `Level_30 = L1` 条件：
  - `n >= 5`
  - `win_rate >= 0.50`
  - `Expect_30 = 1`
- 然后 live `Level_2` 的最终条件更严：
  - `Expect = 1`
  - `Coint = 1`
  - `num_trades > 20`
  - `level30 in (L1, L2)`

这点很关键：
**repo 不是“组合搜索出 pair 就长期持有信仰”，而是让 pair 先通过最近表现的毕业考试。**

对 desk 来说，这比继续空谈“pair selection 最优算法”更值钱，因为它直接给了一个可测 admission layer：

- raw alpha：spread mean reversion
- gate：recent realized expectancy graduation

### C. Execution / overlay 层：让 alpha 以更像真实 desk 的方式活下来
execution bot 里最有意思的，不是单独某个阈值，而是它把交易写成了完整流程：

1. **候选选择**
   - 只从 `Level_2` 挑
   - 避免资产重叠
   - `ORDER BY Num trades ASC, ABS(last_z_score) DESC`
   - 最多 `4` 个并发 pair

2. **entry 触发**
   - 预筛要求 `ABS(last_z_score)` 达到半衰期相关门槛的 `90%`
   - 对更长半衰期的 pair，提高预筛门槛：
     - `HL < 60 -> 2`
     - `HL < 100 -> 2.5`
     - `HL < 140 -> 3`
     - else `3.5`
   - 正式进场端要求 `|z| >= 2`
   - 同时要求 `|z| < 5`，避免追太离谱的异常点

3. **sizing**
   - 用 **beta-normalized hedge** 决定双腿 exposure
   - 控制腿取 **5m 成交额更小** 的那条腿
   - 另一腿按 `beta_norm` 配比，但把 `beta_norm` clamp 在 `[0.8, 1.2]`
   - 单腿最小 notional `500 USDT`
   - 最大 leverage `5x`
   - 若触发日内 throttle，则 exposure 直接减半

4. **execution**
   - 不是一笔梭哈，而是按 `100 USDT` chunk 分块开平
   - chunk 之间暂停 `3s`
   - 监控循环 `30s`

5. **exit**
   - `pnl% >= pair_tp`：止盈
   - `pnl% <= -pair_sl`：止损
   - 超过 `HL × 5min` 后若 cointegration 丢失：退出
   - 若 `|z| >= 6` 且 cointegration 丢失：退出
   - 若 z-score 穿过 `0`：退出

这比“z-score 回到 0 就平”多了一整层真实交易语义。

## 5. 对短周期 desk，最值得抄的其实是「raw alpha + graduation + daily guard」三段式
如果把它 desk 化，最值得先测的不是“完全 faithful 地重建它的数据库工程”，而是下面这条更小、但仍然忠于仓库精神的版本：

### 策略骨架
- **方向**：pairs / stat-arb / relative-value / market-neutral
- **alpha 本体**：cointegrated spread mean reversion
- **admission layer**：recent realized expectancy graduation
- **risk overlay**：daily TP throttle + daily SL block

### 为什么这个版本最适合先做
因为它同时满足四件事：

1. **base alpha 清楚**：spread MR
2. **能独立交易**：不是别人的附庸 gate
3. **能快速实验**：公开 K 线即可启动第一版
4. **能直接接实盘组件**：pairbook、sizing、chunk execution、daily risk 全都可落地

## 6. 我认为 repo 最有价值的“旁支想法”
如果只抄 headline，大家会说：
“哦，这不就是 cointegration pair trading 吗？”

但对我们 desk，真正更有价值的其实是 **旁支**：

### 旁支 1：graduation 比更花哨的 signal 更重要
很多 pair 策略死，不是因为 spread 信号完全没信息，而是因为：

- 某个 pair 的边已经衰退
- 但系统还在机械复用老 pair

这个 repo 用 `60d / max 30 trades` 的 recent expectancy 去做升级/降级，给了一个很诚实的 pair rotation 框架：

- **先承认 pair alpha 会过期**
- 再决定 pair 能不能继续占用 live 预算

这很适合直接服务我们后续所有 pairs / stat-arb 线，而不只是这一篇 repo 本身。

### 旁支 2：日内 profit-lock throttle 很适合 crypto 24/7 desk
`daily_guard_2.py` 不是只会“亏到某处就停机”。它还做了一个更有意思的东西：

- 日内收益达到 `1%` -> 开启 throttle
- 下一档阈值翻倍到 `2%`
- 再到 `4%`、`8%` ……
- throttle 状态下新仓 exposure 直接打半
- 若日内 PnL 到 `-3%` -> block 当天不再开新仓

这不等于 alpha 本体，但它非常适合当 **shared risk overlay**：

- 顺风日减少回吐
- 逆风日直接停手
- 不需要低频宏观数据
- 可以直接挂到 `1m / 3m / 5m / 15m` 的任何快策略上

### 旁支 3：control leg 用低流动性腿，比“固定等额双边”更 desk 化
仓位这块它不是死板地 1:1 配，而是：

- 先看两腿 `5m` dollar volume
- 让 **流动性更差** 的那条腿当 controller
- 先 cap controller exposure
- 再按 beta 扩到另一腿
- 若另一腿超 cap，再双边一起缩小

这给了我们一个很现实的 sizing 原则：
**stat-arb 的容量，应该由更难成交的那条腿决定。**

## 7. 这条线的明显短板
这 repo 不是神谕，明显短板也要写清：

1. **缺数据库 schema / 配置 / 凭证**
   - 说明它更像“可读 operating blueprint”，不是开箱复现包。

2. **live 成绩是作者自报，暂时没有独立审计**
   - `704 trades / 64.6% / PF 1.22 / +35% / -4.36%` 可当线索，不能直接当事实真相。

3. **pair formation 仍不够透明**
   - repo 核心更强的是 execution + governance；
   - 真正的 pairbook 生成似乎部分依赖外部维护的 `list1.csv` / 预先筛选流程。

4. **部分参数仍偏经验化**
   - 例如 `|z| >= 2`、`|z| < 5`、`z_exit = 6`、`daily TP = 1%`、`daily SL = 3%`，需要 desk 自己再做敏感度测试。

但即便如此，它仍然值钱，因为：
**它把“pair alpha 如何活成一个日常可跑系统”这件事写得比大多数论文都具体。**

## 8. 对我们最像最小实验的版本
### 实验目标
先验证：
**cointegration spread MR 在 5m / 15m crypto perp 上，是否只有叠 recent-graduation 与 daily-throttle 后，才更像能活的完整策略。**

### 最小实验口径
**Universe**
- Binance 或 Bybit USDT perp，过去 `30d` ADV 前 `20~30` 个币
- 上线满 `120d`
- 去掉长期限价保护 / 极低价 / 异常 funding 币

**Pairbook（第一轮别贪大）**
- 先人工/半自动选 `10~15` 组高相关 pair
- 可优先同 beta / 同 sector / 同叙事（L1、meme、AI、exchange 等）
- 先不做全组合爆搜

**Signal**
- bar：`5m`
- rolling OLS beta
- spread z-score
- `ADF / p-value / Hurst / HL`
- 只有通过：
  - `ADF <= -2.9`
  - `p <= 0.05`
  - `Hurst <= 0.45`
  - `HL > 0`
  才允许进候选

**Entry**
- baseline：`|z| >= 2`
- strong version：按 HL 分桶提高门槛（`2 / 2.5 / 3 / 3.5`）
- hard cap：`|z| < 5`

**Sizing**
- 用较低 `5m` ADV 腿控制双边容量
- beta-normalized 双腿敞口
- beta clamp 到 `[0.8, 1.2]`
- 单腿最小 notional `300~500 USDT`

**Exit**
- `z cross 0`
- `pair TP / SL`
- `HL timeout + coint lost`
- `|z| >= 6 + coint lost`

**Overlay**
- 日内 `+1%` 开始半仓 throttle
- 日内 `-3%` 当天停手

**Cost**
- 第一轮先用 `6 / 10 / 15 bps per side` 三档
- 另记 funding、maker/taker 占比与 chunk execution 滑点

## 9. 我会怎么排优先级
如果只给一次实验预算，我不会先做“全自动 pair discovery + 全自动毕业系统 + 实盘接单”三件套。

我会按下面顺序：

1. **先测 raw alpha 本体**
   - 小 pairbook
   - `|z|>=2`
   - `z cross 0` 平仓

2. **再加 graduation**
   - recent `60d / 30 trades` 的 expectancy gate

3. **最后加 daily guard**
   - `+1%` throttle
   - `-3%` daily stop

也就是先回答三个问题：

- spread MR 本体有没有边？
- admission layer 是不是比“继续堆 fancy signal”更值钱？
- daily throttle 到底是在保利润，还是只是在砍交易数美化？

## 10. 我的判断
这篇 repo 最该进研究池的，不是因为它证明了“pairs 很强”，而是因为它给了一个很难得的东西：

**raw alpha + pair graduation + daily risk governor 的完整可复现骨架。**

如果要继续扩 desk 的 **raw alpha 素材池 / 实盘组件池**，我会给它一个相当高的优先级，因为它同时补了三块：

- pairs alpha 本体
- pair-level admission
- shared daily overlay

其中最值得复用到别的线上的，不一定是 z-score 本身，反而是：

- **recent expectancy graduation**
- **profit-lock throttle**
- **low-liquidity-leg controller sizing**

## 11. 下一步怎么测
直接做一个 **A/B/C 三层递进实验**，不要一步上 production：

1. **A = raw spread MR baseline**
   - `5m`
   - `|z| >= 2`
   - `z cross 0` exit
   - 不加 graduation，不加 daily overlay

2. **B = A + graduation**
   - 只交易 recent `60d / max 30 trades` 里 `Expect_30 = 1` 的 pair
   - 对比 trade count、胜率、PF、成本后净值

3. **C = B + daily throttle / stop**
   - 日内 `+1%` 后新仓半仓
   - 日内 `-3%` 后停手
   - 对比回吐、MDD、收益偏斜、活跃天数

第一轮输出至少要有：

- pair-level PnL 分布
- graduation 前后 retained pairs 数量
- throttle 触发频率
- daily stop 触发频率
- gross / net Sharpe
- PF
- MDD
- turnover
- 平均持仓时长
- 单腿 ADV 占比

如果结果显示：

- **A 就死透**：这 repo 的价值降级为 execution/risk overlay 参考，不再把它当主 alpha。
- **A 有边，B 明显更稳**：优先保留 graduation，把它作为 pairs 主线的 admission 标配。
- **B 有边，C 只是在大幅砍单**：daily guard 只能算 risk overlay，不能拿来伪装 alpha 改进。
- **C 同时降低回撤且回吐收窄**：daily throttle 可升级为跨 alpha 的 shared component。

## 12. 来源
1. **Anton Velychko (2026). _statistical_arbitrage_trading_system_V1_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: 无  
   - Readable URL / Repo URL: https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1

2. **Anton Velychko (2026). _README.md_ — live results / architecture / system overview. GitHub Repository file.**  
   - Venue: GitHub  
   - DOI: 无  
   - Readable URL: https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/blob/main/README.md

3. **Anton Velychko (2026). _selection/SQL-DB-Coint-upd-6.py_ — 5m spread / half-life / ADF / Hurst / z-score update logic. GitHub Repository file.**  
   - Venue: GitHub  
   - DOI: 无  
   - Readable URL: https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/blob/main/selection/SQL-DB-Coint-upd-6.py

4. **Anton Velychko (2026). _selection/SQL-DB-Stat-upd-5.py_ — pair graduation / recent expectancy / level assignment logic. GitHub Repository file.**  
   - Venue: GitHub  
   - DOI: 无  
   - Readable URL: https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/blob/main/selection/SQL-DB-Stat-upd-5.py

5. **Anton Velychko (2026). _execution/Level_2_CFT_bot_07-12-2025.py_ — candidate selection / dynamic leverage / chunked execution / exit rules. GitHub Repository file.**  
   - Venue: GitHub  
   - DOI: 无  
   - Readable URL: https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/blob/main/execution/Level_2_CFT_bot_07-12-2025.py

6. **Anton Velychko (2026). _execution/daily_guard_2.py_ — profit-lock throttle / daily stop overlay. GitHub Repository file.**  
   - Venue: GitHub  
   - DOI: 无  
   - Readable URL: https://github.com/velychkoanton-stack/statistical_arbitrage_trading_system_V1/blob/main/execution/daily_guard_2.py
