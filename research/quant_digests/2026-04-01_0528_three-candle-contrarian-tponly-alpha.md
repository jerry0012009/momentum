# 别把这篇 2021 BTC futures 论文只读成蜡烛图小技巧：对 desk 更该先测的是「三连同色后反手 fade × TP-only exit」这条 1m raw alpha

- 时间：2026-04-01 05:28 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/single-asset/mean-reversion/pattern/three-candle/contrarian/tp-only/btc/binance-perpetual/1m/3m/5m/15m/paper/public-data/cost/execution
- 证据类型：2021 *Applied Economics Letters* 论文摘要/元数据（OpenAlex + Crossref）+ Binance USDⓈ-M Perpetual 公开 `1m` 本地 transfer check + `3m/5m/15m` 聚合降采样 quick check

- 主题类型：raw alpha
- 基础 alpha：当 BTC 在超短周期里连续走出 `3` 根同色 `1m` K 线后，后续几分钟更容易发生微观结构级回吐；因此更诚实的做法不是追随，而是**反手 fade，并用 take-profit / time-stop 快速收口**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主看的是 **Min-Yuh Day, Paoyu Huang, Yirung Cheng, Yin-Tzu Lin, Yensen Ni (2021)** 的短文：

> **Profitable day trading Bitcoin futures following continuous bullish (bearish) candlesticks**

如果只用一句人话概括，这篇东西真正值得 short-cycle desk 拿走的，不是“又一个 K 线形态”，而是：

**在 `1m` 上，当 BTC 连续出现 3 根同色 bar 时，下一段最值得先测的不是追动量，而是做一个超短持有的 contrarian fade；退出更像 `take-profit + 最长持有期`，而不是抱着 stop-loss/无限等待。**

更重要的是，我顺手拿 **Binance BTCUSDT perpetual 公共 `1m` K 线** 做了一个超小 transfer check，发现它对我们 desk 的正确读法非常明确：

1. **这条线是 1m-native 的 raw alpha**；
2. **3m/5m 还能勉强当执行层 proxy，但边已经明显变薄**；
3. **15m 基本不该再装成同一条 alpha。**

这点很符合本轮 intake 偏好：继续补 **可独立复现、可快速最小实验、能直接写进 entry/exit/sizing/risk/cost** 的 raw alpha，而不是再写一个泛化解释层。

## 2. 为什么这次值得进研究池
这条线值得收，原因很简单：

1. **base alpha 很清楚**：三连同色后的超短期回吐；
2. **复现门槛很低**：只要公开 `1m` OHLCV 就能先跑；
3. **和当前素材池互补**：最近 digest 已经补了很多 `pairs / options / cross-sectional / order-book directional`，这条线补的是 **单币、超短、pattern-triggered mean reversion**；
4. **可以直接长成完整策略**：entry、TP、time-stop、cooldown、成本壳、cluster veto 都很好写；
5. **能快速证伪**：如果 maker-ish 成本都过不去，就立刻降级，不会长期占研发带宽。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = `1m` 级别的短时过度延伸会在连续 3 根同色 bar 后更容易发生回吐，因此最小可交易表达是“第三根收盘后反手 fade，吃接下来几分钟的 micro mean reversion”。**

更直白地写成策略语言：

- 连续 `3` 根 `1m` 阳线 → **下一分钟优先 short fade**；
- 连续 `3` 根 `1m` 阴线 → **下一分钟优先 long fade**；
- 退出不是幻想“大波段反转”，而是吃掉 **接下来 `1~15` 分钟的一小段回吐**。

所以它是一个 **raw alpha**，分类属于：

- `single-asset`
- `micro / ultra-short-horizon`
- `mean reversion`
- `pattern-triggered contrarian`

不是 filter，不是 regime，也不是 overlay。

## 4. 核心来源
### 4.1 主论文
- **Authors**：Min-Yuh Day, Paoyu Huang, Yirung Cheng, Yin-Tzu Lin, Yensen Ni
- **Year**：2021（刊于 2022 卷期）
- **Title**：*Profitable day trading Bitcoin futures following continuous bullish (bearish) candlesticks*
- **Venue**：*Applied Economics Letters*
- **DOI**：`10.1080/13504851.2021.1899115`
- **Readable URL**：https://doi.org/10.1080/13504851.2021.1899115
- **OpenAlex Metadata URL**：https://api.openalex.org/works/https://doi.org/10.1080/13504851.2021.1899115
- **Crossref DOI URL**：https://api.crossref.org/works/10.1080/13504851.2021.1899115

