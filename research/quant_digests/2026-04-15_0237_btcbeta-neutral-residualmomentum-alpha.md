# 别把这份 2026 multi-alpha repo 只读成“又一个日频 momentum 教程”：对 short-cycle desk，更该先拆的是「BTC-beta-neutral residual momentum ranking」这条 raw alpha——但 first verdict 也很清楚：去 beta 能减噪，不等于 `15m` 直译就能赚钱
- 时间：2026-04-15 02:37 UTC
- 类型：2026 GitHub repo source audit（`alpha_14_residual_momentum.py` + `data_fetcher.py` + repo metadata）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：先用滚动回归把每个币的收益拆成 **BTC 市场因子 + idiosyncratic residual**，再对“跳过最近 `1h` 后的累计 residual”做横截面排序；**做多 residual momentum 最强、做空最弱**，赌的是“剥离市场 beta 后，资产自己的相对趋势还会延续”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 原始日频/慢频 long-short 壳是完整的；短周期直译仍需二次验证）
- 主题标签：raw-alpha / cross-sectional / residual-momentum / idiosyncratic-momentum / beta-neutral / market-model / BTC-proxy / long-short / ranking / continuation / binance-perpetual / 15m / 1h / 4h / repo / paper / public-data / cost / risk
- 证据类型：工程证据（源码）+ 学术母体（论文元数据）+ 本地 public-data portability probe

## 1. 这次为什么值得看
先回答 base alpha：**这不是 generic momentum，也不是又一条 pairs spread fade；它的 base alpha 很清楚，就是“把 BTC 这层大盘方向剥掉以后，剩下那部分 idiosyncratic continuation 能不能继续赚”。**

我最后选它，不是因为我们缺“momentum 论文”，而是因为当前 digest 池里：
- pairs / spread / cointegration / basis / funding 这几类已经很多；
- 但 **beta-neutral residual continuation** 这条更接近“去市场噪音后的横截面原始 alpha”还没有被单独讲透；
- 它和我们最近写过的 `loser→winner fade`、`kurtosis fade`、`funding+basis carry` 不是一回事，能补一条 **continuation / de-beta / cleaner cross-sectional ranking** 家族。

更关键的是，这个题不是只有 paper 概念。repo 里这条 `alpha_14_residual_momentum.py` 已经把：
- 信号定义
- raw momentum 对照组
- IS/OOS IC
- Fama-MacBeth
- top/bottom 组合
- `8 bps` 成本

都写进同一套 backtest 壳里，所以它是可以直接拿来当研究骨架的，不是泛泛而谈。

## 2. repo 里到底写了什么
主材料来自 2026 GitHub repo：
- **Repo**：VedantUpasani46 / `Alpha-Research-Discovery`
- **Relevant file**：`alpha_14_residual_momentum.py`
- **Repo URL**：<https://github.com/VedantUpasani46/Alpha-Research-Discovery>
- **Raw file**：<https://raw.githubusercontent.com/VedantUpasani46/Alpha-Research-Discovery/master/alpha_14_residual_momentum.py>

repo 自己给出的原始定义很直白：

1. 对每个资产做滚动市场模型：

```python
r_{i,t} = alpha_i + beta_i * r_{m,t} + eps_{i,t}
```

2. 用滚动窗口估 `beta` / `alpha`，取 residual：

```python
resid_{i,t} = r_{i,t} - (alpha_i + beta_i * r_{m,t})
```

3. 把最近一段 residual 累加，但 **跳过最近几根 bar / 几天**：

```python
resid_mom_{i,t} = sum(resid_{i,t-k}), k in [skip, window]
```

4. 最后做横截面排序，long strongest / short weakest。

repo 默认是日频慢因子口径：
- `REGRESSION_WIN = 126`
- `CUMULATION_WIN = 126`
- `SKIP_DAYS = 5`
- `TOP_PCT = 0.20`
- `TC_BPS = 8.0`

也就是说，原作者不是在赌“最近一两根冲太猛会反转”，而是在赌：

> **把市场共同因子剥掉后，那些真正由资产自身驱动的相对强弱，往往比 raw momentum 更干净、更不容易在系统性反转里一起翻车。**

## 3. 这条 alpha 和普通 momentum 差在哪
repo 最有价值的点，不是“又发明了一个新公式”，而是它把 **raw momentum 和 residual momentum 明确摆在同一套框架里对照**：

- raw momentum：直接看过去一段价格涨跌；
- residual momentum：先把市场 beta 拿掉，再看剩下那部分累计 residual。

