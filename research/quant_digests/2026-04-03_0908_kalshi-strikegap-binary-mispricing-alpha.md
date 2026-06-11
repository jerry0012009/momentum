# 别把这份 2026 Kalshi 新 repo 只读成预测市场工具链：对 short-cycle desk，更该先测的是「spot-trend × strike-gap × binary-mid mispricing」这条完整 raw alpha

- 时间：2026-04-03 09:08 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `backtester.py` + `train.py` + `data/sample_features.csv`）+ Kalshi / Coinbase 公共数据路径
- 主题标签：raw-alpha/cross-market/relative-value/prediction-market/kalshi/coinbase/15m/binary-probability/spot-trend/price-vs-strike/orderbook/kelly/fixed-expiry/1m/3m/5m/15m/repo/public-data/external-data/cost
- 证据类型：repo source + sample dataset + official public data docs（repo-based）

- 主题类型：raw alpha
- 基础 alpha：**Coinbase 现货趋势 + 当前价相对 15m 开盘参考价（strike/floor）的位置 + Kalshi 盘口状态，能更快估出本期 YES 的公平概率；当这个公平概率与 Kalshi 当前二元合约中价出现足够大偏离时，就交易该偏离的回补。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这轮看的是一个 **2026-02-28 创建** 的小型新仓库：`kapelame/kalshi-crypto-bot`（GitHub 目前约 **3 stars**，但代码很短、可读、可直接拆策略）。

repo headline 写的是 **Kalshi 15-minute crypto prediction market trading framework**。表面上它更像一个“数据采集 + 回测 + paper trader + dashboard”的壳子，而且 README 还明确说 live trader 里的 `your_strategy()` 是空的。

但真正值得 desk intake 的，不是“框架已经能下单”，而是：

1. 它把 **crypto 15m hard-expiry binary market** 的一整套工程壳子都搭好了；
2. `backtester.py` 里其实已经写出一条 **可独立复现的 raw alpha 骨架**，不是纯空壳；
3. 这条骨架的本体不是宏观赔率解释，也不是慢频 gate，而是 **`fair probability - quoted probability`** 的可交易偏离。

翻成人话：
**别把它看成“Kalshi 工具箱”。对我们更重要的是：它已经把一条 15m 二元合约 mispricing 策略，拆成了 signal / entry / sizing / fee / risk 的完整骨架。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这轮的 base alpha 很清楚：

> **外部现货价格路径与当前合约参考价（floor strike）共同决定“这 15 分钟最终涨/跌”的公平概率；而 Kalshi 的当前合约中价并不会每一秒都完全跟上这条公平概率，所以会留下一个可交易的二元错价。**

因此它不是：
- filter；
- regime gate；
- 纯 execution overlay；
- 也不是“prediction market 解释文”。

它是一条可以单独站住的 **cross-market / binary-probability / fixed-expiry raw alpha**。

## 3. 为什么这轮值得写，而不是继续补第 N 条 shape/filter
结合当前文档与最近 digest 节奏，这轮有三点价值：

1. **它仍然是 raw alpha，不是又一层 gate。** 当前 bot7 明显更该继续补可独立下单的 alpha，而不是再堆一个共享过滤器。
2. **它扩了素材池的资产形态。** 最近池子里已经有很多 perp/perp、spot/perp、pairs、cross-sectional、microstructure；这轮补的是 **公开 prediction-marketized crypto alpha**，但仍然保持短周期、可回测、可定义成本。
3. **它比 04-03 02:28 那篇 Kalshi 宏观 gate 更贴近 desk 主线。** 那篇更适合作 volatility regime gate；这轮则是能直接写成完整交易规则的主信号。

如果要再说得更直白一点：
**现在更值得补的是“能直接下注的 15m raw alpha”，而不是继续给现有策略找第 N 个 veto。**

## 4. 最值得记住的硬数据
### 4.1 市场结构与数据频率
README 把交易对象说得很清楚：
- 标的是 **BTC / ETH / SOL / XRP** 四个 `15m` crypto contracts；
- 每个 contract 问的是：**“未来 15 分钟价格会上涨吗？”**
- 结算规则是：**收盘 60 秒均价 >= 开盘 60 秒均价，则 YES 结算**；
- 价格用分表示，`yes_bid=24` 就是大约 `24%` implied probability。

