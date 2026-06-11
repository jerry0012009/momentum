# 别把这篇 2021 Ledger 只读成“Bitcoin 行为金融论文”：对 short-cycle desk，更该先测的是「BTC medium-frequency jump-reversal」这条 raw alpha——但 recent Binance 迁移版已明确提示：旧 spot edge 现在只剩极端冲击 pocket

- 时间：2026-04-15 06:48 UTC
- 类型：2021 *Ledger* 论文全文 PDF + Binance Spot / USDⓈ-M `15m/1h/2h/4h` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**BTC 单资产 jump-contrarian mean reversion：当上一根 `1h/2h/4h` bar 出现足够大的单边冲击后，下一根 bar 有统计上更高概率出现反向回吐；对 desk 的落地读法不是“逢跌就抄底”，而是“只在大 shock 后做一根/几根 bar 的反身性回吐”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / mean-reversion / jump-reversal / shock-fade / contrarian / autocorrelation / btc / bitstamp / binance / spot / perpetual / 15m / 1h / 2h / 4h / paper / fulltext / public-data / cost / risk
- 证据类型：open-access paper full PDF + public-data portability probe

## 1. 这次看了什么
主来源是开放获取论文：
- **Author：** Giacomo De Nicola
- **Year：** 2021
- **Title：** *On the Intraday Behavior of Bitcoin*
- **Venue：** *Ledger*
- **DOI：** <https://doi.org/10.5195/LEDGER.2021.213>
- **Readable URL：** <https://ledgerjournal.org/ojs/ledger/article/view/213>
- **PDF URL：** <https://ledgerjournal.org/ojs/ledger/article/download/213/212/1232>
- **Repo URL：** N/A

先把 base alpha 说清楚：

> **这篇东西的 base alpha，不是“crypto 波动大”这种解释，也不是“高波动时少做交易”这种 filter；它的本体就是：BTC 在中频 (`1h/2h/4h`) 出现较大单 bar 冲击后，下一 bar 更容易反向回吐。**

也就是一条很朴素的 **single-asset mean reversion / shock-fade raw alpha**。

## 2. 核心结论
### 2.1 先回答 base alpha
如果只用一句话概括：

> **上一根 bar 涨/跌得越猛，下一根 bar 越可能往反方向吐回来；paper 里最强的不是 `5m` 噪声级 bid-ask bounce，而是 `1h/2h/4h` 这种按常理不该还明显可预测的中频 reversal。**

这不是 regime，也不是 overlay。alpha 本体就是 **shock → next-bar fade**。

### 2.2 paper 里最值钱的不是“Bitcoin 有点反转”，而是中频 shock-fade 的幅度
论文用的是 **Bitstamp BTC/USD `1m` 数据**，样本期 **2015-03 到 2018-06**，再聚合成 `5m / 15m / 30m / 1h / 2h / 4h / 1d`。

先看无条件 lag-1 自相关：
- `1h`：**`-0.0557`**
- `2h`：**`-0.0858`**
- `4h`：**`-0.0564`**
- `1d`：`-0.0071`（不显著）

这已经说明：
- 高频负自相关不稀奇，常常只是微观结构；
- **真正异常的是 `1h/2h/4h` 这种中频还在显著负自相关。**

更关键的是，作者没停在“有点负自相关”，而是继续问：

> **如果只看大跳变（jump / large single-period return），反转会不会更强？**

答案是会，而且强很多。

paper 的条件相关结果里，最亮眼的是：
- `1h`：当上一根达到 `4σ`，下一根相关系数约 **`-0.1483`**；到 `5σ` 约 **`-0.1863`**
- `2h`：当上一根达到 `4σ`，下一根相关系数约 **`-0.2314`**；`5σ` 约 **`-0.3308`**；`6σ` 约 **`-0.4010`**
- `4h`：也有负相关，但稳定度不如 `2h`

也就是说，**paper 里真正值得 intake 的，不是“BTC 有均值回复”这句废话，而是“中频 shock 越极端，下一根 bar 的反向回吐越强”。**

### 2.3 paper 自带了一个完整可实现的最小策略壳
作者没有只做统计显著性，还直接写了一个极简策略：
- 若上一根 bar 大跌且超过阈值，则下一根做多
- 若上一根 bar 大涨且超过阈值，则下一根做空
- 持有 **一个同长度 bar** 后离场

paper 给出的 **未计费** 平均每笔收益：
- `5m`：
  - `4σ` 约 **`+0.14%`**
  - `6σ` 约 **`+0.30%`**
- `1h`：
  - `4σ` 约 **`+0.34%`**
  - `5σ` 约 **`+0.49%`**
  - `6σ` 约 **`+0.58%`**
- `2h`：
  - `4σ` 约 **`+0.74%`**
  - `5σ` 约 **`+1.18%`**
  - `6σ` 约 **`+1.81%`**

