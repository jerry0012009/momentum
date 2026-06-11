# 别把这份 2026 新 repo 只读成“费率排行榜”：对 short-cycle desk，更该先测的是「fee-coverage gated cross-venue funding carry」这条完整 raw alpha

- 时间：2026-04-02 17:34 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `config.yaml` + `scripts/scan_all.py` + `scripts/auto_selector.py` + `scripts/fee_coverage_calculator.py` + `scripts/rolling_position.py` + `scripts/trailing_stop.py`）
- 主题标签：raw-alpha/carry/funding/cross-venue/perp-perp/relative-value/stat-arb/fee-coverage/cost-gate/rolling-position/trailing-stop/gate-bitget-aster-okx/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo-based source audit（工程证据为主，含 README 披露的实盘样例与源码规则）

- 主题类型：raw alpha
- 基础 alpha：**同一币种在不同 perpetual venue 的 funding rate 存在可交易价差；做 `long 最便宜 funding leg / short 最贵 funding leg` 的 delta-neutral 结构，赚 funding differential，本体是 carry / relative-value，不是风控壳。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
### 一句话核心结论
**这轮最值得 intake 的，不是“又一个 funding scanner”，而是 repo 里那条很实在的完整 raw alpha：先找同币跨所 funding spread，再用明确的 `fee coverage` 门槛决定这笔 carry 到底值不值得做；而 rolling build、trailing stop、exchange reliability 这些都已经把它往完整策略推了一步。**

### 一句话它是怎么证明的
- **工程侧**：repo 直接把机会扫描、打分、手续费覆盖度、滚动建仓、移动止损、参数优化拆成独立脚本，不是只有一个“费率排行榜”。
- **硬数据侧**：README 披露的样例里，`PIXEL/JTO/SUPER/0G` 四个机会合计 **约 `57.5U` 敞口、`0.894U/天` 日收**，并宣称 **`6` 个月+、`100+` 笔** 实盘正收益；虽然这当然要打折看，但至少说明作者在尝试把 funding carry 当可执行策略，而不是纯理论。
- **最有价值的细节**：源码里的 `fee_coverage_calculator.py` 逼着我们承认——**不是看到 funding spread 就能收租，必须先过费用壳**。这比很多泛 funding 摘要更适合 desk 直接复现。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这次 **base alpha 很清楚，而且是 raw alpha**。

不是 regime，不是 filter，也不是 risk overlay 假装成 alpha。

alpha 本体就是：
1. **同一 underlier 在不同 perp venue 的 funding 不同步；**
2. **如果某个 venue 更“贵”（更高正 funding）而另一个更“便宜”（更低甚至负 funding），就可以做跨 venue delta-neutral carry；**
3. **真正的收益来源是 funding differential，价格方向尽量被对冲掉。**

所以它的正确归类是：
- `raw alpha`
- 更具体地说是：`carry / funding / cross-venue / relative-value / stat-arb`

`fee coverage`、`rolling build`、`trailing stop` 很重要，但它们都不是 alpha 本体；它们是这条 alpha 能不能活到实盘的执行壳。

## 3. 为什么这轮值得写，而不是继续堆一个泛 funding 摘要
虽然项目最近已经 intake 过不少 funding / basis / carry 方向，但这轮仍然值得写，原因很简单：

1. **它仍然是 raw alpha，不是纯 overlay。**
   这点先过线了。它服务的是 raw alpha 素材池，而不是又写一个“可以给别的 alpha 当 gate”的低优先级组件。
2. **它补的是“显式费用门槛”这一块。**
   最近 desk 的 funding 主题很多都强调 `richest vs cheapest`、`basis diff`、`async clock`，但这份 repo 最值得拿走的是：**能不能开仓，不先看 headline APR，而先看成本覆盖。**
3. **它更像完整策略骨架，而不是一句研究结论。**
   这里不是只给你一个排序器；它把 `entry / ranking / position management / stop / risk preference` 都做了模块化拆解。
4. **它很适合映射到 `1m / 3m / 5m / 15m`。**
   funding 本体不是逐根 1m 主信号，但完全可以用：
   - `15m` 做 opportunity refresh
   - `5m` 做 admission / leg-check
   - `1m/3m` 做执行与对冲同步控制

