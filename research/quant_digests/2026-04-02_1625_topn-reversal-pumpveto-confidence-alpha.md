# 别把这份 2026 新 repo 只读成 XGBoost infra：对 short-cycle desk，更该先测的是「top-N XS loser-bounce × pump-dump veto × confidence sizing」这条完整 mean reversion raw alpha
- 时间：2026-04-02 16:25 UTC
- 主题类型：raw alpha
- 类型：raw alpha
- 基础 alpha：**短窗里最弱的一篮子币，接下来更容易出现 15m~1h 的横截面反弹；但这个 edge 只在“极端 loser 足够集中、且没有明显 pump/dump 痕迹”时才够厚，真正能落地的是“reversal score → top-N 选币 → pump-dump veto → confidence sizing”的完整壳。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是（先做 ML-lite 版，再决定是否上 XGBoost）**
- 主题标签：raw-alpha/cross-sectional/mean-reversion/top-n/loser-bounce/pump-dump-veto/confidence-sizing/binance-perpetual/5m/15m/1h/repo/public-data/cost
- 证据类型：2026 GitHub 新 repo source audit（`README.md`）+ Binance USDⓈ-M `15` 币公共 `5m` 本地 transfer check

## 1) 这次看了什么
这轮不再继续把新 intake 写成单一 breakout / retest / 单币 OFI 小变体，而是补一个 **更像“完整横截面策略骨架”** 的新 repo：

- **gitdhirajsv (2026), `Azalyst-Alpha-Research-Engine`**
- repo headline 看起来像：
  - 444 币
  - 72 个特征
  - XGBoost regression
  - confidence model
  - pump-dump filter
  - IC gating
- 但对我们 short-cycle desk，最值得先拿走的不是“大而全 ML 框架”，而是里面更朴素、也更容易在 `1m/3m/5m/15m` 先复现的那条主干：

> **短窗横截面反转（reversal / loser-bounce）本身是 base alpha；XGBoost 只是排序器，pump-dump veto 与 confidence sizing 才是让它更接近可交易策略的关键配件。**

所以这篇不打算复刻 repo 全量工程，而是把它压缩成 desk 现在就能做的研究题：

> **能不能先用公开 OHLCV 做一个 ML-lite 版 `reversal score × top-N concentration × pump-dump veto`，验证这条 raw alpha 是否真有独立生命力？**

## 2) 先回答题眼：base alpha 是什么？
**Base alpha：**
在 crypto 的短周期横截面里，**刚刚跌得最狠、且跌法更像“过度出清/超卖”，而不是“操纵性 pump-dump”** 的币，未来 `15m~1h` 更容易出现相对反弹；相对地，刚刚冲得最猛且出现过热特征的币，更容易在横截面上回落。

这意味着：
- 它首先是 **raw alpha**，不是纯 filter；
- 核心不是“市场整体涨跌”，而是 **同一时点里谁被砸得最过、谁被拉得最过**；
- 真正决定能否落地的，不只是 `reversal` 本身，而是：
  1. **要不要只做最极端的 top-N**；
  2. **要不要把 pump/dump 痕迹踢出去**；
  3. **仓位要不要跟信号置信度走，而不是一刀切等权。**

## 3) 为什么这条线值得进当前素材池
它符合这轮优先级里的几个关键点：

1. **它是可独立成立的 raw alpha。**
   - 不是单纯给别的策略做 gate。
2. **天然能落成完整策略。**
   - universe、entry、exit、sizing、risk、cost 都能明确写出来。
3. **公开数据可做最小实验。**
   - 先用 Binance perpetual 公共 `5m` OHLCV 就能起步。
4. **和最近 desk 的积累是互补的。**
   - 我们最近补了很多 pairs / OFI / basis / cross-market lead-lag；
   - 这条线补的是 **“横截面反转完整壳”**，而不是再写一个单一 trigger。
5. **repo 给出的真正价值，不是黑箱模型，而是组件拆解顺序。**
   - 先承认 v4 的 momentum 失败；
   - 再把短窗反转、pump-dump 过滤、top-N 集中、confidence sizing 拼成更可交易的东西。

