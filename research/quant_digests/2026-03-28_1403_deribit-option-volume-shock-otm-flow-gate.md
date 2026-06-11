# 别把 Bitcoin options flow 只读成 IV 解释：更该先测的是「Deribit option-volume shock × OTM directional gate」BTC 短周期 raw alpha

- 时间：2026-03-28 14:03 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/single-asset/options-flow/deribit/bitcoin/perp/volume-shock/directional-gate/volatility-learning/otm/dotm/public-data/5m/15m/paper/external-data/cost
- 证据类型：2022 arXiv 全文 PDF 本地抽取 + Deribit 官方 API 文档

## 0. 四个先答字段

- 主题类型：raw alpha
- 基础 alpha：**Deribit BTC options 的成交量冲击（volume shock）对下一段 BTC 现货/永续收益与波动有短暂预测力；而短期限 OTM/DOTM 的 call-vs-put directional pressure 更适合拿来做选边 / veto，而不是单独冒充主信号。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么

这次主看的是一篇直接研究 **Deribit 比特币期权逐笔成交信息** 的论文：

- **Authors**：Carol Alexander, Jun Deng, Jianfen Feng, Huning Wan
- **Year**：2022（version date: 2022-03-28）
- **Title**：*Net Buying Pressure and the Information in Bitcoin Option Trades*
- **Venue**：arXiv, q-fin.GN
- **DOI**：未见
- **Readable URL**：https://arxiv.org/abs/2109.02776
- **PDF URL**：https://arxiv.org/pdf/2109.02776v2.pdf
- **Repo URL**：未见作者配套 repo

辅助确认的数据落地路径来自 Deribit 官方文档：

- `public/get_last_trades_by_currency`：可直接拉 `BTC`、`kind=option` 的公开逐笔成交，含 `instrument_name / timestamp / direction / amount / iv / index_price / price`
  - https://docs.deribit.com/api-reference/market-data/public-get_last_trades_by_currency.md
- `public/get_instruments`：可拿到 option 元数据，含 `expiration_timestamp / strike / option_type / instrument_name`
  - https://docs.deribit.com/api-reference/market-data/public-get_instruments.md

**一句话结论**：
这篇 paper 真正适合 desk 化的，不是“把 aggregate NBP 直接当方向键”，而是拆成两层：

1. **raw alpha 主体**：`BTC option volume shock -> 下一小时 BTC 回报/波动继续动`；
2. **direction gate**：`短期限 OTM/DOTM call-put directional pressure` 用来判断这次 options activity 更像“方向下注”还是“纯波动下注”。

这就比“直接复刻论文 headline：NBP 解释 smile 变化”更适合我们现在的 `5m / 15m` 短周期研发池。

## 2. 为什么它值得进当前研究池

对当前 desk，这个题目的价值在于它补的是一个**还没被充分系统化的高频外部信息层**：

- 不是慢频宏观，也不是只能当天后验解释的新闻；
- 是 **公开、实时、可逐笔订阅** 的交易流；
- 它既能服务 **单币方向 raw alpha**，也能服务 **波动模式切换 / sizing / veto**；
- 即使最后发现“方向 edge 不够厚”，也依然能沉淀成一个很有价值的 shared component：
  - `volume shock` 状态层
  - `directional-vs-volatility` flow decomposition
  - `OTM/DOTM short-dated` admission layer

所以这不是“纯解释型 options microstructure 阅读”，而是很典型的 **raw alpha + gate 可拆分材料**。

## 3. 论文里真正能拿来交易的证据

### 3.1 数据与样本口径

论文样本（第 1、14 页附近）是：

- **市场**：Deribit BTC options
- **频率**：tick-level trades（逐笔）
- **样本期**：**2017-01-01 到 2021-07-28**
- **来源**：作者说明原始样本通过 Deribit API 获取；现在 Deribit 不再方便提供完整历史，长历史可通过 **Tardis / CoinAPI**，但**实时与近期 recent history 仍可通过 Deribit 公共 API 直接拿到**。

