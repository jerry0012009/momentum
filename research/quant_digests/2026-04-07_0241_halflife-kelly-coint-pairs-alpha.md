# 别把 pairs 继续写成固定 z-score 教材：这份 2026 新 repo 更该先测的是「4-test pair admission × half-life-bounded spread MR × fractional-Kelly shell」

- 时间：2026-04-07 02:41 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `cointegration.py` + `signals.py` + `sizing.py` + `backtest.py`）
- 主题类型：raw alpha
- 基础 alpha：**先用 `Engle-Granger + Johansen + residual ADF + OU half-life` 找到“真的会回”的 crypto 配对，再在价差 `z-score` 偏离足够大时做 spread mean reversion；它的 alpha 本体不是 Kelly，不是 kill-switch，而是“通过多重配对准入后留下的可交易均值回复价差”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/engle-granger/johansen/adf/ou-halflife/fractional-kelly/kill-switch/kraken/binance/15m/5m/3m/1m/repo/public-data/cost/risk
- 证据类型：repo 源码直读 + repo 内结果表 + 公开交易所 OHLC 数据可得性

## 1. 这次看了什么
这轮我选的是一个**很新、而且能直接拆成完整策略壳**的仓库：

- **Aman Syed (2026), _Stat-Arb-in-Crypto_**
- Repo URL：<https://github.com/aman3599/Stat-Arb-in-Crypto>
- 数据源：Kraken public OHLC（仓库声明无需 API key）

我选它，不是因为“pairs + z-score”这几个词本身有多新，而是因为它把一条 raw alpha 写成了比较完整的 production skeleton：

1. **配对准入**：不是只看一个 cointegration p-value，而是四重筛选；
2. **入场/出场**：`z-score` 明确；
3. **仓位**：有 fractional Kelly；
4. **风险**：有 stop 与 portfolio drawdown kill-switch；
5. **成本**：回测里明确扣了 `7 bps` 成本 + `3 bps` slippage。

一句话说，这不是“pairs 概念介绍”，而是一个已经能让 desk 直接抄出 first replication 的完整模板。

## 2. 先回答：这篇东西的 base alpha 是什么？
先一句话：

> **base alpha = 多重 cointegration 准入后的 spread mean reversion。**

更具体一点：

- 不是“只要两条线看起来像一起走，就做回归”；
- 而是先要求这对资产同时通过：
  - `Engle-Granger`
  - `Johansen trace`
  - residual `ADF`
  - `OU half-life` 落在可交易区间
- 然后才在价差偏离足够大时进场，赌它回到均值。

这点很关键，因为它把很多 desk 上常见的“pairs 直觉”变成了可审计规则：

- **alpha 本体**：spread 会回；
- **admission layer**：不是所有 pair 都值得赌；
- **overlay**：Kelly、成本、kill-switch 只是让这条 alpha 更像可实盘策略。

如果 base alpha 说不清，就只能算 overlay；这份 repo 在这点上是说得清的。

## 3. 核心结论
- **一句话核心结论**：对 short-cycle desk，pairs 值得抄的不是“固定 `z>2` 就开”，而是“先把 pair admission 做严，再交易真正有半衰期约束的 spread”。
- **一句话证明方式**：仓库直接把 `筛 pair → 算 hedge ratio → 生成 z-score 信号 → Kelly sizing → 成本回测` 串成了完整代码路径，并给出配对级结果表。
- 这份 repo 的最值钱处，不是某个超高收益截图，而是它把 **entry / exit / sizing / risk / cost** 五层全放进了同一个最小系统里。
- README 给的结果里，`7` 个通过筛选的 pair 中，`BTC/SOL` 年化收益约 `4.8%`、Sharpe `3.66`、最大回撤仅 `-0.3%`；`XRP/AVAX` 年化收益约 `15.1%`、Calmar `24.2`，说明“高收益 pair”和“高稳健 pair”不一定是同一对。
- 代码里最值得沿用的不是 4H 频率本身，而是 **把 half-life 写成 calendar days、把 bar 长度显式参数化**。这让 4H → 15m / 5m 的迁移更干净：改的是时间尺度，不是瞎改 bar 数。
- 但 repo 也暴露了两个很实在的 source-audit 问题：
  1. `signals.py` 默认 `lookback=30` 实际按 bar 数滚动，而 README 讨论的是 `120` 个 4H bars ≈ `20` 天；**单位口径存在错位风险**；
  2. `Kelly f` 被 `clip(lower=0)`，意味着当 spread 漂移估计为负时，**short-side sizing 会被压成 0**，这不是我们想要的对称 pairs shell。

## 3.5 为什么和当前项目有关
它和当前 `momentum` 主线的关系非常直接，而且是 **raw alpha 素材池** 关系，不是泛泛“可借鉴”：

1. **补 raw alpha 家族缺口**：当前 digest 池虽然已经有不少 pairs / RV 主题，但很多更偏“单一 admission trick”或“某个 threshold 技巧”。这份 repo 的价值在于它把完整 shell 一次性摆齐了。
2. **适合 desk 现阶段**：当前用户明确希望多补可独立复现、可直接落地的主题。这份仓库恰好不是纯 filter，也不是纯综述，而是一条完整可执行的 pairs raw alpha。
3. **有利于 5m / 15m 迁移**：repo 最值得抄的其实是“calendar-time half-life + 明确 cost + 风险壳”，这些都能平移到 Binance / Hyperliquid 的更快数据上。

