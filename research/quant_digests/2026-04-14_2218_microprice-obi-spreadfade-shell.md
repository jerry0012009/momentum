# 别把这份 HFT repo 只读成低延迟炫技：对 short-cycle desk，更该先拆的是「microprice spread z-score fade × OBI veto」这条 raw alpha 壳

- 主题类型：raw alpha
- 基础 alpha：**对协整 pair 的 `microprice log-spread` 做均值回复；当 spread 的 z-score 走到极端时反向做配对，`OBI`（order-book imbalance）只负责开仓放行/否决，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 时间：2026-04-14 22:18 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `main.cpp` + `optimizer.py` + `analyzer.py` + `book_recorder.py` + `data_loader.py` + `fix_strategies.py`）+ Binance USDⓈ-M `1h/1m/1s` public-data portability probe
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/microprice/order-book-imbalance/obi/microstructure/hft/binance-perpetual/1s/1m/3m/5m/repo/public-data/cost/risk
- 证据类型：repo source audit + public-data live probe + public-data portability backtest

## 1. 这次为什么选它

这轮默认还是优先补 **raw alpha 素材池**，而不是再写一个纯 gate / overlay。

最近几篇 digest 已经写过不少 `pairs / cointegration / spread fade`，但还没单独把这条线拆清楚：

> **当 spread 本体还是老老实实的均值回复时，能不能把“更快的定价口径（microprice）+ 更近盘口的 admission（OBI veto）+ 更像生产壳的执行线程”拼成一条更短周期的 pairs shell？**

这份 repo 值得看的地方，不是作者自称 `~42µs` 逻辑延迟，也不是 `AWS Tokyo` 这些工程姿势；真正值得 desk 收进池子的，是它把下面三件事放在了一条链里：

1. **pair admission**：先用相关性 / 协整 / ADF / half-life 找 pair；
2. **signal**：对 pair 的 `microprice spread` 做 z-score fade；
3. **execution veto**：用两个腿各自的 `OBI` 决定是否允许开仓。

一句话说，它不是“又一个普通 z-score pair notebook”，而是：

> **把 `spread mean reversion` 这条 raw alpha，往真正更短的微观结构执行层又推了一步。**

## 2. 这次看了什么

### 2.1 仓库信息

- **Author**：Samarth Chaudhary
- **Year**：2026（repo 创建于 `2026-01-18`，最后 push 于 `2026-02-05`）
- **Title**：`Crypto_Stat-Arb_HFT_Model`
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：<https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>
- **Repo URL**：<https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>

### 2.2 我重点看的源码

- `README.md`
- `main.cpp`
- `optimizer.py`
- `analyzer.py`
- `book_recorder.py`
- `data_loader.py`
- `fix_strategies.py`

这些文件基本把作者想表达的结构都摆出来了：
- Python 端负责研究、找 pair、扫参数；
- C++ 端负责接 `!bookTicker`、算 `microprice`、看 spread z-score、下单、风控；
- 中间靠 `strategies.json` 做 research-to-execution handoff。

## 3. 先把 base alpha 说死：不是 OBI alpha，也不是 latency alpha

这篇东西的 **base alpha** 是什么？

> **base alpha = 协整 pair 的 spread mean reversion。**

更具体点：
- 先定义 spread：`log(p1) - hedge_ratio * log(p2)`；
- 当这个 spread 偏离均值太远时，赌它向均值回归；
- `z > entry` 时做 short spread（卖第一腿、买第二腿）；
- `z < -entry` 时做 long spread（买第一腿、卖第二腿）；
- `z` 回到中心附近就平仓。

这里：
- `microprice` 只是把价格口径从普通 mid/last 推到更接近盘口压力的位置；
- `OBI` 只是开仓 admission / veto；
- 持仓风险、kill switch、reduceOnly close 都是执行壳。

所以它不是：
- 纯 filter；
- 纯 overlay；
- 纯执行框架；
- 也不是“盘口失衡本身就是 alpha”。

它本质上还是一条很标准的：

> **`pairs / stat-arb / relative-value / mean-reversion` raw alpha。**

## 4. repo 里最值得记住的策略骨架

### 4.1 research layer：先找 pair，再做 spread

