# 别把这份 2026 market-neutral repo 只读成韩国上币工作流：对 desk 更该先测的是「cheapest spot + richest perp」跨 venue contango capture raw alpha，但 admission 阈值必须高于费用壳

- 时间：2026-03-31 17:48 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/relative-value/stat-arb/carry/basis/cross-venue/spot-perp/contango/market-neutral/cheapest-spot/richest-perp/1m/3m/5m/repo/public-data/cost/execution
- 证据类型：2026 GitHub 新仓库 source audit（README + `config.py` + `overseas/price_analyzer.py` + `overseas/trade_executor.py` + `overseas/app.py`）+ Bybit/GateIO/OKX 三交易所公开 orderbook 即时 sanity check

- 主题类型：raw alpha
- 基础 alpha：同一资产在不同 venue 的 **spot ask / perp bid** 会阶段性失衡；当 `最便宜 spot` 与 `最贵 perp` 的 fee-adjusted contango 足够大时，后续更可能向收敛方向回落
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主材料不是论文，而是一份刚在 2026-03 更新的 GitHub 仓库：**`sueun-dev/crypto-market-neutral-platform`**。

它 headline 写的是：
- KRW premium workflow；
- 韩国上币 / 海外对冲自动化；
- market-neutral platform。

但如果按我们当前 desk 的优先级来读，**最值得单独拎出来进素材池的，并不是韩国场景本身，而是仓库里已经写得很完整的 overseas 子系统**：

**实时扫描所有 venue 的 `spot ask` 与 `perp bid`，选出 `cheapest spot + richest perp` 的最佳净价差，只在 fee-adjusted contango 足够大时做 `long spot / short perp`，然后等 spread 收敛后配对平仓。**

翻成人话：
这不是“新闻套利”也不是“上币叙事”，而是一条可以直接拆成 **entry / exit / sizing / risk / cost** 的跨 venue 相对价值 raw alpha。

## 2. 为什么它值得进当前研究池
最近几轮 digest 已经补了不少：
- same-underlier basis；
- cross-venue funding carry；
- options synthetic forward；
- pairs / PCA / copula / cointegration；
- stablecoin / quote-leg parity。

但当前池子里还缺一块很实用的中间层：

**“不靠长期 funding，不靠复杂 pair formation，只用实时最便宜 spot 和最贵 perp 的净差，能不能做成一个更短、更直接的跨 venue contango capture？”**

这份 repo 值得补有 4 个原因：
1. **base alpha 很清楚**：不是 filter，不是 overlay，就是同一资产跨 venue spot-perp 净溢价的收敛；
2. **是完整策略，不是概念卡**：仓库已经给了扫描、下单、配对、风控和并发参数；
3. **天然兼容 1m / 3m / 5m**：这条线本质是 quote/pocket alpha，比 15m K 线形态更接近事件驱动短时相对价值；
4. **非常适合做最小 falsification**：直接用公开 orderbook 就能先验证“机会有没有厚到能盖过费用”。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 同一资产在不同交易所的 spot ask 与 perp bid 会暂时失衡；当 `最便宜 spot` 和 `最贵 perp` 的 fee-adjusted contango 被拉得足够开时，随后更可能向收敛方向回归。**

所以它本质上是：
- `relative-value`
- `stat-arb`
- `carry / basis pocket capture`
- 但交易对象不是 two-coin pair，而是 **same-underlier, cross-venue, spot-vs-perp** 的腿间错价。

## 4. 核心来源
### 4.1 主仓库
- **Author / Owner**：sueun-dev
- **Year**：2026（repo 创建于 2025-09-27，最近一次 push 为 2026-03-11）
- **Title**：*crypto-market-neutral-platform*
- **Venue**：GitHub repository
- **DOI**：无
- **Repo URL**：https://github.com/sueun-dev/crypto-market-neutral-platform

### 4.2 这次实际重点看的文件
- `README.md`
- `src/overseas_exchange_hedge/config.py`
- `src/overseas_exchange_hedge/overseas/price_analyzer.py`
- `src/overseas_exchange_hedge/overseas/trade_executor.py`
- `src/overseas_exchange_hedge/overseas/app.py`

