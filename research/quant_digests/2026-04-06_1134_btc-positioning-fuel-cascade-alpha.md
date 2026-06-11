# 别把 Binance long/short ratio 只当情绪温度计：对 short-cycle desk，更该先测「crowd-positioning fuel-cascade × 13pp fuel exit」这条完整 BTC perp raw alpha

- 时间：2026-04-06 11:34 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + README research monograph + Binance Futures public endpoint live probe）
- 主题类型：raw alpha
- 基础 alpha：**当 Binance `top/global long-short account ratio` 与 `open interest` 在 `5m` 上共同显示“同侧拥挤但尚未触发”“failed pump 后 trapped side 增加”或“强平 OI flush 已接近结束”时，后续 BTC perp 价格会通过 squeeze、cascade 或 forced-liquidation bounce 的机械过程释放拥挤；据此做 directional 交易，并用 `avgLong` 相对入场位的 `13pp fuel shift` 或固定 `24h` 均值回归退出。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/btc/perpetual-futures/positioning/top-trader-retail-long-short/open-interest/liquidation-cascade/squeeze/mean-reversion/fuel-exit/5m/public-data/repo/cost/risk
- 证据类型：repo README 研究长文 + GitHub API metadata + Binance public endpoints live availability check

## 1. 这次看了什么
这轮主材料不是论文，而是一份刚发布不久、但已经把规则、阈值、指标和验证口径写得很完整的 repo 研究长文：

- **D. Chystiakov (2026), _Positioning-Based Directional Trading on BTC Perpetual Futures: A 733-Day Empirical Study_**
  - 类型：GitHub repo / self-published research monograph
  - Readable URL：<https://github.com/iZonex/trading-strategy>
  - Repo URL：<https://github.com/iZonex/trading-strategy>
  - README raw：<https://raw.githubusercontent.com/iZonex/trading-strategy/main/README.md>
  - DOI：N/A
  - Venue：GitHub
  - GitHub metadata：repo `created_at = 2026-04-06T08:28:45Z`，`pushed_at = 2026-04-06T10:17:22Z`

补充的公开数据口径：

- **Binance Futures public data / REST docs**
  - API docs：<https://binance-docs.github.io/apidocs/futures/en/>
  - Public archive：<https://data.binance.vision/>
  - 本轮 live probe 实际打通的 5m 公开接口：
    - <https://fapi.binance.com/futures/data/topLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=5>
    - <https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=5>
    - <https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=5>
    - <https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=5m&limit=5>

我这轮选它，原因很直接：

> **它给的不是又一层 filter，而是一条能直接写成 entry / exit / risk / cost 的 crowd-positioning raw alpha 家族。**

而且它和我们最近已经 intake 过的一串 carry / pairs / microstructure 题目不一样：

- 输入不是 funding、basis、价差或 order book；
- 而是 **谁在 long / short、谁在加速、谁在被挤、OI 是在加载还是在清算**；
- 数据全部来自公开可拿的 Binance 5m 接口与归档。

这让它非常适合进入当前素材池，补上一条此前还没单独讲透的 **public-positioning raw alpha** 路线。

## 2. 先回答：这篇东西的 base alpha 是什么？
### 2.1 base alpha 是清楚的，而且不是 filter
先讲人话：

> **不是“大家看多/看空所以我要反着做”，而是“哪一边已经被挤得太满、但价格还没完全动；或者哪一边刚被强平完，反身性已经快烧完”。**

作者实际上给了 3 种可以拆开测的 base alpha：

1. **极端拥挤 + 静默 = squeeze / cascade 预装填**
   - 例：`avgLong` 极端、`topVel/retVel` 很低、12h price range 很窄；
   - 解读：仓位已经偏到一边，但价格还没真正点火；
   - 交易：跟随未来 squeeze / cascade 方向。

2. **failed pump + divergence 扩大 = trapped side cascade**
   - 例：价格刚 pump 失败，retail 继续接，top 没有跟；
   - 解读：错误一侧越补越多，未来更容易被连锁挤出；
   - 交易：顺着 trapped side 被清算的方向做。

3. **12h OI flush 完成 + price 还在 low 附近 = forced-liquidation bounce**
   - 例：OI 12h 大幅下降，但近 4h flush 速度放缓；
   - 解读：被迫卖的人大多已经卖掉，剩余卖压衰减；
   - 交易：做一个固定时间窗的反弹均值回归。

