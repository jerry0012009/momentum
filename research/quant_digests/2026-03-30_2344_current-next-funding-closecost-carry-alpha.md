# 别把 same-venue funding carry 继续写成“正 funding 就能收租”：这份 OKX V5 仓库更该先测的是「premium-z admission × current+next funding > close-cost」完整 raw alpha
- 时间：2026-03-30 23:44 UTC
- 类型：2021 GitHub 仓库（2026-03 metadata 更新，2024-01 最新 push）+ `README.md` / `src/open_position.py` / `src/close_position.py` / `src/monitor.py` / `src/trading_data.py` source audit + OKX 公开 funding/ticker/candles live sanity check
- 主题类型：raw alpha
- 基础 alpha：**同 venue 的 delta-neutral spot-perp carry**——做多现货、做空永续，吃的是 **perp 相对 spot 的持续溢价 + funding cashflow**；只有当 perp 溢价已经足够 rich、且预期 funding 现金流覆盖 round-trip close cost 时，才值得把这条 carry 真正打开/继续持有。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/spot-perp/same-venue/okx/premium-z/current-next-funding/close-cost-hurdle/vol-adjusted-selection/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：**源码级仓库证据 + OKX 公开 API live sanity check**

> 先把 **base alpha** 说清楚：
>
> **alpha 本体不是“funding 排名表”，也不是“basis 监控面板”。alpha 本体就是同 venue 的 spot-perp carry：long spot / short perp，赚 funding 和 rich premium 的回落。**
>
> 这份 repo 真正值得 desk 搬的，不是“它会自动下单”这件事，而是它把这条 carry 写成了一个完整可执行策略：
>
> **vol-adjusted candidate selection → premium-z admission → current+next funding vs close-cost 持仓治理 → 保证金/对冲比率监控。**

## 1. 这次看了什么
这次主看的是 GitHub 仓库：

> **Aureliano90 (2021, metadata updated 2026-03), _Futures-Spot-Arbitrage-OKEx-V5_**  
> GitHub repo: `https://github.com/Aureliano90/Futures-Spot-Arbitrage-OKEx-V5`

它不是论文，但它有一个对我们很有价值的优点：

> **不是停在“rich funding 候选列表”，而是把 same-venue carry 的 entry / exit / size / leverage / monitoring / fee 都写进了源码。**

当前 desk 已经有不少 funding / basis digest，但很多还停在：
- `funding > 0` 就当成 carry pocket；
- `premium > 0` 就当作可以开；
- 或者只是做 cross-venue ranking / 可视化。

这份 repo 更值钱的地方在于，它把单 venue carry 明确拆成了三层：

1. **先选谁值得做**：不是只看 funding，而是看 `funding / sqrt(ATR)`；
2. **再决定什么时候开**：不是一见到正溢价就上，而是等 `open premium > recent avg + k·std`；
3. **再决定什么时候该关**：不是只盯 funding 当前值，而是拿 `current_rate + next_rate` 去对比 `close-cost hurdle`。

这第三层最有价值。因为它直接回答了一个实盘问题：

> **“就算 funding 还是正的，这个仓现在还值不值得继续扛？”**

## 2. repo 里真正值钱的不是“自动套利”，而是 3 个可移植部件

### 2.1 部件一：不是看绝对 funding，而是看 `funding / sqrt(vol)`
`src/trading_data.py` 里，repo 会先把最近 funding 候选按 `profitability = funding_rate / sqrt(ATR)` 排序：

- 代码位置：`src/trading_data.py:62-77`
- 关键逻辑：`funding_rate_list[n]['profitability'] = funding_rate / np.sqrt(atr)`

这件事的重要性在于：
- 同样 3 bps funding，配到低波 coin 和高波 coin，不是同一种 carry；
- 绝对 funding 看起来一样，但高波币更容易把你拖进保证金/对冲重平衡成本；
- 所以 **funding 要先过“按波动折现”**，才配进候选池。

对 desk 的直接翻译是：

> **别再做“谁 funding 高就做谁”的朴素排名；先做 vol-adjusted carry ranking。**

