# 别把这份 2026 新 repo 只读成“网格 bot”：对 short-cycle desk，更该先测的是「adaptive average 偏离 × 分层 envelope 入场 × 回归中线出场」这条完整 mean reversion raw alpha
- 时间：2026-04-01 14:46 UTC
- 类型：2026 GitHub 新仓库 source audit（`README.md` + `src/strategy.py` + `src/backtester.py` + `src/risk_manager.py` + `config/config.yaml`）
- 主题类型：raw alpha
- 基础 alpha：价格短时偏离自适应均值后，存在向均值回归的倾向；越深的偏离允许分层加仓，盈利目标不是猜反转大底，而是吃“回到均值”这段路。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/envelope/sma/ema/donchian/midline-exit/layered-entry/circuit-breaker/crypto/kraken-futures/binance/okx/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：2026 GitHub repo source audit（工程主证据）

## 1. 这次看了什么
### 一句话核心结论
**这轮最值得拿走的，不是 repo 默认那组 7%/11%/14% 的参数，而是它把“均值回归”写成了一条很完整、很诚实的策略骨架：`偏离均值 → 分层进场 → 回归均值出场 → 会话级熔断`。**

### 一句话它是怎么证明的
**证明方式不是论文统计，而是源码把 alpha、加仓、出场、手续费、回测、session 风控都明确写死了：可以直接复刻、直接改成我们自己的 5m/15m 版本。**

## 2. base alpha 是什么
这次的 **base alpha 很清楚**，不是 overlay 冒充 alpha。

核心就是：
1. 先用 `SMA / EMA / Donchian midline` 定义一个短期“公允均值”；
2. 价格如果离这个均值太远，默认把它当成 **短时 overshoot**；
3. 不追求吃整段反转，只吃 **“回到均值”** 这段最朴素的 mean reversion；
4. 如果偏离继续扩大，用更深的 envelope 做 **第二层/第三层分批进场**，而不是第一枪就 all-in。

所以它属于 **single-asset mean reversion**，不是 grid，也不是纯风控层。

## 3. 为什么这轮值得写
- 当前 desk 已经积累了不少 trend / breakout / carry / pairs 素材；这份 repo 补的是一条**可以独立成完整策略**的单币均值回归骨架。
- 它对当前 backlog 很友好：**alpha 本体、仓位分层、出场逻辑、session 熔断** 都是可单拆组件。
- 它很适合做 **5m / 15m first verdict**：不需要外部数据，不需要复杂特征，拿 OHLCV 就能跑。

## 4. 来源信息
### 主工程来源
- **Author / Repo owner：** Anthony Grant（GitHub: `grantad`）
- **Year：** 2026
- **Title：** `crypto-bot`
- **Repo URL：** <https://github.com/grantad/crypto-bot>
- **Readable URL：** <https://github.com/grantad/crypto-bot>
- **关键文件：**
  - `src/strategy.py`
  - `src/backtester.py`
  - `src/risk_manager.py`
  - `config/config.yaml`

## 5. repo 真正给了什么可复用组件
### 5.1 Entry：偏离均值就开，但按层进
`src/strategy.py` 写得很直白：
- 先算平均线：`SMA / EMA / Donchian` 三选一；
- 再按配置生成多层 envelope；
- `low <= lower_band` 触发 long，`high >= upper_band` 触发 short；
- 已有仓位时，如果继续打到更深一层 band，就触发 **additional entries**。

这等于把“越偏离越敢接/越敢空”的逻辑，做成了**离散可回测的分层状态机**。

### 5.2 Exit：不是拍脑袋止盈，而是回归中线就走
正常止盈非常朴素：
- long：`close >= avg` 平仓；
- short：`close <= avg` 平仓。

这点很重要：**它不幻想抓 V 反转，而是只吃 reversion-to-mid。** 对 short-cycle desk，这比“赌反向趋势成立”诚实得多。

### 5.3 Sizing：天然支持 tranche sizing
仓位不是一次打满，而是按 envelope 层数平均拆分。repo 默认 `envelopes: [0.07, 0.11, 0.14]`，等于最多三层。对我们更有价值的不是默认百分比，而是**三层 capital ladder** 这个结构本身。

### 5.4 Risk：源码里已经有 session circuit breaker
`src/risk_manager.py` 不是装饰：它会按 session 跟踪
- 最大亏损比例
- 最大交易笔数
- 最大亏损笔数
- 最大连续亏损

