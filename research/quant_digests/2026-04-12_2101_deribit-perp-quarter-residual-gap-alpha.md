# 别把这份 2020 Deribit 旧 repo 只看成过时套利脚本：对 short-cycle desk，更该先测的是「perp-vs-quarter residual gap 收敛 × maker-first hedge shell」这条 raw alpha
- 时间：2026-04-12 21:01 UTC
- 类型：GitHub / repo source audit + Deribit public futures live probe
- 主题类型：raw alpha
- 基础 alpha：同 venue、同 underlier 的 `BTC perpetual` 与 `BTC dated future` 本质上共享大部分方向暴露；当顶层可成交 quote 相对“该期限应有 carry”出现异常扩张时，做 `short rich leg / long cheap leg`，赌 residual gap 回落。carry 只是公平价值基线，不是 alpha 本体。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给执行骨架；阈值需按当前期限结构做残差化重标定）
- 主题标签：raw-alpha / relative-value / stat-arb / perp-vs-quarter / quote-gap / carry-residual / convergence / maker-first / deribit / btc / 1m / 3m / 5m / 15m
- 证据类型：工程证据（repo source audit）+ Deribit 公共 API live snapshot

## 1. 这次为什么选它
这轮优先目标还是补 **可独立复现、尽量可直接落地** 的 raw alpha，而不是再写一篇泛泛的 filter / overlay。

我最后选的是 GitHub 仓库 **Hudie / crypto_algo_trading** 里那条 **Deribit perpetual-vs-dated-future** 套利执行壳，重点读了：
- `strategy/backup_deribit_perpetual_future_arb.py`
- `strategy/deribit_cross_future.py`
- `strategy/deribit_cross_remote_future.py`
- `README.md`

先把 **base alpha** 说清楚：

> **不是看 BTC 涨跌，而是看同一条 BTC 曲线里，两条近似同质暴露（perp 与季度 future / 两个远月 future）的可成交价差，是否短时偏离了该期限本该有的 carry 水平，并在几分钟到几十分钟内向中枢回落。**

它属于：
- `raw alpha`
- `relative value / stat-arb`
- `carry / basis` 家族里的 **短周期执行化版本**

和我们之前已经写过的几类主题不一样：
- 不是 **front-vs-back annualized basis** 的 bar-level calendar spread 回测；
- 不是 **basis - implied funding** 的中枢收敛框架；
- 也不是跨 venue options quote gap。

这次真正值钱的，是一个更贴近实盘组件拆解的东西：
**repo 把 entry / edit / cancel / hedge / rebalance 全写成了 live execution shell。**

## 2. repo 里真正可复用的，不是旧阈值，而是完整策略骨架

### 2.1 `backup_deribit_perpetual_future_arb.py` 给的是“先 future 挂 maker，再 perp 做对冲”
从源码可以直接抽出这条执行顺序：

1. 实时监听 `BTC-PERPETUAL` 与一条季度 future 的 quote；
2. 观察两种可成交方向：
   - `future.ask - perp.ask`
   - `perp.bid - future.bid`
3. 当 gap 超过某层 entry threshold，就先在 **future 腿**挂 `post_only limit`；
4. 如果 future 腿成交或部分成交，再用 **perp 腿 market order** 立即把另一边补齐；
5. 若 gap 回落到 admission 区以下，就撤掉 future 挂单；
6. 若持仓腿数不平衡，就额外发一笔 market order 做净额修复。

这套骨架之所以值钱，是因为它不是“看见价差就口头说一句能套利”，而是已经写成：
- entry
- price edit
- cancel
- filled-leg hedge
- net exposure rebalance
- 持仓阈值限制

的完整原型。

### 2.2 源码里能直接看到的关键设计
从 `backup_deribit_perpetual_future_arb.py` 能抽出几件事：

- 触发信号看的是**顶层可成交 gap**，不是收盘价指标；
- 开仓前会按 gap 所处档位决定是否还能继续加仓；
- future 腿挂单后，如果盘口继续移动，会 `edit order` 跟价；
- 若 gap 消失，就 `cancel`；
- future limit fill 后，perp 腿立刻用 market 对冲；
- 若两腿剩余仓位不平，就再做一轮净额修复。

这就是一个非常典型的 **event-driven relative-value execution shell**。

### 2.3 `deribit_cross_future.py` / `deribit_cross_remote_future.py` 说明作者不只做一条配对
同 repo 里还写了：
- `BTC-PERPETUAL` vs `BTC-25SEP20`
- `BTC-25SEP20` vs `BTC-25DEC20`

这说明作者并不是只盯着“perp 对单一季度合约”，而是在做一整个 **同 venue term-structure dislocation family**：
- perp vs 季月
- 近月 vs 远月
- 不同方向各自有分层 gap threshold 与 position threshold

对当前 desk 来说，这意味着它不只是单点灵感，而是一个可以扩成：
- `perp-vs-quarter`
- `front-vs-back`
- `short carry residual`
- `term-structure quote-gap`

