# 别把 adverse selection 只当微观结构术语：对 short-cycle desk，更该先测「signed ASC-share shock × next-bar continuation」这条 microstructure raw alpha

- 时间：2026-04-06 12:24 UTC
- 类型：2023/2022 论文交叉（Crossref abstract + OpenAlex metadata + ScienceDirect introduction/section snippets）+ Binance Futures public quote availability probe
- 主题类型：raw alpha
- 基础 alpha：**当一段 `1m/3m/5m` 的主动成交把“未来中价朝同方向继续移动”的信息含量推高时，价格的短周期 edge 不在均值回归，而在信息尚未完全入价前的同向 continuation；最适合的 desk 化表达，是做 `signed adverse-selection share`（ASC-share）冲击后的 1~3 bar 延续，而不是把它只当 spread/toxicity filter。**
- 是否可独立复现：是（需使用公开 `trade + quote` 数据；最快路径是自采 Binance/Bybit 实时 `aggTrade + bookTicker/depth`，或使用公开历史 LOB 源）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/adverse-selection/information-asymmetry/effective-spread/impact-share/continuation/signed-flow/binance/perpetual/1m/3m/5m/paper/metadata/public-data/cost/risk
- 证据类型：主论文摘要级核心结论 + supporting paper 的负证据 + 公开交易所 quote/trade 数据可得性确认

## 1. 这次看了什么
这轮主材料我选的是一篇**没被当前 digest 池直接 intake 过、但和短周期执行/方向 edge 关系很近**的微观结构论文：

### 主论文
- **Murat Tiniç, Ahmet Sensoy, Erdinc Akyildirim, Shaen Corbet (2023), _Adverse selection in cryptocurrency markets_**
- Venue：*Journal of Financial Research*
- DOI：<https://doi.org/10.1111/jfir.12317>
- Readable URL：<https://doi.org/10.1111/jfir.12317>
- Crossref abstract：可取
- OpenAlex metadata：可取

### 补充对照（负证据，用来限定 horizon）
- **Yaqi Wang, Chunfeng Wang, Ahmet Sensoy, Shouyu Yao, Feiyang Cheng (2022), _Can investors’ informed trading predict cryptocurrency returns? Evidence from machine learning_**
- Venue：*Research in International Business and Finance*
- DOI：<https://doi.org/10.1016/j.ribaf.2022.101683>
- Readable URL：<https://www.sciencedirect.com/science/article/pii/S027553192200071X>

我这轮选它，不是因为它在讲“spread / toxicity / liquidity”这些已经很熟的词，而是因为它其实给了 desk 一句更值钱的话：

> **短周期里，真正该测的不是“成交活不活跃”，而是“这波主动成交到底是不是信息型成交，是否会把未来中价继续往同方向推”。**

这句话如果能落成可复现 proxy，本质上就是一条 **microstructure directional raw alpha**，而不只是一个风险提示器。

## 2. 先回答：这篇东西的 base alpha 是什么？
先一句话说清：

> **base alpha = `signed adverse-selection shock`。**
>
> 也就是：当买方/卖方主动成交之后，未来中价继续沿着同一方向走，说明这波成交不是单纯 liquidity-taking，而是带信息的 price discovery；这时更合理的交易不是逆着它抄回归，而是顺着它做 1~3 bar continuation。

这点为什么重要？因为它把很多看起来像同一类的 microstructure 现象分开了：

- **普通冲击 / 噪音成交**：打出去以后，中价没继续走，甚至回头；更像短期吸收或反打。
- **adverse-selection 型冲击**：打出去以后，中价继续顺着 aggressive side 走；更像信息还没完全入价。

对 short-cycle desk 来说，后者是 raw alpha，前者更像 regime/filter。

## 3. 论文真正给了什么证据
### 3.1 主论文最硬的 3 个点
根据 Crossref/OpenAlex 可取到的摘要信息，主论文的关键信息有 3 个：

