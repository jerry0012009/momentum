# 别把这份今天仍在更新的 adaptive-grid repo 只读成 infra：对 short-cycle desk，更该先测的是「extreme stretch × CVD/OFI divergence × no-liq-surge」这条 countertrend raw alpha

- 时间：2026-04-04 00:20 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `docs/07_GRID_POLICY_LIBRARY.md` + `docs/06_TOXICITY_SPEC.md` + `docs/STATE.md`）
- 主题类型：raw alpha
- 基础 alpha：**短窗极端伸展后的 exhaustion fade**；`CVD/OFI divergence` 不是 alpha 本体，只是 admission / confirmation，`liq_surge` 与 `toxicity` 是 veto / risk layer
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但 **repo 当前主要给的是 policy spec，不是已验证回测**；我们需要自己补最小实验与执行口径
- 主题标签：raw-alpha/mean-reversion/single-asset/microstructure/exhaustion-fade/cvd/ofi/divergence/liquidation-veto/toxicity/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo policy-spec audit（主）+ desk 当前 backlog/学习进展对照（辅）

## 1) 先回答：这篇东西的 base alpha 是什么？
一句话先说清楚：

> **base alpha 不是 divergence。base alpha 是“短窗极端拉伸后，价格有回摆倾向”的 exhaustion fade。**

这里要特别和当前 backlog 区分开：
- `FACTOR_BACKLOG.md` 里，**Price-volume divergence** 已经被记成 `REVIEWED + PARKED`，说明“把 divergence 单独当主角”这条路证据偏弱；
- 这份 repo 里更有价值的点，恰恰是 **没把 divergence 伪装成 alpha 本体**，而是把它降级成 **极端 stretch fade 的 admission 条件**。

所以这轮 intake 的正确读法是：
- **raw alpha 本体**：extreme stretch / exhaustion fade
- **confirmation**：CVD / OFI divergence
- **veto**：liquidation surge、toxicity high
- **risk shell**：tight spacing / small size / fast timeout

这就符合这轮优先级：**不是纯 filter，而是一条可以独立落地的 raw alpha 壳。**

---

## 2) 为什么这轮值得看它
这轮我没有再选另一个 breakout / carry / pairs，是因为当前池子里这些已经很多；反而 **“更快、更脏、但能直接做最小实验的 countertrend exhaustion shell”** 还不够系统。

更关键的是，这份今天还在更新的 repo（`bnzr-team/grinder`，`updated_at=2026-04-04T00:08:42Z`，`pushed_at=2026-04-04T00:18:20Z`）给了一个很符合我们当前阶段的重构方式：

1. **不要再围绕 divergence 单独内循环**；
2. **先承认 alpha 本体是 overshoot mean reversion**；
3. 再把 divergence、liq veto、toxicity veto 挂进去，看看它们到底是在提升命中率，还是只是在减少交易数。

这和当前学习进展是对齐的：
- `MAINLINE1_STRATEGY_FACTOR_MAP.md` 里，divergence 本来就更像结构/确认候选；
- `FACTOR_BACKLOG.md` 也已经提醒：**单独 price-volume divergence 证据弱**；
- 所以这轮真正值得 intake 的，不是“又一个 divergence 指标”，而是 **divergence 被放进 raw alpha 壳里以后，是否终于变得值得测。**

---

## 3) 来源与可追溯信息
### A. 主来源（repo）
- **Author / Org：** `bnzr-team`
- **Year：** 2026
- **Title：** `grinder`
- **Repo description：** `GRINDER - Adaptive Grid Trading System for Crypto Perpetuals`
- **Readable URL：** <https://github.com/bnzr-team/grinder>
- **Repo URL：** <https://github.com/bnzr-team/grinder>
- **Created at：** `2026-01-30T19:23:27Z`
- **Updated at：** `2026-04-04T00:08:42Z`
- **Pushed at：** `2026-04-04T00:18:20Z`