的研究分支。

## 3. 但源码不能原样抄：旧 repo 最大的问题，是阈值口径和今天市场不再同尺度
这里要老实一点：**repo 不能直接 clone 就跑。**

原因至少有三层：

### 3.1 合约是 2020 年的历史品种
源码里写死的是类似：
- `BTC-PERPETUAL`
- `BTC-25SEP20`
- `BTC-25DEC20`

这些当然早就过期了。

### 3.2 阈值是旧市场微结构下的数值
源码里存在一堆写死的 gap 档位，比如：
- `LONG_GAP = [1160, 1177, 1200, 1230, 1255]`
- `SHORT_GAP = [245, 40, 30, 10, -20, -60, -110, -170]`
- 另一份脚本里还有 `[180, 225, 270, 315, 360]` 这类档位

这些数值今天不能生搬硬套。真正该保留的是：
- **分层开仓**
- **仓位越大，阈值越苛刻**
- **maker-first / taker-hedge**
- **gap 消失就撤单**

而不是 2020 年那串具体数字。

### 3.3 repo 的配置卫生很差，必须当作“不可信旧生产残片”来读
仓库里配置文件暴露了历史账户配置痕迹，说明这不是一个可以直接接生产的安全工程样板。

对我们来说，正确读法是：
- **保留 alpha 与 execution 结构**；
- **重写 today’s adapter / parameterization / fee model / risk control**；
- **不要复用它的私有配置方式。**

## 4. public live probe：今天的 Deribit 曲线依然有 carry，但 raw quote gap 已经不能直接拿旧阈值套
我用 Deribit 公共 API 看了 2026-04-12 21:00 UTC 附近的 futures 曲线快照。

### 4.1 当时的关键 mid 数据
- `BTC-PERPETUAL`：`71362.25`
- `BTC-29MAY26`：`71451.25`
- `BTC-26JUN26`：`71571.25`
- `BTC-25SEP26`：`72081.25`
- `BTC-25DEC26`：`72758.75`

对应到 perp 的 basis：
- `26JUN26`：`+209.0`（`+0.293%`，约 `1.44% annualized`）
- `25SEP26`：`+719.0`（`+1.008%`，约 `2.22% annualized`）
- `25DEC26`：`+1396.5`（`+1.957%`，约 `2.79% annualized`）

### 4.2 这组数说明什么
这组快照很直白：

> **今天 perp-vs-quarter 的 raw price gap，大头本来就来自正常 contango，而不是异常错价。**

例如同一时刻：
- `BTC-25SEP26 best_ask - BTC-PERPETUAL best_ask = 720.5`

如果你直接拿旧脚本那种固定 gap 数字去套，极容易把“正常期限结构”误当成 alpha。

所以当前 desk 真正该继承的，不是“固定价差阈值”，而是：

> **对 carry 先做公平价值基线，再看 residual gap 有没有短时异常扩张。**

## 5. 抽成今天可落地的版本，alpha 本体应该怎么定义

### 5.1 更干净的 today 口径
把 raw gap 改写成 **fair-value-adjusted residual gap**：

- `fair_gap(τ) = perp_mid × carry_curve(τ) × τ / 365`
- `residual_ask = (future_ask - perp_ask) - fair_gap(τ)`
- `residual_bid = (future_bid - perp_bid) - fair_gap(τ)`

人话版：
- 先承认远月比 perp 贵，本来就正常；
- 真正可做的，不是“远月为什么贵”，而是**它比“本该贵的水平”又额外贵了一截，或额外便宜了一截**；
- 这额外多出来的一截，才是短周期 relative-value alpha。

### 5.2 对应的交易方向
若 `residual_ask` 明显过高：
- 做 `sell future / buy perp`
- 赌 residual 收敛

若 `residual_bid` 明显过低：
- 做 `buy future / sell perp`
- 赌 residual 收敛

### 5.3 这条线为什么适合 `1m / 3m / 5m / 15m`
因为它本来就是：
- quote-driven
- event-driven
- top-of-book driven

所以最自然的实验频率其实是：
- `1m`：最小 baseline
- `3m`：降噪版本
- `5m`：更接近 desk 当前主频
- `15m`：用于看 carry residual 是否只是秒级噪声，还是能延续成更慢的 close-out pocket

## 6. 这条策略壳，可以怎么直接映射成完整实验

### 6.1 Entry
只在以下同时满足时进场：
1. 选定一组 pair，例如 `perp-vs-near quarter`；
2. 先估一条 bucket-level `fair_gap(τ)`；
3. `residual` 超过 rolling `p95 / p97.5` 或 `z >= 2.0 / 2.5 / 3.0`；
4. 顶层可成交量够；
5. 两腿净成本后仍有剩余 edge；
6. 当前 funding / liquidation / news 没把 curve 直接打进 regime break。

### 6.2 Exit
任一满足就平：
1. `residual` 回到 `0 ~ 0.5σ`；
2. 到达固定 time-stop（先试 `5m / 15m / 30m / 60m`）；
3. 盘口一侧 size 消失；
4. 净敞口修复失败；
5. basis regime 突变，原先的 fair gap 估计明显失效。