顺手说一句：repo 这里用的是原始 ATR，量纲不够漂亮；我们 desk 落地时更建议换成 **NATR / realized vol / spread vol**，但思想是对的。

### 2.2 部件二：entry 不是“正 premium”，而是 `premium z-score`
`src/open_position.py` 的开仓逻辑不是“合约比现货贵就开”，而是先取近期 premium 统计，再要求当前 open premium 过阈值：

- 代码位置：`src/open_position.py:161-185`
- 关键逻辑：
  - `recent_open_stat(hours)`
  - `price_diff = recent['avg'] + 2 * recent['std']`
  - 当前 `best_bid_swap >= best_ask_spot * (1 + price_diff)` 才继续

也就是说，它实际上在做：

> **只有当 perp 相对现货已经“统计上偏 rich”时，才允许开 long spot / short perp carry。**

这和“只要 funding 正就开仓”的差别非常大：
- 后者是 **always-on 收租幻想**；
- 前者是 **只做 premium 已经拉开、且有回落/收敛空间的 pocket carry**。

这点和我们当前 desk 的优先级是对齐的：

> **carry 不是低频票息产品；短周期 desk 要的是“有 pocket 才开”，不是“正 funding 就挂着”。**

### 2.3 部件三：最值钱的是 `current + next funding > close-cost hurdle`
真正让我觉得这份 repo 值得 intake 的，是 `src/monitor.py` 这段：

- 代码位置：`src/monitor.py:144-157`
- 关键逻辑：
  - `open_pd = recent_open_stat()['avg'] + recent_open_stat()['std']`
  - `close_pd = recent_close_stat()['avg'] - recent_close_stat()['std']`
  - `cost = open_pd - close_pd + 2 * trade_fee`
  - **如果** `current_rate + next_rate < cost` **就主动平仓**

这句话非常关键：

> **repo 并不认为“当前 funding 还是正的”就足够继续持有。它要求：当前 funding + 下一次 funding 的总收益，至少得覆盖你为了最终关掉这个 carry 需要吃下的 close-cost hurdle。**

这比很多 funding 策略诚实得多。因为现实里：
- funding 是慢变量；
- premium/basis 的 round-trip、bid-ask、重平衡、手续费、保证金腾挪是快变量；
- **如果未来一个 funding 周期赚不到足够覆盖 close hurdle 的钱，你其实是在拿仓位风险换几个几乎不值钱的 bps。**

## 3. 对我们 desk 来说，这篇 intake 的正确定位
这里要避免误读：

### 3.1 它不是纯 filter digest
如果只把这篇 digest 归成 overlay / filter，会低估它。

更准确的说法是：
- **raw alpha**：same-venue delta-neutral funding/basis carry
- **repo 的新增价值**：把这条 raw alpha 写成“会开、会管、会关”的完整骨架
- **其中最值得偷的部件**：`current+next funding > close-cost` 的 viability check

所以这轮归类仍然应该是：**raw alpha**。

### 3.2 它为什么比再补一篇 generic funding 摘要更值得
因为当前项目里 funding / basis 相关 digest 已经不少，但大量问题都卡在：
- 什么时候值得开？
- 开了以后什么时候该关？
- 正 funding 和真实可赚之间到底差几层？

这份 repo 至少把这个答案写成了能执行的 if/else：

> **开仓要 premium rich，持仓要 funding 覆盖 close-cost，不够就关。**

这不是观点，是策略骨架。

## 4. 用 repo 语言翻成 desk 版本的完整策略

### 4.1 Universe / selection
先做流动性和借贷/成交成本都更清楚的 same-venue majors：
- `BTC-USDT / BTC-USDT-SWAP`
- `ETH-USDT / ETH-USDT-SWAP`
- `SOL-USDT / SOL-USDT-SWAP`
- 再视流动性扩到 `XRP / DOGE / TON / BNB`

**selection score** 不看绝对 funding，而看：
- `funding / sqrt(spread_vol)` 或 `funding / sqrt(NATR)`
- 再加一个最小日均成交额 / 最小盘口厚度门槛

### 4.2 Entry
只在以下都满足时开仓：
1. `funding > 0`（或 current+next funding 为正）
2. `open premium z > z_enter`
3. `gross carry estimate > close-cost hurdle`

