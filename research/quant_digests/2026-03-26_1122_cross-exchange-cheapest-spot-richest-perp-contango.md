# 别把韩国 market-neutral 仓库只读成“跨境出金流程”：更该先测的是「跨交易所 cheapest-spot / richest-perp 净价差收敛」完整 raw alpha

- 时间：2026-03-26 11:22 UTC
- 类型：2026 GitHub 新仓库 + 2019/2023 论文地基 + Bybit/OKX/Gate 公共 order-book live quick check
- 主题类型：raw alpha
- 基础 alpha：当多交易所里 **最便宜的 spot ask** 与 **最贵的 perp bid** 的**费后净价差**超过阈值时，做 `long cheapest spot / short richest perp`，赚跨交易所现货-永续的收敛，而不是赌单腿方向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/cross-exchange/spot-perp/contango/carry/market-neutral/cheapest-spot-richest-perp/bybit/okx/gateio/1m/3m/5m/15m/repo/paper/external-data
- 证据类型：2026 GitHub 仓库代码级审阅 + 2019 JFE/2023 KAIS 论文 + 公共 order-book 最小快检

先把 **base alpha** 说死：**这不是“韩国上币套利流程”也不是“kimchi premium 监控面板”本身。真正可直接 desk 化的 raw alpha，是跨交易所 `spot ask` 与 `perp bid` 的费后 contango 净价差收敛。**

也就是说，这轮我故意**不**把仓库 headline 里最吸睛的韩国出金腿当主角；对我们做 `1m / 3m / 5m / 15m` 的 desk，更值得先拆出来的是它里面那条更短、更纯、更可复制的分支：

> **全市场扫一遍，找 cheapest spot + richest perp 的组合；只在 fee-adjusted net spread 真正为正、且超过 buffer 时，做 delta-neutral 收敛。**

## 1. 这次看了什么
主线材料是一份 2026 新仓库：

- **sueun-dev (2026), _crypto-market-neutral-platform_**
- Readable URL：`https://github.com/sueun-dev/crypto-market-neutral-platform`
- Repo URL：`https://github.com/sueun-dev/crypto-market-neutral-platform`

如果只看 README，很容易把它读成：
- 韩国交易所搬砖
- 上币后转移现货去吃 kimchi premium
- 一个偏“跨境资金/出入金流程”的套利平台

但对我们当前 desk 更值钱的，其实不是这条最慢的跨境腿，而是仓库里已经写死的一条更原子的 alpha：

1. **并行抓多交易所 spot/perp 最优盘口**；
2. **按 taker fee 折算成有效买入/卖出价**；
3. **找出 cheapest spot vs richest perp 的最佳组合**；
4. **当 `net_spread` 超过阈值时，做 long spot / short perp 的 delta-neutral 收敛**；
5. **等净价差回落再平仓**；
6. 韩国腿只是一个**可选增强退出**，不是 alpha 本体。

这就很符合这轮 intake 的优先级：
- raw alpha 很清楚；
- entry/exit/sizing/risk/cost 都能写出来；
- 直接能映射到 `1m / 3m / 5m / 15m` 的最小实验；
- 不需要先伪装成 filter / overlay 才能落地。

## 2. 这份仓库最值钱的，不是“韩国卖出”，而是它已经把 raw alpha 算式写好了
我这次重点看了 4 个文件：

1. `src/overseas_exchange_hedge/overseas/price_analyzer.py`
2. `src/overseas_exchange_hedge/overseas/trade_executor.py`
3. `src/overseas_exchange_hedge/overseas/position_tracker.py`
4. `src/overseas_exchange_hedge/korea/exit/kimchi_premium.py`

最关键的是 `price_analyzer.py`。它不是泛泛说“找套利机会”，而是直接把 entry math 写出来了：

- `effective_spot = spot_ask * (1 + spot_taker_fee)`
- `effective_perp = perp_bid * (1 - perp_taker_fee)`
- `net_spread = (effective_perp - effective_spot) / effective_spot`

