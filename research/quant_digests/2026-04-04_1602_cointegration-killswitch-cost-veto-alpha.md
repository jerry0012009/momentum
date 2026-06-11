# 别把这份 2026 新 repo 只读成又一份 pairs bot：对 short-cycle desk，更该先测的是「cointegration spread fade × cost veto × kill-switch shell」
- 时间：2026-04-04 16:02 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `backtest_results.json` + `backtest_log.txt`）+ Binance USDⓈ-M 公共 `15m/5m` 最小便携性快检
- 主题类型：raw alpha
- 基础 alpha：**cointegrated pair 的 spread 偏离均衡后会向均值回归**；repo 真正值得 desk 先抄的，不是“又一份 z-score pairs 教程”，而是 `pair scan → z-score entry/exit → live state machine → drawdown kill-switch` 这整套能直接落地的完整策略壳
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / cointegration / zscore / drawdown-killswitch / binance-futures / 15m / 5m / repo / public-data / cost / risk
- 证据类型：repo（完整策略壳）+ repo 自带回测结果 + 本地 public-data proxy scan

**先回答 base alpha：这篇东西的 base alpha 很清楚，就是 `cointegrated spread mean reversion`。答得清，所以它是 raw alpha，不只是 filter / overlay。**

## 1. 这次看了什么
这轮主看的是一个很新的完整仓库，而不是单独一篇“pairs 原理介绍”：

1. **Sanin Sergiy（GitHub: `ssanin82`, 2026）**  
   **Title:** *strat-test-cointegration*  
   **Venue:** GitHub repository  
   **DOI:** 无  
   **Readable URL:** <https://github.com/ssanin82/strat-test-cointegration>  
   **Repo URL:** <https://github.com/ssanin82/strat-test-cointegration>  
   我这次重点读了：
   - `README.md`
   - `backtest_results.json`
   - `backtest_log.txt`

2. **Engle, Robert F.; Granger, Clive W. J. (1987)**  
   **Title:** *Co-integration and Error Correction: Representation, Estimation, and Testing*  
   **Venue:** *Econometrica*  
   **DOI:** `10.2307/1913236`  
   **Readable URL:** <https://www.jstor.org/stable/1913236>  
   **Repo URL:** 无  
   这篇不是本轮主角，但它是 repo 里 Engle-Granger pair selection 的方法学地基。

3. **本地最小快检（不是复现 repo 收益，只是验证它对 short-cycle crypto 的可迁移性）**  
   - 数据源：Binance USDⓈ-M Futures 公共 klines  
   - 公开性：公开可得，无 key  
   - 更新频率：`5m / 15m` K 线  
   - 最小实验口径：`ETHUSDT / LINKUSDT`，按 repo 的 spread + z-score 思路做 public-close proxy  
   - 结果文件：`reports/artifacts/quant_digests/2026-04-04_ssanin82_eth_link_proxy.json`

为什么它值得写？因为我们这两天 raw alpha intake 已经有不少 pairs / carry / microstructure / options，但**真正把 entry / exit / sizing / risk / live state 全串起来、又是 2026 新 repo 的“完整可复现壳”并不多**。这份仓库恰好补的是“可直接抄到实验台”的那层。

## 2. 这份 repo 最值钱的，不是理论新，而是“完整策略母板”够直给
repo README 给出的结构非常完整：

- pair selection：Engle-Granger 协整检验 + OLS hedge ratio
- signal：`spread = price1 - hedge_ratio * price2`，再做 rolling z-score
- entry：spread 偏离够大时开双腿
- exit：z-score 过零就平
- sizing：两腿各吃 50% capital
- execution：直接市价成对下单
- live 管理：`IDLE → MONITORING → CLOSING` 三态状态机
- risk：开盘前先查 drawdown，触发阈值就 kill-switch

翻成人话：

> 它不是“找到 pair 以后你自己再想怎么下单”的研究草稿，而是一份已经把完整交易壳写出来的 raw alpha skeleton。

这对当前 desk 的价值很直接：**不是继续补“pairs 可能能做”的论证，而是补“pairs 怎么以最小工程量先跑起来”的可复现材料。**