论文里给了几个对 desk 很有用的背景数：

- Deribit BTC options 名义成交额从 **2017 年的 0.26B USD** 增到 **2021 年（截至 7 月）的 102.96B USD**；
- 2021 年样本里，成交主要集中在 **OTM / DOTM / ATM**；
- 短期限期权占比明显抬升，说明把它压到 `5m / 15m` 的短周期事件流上，并不违和。

### 3.2 最值钱的结果不是“aggregate NBP 预测收益”，而是“volume shock 预测收益”

第 15-16 页 Table 5 是这篇 paper 最适合我们短周期 desk 化的一张表。

作者先做：

\[
 x_t = \gamma_0 + \gamma_1 x_{t-1} + \gamma_2 y_{t-1}, \quad x \in \{r, \Delta IV, \Delta RV\},\ y \in \{\Delta v, N\}
\]

其中：

- `Δv` = options trading volume change
- `N` = aggregate order imbalance / aggregate net buying pressure

关键结果：

1. **成交量冲击对未来收益有显著预测力**
   - **1-hour return**：`γ2 = 0.27***`
   - **1-day return**：`γ2 = 0.51***`
   - **5-day return**：`γ2 = 0.068`（不显著）

   这非常像一个**短命、短持有期**的事件型 alpha，而不是慢频 carry。

2. **aggregate order imbalance 对未来收益不显著**
   - 1-hour：`8.43e-7`
   - 1-day：`-1.38e-6`
   - 5-day：`-6.08e-6`

   也就是说：**别把总 NBP 直接当方向键。**

3. **但成交量与 NBP 都能预测未来波动 / IV**
   - 对 `ΔIV` 和 `ΔRV`，`Δv` 与 `N` 都显著；
   - 其中 `Δv -> ΔIV` 的显著性最持久，甚至延续到后面几天。

所以这篇 paper 给 desk 的最重要启发其实是：

> **方向 raw alpha 的主信号更像是 volume shock；而 flow imbalance 更像“这次 volume shock 到底偏方向交易还是偏波动交易”的分类器。**

### 3.3 directional information 并非没有，但主要藏在 OTM / DOTM，而不是 ATM

论文第 17-18 页把净买压拆成两部分：

对某个 moneyness 桶 `k`，先定义 call/put 各自的 delta-weighted net buying pressure：

\[
A^k_{j,t}=\sum B^k_{ij,t}|\Delta^k_{ij,t}|-\sum S^k_{ij,t}|\Delta^k_{ij,t}|,
\quad j\in\{C,P\}
\]

然后拆成：

- **Directional-motivated demand**
\[
D^k_{C,t}=\frac{A^k_{C,t}-A^k_{P,t}}{2},\quad
D^k_{P,t}=\frac{A^k_{P,t}-A^k_{C,t}}{2}
\]

- **Volatility-motivated demand**
\[
V^k_t=\frac{A^k_{C,t}+A^k_{P,t}}{2}
\]

解释非常直白：

- `D^k_C > 0`：更像在用 call 相对 put 表达**看涨方向信息**；
- `D^k_C < 0`：更像在表达**看跌方向信息**；
- `V^k > 0`：更像在表达**看波动上升**，不一定告诉你涨跌方向。

作者把 moneyness 分成五档（第 11-12 页附近）：

- DOTM：`0.02 < |Δ| <= 0.125`
- OTM：`0.125 < |Δ| <= 0.375`
- ATM：`0.375 < |Δ| <= 0.625`
- ITM：`0.625 < |Δ| <= 0.875`
- DITM：`0.875 < |Δ| <= 0.98`

而真正和方向信息更有关系的，不是 ATM，而是 **OTM / DOTM**。

### 3.4 Table 7 / Table 8：OTM 与 DOTM 同时带 volatility learning 和 directional learning，但前者更强

第 25-27 页的回归结果可以直接转成 desk 语言：