换成人话：

> **资金费正，只是必要条件；premium 已经 rich，且未来 funding 现金流覆盖得了未来关仓成本，才是充分条件。**

### 4.3 Exit
触发任一就平：
1. `current + next funding < close-cost hurdle`
2. `premium z < z_exit`
3. 持仓超过最大 funding 周期数
4. 保证金风险 / 对冲比例偏离过大

### 4.4 Sizing
- 按 `score = funding / sqrt(vol)` 排名分配权重；
- 单币权重上限受盘口厚度限制；
- 资金费越高但 premium 越不稳定，仓位越应该折减；
- `1m/3m` 上只做执行切片，不要拿 funding 本身当逐 bar 主信号。

## 5. OKX 公共 live sanity check：很多“正 funding”其实根本不够覆盖 close hurdle
为了避免只做 repo 读后感，这次我直接用 **OKX 公开 API** 做了一个小快检。

### 5.1 快检口径
- 数据源：OKX public API
  - `market/ticker`
  - `market/history-candles`
  - `public/funding-rate`
- 币种：`BTC / ETH / SOL / DOGE / XRP`
- 频率：
  - premium 统计：最近 4 小时 `1m` candles
  - funding：当前 funding + 公共 endpoint 给出的 next funding
- fee proxy：**每条腿 taker 5 bps**，所以 repo 风格的 `2 * trade_fee` 近似为 **10 bps**
- 计算：
  - `open_trigger = premium_mean + premium_std`
  - `close_trigger = premium_mean - premium_std`
  - `close_cost_hurdle ≈ open_trigger - close_trigger + 2*fee`
  - 比较 `current + next funding` vs `close_cost_hurdle`

### 5.2 快检结果：当前主流币一个都不够
本地脚本输出见：
`reports/artifacts/quant_digests/okx_current_next_funding_closecost_20260330/okx_major_snapshot.csv`

核心数字：

- **ETH**：`current+next funding = +0.68 bps`，但 `close-cost hurdle ≈ 11.16 bps`，差了 **10.47 bps**
- **BTC**：`+0.19 bps` vs `11.42 bps`，差了 **11.23 bps**
- **SOL**：`-0.59 bps` vs `12.96 bps`，本身就是负 carry

这三条已经足够说明问题：

> **“funding 是正的”离“这笔 carry 值得开/继续拿”之间，差了整整一个数量级。**

### 5.3 不只是 funding 不够，当前 premium 也没 rich 到值得追
同一份 snapshot 里，live open premium z-score 也并不高：
- ETH：`z ≈ 0.02`
- BTC：`z ≈ 0.34`
- XRP：`z ≈ 0.42`

也就是说，当前快照下：
- 既没有足够高的 premium rich pocket；
- 也没有足够高的 funding cashflow 去覆盖 close-cost hurdle。

这反而刚好验证了 repo 设计的必要性：

> **如果没有 `premium-z admission + funding>hurdle` 这两层门槛，策略就会把一堆“看起来 funding 为正、其实根本不值得做”的时点误识别成机会。**

## 6. 这条线和 1m / 3m / 5m / 15m 的关系

### 6.1 funding / basis 天生不是逐根主信号
要诚实一点：
- funding 是结算制慢变量；
- basis/premium 虽然快一些，但不是每根 `1m` bar 都值得响应。

所以这条线更适合的结构是：
- **15m / 5m**：做 alpha clock 和 pocket 判定
- **3m / 1m**：做 execution veto / queue quality / 切片

不要把 funding 伪装成 `1m` 逐根 alpha 本体。

### 6.2 对短周期 desk 的正确落地方式
更合理的是：
- `15m`：决定这轮 carry pocket 是否成立
- `5m`：检查 premium rich 是否持续、盘口是否还能吃
- `1m/3m`：决定分几笔进、是 maker 还是 taker、是否先等 spread 更好一点

所以这条题不是和短周期 desk 无关，恰好相反：

> **它很适合做短周期 desk 的“slow alpha + fast execution”组合。**

## 7. 下一步怎么测（必做）