1. **作者用 Bitfinex 的 order + trade 数据，确认 major crypto 存在统计显著的 adverse-selection cost。**
2. **这个 adverse-selection cost 平均约占 effective spread 的 `10%`。**
3. **它不仅和波动/流动性/market toxicity 相关，还能预测 intraday returns。**

对 desk 最重要的是第 3 点：

> **论文不是在说“信息不对称会让交易更难做”这么泛的结论，而是在说：这类微观结构成本本身含有未来收益信息。**

也就是说，这不是纯 overlay；它有资格被读成 directional raw alpha 候选。

### 3.2 为什么还要看 2022 那篇 machine-learning 论文
因为补充论文给了一个很关键的边界条件：

- 作者用 **12 个 crypto、超过 3 年样本、覆盖当时总市值 `76.79%`** 的币种；
- 把 informed-trading indicators、order imbalance、market toxicity、order frequency 之类都塞进 ML；
- 结论却是：**对更慢的 return prediction，增量预测力并不显著。**

这条负证据反而很值钱，因为它在提醒我们：

> **这类 edge 更像“短、局部、事件后数根 bar 的信息延续”，而不是拿去做慢频日度/周度大一统因子。**

所以它反而支持本轮的 desk 化读法：

- **主战场放在 `1m / 3m / 5m`；**
- **不要把它拖成 daily ML feature soup；**
- **也不要把它误降级成纯 filter。**

## 4. desk 化后，最值得先测的不是“水平”，而是 `signed ASC-share`
### 4.1 人话版定义
主论文原意里的 adverse-selection component，本质是在问：

> **你这笔 aggressive trade 打出去之后，未来中价到底有没有继续朝这个方向挪？**

如果有，而且比例不低，那么 effective spread 里那部分“看起来像手续费/点差”的成本，其实不是给做市商赚走了，而是**市场在承认你带着信息在交易**。

### 4.2 最适合 short-cycle desk 的 proxy
我建议不要一上来照学术版完整分解，而是先做一个更容易回测/执行的 public-data proxy：

对每笔 aggressor trade `i` 定义：

- `q_i ∈ {+1, -1}`：买主动为 `+1`，卖主动为 `-1`
- `m_i^-`：成交前中价
- `m_i^+Δ`：成交后 `Δ` 秒中价（如 `5s / 15s / 30s`）
- `p_i`：成交价

则可计算：

- **effective-spread impact**：`ES_i = 2 * q_i * (p_i - m_i^-)`
- **signed adverse-selection component**：`ASC_i = 2 * q_i * (m_i^+Δ - m_i^- )`
- **impact share**：`ASC_share_i = ASC_i / max(|ES_i|, ε)`

bar 级别再做 volume-weighted aggregation：

- `ASC_bar = VWAP_q(ASC_i)`
- `ASCshare_bar = VWAP_vol(ASC_share_i)`

我建议真正 first test 的主信号，用的是：

> **`signed ASCshare_bar` 的极值与持续性。**

因为它比单看 order imbalance 更接近“这波 aggressive flow 到底是不是 information-bearing”。

## 5. 这条 raw alpha 怎么写成完整策略
### 5.1 交易语义
不是“谁买得猛就追谁”，而是：

> **只有当 aggressive side 在打完以后，未来中价继续顺着同方向走，才说明这不是普通噪音冲击，而是信息型冲击。**

因此更好的 entry 是：

#### Long 条件
- `ASCshare_bar_z >= z_hi`
- `ASC_bar > 0`
- 同 bar 或前一 bar 的 taker buy imbalance 为正
- 近 `N` 秒/近 1 bar 没有明显 opposite-side quote refill

#### Short 条件
- `ASCshare_bar_z <= -z_hi`
- `ASC_bar < 0`
- 同 bar 或前一 bar 的 taker sell imbalance 为负
- 近 `N` 秒/近 1 bar 没有明显 opposite-side quote refill

### 5.2 exit 不要复杂
这条 alpha 的 edge 来自“信息还没完全入价”的短 pocket，所以 exit 应该短、机械：

