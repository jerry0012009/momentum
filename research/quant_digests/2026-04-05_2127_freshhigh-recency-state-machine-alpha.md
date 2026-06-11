# 别把这份 Hyperliquid trend repo 只读成“20 日新高 breakout”：对 short-cycle desk，更该先测的是「fresh-high recency state machine」这条完整 raw alpha

- 时间：2026-04-05 21:27 UTC
- 类型：2026 arXiv 全文 HTML source audit + 2024 GitHub repo source audit（`README.md` + `main.py` + `config.json`）+ Hyperliquid 公共 API 文档可得性确认
- 主题类型：raw alpha
- 基础 alpha：**最近 N-bar 刚创新高的币更容易继续走强；若新高长时间不再被刷新，则“高点变陈旧”本身可转成 stale-high short / flat 的反向状态机**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/breakout/fresh-high/recency-state-machine/stale-high/long-short/universe-ranking/top-volume/hyperliquid/binance-perpetual/15m/5m/3m/1m/repo/paper/public-api/cost/risk
- 证据类型：论文 + 仓库源码双证据（可读全文 HTML + 代码规则）

## 1. 这次看了什么
这轮主看两样东西：

1. **Yijia Chen (2026), _Be Water: An Evolutionary Proof for Trend-Following_**  
   - arXiv 全文 HTML 可读；
   - 核心不是给一个现成交易系统，而是给出一个对 short-cycle desk 很有用的结论框架：**在高噪声、高杠杆、胖尾环境里，trend-following 的生存性强于 buy-the-dip 式 mean reversion**。

2. **kalipsot (2024), `Hyperliquid-Basic-Trend`**  
   - repo 很小，但规则写得足够清楚；
   - 真正值得拿走的不是“20-day high”这层表面描述，而是代码里已经写成状态机的 **fresh-high recency shell**：
     - fresh high → 开多 / 持多
     - 新高变旧 → 平多
     - 旧高陈化到特定年龄 → 开空
     - 继续陈化 → 持空
     - 再过期 → 平空

这比再补一篇“trend 有效 / 无效”的泛结论更值钱，因为它直接落到了：**entry / exit / short activation / universe / sizing / execution**。

## 2. 先回答：这篇东西的 base alpha 是什么？
- 主题类型：raw alpha
- 基础 alpha：**fresh-high continuation + stale-high decay**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

这里要说清楚：

它不是“经典 Donchian breakout 再讲一遍”。

真正的 base alpha 是：
1. **某币刚创出过去 N-bar 新高时，后续更容易继续延续；**
2. **一旦这个新高长期没有再被刷新，趋势壳会从 continuation 逻辑切到 decay / exhaustion 逻辑；**
3. **这个“离上次新高过去了多久”本身，就是比单次突破更适合做短周期状态管理的变量。**

翻成人话：
> 不是“碰到新高就一直信趋势”，而是“新高也会老；新高的新鲜度在下降时，趋势 alpha 会衰减，甚至翻成反向”。

## 3. 为什么这轮值得进研究池
这轮我刻意没有再补 overlay / regime，原因很直接：

- 最近两篇 digest 已经是 **order-book liquidity timing overlay** 和 **gamma wall regime router**；
- 按当前规则，这轮应该优先回到 **raw alpha / 可完整落地策略**；
- 而这条 fresh-high recency 壳，确实比继续写一个“shared filter”更接近可交易原型。

它对当前 desk 的直接价值有三点：

1. **它是完整骨架，不只是单个因子。**  
   entry、exit、short activation、universe、杠杆、下单方式，repo 都给了原型。

2. **它不是死板 breakout，而是“breakout 的时间衰减版”。**  
   对 `5m / 15m` desk，这比“破了就追、回来了就跑”的裸 breakout 更有研究价值。

3. **它天然适合做 bar-ratio downscale。**  
   repo 用的是日级；我们完全可以保留“新高年龄比例”而不是照搬“20 天 / 15 天 / 5 天”这些绝对数字。

## 4. 源码里真正写了什么
### 4.1 repo 默认参数其实已经是一个完整策略原型
从 `config.json` 看，repo 默认：
- `leverage = 5`
- `numberOfCoins = 25`
- `sizeUSD = 150`
- `maxOpenPositions = 10`

从 `main.py` 看：
- universe = **按 24h notional volume 排序的前 N 个 Hyperliquid 币**；
- 每天 rebalance 一次；
- 下单用 **IOC limit**，价格直接在 mid 基础上加/减 **1% slippage buffer**；
- 开仓和平仓都按固定美元名义下单。

这意味着它不是“研究笔记级伪代码”，而是已经接近一个能跑的 live prototype。

### 4.2 README 和代码有出入，但代码更有价值
README 的说法是：
- 若今天创 20 日新高 → 开多；
- 若 5 天未创新高 → 平多；
- 若 15 天未创新高 → 开空；
- 若 20 天未创新高 → 平空。

但 `main.py` 里的真实实现更细，而且也更像我们想要的状态机：