也就是说，这轮不是“又来一篇 funding”，而是**把 funding carry 从思路池往可执行素材池又推进了一步**。

## 4. 这次看了什么来源
### 4.1 主工程来源
- **Author / Repo owner**：Siyebai
- **Year**：2026
- **Title / Repo**：*libai-funding-rate*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：<https://github.com/Siyebai/libai-funding-rate>
- **Repo URL**：<https://github.com/Siyebai/libai-funding-rate>

### 4.2 本轮实际审阅的关键文件
- `README.md`
- `config.yaml`
- `scripts/scan_all.py`
- `scripts/auto_selector.py`
- `scripts/fee_coverage_calculator.py`
- `scripts/rolling_position.py`
- `scripts/trailing_stop.py`

### 4.3 原始可读链接
- README（raw）：<https://raw.githubusercontent.com/Siyebai/libai-funding-rate/main/README.md>
- config（raw）：<https://raw.githubusercontent.com/Siyebai/libai-funding-rate/main/config.yaml>
- scanner（raw）：<https://raw.githubusercontent.com/Siyebai/libai-funding-rate/main/scripts/scan_all.py>
- fee coverage（raw）：<https://raw.githubusercontent.com/Siyebai/libai-funding-rate/main/scripts/fee_coverage_calculator.py>
- rolling position（raw）：<https://raw.githubusercontent.com/Siyebai/libai-funding-rate/main/scripts/rolling_position.py>
- trailing stop（raw）：<https://raw.githubusercontent.com/Siyebai/libai-funding-rate/main/scripts/trailing_stop.py>

## 5. 这份 repo 真正给了 desk 什么

### 5.1 先别看 fancy 词，主线其实很朴素
repo 的策略主线就是：
- 同时扫描 `Gate / Bitget / Aster / OKX`
- 找同币跨 venue funding spread
- 再按 spread、流动性、稳定性、volume、交易所可靠性排序
- 只有过了成本壳的机会才建议开仓

`config.py / config.yaml` 里给出的默认骨架很直接：
- `SCAN_INTERVAL_SECONDS = 60`
- `MIN_PAIR_APR = 50`
- `MIN_VOLUME_USD = 50_000`
- `POSITION_SIZE_USD = 100`
- 交易所优先级：`Bitget 0.95 > Gate 0.90 > Aster 0.85`

翻成人话：
**它不是在找“理论上最大 spread”，而是在找“你真能下得动、且 venue 风险不离谱的 spread”。**

### 5.2 README 披露的样例收益，只能当工程线索，不能当学术事实
README 给出的实盘样例是：
- `PIXEL ~20U → 0.182U/天`
- `JTO ~26.6U → 0.148U/天`
- `SUPER ~10.3U → 0.512U/天`
- `0G ~0.58U → 0.052U/天`
- 合计：**`~57.5U` 敞口、`~0.894U/天` 日收**
- 并写了一个 **`~567%` 理论年化**

这些数字当然不能直接信成 desk 结论，因为：
- 样本极小；
- 多是小票；
- 没有标准化资金曲线；
- “理论年化” 很容易高估可持续性。

但它至少提供了一个很重要的信息：
**作者在实际关注的是“小票 funding 高离散窗口”，不是 BTC/ETH 这种被挤平的成熟 carry。**

### 5.3 这轮最值钱的不是扫描器，而是 `fee coverage` 这层 honesty gate
`fee_coverage_calculator.py` 用 taker fee 假设：
- Gate `0.05%`
- Bitget `0.06%`
- Aster `0.05%`
- OKX `0.05%`

并默认：
- 每天 `3` 次 funding 结算
- 每天 `6` 次交易动作（对应若干 round-trip）
- 规则：**只有 coverage > 50% 且净收益为正，才建议开仓**

我按源码口径重算了几个最关键的阈值（以 `Gate + Bitget` 为例）：

1. **rate diff = `0.10%` / settlement**
   - 日 funding 收入：`0.30%`
   - 日手续费成本：`0.33%`
   - **净收益：`-0.03%/天`**
   - 结论：**不值得开仓**

2. **rate diff = `0.20%` / settlement**
   - 日 funding 收入：`0.60%`
   - 日手续费成本：`0.33%`
   - **净收益：`+0.27%/天`**
   - 但 coverage 只有 **`45%`**，还没过 repo 自己的 `>50%` 标准