然后在所有 `(spot_exchange, perp_exchange)` 组合里，**找 `net_spread` 最大的那一组**。

换成人话：

> **不是看名义 basis，也不是看单交易所 perp premium；而是看“扣完两边 taker fee 后，这笔 long-spot / short-perp 还能剩下多少真钱”。**

这就是一条标准的 short-horizon relative-value raw alpha，而且是很诚实的那种——**成本先入模，不是最后再补。**

## 3. 代码级别能抠出来的完整策略骨架
### 3.1 entry：阈值入场，不碰方向赌注
仓库里有两个值得记的参数版本：

- README 展示版：`PRICE_DIFF_THRESHOLD = 0.0021`（**21bp**）
- 当前代码版 `config.py`：`PRICE_DIFF_THRESHOLD = 0.0015`（**15bp**）

同时当前代码里还有：
- `ENTRY_AMOUNT = 100.0`
- `MAX_ENTRIES = 40`
- `SLEEP_SEC = 3`
- `FUTURES_LEVERAGE = 1`

这几个数字翻成人话就是：
- 这是个**阈值触发型** alpha，不是持续做市；
- 默认每次只打小额；
- 会分批累积，而不是一把梭；
- 永续腿固定 `1x`，强调的是 **delta-neutral carry / convergence**，不是融资放大。

### 3.2 execution：先 short perp，再补 long spot，优先快腿成交
`trade_executor.py` 里写得很明确：
- 先确保 perp 侧 `1x leverage`
- 使用 market order
- `PROCEED_ON_PERP_ACK = True`
- perp ACK 之后尽快打 spot
- 对不同交易所有 precision / minQty / minNotional 的防守逻辑

这说明作者自己也知道这条线的生死不在“预测准不准”，而在：
- 盘口是不是还在
- ACK 到 fill 的延迟够不够短
- spot/perp 量纲能不能真正对齐

所以这条线的本质不是低频 carry，而是：

> **一个有明确 latency budget 的短周期收敛 alpha。**

### 3.3 exit：先看净价差回落；韩国腿只是 bonus，不该当主 alpha
`position_tracker.py` 和 `price_analyzer.py` 已经把**正常平仓**该算的东西写齐了：

- `spot_exit = spot_bid * (1 - spot_fee)`
- `perp_exit = perp_ask * (1 + perp_fee)`

也就是说，production 上最诚实的主退出其实应该是：
- 看 open net spread
- 看 close net spread
- 净价差收敛到 break-even / target 区间就平

而 `korea/exit/kimchi_premium.py` 只是额外给了一个增强退出：

- `premium = (korean_bid - overseas_price_krw) / overseas_price_krw * 100`
- 默认 `threshold = 3.0%`

这条腿对更慢、更事件驱动的 regional spread 套利当然有用，但对我们要优先补充的短周期 raw alpha 池，**更应该先把它当 optional bonus，而不是把整个主题都绑在韩国出金上。**

## 4. 文献怎么给这条 repo 分支垫地基
### 4.1 Makarov & Schoar (2019) 给的是“为什么这种跨 venue spread 会长期存在”
- **Igor Makarov, Antoinette Schoar (2019). _Trading and arbitrage in cryptocurrency markets_. Journal of Financial Economics.**
- DOI：`10.1016/j.jfineco.2019.07.001`
- Readable URL：`https://doi.org/10.1016/j.jfineco.2019.07.001`

这篇老但非常硬的 JFE 论文，不是拿来直接抄 `1m` 信号的，而是告诉我们：

- crypto 跨交易所价差真实存在；
- 资金、转账、法币通道、库存约束会让它们**不是瞬间无摩擦消失**；
- 所以“跨 venue 收敛”本身可以是 alpha，不只是噪声。