作者还给了一个很直白的结论：**小周期虽然看起来也赚钱，但很可能会先死于手续费和 spread；真正更像可交易 pocket 的，是 `1h/2h` 这种中频大冲击后的回吐。**

## 3. 为什么这东西和当前 desk 有直接关系
这轮值得写它，不是因为它“经典”，而是因为它满足我们当前更想补的几件事：

1. **它是 raw alpha，不是解释型摘要。**  
   不需要先借助别的主信号，它本体就是一个可回测的 entry/exit 规则。

2. **它补的是“单资产事件型反转”这块。**  
   最近 intake 里 pairs / relative-value / carry 很多，但这种 **单资产、基于上一根大冲击的 shock-fade** 反而不算密。

3. **它天然能拆成 `1h/2h admission + 15m execution`。**  
   对当前 desk，更合理的落地不是把整篇论文硬翻成“每根 `15m` 都逆势做”，而是：
   - 用 `1h/2h` 定义 shock state
   - 用 `15m` 分 1~4 笔反手建仓
   - 用 `15m` 或 `5m` 做 time stop / fail-fast / microstructure veto

## 4. 对 short-cycle desk 的正确读法
### 4.1 不要把 paper 误读成“5m 反转永远有效”
论文里 `5m/15m` 也有正收益，但作者自己已经提醒：
- 高频负自相关很可能混着 bid-ask bounce / 微观结构效应；
- 真正值得严肃看的，是 `1h/2h/4h`。

所以 desk 化时更合理的表述是：

> **这不是一条“纯 `5m` 主信号”，而是一条“中频 shock admission → 短周期执行”的 raw alpha。**

### 4.2 desk 版最小策略壳
先给一个最小、可直接进回测队列的版本：

- **交易对象：** BTCUSDT（先 spot，再 perp）
- **state / admission clock：** `1h` 和 `2h`
- **execution clock：** `15m`
- **entry：**
  - 若上一根 `1h` / `2h` 收益绝对值超过 rolling `2.5σ ~ 4σ`
  - 且方向向上：下一根 `15m` 开始找反手空
  - 且方向向下：下一根 `15m` 开始找反手多
- **exit：**
  - 默认持有一个母 bar（`1h` shock 就持有 `4 x 15m`；`2h` shock 就持有 `8 x 15m`）
  - 或先碰到回吐目标（如回吐 shock 幅度的 `25%~40%`）
  - 或反向继续扩展超过 fail-fast 阈值即止损
- **sizing：** shock 越大，名义仓位越小；按 realized vol 或 ATR 缩放
- **风险：** news shock、宏观窗口、强趋势延续、perp funding/basis 拖累、薄簿时段冲击成本
- **成本：** taker/maker fee + spread + 滑点 + funding（若走 perp）

## 5. public-data portability probe：这条 old-school edge，2026 还剩多少？
为了避免把 2015-2018 Bitstamp 现象直接神化成今天还能用，我补做了一个很小的 **Binance public-data portability probe**。

### 5.1 数据口径
- **Spot：** Binance `api/v3/klines`
- **Perp：** Binance USDⓈ-M `fapi/v1/klines`
- **标的：** BTCUSDT
- **窗口：** 最近约 `3000` 根 bar
- **频率：** `15m / 1h / 2h / 4h`
- **策略口径：** 若上一根收益为正则下一根做空，若上一根收益为负则下一根做多；另看 `>=1σ / 2σ / 3σ` shock 子样本

### 5.2 先说结论
**结论很明确：paper 里的旧 Bitstamp edge，迁到 2025-2026 Binance Spot / Perp，并没有干净复活。**

更准确地说：
- `15m` 还残留一点点负自相关影子，但很弱，更像微观结构 pocket；
- `1h` 在最近样本里基本已经 **不再是 paper 那种稳定可做的中频 fade**；
- `2h` 只有在非常极端的 `3σ` shock 子样本里还勉强看到一点 pocket；
- `4h` 则更接近没 edge，甚至偏 continuation。

### 5.3 这轮 probe 的关键数字
#### Binance USDⓈ-M `15m`（约 `2026-03-15` 到 `2026-04-15`）
- lag-1 autocorr：**`-0.0412`**
- 全样本 contrarian 下一根平均收益：**`+0.006%`**
- `>=3σ` shock 后 contrarian 下一根平均收益：**`+0.028%`**（样本 `47`）

这说明：
- `15m` 还有一点点负自相关；
- 但幅度很小，**离 production 还差一大截**。

#### Binance Spot / USDⓈ-M `1h`（约 `2025-12-11` 到 `2026-04-15`）
- Spot lag-1 autocorr：**`+0.0112`**
- Perp lag-1 autocorr：**`+0.0114`**
- Spot `>=2σ` shock 后 contrarian 下一根平均收益：**`-0.035%`**
- Perp `>=2σ` shock 后 contrarian 下一根平均收益：**`-0.028%`**
- `>=3σ` 甚至更差：Spot **`-0.118%`**，Perp **`-0.133%`**