默认配置里甚至写了：
- `max_loss_pct = 10%`
- `max_trades = 50`
- `max_losing_trades = 15`
- `max_consecutive_losses = 5`

这非常适合我们 desk 拿来做 **mean reversion fail-fast 防爆壳**。

## 6. desk 化拆解
## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产
- 基础 alpha：价格偏离短期均值后的回归
- regime：优先在非单边失控、非 news shock、非持续挤仓环境里启用
- filter / veto：高趋势强度 veto、极端放量单边 veto、事件时段 veto
- risk / sizing / execution overlay：三层分批进场、会话熔断、max hold、成本分档

## 7. 3 个最值得记住的硬信息
1. repo 支持 **3 种均值定义**：`SMA / EMA / Donchian midline`；
2. repo 默认 BTC/ETH 配置都是 **3 层 envelope**，并且支持多次加仓；
3. backtester 明确计入了 **开仓费 2 bps、平仓费 5 bps** 的 fee hook，说明它不是完全无成本的玩具骨架。

## 8. 和当前 1m / 3m / 5m / 15m 的关系
这条线最适合先落在 **5m / 15m**：
- `15m` 用来做 first verdict，噪音没那么夸张；
- `5m` 用来测试 band 是否需要更窄、更快；
- `1m / 3m` 可以作为后续执行层，不建议一上来就拿最细频率硬做，因为 mean reversion 很容易被手续费和连续滑点吃死。

要特别诚实的一点是：repo 默认 `7% / 11% / 14%` 的 envelope 对短周期 crypto 来说 **明显偏慢、偏宽**。**该抄的是结构，不是默认参数。**

## 9. 可复刻的最小实验
### 实验 A：15m 单币分层均值回归 first verdict
- **标的：** BTC / ETH / SOL perpetual
- **均值：** `EMA(24)` 与 `Donchian midline(24)` 做对照
- **band 定义：** 不直接抄固定 7%/11%/14%，改成 `ATR/close` 或 rolling sigma 缩放的 3 层 band
- **入场：** 触碰 band1 开 1/3，band2 再开 1/3，band3 最后 1/3
- **出场：** close 回到 midline；或 `max_hold = 8~12 bars`
- **止损：** 平均持仓价再外扩 `1.0~1.5 × ATR`
- **成本：** round-trip 4 / 8 / 12 bps 三档

### 实验 B：band 宽度是不是 alpha 本体
做 ablation：
1. 固定百分比 band
2. ATR-scaled band
3. rolling sigma band

这能直接回答：**真正有效的是“离均值多远”这个量纲，还是 repo 默认的固定百分比写法。**

## 10. 下一步怎么测
1. **先跑 15m first verdict**：BTC / ETH / SOL，比较 `EMA midline` vs `Donchian midline`。
2. **只做最小参数梯子**：`period = 16 / 24 / 32`，band 用 `0.75 / 1.25 / 1.75 × ATR%`。
3. **先看三件事**：after-cost return、MDD、trade count；若交易数太少，就别急着说它“稳”。
4. **再看分层加仓是否真的有增量**：比较 single-entry vs 3-layer entry。
5. 如果 15m 可活，再把 admission 压到 5m；如果 15m 都不活，就别往 1m/3m 继续美化。

## 11. 这条线最容易错在哪
- **把它误读成网格 bot**：它本体不是“无脑逢跌买”，而是有中线、有退出、有熔断的 mean reversion。
- **照抄默认 7%/11%/14% 参数**：那更像 repo 作者自己的交易节奏，不像短周期 desk 的 honest baseline。
- **忽略趋势失控时的左侧风险**：均值回归最怕单边 news shock / liquidation cascade。
- **只看胜率不看尾部**：这种策略常见问题不是胜率低，而是少数几次连续失控把前面的小盈利吞掉。

## 12. 对当前项目的直接意义
这条线值得进研究池，因为它满足当前优先级最高那档：
- **主题类型：raw alpha**
- **基础 alpha 清楚**
- **可独立复现**
- **可直接落地完整策略**

如果要一句话概括：**这不是“再看一个均值回归概念”，而是拿到了一份能直接拆成 entry / exit / sizing / risk / cost 的单币 raw alpha skeleton。**