### 4.2 本次外部公开数据（transfer check）
1. **Binance USDⓈ-M Futures Klines API**
   - Readable URL：https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - 公开性：公开 REST，无需登录
   - 更新频率：分钟级
   - 本次最小实验口径：`BTCUSDT perpetual`、最近约 `65,000` 根 `1m` bars（`2026-02-15 10:25 UTC` 到 `2026-03-31 04:26 UTC`）
2. **本地产物**
   - `reports/artifacts/quant_digests/three_candle_reversal_probe_20260401.csv`

## 5. 证据里最值得拿走的硬点
### 5.1 论文摘要其实已经把“方向”说出来了：它不是追涨杀跌，而是吃均值回复
OpenAlex 抽取得到的摘要核心信息是：

- 研究对象：**Bitcoin futures**；
- 触发条件：**连续 3 根 bullish / bearish 的 `1m` candlesticks**；
- 退出设计：比较 `take-profit` 与 `stop-loss only`；
- 作者结论：**take-profit 策略能产生显著正的 average profit per trade**；
- 作者解释：连续上涨/下跌后，价格里可能混入了吸引追涨/追跌盘的暂时性拉抬/打压，因此**后续更容易回吐**。

翻成人话就是：

**这篇论文真正押注的不是“连续 3 根同色之后趋势延续”，而是“连续 3 根同色已经把短时情绪打得有点过头，回吐 pocket 更值得先抓”。**

### 5.2 本地 `1m` transfer check：这条线在 BTC perp 上确实先表现成“下一小段回吐”
我用 Binance BTCUSDT perpetual 的公开 `1m` 数据，做了一个最小事件研究：

- 信号：连续 `3` 根 `1m` 同色 K
- 方向：反手 fade（3 连阳做空，3 连阴做多）
- 入场：第三根收盘价近似
- 去重：`15m` cooldown，只保留非重叠事件
- 样本数：**3,361** 个非重叠信号

先看 gross、先不计费：

- **持有 1 分钟**：平均 **+4.76 bps**，胜率 **99.64%**；
- **持有 3 分钟**：平均 **+3.86 bps**，胜率 **65.66%**；
- **持有 5 分钟**：平均 **+3.26 bps**，胜率 **60.19%**；
- **持有 10 分钟**：平均 **+2.87 bps**，胜率 **56.99%**；
- **持有 15 分钟**：平均 **+2.33 bps**，胜率 **53.81%**。

最关键的解读不是“胜率很高”，而是：

1. **edge 的主要厚度就在最前面几分钟**；
2. 越往后拖，均值回复 pocket 会迅速被磨薄；
3. 这更像 **micro reversion scalp**，不是可以悠闲拿 `30m~2h` 的 MR。

### 5.3 但这条线对成本极敏感：4 bps roundtrip 就几乎把 close-to-close edge 吃光
同样在上面的非重叠样本里，我粗略做了 roundtrip 成本敏感性：

#### 固定持有 1 分钟
- gross mean：**+4.76 bps**
- 扣 **2 bps** 后：**+2.76 bps**
- 扣 **4 bps** 后：**+0.76 bps**
- 扣 **6 bps** 后：**-1.24 bps**

#### 固定持有 3 分钟
- gross mean：**+3.86 bps**
- 扣 **2 bps** 后：**+1.86 bps**
- 扣 **4 bps** 后：**-0.14 bps**

这说明：

**如果你打算 taker 进、taker 出，把它硬写成无脑市价单，alpha 大概率当场被费用吃掉。**

所以这条线的 honest 版本必须带上：

- maker-ish entry / exit 偏好；
- 极短 time-stop；
- 只在足够大的三连延伸事件上做；
- 不能忽略 spread 与 queue 风险。

### 5.4 `TP-only` 的表达，比单纯 close-to-close 更像 desk 能落地的版本
我又做了一个更接近论文摘要精神的 quick check：

- 非重叠样本：同样 `3,361` 个；
- 入场：第三根收盘后反手；
- 退出：`take-profit` 命中则落袋，否则到最长持有期按收盘出；

