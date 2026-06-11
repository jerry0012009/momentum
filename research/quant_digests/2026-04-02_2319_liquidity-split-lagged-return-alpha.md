# 别把这篇 2021 IRFA 论文只读成“全市场日频 reversal”：对 short-cycle desk，更该先测的是「24h lagged-return × liquidity-split sign flip」这条 XS raw alpha

- 主题类型：raw alpha
- 基础 alpha：**横截面 lagged-return 的符号并不固定；低流动性 crypto 更像短期均值回归（long losers / short winners），而高流动性大币更像短期延续（long winners / short losers）**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-02 23:19 UTC
- 类型：2021 *International Review of Financial Analysis* 论文摘要（OpenAlex）+ Crossref/OpenAlex metadata + Binance USDⓈ-M `15m` 本地 portability probe
- 主题标签：raw-alpha / cross-sectional / momentum / mean-reversion / liquidity / lagged-return / regime-split / sign-flip / top-bottom / 15m / 5m / 3m / 1m / paper / public-data / cost
- 证据类型：paper-based（摘要级硬结论）+ public-data short-cycle translation

## 1. 这次看了什么

这轮选题优先补的是 **raw alpha**，而不是再补一个纯 filter / overlay。主材料是：

- **Authors**: Adam Zaremba, Mehmet Hüseyin Bilgin, Huaigang Long, Aleksander Mercik, Jan Jakub Szczygielski
- **Year**: 2021
- **Title**: *Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets*
- **Venue**: *International Review of Financial Analysis*, Volume 78, Article 101908
- **DOI**: `10.1016/j.irfa.2021.101908`
- **Readable URL**: <https://doi.org/10.1016/j.irfa.2021.101908>
- **Repo URL**: 未见作者公开 repo

这篇 paper 最值得 intake 的地方，不是“又一篇讲 crypto reversal 的老文献”，而是它把一句很适合 desk 落地的话说得非常干净：

> **同样看过去一天收益，低流动性币更像会反弹，高流动性大币反而更像继续走。**

也就是说，这不是简单的 `reversal alpha`，而是一条更有 desk 味道的：

> **`lagged return sign × liquidity regime` 的横截面 raw alpha。**

## 2. 先回答任务里最重要的那句：base alpha 是什么？

这篇东西的 **base alpha 很清楚**：

> **用过去一天的横截面收益排序下一期收益；但信号方向要看流动性——低流动性侧做 reversal，高流动性侧做 momentum。**

所以它不是：
- 纯 filter
- 纯解释型“为什么会这样”
- 纯 risk overlay

它本体就是一条可以写成完整策略的 **cross-sectional raw alpha**。

更重要的是，这条 alpha 对我们 desk 的价值，不在于非要照抄论文的“全市场日频做法”，而在于它提供了一个非常容易压缩到 `1m / 3m / 5m / 15m` 的最小实验框架：

1. 先看过去 `24h` 的横截面收益；
2. 再按流动性分层；
3. 对一层做 loser-bounce，对另一层做 winner-follow；
4. 用更短持有期去验证 edge 有没有活到 short-cycle。

## 3. 论文里到底说了什么

根据 OpenAlex 可读摘要，这篇 paper 的核心硬结论有四个：

1. **样本覆盖超过 3600 个币**；
2. 他们发现一个很强的预测信号：**last day’s return（过去一天收益）**；
3. 在大样本里，**昨天跌得更差的币，明天显著跑赢昨天涨得更多的币**；
4. 但这个效应并不是全市场同符号：
   - **绝大多数低流动性币**：更像 **短期 reversal**；
   - **少数最大、最可交易的币**：更像 **短期 momentum**。

摘要原话的关键信息可以翻成人话：

> crypto 里“昨天跌很多，今天反弹”不是普适真理；它更像是 **illiquidity-induced reversal**。如果你盯的是少数大币 / 高流动性品种，信号方向甚至会反过来。

这正是这轮值得做它的原因：

