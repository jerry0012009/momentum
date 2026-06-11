# 别把这份 2026 spot-basis engine 只读成套利后台：对 short-cycle desk，更该先测的是「funding-stability E24 score × profit-lock exit」这条完整 carry raw alpha

- 主题类型：raw alpha
- 基础 alpha：**在同标的 `spot long / perp short` 的 delta-neutral 结构里，不是见到正 funding 就无脑开，而是只做“未来 24h 预期净 funding 收益 - fee - basis/liquidity/instability penalty”仍为正、且 funding 足够稳定的那一侧 carry**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-03 03:20 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `backend/core/spot_basis_runtime/scanner.py` + `scoring_config.py` + `backend/core/spot_basis_backtest/engine.py` + `params.py` + `backend/core/spot_basis_auto_engine/open_cycle.py` + `profit_lock.py`）
- 主题标签：raw-alpha/carry/funding/basis/spot-perp/same-underlier/market-neutral/funding-stability/e24-net-profit-lock/drawdown-guard/liquidity-penalty/capacity-score/5m/15m/3m/1m/repo/public-data/cost/risk
- 证据类型：repo-based（而且是**已把 entry / exit / sizing / risk / cost 写进代码**的完整策略壳）

## 1. 这次为什么选它

这轮默认优先补 **能直接落地为完整策略** 的 raw alpha，而不是再做纯解释型材料。

如果只问一句“这篇东西的 base alpha 是什么？”，这次答案很清楚：

> **base alpha = funding/basis carry。**
> 但不是粗糙版“谁 funding 高就去收谁”，而是 **只做 funding 稳定、扣完成本和风险惩罚后，未来 24h 期望净收益仍为正** 的那部分 spot-perp carry。

它比继续补一个普通 gating 主题更值得 intake 的原因也很直接：

1. **它是 raw alpha 本体，不是 filter 伪装成 alpha；**
2. **它给的是完整策略链条**，不是一句“funding 有预测力”；
3. repo 里已经把：
   - 机会扫描
   - 打分
   - 开仓
   - 切换确认
   - profit lock
   - stale data 处理
   - drawdown hard stop
   - backtest engine
   全都写出来了。

对 desk 来说，这种材料的价值很高，因为它不是再给一个“可以以后再想怎么交易”的概念，而是直接往 **复现素材池 / 实盘组件池** 里塞一条可以拆件测试的策略壳。

## 2. 这次看的材料

### 2.1 主材料：完整 repo

- **Author / Maintainer**: `GrooveWJH`（GitHub handle）
- **Year**: 2026
- **Title**: *ArbitrageStation*
- **Venue**: GitHub repository
- **DOI**: N/A
- **Readable URL**: <https://github.com/GrooveWJH/ArbitrageStation>
- **Repo URL**: <https://github.com/GrooveWJH/ArbitrageStation>

### 2.2 本轮重点审的源码文件

- `backend/core/spot_basis_runtime/scanner.py`
- `backend/core/spot_basis_runtime/scoring_config.py`
- `backend/core/spot_basis_backtest/engine.py`
- `backend/core/spot_basis_backtest/params.py`
- `backend/core/spot_basis_auto_engine/open_cycle.py`
- `backend/core/spot_basis_auto_engine/profit_lock.py`

## 3. 先把 base alpha 说死：这是 carry，本体不是 overlay

这条策略的原型很简单：

- 现货多头；
- 永续空头；
- 吃 funding；
- 同时盯 basis、费率稳定性、容量和执行风险。

但 repo 的关键提升在于：

> **它不是把 funding 当单一排名字段，而是把“未来 24h 可兑现净收益”显式写成 score。**

所以这不是：
- 纯 risk overlay；
- 纯 entry filter；
- 纯交易基础设施；
- 也不是“所有 carry 都能用它”。

它是一条明确的 **same-underlier spot-perp market-neutral raw alpha**：

- 只有当 `carry edge` 为正、且稳定、且装得下仓位时才开；
- 只有当 `spread 已兑现足够利润`、`drawdown 过深`、`basis shock`、`数据失真` 等条件触发时才关。

## 4. repo 里真正值得拿来抄的，不是“spot/perp 套保”四个字，而是这套 E24 严格打分

### 4.1 机会扫描不是只看当前 funding，而是先补近 3 天已结算 funding 历史

`scanner.py` 里最重要的一件事是：

