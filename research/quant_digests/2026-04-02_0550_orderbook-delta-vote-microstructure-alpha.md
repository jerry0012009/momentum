# L2 imbalance × aggressive trade delta × EMA vote：一个可快速前向复现的 1m/3m microstructure continuation 候选

- 主题类型：raw alpha
- 基础 alpha：`order book imbalance × aggressor trade delta × short EMA trend` 同向共振后的短周期延续
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（源码已给 entry / flip / sizing 骨架，但缺真实止损与费用回测）

## 先回答一句：这篇东西的 base alpha 是什么？
不是“盘口大就涨”这么粗。**真正的 base alpha** 是：当 `L2 挂单压力`、`最近一段 aggressor 主动成交方向`、`短 EMA 趋势方向` 三者同向时，短周期价格更容易继续沿该方向走 1~几根 bar；`volume_ratio` 在这份 repo 里更像加分项，不是 alpha 本体。

## 为什么这轮值得写它
这轮前两篇 digest 都不是 raw alpha，按当前 intake 规则应优先补 raw alpha。虽然 desk 最近已经连续 intake 过 OBI / OFI 家族，但这份 2026 新 repo 仍然有一个值得单独入池的增量点：**它不是只看 order-book imbalance，而是把“挂单压力”和“主动成交 delta”拆成两条独立腿，再用一个 3-of-4 vote state machine 直接落成可 paper/live 跑的单币方向壳子。**

这让它比“纯 OBI 方向 admission”更接近可复现的完整原型，也比很多只讲 microstructure 解释、不讲执行骨架的材料更适合 desk 现在的 fast alpha intake。

---

## 主要来源

### 1) 直接策略来源（主）
- **Owner / Year**: vortex-systems-tech, 2026
- **Title**: `Crypto-Strategy-Order-Book-Delta-Volume`
- **Type**: GitHub repo（MIT）
- **Created / Updated**: 2026-03-27 / 2026-03-27
- **Readable URL**: https://github.com/vortex-systems-tech/Crypto-Strategy-Order-Book-Delta-Volume
- **Repo URL**: https://github.com/vortex-systems-tech/Crypto-Strategy-Order-Book-Delta-Volume
- **Key files**:
  - `README.md`
  - `binance_orderbook_delta_strategy.py`

### 2) 机制地基（辅）
- **Authors / Year**: Rama Cont, Arseniy Kukanov, Sasha Stoikov, 2014
- **Title**: *The Price Impact of Order Book Events*
- **Venue**: *Journal of Financial Econometrics*
- **DOI**: `10.1093/jjfinec/nbt003`
- **Readable URL**: https://doi.org/10.1093/jjfinec/nbt003

> 这篇经典文献不是 crypto 专用，但足够说明：order-book 事件流本身就能解释短期价格冲击。当前 repo 的可取之处，是把这个逻辑压缩成了 Binance Futures 可直接跑的低门槛实现。

### 3) 数据接口口径（复现实验用）
- Binance USDⓈ-M Futures public depth / aggTrades / klines
- Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api

---

## 我从源码里拆出来的真实策略，不是 README 口号版

这份 repo 的核心不是 ML，也不是复杂优化，而是一个非常朴素的投票壳：

### 输入特征
1. **Order-book imbalance**
   - 取 `top 20` depth
   - 计算：
   - `imbalance = (bid_notional - ask_notional) / (bid_notional + ask_notional)`
   - 阈值：`|imbalance| >= 0.12`

2. **Aggressor trade delta**
   - 取最近 `500` 笔 `futures_aggregate_trades`
   - 用 `m` 字段区分主动买 / 主动卖
   - 计算：
   - `delta = (buy_volume - sell_volume) / (buy_volume + sell_volume)`
   - 阈值：`|delta| >= 0.15`

3. **短趋势方向**
   - `EMA(50)`
   - `close > EMA` 记多头票；`close < EMA` 记空头票

