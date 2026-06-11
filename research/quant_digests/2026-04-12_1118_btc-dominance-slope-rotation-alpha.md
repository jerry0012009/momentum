# 别把这份 2026 kuant repo 里的 BTC dominance 轮动只读成 alt-season 叙事：对 short-cycle desk，更该先测的是「BTC 相对 alt basket dominance slope × weakest/strongest alt switch」这条 raw alpha，但它更像低成本慢换仓书，不是逐根 taker 信号
- 时间：2026-04-12 11:18 UTC
- 类型：2026 GitHub repo source audit（`strategies/crypto_advanced.py::BTCDominanceStrategy`）+ Binance USDⓈ-M `15m` public portability probe
- 主题类型：raw alpha
- 基础 alpha：**当 `BTC` 相对等权 alt 篮子的滚动超额收益继续走强时，`BTC` 往往会继续跑赢当下最弱的那几只 alt；反过来，当这条 dominance slope 继续走弱时，最强 alt 往往会继续跑赢 `BTC`。更可交易的壳不是泛泛的“alt season / BTC season”口号，而是 `BTC vs alt basket` 的相对强弱状态切换，再配 `strongest/weakest alt switch` 做相对价值书。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/cross-sectional/rotation/btc-dominance/alt-season/major-vs-alt/strongest-weakest-switch/binance-perpetual/15m/5m/1m/repo/public-data/cost/risk
- 证据类型：GitHub repo source audit + Binance USDⓈ-M public-data probe

## 1. 这次看了什么
这次看的是 **zwmjj (2026), `kuant-strategies`** 这个新 repo 里的 **`BTCDominanceStrategy`**，代码位置在：
- Repo: `https://github.com/zwmjj/kuant-strategies`
- File: `https://github.com/zwmjj/kuant-strategies/blob/main/strategies/crypto_advanced.py`

它最值得 intake 的地方，不是 README 里那句大而全的“crypto / cross-asset / alt-data / options 都有”，而是这条非常具体的轮动逻辑：
1. 先看 `BTC` 相对 alt 篮子的滚动超额收益；
2. 再看这条超额收益曲线是不是还在继续往同一方向加速；
3. 若 `BTC` dominance 继续走强，就做 `long BTC / short weakest alts`；
4. 若 `BTC` dominance 继续走弱，就做 `short BTC / long strongest alts`。

翻成人话：
- 它不是“猜市场涨跌”；
- 也不是“单腿追 BTC / 追 alt”；
- 它本质上是一条 **major vs alt sleeve 的相对价值轮动 alpha**。

这点对当前 desk 有意义，因为我们最近已经补了很多 funding / basis / order-flow / session pocket，但 **“BTC 与 alt 之间的相对强弱状态切换”** 这条 raw alpha 壳，素材还不算厚。

## 2. 核心结论
- **一句话核心结论：** 这条 `BTC dominance slope × strongest/weakest alt switch` 的想法，作为 **raw alpha 候选是成立的**；但它在 `15m` perp 上**不是逐根 taker 信号**，而更像一条 **低成本、低频、慢换仓的 relative-value 书**。
- **一句话证明方式：** 我先按 repo 核心逻辑把信号移植到 Binance USDⓈ-M `15m`，再分别看：
  1. 连续轮动 / 高频换仓版，
  2. 降频 rebalance 版，
  3. 加 dominance-gap 过滤后的低活跃度版本。

### 2.1 先看最直白的 port：信号本身不是假的
在 `BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT / XRPUSDT / DOGEUSDT` 上，若直接按这条逻辑做连续轮动：
- 最好的 **gross** 版本大致出现在：
  - `lookback = 32 bars`
  - `sma = 8 bars`
  - `top_alts = 4`
  - `每 4 根 15m rebalance 一次`（约 1 小时）
- 这版约为：
  - **`+22.37%` gross cumret**
  - **Sharpe `2.16`**
  - **MDD `-8.96%`**
  - 但平均 turnover 仍有 **`0.178x / bar`**。

也就是说：
- **信号方向本身是有 edge 的**；
- 问题不在“完全没用”，而在 **换仓成本太敏感**。

### 2.2 但一上 taker-ish 成本，这族信号很快塌
同一族连续轮动 / 高活跃度配置，在我这轮 sweep 里：
- 到 **`4 bps one-way`** 时，已经基本全线转负；
- 测试里最不差的高活跃版本，仍大约是：
  - **`-25.53%` cumret**
  - **Sharpe `-2.95`**。

