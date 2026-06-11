# 别把 Kogan et al. (2024) 只读成“crypto 散户行为论文”：对 short-cycle crypto desk，更该先拆的是「recent return shock × retail-chasing proxy」这条 raw alpha

- **主题类型：** raw alpha
- **基础 alpha：** 短窗价格刚明显朝一个方向跑、且市场没有出现“主动止盈/反手”痕迹时，crypto 散户更容易顺着价格去追，后续几根到几十根 bar 更容易继续同向漂移。
- **是否可独立复现：** 是
- **是否可直接落地完整策略（entry/exit/sizing/risk/cost）：** 否

## 先回答一句：这篇东西的 base alpha 是什么？

**base alpha 不是“散户很爱 crypto”这种泛行为结论，而是：`own-past return continuation`。**
更具体地说，是 **“价格刚涨/跌过后，crypto 里的零售资金不像股票/黄金那样更倾向逆向再平衡，而更容易顺着价格继续抱/追，因此短窗内更容易出现延续”**。

对当前 desk 最有价值的，不是照搬论文里的账户级组合份额回归，而是把它翻成一个更快可测的代理版：

> **`recent return shock × activity / no-rebalance proxy -> next 15m~60m continuation`**

也就是：**先用价格冲击定义“方向”，再用成交活跃/换手放大但没有明显反抽的状态，去近似“零售追价而不是逆向再平衡”**。

---

## 这篇论文讲了什么，为什么值得 intake

**来源**
- **Authors：** Shimon Kogan, Igor Makarov, Marina Niessner, Antoinette Schoar
- **Year：** 2024
- **Title：** *Are cryptos different? Evidence from retail trading*
- **Venue：** *Journal of Financial Economics*
- **DOI：** <https://doi.org/10.1016/j.jfineco.2024.103897>
- **Readable URL：** <https://researchonline.lse.ac.uk/id/eprint/122266/>
- **PDF：** <https://researchonline.lse.ac.uk/id/eprint/122266/3/Are_cryptos_different.pdf>
- **Repo URL：** 论文页注明有 replication package，但本轮未直接拿到可执行仓库链接

**我为什么选它**
1. 它是 **近 5 年、顶刊、开放获取**，不是只靠题目想象；
2. 它直接回答一个很关键、而且和短周期研究有关系的问题：**crypto 的零售资金到底更像均值回归，还是更像追涨杀跌？**
3. 它给的是 **跨资产、同一批人** 的比较：同样的散户，在股票/黄金里更 contrarian，在 crypto 里却更 momentum-like。这个差异对 short-cycle alpha 很值钱，因为它说明 **“crypto continuation 不是只能拿技术分析硬猜，背后可能有真实的持仓/行为机制支撑。”**

---

## 论文里最重要的几个硬点

基于我本轮拿到的正文前言与摘要，可确认的关键信息有：

1. **样本来自 eToro 的约 200,000 个零售账户，时间是 2015–2019。**
   这不是纯价格面板，而是真正带账户行为的数据。

2. **作者在股票、黄金、crypto 之间做同人对照。**
   结论非常明确：
   - 散户在 **股票、黄金** 上更像 **contrarian / 逆向再平衡**；
   - 但在 **crypto** 上更像 **momentum-like / 顺着价格继续抱住或追价**。

3. **这种差异不是简单由“客户群不同”解释的。**
   论文明确强调：即使只看 **同时交易股票和 crypto 的同一批人**，这个差异依然存在。

4. **这也不只是“彩票偏好”或“手续费差异”能解释的。**
   论文在前言里点名排除了：
   - investor composition
   - inattention
   - fees
   - lottery-like assets preference
   - lack of cash-flow information

5. **crypto 里更像“价格变化 -> 改变散户对未来采用/扩散概率的看法 -> 再顺着价格更新预期”。**
   直白说：**价格本身就会改变他们对“这玩意以后是不是更值钱”的信念**，所以涨了以后不是先卖，而是更容易继续相信它会涨。

---

## 对我们 desk 最有价值的翻译