- **主退出**：持有 `1~3` bars
- **反向退出**：`ASC_bar` 或 `ASCshare_bar` 反号
- **失败退出**：入场后 `1` bar 内没有 follow-through，直接平
- **时间止损**：`max_hold = 15m`（对 `5m` bar 就是 3 bars）

### 5.3 sizing
先别上 fancy optimizer，第一轮最简单：

- 仓位 `∝ min(|ASCshare_bar_z|, z_cap)`
- 单笔风险预算固定
- 在 high-spread / high-liq-stress 时自动缩小

### 5.4 cost
这条线对成本非常敏感，因为它吃的是**很短的 information drift**：

- baseline 先跑 `4 / 8 / 12 bps` round-trip
- maker-only 不要默认，因为很多时候信号本身就发生在主动冲击里
- 先按 taker realistic fill 做悲观版本，再看是否值得往 maker-improve 优化

## 6. 为什么它值得进当前研究池
### 6.1 它补的是一个当前池子里还没单独讲透的 family
最近 intake 很多主题都已经覆盖：

- carry / funding / basis
- pairs / residual / same-underlier RV
- leader-laggard / cross-asset spillover
- pattern / breakout / squeeze release

但 **“information-bearing trade impact”** 这条线目前还没有被单独拆成一篇完整 digest。

它的独特之处在于：

- 输入不是价差、不是 funding、不是 pattern；
- 而是 **aggressive trade 打完之后，未来中价是否继续确认它**；
- 这更贴近 execution edge 和短周期方向 edge 的交叉地带。

### 6.2 它也能服务别的 alpha，但这次不该只把它降级成 filter
它当然也能做 shared gate：

- breakout 要求 `ASCshare` 同向确认；
- mean reversion 避开强 `ASCshare` 同向冲击；
- pairs 执行时回避单腿被强 adverse selection 吃穿。

但如果本轮只把它写成 gate，就亏了。因为主论文已经明确说它**预测 intraday returns**。所以这轮更应该把它放回 raw alpha 本体来测。

## 7. 与 `1m / 3m / 5m / 15m` 的关系
我会这样摆层级：

- **信号生成层**：`1m / 3m`
  - 因为 adverse selection 本质是更快的 L1/L2 + trade 现象
- **组合评估层**：`5m`
  - 看是否还能保留 edge、降低噪音
- **不建议**把 `15m` 当主生成层
  - 到 `15m` 很可能已经把信息 drift 与后续噪音/均值回归混在一起

所以这条线最自然的读法是：

> **`1m/3m` 主信号，`5m` 做降采样稳健性检查，`15m` 只做 transfer 边界观察。**

## 8. 下一步怎么测
### 8.1 最小实验（最快能开跑）
#### 数据
公开可得的最小口径：
- **Trade**：Binance Futures `aggTrade` / live websocket
- **Quote**：Binance Futures `bookTicker` 或 `depth` / live websocket
- 文档：<https://binance-docs.github.io/apidocs/futures/en/>
- 公共归档：<https://data.binance.vision/>

本轮 live probe：
- `bookTicker` REST 公共可取
- `aggTrade/depth` REST 当前触发 `-1003`/`418` 限频，说明**实盘/研究都应优先 websocket 或 archive 路径**，不要用高频 REST 轮询

#### 标的
- 先只做 `BTCUSDT` perp
- 第二轮再看 `ETHUSDT`

#### 频率
- 主实验：`1m`
- 稳健性：`3m`, `5m`

### 8.2 具体实验步骤
#### 实验 A：最朴素的 signed ASC-share continuation
1. 采集逐笔 trade + quote
2. 计算每笔 `ASC_i` 与 `ASCshare_i`
3. 聚合成 `1m` bar 的 `ASC_bar`, `ASCshare_bar`
4. 按 `z-score` 分桶
5. 检查未来 `1/2/3` bars 累积收益的单调性

如果 `|z|` 越高，未来同向 drift 越强，这条线就成立了。