数据采集器默认：
- **每 `2s`** 轮询 Kalshi 市场 + Coinbase 真实价格；
- 样例文件 `data/sample_features.csv` 我直接拉下来核过，实际有 **`2,470` 行、`67` 列**；
- 包含 4 个资产的 `mid / spread / floor_strike / time_to_expiry / real_price / price_vs_strike_pct / ob_imbalance / mom_5s/15s/30s` 等字段。

### 4.2 repo 已经给出明确 risk shell，不是“以后再想”
`backtester.py` 的默认风控参数很具体：
- 初始 bankroll：**`$100`**
- 单笔最大：**`5%` bankroll**
- 总敞口上限：**`15%` bankroll**
- 同方向最多：**`2` 个资产**
- 日亏损熔断：**`-15%`**
- 最小 edge：**`4%`**
- 只交易中价在 **`0.25~0.75`** 的合约
- 只在距离结算 **`180~700s`** 的窗口入场
- 最大可接受 spread：**`4c`**
- Kelly fraction：**`15%`**

这很关键，因为它说明：
**这不是“先拍方向、风控以后再补”的想法单；它已经是一条完整策略壳。**

### 4.3 fee model 与 sample spread 也足够具体
repo 使用 Kalshi 官方风格的 fee 近似：
- taker：`ceil(0.07 * contracts * P * (1-P) * 100) / 100`
- maker：`ceil(0.0175 * contracts * P * (1-P) * 100) / 100`

这意味着在 `P=0.5` 附近，单合约手续费最高：
- taker 大约 **`$0.02/contract`**
- maker 大约 **`$0.01/contract`**

我顺手看了 sample 数据里的 spread：
- BTC `spread` 均值约 **`1.59c`**，90 分位约 **`3c`**
- ETH 均值约 **`1.83c`**，90 分位约 **`3c`**
- SOL 均值约 **`2.07c`**，90 分位约 **`3c`**
- XRP 均值约 **`2.33c`**，90 分位约 **`4c`**

所以 repo 的 `max_spread = 4c` 并不是随便拍出来的，它大致对应了 sample 里“还能交易、但已经接近宽价尾部”的边界。

## 5. repo 真正值得拿走的，不是框架，而是概率错价 skeleton
### 5.1 规则策略已经写出来了
`backtester.py` 里的 `rule_strategy()` 实际就是这条 alpha 的第一版：

- 信号 1：过去 **15m** 现货趋势
- 信号 2：过去 **30m** 现货趋势
- 信号 3：当前 `price_vs_strike_pct`
- 信号 4：最近几个结算周期的 YES/NO 偏向
- 信号 5：盘口 `ob_imbalance`

作者给的组合权重甚至都写死了：
- `trend_15m * 5`
- `trend_30m * 3`
- `price_vs_strike_pct * time_factor * 2`
- `settlement_bias`
- `ob_imbalance * 0.01`

然后把综合信号通过 `tanh` 映射成一个 `estimated_p`，再直接和市场中价 `mid` 比：
- `estimated_p > mid` → 买 YES
- `estimated_p < mid` → 买 NO
- edge 不够厚就不交易

这就是一条完整的 **`fair probability - market mid`** raw alpha。

### 5.2 ML 版本只是同一 alpha 的升级壳，不是另一条本体
`train.py` / `backtester.py` 里的 ML 版本，本质上没有改 base alpha，只是把公平概率估计器从规则版换成：
- **XGBoost**（若可用）
- 或 sklearn **GradientBoosting** fallback

训练字段大约 **14 个核心特征**，包括：
- `mid`
- `spread`
- `time_to_expiry`
- `time_to_expiry_pct`
- `ob_imbalance`
- `price_vs_strike_pct`
- `volume`
- `oi`
- `mom_5s / 15s / 30s`
- `btc_mid_ctx`
- `btc_lead`
- `mid_decisiveness`

而且作者评估口径也比较老实：
- `accuracy`
- `Brier score`
- `calibration`
- `edge analysis`

这对我们有个很重要的启发：
**第一轮根本不需要上复杂模型；只要先验证 `estimated_p - mid` 是否在 edge decile 上单调变好，就足以判断这条 alpha 本体值不值得继续。**