这和 paper 的 2015-2018 Bitstamp 结果方向都不一样：

> **最近样本里，`1h` 大冲击后并不是“更好 fade”，反而更像已经被市场吸收，甚至有继续顺着走一小段的倾向。**

#### Binance USDⓈ-M `2h`
- 全样本 lag-1 autocorr：**`+0.0077`**
- `>=2σ` shock 后 contrarian 下一根平均收益：**`-0.034%`**
- `>=3σ` shock 后 contrarian 下一根平均收益：**`+0.070%`**（样本 `57`）

也就是说：
- `2h` 并不是 paper 里那种大面积稳定 pocket；
- **只在非常极端的冲击样本里，才勉强还剩一点可继续深挖的 shadow edge。**

#### Binance USDⓈ-M `4h`
- lag-1 autocorr：**`+0.0159`**
- `>=2σ` shock 后 contrarian 下一根平均收益：**`-0.080%`**

这基本可以先看作 **不过线**。

## 6. first verdict
我的 first verdict 很明确：

> **这篇 paper 值得进 raw-alpha 素材池，但更像“旧市场结构下的中频 jump-reversal baseline”，不是 2026 Binance 上还能直接照抄的 production alpha。**

更具体一点：
- **值得保留的部分：** `extreme shock -> next-bar fade` 这个原始结构
- **不该照抄的部分：** paper 那种默认 `1h/2h` 广谱有效的乐观读法
- **当前最像还值得继续测的 pocket：** `2h` 极端 shock（`>=3σ`）后的反手回吐
- **当前最不该先上真钱的部分：** `1h` shock-fade 直译版

所以它对我们更有价值的角色是：

> **一条可复现、可 falsify、而且已经被 recent public-data quick check 打过预防针的 raw-alpha baseline。**

## 7. 下一步怎么测
### 7.1 先别全局优化，先做 3 个最小 A/B
1. **A：paper 原版**
   - `1h/2h` shock 后，下一根全额反手，持有一个同长度 bar

2. **B：desk 版 `1h/2h admission + 15m execution`**
   - shock 后拆成 `15m` 分批入场
   - 加 `VWAP reversion target` 与 fail-fast

3. **C：只保留极端 shock**
   - 只做 `>=3σ` 或 `>=4σ`
   - 直接比较 trade count、expectancy、MDD、成本后净值

### 7.2 这 5 个维度必须一起出
- gross expectancy
- net expectancy（至少 `2 / 4 / 8 bps` 三档）
- shock size vs edge slope
- bull / bear / high-vol / low-vol 分层
- spot vs perp / US session vs Asia session 分层

### 7.3 最先该加的 veto
- CPI / FOMC / ETF decision 等宏观窗口
- funding / basis 已经极端单边时
- order book depth 明显变薄的时段
- 连续趋势日（避免把真正的 trend impulse 当成一根过冲）

### 7.4 如果要继续深挖，优先看这两条而不是乱调参
1. **“冲击来源”分层**：先分 news shock、liquidation shock、普通波动 shock
2. **“极端尾部 pocket”分层**：只看 `>=3σ` / `>=4σ` 是否仍成立

## 8. 为什么这篇不是纯解释型材料
如果只看标题，这篇很容易被误归类成：
- market efficiency 讨论
- 行为金融解释
- Bitcoin stylized facts 总结

但对我们这个 desk 来说，更有用的 intake 方式不是“它解释了什么”，而是：

> **它给了一条足够清楚、可以一行代码写 entry、可以一行代码写 exit 的 raw alpha 原型，而且 recent Binance probe 还能马上告诉你：这条原型今天已经衰减到什么程度。**

这就够它进入研究池。

## 9. 数据与公开性
- **paper 主数据：** Bitstamp BTC/USD `1m` 历史数据（论文样本 `2015-03` 到 `2018-06`）
- **desk portability probe：** Binance Spot / USDⓈ-M 公共 kline API
- **公开性：** 全部公开可得
- **更新频率：** 可达 `1m/5m/15m/1h/2h/4h`
- **最小可复现实验口径：** BTCUSDT 上定义 rolling shock 阈值（按 return / realized vol 标准化），做 `next-bar fade` 与 `15m execution` 两版 A/B

## 10. 来源
- De Nicola, G. (2021). *On the Intraday Behavior of Bitcoin*. *Ledger*.
  - DOI: <https://doi.org/10.5195/LEDGER.2021.213>
  - Readable URL: <https://ledgerjournal.org/ojs/ledger/article/view/213>
  - PDF URL: <https://ledgerjournal.org/ojs/ledger/article/download/213/212/1232>
  - Crossref URL: <https://api.crossref.org/works/10.5195/LEDGER.2021.213>
  - Repo URL: N/A