这意味着：
- 如果把它理解成“每有 state 就立刻 aggressive rebalance 的 taker book”，**不行**；
- 但如果把它当成一条 **慢换仓状态书 / maker-first allocator / execution-aware sleeve**，事情就没那么糟。

### 2.3 真正更像 desk 可测版本的是：过滤后、慢 rebalance、低活跃度
我把它再压成更 desk 化的壳：
- 仍然用 repo 的核心结构：`BTC vs alt basket` dominance slope；
- 但加入 **dominance gap filter**：只有当 `BTC` 相对 alt 篮子的滚动超额收益累积已经超过某个阈值时，才允许持仓；
- 并把 rebalance 节奏降到 **每 24 根 `15m`**（约 `6h`）。

这轮里最像 first-verdict 的版本是：
- `lookback = 32`
- `sma = 8`
- `top_alts = 3`
- `dominance gap threshold = 60 bps`
- `rebalance every 24 bars`

结果：
- **gross：`+4.83%` cumret，Sharpe `0.95`，MDD `-4.58%`**
- 平均 turnover 仅 **`0.0176x / bar`**
- active ratio 约 **`24.6%`**
- 全样本约 **`144` 次入场**，只有 **`14` 次直接翻向**。

把成本粗扣后：
- **`1 bp one-way`**：仍约 **`+1.47%` cumret`，Sharpe `0.33`**；
- **`2 bps one-way`**：转成 **`-1.78%` cumret`，Sharpe `-0.29`**。

所以这条线当前最准确的判词是：
> **它是 raw alpha，不是幻觉；但它更像“低成本 slow rebalance relative-value sleeve”，不是能随便 taker 撞进去的短打信号。**

## 3. 为什么和当前项目有关
这条线值得进池，原因主要有 4 个：
1. **它是 raw alpha，不是 filter。**
   - 有明确方向、进场、换仓、出场、成本口径；
   - 不是单纯辅助打分。
2. **它补的是当前素材池里相对少一点的“BTC vs alt 轮动状态书”。**
   - 不是 generic breakout；
   - 也不是 funding / OI / liquidation 一类 crowding 数据分层。
3. **它天然是 relative-value 壳。**
   - 多空对冲后，对大盘绝对方向依赖没那么重；
   - 对 short-cycle desk 来说，比“单腿追 alt season”更像可以控风控、控仓位的书。
4. **它很适合往 `15m state -> 5m / 1m execution` 继续拆。**
   - alpha 本体在 `15m` 上形成；
   - 真正的成交优化可以下沉到 `5m / 1m`。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / rotation / major-vs-alt / strongest-weakest switch
- 基础 alpha：`BTC` 相对 alt 篮子的 dominance slope 若继续往一个方向强化，则 `BTC` 与当前 strongest/weakest alts 的相对表现往往还会继续扩张
- regime：`BTC season` / `alt season` 的局部状态切换，但这里用的是 **可计算的相对强弱 slope**，不是叙事词
- filter / veto：只在 dominance gap 超过阈值时开仓；避免在 `BTC vs alt` 没有明确状态时频繁换仓
- risk / sizing / execution overlay：`BTC` 半仓，对侧 `top_n` alts 均分半仓；优先低频 rebalance；成本必须按 multi-leg turnover 扣，不要偷算成单腿

## 4. 可复刻的最小实验
### 研究假设
如果 `BTC` 相对 alt 篮子的超额收益已经明显偏向某一边，而且这条相对强弱曲线还在继续朝同方向移动，那么 **最弱 alt / 最强 alt** 往往会继续承担这条 dominance 变化的下一段。

