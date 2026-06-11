# 别把这篇 2022 crypto TA 论文只读成“交易成本提醒”：对 short-cycle desk，更该先测的是「MA / breakout raw alpha × bubble-state gate × cost ladder」这条完整策略骨架

- 时间：2026-04-01 18:11 UTC
- 类型：2022 *Journal of International Financial Markets, Institutions and Money* 开放获取摘要/Introduction/Closing snippets + Crossref 元数据
- 主题类型：raw alpha
- 基础 alpha：价格型 **moving-average / breakout trend-following**；bubble state 不是 alpha 本体，但会决定这条 raw alpha 在什么 regime 下更值得开、放大或直接禁做。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/moving-average/breakout/bubble-regime/transaction-cost/psY/gsadf/btc/eth/xrp/ltc/bch/1m/3m/5m/15m/1d/paper/public-data/cost
- 证据类型：开放获取文章页摘要/Introduction/Closing snippets + Crossref DOI 元数据（paper-based）

## 1. 这次看了什么
**这篇 paper 真正值得 intake 的，不只是“交易成本会吃掉 1m 技术指标”，而是一条更完整的策略读法：crypto 里的 price-only trend raw alpha 可以从 `MA / breakout` 家族开始做，但必须从第一天起就把 `cost ladder + bubble-state gate` 写进策略壳。**

**作者把 `69` 条参数化技术规则同时放到 `1-min` 和 `1-day`、`5` 个主流币、`2016-01-01 ~ 2021-11-10` 的样本里，先看扣费前后利润，再用 PSY/GSADF bubble dating 去解释“哪些 regime 更容易跑出 excess return”。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这轮的 **base alpha 很清楚**：

- 不是 bubble 检测本身；
- 不是 transaction cost 解释本身；
- 而是 **基于过去价格路径的趋势延续 / 突破延续**，也就是 `moving-average` 和 `breakout` 两大家族的技术交易规则。

翻成人话：
**alpha 本体是“价格已经朝一个方向走出来后，短期内还有继续走的倾向”；bubble gate 只是告诉你，什么环境下更值得信它。**

所以这轮应归类为：
- `raw alpha`
- `trend / momentum / breakout`
- 但天然需要配一层 `regime gate + cost shell`

## 3. 为什么这轮值得写，而不是继续补一个只会服务别人的 gate
最近 intake 已经补了不少 `pairs / stat-arb / carry / microstructure / MR`。这篇 paper 这轮值得进池，原因在于：

1. **base alpha 清楚。** 主体就是价格型 trend-following，不是抽象解释层。
2. **完整策略骨架天然齐。** 规则、频率、成本、对照基准、regime 解释都在一篇 paper 里。
3. **它对 short-cycle 很诚实。** 论文没有把 `1-min` 包装成无脑可搬运的 alpha，反而明确提示：**raw alpha 可能在更细频率存在，但一上成本，成活率会明显恶化。**
4. **它特别适合做 ablation。** 我们可以直接拆成：
   - `raw alpha only`：MA / breakout；
   - `raw alpha + cost ladder`；
   - `raw alpha + bubble gate + cost ladder`；
   看哪层才是真增量。

## 4. 来源信息
### 主论文
- **Authors：** Daniel Svogun, Walter Bazán-Palomino
- **Year：** 2022
- **Title：** *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?*
- **Venue：** *Journal of International Financial Markets, Institutions and Money*, Volume 79, Article 101601
- **DOI：** `10.1016/j.intfin.2022.101601`
- **Readable URL：** <https://doi.org/10.1016/j.intfin.2022.101601>
- **Article URL：** <https://www.sciencedirect.com/science/article/pii/S1042443122000816>
- **Crossref metadata：** <https://api.crossref.org/works/10.1016/j.intfin.2022.101601>
- **Data source（文中写明）：** CryptoDataDownload.com 公开价格数据

## 5. 论文具体做了什么
### 5.1 Universe 和频率都很直白
文中样本是：
- **币种：** BTC、ETH、XRP、LTC、BCH
- **频率：** `1-min` 与 `1-day`
- **区间：** `2016-01-01 ~ 2021-11-10`（或各币最早可得）

作者还说明，这些币在当时大约覆盖了 crypto 市值的 **约三分之二**。也就是说，它不是只在 BTC 上讲故事。

### 5.2 信号本体：69 条参数化技术规则
paper 的 raw alpha 本体来自 **69 条参数化技术规则**，核心家族是：
- **moving-average strategies**
- **breakout strategies**

也就是典型的：
- 均线快慢线方向 / 穿越；
- 价格突破过去区间上沿 / 下沿后的跟随。

对当前 desk 来说，这一点最关键：
**它研究的不是“复杂模型预测价格”，而是最容易被我们直接搬成 15m/5m 策略卡的那类价格型趋势 alpha。**

### 5.3 它不是只看毛收益，而是直接比较扣费前后
paper 明确区分：
- **without transaction costs**
- **with transaction costs**