4. **量能加分项**
   - `volume_ratio = last_volume / rolling_mean(volume, 20)`
   - 只有当 `volume_ratio >= 1.2` 时，才给当前 `delta` 同向一票
   - 这意味着它**不是硬 volume gate**，只是第四票

### 入场规则
- `long_score >= 3` 且 `long_score > short_score` → `BUY`
- `short_score >= 3` 且 `short_score > long_score` → `SELL`

### 仓位与风险骨架
- 风险预算：`balance × 1%`
- 估算 stop distance：`max(1.5 × ATR(14), 0.3% × price)`
- 名义杠杆：`5x`
- `qty = (risk_usdt × leverage) / stop_distance`

### 出场 / 翻仓
- 没有显式止损单
- 当前实现主要靠**反向信号触发 flip**
- 也就是说：
  - 空仓 → 按当前票数进场
  - 持多仓且出现强空头票 → 平多并翻空
  - 持空仓且出现强多头票 → 平空并翻多

### 最关键的诚实结论
这份 repo 已经是**可以跑的原型**，但还不是 desk 可直接上实盘的最终版，因为：
1. `ATR` 只参与 sizing，没有被落实为真实 stop / time stop
2. 没有费用 / 滑点回测
3. 使用 REST polling，不是事件驱动撮合级实现

所以它是很好的 **raw alpha intake + 最小前向实验骨架**，但还不该被误读成“现成成熟策略”。

---

## 对 short-cycle desk 最有价值的，不是整份脚本，而是这个“二腿确认”

如果只看 order-book imbalance，很容易掉进两个坑：
- 挂单是会撤的，容易被假深度骗
- 单看 OBI，经常分不清“真推动”还是“被动挂单挤压”

这份 repo 的真正增量在于：**再加一条 aggressor delta 腿。**

可以把它翻成人话：
- `imbalance` 像“墙往哪边堆”
- `trade delta` 像“真正冲过去的人往哪边打”
- `EMA` 像“最近这段路原本朝哪边走”

三者同向，才值得下注 continuation。

这比“只看盘口”更像真实推进；也比“只看成交 delta”更少被单根 burst 噪音误导。

---

## 公开数据最小快检（我直接对 Binance Futures 公共接口做了 90 秒 live sampling）

采样方式：
- 交易对：`BTCUSDT / ETHUSDT / SOLUSDT`
- 频率：每 `10s` 取一次 snapshot
- 总样本：每个币 `9` 个 snapshot
- 使用的就是 repo 同口径：`depth(20)`、最近 `500` 笔 `aggTrades`、`1m klines`

### 结果摘要
- **BTCUSDT**：`0 / 9` 次触发方向信号
- **ETHUSDT**：`1 / 9` 次触发 `SELL`
- **SOLUSDT**：`6 / 9` 次触发 `BUY`

### 中位数特征强度
- **BTCUSDT**：
  - `median |imbalance| = 0.422`
  - `median |delta| = 0.552`
  - `median volume_ratio = 0.878`
- **ETHUSDT**：
  - `median |imbalance| = 0.767`
  - `median |delta| = 0.728`
  - `median volume_ratio = 0.159`
- **SOLUSDT**：
  - `median |imbalance| = 0.125`
  - `median |delta| = 0.256`
  - `median volume_ratio = 0.403`

### 这组快检说明什么
1. **信号不是全市场乱闪。** 在 27 个 symbol-snapshots 里，真正形成方向 admission 的只有 `7` 个。
2. **volume_ratio 在当前实现里确实只是加分，不是主门槛。** 因为 BTC / ETH / SOL 的 volume_ratio 中位数都低于 `1.2`，但 SOL 仍然出现了 `6/9` 次 `BUY`，说明主要靠的是 `imbalance + delta + EMA` 三腿共振。
3. **这个壳子更像 alt/单边推进状态捕捉器，不像 BTC 全天候方向机。** 这很符合 short-cycle desk 的直觉：BTC 更容易被噪音和对敲抵消，SOL 这类 beta 币更常出现“一边挂单 + 一边主动打单 + 顺趋势”的短窗共振。