3. 若按这段代码的假设，
   - **break-even spread 大约是 `0.11%` / settlement**
   - **要满足 “coverage > 50%” ，spread 大约要到 `0.22%` / settlement**

这三个数字非常重要。因为它们直接告诉 desk：
**这条 alpha 不是 always-on 收租，更像“高 spread、高手续费覆盖、高离散窗口”才值得碰的 pocket carry。**

### 5.4 这份 repo 其实已经把 alpha 与 overlay 分开了
repo 里的模块分工很清楚：
- `scan_all.py`：找 raw alpha 候选
- `auto_selector.py`：做 ranking / filter
- `fee_coverage_calculator.py`：做成本 gate
- `rolling_position.py`：做分批建仓与盈利后加仓
- `trailing_stop.py`：做盈利保护

也就是说，它非常适合按 desk 语言重述成：
- **alpha 本体**：funding differential
- **filter / veto**：coverage、liquidity、stability、exchange reliability
- **risk / sizing**：rolling build + max position pct
- **exit / overlay**：breakeven + trailing stop

这就是为什么它不是“只会扫表”的玩具，而是可拆成完整策略骨架的来源。

## 6. 但这份 repo 也有两个必须先修的地方

### 6.1 funding 方向口径疑似有反向风险
`scan_all.py` 里是这样排机会的：
- 取 funding **最高** 的 venue 叫 `max_long`
- 取 funding **最低** 的 venue 叫 `max_short`
- 然后输出 `long_exchange = max_long`、`short_exchange = max_short`

如果这些交易所 funding API 采用的是标准口径（**正 funding = longs pay shorts**），那么经济方向应该通常是：
- **short 最贵 funding leg**
- **long 最便宜 / 最负 funding leg**

换句话说，源码里的 leg 命名和真实资金流方向之间，至少存在 **sign-convention risk**。

这不意味着这条 alpha 失效，反而说明：
**alpha 本体是对的，但第一版复现必须自己统一 funding 符号与收付款方向，不能直接照抄 scanner 输出。**

### 6.2 不同脚本里的单位口径并不完全一致
源码里至少有三种容易混淆的写法：
- `config.yaml`：`min_spread: 0.001` 并注释成 `0.1%`
- `auto_selector.py`：`min_spread: 0.10`
- `scan_all.py`：筛选条件写成 `spread > 0.01`

这提示一个非常实际的问题：
**spread 在不同脚本里到底是 decimal、百分数，还是 bps，没有被统一到底。**

所以第一轮最小实验里，必须先做一件很无聊但很关键的事：
- 所有 funding diff 统一转成 **bps per settlement**
- 所有 fee 统一转成 **bps per leg / round-trip**
- 所有 APR 统一从这个标准单位推导出来

否则回测会很容易“看起来很赚钱，其实只是单位没对齐”。

## 7. 对当前 `1m / 3m / 5m / 15m` desk 的正确读法
### 7.1 这条 alpha 服务短周期，但不是逐根 1m 主信号
更诚实的拆法应该是：
- **raw alpha 层**：同币跨 venue funding differential
- **event layer**：围绕 funding settlement window 更新 opportunity
- **`15m/5m` admission 层**：检查 spread 是否仍在、盘口深度是否够、basis 是否没突然反向
- **`1m/3m` execution 层**：分腿同步、减冲击、避免 legging

也就是说：
- 它当然能服务 `1m / 3m / 5m / 15m`
- 但方式不是“每根 1m 给方向”
- 而是“每个 funding pocket 给你一个 carry trade 候选，然后用更细频率把它执行得像样”

### 7.2 它和近期 raw alpha 素材池的关系
这条线和最近 desk 的 accumulation 是互补的：
- 不是继续围绕 breakout/pullback 内循环；
- 也不是只补一个 shared gate；
- 它补的是 **carry / relative-value** 家族里更 executable 的一支。

而且它的价值不在“Funding carry 这个词新不新”，而在：
**把 funding carry 的真正门槛——费用壳、venue 可靠性、滚动建仓——写得很直白。**