## 4. 策略拆解（必填）
- 方向属性：**相对价值 / market-neutral / pairs mean reversion**
- 基础 alpha：**通过四重检验后的 cointegrated spread 会向均值回归**
- regime：**只交易 half-life 处于可交易区间的 pair；过快代表 execution risk，过慢代表资本占用太久**
- filter / veto：**EG p-value、Johansen 95% trace、residual ADF、z-score 入场阈值、stop-z、pair 级最小样本长度**
- risk / sizing / execution overlay：**25% fractional Kelly、单 pair 最大 `20%` 资本、回测扣 `10 bps` round-trip（`7 bps` 成本 + `3 bps` slippage）、`25%` portfolio drawdown kill-switch**

## 5. 这套 repo 实际怎么写策略
按源码看，它的主策略壳可以浓缩成下面 5 句：

1. 对每个 pair 做 `log(A) ~ beta * log(B)`，得到 hedge ratio 与 spread；
2. 只保留同时通过 `EG + Johansen + residual ADF + OU half-life` 的 pair；
3. 对 spread 做 rolling z-score：
   - `z < -2` 做 long spread
   - `z > +2` 做 short spread
   - `|z| < 0.5` 平仓
   - `|z| > 3.5` 止损
4. 用 fractional Kelly 决定仓位，但上限 `20%` 资本/对；
5. 回测按实际两腿收益算 PnL，并在 trade day 扣成本；若组合回撤超过 `25%`，直接停机。

这就是它最适合我们 desk 的地方：**不是只有信号，没有风控；也不是只有风控，没有 alpha。**

## 6. 可复刻的最小实验
### 6.1 研究假设
在 `15m` 或 `5m` crypto 数据上，真正值得交易的 pairs alpha，不是“任何价差偏离都回”，而是：

> **只有通过多重配对准入，且 half-life 落在短周期 desk 能接受的资本占用区间时，spread z-score mean reversion 才更像可交易 raw alpha。**

### 6.2 一个可计算定义
建议先做 **Binance USDT perp 或 spot** 的最小迁移版：

- Universe：`BTC, ETH, SOL, XRP, DOGE, ADA, LINK, AVAX, LTC, BCH` 等高流动资产
- Refit 频率：每日或每 `4h` 重算一次 pair admission
- Pair admission：
  - `EG p < 0.15`
  - Johansen trace > 95% critical value
  - residual `ADF p < 0.10`
  - half-life 落在：
    - `15m`：`0.5 ~ 10` 天
    - `5m`：`0.25 ~ 7` 天
- Signal：
  - entry：`|z| >= 2.0`
  - exit：`|z| < 0.5`
  - stop：`|z| > 3.5`

### 6.3 最小回测切口
- 先做：`15m`，过去 `120~180` 天，top-liquid 8~12 币
- 再做：`5m` 稳健性对照
- 评估一定要先上 **固定名义仓位** 版本，再上 **对称化 Kelly / vol-target** 版本；不要一开始就把 sizing 和 alpha 混在一起

### 6.4 最该先看哪 2 个指标
1. **成本后净收益 / trade count / positive pair ratio**：确认它不是只有少数 pair 偶然撑起来；
2. **max drawdown + holding-time 分布**：确认 short-cycle 上的 half-life 约束是不是把“看起来回归、其实拖很久”的 pair 过滤掉了。

### 6.5 我更建议的 first verdict 顺序
1. **先固定仓位**，验证 raw alpha 本体；
2. 再加 **half-life gate**；
3. 最后才加 **对称版 Kelly / vol-target / pair ranking**。

这样能避免把“仓位救了坏信号”错认成 alpha 成立。

## 7. 风险与保留意见
- **样本太短**：README 自己也承认当前结果大约只来自 `~4` 个月样本，这个长度不足以证明 pair 关系稳健。
- **Kraken 4H ≠ Binance 5m/15m**：数据质量、流动性层级、交易成本、资金费率都会变，不能直接照抄收益数字。
- **calendar-time 是优点，也是迁移难点**：如果把 `120` 个 4H bars 机械改成 `120` 个 15m bars，等于把 `20` 天窗口误缩成 `1.25` 天；这是最容易把策略抄坏的地方。
- **Kelly 实现当前不对称**：源码的 `clip(lower=0)` 会让负漂移场景拿不到正常 short-side 尺寸，进入 live 前必须改成对称表达（例如基于 `|mu|` 或直接用 vol-target 壳）。
- **z-score shell 可能拥挤**：pairs 的 alpha 往往死在 admission 之后的 execution、cost 与 relationship breakdown，而不是死在公式看不懂。

## 8. 下一步怎么测
如果只给这轮一个明确行动，我会建议：

> **不要先复刻 repo 的 Kelly；先复刻它的“四重配对准入 + calendar-time half-life + fixed-notional spread z-score shell”。**

更落地一点：

1. 在 Binance `15m` top-liquid perp 上跑 rolling pair admission；
2. 只保留 half-life `0.5~10` 天的 pair；
3. 用固定名义仓位回测 `z-entry / z-exit / z-stop`；
4. 看成本后是否仍有正的 pair ratio；
5. 只有 alpha 本体过关，再试对称化 Kelly 或 vol-target。

这一步如果跑出来，哪怕收益一般，也会给当前 desk 多一类真正能进入后续 admission check 的 **pairs raw alpha skeleton**。

## 9. 来源
### 主来源（repo）
- **Aman Syed. (2026). _Stat-Arb-in-Crypto_. GitHub repository.**
- Repo URL：<https://github.com/aman3599/Stat-Arb-in-Crypto>
- Readable URL：<https://github.com/aman3599/Stat-Arb-in-Crypto>

### 理论地基（repo 中实际使用的方法族）
- **Engle, R. F., & Granger, C. W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica.**
- DOI：<https://doi.org/10.2307/1913236>
- Readable URL：<https://www.jstor.org/stable/1913236>

- **Johansen, S. (1991). _Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models_. Econometrica.**
- DOI：<https://doi.org/10.2307/2938278>
- Readable URL：<https://www.jstor.org/stable/2938278>