## 4) 从 repo 里真正该拿走的是什么
### 4.1 repo 的关键事实
根据 repo README：
- 数据：**444** 个 Binance 交易对、**3+ 年**、`5m` 频率、**2600 万+** 行；
- v4 是 momentum-dominated binary classifier，作者明确写到：**0/103 profitable weeks**；
- v5 改成：
  - **regression，不是 classification**；
  - horizon 改到 **1h (12 bars)** / **15m (3 bars)**；
  - 特征从 momentum-dominated 改到 **reversal-dominated**；
  - 新增 **8 个 reversal 特征**、**6 个 pump-dump 特征**、**4 个 quantile-rank 特征**；
  - 再叠加 **confidence model** 做仓位分层。

最值得 desk 听进去的一句话其实不是“XGBoost 很强”，而是：

> **“crypto mean-reverts” 这件事，在作者自己的失败复盘里，是从 `momentum` 主导切到 `reversal` 主导的核心理由。**

### 4.2 这份 repo 对 desk 的真正启发
对我们来说，这份 repo 的 transferable 部分不是全量 ML infra，而是这四个动作：

1. **把 alpha 定义成短窗 reversal，而不是继续执着 trend。**
2. **别等权撒网，要做 top-N 集中。**
3. **别把 pump/dump 当成 alpha 本体，要把它当 veto。**
4. **仓位别平均分，至少要有一个简化版 confidence layer。**

换句话说，repo 在教我们的不是“怎么堆 72 个特征”，而是：

> **薄 edge 的横截面反转，必须靠“集中、过滤、分层”三件套，才有可能从研究信号变成交易策略。**

## 5) 本地最小 transfer check（公开数据，先测便宜壳）
### 5.1 数据口径
我先没复刻 repo 的 XGBoost，而是做了一个最便宜的 transfer shell，看看 **“横截面短窗反转”本体到底有多厚**。

- 交易所：Binance USDⓈ-M perpetual 公共 `5m` klines
- 币种：`BTC, ETH, BNB, SOL, XRP, DOGE, ADA, LINK, AVAX, LTC, BCH, ETC, DOT, TRX, SUI`
- 区间：**2026-03-02 10:20 UTC ~ 2026-04-02 16:15 UTC**
- 每币样本：**9000 根 `5m` bar**
- 调仓时点：每小时一次（`xx:55` 收盘后，下一根入场）

### 5.2 先测最裸的 raw alpha：`1h loser/winner` 横截面反手
最便宜版本：
- 每小时看过去 `12 x 5m = 1h` 收益；
- **long**：过去 1 小时最差的 2 个币；
- **short**：过去 1 小时最强的 2 个币；
- 持有 **1 小时**；
- 多空各等权，按 basket 平均收益记账。

结果：
- 样本数：**725** 个 hourly basket
- 平均毛收益：**+0.72 bps / basket-hour**
- 胜率：**54.1%**
- 30 天累计毛收益：**+5.20%**

这说明一件事：

> **“短窗横截面反转”本体不是 0，但很薄。**

### 5.3 再加一个 repo 风格的 `pump-dump veto`
我用一个很便宜的 proxy 模仿 repo 的 pump-dump filter：
- 若某币同时满足：
  - `1d volume z-score` 很高
  - `1d range z-score` 很高
- 则本次横截面选币直接剔除。

结果：
- 样本数：**718**
- 平均毛收益：**+0.62 bps / basket-hour**
- 胜率：**53.5%**
- 30 天累计毛收益：**+4.36%**

结论也很直接：
- **只加一个很粗糙的 veto，不足以把薄 edge 变厚。**
- repo 的价值不在“有个 veto 就行”，而在 **reversal ranking + concentration + confidence** 一起上。

### 5.4 成本下的结论：便宜壳还不够
按更现实的成本压力看：
- 若按 **2 bps 单边**（约 4 bps round trip / leg）估，
  - 上面这个最便宜的 hourly basket 壳 **明显不够厚**；