### 一个可计算定义
1. 资产池：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT / XRPUSDT / DOGEUSDT`
2. 周期：`15m`
3. 先算：
   - `btc_ret - mean(alt_ret)`
   - 对其做 `32 bars` rolling sum，得到 dominance gap
   - 再做 `8 bars` SMA，并取一阶差分，得到 dominance slope
4. 若：
   - `dominance slope > 0`
   - 且 `dominance gap > +60 bps`
   则做：
   - `long BTC 0.5`
   - `short 当下最弱的 3 只 alt，合计 -0.5`
5. 若：
   - `dominance slope < 0`
   - 且 `dominance gap < -60 bps`
   则做：
   - `short BTC -0.5`
   - `long 当下最强的 3 只 alt，合计 +0.5`
6. `rebalance every 24 bars`（约 `6h`）
7. 成本先测 `0 / 1 / 2 bps one-way`

### 当前最像 desk 版本的 first test
先别把它做成高频 signal，先测这版：
- signal TF：`15m`
- execution shell：`6h` 慢换仓
- universe：6 币 major/alt sleeve
- filter：`|dominance gap| >= 60 bps`
- sizing：`BTC 0.5`，对侧 `3` 只 alt 均分 `0.5`

### 和 `1m / 3m / 5m / 15m` 的关系
- **alpha 本体**：当前更像 `15m` state alpha
- **执行下沉**：可把下单拆到 `5m / 1m`
- **不建议**：直接把这条信号误当成 `1m` 原生方向信号

## 5. 风险与保留意见
- 这条 edge **高度成本敏感**。如果按 taker-ish 方式频繁换仓，收益很快被吃光。
- 当前 public probe 只用了 6 个 liquid majors/alts；真实 alt universe 扩张后，可能：
  - 机会更多；
  - 也可能 turnover 更差。
- 当前 strongest / weakest alt 的暴露并不均匀，选中频率更集中在：
  - `DOGEUSDT`
  - `SOLUSDT`
  - `XRPUSDT`
  说明它有一定 **资产集中度风险**。
- repo 原始实现偏日频思路；我这轮是 **desk-oriented intraday port**，不能把参数解释成作者已验证的短周期最优值。
- 这条线更像 **state rotation book**，不是 ultra-short microstructure alpha；不要拿它去和秒级 OBI / OFI 比“每根收益率”。

## 6. 最值得复用的点
这份 repo 最值得复用的，不是“BTC dominance”这个名词，而是它背后的模板：
**核心资产 vs 卫星资产篮子 -> 相对强弱状态 -> strongest/weakest sleeve 切换。**

这套模板后面还可以继续复用到：
- `ETH vs L2 / beta-alt basket`
- `BNB vs exchange-beta basket`
- `BTC vs memecoin sleeve`
- `BTC vs funding-sensitive alt sleeve`

也就是说，今天 intake 的不只是一个具体 alpha，还有一套 **major-vs-satellite rotation 模板**。

## 7. 一句话结论
> 这份 2026 repo 里最值得当前 short-cycle desk 先 intake 的，不是泛泛的“alt season 轮动”叙事，而是更可计算的这条 raw alpha：**`BTC 相对 alt basket dominance slope` 若继续强化，就切到 `BTC / weakest alts`；若继续走弱，就切到 `strongest alts / BTC`。** 但 public probe 也很明确：它更像 **低成本、慢换仓、execution-aware 的 relative-value 书**；若按逐根 taker 信号去打，edge 会被换手吃掉。

## 8. 下一步怎么测
1. **先做 `15m state -> 5m execution` 分层测试**
   - `15m` 只负责出状态；
   - `5m` 负责把 `BTC` 和 alt 腿分批成交；
   - 看 maker / passive fill 能不能把有效成本压到 `1 bp one-way` 附近。
2. **把 alt sleeve 改成更 desk 化的分层**
   - `beta-alt`、`memecoin`、`exchange-beta`、`L1 majors`
   - 看 strongest/weakest 切换是否在某些 sleeve 上更干净。
3. **测试“只在 funding / OI / session clock 对齐时启用”**
   - 看它能不能作为现有 raw alpha 的 state router；
   - 但 router 只是扩展，不要覆盖今天这条 alpha 本体。
4. **把 `rebalance every 24 bars` 改成 event-driven refresh**
   - 只在 dominance gap 跨阈值 / 失效时刷新，进一步降 turnover。

## 9. 本轮产物
- 研究笔记：`research/quant_digests/2026-04-12_1118_btc-dominance-slope-rotation-alpha.md`
- Continuous / throttled summary：`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_continuous_rebalance_summary.csv`
- Filtered summary：`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_filtered_rebalance_summary.csv`
- Selected config detail：`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_detail.csv`
- Selected config alt frequency：`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_alt_frequency.csv`
- Meta：`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_meta.json`

## 10. 来源
1. **zwmjj (2026). `kuant-strategies`**
   - Repo URL: `https://github.com/zwmjj/kuant-strategies`
   - Readable file URL: `https://github.com/zwmjj/kuant-strategies/blob/main/strategies/crypto_advanced.py`
   - Relevant class: `BTCDominanceStrategy`
   - Repo metadata（本轮查询）: created `2026-04-11T19:54:53Z`, updated `2026-04-11T20:07:34Z`
2. **Binance USDⓈ-M Futures Public Data**（本轮 portability probe 实际使用）
   - REST klines: `https://fapi.binance.com/fapi/v1/klines`
   - Archive data: `https://data.binance.vision/`
3. **本地 probe artifacts**
   - `reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_continuous_rebalance_summary.csv`
   - `reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_filtered_rebalance_summary.csv`
   - `reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_detail.csv`
   - `reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_alt_frequency.csv`