### B. 本轮实际使用的关键文件
- `README.md`
- `docs/07_GRID_POLICY_LIBRARY.md`
- `docs/06_TOXICITY_SPEC.md`
- `docs/STATE.md`

### C. 需要先说清的一点
repo 的 README 很诚实：
- 这个项目的主干是 **adaptive grid infra**；
- `STATE.md` 也明确写了很多 smart-grid / policy 层内容仍属于 **spec exists, not implemented**；
- 所以这轮不能把它写成“现成已验证策略”，而应该写成：
  > **一个很新的 repo 里，最适合我们 desk 先拆出来做最小实验的 raw alpha branch。**

---

## 4) repo 里真正值得抄的，不是整包 grid，而是这一条「Mean Reversion Sniper」
`docs/07_GRID_POLICY_LIBRARY.md` 里最值得拿出来单独讨论的，不是 funding harvester，也不是整个 range grid，而是：

### 4.1 Mean Reversion Sniper Policy
repo 给的规则非常直接：
- 极端阈值：`extreme_threshold = 3.0`
- 价格上冲过热：`momentum_5m > 3`
- 价格下杀过头：`momentum_5m < -3`
- 需要有 **divergence**：
  - 若价格强上冲，但 `cvd_change_1m < 0`，算 exhaustion
  - 若价格强下杀，但 `cvd_change_1m > 0`，算 exhaustion
  - 或者用 `ofi_zscore` 做同样的反向确认
- 若 `liq_surge = True`，**直接暂停，不做逆势接刀**
- grid 参数示例：`8 bps` spacing、`3` levels、`60 USD` size per level

翻成人话：

> **先找“冲得太过”的短窗价格动作，再要求 order-flow 没有继续配合，最后避开正在发生的强平瀑布。**

这其实已经是一条很完整的 raw alpha 骨架了。

### 4.2 它为什么比 repo 里的其他分支更适合我们现在
因为它天然适合 `1m / 3m / 5m`：
- 不是慢频 daily 因子；
- 不是必须依赖难拿的链上或私有数据；
- 可以直接用 **公开交易所 kline + aggTrades + bookTicker/depth** 先做最小实验；
- 若 liquidation 数据暂时拿不全，也可以先把 `liq_surge` 作为二阶段 veto，而不是卡死在第一步。

---

## 5) 它到底是不是 raw alpha？
我的判断：**是。**

但要把层次拆干净：

### 5.1 alpha 本体
- **本体：** short-horizon exhaustion fade / overshoot mean reversion
- 也就是：价格短时间走得过快、过远，下一段出现回摆

### 5.2 不是 alpha 本体的部分
- **CVD / OFI divergence**：是 admission / confirmation
- **liq_surge**：是 veto
- **toxicity_score**：是 risk overlay

这点非常重要。因为如果把 `divergence` 自己写成主角，就又会回到 backlog 已经提醒过的老问题：

> **divergence 单独看很容易变成“看起来聪明、实际证据弱”的弱过滤器。**

而放进这条壳里之后，逻辑变成：

> **极端 stretch 才是开仓前提；divergence 只是判断这次 stretch 到底是“真 acceleration”还是“已经出现 flow 衰竭”。**

这就合理得多。

---

## 6) 用 desk 语言把策略拆成完整壳
如果把 repo 里的 grid policy 翻译成我们更容易回测的 directional shell，我会先这么落地：

### 6.1 Entry
以 `1m/3m` 为执行层、`5m` 为主信号层：

**做空条件**
1. `zscore(ret_5m)` 或 vol-normalized `momentum_5m` > `+3`
2. 同时满足其一：
   - `cvd_change_1m < 0`
   - `ofi_zscore < -1`
3. `liq_surge = False`
4. `toxicity_score < 2.0`

**做多条件**
1. `zscore(ret_5m)` 或 vol-normalized `momentum_5m` < `-3`
2. 同时满足其一：
   - `cvd_change_1m > 0`
   - `ofi_zscore > +1`
3. `liq_surge = False`
4. `toxicity_score < 2.0`