`analyzer.py` 的路线是：
- 从 Binance USDⓈ-M 拉 liquid USDT 对；
- 先筛相关性（`MIN_CORRELATION = 0.85`）；
- 再跑 OLS hedge ratio；
- 对 spread 做 ADF；
- 再算 half-life；
- 满足条件的 pair 输出到 `cointegrated_pairs.csv`。

翻成人话就是：

> **不是拿任何两个相关币就直接上 z-score，而是先问“它到底像不像一条会回来的 spread”。**

### 4.2 optimizer layer：1m spread 回测 + 参数网格

`optimizer.py` 用的是典型的 spread-fade 网格：
- `WINDOWS = [30, 60, 120, 240, 360]`
- `ENTRY_ZS = [1.5, 2.0, 2.5, 3.0]`
- `EXIT_ZS = [0.0, 0.25, 0.5]`
- `STOP_ZS = [4.0, 5.0, 8.0]`
- `FEE_PCT = 0.0012`

逻辑也很直白：
- `z > entry` → short spread
- `z < -entry` → long spread
- 回到 `exit` 附近平仓
- 或 hit `stop_z` 被打掉

这部分没什么花活，但优点是：**alpha 本体很干净，容易搬到我们自己的 1m / 3m / 5m 研究框架里。**

### 4.3 C++ live layer：真正的新意在 `microprice + OBI veto`

`main.cpp` 里，作者没有直接用 last 或普通 mid，而是用：

> `microprice = (best_bid * ask_vol + best_ask * bid_vol) / (bid_vol + ask_vol)`

也就是：
- 如果 bid 侧挂得更厚，价格口径会偏向 ask；
- 如果 ask 侧挂得更厚，价格口径会偏向 bid。

然后在 pair 信号里再叠一层 `OBI`：
- `obi = (bid_vol - ask_vol) / (bid_vol + ask_vol)`
- 默认阈值：
  - `Z_ENTRY = 2.0`
  - `Z_EXIT = 0.5`
  - `OBI_LONG_THRESHOLD = -0.2`
  - `OBI_SHORT_THRESHOLD = 0.2`
  - `BET_SIZE = 1000`

开仓逻辑可以翻成人话：
- spread 太高时，本来想 short spread；
- 但只有当第一腿没有出现“强烈反向挤压”、第二腿没有出现“明显不利盘口”时，才真的放行；
- 另一边同理。

这层东西最值得 desk 记住的，不是阈值本身，而是它背后的结构：

> **spread alpha 负责告诉你“价差远了”；OBI 负责告诉你“现在追进去会不会刚好撞上盘口不利一侧”。**

## 5. 但它还不能被直接叫做 production shell：源码里有 3 个很关键的断点

这是这轮最值得诚实写出来的部分。

### 5.1 `optimizer.py` 和 `main.cpp` 没真正接上

`optimizer.py` 输出的是：
- `window_minutes`
- `entry_z`
- `exit_z`
- `stop_z`

但 `main.cpp` 真正读取并使用的却是：
- `leg1`
- `leg2`
- `hedge_ratio`
- `mean`
- `std_dev`

也就是说：

> **研究层找到的 entry/exit/stop 参数，live engine 根本没用上。**

### 5.2 `main.cpp` 依赖 `mean/std_dev`，而 optimizer 并不输出它们

这也是为什么 repo 里又多了一份 `fix_strategies.py`：
- 它要拿最近 `200` 根 `1m` K 线，重新给 pair 补 `mean` 和 `std_dev`；
- 没这一步，`main.cpp` 直接拿 optimizer 产出的 `strategies.json` 是跑不起来的。

换句话说：

> **repo 现在不是“一键从 research 直通 live”，而是 research 产物还要再补一次参数，才能接进执行层。**

### 5.3 pair admission 里的 half-life 单位有歧义

`analyzer.py` 注释写的是：
- `MAX_HALF_LIFE = 240  # Max 4 hours to revert`

但它实际是在 **1 小时重采样数据** 上估 half-life，再直接拿 `hl < 240` 做筛选。

这意味着代码实际放行的更像是：
- **`< 240` 个 hourly bars**，也就是远大于 `4h`；
- 注释和实现对不上。

这会直接影响 pair universe：
- admission 可能比作者自己以为的更宽；
- short-horizon desk 想拿来就用，必须先修这个单位问题。