`checkAthDay()` 会把“过去 20 日最高收盘离今天有多远”分桶：
- `0`：今天就是新高
- `1`：新高出现在最近 `1~3` 天内
- `2`：新高出现在 `4~13` 天前
- `3`：新高出现在 `14` 天前
- `4`：新高出现在 `15~18` 天前
- `5`：新高出现在 `19+` 天前

然后 `rebalance()` 真正规则是：

**Long 侧**
- `athDays == 0`：可开多 / 持多
- `athDays == 1`：继续持多
- `athDays >= 2`：平多

**Short 侧**
- `athDays == 3`：开空
- `athDays == 4`：继续持空
- 其他情况：平空

这就非常关键了：

> repo 真正实现的，不是“固定 20 日突破系统”，而是一个 **基于最近新高年龄的多空状态机**。

对 desk 来说，这比 README headline 更重要。

## 5. 对 short-cycle desk 最值得偷的，不是 breakout，而是“新高年龄”
### 5.1 为什么这不是又一个普通 breakout
普通 breakout 更像：
- 价格过了上轨 → 开多；
- 回到区间 → 平；
- 可能配一个 ATR stop。

而这个 repo 的有趣点在于：
- **entry 只在 fresh-high 触发**；
- **持仓不由价格相对某条线决定，而由“离上次新高过去多久”决定**；
- **short 不是单纯做反转，而是做“趋势迟迟不再续命”的 stale-high state。**

所以更贴切的理解不是 breakout，而是：
**high-age / recency-state alpha**。

### 5.2 paper 给了什么支撑
`Be Water` 这篇 2026 arXiv 虽然不是实盘回测论文，但它给了一个很像“为什么 trend 壳值得优先测”的背景结论：
- 作者在 **5 年、5 分钟频率、100 个资产、10,000 个 agent** 的模拟环境里比较不同 archetype；
- 结果是 **Trend-Following archetype** 生存下来，而 **Mean-Reversion / buy-the-dip** 更脆弱；
- 论文还把 stop / leverage / ATR 风险边界写得很明确。

我不会把这篇当成“直接可下单证据”，但它给了一个对 desk 有用的优先级判断：
**在高噪声、高杠杆环境里，先补 trend shell 是合理的；而这个 repo 恰好提供了一个更可执行的 trend shell。**

## 6. desk 版完整策略拆解
### 6.1 策略定义
**基础 alpha：** recent-high continuation；新高年龄老化后切到 stale-high decay  
**交易对象：** 流动性最好的 perp universe  
**主战场：** `15m`，`5m` 做更快版本，`3m/1m` 只做 child execution

### 6.2 策略变量
定义：
- `L_high`：看过去多少根 bar 的最高收盘
- `age_high_t`：距离最近一次 `close == rolling_max(close, L_high)` 已过去多少根 bar
- `tau_keep_long`：fresh-high 还能继续算 continuation 的最大年龄
- `tau_open_short`：从 trend decay 切到 stale-high short 的触发年龄
- `tau_close_short`：short 再继续拿就太旧的年龄上限

把 repo 规则抽象成比例就是：
- `tau_keep_long ≈ 0.20 * L_high`
- `tau_open_short ≈ 0.70 * L_high`
- `tau_close_short ≈ 0.95 * L_high`

这个“比例读法”比照搬 20 天更适合我们的 `1m/3m/5m/15m`。

### 6.3 入场 / 出场
**Long entry**
- `age_high_t == 0`
- universe 在 top liquidity bucket 内
- spread / slippage 不超阈值
- 若 BTC 本身处于极端单边反向冲击，可加 veto

**Long hold**
- `age_high_t <= tau_keep_long`

**Long exit**
- `age_high_t > tau_keep_long`
- 或 hit `ATR stop`
- 或出现极端 adverse move / microstructure veto

**Short entry**
- `age_high_t == tau_open_short` 附近
- 且价格已跌回短期均线 / VWAP 下方，避免在仍强势时硬逆势

**Short hold**
- `tau_open_short < age_high_t <= tau_close_short`

**Short exit**
- `age_high_t > tau_close_short`
- 或价格重新刷新 `L_high` 新高
- 或触发 hard stop

### 6.4 sizing / risk / cost
**sizing**
- 初版建议 `equal-risk`，单币风险预算相同；
- 同时持仓数上限先测 `6 / 8 / 10`；
- 单币 notional cap 不超过组合资金 `10%~12%`。

**risk**
- `ATR(20)` 或 `rolling sigma` 做 stop；
- 若 `age_high` 结构仍多头但 realized vol 突然翻倍，仓位减半；
- short leg 默认更小，先用 `0.5x~0.75x` long 名义。

**cost**
- 先按 taker 成本测；
- `1m/3m` 只做执行，不要把主 alpha 下沉到噪声层；
- 若 fresh-high 发生在 spread 快速放大时，宁可 miss，不要硬追。

