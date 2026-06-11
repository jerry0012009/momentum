# 别把这份 2026 Hyperliquid 新 repo 只读成“策略大杂烩”：对 short-cycle desk，更该先测的是「ADX/ATR regime switch × trend sleeve / mean-reversion sleeve」这条完整 raw alpha
- 时间：2026-04-03 10:20 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `src/strategies/adaptive_regime.py` + `config/settings.yaml` + `src/engine/backtest.py` + `src/engine/portfolio.py`）
- 主题类型：raw alpha
- 基础 alpha：**regime-switched dual raw alpha**；趋势态做 `MA crossover + DI confirmation`，震荡态做 `BB overshoot + RSI fade`，高波动态降仓/停手，赌的是“不同市场状态该由不同 alpha 接管”，而不是任何时候都死跑同一套信号
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/regime-switched/trend/mean-reversion/single-asset/adx/atr/bollinger/rsi/moving-average/directional-index/trailing-stop/kill-switch/hyperliquid/5m/15m/3m/1m/repo/public-data/cost/risk
- 证据类型：repo 源码证据（主）+ 内置回测结果（辅）

## 1. 这次看了什么
### 一句话核心结论
**这轮最值得 intake 的，不是 repo 里“又有 9 个策略”的广度，而是它已经把一条可独立成卡的完整策略写清楚了：先用 `ATR expansion + ADX` 判断当前更像波动爆发、趋势推进还是区间来回，再把趋势 alpha 和均值回复 alpha 分开接管。**

### 一句话它是怎么证明的
**不是靠 README 里空泛讲逻辑，而是源码把 regime 判定、两个 raw alpha sleeve、仓位切换、ATR trailing stop、手续费/滑点、单笔仓位上限和 drawdown kill switch 都写死了。**

## 2. 先回答最重要的问题：这篇东西的 base alpha 是什么
先把这句说死：

> **base alpha 不是单独的 ADX，也不是单独的 filter。它的本体是“一条可交易的 regime-switched dual-alpha strategy”——趋势态吃 continuation，区间态吃 overshoot snapback。**

更直白一点：
- 如果市场正在走趋势，就不要硬做左侧回归；
- 如果市场只是区间摆动，就不要拿均线突破去追；
- 如果 ATR 突然扩张到异常水平，就先把仓位降下来，承认“现在最重要的是别死”。

所以它不是纯 `filter / regime / overlay`，而是一个**能独立下单、独立回测、独立做风控**的完整 raw alpha 壳。

## 3. 为什么这轮值得写，而不是继续补一篇单腿 trend / 单腿 MR
这轮虽然不是“新论文 headline alpha”，但它仍然值得进本轮 intake，原因很直接：

1. **它仍然优先服务 raw alpha。** 不是讲抽象状态识别，而是把两个可独立交易的 raw alpha（trend / mean reversion）接成一条完整策略。
2. **它正好衔接当前学习主线。** `LEARNING_TRACK` 明确把“趋势跟随、波动管理、市场状态过滤”列为核心模块；`FACTOR_BACKLOG` 也把 `ATR position sizing`、`volatility regime filter` 置于高优先级。这个 repo 给的是一张现成的“把这些模块焊在一起”的策略卡。
3. **它和最近 digest 的关系是“往前拼装”，不是重复。** 最近素材池已经补了不少：
   - 单资产趋势壳
   - 单资产 mean reversion 壳
   - 各类 overlay / gate / sizing
   但“**什么时候该让哪条 alpha 接管**”这一层，还缺一张足够简单、足够可复现的完整卡。
4. **它适合快验证。** 所有输入都只依赖公开 OHLCV，先做 `15m` existence test 很容易，随后可自然下钻到 `5m`。

所以更准确的定位是：

> **这不是拿 regime 当主角的一篇 filter digest，而是一条把两类 raw alpha 装进同一个状态机里的“完整策略候选”。**

## 4. 来源信息
### 主来源
- **Repo owner：** `andreaambrosio`
- **Year：** 2026
- **Title：** `hype-backtesting`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/andreaambrosio/hype-backtesting>
- **Repo URL：** <https://github.com/andreaambrosio/hype-backtesting>
- **GitHub metadata：** created `2026-03-12T16:34:49Z`，pushed `2026-03-12T20:35:33Z`，default branch `main`
- **Repo description：** `Crypto & equities backtesting framework — Hyperliquid HIP-3, funding arb, basis trade, momentum, mean reversion`