- 它不是只给一个 headline alpha；
- 它顺手给了一个 **sign-flip 的结构条件**；
- 这个条件非常容易做成 desk 版 `gate` 或 `fork`。

## 4. 这篇 paper 对当前 desk 最有价值的，不是“全市场日频 reversal”，而是 liquidity split

如果只把它总结成“crypto 有 short-term reversal”，那读浅了。

对我们做 `1m/3m/5m/15m` 的 short-cycle desk，更有价值的读法是：

### 4.1 先别假设 lagged-return 一定是反转

很多 desk 容易把“过去 24h 跌很多”自动翻译成：
- 今天该抄底；
- 做 top-N losers 反弹；
- 用更短周期捡 bounce。

这篇 paper 的提醒是：

> **你得先问：你交易的是哪一类币？**

若是：
- 大币、活跃 perp、全天有人打的主流合约 → 可能更像 continuation；
- 小币、长尾、低流动性现货 → 才更像 illiquidity reversal。

### 4.2 这不是“filter 附属件”，而是 alpha 符号本身要翻面

很多 regime/filter 研究只是说：
- 某个 alpha 在某环境更强；
- 或同方向信号在某环境更弱。

而这篇更有价值，因为它在说：

> **同一个 lagged-return 排序信号，在不同 liquidity bucket 下，方向可以直接反过来。**

这对策略工程很关键：

- 若方向只会“强/弱变化”，你可以做同符号加权；
- 若方向会“正负翻转”，你必须做 **forked sleeve**，而不是一刀切。

所以对我们来说，它更像：

- **raw alpha 主体**：lagged-return cross-section
- **核心结构条件**：liquidity split
- **工程表达**：对不同 bucket 走不同 sign

## 5. 我做的最小 portability probe：Binance USDⓈ-M `15m`

为了避免把 paper 摘要直接硬吹成 production edge，我补了一个非常小但够 desk 化的可移植性快检。

### 5.1 数据与实验口径

- **市场**：Binance USDⓈ-M perpetual
- **频率**：`15m`
- **样本窗**：`2026-03-13 23:30 UTC` 到 `2026-04-02 23:15 UTC`
- **Universe**：当前按 `24h quoteVolume` 排序的前 `60` 个 USDT perp，过滤后保留 `58` 个
- **formation signal**：过去 `96` 根 `15m` bar，即 **过去 24h 收益**
- **liquidity proxy**：过去 `96` 根 `15m` 的平均 `quote_volume`
- **rebalance**：每 `4` 根 bar（每小时）更新一次横截面
- **holding**：持有 `4` 根 bar（1 小时）
- **策略原型**：
  1. `rev_all`：全市场 long losers / short winners
  2. `mom_all`：全市场 long winners / short losers
  3. `rev_ill`：只在低流动性 `80%` bucket 做 reversal
  4. `mom_liq`：只在高流动性 `20%` bucket 做 momentum
  5. `combo`：低流动性 reversal + 高流动性 momentum 同时做

这不是 paper-perfect replication，但足够回答最重要的问题：

> **把“过去 1 天收益 + liquidity split”压到 short-cycle 的 15m / 1h 壳上，方向到底站哪边？**

## 6. probe 结果：当前 liquid perp desk 上，continuation 明显强于 loser-bounce

### 6.1 全市场直接对打：momentum 赢，reversal 输

在这组 `58` 个当前活跃 perp 的 `15m -> 1h` 快检里：

- **`mom_all`**：
  - gross Sharpe **`4.89`**
  - 累计收益 **`+30.1%`**
  - 平均换手 **`0.270`**
  - 计入单边 `4 bps` 成本后 Sharpe **`4.00`**、累计 **`+23.8%`**
  - 计入单边 `8 bps` 成本后 Sharpe **`3.11`**、累计 **`+17.9%`**

- **`rev_all`**：
  - gross Sharpe **`-4.89`**
  - 累计收益 **`-24.3%`**

这说明：

> **如果你今天在主流 perp universe 上，不分桶地做“昨天跌得多今天买回来”，方向大概率是错的。**

### 6.2 只看最 liquid 的高流动性 bucket，momentum 更干净

