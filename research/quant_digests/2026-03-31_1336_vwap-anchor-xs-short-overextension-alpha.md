# 别把这份 2026 新仓库只读成横截面教学脚本：对 desk 更该先测的是「rolling-VWAP anchor × short-rich basket」raw alpha，而不是对称 long-short MR

- 时间：2026-03-31 13:36 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/cross-sectional/mean-reversion/short-overextension/vwap-anchor/relative-value/short-basket/asymmetric-reversal/binance/perpetual/mexc/15m/5m/1m/3m/repo/public-data/cost
- 证据类型：2026 GitHub 新仓库元数据 + `README.md` / `cross-sectional-crypto-backtest.py` / `cross-sectional-crypto-production.py` source audit + Binance USDⓈ-M Perpetual 公开 `15m` 最小 transfer check

- 主题类型：raw alpha
- 基础 alpha：横截面里“相对 rolling VWAP 最贵、最偏离”的币，在后续短窗口里更容易回吐；更适合做 `short rich basket`，不适合机械对称地 `long cheap basket`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次主看的是 **Alphanume Strategy Lab** 在 2026-03 新开的公开仓库里一条 crypto 子策略：**Cross-Sectional Mean Reversion (Crypto)**。

它不是论文，但它有两个对 desk 很有用的特点：

1. **不是只有 README**：同时给了 backtest 脚本和 production ranking 脚本；
2. **base alpha 很清楚**：不是抽象“市场有均值回复”，而是 **同一时刻横截面里，谁相对 rolling VWAP 最离谱，就优先 fade 谁**。

更关键的是，我拿公开 Binance perp `15m` 数据做了一个超小 transfer check 后，发现它最值得保留的不是“完整对称 long-short reversal”，而是更偏 **asymmetric short-overextension sleeve**：

- **short top bucket** 有边；
- **long bottom bucket** 反而拖后腿；
- 把两边硬拼成对称 dollar-neutral spread，edge 基本被抹平。

这正适合当前 desk 的 intake 逻辑：优先找 **能独立成立的 raw alpha**，而不是为了形式完整，把没有边的腿也塞进去。

## 2. 为什么这次值得进研究池
这轮 bot7 的优先级里，`可独立复现且可直接落地完整策略` 高于纯解释型材料。这条线值得收，原因有三点：

1. **base alpha 直接、可交易**：横截面最贵那一篮子，未来几根 bar 更容易回吐。
2. **repo 已经给了 strategy shell**：不是只给 ranking 思路，而是有 universe、feature、ranking、持有期、production signal 输出。
3. **它补的是我们当前素材池里偏少的一类“非对称 MR”**：很多 mean reversion digest 默认写成对称 long-short；这条线更像是 **只保留 short rich 一侧**，再用 BTC hedge / beta-light 方式处理市场暴露。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = 在同一时间的横截面里，价格相对 rolling VWAP 偏离最大的“贵票”更容易在后续短窗口里回落。**

更直白地写成策略语言：

- 先对所有候选币算 `dist_from_vwap = (close - rolling_vwap) / rolling_vwap`；
- 每个 rebalancing timestamp 做一次横截面排序；
- **优先 short 排名最高的一小篮子**；
- 不默认同时去 long 最低的一篮子，因为“cheap leg”未必同样有回复边。

所以这是一条 **raw alpha**，属于 `cross-sectional / mean reversion / relative-value`，不是 filter，也不是 overlay。

## 4. 核心来源
### 4.1 主仓库
- **Authors / Org**：Alphanume Strategy Lab / GitHub `alphanume-markets`
- **Year**：2026
- **Title**：*Cross-Sectional Mean Reversion (Crypto)*（位于 `Alphanume-Strategy-Lab` 仓库）
- **Venue**：GitHub Repository
- **DOI**：无
- **Readable URL**：https://github.com/alphanume-markets/Alphanume-Strategy-Lab/tree/main/Strategies/Crypto/Cross%20Sectional%20Mean%20Reversion
- **Repo URL**：https://github.com/alphanume-markets/Alphanume-Strategy-Lab
- **仓库元数据（本次审阅时）**：
  - repo 创建时间：`2026-03-01`
  - 最近更新时间：`2026-03-28`
  - GitHub stars：`15`
- **本次重点审阅文件**：
  - `Strategies/Crypto/Cross Sectional Mean Reversion/README.md`
  - `Strategies/Crypto/Cross Sectional Mean Reversion/cross-sectional-crypto-backtest.py`
  - `Strategies/Crypto/Cross Sectional Mean Reversion/cross-sectional-crypto-production.py`