### 4.3 本地即时 sanity check 数据源（公开可得）
- **Bybit spot/perp orderbook**：`/v5/market/orderbook`
- **GateIO spot orderbook**：`/api/v4/spot/order_book`
- **GateIO USDT perp orderbook**：`/api/v4/futures/usdt/order_book`
- **OKX books**：`/api/v5/market/books`
- 数据公开性：公开 REST，无需私钥即可拿 top-of-book
- 更新频率：秒级，天然适合 `1m / 3m`；聚合后也可映射到 `5m`

## 5. 仓库里最该拿走的硬点
### 5.1 这份 repo 的信号骨架非常直接：所有 venue 里找“最便宜现货”和“最贵合约”
`price_analyzer.py` 里真正关键的，不是花哨的统计，而是一个非常 desk 化的实时 ranking：

- 对每个 venue 同时抓 `spot order book` 与 `perp order book`；
- 用 `spot ask` 代表买入现货成本；
- 用 `perp bid` 代表做空永续的可成交价；
- 再把 spot taker fee 和 futures taker fee 显式扣进去：
  - `effective_spot = spot_ask * (1 + spot_fee)`
  - `effective_perp = perp_bid * (1 - perp_fee)`
- 最后算：
  - `net_spread = (effective_perp - effective_spot) / effective_spot`

然后它不是只看单一 venue，而是：
**遍历所有 `spot_exchange × perp_exchange` 组合，选出净价差最大的那一组。**

这点很重要：
它让策略从“某个交易所的 basis”升级成了 **跨 venue 的最佳路由问题**。

### 5.2 config 已经把第一版完整策略壳写出来了
`config.py` 的默认运行参数是：
- `ENTRY_AMOUNT = 100 USDT`
- `MAX_ENTRIES = 40`
- `PRICE_DIFF_THRESHOLD = 0.0015`（15 bps）
- `SLEEP_SEC = 3`
- `FUTURES_LEVERAGE = 1`

翻成人话：
- 每次先用小额试探；
- 最多分 40 次建仓；
- 每 3 秒重扫一次；
- 永续只上 1x；
- 看到 contango 超过阈值才动手。

这已经不是“想法”，而是非常接近 live monitor + execution shell 的第一版。

### 5.3 它不是 paper alpha，而是 execution-aware alpha
`trade_executor.py` 里有几个非常值得 desk 抄走的工程点：
- **先发 perp，收到 ACK 就允许继续 spot leg**：`PROCEED_ON_PERP_ACK = True`
- **fill polling + myTrades fallback**：减少单边成交不确定性
- **强制 1x leverage / one-way mode**：不让 hedge 壳滑向高杠杆方向赌波动
- **最小 notional / precision-aware sizing**：避免“理论有 edge，实盘下不出去”

所以这份材料真正值钱的地方，不只是“价差能回归”，而是：
**它已经把跨 venue delta-neutral contango capture 写成了真实 desk 会关心的样子。**

### 5.4 unwind 逻辑也给了一个很实用的 exit 原型
`app.py` 的海外清算部分，不是无脑平仓，而是等：
- `spot bid` 与 `perp ask` 的 gross spread 收敛到一个更窄区间；
- 默认用 `abs(gross_spread) <= 0.10%` 作为 paired close 的触发条件之一；
- 然后按匹配数量 chunked unwind。

这说明它的 exit 不是“时间到了就关”，而是：
**把 PnL realization 继续写成 spread 收敛过程。**

## 6. 这份 repo 最重要的 desk 化读法：15 bps admission 阈值太低，几乎只够覆盖最便宜的单次入场费用
仓库默认 `PRICE_DIFF_THRESHOLD = 15 bps`，但如果照它自己的 taker fee 表来算，**仅仅开仓这一脚的费用壳就已经在 15~25.5 bps 之间**：

- 最便宜组合约 **15 bps**：
  - `Bybit/OKX spot 10 bps + GateIO/OKX perp 5 bps`
- Bybit 自家 spot + perp 约 **15.5 bps**
- 最贵组合约 **25.5 bps**：
  - `GateIO spot 20 bps + Bybit perp 5.5 bps`