1. **市场制造商库存约束很强，且比成熟市场更强**
   - `α5` / `β5` 普遍在 **-0.39 到 -0.46** 左右且高度显著；
   - 作者直接说这比 S&P 500/TAIEX 的绝对值更大，意味着 **Deribit options market maker inventory pressure 更重**。

   Desk 含义：options flow 的信息可能更容易先体现在 IV / quote 调整里，而不一定无摩擦传到 spot/perp。

2. **ATM 主要是 volatility learning，不太像纯方向信号源**
   - 2021 ATM call：`β3 = 0.215***`, `β4 = 0.184**`
   - 2021 ATM put：`β3 = 0.011`, `β4 = -0.243***`

   这说明 ATM activity 很容易混着 volatility trade，拿来直接做 perp 方向键会很脏。

3. **OTM/DOTM 才是方向信息更值得看的地方**
   - 2021 **OTM call**：`β3 = 0.484***`, `β4 = 0.335***`
   - 2021 **DOTM call**：`β3 = 2.493***`, `β4 = 1.756***`
   - 2019 短期限 **OTM call [1,7 days]**：`β3 = 22.084***`, `β4 = 3.808`

   这里 `β3` 是 volatility-motivated pressure，`β4` 是 directional-motivated pressure。

   结论不是“direction > vol”，恰好相反：

   - **volatility-motivated demand 整体更强**；
   - 但 **directional demand 在 OTM/DOTM 是存在且可辨认的**；
   - 所以它最适合干的不是“独立顶替主 alpha”，而是给 volume shock 做 **方向分类与 veto**。

### 3.5 一个容易被忽略、但很适合 desk 的分叉结论

论文自己的 headline 更偏向“期权净买压如何影响 smile/IV”。

但对短周期 desk，更有价值的分叉其实是：

- **主 alpha**：`option volume shock`
- **辅助分类层**：`OTM/DOTM short-dated D_t`
- **波动模式层**：`V_t`

这正好符合我们当前“不要只抄 headline，要优先拆能快速复现的 raw alpha / gate / overlay 组件”的 intake 原则。

## 4. desk 化后的最小策略骨架

下面给的是一个可以直接进入最小实验的版本，不是纸上谈兵。

### 4.1 交易对象

- **信号市场**：Deribit BTC options
- **执行市场**：BTC perp（优先 Binance / Deribit perp 任一高流动 venue）
- **默认频率**：`15m`
- **更快版本**：`5m`

### 4.2 信号定义

#### Signal A：option volume shock（主 alpha）

每个 bar（`5m` 或 `15m`）聚合所有 BTC option trades：

- `gross_option_volume_t`：成交量总和（按 BTC 名义或美元名义都可以，先两套都测）
- `signed_trade_count_t`：可作为次要稳定性特征
- `Δv_t`：对 `gross_option_volume` 做变化率或 rolling z-score

推荐先用最稳的版本：

- `volshock_z_t = zscore(log(1 + gross_option_volume_t), lookback=20~40 bars)`

raw alpha 假设：

- `volshock_z_t` 很高时，下一小时 BTC 更容易继续走出**可交易净位移**；
- 但方向要靠下面的 `D_t` 来分边。

#### Signal B：short-dated OTM/DOTM directional gate（方向选边）

只看：

- `TTM <= 7 days`
- `0.02 < |delta| <= 0.375`
  - DOTM + OTM

计算：

- `A_call_t`
- `A_put_t`
- `D_t = (A_call_t - A_put_t) / 2`
- `V_t = (A_call_t + A_put_t) / 2`

对 `D_t` 和 `V_t` 再各自 rolling z-score：

- `dir_z_t = zscore(D_t)`
- `volinfo_z_t = zscore(V_t)`

解释：

- `dir_z_t >> 0`：options flow 更像**看涨方向下注**
- `dir_z_t << 0`：更像**看跌方向下注**
- `volinfo_z_t >> 0` 且 `|dir_z_t|` 不高：更像**纯波动交易**，这时做方向单要保守

### 4.3 入场规则（最小可复现版）

#### 15m 版本