### 4.2 Cho / Park / Ahn (2023) 给的是“韩国腿可以做成增强退出，但别把它误当 alpha 本体”
- **GiJeong Cho, Jonghyun Park, Hyunchul Ahn (2023). _A Study on Statistical Arbitrage Transactions of Cryptocurrency Using Kimchi Premium and Exchange Rate Fluctuations Prediction_. Journal of the Korea Academia-Industrial cooperation Society.**
- DOI：`10.5762/KAIS.2023.24.10.354`
- Readable URL：`http://dx.doi.org/10.5762/kais.2023.24.10.354`

OpenAlex 抽到的摘要很直白：
- 他们用 `2017-09-26 ~ 2023-04-06` 的汇率 + Upbit/Binance BTC spot 数据；
- 结论是 **kimchi premium 会围绕由汇率决定的平均水平回归**；
- 并尝试用 LSTM 预测汇率，来提升统计套利机会与收益。

对我们最值钱的翻译不是“去做一个汇率 LSTM”，而是：

> **如果 regional premium 的确有均值回归属性，那它更像 cross-exchange spot/perp 主策略的二级退出增强，不该反过来吃掉主 alpha 的位置。**

## 5. 公共 live quick check：这条 alpha 现在在 majors 上根本不宽，别自欺欺人
为了不把 repo 直接神化，我补了一个很便宜但很诚实的 live check：

### 数据源与公开性
- Bybit public orderbook
- OKX public books
- Gate.io public orderbook
- 全都是公开 REST，无需私钥
- 更新频率：秒级

### 最小实验口径
- 标的：先用 `BTCUSDT`
- 交易所：Bybit / OKX / Gate
- 频率：每 `5s` 抓一次
- 样本：连续 `24` 次快照（约 `2` 分钟）
- 算法：严格照仓库逻辑，先加 spot taker fee、再减 perp taker fee，然后看 cheapest spot vs richest perp 的 `net_spread`

### 这轮最重要的 4 个数
1. **24 次快照里，最佳费后净价差平均只有 `-20.1bp`。**
2. **最好的一次也只有 `-18.5bp`，最差约 `-20.9bp`。**
3. **超过代码阈值 `15bp` 的次数是 `0/24`；超过 README 旧阈值 `21bp` 的次数也是 `0/24`。**
4. **最佳组合 24 次里有 21 次是 `Bybit spot -> Gate perp`，说明“最优 pair 很稳定”，但稳定的是负毛边，不是正 edge。**

对应 artifact：
- `reports/artifacts/quant_digests/krw_or_cross_exchange_contango_20260326_live_snapshots.json`
- `reports/artifacts/quant_digests/cross_exchange_contango_20260326_live_summary.csv`

### 再补一个 top-6 snapshot
我又做了一个单次 top-6 snapshot（`BTC / ETH / SOL / XRP / ADA / DOGE`）：

- `BTC`: **-19.7bp**
- `ETH`: **-19.2bp**
- `SOL`: **-21.8bp**
- `XRP`: **-21.5bp**
- `ADA`: **-30.4bp**
- `DOGE`: **-20.4bp**

对应 artifact：
- `reports/artifacts/quant_digests/cross_exchange_contango_20260326_top6_snapshot.json`

这组数的意思很明确：

> **如果只扫 majors、只用 taker/taker、又没有更低手续费档或 maker rebate，这条 alpha 现在基本活不在 BTC/ETH 这些最拥挤品种上。**

这不是坏消息，反而很重要，因为它帮我们提前避免把 repo 误读成“随便扫三家大所 BTC 就能收租”的幻觉。

## 6. 这条线对短周期 desk 的正确读法
### 6.1 它仍然是 raw alpha，但不是“majors 常开型”
从代码骨架看，它确实是一条：
- 可独立复现
- 可写完整策略
- 成本先入模
- 纯 relative-value / stat-arb

所以它是 **raw alpha** 没错。

但从 live quick check 看，当前更合理的定位是：

- **对 BTC/ETH：默认不是 always-on 主策略**
- **对 alt / listing / 流动性偏薄合约：可能是 event pocket / dislocation scanner**
- **对有更低 fee tier / maker rebate / 内部库存的人：可能重新活过来**