#### 实验 B：只做最极端口袋
- long：`ASCshare_z >= 2`
- short：`ASCshare_z <= -2`
- next bar open 入场
- 持有 `2` bars
- 若下一 bar `ASC_bar` 反号，提前平仓

#### 实验 C：和“普通 order imbalance”做 horse race
同样的 universe、同样的持有期，比较：
- `signed ASCshare`
- 纯 `taker imbalance`
- 纯 `OFI`
- 纯 `bar return`

如果 `ASCshare` 胜出，说明这不是把老 signal 重新命名。

### 8.3 first verdict 最该先看什么
别先看年化，先看这 5 个：

1. **future 1~3 bar return monotonicity**：极端 `ASCshare` 是否对应更强 continuation
2. **hit-rate by bucket**：不同阈值桶是否稳定分层
3. **cost cliff**：`4/8/12bps` 下 edge 剩多少
4. **delay sensitivity**：`Δ = 5s / 15s / 30s` 时 proxy 是否稳定
5. **BTC→ETH portability**：是否只有 BTC 有 edge，还是 major perp 都能迁移

## 9. 风险与盲点
### 9.1 最大现实问题：历史 quote 数据的可得性比 K 线差
这条线最大的工程门槛不是想法，而是数据：

- `trade` 公共获取不难；
- **quote / midquote 历史**才是关键；
- 所以第一轮最省事的办法通常不是回补很长历史，而是**先开始连续自采**，再做滚动 forward + 最近窗口回测。

### 9.2 它容易和别的 microstructure signal 高相关
比如：
- order imbalance
- OFI
- VPIN / toxicity
- depth imbalance

所以必须做 horse race，确认不是旧信号换壳。

### 9.3 不该把它拖成慢频因子
补充论文已经提醒我们：

> **把 informed-trading / toxicity 这些变量直接丢进更慢频 ML，未必会得到好预测。**

所以这条线不要被错误地 desk 化成“日频市场状态分”。它更像快节奏 directional pocket。

## 10. 我的结论
如果只用一句话总结：

> **这次最值得 intake 的不是“adverse selection 会提高交易成本”这个常识，而是“signed adverse-selection share 本身就是可以拿来做 1~3 bar continuation 的 microstructure raw alpha”。**

我对它的当前评级：

- **是否值得进入研究池**：是
- **优先级**：中高
- **更像什么**：raw alpha，本体优先；其次才是 breakout / pairs / MR 的 shared gate
- **最小实验建议**：先做 `BTCUSDT 1m` 的 `ASCshare` 分桶 + 2-bar continuation
- **当前证据评级**：`medium-idea / medium-evidence`
  - idea 很清楚
  - 论文证据明确说“predict intraday returns”
  - 但公开可回补的数据工程门槛高于普通 K 线题

如果第一轮结果成立，这条线后面可以自然分叉成两条：

1. **directional book**：`signed ASCshare` continuation
2. **execution/risk book**：强 adverse-selection 反向 veto / size-down

但当前默认优先顺序，还是先把它当 **raw alpha** 来测。

## 11. 来源链接
### 主论文
- DOI：<https://doi.org/10.1111/jfir.12317>
- Crossref metadata：<https://api.crossref.org/works/10.1111/jfir.12317>
- OpenAlex metadata：<https://api.openalex.org/works/https://doi.org/10.1111/jfir.12317>

### 补充论文
- DOI：<https://doi.org/10.1016/j.ribaf.2022.101683>
- ScienceDirect article page：<https://www.sciencedirect.com/science/article/pii/S027553192200071X>
- Crossref metadata：<https://api.crossref.org/works/10.1016/j.ribaf.2022.101683>
- OpenAlex metadata：<https://api.openalex.org/works/https://doi.org/10.1016/j.ribaf.2022.101683>

### 公开数据 / 文档
- Binance Futures API docs：<https://binance-docs.github.io/apidocs/futures/en/>
- Binance public archive：<https://data.binance.vision/>
- Binance Futures bookTicker public REST：<https://fapi.binance.com/fapi/v1/ticker/bookTicker?symbol=BTCUSDT>