- 扫描前会强制刷新 **近 3 天 funding history**；
- 然后对每个候选计算 funding stability；
- 默认按 `score_strict` 排序，而不是按单个 funding rate 排序。

这意味着它的基本哲学不是：

> “现在 funding 高，冲。”

而是：

> “现在 funding 看起来高，但它到底稳不稳、翻不翻符号、能不能覆盖手续费和 basis 风险？”

这个思路对 short-cycle desk 很重要，因为很多 funding carry 死法都不是“方向看错”，而是：
- fee 没覆盖；
- funding 只是一笔脉冲；
- basis 已经偏得太离谱；
- 容量一上去，impact 把 edge 吃没。

### 4.2 它把 `未来 24h 净收益` 显式写成了 entry 的核心变量

`scoring_config.py` 里的核心变量是：

- `expected_24h_gross_pct`
- `fee_amortized_pct_day`
- `risk_penalty_pct_day`
- `e24_net_pct`
- `confidence`
- `capacity`
- `score_strict = e24_net_pct * confidence * capacity`

翻成人话：

1. 先估计未来 24h 这条 carry 大概能赚多少；
2. 再扣掉摊销手续费；
3. 再扣 basis/liquidity/instability/stale/period uncertainty 等风险罚分；
4. 然后乘上 **“我有多确信它稳定”** 和 **“它能装多大仓位”**。

这比很多 funding 排名逻辑高一层，因为它避免了两个常见错觉：

- **错觉一：高 funding = 高 alpha。**
  - 不对，高 funding 可能只是快翻号、快回归、快被 basis 吃掉。
- **错觉二：有 alpha = 能上仓。**
  - 不对，容量不足、impact 太大时，纸上 alpha 不可交易。

### 4.3 代码里的几个关键数值，值得直接抄成第一版实验参数

repo 默认参数里最有用的几组数：

- **funding 稳定性回看窗**：`3 days`
- **调仓 bucket**：`15m`
- **最多开仓对数**：`5`
- **目标资金利用率**：`60%`
- **单对最小名义**：`300 USD`
- **单对最大名义**：`3000 USD`
- **单账户硬止损**：`-4%` drawdown
- **切换确认轮数**：`3`
- **数据 stale 容忍**：`3` 个 `15m` bucket

这些数字未必是我们的最终最优值，但非常适合作为 desk 第一个最小可跑版本的默认超参。

## 5. 这条 raw alpha 的信号骨架，其实已经比很多“论文 + repo”组合更完整

### 5.1 Entry：不是“正 funding 就开”，而是 **正的可兑现净 carry** 才开

从代码逻辑看，第一版可以直接抽象成：

**Entry 条件**
1. 标的同时有可交易 spot 与 perp；
2. 近 3 天 funding history 足够；
3. `e24_net_pct_strict > 0`；
4. `confidence` 达标；
5. `capacity` 达标；
6. impact、basis、stale 风险不过界；
7. 连续若干轮确认后才真正 rebalance / open。

对我们 desk，这个写法最大的现实意义是：

> **它把 carry 从“慢频观念”改写成了“每 15m 可以重新审核一次的净收益排名问题”。**

### 5.2 Exit：repo 真正有价值的，是它没把平仓写成“funding 变负就跑”

`profit_lock.py` 里最值得抄的是这个想法：

- 它先计算当前持仓的 `spread_pnl_pct`；
- 再减掉开仓费和预计平仓费；
- 得到一个 `lock_metric_pct`；
- 只要这个值已经大于阈值 `threshold_pct = max(entry_e24_pct, current_e24_pct)`，就直接锁利润。

也就是：

> **如果本来预计未来 24h 才能赚到的钱，spread 现在已经提前兑现出来了，那就别再恋战，先把钱落袋。**

这对 short-cycle desk 很关键，因为很多 carry 仓并不是死在 funding 本身，而是死在：

- 你已经吃到了该吃的 basis/spread 回归，
- 但还继续抱着等下一次 funding，
- 最后又把已实现利润吐回去。

### 5.3 Risk：它把 production 里最常见的几种死法都单独做了 guard

`open_cycle.py` 里有几类 guard，都是很 desk-friendly 的：

1. **API fail circuit breaker**
   - 连续 API 失败达到阈值，直接 disable；
2. **hedge mismatch repair / fallback close**
   - 两条腿对不上先修，不行就平；
3. **NAV stale guard**
   - 资金快照过期，不拿旧 NAV 做 sizing；