- **Long entry**
  1. `volshock_z_t >= 1.5`
  2. `dir_z_t >= 0.75`
  3. `abs(dir_z_t) / max(abs(volinfo_z_t), 1e-6) >= 0.33`
     - 避免“全是 vol trade，几乎没方向信息”

- **Short entry**
  1. `volshock_z_t >= 1.5`
  2. `dir_z_t <= -0.75`
  3. 同样要求方向占比门槛

#### 5m 版本

门槛略抬高，避免噪音：

- `volshock_z_t >= 2.0`
- `|dir_z_t| >= 1.0`

### 4.4 出场规则

先用和论文最一致的“1 小时短持有”骨架：

- `15m`：持有 **4 bars**
- `5m`：持有 **12 bars**

同时加两个简单风控：

- **止损**：`1.0 x ATR(20)`
- **止盈 / 提前平仓**：
  - 反向 `dir_z_t` 出现；或
  - `volshock_z_t` 在下一 bar 迅速回落到 0 附近，表示事件没延续

### 4.5 仓位与风控

- 基础仓位：按 perp 波动目标做 vol targeting
- 放大条件：`volshock_z_t` 高且 `|dir_z_t|` 高
- 缩小 / 不做：
  - `volinfo_z_t` 很高，但 `|dir_z_t|` 很低
  - 说明更像 **long-vol / short-vol 交易挤在 options 里**，未必有明确方向边

一个简单可执行的 sizing：

\[
size_t = size_0 \times \min(2.0, \max(0, volshock_z_t-1)) \times \min(1.5, |dir_z_t|)
\]

然后再乘：

- `0.5`，如果 `|dir_z_t| / |volinfo_z_t| < 0.5`
- `0`，如果 `|dir_z_t| / |volinfo_z_t| < 0.25`

### 4.6 成本与执行要求

这类信号能不能活，关键不在 paper 的 t 值，而在你能不能把它做成**大于 perp 全成本**的净位移。

必须单独记录：

- perp taker / maker fee
- 实际滑点
- 信号触发后 1 bar 内是否已经被 chase 掉
- `5m` vs `15m` 哪个更容易留下净利润

我的默认判断：

- **15m 更像第一站**，因为论文最强结果对应的是“下一小时”；
- `5m` 可以做，但大概率要更高门槛，且对 execution 更敏感。

## 5. 为什么我把它定为 raw alpha，而不是纯 filter

因为这里的 **base alpha 很清楚**：

> **option volume shock 本身就是一个独立可测的、短持有期的 BTC directional/volatility event alpha。**

不是那种“先有别的主策略，我再给你加个修饰层”的材料。

当然，它不是“裸 volume 一把梭”——需要 `dir_z` 和 `volinfo_z` 来拆语义。

所以更准确地说，这是一条：

- **raw alpha 主体**：`volume shock`
- **regime / confirmation 层**：`OTM/DOTM directional-vs-volatility decomposition`

这完全符合“**可清楚拆成 raw alpha + regime/filter**”这一档，而且主 alpha 不是虚的。

## 6. 数据可得性与最小复现实验口径

### 6.1 数据源

**公开可得**：是。

1. **Deribit `public/get_last_trades_by_currency`**
   - 拉 `currency=BTC`, `kind=option`
   - 有 `timestamp / direction / amount / iv / index_price / instrument_name`
2. **Deribit `public/get_instruments`**
   - 拿 `expiration_timestamp / strike / option_type`
3. **执行腿市场数据**
   - Binance / Deribit BTC perp 的 1m K 线或逐笔均可公开拿到

### 6.2 更新频率

- options trades：逐笔、实时
- instrument metadata：低频更新即可
- perp execution bar：1m 聚合后再压到 `5m/15m`

### 6.3 最小可复现实验口径

#### Public-only live / recent backfill 版本

