# 别把 Hurst / ADX / RV 一股脑塞进 15m 进场：更值得先测的是 4-state regime matrix，给三条线做 shared allow/deny gate
- 时间：2026-03-18 17:07 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/regime/hurst/adx/realized-volatility/filter/repo/crypto/15m
- 证据类型：仓库脚本 + 公开 OHLCV / 可快速复现实验

## 1. 这次看了什么
这次看的是 GitHub 仓库 `damianpitt/capital41-indicators`（2026）里的 `Capital41 Regime Matrix v2`。整套 repo 面向 `30m / 4h`，而且带不少配套脚本，不适合整套照抄；但其中这一支很适合现在 desk：**别再给 `breakout-short`、`Fib retest_hold`、`EMA / PSAR` 各自补一堆零散过滤器，先把“当前到底更像趋势、扩张、压缩，还是均值回归”冻结成一个共享 state gate。**

## 2. 核心结论
- **一句话核心结论**：这份 repo 最值得偷的不是它的 adaptive EMA 或 ATR 止损宽度，而是一个更朴素、也更适合我们当前三条收口线的想法：**先用 4-state regime matrix 决定 setup 能不能开火，再讨论具体 entry 长什么样。**
- **一句话证明方式**：源码把状态机写得很清楚：`Trend = Hurst >= 0.58 & ADX >= 22 & ADX slope > 0`，`Expansion = RV slope > threshold & ADX slope > 0 & 非 Trend`，`Compression = RV slope < -threshold & ADX <= 16`，其余归到 `Mean Reversion`；再把状态映射到 EMA / ATR 宽度与 `pressure 0~100`。这说明它本质上不是单指标判断，而是**把路径持久性、趋势强度、波动变化三件事拼成一个可编程状态标签**。
- 这题现在值得做，因为它正好对上 `FACTOR_BACKLOG` 里已经被列为 `P0` 的 `Volatility regime filter`：我们已经知道“三条线都怕在错的市场状态里硬做”，但还缺一个比单独 `session`、`OI`、`VWAP` 更系统的状态框架。
- 对 desk 最有价值的读法，不是“让 adaptive EMA 直接替换现有 EMA / PSAR”，而是把它降级成 **shared allow/deny layer**：`Trend / Expansion` 更像 continuation 允许态，`Compression` 更像 breakout 准备态，`Mean Reversion` 更像该减仓或禁入的坏环境。
- 如果要回答“它为什么比继续给三条线各补一个小滤镜更值得”，答案也很简单：**因为三条线现在缺的不是第 N 个局部 trigger，而是一层能统一解释什么时候该做、什么时候别做的共同状态语言。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：最该测的不是在每次破位后再加一个花哨图形，而是 **只有在 `Trend / Expansion` 状态里才允许 follow-up short`；若落在 `Mean Reversion`，就把它当高风险假跌破区。** `Compression -> Expansion` 转换则可以单独当 breakout 启动态样本。
- 对 `Fibonacci confirmation / retest_hold`：Fib 负责回答“回到哪一段”，regime matrix 负责回答“这段回踩所在的市场环境，像趋势延续还是像来回甩”。也就是：**Fib 给位置，state gate 给环境许可。**
- 对 `EMA / PSAR raw alpha focus`：它现在最缺的不是更多均线，而是一个能回答“这类顺势信号在哪些 bar 结构里天然更容易被来回打脸”的 shared veto。`Mean Reversion` 与低 pressure 状态正好可以扮这个角色。
- 更关键的是，这条线只需要公开 OHLCV，就能先做最小实验；它比再引入一条更贵的外部数据更适合当前快验证节奏。

## 4. 可复刻的最小实验
- **研究假设**：对现有 `breakout_short`、`fib_retest_hold`、`ema_psar_raw` 来说，用一个上层 `30m` regime label 去 gate `15m` setup，比继续堆单点确认条件，更可能稳定降低 `false-break / false-hold / chop-loss`。
- **公开数据源**：Binance perpetual `15m` 与聚合成 `30m` 的 OHLCV 即可；不需要订单簿、资金费率、OI 或额外低频宏观数据。
- **最小可计算定义**：
  1. 先在 `30m` 计算简化版 regime：`hurst_100`、`ADX14`、`ADX slope(5)`、`rv20 = stdev(logret, 20)`、`rv slope(5)`；
  2. 用 repo 默认阈值先冻结四态：`Trend / Expansion / Compression / MR`；
  3. 再把 `30m` 状态 forward-fill 到子级 `15m` bar；
  4. 第一轮先**不要**接它的 adaptive EMA / stop 宽度，只测 state gate 本身；
  5. 可选再补一个方向压力分数：`pressure > 60` 只给 long continuation，`pressure < 40` 只给 short continuation。
- **第一轮 bucket**：
  1. `base`：现有 setup 原样；
  2. `no-MR gate`：只删除 `Mean Reversion` 状态样本；
  3. `trend-expansion only`：只保留 `Trend / Expansion`；
  4. `compression-breakout arm`：只看 `Compression -> Expansion` 切换后 `1~3` 根内的 breakout/follow-up。
- **最先看的 4 个指标**：`post-cost expectancy`、`trade count retention`、`false-break / false-hold rate`、`4/8 bar forward return dispersion`。
- **下一步怎么测**：先别在 `15m` 直接重算一堆高噪声 Hurst，也别碰 repo 里的自适应参数。第一轮就固定 `BTC / ETH / SOL` perpetual、最近 `180d`、`15m` 入场、`30m` 状态门控、`next-bar open`、`no-overlap`，只回答一个问题：**删掉 `MR` 或只保留 `Trend / Expansion`，能不能在不把样本砍废的前提下，稳定改善三条线的 continuation 质量？** 如果连这一步都没有增量，就没必要继续把 Hurst / ADX / RV 包装成更复杂的 meta model。

## 5. 风险与保留意见
- 这份 repo 的主定位是 `30m / 4h`，不是为 `15m` crypto 精调过的现成模板；直接把原阈值原封不动搬到 `15m`，很容易把 regime classifier 变成噪声放大器。
- 里面的 Hurst 近似写法很轻量，适合做快实验，不代表就是最稳的长期定义；如果第一轮有增量，下一步再考虑更稳的 persistence proxy，而不是反过来一开始就优化 Hurst。
- `Compression` 与我们今天早些时候已经写过的 `squeeze -> release` 有信息重叠，所以后续必须做 ablation：确认 regime matrix 真的带来额外解释力，而不是换个更高级名字重复讲压缩。
- 不要太早使用它的 adaptive EMA 与 stop 宽度；那会把“状态判别对不对”和“参数改了所以看起来变好”混在一起，第一轮结论会不诚实。

## 6. 来源
- Damian Pitt / CAPITAL41. (2026). *capital41-indicators* — `Capital41 Regime Matrix v2`. GitHub repository.
  - Venue / DOI：GitHub / N/A
  - Repo URL: <https://github.com/damianpitt/capital41-indicators>
  - Readable URL: <https://github.com/damianpitt/capital41-indicators>
  - README: <https://raw.githubusercontent.com/damianpitt/capital41-indicators/main/README.md>
  - Regime Matrix source: <https://raw.githubusercontent.com/damianpitt/capital41-indicators/main/Capital41_RegimeMatrix/Capital41_Regime_Matrix_v2.pine>
  - Repo metadata snapshot: created `2026-01-16`, `2` stars, `0` forks at fetch time.
- Binance USDⓈ-M Futures. *Kline/Candlestick Data*.
  - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
  - 用途：构造 `15m` 主图与 `30m` 上层 regime label 的最小实验数据源。