4. **profit lock exit**
   - spread 利润已兑现就关；
5. **portfolio drawdown soft / hard stop**
   - soft 减仓，hard 全平；
6. **basis shock exit**
   - basis 异常扩张时直接离场；
7. **stale-data risk reduce**
   - 数据老化就缩风险。

这套东西的意义不是“好复杂”，而是：

> **它说明这条 carry 已经不是想法阶段，而是接近生产阶段的策略壳。**

## 6. 对 short-cycle（1m / 3m / 5m / 15m）该怎么诚实地理解它

这里必须说实话：

- 这条 alpha 的 **经济来源** 不是 1m/3m 微观结构；
- 它本质上还是 funding/basis carry；
- 所以 **主信号形成周期天然偏慢**。

但这不等于它和短周期 desk 无关。

更准确的读法应该是：

### 6.1 `15m / 5m` 是主工作频率

最自然的第一版是：

- **15m**：重算 score、重排候选、评估是否切换；
- **5m**：盯 profit-lock、basis shock、stale data、执行成本；
- **1m / 3m**：用于执行分片、滑点检测、microstructure veto，而不是重建 funding edge 本身。

### 6.2 它适合当“慢 alpha + 快执行壳”

也就是说：

- alpha 本体：`funding-stable carry`
- 快周期组件：
  - 入场分片
  - queue 选择
  - spread 兑现即平
  - 1m/3m 的 slippage veto

这和把外部低频变量硬装成逐 bar directional alpha 不一样。

这里的 carry 本体本来就可独立赚钱；
短周期做的是 **执行和风控优化**，不是替它编故事。

## 7. 第一版最小实验，建议直接照 repo 思路压成 desk 版

## 7.1 数据口径

**公开可得数据**：
- Binance / Bybit / OKX 公共 perp funding history
- spot / perp 行情（`1m`、`5m`、`15m`）
- 24h volume
- fee schedule（可先用 taker 近似）

**更新频率**：
- funding：按交易所结算频率更新（常见 8h）
- price / basis / volume：分钟级

**最小可复现实验口径**：
- Universe：先只做主流 `10~20` 个有 spot+perp 的币
- Bucket：`15m`
- Funding stability 窗口：过去 `3d`
- Ranking：每 `15m` 算一次 `score_strict`
- Portfolio：取前 `1~5` 个正分候选，做 `spot long / perp short`

## 7.2 Entry / Exit / Sizing / Risk / Cost

### Entry
- `e24_net_pct_strict > 0`
- `confidence >= 0.55`
- `capacity >= 0.12`
- `impact_pct <= 0.30`
- `score_strict` 排名前列
- 同一候选连续 `3` 个刷新轮仍满足，再开仓

### Exit
- `profit-lock`：`spread_pnl_pct - open_fee - close_fee >= max(entry_e24, current_e24)`
- `score_strict <= 0` 连续 `2~3` 轮
- basis shock
- data stale
- portfolio drawdown hard stop

### Sizing
- 组合总利用率先卡 `60%`
- 最多 `5` 对
- 单对先做 `300~3000 USD`
- 先做 equal-notional；第二轮再加 vol / ADV cap

### Cost
- 先按 taker/taker 双边估
- 单独记录：
  - 开仓费
  - 平仓费
  - rebalance 费
  - basis 漂移损益
  - funding 收益

## 7.3 第一批该看的结果，不是年化，而是这 6 个数

1. `funding pnl / gross pnl` 占比
2. `basis pnl` 是否经常把 funding 吃掉
3. `profit-lock` 触发占比
4. `avg hold time`
5. `fee / gross edge` 比例
6. `hard stop` / `stale close` / `basis shock` 触发频率

如果这 6 个数难看，说明这条 alpha 不是“没故事”，而是 **不可执行**。

## 8. 我认为这条策略最值得 desk 抄的，不是 carry 本身，而是这三个“旁支组件”

虽然主 digest 选的是 raw alpha，但 repo 里有三个拆件也很值得单独复用：

### 8.1 `E24 net` 思路
把一条 raw alpha 改写成：

> **未来 24h 预期收益 - 成本 - 风险罚分**

这套表达方式，其实也能迁到：
- pairs
- funding switch
- cross-venue carry
- event-driven basis fade

### 8.2 `profit-lock` 思路
如果当前 spread 已经把未来预期收益提前兑现，就先平。