## 7. 1m / 3m / 5m / 15m 的映射建议
### 15m（主版本）
建议先测：
- `L_high = 96 / 192 / 288`
- `tau_keep_long = round(0.20 * L_high)`
- `tau_open_short = round(0.70 * L_high)`
- `tau_close_short = round(0.95 * L_high)`

例子：
- `L_high = 96` 时：
  - `tau_keep_long = 19`
  - `tau_open_short = 67`
  - `tau_close_short = 91`

这相当于：
- 新高后还给它约 `4.75h` 的 continuation 容忍；
- 若快 `17h` 都没再创新高，就考虑 stale-high short；
- 快满 `1d` 还没新高，则 short 也应收掉。

### 5m（快版本）
保持相同物理时间：
- `L_high = 288 / 576 / 864`
- 其余阈值按同样比例算

但 5m 版必须额外加：
- spread veto
- 盘口深度 veto
- BTC 同步方向 veto

### 3m / 1m
不建议直接把主 alpha 做成 3m / 1m。
更好的用法是：
- `15m/5m` 先定方向；
- `3m/1m` 只负责更便宜的进场：
  - fresh-high 后的小回踩买入；
  - stale-high short 前的 weak bounce 卖出。

## 8. 最小可复现实验
### 实验 A：fresh-high recency shell vs 裸 breakout
**目的：** 验证“新高年龄状态机”是否优于简单 breakout 持有。

- universe：Binance USDⓈ-M / Hyperliquid perp `top 15` 流动性币
- bar：`15m`
- baseline：
  1. `close > rolling_high(L_high)` 就开多，固定持有 `H`
  2. fresh-high recency state machine
- 指标：
  - after-cost return
  - Sharpe
  - turnover
  - MDD
  - trade expectancy
  - long leg / short leg 分开归因

### 实验 B：short leg 要不要保留
**目的：** 验证 stale-high short 是 alpha 还是噪声。

并排比较：
1. `long-only fresh-high`
2. `long + stale-high short`
3. `long + stale-high short (smaller size)`

重点看：
- short leg 是否贡献净收益；
- short leg 是否只是在放大回撤；
- short leg 在高 funding / squeeze 环境下是否显著恶化。

### 实验 C：5m child execution 能否省成本
**目的：** 验证执行层是否值得。

- 主信号在 `15m`
- 执行对比：
  1. 15m 收盘直接 taker
  2. 5m 等一次回踩 / micro pullback 再进
- 看 slippage、fill rate、净收益、漏单成本。

## 9. 风险与保留意见
1. **`Be Water` 是模拟论文，不是实盘证据。**  
   它更适合作为“先补 trend shell 而不是继续补 buy-the-dip”的研究优先级依据。

2. **repo 体量小、未经过严谨学术验证。**  
   但也正因为简单，才适合拿来做最小实验。

3. **README 与源码不一致。**  
   这次必须以代码为准，不能只抄 README headline。

4. **short leg 可能并不稳定。**  
   stale-high short 听起来合理，但 crypto squeeze 风险很高；它必须单独审判，不能默认保留。

5. **绝对时间尺度不能照搬。**  
   20 天对 short-cycle desk 太慢；应保留比例结构，而不是搬原始日级参数。

## 10. 来源
1. **Chen, Yijia. (2026). _Be Water: An Evolutionary Proof for Trend-Following_. arXiv.**  
   - Author: Yijia Chen  
   - Year: 2026  
   - Title: Be Water: An Evolutionary Proof for Trend-Following  
   - Venue: arXiv  
   - DOI: <https://doi.org/10.48550/arXiv.2603.29593>  
   - Readable URL: <https://arxiv.org/abs/2603.29593>  
   - HTML URL: <https://arxiv.org/html/2603.29593>  
   - Repo URL: N/A

2. **kalipsot. (2024). _Hyperliquid-Basic-Trend_. GitHub Repository.**  
   - Author / Repo owner: kalipsot  
   - Year: 2024  
   - Title: Hyperliquid-Basic-Trend  
   - Venue: GitHub Repository  
   - DOI: N/A  
   - Readable URL: <https://github.com/kalipsot/Hyperliquid-Basic-Trend>  
   - README URL: <https://raw.githubusercontent.com/kalipsot/Hyperliquid-Basic-Trend/master/README.md>  
   - Code URL: <https://raw.githubusercontent.com/kalipsot/Hyperliquid-Basic-Trend/main/main.py>  
   - Config URL: <https://raw.githubusercontent.com/kalipsot/Hyperliquid-Basic-Trend/main/config.json>

3. **Hyperliquid Docs. Info endpoint / public market data docs.**  
   - Readable URL: <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint>

4. **Binance USDⓈ-M Futures market data docs（用于 desk 侧最小复现实验的数据替代）**  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api>

## 11. 下一步怎么测（一句话）
先在 `15m top-15` 流动性 perp 池上，把 `fresh-high recency state machine` 与 `裸 breakout`、`long-only fresh-high`、`long+stale-high short` 四条线并排回测；如果结果显示 **“新高年龄”比单次突破更能稳定决定持有/翻空节奏**，就把它升级成 desk 的标准 trend raw alpha 骨架。