### 本文主审计文件
- `README.md`
- `src/strategies/adaptive_regime.py`
- `config/settings.yaml`
- `src/engine/backtest.py`
- `src/engine/portfolio.py`

## 5. 源码到底把这条策略写成了什么样
## 5.1 Regime detection：先分状态，再决定谁上场
`adaptive_regime.py` 默认参数：
- `adx_period = 14`
- `adx_trend_threshold = 25`
- `adx_range_threshold = 20`
- `atr_expansion = 1.5`

状态判断顺序：
1. 若当前 ATR 相对前一段 ATR 扩张超过 `1.5x` → `volatile`
2. 否则若 `ADX > 25` → `trending`
3. 否则若 `ADX < 20` → `ranging`
4. 其他 → `neutral`

这里最有价值的不是阈值本身，而是它承认一件很现实的事：

> **“趋势存在” 和 “波动正在失控” 不是一回事。**

也就是说，作者没有把所有强运动都当趋势继续追，而是先给“波动爆发”单独留了一个档位。

## 5.2 Trending sleeve：趋势态不是裸追，而是 crossover + DI 共振
趋势态用的不是复杂模型，而是很透明的一套：
- `fast_ma = 8`
- `slow_ma = 24`
- `plus_di / minus_di` 方向确认

开仓条件：
- **做多：** 上一根 `fast <= slow`，当前 `fast > slow`，且 `+DI > -DI`
- **做空：** 上一根 `fast >= slow`，当前 `fast < slow`，且 `-DI > +DI`

翻成人话：
- 先要求趋势结构真的发生切换；
- 再要求方向动能和这次切换是同向的；
- 不接受“均线刚交叉，但 DI 完全不配合”的半吊子趋势。

所以这里的 raw alpha 是：

> **趋势态下的 own-price continuation。**

## 5.3 Ranging sleeve：区间态才允许做 BB + RSI fade
震荡态参数：
- `bb_period = 20`
- `bb_std = 2.0`
- `rsi_period = 14`
- `rsi_oversold = 30`
- `rsi_overbought = 70`

开仓条件：
- **做多：** `price <= lower_band` 且 `RSI < 30`
- **做空：** `price >= upper_band` 且 `RSI > 70`

这条线的 desk 读法很清楚：

> **只有在 ADX 已经低到更像区间时，才允许把 BB 触边当 overshoot，而不是把它误读成趋势中继。**

这恰好解决了很多均值回复系统的第一死因：
- 在强趋势里过早左侧抄顶/抄底。

所以这里的 raw alpha 是：

> **区间态下的 overshoot snapback。**

## 5.4 Volatile sleeve：不是再发明第三条 alpha，而是直接降速
源码里高波动态没有单独设计新 signal，而是直接把仓位从：
- 常规 `position_size_pct = 0.15`
- 降到 `vol_regime_size = 0.08`

也就是说：
- 这不是高波动下更激进地去追；
- 而是承认高波动更容易让两条 alpha 都变脏；
- 优先做**size-down / sit-out**，而不是硬凑第三条交易逻辑。

这点很符合当前 desk 需要的诚实口径：

> **高波动态更像风险挡位，不是另一个 magical alpha。**

## 5.5 Exit / risk / cost 不是留白，而是完整写进了回测壳
### 统一 trailing stop
无论 long / short，源码都用：
- `trailing_stop_atr = 2.0`
- long：价格跌破 `trailing_high - 2*ATR` 平仓
- short：价格升破 `trailing_low + 2*ATR` 平仓

### 全局回测/组合约束（`config/settings.yaml` + `portfolio.py`）
- `initial_capital = 100000`
- `commission_bps = 2.0`
- `slippage_bps = 1.0`
- `max_position_pct = 0.25`
- `max_drawdown_pct = 0.15`

`portfolio.py` 还明确实现了：
- 按仓位百分比开仓
- 滑点调整 fill price
- 双边 commission 计入平仓 PnL
- 触发 `15%` drawdown 后 kill switch 强平并停机