- 按 **4 bps 单边** 则更不需要讨论。

所以这轮最重要的不是“这条线失败了”，而是更精确地知道：

> **repo 的 transferable alpha 不是“任何 loser basket 都能赚钱”，而是“必须把 reversal 做成高浓度 top-N + 置信度分层 + manipulative-move veto”的完整策略壳。**

这恰好符合当前 desk 的需要：
- 不是又补一篇“crypto 会反转”的泛论；
- 而是补一份 **明确告诉我们 cheap shell 为什么不够、下一步该压哪几个旋钮** 的 intake。

## 6) desk 该怎么把它落成完整策略（先做 ML-lite v0）
### 6.1 Universe
先别上 444 币，先从 **20~40 个流动性更稳定的 perpetual** 起步：
- BTC / ETH / SOL / XRP / DOGE / BNB / ADA / LINK / AVAX / LTC ...
- 先要求：
  - 最近 `30d` 日均成交额足够高；
  - 最低 tick / spread / 费率更可控。

### 6.2 Signal：先不用 XGBoost，先做 4 因子 reversal stack
直接用 repo 里最容易 transfer 的 reversal 侧 primitives，先做一个线性分数：

- `rev_1h`：过去 1h 收益取负
- `rev_4h`：过去 4h 收益取负
- `mean_rev_zscore_1h`：价格偏离近窗均值的 z-score，偏离越负越偏多
- `oversold_rev / overbought_rev`：用 RSI / 布林位置 / wick 之类 cheap proxy 先替代

最小版得分：

`score = z(rev_1h) + 0.5*z(rev_4h) + 0.5*z(mean_rev_zscore_1h) + oversold_proxy`

然后做横截面排序：
- **long**：score 最高的 top-N
- **short**：score 最低的 bottom-N

### 6.3 Concentration：别做 15% quantile，先做固定 top-N
这是我觉得这份 repo 最值得先偷的组件之一。

先测：
- `N ∈ {1, 2, 3, 4}`
- 不要先做宽篮子；
- 因为我们刚刚的本地快检已经说明：**粗糙 loser basket 的问题，不是完全没 edge，而是太薄、太分散。**

如果 top-N concentration 有效，应该看到：
- 交易数下降；
- 单笔/basket 毛 edge 上升；
- cost survival 明显改善。

### 6.4 Pump-dump veto：要做得比“单阈值排除”更像 veto
最小版先用三个 cheap proxy：
- `vol_spike_zscore`
- `abnormal_range`
- `tail_risk / long-wick`

只要其中两项同时过阈值，就暂时不纳入可交易池。

注意这里的定位：
- **它不是 alpha 本体；**
- 它是防止我们把“操纵性急拉急砸”错当成 mean reversion 便宜筹码。

### 6.5 Exit
短周期版先别复杂化：
- 默认持有：`3 / 6 / 12` 根 `5m` bar（即 `15m / 30m / 60m`）
- 任一条件提前平仓：
  1. score 翻到另一侧；
  2. alpha 衰减到 0 附近；
  3. 单币 hit intraday stop。

### 6.6 Sizing
最小版就做一个 **confidence-lite**：
- `size_i ∝ min( |score_i| / realized_vol_i , cap )`
- 或者按 `score` 的横截面 rank bucket 分层：
  - top 1: 1.0x
  - top 2~3: 0.7x
  - 其余：0.4x

这就已经比等权更像 repo 想表达的东西了：

> **不是所有 reversal 都同等可信。**

### 6.7 Risk / cost
必须明确写进 v0：
- 单币 notional cap
- 单侧最大持仓数 cap
- 同主题币（比如 meme cluster）相关性 cap
- 成本至少压两档：
  - **2 bps 单边**
  - **4 bps 单边**
- 若 4 bps 单边下完全塌掉，就不能把它当可交易壳，只能当研究中间件。

## 7) 这条线和 `1m / 3m / 5m / 15m` 的关系
这条 alpha 最自然的层级关系是：