高流动性前 `20%` bucket 的 winner-follow 结果：

- **`mom_liq`**：
  - gross Sharpe **`3.02`**
  - 累计收益 **`+56.2%`**
  - 平均换手 **`0.300`**
  - 单边 `4 bps` 后 Sharpe **`2.70`**、累计 **`+47.9%`**
  - 单边 `8 bps` 后 Sharpe **`2.38`**、累计 **`+40.0%`**

这组数字很重要，因为它正好呼应 paper 的一句核心判断：

> **“largest and most tradeable coins exhibit momentum rather than reversal.”**

也就是说，至少在当前 Binance 主流 perp 样本里，这个 sign flip 方向是对的。

### 6.3 低流动性 bucket 上，paper 的 reversal 还没直接移植成功

低流动性 `80%` bucket 的 loser-bounce：

- **`rev_ill`**：
  - gross Sharpe **`-4.65`**
  - 累计收益 **`-18.1%`**

这意味着一个很重要但容易被忽略的事实：

> **论文里的 reversal edge，大概率活在“更广、更尾部、更现货、更不连续”的币池里；它并没有自动迁移到今天仍然属于 Binance 前 60 成交额的 perp universe。**

换句话说：
- paper 是对的；
- 但 desk 若只看当前活跃 perp，实际更像站在它说的“高流动性侧”；
- 因此现在更值得先做的是 **liquid-momentum sleeve**，而不是盲目抄 loser-bounce。

### 6.4 sign-flip 组合有生命迹象，但还不够 production

把低流动性 reversal 与高流动性 momentum 拼成 `combo`：

- gross Sharpe **`1.90`**
- 累计收益 **`+15.4%`**
- 单边 `4 bps` 后 Sharpe **`1.27`**、累计 **`+9.4%`**
- 单边 `8 bps` 后 Sharpe **`0.64`**、累计 **`+3.8%`**

这说明组合方向不是全错，但当前快检里：

- **liquid momentum** 是主贡献；
- **illiquid reversal** 在这组样本里拖后腿；
- 直接拼装成 production 还太早。

## 7. 我会怎么给这篇东西下判断

### 7.1 它依然是 raw alpha，不是 filter 论文

因为它回答的是：

- 排什么？——过去 24h 收益
- 排完怎么做？——long losers 或 long winners
- 什么时候翻面？——看 liquidity bucket

所以这不是“解释过去为什么会这样”的纯综述，而是一条 **可直接下单的横截面 raw alpha**。

### 7.2 但对当前 desk，最值得 intake 的不是 headline reversal，而是“direction fork”

如果只按摘要 headline 抄：
- long yesterday’s losers
- short yesterday’s winners

那么在当前 liquid perp desk 上，很可能直接站反。

更合适的 desk 版解读是：

> **lagged-return alpha 不是固定 reversal，而是一个需要先经过 liquidity fork 的 raw alpha family。**

也就是：

- **Liquid / majors / perp**：优先测 continuation
- **Long-tail / small / cash spot / 更差 liquidity**：再单独测 loser-bounce

这更符合当前素材池建设目标：
- 不是再围着单一 breakout 形态打转；
- 而是补一个 **可拆成多个 sleeve 的横截面母因子**。

## 8. 映射到 `1m / 3m / 5m / 15m` 的最小实验建议

### 实验 A：先把 liquid momentum sleeve 做实

这是当前最值得先跑的版本。

**Universe**
- Binance / Bybit / OKX 上按过去 `24h` 成交额排序的前 `10~20%` perp

**Signal**
- `ret_24h = close_t / close_{t-96} - 1`
- 每小时排序一次
- long top quantile winners / short bottom quantile losers

**Execution**
- 先用 `15m` 生成信号
- 再下钻到 `5m / 3m` 优化入场
- `1m` 只做 micro execution，不重新定义 alpha

**Risk / Cost**
- 单腿权重 cap
- funding veto
- 大单异常成交量 / pump-dump veto
- 至少扫 `4 / 6 / 8 bps` 三档成本