### 6.2 真正值得 desk 先测的是“扫描器”，不是“韩国退出器”
更贴近我们现在短周期研发节奏的落地顺序，应该是：

1. 先把跨交易所 `spot ask vs perp bid` 扫描器跑起来；
2. 把触发事件存下来；
3. 看哪些币、哪些交易时段、哪些 venue pair 会反复出现正毛边；
4. 只有当主 alpha 被确认后，再决定要不要给它加韩国 premium exit 这类慢腿增强。

## 7. desk 版最小完整策略骨架
### 7.1 entry
- universe：先 `top 50~100` USDT spot/perp 共有币
- venues：Bybit / OKX / Gate（后续可扩 Binance、KuCoin、Bitget）
- 计算：
  - `effective_spot_buy = best_spot_ask * (1 + taker_fee_spot)`
  - `effective_perp_short = best_perp_bid * (1 - taker_fee_perp)`
  - `net_spread = (effective_perp_short - effective_spot_buy) / effective_spot_buy`
- 触发：
  - 基线先测 `> 15bp`
  - 压力测试 `> 21bp / 25bp / 30bp`

### 7.2 exit
- 主退出：
  - `close_net_spread <= 0bp` 或 `<= 3bp`
- 时间退出：
  - `1m / 3m / 5m / 15m` 四档固定持有
- optional bonus：
  - 若该币可转韩国腿，再挂 `kimchi premium >= 3%` 的慢速增强退出

### 7.3 sizing
- 单次 notional：按 repo 逻辑先从固定小额开始
- 组合上限：按 venue pair / coin 做 caps
- 只有当两腿盘口量都覆盖目标下单量，才允许入场

### 7.4 risk / veto
- 若 perp funding 极端转负，说明 rich perp 可能很快塌，要缩小持有窗
- 若其中一腿 top-of-book 深度明显不够，直接 veto
- 若 API ACK / fill 延迟超预算，直接 kill，不做“裸露半腿”幻想
- 若正毛边只存在于 taker/taker 之前、费后一过就没了，直接 veto

### 7.5 cost
这条线最该诚实的地方就是 cost：
- taker/taker 是第一道生死线
- 下一层才是 slippage、reject、partial fill、borrow/inventory friction
- 所以 production 评估必须至少三档：
  - `fees only`
  - `fees + 0.5 tick`
  - `fees + 1 tick + partial fill`

## 8. 为什么它能映射到 `1m / 3m / 5m / 15m`
虽然 repo 代码是秒级轮询，但它对 desk 的短周期映射很自然：

- `1m`：最适合事件采样与最快速 time stop
- `3m`：最像“给收敛一点时间，但不让 inventory 风险拖太久”
- `5m`：适合第一版 production backtest
- `15m`：更适合作为“慢 pocket 兜底”，不该拿来做最早入场

也就是说，这条线并不是“只能做 tick 级 HFT”。它完全可以先降采样成 `1m / 3m / 5m` 的 event-driven stat-arb 研究线。

## 9. 我现在的判断
**这主题值得进池，而且应该归类成 raw alpha。**

但更准确的 verdict 不是：
- “韩国 market-neutral 仓库 = 可直接搬来跑 BTC 收租”；

而是：
- **“这仓库里面藏着一条很干净的 cross-exchange cheapest-spot / richest-perp 收敛 raw alpha；只是当前 majors 上费后基本不宽，所以研究重点应该转向 altcoin dislocation / fee-tier / maker 化，而不是沉迷韩国出金叙事。”**

换句话说：

> **alpha 候选是对的，headline 读法是错的。**

## 10. 下一步怎么测（最重要）
### P0：先把 event scanner 跑起来，而不是继续读 README
- universe：`top 50~100` spot/perp 共有币
- venues：Bybit / OKX / Gate / Binance / Bitget
- 频率：`5s` 或 `10s`
- 保存：每次触发时的 `coin / spot_ex / perp_ex / raw_spread / fee_adjusted_spread / top_depth / funding`