- **`15m`**：更适合作为主决策层
  - 横截面反转本身更需要一点点噪声压缩；
- **`5m`**：最适合做 signal update 与持仓管理
- **`1m / 3m`**：更适合做 execution refinement
  - 例如分批入场、减少冲击、等 micro pullback 再挂。

也就是说，这条线虽然来自 `5m` engine repo，但不一定要把 `5m` 当唯一主信号频率；
**更合理的 desk 做法很可能是 `15m` 选篮子、`5m` 管持仓、`1m/3m` 做执行。**

## 8) 这轮真正的判断
如果只问一句“这条东西值不值得进研究池”，我的回答是：**值。**

但它值得进入研究池的原因不是：
- “README 里用了 XGBoost，很高级”；
- 或者“444 币、72 特征，看起来很全”。

而是因为它很清楚地告诉我们：

1. **短窗 raw alpha 的 base 是 XS reversal，不是继续硬凹 momentum。**
2. **cheap shell 很薄，说明必须做 concentration。**
3. **pump/dump 要当 veto，不要当 alpha 本体。**
4. **仓位要跟置信度走，否则薄 edge 很容易被成本吃掉。**

这四点都直接服务于当前 desk 的 raw alpha 素材池建设，而不是偏离主线。

## 9) 下一步怎么测（直接进复现队列）
### Step 1：先做 ML-lite 四因子版本
用公开 OHLCV 先还原这四个组件：
- `rev_1h`
- `rev_4h`
- `mean_rev_zscore_1h`
- `oversold/overbought proxy`

不要先上 XGBoost，先看 **线性组合 + 横截面排序** 能不能把毛 edge 从 `<1 bps / basket-hour` 拉升到 **>8~10 bps** 量级。

### Step 2：优先扫 `top-N × hold`，不要先扫大而全模型
先做这个小网格：
- `N ∈ {1,2,3,4}`
- `hold ∈ {3,6,12}` bars
- `rebalance ∈ {15m, 30m, 60m}`

核心问题只有一个：
> **edge 是不是藏在“更集中、更短持有”的 pocket 里？**

### Step 3：把 pump-dump veto 做成二元 admission，不是软打分
直接比较：
- no veto
- soft penalty
- hard veto

看哪种最能在 **不显著压缩胜率的前提下** 提高净 bps。

### Step 4：做 confidence-lite sizing
至少做两版：
- 等权
- `|score| / vol` 分层

如果分层 sizing 没有改善净值曲线，说明 repo 的“confidence”对 short-cycle transfer 可能没那么重要；
如果改善明显，就说明这条线确实更像“完整策略”，不是单点因子。

## 10) 来源与链接
### 主来源（repo）
- **Author / Org**：`gitdhirajsv`
- **Year**：2026（README 最新更新时间写到 **Apr 2, 2026**）
- **Title**：*Azalyst Alpha Research Engine*
- **Venue / DOI**：N/A（GitHub repo，不是正式论文）
- **Readable URL**：https://github.com/gitdhirajsv/Azalyst-Alpha-Research-Engine
- **Raw README URL**：https://raw.githubusercontent.com/gitdhirajsv/Azalyst-Alpha-Research-Engine/main/README.md

### repo 内直接可转移的关键信息
- v4 momentum-dominated binary classifier：**0/103 profitable weeks**
- v5 数据规模：**444 pairs / 3+ years / 26M+ rows / 5m**
- short-horizon target：**1h (12 bars) / 15m (3 bars)**
- 新增结构：**8 reversal features / 6 pump-dump indicators / 4 quantile-ranked features**

---

**一句话结论：**
这份 2026 新 repo 真正值得 desk intake 的，不是全量 XGBoost infra，而是它把一条本来很薄的 **XS 短窗反转**，拆成了 `top-N concentration + pump-dump veto + confidence sizing` 的完整策略壳；下一步最该做的，是先用公开 OHLCV 复刻一个 ML-lite 版，看它能不能在 `15m/5m` 上先活过成本。