所以这不是“把 long/short ratio 当情绪温度计”的 filter；它本体就是一套 **directional raw alpha**。

### 2.2 一句话核心结论
> **Binance 的 crowd positioning 不是慢情绪指标，而是可以直接刻画“清算燃料是否已装满 / 是否快烧完”的交易输入。**

### 2.3 它是怎么证明这个结论的
> **作者用 733 天、约 21 万根 `5m` BTC perp 数据，把 top/global long-short ratio、OI 与价格拼成 8 个子模型，声称得到 290 笔交易、72% 胜率、PF 3.53，并做了时间切分、rolling walk-forward 和 Monte Carlo。**

但这里必须立刻加一句保守话：

- 这是 **repo README 研究长文证据**，不是公开代码已审计结果；
- 当前 repo 主要内容是 `README + figures`，**没有随手可跑的策略代码 / trade log**；
- 所以它值得进研究池，但必须走 **独立复现**，不能把 README 的业绩直接当结论。

## 3. repo 到底给了哪些可复现规则
### 3.1 公开数据口径很干净
作者使用的数据源都能映射到公开口径：

- `topLongShortAccountRatio`（top traders）
- `globalLongShortAccountRatio`（global / retail）
- `openInterestHist`
- `klines`

并定义了几组足够直接的指标：

- `avgLong = (topLong + retLong) / 2`
- `div = retLong - topLong`
- `topVel_h = topLong(t) - topLong(t-h)`
- `retVel_h = retLong(t) - retLong(t-h)`
- `fuelShift = |avgLong(t) - avgLong(entry)|`
- `avgLShift_24 = avgLong(t) - avgLong(t-24h)`

这些定义都够朴素，复现门槛不高。

### 3.2 它最值得 first test 的，不是一次抄全 8 个模型，而是先拆 3 个最清楚的壳
#### A. PB14-L：极端空仓挤压 LONG
作者给的条件大致是：

- `avgLong < 48%`
- `|topVel_24| < 1.5pp`
- `|retVel_12| < 2.5pp`
- `12h range < 2.5%`
- `OI_USD <= 10B`

翻成人话：

> **两边都已经偏 short，但最近又都没怎么动，价格也没怎么动，说明 barrel 已经装弹但还没开火；任何向上触发都可能变成 squeeze。**

repo 自报：

- `111` 笔交易
- `76%` 胜率
- 扩展样本 `PnL +205%`

#### B. PB12：拥挤多头 first-weakness SHORT
作者给的核心条件：

- `avgLong > 65%` 区域内
- `div < -5%`（top 比 retail 更 long）
- `topVel_24 > -2pp`（top 还没明显减仓）
- `ΔP_4h < -0.3%`
- `ΔOI_12h > -3%`
- `topLong > 60%`

翻成人话：

> **真正危险的不是“大家都多”，而是“聪明钱也很重、多头先出现一点点弱化，但还没正式撤退”。这时如果外部卖压来一下，容易触发连锁踩踏。**

repo 自报：

- 合并口径约 `53` 笔交易
- 总体 `76%` 胜率
- `PnL +48%`

#### C. FLIQ-L：OI flush 完成后的 24h bounce
这是我觉得对 desk 很实用、而且最快能做出 first verdict 的均值回归分支：

- `ΔOI_12h < -3%`
- `ΔOI_4h > -0.5%`（flush 在减速，不是继续恶化）
- `ΔP_12h < -2%`
- 价格仍贴近 12h low

翻成人话：

> **不是“跌多了就买”，而是“被迫平仓已经发生，而且强平速度明显在衰减，这时去抓清算后的机械反弹”。**

repo 自报：

- `23` 笔交易
- `78%` 胜率
- `PF 12.85`
- `PnL +47.1%`
- **退出不是 fuel exit，而是固定 `24h` 持有**

这点很关键：

> **同一份 crowd-positioning 数据，可以同时服务 trend/cascade alpha 和 mean-reversion alpha；但 exit 不能乱共用。**

### 3.3 它最值得借的，不只是 entry，还有 exit 思路
作者最有意思的贡献，不一定是 entry 本身，而是这个退出逻辑：

- trend / cascade 模型：当 `fuelShift >= 13pp` 时退出
- 保护：`SL 5%`
- 最大持仓：`14d`
- mean-reversion 模型（FLIQ-L）：固定 `24h` 退出

他给出的对比非常值得单独复现：