### 7.1 先做 desk 版最小实验
**目标**：验证 `premium-z admission × current+next funding > close-cost` 是否明显优于 `funding > 0` 的朴素 carry。

**Universe**
- `BTC/ETH/SOL` same-venue OKX spot+swap

**版本对比**
1. **baseline**：`funding > 0` 就开，固定持有到下一结算
2. **premium gate**：`funding > 0` 且 `premium z > 1`
3. **fullstack**：`premium z > 1` 且 `current+next funding > close-cost hurdle`
4. **fullstack + execution**：版本 3 再叠 `1m` spread / depth veto

**评价指标**
- 每次 funding 周期净收益
- 年化换手 / 平均持仓 funding 周期数
- 关仓前后的 realized premium 收敛幅度
- maker-taker / taker-taker 成本敏感性

### 7.2 关键要扫的参数
- `z_enter = 0.5 / 1.0 / 1.5 / 2.0`
- `z_exit = 0 / 0.25 / 0.5`
- `vol score`：`funding/sqrt(NATR)` vs `funding/spread_vol`
- `close-cost hurdle`：
  - 只算手续费
  - 手续费 + bid/ask
  - 手续费 + bid/ask + rebalance slippage

### 7.3 最该优先回答的 4 个问题
1. **`current+next funding > close-cost` 这一层，能否明显减少“正 funding 但不值做”的伪机会？**
2. **premium z 门槛是提高单笔质量，还是只是把交易数砍掉？**
3. **这条线在 majors 上能不能活，还是只在高 funding alt pocket 偶发成立？**
4. **真实可活的成本结构到底是 maker-taker 还是必须 maker-maker / rebate？**

## 8. 当前结论（一句话版）
> **这份 OKX V5 仓库对 desk 最值钱的，不是“spot-perp carry”这个老题材本身，而是把它写成了 `vol-adjusted selection → premium-z admission → current+next funding > close-cost` 的完整生存线；从 OKX 当前主流币 live snapshot 看，绝大多数“正 funding”根本不够覆盖这道 hurdle。**

## 9. 文件与产物
- 研究笔记：`research/quant_digests/2026-03-30_2344_current-next-funding-closecost-carry-alpha.md`
- 快检脚本：`reports/artifacts/quant_digests/okx_current_next_funding_closecost_20260330/okx_current_next_funding_closecost_probe.py`
- 快检结果：
  - `reports/artifacts/quant_digests/okx_current_next_funding_closecost_20260330/okx_major_snapshot.csv`
  - `reports/artifacts/quant_digests/okx_current_next_funding_closecost_20260330/okx_major_snapshot.json`
  - `reports/artifacts/quant_digests/okx_current_next_funding_closecost_20260330/summary.md`
- 页面 URL（发布后）：
  - `https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-30_2344_current-next-funding-closecost-carry-alpha.html`

## 10. 来源
1. **Aureliano90 (GitHub handle, repo created 2021; metadata updated 2026-03). _Futures-Spot-Arbitrage-OKEx-V5_.**
   - Repo URL: `https://github.com/Aureliano90/Futures-Spot-Arbitrage-OKEx-V5`
   - README: `https://raw.githubusercontent.com/Aureliano90/Futures-Spot-Arbitrage-OKEx-V5/main/README.md`
   - 关键源码：
     - `src/open_position.py`
     - `src/close_position.py`
     - `src/monitor.py`
     - `src/trading_data.py`
2. **OKX V5 API Docs**（公开可得，最小可复现实验数据源）
   - Docs URL: `https://www.okx.com/docs-v5/en/`
   - Funding endpoint: `https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate`
   - Market ticker endpoint: `https://www.okx.com/docs-v5/en/#public-data-rest-api-get-ticker`
   - Candles endpoint: `https://www.okx.com/docs-v5/en/#market-data-rest-api-get-candlesticks-history`
   - 公开性：公开 API，无需私钥即可抓取
   - 更新频率：ticker/funding 接近实时，candles 按 bar 更新
   - 最小可复现实验口径：`BTC/ETH/SOL/DOGE/XRP` 的 OKX spot + USDT perpetual，最近 4 小时 `1m` premium 统计 + funding 快照，对比 `current+next funding` 与 `close-cost hurdle`