然后看：
1. 有多少规则仍然正收益；
2. 有多少规则在扣费后仍能跑赢 buy-and-hold 的 excess return。

这对 short-cycle desk 很重要，因为很多 intraday 技术规则不是“信号没方向”，而是**方向有一点，但成本先把你吃死了。**

### 5.4 它把 bubble regime 当作“什么时候更该信这条 raw alpha”
作者用 **Phillips–Shi–Yu (2015) / PSY** 的 **GSADF** 方法去识别 bubble periods，然后用 logistic regression 看：
- transaction cost 是否影响 excess return 的概率；
- bubble periods 是否影响 excess return 的概率；
- 二者是否有交互。

翻成人话：
**这篇 paper 不是把 bubble 当另一个 alpha，而是把它当“趋势型 raw alpha 在什么环境下更容易活”的 regime 解释器。**

## 6. 3 个最值得记住的硬数据点
1. **样本设计本身就很适合做 transfer**：`69` 条参数化规则、`5` 个主流币、`2016-01-01 ~ 2021-11-10`、`1-min` 和 `1-day` 双频对照。
2. **扣费后仍有规则能活，但明显是 `1-day > 1-min`。** paper 明确写到：加入 transaction costs 后，`1-min` 的盈利规则数量明显下降；仍然存在部分正 adjusted return，但**产生正 excess return 的规则在 `1-day` 比 `1-min` 更多**。
3. **bubble effect 有币种分化，不是“一刀切”。** 论文在每币“最赚钱的 5 条策略子集”上做 logit 后发现：bubble periods 会提高 **ETH / XRP / LTC** 出现 excess return 的概率；对 **BTC** 没有显著作用；**BCH** 则连 transaction costs 和 bubbles 都没显示出明显影响。

## 7. 对 desk 最该偷走的，不是“bubble”两个字，而是完整策略读法
如果只把这篇 paper 读成“交易成本很重要”，那只拿到了风险管理层。

对当前 desk 更值钱的读法是：

1. **raw alpha 本体：** 价格型 trend-following（MA / breakout）；
2. **gate 层：** bubble-state / acceleration state；
3. **落地层：** cost ladder、trade-frequency control、entry breach threshold；
4. **风险层：** 只在 regime 一致时放大，不一致时降权或禁做。

也就是说，这轮最值得 intake 的不是某一条孤立均线，而是：
**“MA / breakout 是可以直接复现的 raw alpha 家族，但在 crypto 尤其 short-cycle 上，必须从第一天起就把 regime 和成本写进同一张策略卡。”**

## 8. 和当前 `1m / 3m / 5m / 15m` 的关系
### 8.1 这篇 paper 最有价值的，不是鼓励我们先上 1m
论文已经给了非常明确的现实约束：
- `1-min` 技术规则不是完全没有 edge；
- 但**交易成本会让它比 `1-day` 脆弱得多**。

所以对当前 desk，更合理的落地方向是：
- **先在 `15m` 做 raw alpha existence test**；
- **再到 `5m` 做执行与 admission 精修**；
- `1m / 3m` 只拿来管入场切分、确认和 maker/taker 选择，不要第一刀就拿来判断 alpha 本体是否存在。

### 8.2 bubble gate 不该伪装成逐根信号
bubble state 天生更像：
- **regime gate**
- **risk / sizing overlay**
- **execution veto**

而不是每根 `1m / 5m` 的主信号。

也就是说，正确映射应该是：
- **主信号：** 15m/5m 的 MA / breakout continuation；
- **慢变量 gate：** 4h / 1d 更新一次的 bubble-state 或 acceleration-state；
- **执行层：** 1m/3m 只做细化。

### 8.3 这条 raw alpha 更适合先做 liquid perps，而不是一开始铺太宽
由于 paper 的结论已经强调 cost 敏感，短周期版本不应第一刀就铺到一堆尾部币，而应先在：
- BTC
- ETH
- SOL
- XRP
- DOGE（可选）
- BNB（可选）

这类**更可能承受得住 trend entry + exit 摩擦**的 liquid perp 上做 first verdict。

## 9. 可复刻的最小实验
### 实验 A：15m raw-alpha first pass（最优先）
- **Universe：** top `8~12` liquid perps
- **Bar：** `15m`
- **Signal family 1（MA）：**
  - fast / slow = `8/32`, `12/48`, `16/64` bars
  - 入场：`fast > slow` 做多，`fast < slow` 做空
  - 出场：反向 cross 或 `max_hold`
- **Signal family 2（breakout）：**
  - lookback = `24 / 48 / 96` bars
  - 入场：收盘突破区间上沿 / 下沿
  - 为减少噪音，先加 `0.10 / 0.15 / 0.20 ATR` breach threshold
- **Sizing：** 单币 vol target + 组合 gross cap
- **Cost ladder：** round-trip `4 / 8 / 12 / 20 / 30 bps`