- `3% trailing stop + 3% SL`：平均每笔 `+1.52%`
- `13pp fuel exit + 5% SL`：平均每笔 `+3.25%`

换句话说，repo 在讲一件对 desk 很重要的事：

> **如果 alpha 的核心是“仓位燃料在释放”，那 exit 也该围绕燃料释放，而不是围绕固定百分比 trailing stop。**

## 4. 为什么它值得进入当前 short-cycle 研究池
### 4.1 它补的是一条新的 raw alpha 家族，不是重复我们最近的 carry / pairs 题
最近 intake 里已经有不少：

- carry / funding / basis
- pairs / relative value
- order-book / microstructure
- breakout / trend shell

这次这条线的区别是：

- 它仍然是 **raw alpha**；
- 但 raw alpha 的输入从价格、价差、book、funding，换成了 **公开 crowd-positioning + OI**；
- 对 desk 来说，这是一个新的“可复现主信号家族”，而不只是辅助确认层。

### 4.2 它和 `1m / 3m / 5m / 15m` 的关系是清楚的
我会把它这样落位：

- **主状态层**：`5m`
  - 因为原始 ratio / OI 数据就是 `5m`
- **执行层**：`1m / 3m`
  - 入场分拆、滑点控制、先后腿同步、触发后 early-fail kill
- **监控层**：`15m`
  - 观察 fuel 是否继续释放、是否进入 no-signal / exhausted 区域

也就是说：

> **不要把它硬伪装成逐根 `1m` 预测器；更合理的读法是“5m 状态引擎 + 1m/3m 执行子层”。**

### 4.3 repo 其实还暗示了一个更大的研究方向
README 最后把 BTC / ETH / SOL 分成三类市场：

- BTC：**Positioning Market**
- ETH：**OI Flow / Mean-Reversion Market**
- SOL：**Cascade / Momentum Market**

我不会把这部分直接当结论，因为没有代码、而且 ETH/SOL 还只是 preliminary；但这至少提示我们：

> **未来 crowd-positioning 这条线不一定只是一条 BTC 单币因子，而可能是一个“按资产微观结构切分”的策略家族。**

## 5. 这份材料最值得复用 / 借鉴 / 学习的地方
### 5.1 值得复用的不是 repo 业绩，而是它的“状态机拆法”
最值得借的，是这 4 步：

1. 先问 **fuel 有没有装满**（extreme positioning）
2. 再问 **有没有人已经开始动**（velocity）
3. 再问 **点火了没有**（price weakness / range break / OI flush deceleration）
4. 最后问 **燃料烧完没有**（fuelShift / fixed mean-reversion horizon）

这是一种非常 desk-friendly 的结构，因为它天然可以拆成：

- `state`
- `trigger`
- `hold`
- `exit`

### 5.2 值得学习的是：trend 与 mean-reversion 用同一组输入，但不共享退出语义
很多 repo 会犯的错，是把同一套 exit 套到所有信号上。
这篇材料相对清醒：

- trend / cascade：看 fuel 是否烧完
- mean-reversion：看 bounce 时间窗是否结束

这对我们当前 desk 非常重要，因为它提醒我们：

> **输入变量可以共用，交易语义不能混。**

### 5.3 值得借鉴的是：先做“机械解释”，再做阈值微调
README 很强调：

- 不是先跑一堆参数，再找最优值；
- 而是先讲清楚：谁在被挤、谁在补仓、谁在逃命、为什么 OI 和 ratio 应该一起看。

这点和当前研究自动化 brief 其实是同方向的：

> **快验证不是瞎试参数，而是先把 `trade on / trade off` 写清楚。**

## 6. 直接给 desk 的最小实验：下一步怎么测
### 6.1 不要一开始就复刻全 8 模型
第一轮最小实验只做 3 个：

1. `PB14-L`：极端短仓静默 squeeze LONG
2. `PB12`：拥挤多头 first-weakness SHORT
3. `FLIQ-L`：12h OI flush 完成后的 24h bounce LONG

原因：

- base alpha 最清楚；
- 数据都公开；
- 语义彼此区分明显；
- 能同时覆盖 trend/cascade 与 mean-reversion 两本书。

### 6.2 最小可复现实验口径
#### 数据
- 标的：`BTCUSDT` perpetual
- bar：`5m`
- 核心输入：
  - `topLongShortAccountRatio`
  - `globalLongShortAccountRatio`
  - `openInterestHist`
  - `klines`
