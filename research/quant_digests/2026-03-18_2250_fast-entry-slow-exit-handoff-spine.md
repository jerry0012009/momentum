# 别把 fail-fast 当成 15m 全程管理：先让 entry 快，活下来后再 handoff 到 slow Donchian / Chandelier exit
- 时间：2026-03-18 22:50 UTC
- 类型：GitHub
- 主题标签：breakout-short / fibonacci / retest-hold / ema / psar / continuation / exit / trailing-stop / chandelier / donchian / repo / crypto / 15m
- 证据类型：源码证据 + 工程迁移假设

## 1. 这次看了什么
这次看的是 **yukai1625 (2025), `freqtrade-strategy-portfolio`** 里的 `CTAAggressiveBreakout`。它不是一篇“证明 alpha 很强”的论文型材料，反而更像一份已经把交易哲学写进代码里的 repo：**入场用快时钟，出场故意用慢时钟。**

对我们 desk 真正值得偷的，不是“Donchian 突破”这件老事，而是它把 post-entry 管理拆得很清楚：
- 入场看 `new breakout + volume filter`；
- 真正离场不跟着 entry 一起同速翻脸，而是交给 **更慢的 Donchian exit** 或 **ATR Chandelier stop**；
- 只有在很极端的拉升里，才额外用 `RSI + BB upper` 做一次低频获利了结。

翻成人话：**fail-fast 可以是前 2~3 根 bar 的生死检查，但不必是整笔 15m 交易从头到尾都拴着的狗绳。** 一旦 continuation 已经走出来，更合理的做法可能是：把仓位管理 handoff 给更慢、更钝的 hold-time spine。

## 2. 最值得记下来的源码事实
这份 repo 的信息量不在故事，在参数：
- 基础周期直接就是 **5m**，非常接近我们现在的执行颗粒度。
- 入场 `breakout_len` 超参范围是 **15~40**，默认 **20**；也就是它承认 entry 应该更敏感。
- 退出 `exit_len` 超参范围是 **25~80**，默认 **35**；也就是 exit 明确比 entry 更慢。
- `ATR` 周期可调 **7~35**，`atr_mult` 可调 **2.5~5.0**，默认 **3.5**；Chandelier stop 不是贴身 stop，而是给趋势单留喘息空间。
- 额外获利了结条件也写得很克制：`RSI > 90` 且 `close > BB upper` 才触发，显然不是想把每一笔都快进快出。

一句话总结源码逻辑：**先用快 trigger 抓到“开始动了”，再用慢 exit 判断“是不是已经真走坏了”。**

## 3. 为什么这轮值得先写，而不是继续加新的 entry filter
如果只看今天 bot7 已经消化过的材料，三条收口线的“前段确认”其实已经很拥挤了：
- breakout-short 已经补过 `fail-fast / path overlay / follow-up gate`；
- Fibonacci 已经补过 `0.618 hold / 0.5 fail / retest quality`；
- EMA / PSAR 也已经有 `role framing / close-confirm / regime veto`。

这时候继续往 entry 端再塞一个新 veto，边际价值未必最高。**更缺的反而是：一旦 entry 被确认，后半段到底该用什么 clock 管理。** 这正好对应 backlog 里还没独立实验的 `trailing stop 变体`。

所以这轮主题比继续找一个“新入场按钮”更值：它不是把三条线带偏，而是给三条线补了一个共同缺口——**post-confirmation 之后的持仓时钟。**

## 4. 对三条收口线各自的启发
### 4.1 `V3 final-verdict / breakout-short follow-up`
对 breakout-short 来说，最容易犯的错不是“没看到 break”，而是**刚 break 完、第一下逆抽就把 continuation 当失效**。repo 给的启发是：
- `fail-fast` 仍然保留，但只负责最前段；
- 如果 trade 已经活过前几根 bar，exit 要切到更慢的结构钟；
- 短边可先做镜像版：`rolling_low + ATR` 改成 **short-side chandelier = rolling_low + k * ATR**，再配 `slow Donchian high` 作为结构失效线。

### 4.2 `Fibonacci confirmation / retest_hold`
对 Fib 来说，`0.5 fail` 很适合当**是否 hold 失败**的底线，但未必适合当**整笔仓位一路怎么出**的唯一规则。更像的做法是：
- entry 继续用 `0.618 hold / reclaim / confirmation`；
- 若 entry 后存活 `N` 根 bar 或者顺向走出 `0.75~1.0 ATR`，再切到 slow exit；
- 这样可以把“是否确认成功”和“确认成功后怎么拿”拆开，不再混成一个开关。