所以这不是“只有 signal，没有实现细节”的 idea note；它已经是：
- entry
- exit
- trailing stop
- sizing ceiling
- cost accounting
- drawdown kill switch

的完整闭环。

## 6. 这份 repo 里最值得记住的 6 个硬数据点
README 给出的 repo 内置回测结果（**90 天 hourly Hyperliquid 数据**，标的含 `BTC / ETH / SOL / HYPE / TURBO / MEME / WIF`）：

1. **Adaptive Regime 总收益：`+2.78%`**
2. **Sharpe：`0.99`**
3. **Sortino：`1.21`**
4. **Max Drawdown：`11.32%`**
5. **Win rate：`34.9%`**
6. **Trades：`211`**

这组数不能吹成“production-ready alpha 已证实”，因为：
- 样本只有 90 天；
- 频率是 hourly，不是我们真正关心的 `5m/15m`；
- 标的混有较噪的 meme / HIP-3 资产；
- 没有独立 OOS 证明。

但它至少说明两件事：
1. 这不是 PPT 策略，作者确实跑过；
2. 这条策略在“计入 `2bps fee + 1bp slippage`”的壳里并非完全塌掉。

## 7. 我对这条策略的判断：最值钱的是“谁接管市场”，不是 ADX 这个指标本身
如果把这条东西误读成“ADX 大于 25 就买、低于 20 就反着做”，会完全错过重点。

更准确的拆法应该是：
- **raw alpha A：** 趋势 continuation
- **raw alpha B：** 区间 overshoot mean reversion
- **regime router：** `ATR expansion + ADX`
- **risk shell：** ATR trailing + reduced size + kill switch

所以它最值钱的地方不是 invent 新因子，而是把一个我们经常嘴上说、但不常写成完整代码的判断落地了：

> **不同 market regime，应该让不同 alpha 接管。**

这件事和当前素材池的直接关系也很强：
- 最近单独的 trend 卡在补；
- 单独的 mean reversion 卡也在补；
- 现在正好需要一张“二者怎么在同一策略里共存”的卡。

## 8. 它和当前 `1m / 3m / 5m / 15m` 的关系
## 8.1 不是直接抄 hourly，而是拿它做 short-cycle shell
必须诚实：repo 当前展示的是 **hourly Hyperliquid** 结果，不是 short-cycle production 结果。

所以正确落地方式不是“直接把 hourly PnL 当证据”，而是：
- 把它当 **strategy shell**；
- 先迁移到 `15m` 做 existence test；
- 再下钻到 `5m` 看 trade count / cost / whipsaw；
- `1m / 3m` 暂时只当 execution 层，不建议一上来拿来当主信号级别。

## 8.2 为什么它仍然比继续补单腿 alpha 更值得
因为它回答的是更靠近实盘的一句：

> **当 trend alpha 和 mean-reversion alpha 都可能成立时，应该由谁在什么时候上场？**

这比继续再堆一张“又一个单腿 raw alpha”更接近后续 desk 组合层。

但它又没有跳得太远，因为：
- 两条 sleeve 本体都很朴素；
- 不依赖外部稀缺数据；
- 所有状态都能用公开 OHLCV 算；
- 非常适合做 ablation。

## 9. 最小可复现实验
### 实验 A：15m 单币 regime-switched baseline（最优先）
**标的：** `BTC / ETH / SOL` perp

**bar：** `15m`

**状态机：**
- `ADX(14) > 25` → trend sleeve
- `ADX(14) < 20` → range sleeve
- `ATR_now / ATR_prev > 1.5` → volatile size-down

**trend sleeve：**
- `EMA8/EMA24` crossover
- `+DI > -DI` 才做多；`-DI > +DI` 才做空

**range sleeve：**
- `BB20, 2σ`
- `RSI14 < 30` 做多 / `RSI14 > 70` 做空

**统一 exit：**
- `2 * ATR(14)` trailing stop
- 可加一个 `time-stop` 作为 desk 版补充

**成本：**
- round-trip `8 / 12 / 20 / 30 bps`

先只回答一句：