## 8. 策略拆解（按 desk 口径重述）
- **方向属性**：market-neutral / relative-value / stat-arb
- **基础 alpha**：short highest-positive-funding venue, long lowest/negative-funding venue（先统一标准 funding sign）
- **filter / veto**：min liquidity、exchange reliability、fee coverage、unit-consistent spread threshold、basis / mark-price 异常过滤
- **risk / sizing**：先小仓试探，底仓分 `3` 批构建；盈利后才允许加仓；总仓上限 `50%`
- **exit / overlay**：coverage 消失、spread 收敛、hold timeout、breakeven + trailing stop
- **成本**：不能只看 fee table；还要看 legging risk、滑点、提款/资金调拨约束、不同 venue 的执行可靠性

## 9. 最小可复现实验（下一步怎么测）
### 9.1 研究假设
**H1：** 同币跨 venue funding differential 在 alt-heavy、流动性尚可的币上，仍能形成可交易的 carry pocket。  
**H2：** 真正决定这条 alpha 能不能活下来的，不是 raw spread 本身，而是 `fee coverage gate`。  
**H3：** 在统一符号和单位后，很多 headline 高 APR 机会会被费用壳和执行壳大幅筛掉。

### 9.2 数据源、公开性、更新频率
- **数据源**：Gate / Bitget / Aster / OKX 的公开 funding / ticker / instrument 接口
- **公开性**：公开可得
- **更新频率**：行情可做到分钟级；funding 通常围绕 `8h` 结算更新；机会扫描可按 `1m~5m` refresh
- **最小可复现实验口径**：
  - 标的：同币跨 venue perpetual
  - 频率：`15m` 做机会状态，`5m` 做 admission，`1m/3m` 做执行模拟
  - 单位：全部转成 `bps per settlement`

### 9.3 first-pass 实验设计
先不要卷复杂优化，第一轮只跑三组：

1. **A：raw spread only**
   - 每次 funding 前后更新 richest/cheapest venue pair
   - long cheapest, short richest
   - 持有 `1` 次结算

2. **B：raw spread + fee coverage gate**
   - 只有当 `net funding income - round-trip cost > 0`
   - 且 `coverage > 0 / 30% / 50%` 三档门槛时才进

3. **C：B + rolling build / profit protection**
   - 底仓三批建
   - 盈利后才加仓
   - breakeven / trailing stop 保护退出

统一比较：
- gross PnL
- after-cost PnL
- hit ratio
- average holding settlements
- leg divergence
- max adverse excursion
- 被 gate 筛掉的机会比例

### 9.4 先测什么，不先测什么
**先测：**
- funding sign 是否统一正确
- spread 单位是否一致
- fee gate 之后还剩多少真实机会
- 小票机会是否只是看起来 APR 高、实际深度不够

**先不测：**
- 复杂 Bayesian 参数优化
- 太花的 AI ranking
- 一上来跑几十个 venue 组合
- 直接把 README 里的 theoretical APR 当目标函数

### 9.5 建议的第一刀参数
- hold：`1 / 2` 个 funding settlements
- fee ladder：`10 / 20 / 35 bps round-trip`
- coverage gate：`0 / 30% / 50%`
- depth gate：单腿最小可成交名义 `5k / 10k / 25k USDT`
- refresh：`15m` 状态刷新 + `5m` 下单检查

## 10. 风险与限制
1. **repo 的收益展示偏 showcase，不是标准化回测。**
2. **小票 funding carry 很容易被执行细节吃掉。** headline APR 再高，腿没法同步就没意义。
3. **sign / unit consistency 是本轮最大工程风险。** 不先修这两个，后面的“优化”都不可信。
4. **跨 venue carry 有额外 operational risk。** 包括 API 稳定性、资金调拨、单边爆仓、仓位不同步、提现延迟等。
5. **这条 alpha 更像 pocket，不像 always-on。** 从 fee coverage 的阈值就能看出来，它天然更依赖高离散窗口。

## 11. 一句话结论
**如果这轮只拿走一件事，我会拿走这句：跨 venue funding carry 当然还是 raw alpha，但真正值得 desk 先复现的，不是“谁 funding 高就冲谁”，而是“统一 funding 符号与单位后，只做那些 `spread 足够厚、费用壳真能覆盖、venue 也够可靠` 的 pocket carry”。**