### 5.3 它和上一轮 Polymarket raw alpha 不是同一件事
虽然都属于 prediction market / binary 交易，但这轮跟 04-02 那篇 Polymarket digest 不完全一样：

- Polymarket 那条更偏 **Binance 快腿冲击 → 慢腿 quoted probability 补动**；
- Kalshi 这条更像 **开盘参考价锚定的 15m hard-expiry event contract**；
- 它强调的是：**“离当前 strike 还有多远 + 现在剩多少时间 + 盘口怎么报价”**，而不只是跨市场快慢腿。

所以这轮更适合作为一个单独的 raw alpha intake，而不是重复写 prediction-market lead-lag。

## 6. 3.5 策略拆解（必填）
- **方向属性：** cross-market / binary-probability / fixed-expiry / relative-value
- **基础 alpha：** 外部现货趋势与 strike-gap 对 15m YES 概率的估计，比当前 Kalshi mid 更快或更准
- **regime：** 中价不太偏（`25%~75%`）、时间还够（`180~700s`）、spread 不太宽时更值得开机
- **filter / veto：** 宽 spread veto、临近结算 veto、已有持仓 veto、同方向过多 veto、熔断 veto
- **risk / sizing / execution overlay：** Kelly fraction、单笔 5%、总敞口 15%、maker/taker fee、同向资产数限制

## 7. 和当前 `1m / 3m / 5m / 15m` 的关系
### 7.1 它天然是 `15m` 主信号
这条线的交易载体本身就是 **15m binary contract**，所以：
- `15m` 是主持有期 / 结算时钟 / alpha 本体；
- `5m` 适合拿来重写 rule signal（例如 `ret_5m`, `ret_15m`, `ret_30m`）；
- `3m / 1m` 更适合做 execution timing、edge persistence、二次确认。

### 7.2 对 perp/spot desk 也有迁移价值
即使最后不下 Kalshi，这条材料也有 desk 价值，因为它等价于在问：

> **“当一个 hard-expiry 概率市场吸收 crypto 现货信息不够快时，能不能把这份滞后反过来当外部 price discovery 载体？”**

这层读法后面可迁移到：
- Polymarket / Kalshi / 其他 event contracts
- ETF intraday binary framing
- funding event / listing event / macro event 赔率市场
- 甚至把 binary fair-probability 当作 perp 短线方向的外部 filter 或 confidence scaler

但这轮要坚持一个边界：
**本篇主 digest 讨论的是 raw alpha 本体，不是把它降级成 filter。**

## 8. 数据源、公开性、更新频率、最小可复现实验口径
### 8.1 数据源
- **Kalshi market/orderbook data**：公开可拉，无需 auth 即可做行情采集
- **Kalshi trading/account API**：下单才需要 key
- **Coinbase spot price**：公开可拿，repo 已接线
- **sample dataset**：repo 自带 `sample_features.csv`

### 8.2 公开性
- 行情层：**公开可得**
- 下单层：需要账户与 API key
- 对我们当前研究最重要的行情 / 样本 /回测层，并不依赖私有 feed

### 8.3 更新频率
- repo collector 默认 **每 `2s`** 采集一次
- contract 本身 **每 `15m`** 一个新周期
- `time_to_expiry` 是秒级倒计时，因此非常适合做短周期硬时钟实验

### 8.4 最小可复现实验口径
第一轮可以先不碰 live trading，只做一个 honest baseline：

1. 资产：`BTC / ETH / SOL / XRP`
2. 样本：repo sample + 自己再抓 `2~7` 天新数据
3. 特征：
   - `ret_1m / 3m / 5m / 15m`
   - `price_vs_strike_pct`
   - `ob_imbalance`
   - `spread`
   - `time_to_expiry`
4. 标签：本期 YES/NO 结算结果
5. 规则：
   - 先估 `p_fair`
   - 再看 `edge = p_fair - mid`
   - 扣 spread + fee 后看 decile monotonicity
6. 执行：必须 one-sample lag，不能 same-tick 幻觉成交