这篇 paper 原文不是在做 `1m/5m/15m` 逐 bar 交易规则；它是 **账户持仓份额 + 行为金融** 证据。

但把它翻成人话后，对 short-cycle desk 的启发其实挺直接：

### 不是所有“涨了还涨”都一样

很多 continuation 研究只停在：
- 过去涨了 -> 未来可能继续涨

这篇 paper 真正补的是：
- **为什么在 crypto 里，涨了之后更可能继续涨？**
- 因为一部分资金并没有像股票散户那样做逆向再平衡，反而更可能继续抱住，甚至顺着追。

### 因此我们不该只测裸 momentum

更该测的是：

> **“有价格冲击” + “有追价/不减仓代理” + “没有明显反抽/均值回归痕迹”**

这比简单 `ret_3bar > 0 就追多` 更接近论文想表达的机制。

---

## 更适合当前 desk 的最小代理版 alpha

### alpha 定义（代理版）

在 `1m / 3m / 5m / 15m` 上，先定义：

- `shock_ret_L`：过去 `L` 根累计收益
- `range_close`：当前收盘在过去 `L` 根高低区间中的位置
- `vol_z`：成交量/成交额异常程度
- `pullback_ratio`：冲击后回吐比例
- `follow_through_h`：未来 `h` 根是否继续同向

然后做一个 **retail-chasing proxy score**：

`RCP = z(shock_ret_L) + z(vol_z) + z(range_close) - z(pullback_ratio)`

直觉解释：
- **涨/跌得够快**：说明有方向冲击；
- **成交也同步放大**：说明不是死盘单跳；
- **收在区间边缘附近**：说明冲击后没怎么被打回来；
- **回吐很少**：更像“资金继续抱着/追着”，不像逆向再平衡。

### 交易读法

#### 版本 A：单资产 continuation
- 当 `shock_ret_L > q90` 且 `RCP > q80`：
  - 做多下一根到未来 `h` 根 continuation
- 当 `shock_ret_L < q10` 且 `RCP < q20`：
  - 做空下一根到未来 `h` 根 continuation

#### 版本 B：横截面 router
- 在同一时点对 universe 里各币计算 `RCP`
- **long** top decile `RCP`
- **short** bottom decile `RCP`
- 持有 `3 / 6 / 12` 根 bar

这个版本更像论文原意，因为原论文本质也是在看 **资金如何在资产里重新分配份额**。

---

## 它和最近已做主题的边界

这轮我没有把它写成：
- 一般性的 volume burst continuation
- generic leader rotation
- 或又一篇“彩票偏好” winner-fade

因为这里真正新增的，不是又一个技术指标，而是：

> **同一批散户，在 crypto 里就是更不爱逆向再平衡、更容易顺着价格持有/追价。**

所以它更像是：
- 给 **single-asset continuation** 一个行为地基；
- 给 **cross-sectional relative-strength / top-vs-bottom ranking** 一个机制补强；
- 同时也提醒我们：**别默认把股票里常见的散户 contrarian 逻辑照搬到 crypto。**

---

## 为什么它目前仍然不是“完整策略已就绪”

虽然我把它定为 `raw alpha`，但还没把它定成“可直接落地完整策略”，原因也很清楚：

1. **原文证据层级主要是日度 / 账户份额行为，不是分钟级执行规则**；
2. **原始账户数据不可直接公开拿到**，所以短周期要靠 OHLCV / 成交额 / 活跃度做代理；
3. **exit / sizing / friction** 需要我们自己补，论文本身不负责；
4. 这种 continuation 类代理很容易和：
   - listing / pump / news shock
   - funding boundary
   - taker imbalance
   - session seasonality
   混在一起，需要单独做 honesty check。

所以它现在最合适的定位是：

> **一个值得进入 short-cycle 素材池的 raw alpha 候选，且更像“机制支持下的 continuation proxy”，不是现成 production strategy。**

---

## 最小实验怎么做