所以如果只按 15 bps admission：
- 你只是刚好覆盖最便宜的开仓壳；
- 还没算 exit taker；
- 还没算 legging 风险；
- 还没算滑点；
- 更没算 orphan risk。

**这篇东西最值得 desk 拿走的不是“15 bps 就上”，而是：这条 raw alpha 存在，但 admission 必须改成 fee-aware，而不是写死一个拍脑袋阈值。**

## 7. 三交易所公开 top-of-book 即时 sanity check：现在这条线不是 always-on，而是 pocket-driven
我用 Bybit / GateIO / OKX 的公开 orderbook，对 23 个常见币（BTC、ETH、SOL、XRP、DOGE、ADA、SUI、LTC、BCH、LINK、AVAX、TRX、DOT、BNB、PEPE、UNI、APT、ARB、OP、ETC、NEAR、FIL、ATOM）做了一个即时 snapshot sanity check。

口径很简单：
- 每个交易所取 `spot ask` 和 `perp bid` 的 top-of-book；
- 用仓库自己的 taker fee 表做 fee-adjusted net spread；
- 穷举 `spot venue × perp venue`，找当下的 best combo。

### 7.1 结果：**23/23 没有一个币在当下快照里出现正的 after-fee entry spread**
也就是：
- **positive opportunities = 0 / 23**
- 这条线不是“永远有票”；
- 更像是 **事件型 pocket / 供需短时撕裂** 出现时才值得开火。

### 7.2 当下最接近可做的几个也仍然是负的
在 2026-03-31 17:48 UTC 左右的快照里：
- **BTC best combo ≈ -17.4 bps**
  - buy `OKX spot @ 67686.9`
  - short `Bybit perp bid @ 67674.1`
- **ETH best combo ≈ -18.8 bps**
  - buy `OKX spot @ 2099.37`
  - short `OKX perp bid @ 2098.56`
- **AVAX best combo ≈ -19.5 bps**
  - buy `OKX spot @ 8.837`
  - short `OKX perp bid @ 8.833`

翻成人话：
- 大部分时候，市场自己已经把这条边抹得很薄；
- 如果没有 listing、单 venue 扫单、funding clock、或局部 inventory squeeze 之类的事件，**光看静态 contango 是不够肥的**。

### 7.3 这不等于 alpha 不存在，反而说明正确玩法是“等 pocket”，不是“常开引擎”
这条 sanity check 对 desk 的价值，不是证明 repo 无效，而是告诉你：

**这是一条需要事件式 admission 的 relative-value alpha，不是全天候持续刷单 alpha。**

因此：
- 可以做；
- 但要等；
- 而且要有比 repo 默认值更严格的触发门槛。

## 8. 对 1m / 3m / 5m / 15m 的正确读法
### 8.1 这条线天然更偏 `1m / 3m`
原因很直接：
- 信号源是 top-of-book / quote dislocation；
- 价差修复通常比 K 线形态演化快得多；
- 你等到 15m 收盘再看，很多 pocket 早没了。

所以这条 raw alpha 最自然的顺序是：
1. **先做 `1m / 3m` 事件 pocket 采样**；
2. 再看能否降采样成 `5m` 的 slower router；
3. `15m` 最多拿来做 regime / venue-health 过滤，不适合当主触发频率。

### 8.2 但它仍然服务当前 desk
虽然更快，但它和我们当前 desk 的关系是直接的：
- 它补的是 **relative-value / stat-arb / carry** 这条原始 raw alpha 素材；
- 不是继续围绕 breakout / retest 打转；
- 而且其中的 fee-aware admission、legging、paired unwind，又能反哺很多更慢策略的 execution layer。

## 9. 这篇东西怎么拆成可执行策略
### 9.1 Universe
先只做：
- 同时在 2~3 个 venue 都有足够深度的币；
- `spot` 与 `USDT perp` 都可交易；
- 先从 BTC / ETH / SOL / XRP / DOGE / LINK / AVAX 这类通用标的起步。