### 6.2 Exit
我不建议直接照抄 grid，而建议先做最简单、最诚实的 exit：
- **主退出：** 回到短窗均值（VWAP / EMA20 / 5m midline）
- **止损：** 再走 `0.8~1.2 x ATR_1m` 或再扩张 `1.0~1.5σ`
- **时间止损：** `3~8` 根 `1m` bar 内不回摆就平
- **事件止损：** 如果中途 `liq_surge` 或 `toxicity_score >= 2.0`，直接 flatten

### 6.3 Sizing
这类 countertrend 单最怕“看对方向但先被继续 squeeze”。所以 sizing 必须保守：
- 用 `target risk per trade` 而不是固定名义本金
- `size ∝ 1 / realized_vol_1m`
- 若 `spread_bps` 或 `toxicity_score` 升高，自动减半
- 单笔风险建议先从组合权益的 `10~20 bps` 开始

### 6.4 Cost
这条 alpha 很容易死在成本上，所以要一开始就做成本梯度：
- maker/taker 两套
- round-trip 先测：`2 / 4 / 6 / 8 bps`
- 只要 gross edge 扛不住 `4~6 bps`，就不应该进入高优先排期

---

## 7) 与当前 `1m / 3m / 5m / 15m` 的关系
这条线我会明确归类成：

> **更偏 `1m / 3m` 的高强度 raw alpha，`5m` 可做慢一点的信号壳，`15m` 更适合作为大环境 veto。**

具体说：
- `1m`：最适合做 CVD / OFI / spread / toxicity 细粒度确认
- `3m`：适合做噪音稍低的执行与回测基线
- `5m`：适合定义 extreme stretch 本体
- `15m`：不建议把它硬装成主信号；更适合做 `trend too strong / vol too high / no-fade regime` 的背景门控

所以这条 alpha 虽然能映射到 `5m/15m` 体系，但它最自然的 home 其实是 **`1m/3m` fast sleeve**。

---

## 8) 数据源、公开性、更新频率、最小复现实验口径
### 8.1 必需数据
1. **Klines / trades**
   - 公开性：公开可得
   - 来源：Binance/Bybit/OKX 公共 API
   - 频率：秒级 / 分钟级
   - 用途：构造 `momentum_5m`、vol-normalized stretch、ATR

2. **AggTrades / taker flow**
   - 公开性：公开可得
   - 来源：Binance Futures `aggTrades` / trade stream
   - 频率：实时
   - 用途：构造 `CVD change 1m`

3. **BookTicker / Depth**
   - 公开性：公开可得
   - 来源：Binance/Bybit 公共盘口接口
   - 频率：实时
   - 用途：构造 `OFI z-score`、spread、depth imbalance、toxicity proxy

### 8.2 二阶段可选数据
4. **Liquidation / force-order stream**
   - 公开性：公开可得（但历史回补通常比 klines 麻烦）
   - 来源：交易所公开 liquidation stream / 公共 liquidation feed
   - 频率：事件驱动
   - 用途：把 repo 里的 `liq_surge veto` 真正落地

### 8.3 最小可复现实验口径
第一版不必等所有东西齐全：
- 先用 `BTCUSDT`, `ETHUSDT`, `SOLUSDT`
- 先做 `1m/3m/5m`
- 先跑 **extreme stretch + divergence**
- 再加 `liq_surge veto`
- 最后再加 `toxicity gate`

也就是说，第一步先验证：
> **这条 raw alpha 本体在没有 fancy veto 时，是否已经有一点诚实的 gross edge。**

---

## 9) 下一步怎么测（最重要）
### 实验 A：先测 raw alpha 本体，不加 liquidation veto
**目标**：确认这不是“又一个 divergence 幻觉”。

- 标的：`BTCUSDT`, `ETHUSDT`, `SOLUSDT`
- 周期：`1m`, `3m`, `5m`
- 信号：
  - `stretch_z > 3`
  - `CVD` 或 `OFI` 反向 divergence