## 6. 我这轮做的 Binance public-data portability probe

为了不只停在源码阅读，我补了两层最小验证：

### 6.1 第一步：先在 liquid universe 里找一个还能讲得通的 pair

我用 Binance USDⓈ-M 当前 `24h quote volume` 前 15 个 USDT 对，抓最近 `325` 根 `1h` 收盘，按 repo 的大框架做了一个 quick pair scan。

其中比较干净的一对是：
- **`DOGEUSDT / XRPUSDT`**
- 相关性：**`0.916`**
- spread ADF `p-value`：**`0.0246`**
- half-life：**`11.6h`**
- OLS hedge ratio：**`0.0562`**

为什么选这对？
- 它比 `SOL/XAG` 这类混着商品代理的 pair 更像纯 crypto liquid pair；
- 也能避开最近 digest 里已经反复写过的 `BTC-ETH` 近邻路径。

### 6.2 第二步：做 180 秒 live microstructure quick check

我按 repo 的思路，用 Binance `depth?limit=5` 连续抓了 `180s` 的 `DOGE/XRP` 五档盘口，计算：
- 两腿各自 `OBI`
- 两腿 `microprice`
- pair spread 的实时 z-score

同时用最近 `200` 根 `1m` close`（配合 hedge ratio）`给 spread 做 `mean/std` 标准化。

产物保存到了：
- `reports/artifacts/quant_digests/doge_xrp_microprice_obi_liveprobe_2026-04-14.csv`

结果很直白：
- `180` 个 1 秒样本里，**`|z| > 2` 的次数是 `0`**；
- `short_signal = 0`；
- `long_signal = 0`；
- z-score 整体分布大概在 **`0.36 ~ 0.68`** 之间。

这说明什么？

> **在 liquid pair 上，这种 `microprice spread + OBI veto` 不是那种“每分钟乱响一堆信号”的玩具。它更像一个低频、挑时机、需要更长观察窗或更多 pair 并行的短周期壳。**

### 6.3 第三步：补一个 7 天 `1m` portability backtest

我继续对同一对 `DOGE/XRP` 抓了最近 `7d` 的 `1m` K 线（`10080` bars），沿用 repo 的参数网格跑最小 spread 回测。

核心结果：

1. **不计费时，spread MR 本体是正的**
   - best params：`window=240`, `entry_z=2.5`, `exit_z=0.5`, `stop_z=8.0`
   - `41` 笔交易
   - 累计 spread PnL：**`+0.0542`**

2. **按 repo 口径的 `12 bps` round-trip 费用后，best 组合转负**
   - best params：`window=360`, `entry_z=3.0`, `exit_z=0.25`, `stop_z=8.0`
   - `22` 笔交易
   - 累计 spread PnL：**`-0.01085`**
   - 胜率：**`59.1%`**
   - 平均持有：**`155.8` 分钟**

3. **如果 friction 压到约 `6 bps` round-trip，best 组合又回到正值**
   - 累计 spread PnL：**`+0.02075`**

4. **信号本身并不稀缺**
   - `|z| > 1.5`：`2674` 次
   - `|z| > 2.0`：`1492` 次
   - `|z| > 2.5`：`769` 次

这组数字最重要的解读不是“它能直接上”，而是：

> **spread MR 本体存在，但它对 friction 非常敏感；repo 里那种 HFT/microstructure 包装，不是锦上添花，而是它能否活下来的核心。**

## 7. first verdict：这是 raw alpha，但还不是可直接落地的完整策略

把这轮结论压缩成四句话：

1. **它是 raw alpha，不是 filter。**
   - base alpha 很清楚，就是 `pair spread mean reversion`。

2. **它能独立复现。**
   - Binance public klines / depth 就够搭一个最小实验。

3. **它还不能直接落地成完整 production shell。**
   - research/live handoff 没接好；
   - 成本假设能把 edge 直接打穿；
   - 还缺 queue position / slippage / partial-fill / maker fill realism。

4. **它更像“低摩擦 + 更强执行”的 pocket。**
   - 如果 execution 还是粗糙 taker，edge 很容易没；
   - 如果能做更像 maker-first / passive-close / latency-sensitive 的 close-out，这条线才有继续挖的意义。