翻成人话：
- raw momentum 经常把“市场整体一起涨”也当成 alpha；
- residual momentum 更像在问：**同样在这轮 BTC 大行情里，哪些币是“超额地自己走强/走弱”的？**

这件事对 short-cycle desk 其实很重要，因为我们很多横截面信号最后都会遇到一个问题：

> 到底赚的是资产自己的 edge，还是只是赌到了那段时间的 BTC / beta / market drift？

这条 residual momentum 提供的正是一个更干净的答案框架。

## 4. 为什么它对 crypto desk 有意义
虽然 repo 默认更像 equity / slow-horizon 写法，但源码里自己就明确写了：
- market proxy 可以换成 crypto market proxy；
- crypto 场景下，可以把 `BTC` 作为市场因子；
- 最终信号仍是 cross-sectional rank，再做 long-short。

这就让它很适合 desk 化成三种用途：

### 4.1 直接当 raw alpha 候选
最直接的读法就是：
- universe 取 liquid majors / liquid alts；
- `BTC` 做 market factor；
- 每个币估 rolling beta；
- 对 residual cumulative return 排名；
- 做 market-neutral long-short。

这是一个完整、可独立成立的 raw alpha，而不是 overlay。

### 4.2 当别的 alpha 的去噪底座
如果你不想直接交易 residual momentum，也可以把它拿来给别的横截面 alpha 去噪：
- loser/winner reversal 先在 residual return 上做；
- pairs / bucket clustering 先看 residual correlation；
- funding / carry 排名时，先区分 signal 到底只是市场 beta 还是 idiosyncratic crowding。

### 4.3 当“别把 raw momentum 过度神化”的 falsification 工具
它还有个很现实的价值：

> 如果一个所谓的横截面 momentum 信号，一旦去掉 BTC beta 就没了，那它可能根本不是资产自身 alpha，而只是 market drift 的重命名。

这对研究池筛选很有帮助。

## 5. 我做的 `15m` portability probe：去 beta 确实减噪，但还不够让它直接上线
为了不只停留在源码阅读，我又拿 Binance 公共 `15m` 永续数据做了一个很小的短周期 probe。

### 5.1 数据口径
- 数据源：Binance USDⓈ-M public klines
- 市场因子：`BTCUSDT`
- 横截面 universe：`ETH / SOL / XRP / BNB / DOGE / ADA / TRX / LINK / AVAX / LTC / BCH / DOT / AAVE / NEAR / ETC / SUI`
- 样本区间：`2026-04-01 09:00 UTC ~ 2026-04-15 02:30 UTC`
- bar 数：`1319` 根 `15m`
- 调仓频率：按预测 horizon 对齐（`1h ~ 4h`）
- 费用假设：换手对应 one-way `4 bps`

### 5.2 我测的最小映射方式
我没有硬复刻 repo 的 `126d / 126d / skip 5d`，而是做了一个很小的短周期映射网格：
- regression window：`2d ~ 8d`
- cumulation window：`1d ~ 3d`
- skip：固定 `1h`
- hold horizon：`1h / 2h / 4h`

**小网格里 residual 版本最不差的一组**是：
- regression `576` bars（约 `6d`）
- cumulation `192` bars（约 `2d`）
- skip `4` bars（`1h`）
- hold `8` bars（`2h`）

对应结果：
- **Residual mean IC = `-0.0049`**
- **Raw momentum mean IC = `-0.0335`**
- **Residual gross Sharpe = `+0.29`**
- **Raw momentum gross Sharpe = `-3.21`**
- **Residual net Sharpe = `-1.71`**
- **Raw momentum net Sharpe = `-5.16`**
- signal correlation（residual vs raw）≈ **`0.71`**

### 5.3 这组数怎么解读
重点不是“residual 赚钱了”，因为它**并没有**。

重点是两件事：

1. **去 beta 以后，短周期 continuation 的确变得没那么糟。**
   - 同一小网格里，residual 版几乎系统性优于 raw momentum；
   - 至少说明 repo 的“去掉市场共同因子”这个方向不是空话。

2. **但直接把日频 residual momentum 压缩成 `15m` long-short，还不够。**
   - net Sharpe 仍是负的；
   - turnover 仍偏高；
   - 说明这条线当前更像一个 **中慢频 state / ranking input**，还不是现成可下 production 的 `15m` 主信号。

所以 first verdict 很明确：