- 入场：信号 bar 结束后 `next open`
- 出场：
  - 回到 `VWAP/EMA20`
  - 或 `max_hold = 5 bars`
  - 或 `ATR stop`
- 成本：`0 / 2 / 4 / 6 / 8 bps`

**先看 5 个指标：**
1. `avg bps/trade`
2. `hit rate`
3. `MAE / MFE`
4. `time-to-mean`
5. `post-cost pnl`

### 实验 B：加 liquidation veto
**目标**：确认 repo 的 `liq_surge=False` 到底是在真提升，还是只是在减少交易数。

- 新增条件：出现 liquidation surge 的窗口全部 skip
- 对比 A/B：
  - trade count 下降多少
  - `avg bps/trade` 提升多少
  - `left-tail MAE` 是否明显收敛

### 实验 C：加 toxicity gate
**目标**：确认 adverse-selection 风险是否主要发生在 spread / impact 太坏的时候。

- 先做最简单 proxy：`spread_z + OFI_shock + short-horizon impact`
- `toxicity_score >= 2.0` 时不做
- 看它是否主要改善：
  - 极端 continuation 误伤
  - 滑点后净收益
  - worst-decile trade

### 实验 D：把 `1m/3m` 胜出的版本，搬到 `5m/15m` 看可迁移性
如果这条线在 `1m` 里有 edge，但 `5m` 很快变钝，就说明：
- 它更像真正的 fast alpha；
- 不适合硬塞进 `15m` 主引擎；
- 应该作为一个独立 fast sleeve 存在，而不是被误当成通用 MR 因子。

---

## 10) 我对这条线的 desk 判断
如果一句话总结：

> **这不是“divergence 因子翻新”，而是“extreme stretch fade”这条 raw alpha，被一个新 repo 用更合理的 admission / veto 结构重新摆正了。**

我会把它放进研究池，但带着两个很明确的前提：

1. **不要把 repo 的 docs-spec 当回测证明。**
2. **不要把 divergence 再次误写成 alpha 本体。**

如果实验 A 连本体都站不住，就别继续给它堆 liq / toxicity / grid 细节；
如果实验 A 站得住，而 B/C 明显改善左尾和 post-cost，那这条线就值得进入下一轮复现排期。

---

## 11) 来源链接
1. **bnzr-team (2026), _grinder_**, GitHub repository  
   - Repo URL: <https://github.com/bnzr-team/grinder>
   - Readable URL: <https://github.com/bnzr-team/grinder>
   - README: <https://raw.githubusercontent.com/bnzr-team/grinder/main/README.md>
2. **`docs/07_GRID_POLICY_LIBRARY.md`**  
   - Raw URL: <https://raw.githubusercontent.com/bnzr-team/grinder/main/docs/07_GRID_POLICY_LIBRARY.md>
3. **`docs/06_TOXICITY_SPEC.md`**  
   - Raw URL: <https://raw.githubusercontent.com/bnzr-team/grinder/main/docs/06_TOXICITY_SPEC.md>
4. **`docs/STATE.md`**  
   - Raw URL: <https://raw.githubusercontent.com/bnzr-team/grinder/main/docs/STATE.md>
5. **Binance public market data docs**（用于最小复现实验）
   - Klines: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
   - Aggregated Trades: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List>
   - Book Ticker: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Order-Book-Ticker>
   - Force Orders / liquidation stream: <https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams>

## 12) 最短版结论
这轮最值得 intake 的，不是 `grinder` 整包 adaptive-grid infra，而是其中一条目前还没在池子里被好好拆开的 raw alpha：

> **extreme short-horizon stretch × order-flow divergence confirmation × liquidation/toxicity veto 的 exhaustion fade。**

它的关键优点是：
- **base alpha 清楚**，不是纯 filter；
- **公开数据就能做最小实验**；
- **天然适合 `1m/3m` fast sleeve**，再决定是否向 `5m` 迁移；
- 同时又和当前 backlog 的教训一致：**divergence 只能当 admission，不能再冒充 alpha 本体。**