### 实验 B：别直接放弃 reversal，但要把 universe 下沉

若要验证 paper 原始 reversal 侧，建议别继续只看前 60 大 perp。

应改成：
- 更广 mid-cap / small-cap perp
- 或可交易 spot alt universe
- liquidity decile 更细分，而不是只切 top20% vs rest

关键不是问“reversal 有没有”，而是问：

> **sign flip 的 cutoff 到底在哪个 liquidity decile 开始出现？**

### 实验 C：做连续 sign model，而不是硬二分桶

第一版可先简单分桶；但更像 production 的做法应是：

`signal = rank(ret_24h) × f(liquidity)`

其中 `f(liquidity)`：
- 在高流动性区间为正；
- 在低流动性区间为负；
- 在中间区间靠近 0 或平滑过渡。

这比生硬地“前 20% 做 momentum，后 80% 做 reversal”更适合 desk 长期维护。

## 9. 下一步怎么测

### Step 1：确认 cutoff 位置

在更广 universe 上做：
- liquidity decile `1..10`
- 每个 decile 分别测 `24h lagged-return` 的 continuation / reversal
- 画出 `Sharpe vs liquidity decile`

要回答的问题：

> **到底是 top 1-2 decile 才 continuation，还是更大范围都 continuation？**

### Step 2：做 formation / holding 网格

当前快检只测了：
- formation = `24h`
- hold = `1h`

下一步至少应扫：
- formation：`6h / 12h / 24h / 48h`
- hold：`15m / 30m / 1h / 2h / 4h`

很可能会出现：
- liquid bucket：短 formation + 短 hold continuation 最强
- illiquid bucket：较长 formation + 稍长 hold reversal 才开始成立

### Step 3：把它和现有 top-N / pump-dump veto 组件对接

如果后续继续测 loser-bounce 支线，不要裸跑。

建议至少接：
- `pump-dump veto`
- 异常 funding / basis veto
- 最低成交额门槛
- 单名义仓位 cap

这样才能分清：
- reversal 本身不存在；
- 还是 reversal 在脏样本里被极端事件污染。

## 10. 主要风险

- **样本迁移风险**：论文是更广的 crypto universe；当前快检是 today’s liquid perp sample，不能简单同一化。
- **幸存者偏差**：按当前成交额选 universe，会天然偏向“还活着且活跃”的币。
- **容量错觉**：illiquid reversal 就算真实存在，容量和冲击成本也可能很差。
- **信号污染**：新闻、上币、拉盘、资金费率、做市断层都会让 loser-bounce 变成接飞刀。
- **过度二分风险**：liquidity 是连续变量，生产环境最好别永久停在硬分桶。

## 11. 一句话结论

这篇 2021 IRFA 最值得收进当前 short-cycle 素材池的，不是“crypto 昨跌今反弹”这句 headline，而是更强的那句：

> **`lagged-return` 这条横截面 alpha 的方向，要先看流动性；在当前 liquid perp desk 上，更该先测的是 `24h winner-follow`，而不是盲目抄 `loser-bounce`。**

## 12. 来源

1. Zaremba, A., Bilgin, M. H., Long, H., Mercik, A., Szczygielski, J. J. (2021). *Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets*. *International Review of Financial Analysis*, 78, 101908. DOI: `10.1016/j.irfa.2021.101908`  
   Readable URL: <https://doi.org/10.1016/j.irfa.2021.101908>
2. OpenAlex abstract summary for DOI `10.1016/j.irfa.2021.101908`: 核心信息包括“`last day's return` 是强预测信号”“低流动性币更偏 reversal”“largest and most tradeable coins exhibit daily momentum”。
3. 本地 Binance USDⓈ-M `15m` portability probe（2026-03-13 至 2026-04-02，58 symbols，24h formation / 1h hold / hourly rebalance）：`mom_all` gross Sharpe `4.89`、`mom_liq` gross Sharpe `3.02`、`combo` gross Sharpe `1.90`、`rev_ill` gross Sharpe `-4.65`。