这不只适用于 carry，也适用于：
- pairs spread MR
- relative-value convergence
- 事件驱动 shock fade

### 8.3 `confidence × capacity` 双乘法
很多研究只排 alpha，不排“能装多大”。

这个 repo 的可贵之处在于：
- `confidence` 负责“像不像真的 edge”；
- `capacity` 负责“这 edge 能不能交易”。

这比只看 signal strength 更接近 production 思维。

## 9. 这条 alpha 最可能死在哪里

### 9.1 funding 频率天然偏慢，别强行装成 1m directional alpha

如果把它误读成：
- 每 1m 都有新 alpha；
- 或 1m/3m 排名能更强；

大概率会把它做坏。

更合理的是：
- 15m 做组合决策；
- 5m 做风险刷新；
- 1m/3m 做执行质量控制。

### 9.2 basis shock 可能比 funding 更大

很多 carry 回撤不是 funding 不够，而是：

- perp 折价/溢价快速扩张；
- mark/index 偏离加大；
- 你还没等到结算，就先在 basis mark-to-market 上吃亏。

所以第一轮 backtest 一定要把：
- funding pnl
- basis pnl
分开记。

### 9.3 fee amortization 假设很关键

repo 里把 round-trip fee 按 `hold_days` 摊销，这个思路对，但：

- 如果真实持有时间比假设短；
- 或需要更频繁切换；

那 `e24_net_pct` 很容易被高估。

所以 desk 第一轮要额外跑：
- `hold_days` 偏乐观 / 中性 / 偏保守 三档。

## 10. 结论

如果只看 headline，这个 repo 很容易被读成“又一个套利后台”。

但对我们 desk，更值得 intake 的其实是：

> **把 same-underlier spot-perp carry 写成 `E24 expected net edge` 排名问题，再用 `profit-lock + drawdown/basis/stale guards` 把它补成完整策略。**

一句话总结：

- **主题类型**：raw alpha
- **基础 alpha**：funding/basis carry
- **是否可独立复现**：是
- **是否可直接落地完整策略**：是

而且这次不是“勉强能落地”，是真正已经具备：
- entry
- exit
- sizing
- risk
- cost
- backtest
- live cycle

全链条定义的那种可落地。

## 11. 下一步怎么测（直接执行版）

### Step 1：做最小离线回测
- 标的：BTC / ETH / SOL + 5~10 个高流动性 alt
- 频率：`15m`
- 窗口：近 `3d` funding history
- 组合：top `1~3` 正分 carry
- 成本：taker/taker 双边 + `2` 档额外滑点压力测试

### Step 2：拆 PnL 归因
至少分成：
- funding pnl
- basis pnl
- fee pnl
- forced exit pnl

### Step 3：加 5m 执行 veto
当以下任一发生时，延后开仓或减半：
- 过去 `5m` basis 扩张超过阈值
- 过去 `5m` 盘口/成交额恶化
- 下一个 funding settlement 太近，来不及摊薄费用

### Step 4：再决定是否下钻到 1m / 3m
如果 `15m` 版本本身站不住，没必要把它强压成更快频率；
如果 `15m` 版本能站住，再看 1m/3m 是否只改善执行，而不是改变 alpha 本体。

## 12. 来源链接

- Repo 首页：<https://github.com/GrooveWJH/ArbitrageStation>
- README：<https://raw.githubusercontent.com/GrooveWJH/ArbitrageStation/main/README.md>
- Scanner：<https://raw.githubusercontent.com/GrooveWJH/ArbitrageStation/main/backend/core/spot_basis_runtime/scanner.py>
- Strict scoring：<https://raw.githubusercontent.com/GrooveWJH/ArbitrageStation/main/backend/core/spot_basis_runtime/scoring_config.py>
- Backtest engine：<https://raw.githubusercontent.com/GrooveWJH/ArbitrageStation/main/backend/core/spot_basis_backtest/engine.py>
- Backtest params：<https://raw.githubusercontent.com/GrooveWJH/ArbitrageStation/main/backend/core/spot_basis_backtest/params.py>
- Auto open cycle：<https://raw.githubusercontent.com/GrooveWJH/ArbitrageStation/main/backend/core/spot_basis_auto_engine/open_cycle.py>
- Profit lock：<https://raw.githubusercontent.com/GrooveWJH/ArbitrageStation/main/backend/core/spot_basis_auto_engine/profit_lock.py>