> 重要：这只是 live sanity check，不是收益回测。它证明的是“信号会真实触发，且不是完全乱闪”；还没证明净收益为正。

---

## 它更适合我们 desk 的落地版本

### A. 主版本：1m / 3m 单币 continuation raw alpha
这是我认为最值得先测的版本。

**建议 desk 版规则：**
- 交易 universe：`BTC / ETH / SOL / BNB / DOGE` 这类高流动 perp
- bar：`1m` 原生；再聚合成 `3m`
- 信号：
  - `imbalance(top20)` 取 bar close 前最后一笔 snapshot
  - `delta` 用该 bar 内全部 aggTrades 归总
  - `EMA(50)` 方向
- 入场：
  - 多头：`imbalance >= q80`、`delta >= q80`、`close > EMA`
  - 空头：对称
- 出场：
  - `opposite vote`
  - 或 `2 × ATR(14)` stop
  - 或 `N=3~6` bars timeout
- 成本：
  - 先按 taker round-trip `10 bps` 起算
  - stress test 到 `15~20 bps`

### B. 次版本：给 5m / 15m breakout / momentum 当 admission gate
如果 raw alpha 单跑不够稳定，这个二腿确认也很适合作为 shared gate：
- 只有当 lower-TF `imbalance + delta` 与 5m/15m 主方向一致时，才允许追价
- 反之，主信号成立但 microstructure 不确认，则 veto 或降杠杆

但这篇 digest 的主结论仍然是：**它先值得作为独立 raw alpha 测，而不是先降级成 filter。**

---

## 为什么它没有被我归到“可直接完整落地策略”最高档
因为目前还差三件关键东西：

1. **真实风险闭环还没写完**
   - sizing 用了 stop distance
   - 但执行层没有挂真实 stop / trailing stop / timeout stop

2. **成本太重要，而源码没回测**
   - 这是一个可能会频繁 flip 的 taker 型策略
   - 如果 round-trip 成本 + 滑点吃掉 10~20bps，很容易把 1m alpha 磨平

3. **历史 order-book 数据获取不是“点一下就有”**
   - `klines`、`aggTrades` 历史好拿
   - 真正的 `depth imbalance` 历史需要自己录，或者用外部档案服务

所以它是：
- **raw alpha 候选：是**
- **可独立复现：是**（因为输入都是公开接口，只是需要自己开始录 depth）
- **立刻无脑上实盘：否**

---

## 最小可复现实验口径

### 数据源
- Binance USDⓈ-M Futures public API / WebSocket

### 公开性
- 公开可得，无需付费、无需私钥即可取 market data

### 更新频率
- `depth`：近实时
- `aggTrades`：近实时
- `klines`：`1m` 可直接拿；`3m/5m/15m` 可聚合

### 最小实验
**最诚实、最快的实验不是先做长历史回测，而是：**
1. 立刻开一个 `depth + aggTrades + klines` recorder
2. 连续录 `3~7` 天 BTC/ETH/SOL/BNB/DOGE
3. 用 recorder 生成 bar-close snapshot 特征
4. 跑：
   - `1m` 直接版本
   - `3m` 聚合版本
   - `1m signal → 3m hold` 混合版本
5. 统一按 taker `10/15/20 bps` 三档做 stress

如果想更快做“今天就能开始”的前向实验：
- 不等历史，先 paper-run `48h`
- 记录每次触发后的 `+1 / +3 / +5` bar markout
- 看 `SOL/BNB/DOGE` 是否明显优于 `BTC`

---

## 我建议 desk 先测的 4 个假设

### 假设 1：`delta` 比 `volume_ratio` 更重要
repo 里 volume 只是第四票。我怀疑真正有信息量的是：
- `OBI + delta + EMA`
而不是：
- `OBI + delta + volume`