- 连续采集 **2~4 周** Deribit BTC option trades
- 聚合成 `5m`、`15m`
- 计算 `volshock_z`, `dir_z`, `volinfo_z`
- 执行腿用 BTC perp
- 测：
  - horizon = `1, 2, 4, 8` bars
  - long / short 分开
  - 只做 `TTM<=7d` vs 全部期限
  - 只做 `OTM+DOTM` vs `ATM+OTM+DOTM`

#### 如果要更长回测

- 论文明确提到：Deribit 现在不再方便提供完整老历史；
- 长历史需要 **Tardis / CoinAPI** 或自建录制。

所以这条 alpha 的现实落地路径很明确：

- **先做 live-forward / recent history 最小实验**；
- 过关后再决定是否买历史档案做更长回测。

这比一开始就上重型数据采购更合适。

## 7. 这条信号最容易踩的坑

### 7.1 把 aggregate NBP 误当方向键

论文已经很清楚：

- `N` 对未来 return **不显著**；
- 真正对 return 有意义的是 **volume shock**；
- `N` / `D` / `V` 更像解释“这波 options flow 的语义”。

### 7.2 ATM 太脏

ATM 很容易吸进大量纯波动交易。

如果你把 ATM 也和 OTM/DOTM 一样当方向信息源，signal purity 大概率会掉得很快。

### 7.3 市场成熟后，edge 可能变薄

论文自己就强调：

- 2019 -> 2021，部分系数在衰减；
- Deribit 逐渐成熟，market maker inventory 管理也会改善。

所以我们不该默认 paper 里的系数现在原封不动还在，而应该把它当 **live alpha intake**：

- 先测现在是否还活；
- 再决定要不要升成生产素材。

### 7.4 这更像 BTC 主信号，不是现成山寨横截面信号

它最自然的第一落点是：

- `BTC perp directional event alpha`

而不是立刻外推到 alt basket。后者可以做二期：测 `BTC options flow shock -> alt beta spillover`，但不应在本轮一上来就混进去。

## 8. 下一步怎么测

### 实验 1：先验证最核心命题

**命题**：Deribit BTC options 的 `volume shock × OTM/DOTM directional gate` 能否在 BTC perp `15m` 上留下净成本后 alpha。

- bar：`15m`
- 入场：`volshock_z >= 1.5` 且 `|dir_z| >= 0.75`
- 出场：持有 `4 bars`
- 成本：按真实 fee + conservative slippage
- 输出：
  - hit rate
  - average net return
  - information ratio / Sharpe
  - long/short 分解
  - 分 bucket（高 `volinfo_z` / 低 `volinfo_z`）

### 实验 2：验证 direction gate 是否真的有增益

做三组对照：

1. `volume shock only`
2. `volume shock + dir_z`
3. `volume shock + dir_z + volinfo veto`

如果 2/3 明显优于 1，说明这篇 paper 的 desk 化分叉是对的。

### 实验 3：5m 压缩测试

- 同样信号逻辑压到 `5m`
- 但把触发阈值抬高
- 看 edge 是被提早交易掉，还是确实还能留下更快 alpha

### 实验 4：只看短期限 vs 全期限

比较：

- `TTM <= 7d`
- `TTM <= 21d`
- `all maturities`

我预期：**短期限版本更干净**，因为论文里方向信息最像是藏在短期限 OTM/DOTM。

## 9. 我对这篇材料的最终判断

**结论：值得进入研究池，而且优先级不低。**

但进入研究池的方式不是：

- “复刻一篇 options-IV 解释论文”

而是：

- **把它拆成一条可独立复现的 BTC raw alpha：`option volume shock`**；
- 再把 **`OTM/DOTM directional-vs-volatility decomposition`** 当作方向分边与 veto 层。

如果最小实验有效，这条东西后续有三种扩展方向：

1. 做成 **BTC 单币事件型 raw alpha**；
2. 做成 **BTC 主信号 -> alt beta spillover gate**；
3. 做成 **波动模式切换 / sizing overlay**，服务其他 raw alpha。

所以它不是只能服务一个策略的“窄论文”，而是能沉淀成 **一条主 alpha + 两条共享组件** 的高质量 intake。