### 4.2 外部公开数据（本次 transfer check）
1. **Binance USDⓈ-M Futures Klines API**
   - Readable URL：https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - 公开性：公开 REST，无需登录
   - 更新频率：分钟级
   - 本次最小实验口径：`15m` K 线，12 个流动性较高的 USDT perp（BTC/ETH/SOL/XRP/DOGE/ADA/LINK/AVAX/LTC/BCH/TRX/DOT）

## 5. 证据里最值得拿走的硬点
### 5.1 这不是一句“价格偏离 VWAP 会回归”的空话，repo 把交易壳写出来了
从代码看，这条线的 first-pass 结构非常明确：

- **Universe**：Tiingo crypto 元数据里所有 `USDT` quote 资产，再筛到指定交易所（示例是 `MEXC`）；
- **Backtest lookback**：过去约 `2 年`；
- **Bar 粒度**：`4hour`；
- **rolling window**：`vol_window_size = 6`，也就是约 `24 小时`；
- **信号**：`dist_from_vwap = (close - vwap) / vwap`；
- **排序**：横截面 `percentile rank`；
- **组合**：`top 10` most extended；
- **持有期**：从当前 PIT 到次日 PIT，约 `1 天`；
- **方向**：源码最后把 basket return 乘以负号换成 PnL，等价于 **short top basket**。

最重要的一点是：**repo 自己已经在 backtest 里把方向写死成“short top bucket”了**。这不是我额外脑补的，而是源码尾部明确把正 forward return 变成负 PnL，反映其 intended direction。

### 5.2 production 脚本说明它不是纯研究草图，而是能直接变成每日候选清单
`cross-sectional-crypto-production.py` 做的事很像一个轻量实盘 scanner：

- 只拉近 `10 天` 历史；
- 对最近日期做一次横截面 ranking；
- 输出 `top 10` ticker；
- 自动附 `exit_date`；
- 还把 spot-style ticker 转成 `BTC_USDT` 这类 futures-style 字符串。

这很有价值，因为它说明：
- 这条线不是“研究上存在，部署上另说”；
- 它天然适合 desk 做成 `1m/5m/15m` 的 live ranker；
- 只要把数据源从 Tiingo/MEXC 换成 Binance/Bybit/OKX perp，就能快速进入最小生产态。

### 5.3 repo 里的“VWAP”其实更接近 rolling central-price anchor，不是严格成交量 VWAP
源码写法是：

- 先取 `central_px = mean(open, high, low, close)`；
- 再做 `vwap_px = (central_px * volume) / volume`；
- 最后 rolling mean 成 `vwap`。

这意味着它本质更像：

**rolling central-price anchor**，而不是严格意义上的 cumulative trade VWAP。

这不是坏事，反而给了 desk 一个更清楚的实验方向：

1. **先忠实复现 repo 版本**：rolling central-price anchor；
2. **再做真实 volume-weighted VWAP 版本**；
3. 比较两者在 perp 上的 alpha/cost 差异。

也就是说，repo 给我们的不是“标准答案”，而是一个很清楚、很容易扩展的 baseline。

## 6. 最关键的新发现：公开 `15m` transfer check 显示，这条线更像“只保留 short rich leg”的非对称 raw alpha
我用 Binance USDⓈ-M Futures 公共 `15m` K 线，对 12 个流动性较好的 USDT perp 做了一个超小型 transfer check：

- 样本：最近约 `1500` 根 `15m` bars（约 15.6 天）
- 横截面：12 个流动 perp
- anchor：滚动 `96` 根 `15m` bars（约 24h）rolling VWAP
- rebalancing：每 `4` 根 bar（每 `1h`）
- bucket：每次取最贵 `top 2` / 最便宜 `bottom 2`
- 先不计手续费，只看 gross transfer

产物文件：
- `reports/artifacts/quant_digests/binance_vwap_xs_mr_15m_20260331_1329.csv`

### 6.1 结果一：`short top-2 rich basket` 有边，而且 hold 不是越短越好
我额外扫了 `30m / 1h / 2h / 4h` 四档持有期，结果如下：

- **持有 30m（2 bars）**：平均每笔约 **4.46 bps**，胜率 **55.0%**，粗略累计 **+16.7%**；
- **持有 1h（4 bars）**：平均每笔约 **3.60 bps**，胜率 **51.9%**，粗略累计 **+13.1%**；
- **持有 2h（8 bars）**：平均每笔约 **7.62 bps**，胜率 **55.1%**，粗略累计 **+29.7%**；
- **持有 4h（16 bars）**：平均每笔约 **12.95 bps**，胜率 **55.5%**，粗略累计 **+54.7%**。