> **在 15m perp 上，regime switching 是否比“永远只跑 trend”或“永远只跑 MR”更耐成本？**

### 实验 B：四组并行 ablation
同一 universe、同一成本，平行跑：
1. **Trend-only**（只留 trend sleeve）
2. **MR-only**（只留 range sleeve）
3. **Trend + MR without vol size-down**
4. **Trend + MR + vol size-down**

要回答的问题：
- regime router 是否真的提升净值分布？
- 高波动 size-down 是不是多此一举？
- 哪个 sleeve 在 `15m` 才是真正主要贡献者？

### 实验 C：从 15m 下钻到 5m
如果 15m 有存在证据，再做：
- signal 仍在 15m 生成
- execution 到 5m 执行
- 或直接 5m 重新估 ADX/ATR/BB/RSI

重点看：
- trade count 是否明显提升
- whipsaw 是否同步爆炸
- fee 后是否还剩正 pocket

## 10. 下一步怎么测
### Step 1：先验证 router 有没有用
第一刀不要优化参数，先比较：
- trend-only
- MR-only
- regime-switched

如果 router 连“把两条已知 raw alpha 接起来”都做不好，就没必要继续给它加更多状态机。

### Step 2：固定 router，再看参数敏感性
优先测：
- `ADX trend threshold = 22 / 25 / 28`
- `ADX range threshold = 18 / 20 / 22`
- `ATR expansion = 1.3 / 1.5 / 1.8`
- `EMA fast/slow = 8/24, 10/30`
- `BB std = 1.8 / 2.0 / 2.2`

### Step 3：看 trade attribution，不只看总收益
必须分开统计：
- trend sleeve 的 trade count / win rate / avg hold / avg pnl
- MR sleeve 的 trade count / win rate / avg hold / avg pnl
- volatile size-down 前后表现差

否则最后很容易只得到一个总 Sharpe，却不知道是哪一条腿在赚钱。

## 11. 主要风险与诚实边界
1. **repo 现有结果是 hourly，不是 5m/15m。** 不能直接拿来当 desk 证据。
2. **ADX / ATR 都有滞后。** 在状态切换很快的市场里，可能出现“刚判成趋势就进入反转”或“刚判成区间就开始突破”。
3. **双 alpha 共存不一定比单 alpha 强。** 组合后也可能只是在两个都不够强的策略之间来回切换。
4. **Hyperliquid 资产结构特殊。** HYPE / TURBO / MEME 的行为不必然可转移到 BTC/ETH 主流 perp。
5. **高波动不等于该减仓到什么程度。** `0.08` 只是 repo 默认值，不是 desk 真理。

## 12. 最终结论
如果这轮只记一件事，我希望记住的是：

> **这份 2026 repo 最值得 desk intake 的，不是“ADX 也能做策略”，而是它把两条不同 raw alpha——趋势 continuation 与区间 mean reversion——通过一个极简状态机接成了完整壳。**

对当前 short-cycle desk 来说，这张卡的价值在于：
- 它仍然是 raw alpha 主题，不是纯 filter；
- 它正好衔接当前学习地图里的 `trend + volatility + regime` 三块；
- 它能非常快地做 `15m -> 5m` 的 ablation；
- 一旦 router 有用，后面很多已有 alpha 卡都可以按这个思路重组。

## 13. 参考来源
1. **andreaambrosio. (2026). _hype-backtesting_. GitHub Repository.**  
   - Repo URL: <https://github.com/andreaambrosio/hype-backtesting>
2. **`README.md`（repo root）**  
   - Readable URL: <https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/README.md>
3. **`src/strategies/adaptive_regime.py`**  
   - Source URL: <https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/src/strategies/adaptive_regime.py>
4. **`config/settings.yaml`**  
   - Source URL: <https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/config/settings.yaml>
5. **`src/engine/backtest.py` / `src/engine/portfolio.py`**  
   - Source URL: <https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/src/engine/backtest.py>  
   - Source URL: <https://raw.githubusercontent.com/andreaambrosio/hype-backtesting/main/src/engine/portfolio.py>

## 14. 归档位置
- Digest：`research/quant_digests/2026-04-03_1020_adaptive-regime-switch-trend-mr-alpha.md`