> **repo 给的是一条值得进研究池的 raw alpha 家族；但对 short-cycle desk，先别把它当“可以直接拿去做 `15m` 连续轮动”的现成 cash machine。**

## 6. 我对这条线的 desk 化判断
### 6.1 应该保留什么
最该保留的是这个思想：

> **先去掉 `BTC` 这层共同 beta，再谈横截面 continuation。**

这和直接做：
- raw return ranking
- loser/winner reversal
- simple relative strength

是不同层次的东西。

### 6.2 不该直接照搬什么
不该直接照搬的是：
- 把日频 residual momentum 的符号、窗口、持有期，机械压缩到 `15m`；
- 以为去 beta 以后就天然能过成本；
- 把它误读成“又一个慢因子，所以对 intraday 没意义”。

更合理的读法是：
- 它本体是 **de-beta cross-sectional continuation**；
- 对 short-cycle 更像 **ranking backbone / regime state / combination feature**；
- 真正需要优化的是 horizon、rebalance 节奏、bucket neutralization 和成本约束。

## 7. 下一步怎么测
这里必须具体，不然这篇就只是概念卡片了。

### 实验 1：先把主战场从 `15m` 提到 `1h`
- 不要急着逐根 `15m` 调仓；
- 先测 `1h` bars，持有 `4h / 8h / 24h`；
- 看 residual continuation 是否其实是更慢的 cross-sectional drift。

### 实验 2：比较三种 market proxy
同样一套 residual momentum，只替换市场因子：
1. `BTC`
2. equal-weight basket mean
3. `BTC + ETH` 双因子回归

看哪种 proxy 最能减少 raw momentum 的 market contamination。

### 实验 3：直接做“residual continuation vs residual reversal”符号对照
这条很关键。

同一个 residual return 底座，直接测两边：
- `+rank(resid_mom)`：continuation
- `-rank(resid_mom)`：reversal

因为 crypto intraday 很可能不是 equity 那种慢 continuation，而更像：
- `1h` 以下偏 residual reversal
- `4h~1d` 才逐渐转成 residual continuation

### 实验 4：先按 residual correlation / beta bucket 分层，再做排序
不要在一个大而杂的 universe 上直接排全局 rank。

更像实盘的做法：
- 先按 residual correlation clustering / sector proxy / beta bucket 分层；
- 再在 bucket 内做 residual momentum rank；
- 比较全局 rank vs bucket rank 的 IC、turnover、净 Sharpe。

### 实验 5：把它当 feature，不强迫它单独成书
把 residual momentum 接到已有框架里：
- 和 `loser→winner fade` 组合
- 和 `funding / basis crowding` 组合
- 和 `liquidity filter / turnover throttle` 组合

先回答一个更现实的问题：

> **它是一个独立 alpha，还是一个能明显提升别的横截面 alpha 质量的去噪特征？**

## 8. 最后一句话结论
这轮最值得 intake 的，不是“residual momentum 在美股里很经典”这件事，而是：

> **对 crypto short-cycle desk，`BTC-beta-neutral residual ranking` 提供了一条很干净的横截面 raw alpha 思路：先把市场 drift 剥掉，再看真正属于资产自身的 continuation。**

但同样要说清楚 first verdict：

> **去 beta 确实减噪，可它还没有神奇到让 `15m` 直译版自动过成本。更靠谱的下一步，是把它往 `1h/4h` state、bucket-neutral rank、或“residual continuation vs residual reversal”符号测试上推进。**

## 9. 来源与引用
1. **David Blitz, Joop Huij, Martin Martens (2011). _Residual Momentum_. Journal of Empirical Finance, 18(3), 506-521. DOI:** `10.1016/j.jempfin.2011.01.003`  
   Readable URL: <https://doi.org/10.1016/j.jempfin.2011.01.003>
2. **David Blitz, Joop Huij, Martin Martens (2013). _Residual Momentum_. SSRN. DOI:** `10.2139/ssrn.2319861`  
   Readable URL: <https://doi.org/10.2139/ssrn.2319861>
3. **VedantUpasani46 (2026). _Alpha-Research-Discovery_. GitHub repository.**  
   Repo URL: <https://github.com/VedantUpasani46/Alpha-Research-Discovery>
4. **Relevant implementation file:** `alpha_14_residual_momentum.py`  
   Raw URL: <https://raw.githubusercontent.com/VedantUpasani46/Alpha-Research-Discovery/master/alpha_14_residual_momentum.py>