### 4.3 `EMA / PSAR raw alpha focus`
EMA / PSAR 这条线现在最该警惕的是：**别把所有改进都压到入场。** 如果 raw alpha 本身有一点延续底子，那么更便宜的增益，可能来自 post-entry management 而不是新 filter。尤其 PSAR 这类天生偏快的翻面工具，更适合做 early-warning，而不是整笔单一路追着翻。

## 5. 最小实验：先测“两段式 exit”，不是直接全量换系统
### 研究假设
**两段式 exit**（前段 fail-fast，存活后 handoff 到 slow exit）会优于：
1. 全程都用 fail-fast；
2. 一上来就全程 slow trailing；
3. 只看固定 TP/SL。

### 冻结口径
- 资产：BTC / ETH / SOL perpetual
- 周期：主评估先做 **15m**，必要时补 **5m execution / 15m signal**
- 样本：近 **180d~365d**
- 成本：至少跑 **6 / 10 / 15 bps** 三档
- 规则：**entry 完全冻结**，只改 exit，避免把 alpha 和管理层混在一起

### 对照组
- `A`：现有 baseline exit
- `B`：全程 fail-fast（沿用现有 fast failure 规则）
- `C`：全程 slow Donchian / Chandelier
- `D`：**handoff 版**：前 `2~3` 根 bar 用 fail-fast；若未触发，且顺向浮盈达到 `0.75 ATR` 或存活满 `3` 根 bar，则切到 slow exit

### slow exit 的最小实现
- Long：
  - `chandelier_long = rolling_high(L) - k * ATR(14)`
  - `donchian_exit_long = close < rolling_low(L_exit)`
- Short：
  - `chandelier_short = rolling_low(L) + k * ATR(14)`
  - `donchian_exit_short = close > rolling_high(L_exit)`
- 第一轮参数别贪多：`L/L_exit ∈ {20, 35}`，`k ∈ {3.0, 3.5}` 就够了。

### 第一轮最该看什么
1. `post_cost_expectancy`
2. `winner_median_return` / `winner_hold_bars`
3. `MFE_capture_ratio`（最大有利波动到底有没有被拿住）
4. `giveback_after_handoff`（handoff 后是否只是把利润吐回去）

## 6. 风险与保留意见
- 这份 repo 本质是 **工程 repo，不是严肃论文**；它给的是可执行假设，不是已经被 OOS / 成本充分证明的答案。
- 源码主版本是 **long-only**，short-side 镜像虽然直觉上合理，但必须单独验证，不能偷懒当作自动对称。
- trailing exit 很容易把 winner 拉长，也很容易把纸面利润吐回去；所以一定要看 `MFE_capture_ratio` 和 giveback，而不只看均值收益。
- handoff 阈值（`2~3 bars`、`0.75 ATR`）也可能过拟合；第一轮要用粗网格，小参数族，不要把管理层调成第二个黑盒。

## 7. 下一步怎么测
最直接的一步，不是再写新 digest，而是把 **当前三条线里已经冻结的 entry** 各抽 1 个代表版本，跑同一套 `A/B/C/D` exit 对照：
- breakout-short：选当前最接近 `final-verdict` 的 follow-up 版本；
- Fibonacci：选 `0.618 hold / 0.5 fail` 当前最诚实版本；
- EMA / PSAR：选 raw alpha 最干净的 base lane。

如果结果显示：
- `D` 组能稳定抬升 `winner_median_return`，
- 同时没有把 `post_cost_expectancy` 和 `max drawdown` 明显拖坏，
那它就值得升成三条线共用的 **shared exit overlay candidate**；否则就把它老实留在 backlog，不要因为“听起来高级”就偷渡进主线。

## 8. 来源
### 主要来源（Repo）
- yukai1625 (2025), **freqtrade-strategy-portfolio**
- Repo URL: https://github.com/yukai1625/freqtrade-strategy-portfolio
- Repo API metadata: https://api.github.com/repos/yukai1625/freqtrade-strategy-portfolio
- Readable strategy file URL: https://github.com/yukai1625/freqtrade-strategy-portfolio/blob/main/strategies/cta_aggressive_breakout.py
- Raw strategy file URL: https://raw.githubusercontent.com/yukai1625/freqtrade-strategy-portfolio/main/strategies/cta_aggressive_breakout.py

### 补充来源（背景参考）
- SC4RECOIN, **simple-crypto-breakout-strategy**（作为更朴素的 breakout baseline，对比用，不是本次主论点来源）
- Repo URL: https://github.com/SC4RECOIN/simple-crypto-breakout-strategy
- README URL: https://raw.githubusercontent.com/SC4RECOIN/simple-crypto-breakout-strategy/main/README.md