### 数据
- **主数据：** Binance USDⓈ-M 或 Spot 公共 `1m / 3m / 5m / 15m` OHLCV
- **Universe：** 先从 `BTC / ETH / SOL / BNB / DOGE / XRP / ADA / LINK` 这类高流动币开始
- **公开性：** 公开可得
- **更新频率：** 分钟级
- **是否依赖外部私有账户流：** 否（只做价格/量代理版）

### 实验 1：单币 continuation honesty check
目标：先确认这不是“冲高回落假 continuation”。

- 对每个币、每个 bar：
  - 计算过去 `3/6/12` 根收益 `shock_ret_L`
  - 计算 `RCP`
- 分箱统计未来：
  - `1 / 3 / 6 / 12` 根收益均值
  - 胜率
  - MFE / MAE
  - cost 后 edge
- 核心看：
  - `high shock + high RCP` 是否比 `high shock only` 更强
  - `high shock + low RCP` 是否更像 exhaustion 而不是 continuation

### 实验 2：横截面 top-vs-bottom
目标：看它能不能成为更干净的 raw alpha，而不是单币噪音。

- 每个时点在 universe 内按 `RCP` 排序
- long top 20%，short bottom 20%
- 持有 `15m / 30m / 60m`
- 比较：
  - plain return rank
  - return + volume rank
  - `RCP` rank

### 实验 3：和现有 continuation 线做区分
目标：确认它不是旧主题换皮。

与以下对象做 horse race：
- plain `ret_3bar`
- `price burst × volume burst`
- `taker imbalance`
- `path-shape continuity`

如果 `RCP` 只是在这些因子上重复，那它不是新 alpha；
如果 `RCP` 在控制这些之后还有增量解释力，它就值得保留。

---

## 我对这条线的当前判断

### 值得保留的原因
- **raw alpha 方向明确**：就是 continuation，不是 filter 假扮 alpha；
- **机制比很多 continuation 候选更扎实**：不是只会说“过去涨了未来可能还涨”；
- **能用公开分钟 OHLCV 很快做代理实验**；
- **还能服务于横截面 relative-strength 排名**，不只单币能用。

### 主要风险
- 代理变量不一定真能抓到“零售不再平衡”；
- 强冲击段可能被 news / liquidation / funding boundary 主导；
- 低流动币可能把 continuation 和操纵混在一起；
- 成本后很可能只有高流动、高清晰冲击 pocket 还能活。

### 当前结论

**保留。**
但我会把它定位成：

> **“有行为机制支持的 continuation proxy 候选”**，
> 不是“论文已经直接证明 5m/15m 可交易 production alpha”。

---

## 下一步怎么测

按优先级我建议直接做这 4 步：

1. **先在 Binance majors 跑 `5m` 与 `15m` 的 `RCP` 分箱图**
   - 看 future `1/3/6/12` bar drift 是否单调；
2. **做 plain momentum vs `RCP` horse race**
   - 回答它是不是只是 `ret_L` 换壳；
3. **做横截面 long-short 版本**
   - 看它是否比单币版本更稳；
4. **最后再接现有 execution 层**
   - 例如 time-stop、ATR stop、cost hurdle、vol veto。

如果这 4 步里：
- `RCP` 没法显著优于 plain short-horizon momentum，
  那这条线就该降级为 **机制解释 / feature candidate**；
- 如果 `RCP` 在 `5m/15m` 上能稳定抬升 continuation 命中率，
  它就值得进入下一轮 clean replication。

---

## References

1. **Kogan, S., Makarov, I., Niessner, M., & Schoar, A. (2024). _Are cryptos different? Evidence from retail trading_. Journal of Financial Economics, 159, 103897.**  
   - DOI: <https://doi.org/10.1016/j.jfineco.2024.103897>  
   - Readable URL: <https://researchonline.lse.ac.uk/id/eprint/122266/>  
   - PDF: <https://researchonline.lse.ac.uk/id/eprint/122266/3/Are_cryptos_different.pdf>

2. **OpenAlex metadata page**  
   - <https://openalex.org/W4389306500>

3. **LSE Research Online repository record**  
   - <https://researchonline.lse.ac.uk/id/eprint/122266/>