这组数最值得 desk 拿走的不是“收益看起来高”，而是：

**这条线在 `15m` transfer 下更像是 2h~4h 的 overextension fade，不像 15m 内一两根 bar 就迅速回完的 ultra-fast scalp。**

### 6.2 结果二：`long bottom-2 cheap basket` 明显不行，强行做对称 spread 会把 alpha 抹平
同一组快检里：

- **long bottom-2 cheap basket（1h hold）**：平均每笔约 **-3.51 bps**；
- **dollar-neutral short-top / long-bottom spread（1h hold）**：平均每笔只剩 **+0.05 bps**，几乎归零；
- 即便 hold 拉到 `2h~4h`，spread 也没出现像 short-only 那样自然变厚的边。

这说明一个很重要的 desk 结论：

**这不是一条值得机械写成“最贵做空、最便宜做多”的对称 XS MR。更像是一条“只 short rich leg，再用 beta hedge 控暴露”的非对称 raw alpha。**

### 6.3 结果三：top bucket 的平均 overextension 不算夸张，但足以做 admission
在 `1h` rebalancing 下，快检样本里：

- top-2 bucket 的平均 `dist_from_vwap` 约 **+82.3 bps**；
- bottom-2 bucket 的平均 `dist_from_vwap` 约 **-128.8 bps**。

但 bottom 这边并没有自然变成可赚钱的 long leg。这再次说明：

- “偏离更大” ≠ “更适合对称交易”；
- **cheap bucket 里混着持续走弱 / narrative 崩塌 / 结构性 loser**；
- 对 desk 更诚实的写法，是把这条线定义成 **short-side overextension alpha**。

## 7. 对 crypto `1m / 3m / 5m / 15m` 的正确读法
### 7.1 它是 raw alpha，但不是“便宜就买、贵了就卖”的教科书对称反转
repo 名字虽然叫 mean reversion，但对 desk 最该保留的核心，其实是：

- **横截面 rank**；
- **rolling anchor**；
- **只做高质量一侧**；
- **不为了形式完整去保留负边那一腿**。

也就是说，这条线更接近：

**cross-sectional overextension short sleeve**

而不是：

**classical symmetric long-short reversion basket**。

### 7.2 对 `15m` 最自然，对 `5m` 更像执行层细化
从本次 transfer check 看：

- `15m` 最适合做 admission / ranking / hold-window research；
- `5m` 更适合做 execution refinement：
  - 分批进场
  - intrabar extension 确认
  - spread / depth veto
- `1m / 3m` 暂时更适合做 **micro execution layer**，不适合先拿来当主 signal 形成层。

## 8. 如果把它落成完整策略，应该怎么写
### 8.1 Entry
在 liquid perp universe 上，每 `15m` 或每 `1h` 做一次：

1. 计算 rolling anchor（先做 repo 原版，再做真实 VWAP 版）；
2. 算 `dist_from_anchor`；
3. 横截面排序；
4. 只选 `top N` richest names；
5. 叠加最小 admission：
   - `dist_from_anchor > threshold`
   - `avg_notional > threshold`
   - funding 不处于极端 squeeze 区
   - 近几根 bar 没有重大公告 / 上币 / narrative 冲击

first pass 可以直接写成：

- **Universe**：12~30 个流动性最好 perp
- **Signal frequency**：`15m`
- **Rebalance**：每 `1h`
- **Entry bucket**：top `2~3`
- **Threshold**：至少 `+60 ~ +100 bps` overextension 才进

### 8.2 Exit
优先三套最简单的：

1. **固定持有期 exit**：`2h` / `4h`
2. **回归阈值 exit**：`dist_from_anchor` 回到 `+10 ~ +20 bps` 内
3. **失败止损 exit**：若 overextension 继续扩大到更高分位，直接止损，不硬等“总会回来”

根据这轮快检，我会把 **`2h` 和 `4h`** 作为首批重点窗口，而不是只盯 `30m`。

### 8.3 Sizing
因为它本质上是 short-rich sleeve，最自然的 sizing 不是对称 long-short，而是：

- 单名义仓位 = inverse vol × liquidity scalar
- 总 gross 不超过资金的一定比例
- 单 narrative / 单 sector 设 cap
- 如要去 beta：
  - 用 BTC/ETH index future 做轻量 hedge
  - 不默认拿 bottom bucket 去对冲

### 8.4 Risk
这条线最容易死在四个地方：

1. **short squeeze / narrative melt-up**
2. **上币、空投、治理投票、链上事件**
3. **极端 funding 正向挤仓**
4. **便宜腿根本不是 alpha，只是弱者恒弱**