- 样本建议：先拉最近 `180d~365d` 做 first verdict；能补齐 S3 归档后再扩展到作者声称的 `733d`

#### 信号生成
- 每根 `5m` 计算：
  - `avgLong`
  - `div`
  - `topVel_24`
  - `retVel_12`
  - `avgLShift_24`
  - `ΔOI_4h / ΔOI_12h`
  - `12h range`

#### 交易执行
- baseline：`signal close -> next bar open` 进场
- child execution：再做一个 `1m` TWAP / 3-bar VWAP 版本
- 费用：至少跑 `6 / 10 / 14 bps round-trip` 三档
- 资金费：对持有超过 8h 的仓位计入真实 funding

#### 退出
- `PB14-L / PB12`：
  - `fuelShift >= 13pp`
  - 或 `SL 5%`
  - 或 `max hold 14d`
- `FLIQ-L`：
  - 固定 `24h` 平仓

### 6.3 first verdict 最该先看哪几个指标
不要第一天就盯年化收益，先看这 5 个：

1. **方向命中率**：触发后 `4h / 12h / 24h` 的方向是否对
2. **MFE/MAE 分布**：是不是确实存在“燃料释放”特征
3. **entry-to-trigger latency**：信号后多久才开始走
4. **fuel exit vs fixed trailing**：13pp fuel exit 是否真优于普通 trailing stop
5. **cost cliff**：在 `6/10/14bps` 下 edge 剩多少

### 6.4 第二轮再做什么
如果第一轮有 edge，再做 3 个扩展：

- **百分位 / z-score 版本**：把固定阈值改成 rolling percentile，避免阈值过拟合
- **cross-asset portability**：只先测 ETH 的 `OI-flush bounce`，不要一上来照搬全部 BTC 阈值
- **execution veto**：用 `1m` microstructure 信号做入场取消条件，而不是替代主信号

## 7. 风险、盲点与不该先做的事
### 7.1 当前最大问题：证据强，但仍是“source-audited”，不是“code-audited”
必须明确：

- repo 现在更像研究备忘录，不像可运行系统；
- 没有完整代码、trade blotter、参数文件；
- 所以所有漂亮数字都要打折看。

### 7.2 bear-no-divergence 盲点很真实
作者自己也承认：

- 当两边都很 long、但没有明显 divergence 时；
- 真正的下跌可能来自外部卖压、新闻、现货流出；
- positioning 数据本身是看不见这些外生触发的。

这意味着：

> **这条 alpha 不是市场全覆盖系统，而是一条“只覆盖某些可机械解释的挤仓 / 清算事件”的 raw alpha。**

### 7.3 不要先做的事
第一轮先别做：

- 全量 8 模型同时复刻
- 直接外推 ETH / SOL 全家桶
- 直接把 README 的 +828% 当作目标收益
- 用 `1m` 把 ratio 数据重采样成伪高频主信号

这些都太容易把第一轮研究带偏。

## 8. 我的结论
如果只用一句话总结：

> **这份 repo 最值得 intake 的，不是它那串很夸张的总收益数字，而是它把“public crowd positioning → mechanical squeeze/cascade/bounce”写成了一套能直接独立复现的 raw alpha 状态机。**

对当前 desk，我会把它归为：

- **值得进入素材池**：是
- **优先级**：高
- **第一轮复现目标**：`PB14-L + PB12 + FLIQ-L`
- **第一轮口径**：`BTCUSDT 5m state engine + 1m/3m execution child layer`
- **当前证据评级**：`high-idea / medium-evidence`（因为规则清楚、数据公开，但尚无公开代码审计）

只要第一轮验证显示：

- 方向 edge 还在；
- `fuel exit` 不是 README 幻觉；
- 成本后仍有剩余；

这条线就很适合进入下一阶段，作为我们 raw alpha 池里一条和 carry / pairs / breakout 明显不同的 **public-positioning family**。

## 9. 来源链接
- Repo：<https://github.com/iZonex/trading-strategy>
- Raw README：<https://raw.githubusercontent.com/iZonex/trading-strategy/main/README.md>
- Binance Futures API docs：<https://binance-docs.github.io/apidocs/futures/en/>
- Binance Public Data archive：<https://data.binance.vision/>
- Live probe endpoints：
  - <https://fapi.binance.com/futures/data/topLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=5>
  - <https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=5m&limit=5>
  - <https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=5>
  - <https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=5m&limit=5>