所以这轮 4 字段应该老实写成：
- 主题类型：`raw alpha`
- 基础 alpha：`microprice spread mean reversion`
- 是否可独立复现：`是`
- 是否可直接落地完整策略：`否`

## 8. 这条线为什么仍然值得进入研究池

### 8.1 它补的不是“又一个 pairs 标题”，而是 `pairs × microstructure admission`

最近 pairs digest 已经不少，但多数还停在：
- close-to-close spread
- 15m/5m z-score
- vol gate / pair admission / rolling beta

这份 repo 额外给出的，是：

> **把 spread 的观察口径往盘口推进一层，把 admission 也往盘口推进一层。**

这对 short-cycle desk 是有增量的。

### 8.2 它把“alpha 本体”和“执行壳”分得还算清楚

这点很重要。源码虽然有断点，但结构上没有混淆：
- alpha 本体：spread extreme → mean reversion
- admission：OBI veto
- 风控：per-position loss / global kill switch
- 执行：persistent order thread + reduceOnly close

这种拆法对我们自己重写最有帮助。

### 8.3 它提醒了一个现实：HFT 外壳不是装饰，而是 edge 的一部分

这类 alpha 在 `1m` 甚至更快层面，常见误判就是：
- 只做 signal notebook；
- 把 fill / queue / spread crossing 当成“后面再说”。

这轮 quick probe 恰好反过来提醒：

> **如果 friction 压不下去，那你看到的可能只是“有方向感的统计现象”，不一定是“可交易的 PnL”。**

## 9. 下一步怎么测

我不建议下一步继续在同一套粗糙 taker 框架里磨参数；更值钱的是下面 4 件事：

### 9.1 先修 research-to-live handoff

必须先改掉两处硬伤：
- 让 `optimizer.py` 直接输出 `mean/std_dev`；
- 让 `main.cpp` 真正读取并使用 `window/entry/exit/stop`，不要继续硬编码 `Z_ENTRY/Z_EXIT`。

不修这个，后面所有 live probe 都会混着配置漂移。

### 9.2 把 pair admission 改成真正适合 short-cycle 的口径

建议：
- 用 rolling `7d/14d` 的 `1h` 协整 / ADF / half-life 重估；
- 明确把 half-life 上限改成 **`<= 12h` 或 `<= 24h`**，不要再放一个注释和代码不一致的 `240`；
- top-30 liquid perp 并行筛 pair，而不是盯单对。

### 9.3 execution 先测“maker-first close-out”，不要急着追更多 signal

最小实验可以这样分层：
- `1m` 决定 state 和方向；
- `5s/1s` 决定是否放行；
- 平仓优先挂被动单，或做更保守的 close-out 窗口；
- 把实际 friction 压到 `<= 6 bps` 再看这条线是否还能活。

### 9.4 OBI 别再用固定阈值，改成分位数 / z-score 版

`±0.2` 这种裸阈值太依赖单币微观结构。

下一轮更值得测的是：
- pair 内部做 rolling OBI z-score；
- 或对每个币做最近 `N` 秒 / `N` 分钟的 OBI percentile；
- 只在 spread 极端 + OBI 不逆风时放行。

这样更容易扩到不同 liquidity bucket。

## 10. 相关产物

- live probe 数据：`reports/artifacts/quant_digests/doge_xrp_microprice_obi_liveprobe_2026-04-14.csv`
- 本轮 summary：`reports/artifacts/quant_digests/crypto_statarb_hft_probe_summary_2026-04-14.json`

## 11. 来源

1. **Samarth Chaudhary. (2026). _Crypto_Stat-Arb_HFT_Model_. GitHub repository.**  
   - Readable URL: <https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>  
   - Repo URL: <https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>
2. **Repo source files used in this digest**  
   - `README.md`  
   - `main.cpp`  
   - `optimizer.py`  
   - `analyzer.py`  
   - `book_recorder.py`  
   - `data_loader.py`  
   - `fix_strategies.py`
3. **Public data used for portability check**  
   - Binance USDⓈ-M public klines: <https://fapi.binance.com/fapi/v1/klines>  
   - Binance USDⓈ-M public depth: <https://fapi.binance.com/fapi/v1/depth>