## 3. repo 里最值得 desk 关注的几个硬参数
README 公开写了这些关键默认值：

- 交易对：默认 `ETHUSDT / LINKUSDT`
- `TIMEFRAME = 1h`
- `KLINE_LIMIT = 200`
- `Z_SCORE_WINDOW = 21`
- `SIGNAL_TRIGGER_THRESHOLD = 0.02`
- `TRADEABLE_CAPITAL_USDT = 2000`
- leverage：`10x`
- `DROWDOWN_LIMIT_PCT = 90%`

repo 自带回测结果文件 `backtest_results.json` 还给出了一组作者自己的样例：

- starting capital：`2000`
- final capital：`2631.76`
- total PnL：`+631.76`
- total return pct：`+31.59%`
- num trades：`4`
- win rate：`25%`

这里最值得 desk 警惕的点，不是收益高低，而是**参数口径看起来过松**：

1. README 写的 `SIGNAL_TRIGGER_THRESHOLD = 0.02` 对 z-score 来说几乎等于没门槛。  
2. README 还写 `p_value < 0.5` 就算通过，这也明显比多数正式 stat-arb admission 要宽。  
3. `DROWDOWN_LIMIT_PCT = 90%` 更像示例保护，而不是 production 风控。  

也就是说：

> 这份 repo 的正确读法，不是“参数已经对了”，而是“策略骨架已经有了，但 admission / threshold / cost 假设必须重写”。

## 4. desk 视角下，它真正可落地的 raw alpha 长什么样
### 4.1 alpha 本体
- 先选一对在 rolling window 里仍保持稳定线性关系的合约
- 用 OLS 算 hedge ratio
- 构造 spread
- 当 spread 的 rolling z-score 偏离足够大时，做反向配对仓位
- 等 spread 回到均值附近或过零就平

这就是很标准、很清楚的 **relative-value / stat-arb / mean-reversion raw alpha**。

### 4.2 desk 该抄的不是 repo 的默认参数，而是下面这个“短周期版本”
如果把它翻成我们 `15m / 5m` 的最小实验，我会先这样定：

- universe：先从高流动 perp 小池开始，如 `BTC / ETH / SOL / LINK / ADA / DOGE / LTC / XRP`
- pair admission：
  - rolling corr 不低于某阈值
  - hedge ratio 稳定，不要频繁翻倍跳变
  - spread 波动率不能太低，否则全是手续费策略
  - pair 最近 `N` 天 funding 差异不能极端
- signal：
  - `15m` 主信号：`|z| >= 2.0` 入场
  - `5m` 不建议直接复刻 repo 的超松阈值，更适合做 finer execution / 早退 / veto
- exit：`z` 过零或回到 `|z| <= 0.3~0.5`
- sizing：
  - baseline 先做 beta-neutral / equal-risk，不要直接照抄 50/50 名义资金
- risk：
  - `|z| >= 3.0~3.5` stop
  - 单笔最长持有时间上限
  - pair 级别 drawdown kill-switch
  - 两腿成交不同步时直接撤/减
- cost：
  - maker/taker 分开测
  - 两腿四次成交的总成本要显式进回测
  - funding 不能省略

## 5. 本地 public-data 快检：repo 这套壳能跑，但当前 gross edge 明显不够覆盖成本
我用 Binance 公共 `ETHUSDT / LINKUSDT` 做了一个最小 proxy，不复现 repo 内部结果，只测“这套壳压到 short-cycle 后像不像真实可交易候选”。

### 5.1 `15m` probe
口径：
- 最近 `1500` 根 `15m` bars
- OLS beta 构 spread
- `entry = |z| >= 2.0`
- `exit = z` 过零
- `stop = |z| >= 3.5`
- 不加 funding，不做盘口撮合，仅 public close proxy

结果：
- corr：`0.944`
- half-life：约 `83.4 bars`，折合约 `20.8h`
- Hurst：`0.415`
- 触发交易：`51` 笔
- 胜率：`56.9%`
- 单笔平均 **gross**：约 `+3.84 bps`
- median hold：`13 bars`，约 `3.25h`
- 若套用 repo 自己的 `15bps` 成本 proxy，单笔平均变成约 **`-11.16 bps`**