目标不是立刻找最优参数，而是先回答：
**价格型 trend raw alpha 在 liquid perp 的 15m 上，扣费后还有没有基本生命体征。**

### 实验 B：bubble-state gate ablation
在实验 A 上加两层对照：
- **No gate**：所有时段都做
- **Bubble / acceleration gate**：只在慢变量趋势扩张状态下做，其他时段降权或禁做

如果暂时不想先上完整 PSY/GSADF，可先用简化 proxy：
- 日频 `20d/60d` realized trend acceleration；
- 或日频 close 离长期均线的 standardized extension；
- 或 `4h` 级别的 rolling explosive-move proxy。

注意：**这层只是 regime 代理，不要冒充 alpha 本体。**

### 实验 C：5m execution refinement
若 `15m` after-cost 仍有边际，再把触发点下钻到 `5m`：
- `15m` 给方向旗标；
- `5m` 决定 immediate entry 还是 pullback entry；
- 比较：
  - 立即追入
  - 首次回踩均线再进
  - 首次突破后回踩区间边界再进

如果 `15m` 本体不活，就不要拿 `5m/1m` 去“优化”一条已经死掉的信号。

## 10. 怎样把它落成完整策略（entry / exit / sizing / risk / cost）
### 10.1 Entry
- 先选 `MA` 或 `breakout` 家族，不要第一版就混成大杂烩；
- 先在 `15m` 上给方向；
- 只有通过慢变量 bubble / acceleration gate 时才允许正常仓位。

### 10.2 Exit
第一轮先用最朴素的两种：
1. **反向穿越 / 反向跌回区间内**；
2. **固定 `max_hold`**（如 `8 / 16 / 24` 根 `15m`）。

### 10.3 Sizing
- 单币先按 realized vol 逆向缩放；
- 组合层设 gross cap；
- regime 不一致时把仓位打到 `0.25x / 0.5x`，不要非黑即白。

### 10.4 Risk
至少加四个：
1. **news / listing / delisting veto**
2. **高 funding 或异常 basis veto**（防止把 carry 扭曲误读成 trend）
3. **连续假突破 kill-switch**
4. **跨币同向暴露 cap**

### 10.5 Cost
这篇 paper 给 desk 最重要的提醒之一就是：
**trend signal 的生死，常常先输在 turnover，而不是输在预测方向。**

所以第一轮就必须强制出：
- gross vs net
- maker-ish vs taker-ish
- `4/8/12/20/30bps` 梯子
- 每日 / 每周 turnover

## 11. 下一步怎么测
1. **先把 MA 和 breakout 家族分开测。** 别一上来就混合，否则不知道是谁在赚钱、谁在拖后腿。
2. **先做 `15m` existence test。** 这篇 paper 已经提醒你 `1-min` 成本很容易毁掉表面 edge，所以别第一刀就上最脏频率。
3. **bubble gate 先做 ablation，不要默认加。** 如果 raw alpha 脱离 gate 完全死掉，那就诚实把最终主题写成“raw alpha + regime gate”的完整策略，而不是假装它是纯裸 alpha。
4. **成本梯子必须和参数搜索同时跑。** 不能先找 gross 最优，再事后补一层成本。
5. **如果 15m 只剩少量正边，再到 5m 做执行 refinement。** 若 15m after-cost 已经为负，就不要继续在 1m/3m 上浪费研究预算。

## 12. 这条线最容易错在哪
- **把 bubble gate 误当 alpha 本体。** 真正的 alpha 还是 MA / breakout continuation。
- **把日频结论机械压缩到 1m。** 论文已经提示不同频率下成本结构差异很大。
- **只看盈利率，不看 turnover 与净收益。** 这会把一条“方向有点对但根本赚不到钱”的信号误收进池子。
- **把所有 breakout 都当一回事。** 在 short-cycle 上，是否加 breach threshold、是否限制假突破再入，会直接决定净值曲线生死。

## 13. 对当前项目的直接意义
这轮主题值得进池，因为它满足当前优先级较高的几条：
- **主题类型：raw alpha**
- **基础 alpha 清楚**
- **能直接映射到完整策略骨架**
- **只依赖公开价格数据**
- **能很快做 `15m / 5m` 最小实验**

如果要一句话概括：
**这篇 2022 paper 最值钱的不是“别忘了成本”，而是给了我们一张非常实用的策略卡：先把 `MA / breakout` 当作 raw alpha 认真测，再用 `bubble-state gate + cost ladder` 去决定它能不能在 short-cycle crypto 上活成真正可交易的东西。**

## 14. 来源链接
- DOI：<https://doi.org/10.1016/j.intfin.2022.101601>
- Article page：<https://www.sciencedirect.com/science/article/pii/S1042443122000816>
- Crossref：<https://api.crossref.org/works/10.1016/j.intfin.2022.101601>
- Journal page（container metadata via Crossref）：*Journal of International Financial Markets, Institutions and Money*, Volume 79, Article 101601