目标不是先算收益，而是先回答：
- **哪些币真的会出现费后正毛边？**
- **这些事件一天有几次？**

### P1：做真正的 `1m / 3m / 5m / 15m` markout
对每个触发事件，至少输出：
- open spread
- close spread at `+1m/+3m/+5m/+15m`
- gross bps
- net bps after cost assumptions
- hit rate / median / tail loss

### P2：把 coin 按 liquidity bucket 分层
我强烈怀疑：
- `BTC/ETH` 上这条边大概率被 fees 吃光；
- 真正会活的是 **中高流动性 alt 的短时 dislocation**；
- 再往小盘走，又会被深度和 partial fill 吃掉。

所以下一步必须分：
- majors
- liquid alts
- thin alts

### P3：单独测 maker/taker 混合版本
如果 taker/taker 费后全是负的，下一步别硬做更大样本，而是直接比较：
- taker/taker
- maker spot / taker perp
- taker spot / maker perp

因为这条线的可活性，很可能主要取决于**你能不能把其中一条腿 maker 化**。

### P4：韩国腿只在主 alpha 站稳后再接
只有当 P0~P3 证明主 alpha 存在后，再去评估：
- `USDT/KRW`
- `Upbit/Bithumb bid`
- `kimchi premium >= 3%`

是否能把某些事件升级成更慢的 region-exit bonus。不要反过来本末倒置。

## 11. 来源
1. **sueun-dev. (2026). _crypto-market-neutral-platform_. GitHub repository.**  
   - Readable URL：`https://github.com/sueun-dev/crypto-market-neutral-platform`  
   - Repo URL：`https://github.com/sueun-dev/crypto-market-neutral-platform`
2. **仓库源码：`price_analyzer.py`**  
   - URL：`https://raw.githubusercontent.com/sueun-dev/crypto-market-neutral-platform/main/src/overseas_exchange_hedge/overseas/price_analyzer.py`
3. **仓库源码：`trade_executor.py`**  
   - URL：`https://raw.githubusercontent.com/sueun-dev/crypto-market-neutral-platform/main/src/overseas_exchange_hedge/overseas/trade_executor.py`
4. **仓库源码：`position_tracker.py`**  
   - URL：`https://raw.githubusercontent.com/sueun-dev/crypto-market-neutral-platform/main/src/overseas_exchange_hedge/overseas/position_tracker.py`
5. **仓库源码：`kimchi_premium.py`**  
   - URL：`https://raw.githubusercontent.com/sueun-dev/crypto-market-neutral-platform/main/src/overseas_exchange_hedge/korea/exit/kimchi_premium.py`
6. **Makarov, I., & Schoar, A. (2019). _Trading and arbitrage in cryptocurrency markets_. Journal of Financial Economics.**  
   - DOI：`10.1016/j.jfineco.2019.07.001`  
   - Readable URL：`https://doi.org/10.1016/j.jfineco.2019.07.001`
7. **Cho, G., Park, J., & Ahn, H. (2023). _A Study on Statistical Arbitrage Transactions of Cryptocurrency Using Kimchi Premium and Exchange Rate Fluctuations Prediction_. Journal of the Korea Academia-Industrial cooperation Society.**  
   - DOI：`10.5762/KAIS.2023.24.10.354`  
   - Readable URL：`http://dx.doi.org/10.5762/kais.2023.24.10.354`
8. **Bybit V5 Market Orderbook API**  
   - URL：`https://api.bybit.com/v5/market/orderbook`
9. **OKX Market Books API**  
   - URL：`https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-order-book`
10. **Gate.io Spot / Futures Order Book API**  
   - Spot：`https://api.gateio.ws/api/v4/spot/order_book`  
   - Futures：`https://api.gateio.ws/api/v4/futures/usdt/order_book`