## 9. 下一步怎么测
### 最小实验 1：先把 repo 的 5s/15s/30s 特征改写成 desk 常用 `1m / 3m / 5m`
不要直接照搬 5 秒级 mom。
第一步更适合做：
- `ret_1m`
- `ret_3m`
- `ret_5m`
- `ret_15m`
- `price_vs_strike_pct`
- `spread`
- `time_to_expiry`

看 edge decile 是否仍然单调。

### 最小实验 2：把 `price_vs_strike_pct` 和外部趋势拆开做 ablation
至少分 4 组：
1. 只用 `price_vs_strike_pct`
2. 只用现货趋势
3. `price_vs_strike_pct + 现货趋势`
4. 再加 `ob_imbalance`

要回答的核心问题是：
**真正的 alpha 是“离 strike 多远”本身，还是“外部价格趋势告诉你它会不会继续越过 strike”？**

### 最小实验 3：先做 `time_to_expiry bucket`
把样本切成：
- `> 10m`
- `5~10m`
- `< 5m`

大概率 edge 不会均匀分布在整段生命周期里。
如果只有某个 bucket 存活，就别假装它是全时段 alpha。

### 最小实验 4：先用 maker-ish / taker-ish 两套成本一起压
这类 binary 市场很容易死在成本上，所以必须一开始就给：
- maker-ish
- taker-ish
- 宽 spread veto / 无 veto

三组同时看。

### 最小实验 5：确认这条线能不能服务现有 crypto desk
如果 Kalshi 盘口容量太薄，就再做一版映射实验：
- 把 `Kalshi fair-probability error` 当作外部信号；
- 检查它对 Binance perp 下一根 `1m / 3m / 5m` return 有没有信息增量。

这样就算 Kalshi 自身容量一般，它也可能变成一个 **外部 alpha sensor**。

## 10. 风险与保留意见
1. **repo 规模很小。** 只有几个 stars，不能因为它是新仓库就自动抬成高置信 production 候选。
2. **live trader 主策略其实留空。** 所以这轮真正能 intake 的，是 backtester 里那条 rule/ML probability alpha，而不是 README 里承诺的完整 live 策略。
3. **binary 市场容量与滑点可能很伤。** 即使 sample spread 不离谱，真实成交深度仍可能限制容量。
4. **硬结算结构会放大 late-entry 风险。** 临近结算的错误成交，不像 perp 那样还能慢慢磨回来。
5. **样本还不够长。** repo sample 只有 `2470` 行，明显不够给 production verdict；它更像一个“今天就能开工”的 starter kit。

所以我对它的定位是：
**高可复现度的 raw alpha skeleton，适合先做 first verdict；是否能进实盘池，要靠更长样本与 cost ladder 决定。**

## 11. 来源
### 11.1 主来源（repo）
- **Author / Maintainer**：`kapelame`
- **Year**：2026
- **Title**：*Kalshi Trading Framework* / `kalshi-crypto-bot`
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：<https://github.com/kapelame/kalshi-crypto-bot>
- **Repo URL**：<https://github.com/kapelame/kalshi-crypto-bot>
- **GitHub API metadata**：<https://api.github.com/repos/kapelame/kalshi-crypto-bot>

### 11.2 公共数据 / 文档
- **Kalshi API Reference**：<https://trading-api.readme.io/reference/getting-started>
- **Kalshi exchange**：<https://kalshi.com>
- **Coinbase Exchange API docs**：<https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductcandles>

### 11.3 直接审阅文件
- `README.md`：<https://raw.githubusercontent.com/kapelame/kalshi-crypto-bot/main/README.md>
- `backtester.py`：<https://raw.githubusercontent.com/kapelame/kalshi-crypto-bot/main/backtester.py>
- `train.py`：<https://raw.githubusercontent.com/kapelame/kalshi-crypto-bot/main/train.py>
- `data/sample_features.csv`：<https://raw.githubusercontent.com/kapelame/kalshi-crypto-bot/main/data/sample_features.csv>

## 12. 一句话结论
**这份 2026 Kalshi repo 最值钱的不是“预测市场基础设施”，而是它已经把一条可快速复现的 15m raw alpha 摆在桌上：`外部 spot trend + strike gap -> fair YES probability`，再去交易 `fair probability - market mid` 的回补。先做 cost-first 的 first verdict，很值得。**