结果里比较像 first-pass baseline 的，是这两个组合：

#### `TP = 10 bps, max hold = 10m`
- TP 命中率：**67.59%**
- gross mean：**+3.54 bps**
- 正收益占比：**76.64%**

#### `TP = 10 bps, max hold = 15m`
- TP 命中率：**74.11%**
- gross mean：**+3.68 bps**
- 正收益占比：**78.66%**

这组数给出的 desk 结论是：

**这条线的更自然形态不是“赌大 reversal”，而是“很快收 7.5~10 bps 的回吐，收不到就滚”。**

### 5.5 一旦把 bar 粒度抬高，这条 alpha 会快速衰减，15m 甚至反过来
我把同样逻辑粗暴聚合到更慢的 bar 上做了降采样 quick check：

#### `3m` 聚合后，连续 3 根同色再反手
- 下一个 `3m`：平均仅 **+0.51 bps**，胜率 **55.05%**
- 再往后 `6m~15m`：大致仍只有 **+0.39 ~ +0.73 bps**

#### `5m` 聚合后
- 下一个 `5m`：平均 **+0.88 bps**，胜率 **54.03%**
- 后续 `10m / 15m`：仍然只是 **+0.85 ~ +0.93 bps**

#### `15m` 聚合后
- 下一个 `15m`：平均 **-0.98 bps**
- `30m / 45m`：平均 **-1.64 / -2.55 bps**

所以别把这条线硬升维成 `15m` 主信号。最诚实的结论是：

**它本质属于 `1m` 高强度 raw alpha；`3m/5m` 最多只适合作为执行层压缩表达；`15m` 已经不是同一件事。**

## 6. 对当前 desk 的正确读法
### 6.1 这是 raw alpha，不是 filter
它不是在说“当前更适合做 mean reversion”。

它直接给的是：

- 触发条件：三连同色；
- 方向：反手；
- 收益来源：随后几分钟的回吐；
- 退出方式：TP / time-stop。

所以它是**独立成立的 raw alpha**，可以单独 backtest，可以单独上 live sim。

### 6.2 但它不该被误解成“对所有周期都通用的 candle pattern”
这不是那种能一路抬到 `15m` 的形态学大法。恰恰相反：

- **越接近 `1m`，越像原生信号**；
- **越往 `3m/5m` 压缩，越像执行近似**；
- **到了 `15m`，edge 已经失真甚至翻负。**

### 6.3 它和当前素材池的关系
这条线补的不是：

- cross-sectional ranking
- pairs / basis / funding carry
- order-book directional continuation

而是：

**单币、超短、反手、pattern-driven mean reversion**。

这正好扩一下我们当前 raw alpha 池的形状，不会只是重复已有的 options / stat-arb 主题。

## 7. 如果把它落成完整策略，应该怎么写
### 7.1 Entry
first pass 可以直接写成：

1. 标的：`BTCUSDT perpetual`（先单币）
2. 周期：`1m`
3. 触发：最近连续 `3` 根 bar 同色
4. 方向：
   - `+++` → short
   - `---` → long
5. admission 增强（建议至少加 1~2 个）
   - 三根累计实体绝对值 `>= x bps`
   - 第三根 volume / trade count 高于 rolling 分位
   - 信号触发时 spread 不高于近 30m 分位阈值
   - 最近 `N` 分钟内未出现同方向重复信号（cooldown）

### 7.2 Exit
对 desk 最自然的 first-pass 退出，不是“只看 paper 说 stop-loss 冗余就完全不设风险”，而是：

1. **主退出：TP 7.5~10 bps**
2. **时间退出：10~15 分钟还没 TP 就平**
3. **灾难止损：15~20 bps 或 vol-scaled hard stop**
4. **极端流动性恶化 / funding boundary / news shock 直接撤退**

也就是说：

- **alpha exit** 用 `TP + time-stop`
- **risk exit** 用 hard stop / kill switch

别把两件事混在一起。

### 7.3 Sizing
这类 1m 信号最怕 cluster risk，所以 sizing 应偏保守：

- 单笔固定风险预算；
- 连续信号不叠加，只允许“前一笔结束后再来”；
- 若 30m 内触发过多，自动 size-down；
- 不建议一上来多币扩张，先把 BTC 单币跑稳。

### 7.4 Risk
它最容易死在四件事：