**先测：** 去掉 volume 票，比较 hit rate / markout / turnover。

### 假设 2：alts 比 BTC 更适合这条 alpha
本次 90 秒 live sampling 已经给出一个很直观的线索：
- BTC 触发稀少
- SOL 明显更容易形成共振 admission

**先测：** `BTC, ETH, SOL, BNB, DOGE` 分币比较 forward markout。

### 假设 3：`3m` 可能优于 `1m`
1m 容易被撮合噪音和 taker 费用磨掉；3m 可能让 `delta` 与 `imbalance` 更稳定。

**先测：**
- `1m enter / 1m exit`
- `1m enter / 3m hold`
- `3m aggregated signal`

### 假设 4：它更像 continuation admission，不像全天候 alpha
也就是说，真正该测的不是“全时段都开”，而是：
- 只在 realized vol 上升段
- 只在 funding 中性或顺向拥挤不极端时
- 只在 session overlap（欧美交接）内启用

---

## 风险与失败模式

1. **假挂单 / 撤单噪音**
   - imbalance 很容易被 spoofing 污染
   - 所以必须保留 delta 这条腿，不要退化成纯 OBI

2. **REST polling 低频错位**
   - repo 现在每 `10s` 拉一次
   - 真正研究时应改成 WebSocket 事件聚合到 bar close

3. **过度 flip**
   - opposite signal flip 很容易带来高 turnover
   - 所以必须补 `min hold` / `cooldown` / `timeout`

4. **大币种拥挤、alpha 被费用吃掉**
   - BTC 可能最早看上去“最干净”，但其实最难赚
   - 反而 beta alt 可能更有短窗惯性

---

## 一句话结论
这份 2026 新 repo 最值得 intake 的，不是“订单簿 + 成交量”这种泛泛概念，而是一个**能用公开 Binance Futures 数据快速前向复现的 microstructure continuation 原型**：

> **`L2 imbalance × aggressive trade delta × EMA trend` 三腿同向时做短周期延续；volume 只当加分，不当本体。**

对当前 desk，我认为它应被放进 **raw alpha 素材池**，优先做 `1m/3m` 前向录数与 markout 实验，而不是先降级成 filter。

---

## 下一步怎么测（直接执行版）

### 最小实验 v1（本周就能做）
1. 录 Binance Futures `depth20 + aggTrades + 1m klines`
2. universe 先做：`BTC / ETH / SOL / BNB / DOGE`
3. 每个 bar 生成：
   - `imbalance_t`
   - `delta_t`
   - `ema_dir_t`
   - `volume_ratio_t`
4. 跑 3 个版本：
   - **V1**: `OBI + delta + EMA` 三票制
   - **V2**: `OBI + delta + EMA + volume bonus` 四票制（repo 原味）
   - **V3**: `OBI + delta` 做 admission，`EMA` 只做 veto
5. 统一 exits：
   - opposite vote
   - `2 × ATR` hard stop
   - `3 / 6` bars timeout
6. 成本三档：`10 / 15 / 20 bps` round-trip
7. 先看：
   - `+1 / +3 / +5` bar markout
   - turnover
   - signal density
   - per-symbol PnL concentration

### 我最想先看的判断标准
- 如果 **SOL/BNB/DOGE 在 3m 上明显优于 BTC/ETH**，这条就值得继续
- 如果 **去掉 volume 票后结果更稳**，说明 alpha 本体真的是 `pressure agreement`，不是放量 breakout
- 如果 **一上 15bps 就全灭**，那它更适合当 lower-TF confirmation，而不是独立主策略

---

## 文件信息
- 文件路径：`research/quant_digests/2026-04-02_0550_orderbook-delta-vote-microstructure-alpha.md`
- 站点相对 URL：`/reading/quant_digests/2026-04-02_0550_orderbook-delta-vote-microstructure-alpha.html`