### 6.3 Sizing
沿用 repo 的思想，不沿用它的旧数值：
- `size_per_trade = min(future_top_size, perp_top_size, venue risk cap)`
- position ladder：仓位越大，下一档 entry threshold 越苛刻
- pair-level notional cap：perp-vs-quarter 单独设上限
- tenor bucket cap：近月 / 远月分别记账，别混在一起

### 6.4 Risk
主要风险不是方向，而是：
- **单腿先成交、另一腿补不齐**
- **残差其实没回归，而是 carry regime 变了**
- **盘口 stale / quote flicker**
- **持仓期间 funding / margin / fee 把 edge 吃掉**
- **一条 pair 看着中性，但多条 pair 叠加后在 curve 上形成净暴露**

### 6.5 Cost
至少显式建三档：
- maker+taker 乐观档
- taker+taker 保守档
- “future maker fill 率不足”的中性档

否则很容易把 paper alpha 误读成可成交 alpha。

## 7. 为什么我认为这轮它值得进研究池
这轮它值得，不是因为“repo 很新”，而是因为它把我们当前最缺的一类素材补得很实：

> **短周期、可事件驱动、可落到执行细节的 same-venue relative-value raw alpha。**

对当前 desk，它的价值有三点：

1. **它是 raw alpha，不是 overlay。**
   方向很明确：做 residual gap 收敛，而不是做解释性分析。

2. **它离实盘组件很近。**
   repo 里已经有 order edit / cancel / hedge / rebalance 这些我们真正要拆的东西。

3. **它能扩展成一整个 family。**
   先做 `perp-vs-quarter`，再扩到：
   - `perp-vs-next-quarter`
   - `front-vs-back`
   - `same-underlier multi-pair netting`

## 8. 下一步怎么测
这轮必须落到最小实验，不空谈。

### 8.1 第一版先别碰全事件级回放，先做 `1m / 3m / 5m / 15m` baseline
输入：
- Deribit public futures best bid / ask snapshot
- instrument expiration timestamp
- perp mid / future mid
- funding（可选，先不做也行）

构造：
1. 选 `BTC-PERPETUAL` 对 `BTC-26JUN26 / BTC-25SEP26 / BTC-25DEC26`；
2. 对每个 tenor 估 `fair_gap(τ)`；
3. 计算 `residual_bid / residual_ask / residual_mid`；
4. 在 `1m / 3m / 5m / 15m` 上分别做 rolling z-score / percentile；
5. 比较 residual 是否存在可重复的收敛半衰期。

### 8.2 第一批参数先只扫这几个
- entry：`z >= 2.0 / 2.5 / 3.0`
- exit：`z <= 0.5 / 0`
- time stop：`5 / 15 / 30 / 60 min`
- cost：`2 / 5 / 10 bps` 三档
- bar freq：`1m / 3m / 5m / 15m`

### 8.3 第一轮只回答 4 个问题
1. residual gap 在哪一个 tenor 最容易回归？
2. `1m` 的信号是不是只是噪声，还是比 `5m` 更有 edge？
3. maker-first / taker-hedge 的 fill 假设对结果有多敏感？
4. 单 pair 有 edge 后，多 pair 净额化能不能明显降 inventory risk？

### 8.4 kill rule
如果第一轮 baseline 显示：
- residual 没有稳定回归；
- 过成本后 edge 基本消失；
- maker-first 假设一放松就全没了；

那这条线就降级，不继续占 bot7 的主 intake。

## 9. 来源与可复现性
### 9.1 Repo / readable URL
- **Repo：** `https://github.com/Hudie/crypto_algo_trading`
- **Readable URL：** `https://github.com/Hudie/crypto_algo_trading`
- **核心源码：**
  - `https://raw.githubusercontent.com/Hudie/crypto_algo_trading/master/strategy/backup_deribit_perpetual_future_arb.py`
  - `https://raw.githubusercontent.com/Hudie/crypto_algo_trading/master/strategy/deribit_cross_future.py`
  - `https://raw.githubusercontent.com/Hudie/crypto_algo_trading/master/strategy/deribit_cross_remote_future.py`
  - `https://raw.githubusercontent.com/Hudie/crypto_algo_trading/master/README.md`

### 9.2 live probe 数据源
- Deribit instruments：`https://www.deribit.com/api/v2/public/get_instruments?currency=BTC&kind=future&expired=false`
- Deribit book summary：`https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=future`
- Deribit order book：`https://www.deribit.com/api/v2/public/get_order_book?instrument_name=BTC-PERPETUAL&depth=1`

### 9.3 复现口径
- **公开性：** 是，公共 API
- **更新频率：** 近实时
- **最小可复现实验口径：** 只拿 best bid/ask + expiry timestamp，就能先做 residual gap 的 bar-level baseline；要往更真实推进，再补 event-driven order edit / fill model。