### 5.2 `5m` probe
口径：
- 最近 `1500` 根 `5m` bars
- 同一套 spread / z-score 思路
- 加一个 `48 bars` time stop（约 `4h`）

结果：
- corr：`0.900`
- half-life：约 `127.5 bars`，折合约 `10.6h`
- Hurst：`0.447`
- 触发交易：`49` 笔
- 胜率：`71.4%`
- 单笔平均 **gross**：约 `+4.08 bps`
- median hold：`11 bars`，约 `55min`
- 若套用 repo `15bps` 成本 proxy，单笔平均约 **`-10.92 bps`**

这组结果非常关键：

> **它说明 repo 的 alpha 骨架是能工作的，但在 short-cycle 上如果不先把成本、入场强度和 pair admission 重写，gross edge 大概率会被手续费直接吃掉。**

所以，这份材料更适合被 desk 当成：
- 一个可直接拆 entry/exit/risk 的完整 raw alpha skeleton；
- 而不是一个“参数原样照搬即可上线”的现成策略。

## 6. 这条线与当前 short-cycle desk 的直接关系
这轮之所以值得进研究池，是因为它直接服务于 **raw alpha 素材池**，而不是泛泛的解释型综述：

- 它是 **独立可复现** 的 raw alpha：cointegrated spread mean reversion
- 它能直接补全完整策略组件：entry / exit / sizing / risk / cost / live-state
- 它适配我们当前频段：`15m` 适合主信号，`5m` 适合 execution / veto / 早退
- 它还能跟已有 pairs / carry / microstructure 素材池拼接：
  - pairs alpha 本体 = spread fade
  - shared gate = funding / OI / liquidity / volatility veto
  - risk overlay = drawdown kill-switch / time stop / leg-sync protection

## 7. 我对这份 repo 的结论
一句话版：

> **这不是一份“参数靠谱”的 repo，但它是一份“骨架很适合直接搬到 desk 实验台”的 repo。**

最值得拿走的不是 `0.02` 这种阈值，而是：
- pair scan
- spread + zscore 信号定义
- 双腿同步执行壳
- live state machine
- drawdown kill-switch

最值得立即改掉的是：
- 过松的 signal threshold
- 过宽的协整 admission
- 50/50 名义仓位
- 对真实成本的低估

## 8. 下一步怎么测
只给最小、可执行的下一步，不讲空话：

1. **先做 15m 主信号版，不要一上来就 1m。**  
   - universe：`BTC / ETH / SOL / LINK / ADA / DOGE / LTC / XRP`  
   - rolling window：`200~400` bars  
   - 只保留 corr 稳定、spread 波动率足够、beta 不乱跳的 pair

2. **把 repo 的入场阈值重写成真正有成本余量的版本。**  
   - baseline A：`entry |z| >= 2.0`，`exit |z| <= 0.5`，`stop |z| >= 3.5`  
   - baseline B：`entry |z| >= 2.5`，测 trade count 是否显著下降但 gross/trade 抬升

3. **仓位改成 beta-neutral / residual-vol scaled。**  
   不要再用 README 的 50/50 名义资金；短周期两腿波动不对称时，这会把 spread alpha 变成方向暴露。

4. **显式打三档成本回测。**  
   - maker-favored：`4~6 bps` round-trip  
   - mixed：`8~12 bps`  
   - stressed：`15~20 bps`  
   只保留在 mixed 档还能活的 pair。

5. **把 5m 降级成 execution 层，而不是主 alpha 层。**  
   用 `5m` 做：
   - 入场分批
   - z-score 回归到一半先减仓
   - 波动突增时提前 flat

## 9. 相关文件与链接
- 研究笔记：`research/quant_digests/2026-04-04_1602_cointegration-killswitch-cost-veto-alpha.md`
- 本地快检结果：`reports/artifacts/quant_digests/2026-04-04_ssanin82_eth_link_proxy.json`
- repo：<https://github.com/ssanin82/strat-test-cointegration>
- foundation paper：<https://www.jstor.org/stable/1913236>