### 9.2 Signal
定义：
- `entry_spread(i, s_ex, p_ex, t) = (perp_bid * (1 - f_perp) - spot_ask * (1 + f_spot)) / spot_ask`
- 每一时刻对所有 `s_ex × p_ex` 组合取最大值

只有当：
- `best_entry_spread >= θ_entry`
- 且 quote 没过期
- 且 top-of-book size 够
- 且 funding 没明显反向吞噬预期收益

才允许：
- `long cheapest spot`
- `short richest perp`

### 9.3 Exit
可以先做最朴素版本：
- `best_exit_spread <= θ_exit`
- 或 hold 超过 `H` 分钟
- 或价差继续扩大到 `stop_spread`
- 或腿间其中一边 quote stale / venue health 失常

第一版可以测：
- `θ_entry ∈ {25, 35, 45, 60} bps`
- `θ_exit ∈ {0, 5, 10} bps`
- `H ∈ {3, 5, 10, 30} min`

### 9.4 Sizing
- 按弱腿 top-of-book volume 决定最大 notional；
- 强制 `1x` perp；
- 单币、单 venue、单时刻都设 notional 上限；
- 并发数不要高于真实可配对资金数量。

### 9.5 Risk / Cost
这条线最重要的不是方向，而是 operational risk：
- 双腿 taker fee
- 双腿 exit fee
- slippage
- legging delay
- orphan leg
- venue API fail
- withdraw/transfer 不应假设当场可做

正确假设应该是：
**预先在各 venue 都有库存与保证金，做的是已预注资的跨 venue 对冲，不是临时搬砖。**

## 10. 下一步怎么测
### 实验 1：先验证 pocket 有没有厚度
用公开 API 录 `1s / 5s` top-of-book：
- 交易所：Bybit / GateIO / OKX
- 标的：先 10~20 个高流动币
- 周期：至少 14 天

输出：
- after-fee positive spread 出现频率
- 按币种 / venue pair 分层的 `p95 / p99 spread`
- pocket 持续时长分布

### 实验 2：做事件窗，不急着先做全回测
对所有 `best_entry_spread >= θ_entry` 的时刻做 event study：
- 1 / 3 / 5 / 10 / 30 分钟后 spread 收敛多少
- hit-rate
- max adverse excursion
- median time-to-close

这一步能最快回答：
**它到底是“会回”还是只是“偶尔看着肥”。**

### 实验 3：把 legging 风险写进来
对每次信号额外模拟：
- 250ms / 1s / 3s 延迟
- 只按 top-of-book 成交
- quote stale veto
- orphan leg 强平

如果一加延迟边就没了，这条线就只能留给更低延迟系统，不适合当前 desk。

### 实验 4：找 pocket 触发器，而不是盲扫全天
如果实验 1~3 有边，再往上叠最可能有用的 filter：
- funding clock 附近
- 单 venue 大额扫单 / depth 抽空
- 上币 / 事件 / 单 venue inventory shock
- 高 realized vol 但 quote 仍未同步的窗口

也就是说，**第二阶段重点不是调参数，而是回答“什么时候这条边会厚起来”。**

## 11. 结论
这份 repo 值得进研究池，但要用对读法。

它真正该留下来的不是：
- 韩国上币 narrative；
- 15 bps 固定阈值；
- “market-neutral 一定稳”。

而是：

**一条可独立复现、可直接落地、非常适合 `1m / 3m / 5m` 做最小实验的 raw alpha：`cheapest spot + richest perp` 的跨 venue fee-adjusted contango capture。**

当前最关键的 desk 结论是：
1. **这条 alpha 本体成立，且不是 filter；**
2. **repo 已经把它写成完整执行壳；**
3. **但默认 15 bps admission 明显过松，必须改成 fee-aware threshold；**
4. **即时 sanity check 显示它不是 always-on，而是 pocket-driven，所以研究重点应放在“机会出现的条件”和“机会能活多久”。**

如果只给一个最小动作：
**先别回测整年；先录 14 天三交易所 top-of-book，做 `after-fee positive spread` 的事件窗统计。**

这一步最省时间，也最能决定这条线该不该进下一轮复现队列。