所以风险控制里至少要有：

- single-name cap
- sector cap
- event veto
- funding squeeze veto
- 连续放大止损，不许“摊平等回归”

### 8.5 Cost
短侧横截面策略最容易高估 alpha，原因是 turnover + taker cost：

- taker 开仓
- taker/被动混合平仓
- spread widening
- funding（若持有跨 funding boundary）
- 滑点与冲击

本次 `15m` quick check **没有计费**，因此只能说明“有 transfer 价值”，不能直接说明“可实盘赚钱”。

## 9. 为什么它比继续补一个“对称 cross-sectional reversal”更值得
因为这次最有价值的，不是“又找到一个 MR 信号”，而是明确了一件事：

**repo headline 看起来像对称 XS MR，但真正适合我们 desk 的 branch，是 asymmetric short-overextension alpha。**

这完全符合本轮任务允许的读法：

- 不必死抄论文/仓库 headline；
- 若旁支更适合 desk，就单独拎出来；
- 只要能快速做最小实验、快速验证，就值得进池。

## 10. 最小可复现实验（建议直接做）
### 实验 A：15m perp short-rich baseline
- **数据源**：Binance / Bybit / OKX perp 公共 `15m` K 线
- **公开性**：公开可得
- **更新频率**：`15m`
- **Universe**：20 个最 liquid USDT perp
- **Signal**：rolling 24h anchor 偏离横截面 rank
- **Rebalance**：每 `1h`
- **Entry**：short top `2~3`
- **Exit**：`2h` / `4h` 固定持有
- **对照组**：
  - short-only
  - short-top + BTC hedge
  - short-top / long-bottom 对称 spread
- **核心问题**：short-only 是否稳定优于对称版本？

### 实验 B：anchor 定义对照
- **版本 1**：repo 原版 rolling central-price anchor
- **版本 2**：真实 volume-weighted rolling VWAP
- **版本 3**：VWAP + realized-vol normalization
- **目标**：确认这条线的 alpha 到底来自“横截面 overextension”还是来自某个特定 anchor 定义。

### 实验 C：5m execution honesty replay
- **数据源**：公开 `5m` / top-of-book / spread proxy
- **问题**：`15m` 形成的 short-rich 候选，在 `5m` 上如何分批进、何时不追？
- **目标**：把“研究上有边”变成“成交后还有边”。

## 11. 下一步怎么测
1. **先别做对称 long-short**：先把 `short top bucket` 单独跑干净。  
2. **先做 `2h / 4h` 持有期**：本次 `15m` quick check 显示这两档更像自然 pocket。  
3. **把 bottom bucket 从 alpha 腿降级成对照组**：它现在更像 falsification leg，不像该保留的主腿。  
4. **补一个 BTC beta-hedged 版本**：如果 short-only 暴露太高，就用 index hedge，不要默认拿 cheap bucket 硬配平。  
5. **强制跑三套成本**：maker-heavy / mixed / taker-heavy；没有成本分层，这类轮动短侧策略很容易自欺。  
6. **分 sector 看稳定性**：meme / majors / infra / L2 很可能不是同一条 alpha。  

## 12. 一句话结论
这份 2026 新仓库真正适合 desk 拿走的，不是“横截面 VWAP 偏离做对称均值回复”，而是：**把 rolling-VWAP anchor 改写成一条只保留 short rich leg 的非对称 raw alpha，再用 beta hedge 和成本约束把它落成 `15m`→`2h/4h` 的完整策略。**

## 13. 来源链接
- 主仓库目录：https://github.com/alphanume-markets/Alphanume-Strategy-Lab/tree/main/Strategies/Crypto/Cross%20Sectional%20Mean%20Reversion
- 主仓库主页：https://github.com/alphanume-markets/Alphanume-Strategy-Lab
- README 原文：https://raw.githubusercontent.com/alphanume-markets/Alphanume-Strategy-Lab/main/Strategies/Crypto/Cross%20Sectional%20Mean%20Reversion/README.md
- Backtest 脚本：https://raw.githubusercontent.com/alphanume-markets/Alphanume-Strategy-Lab/main/Strategies/Crypto/Cross%20Sectional%20Mean%20Reversion/cross-sectional-crypto-backtest.py
- Production 脚本：https://raw.githubusercontent.com/alphanume-markets/Alphanume-Strategy-Lab/main/Strategies/Crypto/Cross%20Sectional%20Mean%20Reversion/cross-sectional-crypto-production.py
- Binance USDⓈ-M Kline API：https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