1. **强趋势日里连续 squeeze**；
2. **高费用 / 低深度时误以为有 edge**；
3. **信号簇拥，连续反手被碾**；
4. **宏观事件 / 大额清算 / 撮合异常时还继续机械做。**

所以至少要带：

- cooldown
- cluster cap
- spread veto
- volatility expansion veto
- event kill switch

### 7.5 Cost
这条线最大的诚实点，就是：

**raw alpha 有，但很薄。**

因此成本建模必须前置：

- maker / taker 分场景分开跑；
- 不仅算手续费，还要算 spread 与 queue miss；
- 用 `2 / 4 / 6 / 8 bps` 四档 roundtrip 做生存线；
- 如果只能 taker-heavy，就别自欺。

## 8. 最小可复现实验（建议直接做）
### 实验 A：1m native baseline
- **数据源**：Binance / Bybit BTC perp 公开 `1m` K 线
- **公开性**：公开可得
- **更新频率**：分钟级
- **信号**：三连同色反手
- **入场**：第三根 close 后的下一分钟第一档可成交价近似
- **退出**：`TP 7.5 / 10 bps` × `max hold 5 / 10 / 15m`
- **成本**：`2 / 4 / 6 / 8 bps` 四档
- **目标**：确认哪条成本壳下还能活

### 实验 B：admission 强化
在实验 A 上叠加：

- 三根累计实体阈值
- volume burst 分位
- 当时 spread 分位 veto
- funding boundary veto

核心问题：

**能不能把“很高但很薄”的原始胜率，筛成“更少但更厚”的 maker-ish 信号？**

### 实验 C：多交易所 transfer
- **标的**：Binance / Bybit / OKX BTC perp
- **目标**：确认这是不是 Binance 特有微结构现象
- **输出**：每所各自的 gross / net edge、cluster risk、最佳 TP/time-stop

### 实验 D：3m/5m 只做执行，不做再定义
- `1m` 负责产生信号
- `3m/5m` 只负责：
  - 限价挂单位置
  - 分批进场
  - 被动退出时机

不要把 `3m/5m` 重新当成“也有同样三连反手 alpha”。这轮 quick check 已经提醒我们，**信号本体是 1m 的，不是 5m 的。**

## 9. 为什么它比继续补一个泛化 filter 更值得
因为这轮任务优先级里，**可独立复现、可直接落地完整策略的 raw alpha** 明显高于 filter / overlay。

而这条线满足：

- 有明确 trigger；
- 有明确方向；
- 有明确退出骨架；
- 有公开数据；
- 有本地最小验证；
- 还能快速被成本证伪。

这比再写一个“也许能改善别的策略”的 shared gate，更符合当前 bot7 的主目标：**持续补充 raw alpha 素材池。**

## 10. 下一步怎么测
1. **先只做 BTC 单币 `1m`**，不要一开始扩 alt。  
2. **先跑 `TP 7.5/10 bps × hold 10/15m` 四宫格**，同时分 `2/4/6/8 bps` 成本壳。  
3. **把 maker-entry / maker-exit 概率单独建模**，不要再用纯 close-to-close 自嗨。  
4. **加 cooldown + cluster veto**，验证 edge 是否只是信号拥挤造成的假厚度。  
5. **做跨交易所 transfer**：Binance 活，不代表 Bybit/OKX 也活。  
6. **若 4 bps 下全面转负，就把它降级成“maker-only scalp sleeve”**，而不是硬塞进通用短周期主策略。  

## 11. 一句话结论
这篇 2021 BTC futures 论文对当前 desk 最值钱的，不是“连续三根同色 K 线”这个表面形态，而是：**把它诚实地还原成一条只属于 `1m` 的 contrarian micro-mean-reversion raw alpha——第三根收盘后反手 fade，优先用 `TP + time-stop` 快速收口，并把成本门槛放在研究最前面。**

## 12. 来源链接
- DOI 页面：https://doi.org/10.1080/13504851.2021.1899115
- OpenAlex metadata：https://api.openalex.org/works/https://doi.org/10.1080/13504851.2021.1899115
- Crossref metadata：https://api.crossref.org/works/10.1080/13504851.2021.1899115
- Binance USDⓈ-M Kline API：https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
- 本地实验产物：`reports/artifacts/quant_digests/three_candle_reversal_probe_20260401.csv`
