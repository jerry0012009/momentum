# 别把韩盘份额只当 Kimchi premium 新闻：这篇 2026 *Systems* 论文更该先落地的是「ΔKVSI × Korea-led continuation / offshore fade」共享 regime gate
- 时间：2026-04-02 05:22 UTC
- 类型：2026 *Systems* 论文 DOAJ 摘要 + Crossref/OpenAlex metadata + Upbit/Binance 公共 `5m` portability probe
- 主题类型：regime
- 基础 alpha：**无独立 raw alpha；它更适合服务 `1m/3m/5m/15m` 的 BTC/major cross-market momentum、lead-lag continuation 与 shock-reversal 策略。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：regime/filter/shared-gate/venue-segmentation/kvsi/korea/upbit/binance/kimchi-premium/cross-market/momentum/lead-lag/shock-reversal/public-data/5m/15m/paper/external-data
- 证据类型：DOAJ 摘要证据 + metadata + 公共数据 portability probe

> 先回答 base alpha：**答不清独立 raw alpha。** 更诚实的定位，是一个能同时服务多类 raw alpha 的 **venue-segmentation gate**。如果硬把它包装成“下一根 BTC 必涨/必跌”，那是在超出证据说话。

## 1. 这次看了什么
这次主看的是：
- **Deok Han, YoungJun Kim (2026), _Enhancing Reinforcement Learning-Based Crypto Asset Trading: Focusing on the Korean Venue Share Indicator_**
- DOAJ 收录摘要 + Crossref / OpenAlex metadata
- **Upbit `KRW-BTC` 分钟蜡烛** 与 **Binance BTCUSDT spot / perp 公共 `5m` 数据**，做一个 desk-side public-data portability probe

这轮我没有把它硬写成一条新的 raw alpha，原因很简单：
- 论文 headline 是 **把 KVSI 放进 RL state**；
- 真正可迁移给我们 desk 的，不是 RL 本身；
- 而是一个更值钱的旁支：**“韩盘相对全球盘口的话语权”这个 state variable，能不能拿来决定哪些短周期 alpha 值得开火、哪些更该降档。**

如果一定要一句话概括这轮主题：
**不是做 “Kimchi premium 叙事学”，而是把 `韩国交易量份额变化` 变成一个可复现、可接线、可拿来 gate 现有 raw alpha 的 venue-level regime 指标。**

这轮为什么仍值得 intake，而不是继续机械地补第 N 条 pairs / funding / breakout raw alpha？
- 过去几天 raw alpha intake 已经很密；
- 但库里还缺一个**公开可拿、分钟级可更新、能解释“到底是谁在主导价格发现”** 的 cross-venue 状态变量；
- 这类信号不是宏观慢变量，而是 **可映射到 `5m/15m` 的微观结构 gate**，对现有动量、lead-lag、冲击后反手线都能直接服务。

## 2. 核心结论
### 2.1 论文真正有用的点
DOAJ 摘要给出的可用信息其实很集中：
1. **核心对象**：作者提出 **KVSI（Korean Venue Share Indicator）**，本质是 **韩国交易所相对全球交易所的交易量份额指标**。
2. **研究动机**：crypto 市场并没有完全“全球一体化”；韩国市场份额本身就不小，且长期存在 **Kimchi premium / venue segmentation / price discovery** 问题。
3. **论文结论**：把 KVSI 放进多个 RL 模型的 state 后，**相对不含 KVSI 的 baseline，累计收益（CR）、Sharpe ratio（SR）和最大回撤（MDD）都有统计显著改善**。
4. **更重要的一句**：**KVSI 带来的提升具有 market-regime dependence。**

翻成人话：
**作者真正告诉你的，不是“用 RL 炒币”，而是“谁在主导盘口信息吸收”这件事，本身值得进入状态空间。**

### 2.2 对 short-cycle desk 最该偷的，不是 RL，而是这个可解释 state
对我们 desk，最有迁移价值的读法是：
- 当 **韩国份额上升 / 份额变化加速** 时，说明价格发现权更可能暂时向韩盘倾斜；
- 这类时点更可能出现：
  - offshore 跟随 continuation；
  - 或 offshore 原本的 fade 信号失效；
  - 或 BTC / major 先出现“韩国主导的冲击”，再向其他 venue 扩散。

所以它更像：
- `momentum / lead-lag` 的 **gate-on** 条件；
- `shock-reversal` 的 **veto** 条件；
- 或多市场策略的 **risk budget 调整器**。

## 3. 本地 public-data portability probe（不是论文精确复现）
我补了一个很轻的 desk-side probe，不去碰 RL，只回答一句话：
**“公开可拿的 Upbit/Binance 数据，能不能先把 KVSI 类 proxy 做出来，并在 `5m -> 15m` 上看到一点 transfer 痕迹？”**

### 3.1 口径
- 韩国腿：**Upbit `KRW-BTC` `5m` candles**
- 全球腿 proxy：**Binance `BTCUSDT` spot `5m` quote volume**
- 交易对象：**Binance BTCUSDT perpetual `5m` returns**
- 样本：**2026-03-29 18:00 UTC 到 2026-04-02 05:15 UTC**
- 样本量：**996 根 `5m` bar**
- FX 处理：
  - 用同一 bar 的 `Upbit KRW-BTC price / Binance BTCUSDT spot price`
  - 反推出 **隐含 KRWUSD**
  - 再把 Upbit `candle_acc_trade_price`（KRW）转成 USD notional
- proxy 定义：
  - `KVSI_proxy = Upbit_USD_quote_volume / (Upbit_USD_quote_volume + Binance_spot_quote_volume)`
  - 同时看 **level z-score** 与 **ΔKVSI z-score**
- 预测目标：**Binance BTCUSDT perp 下一根 / 下两根 / 下三根 `5m` log return**

### 3.2 快检结果
结果很诚实：**level 本身不强，但“份额变化”比“份额绝对水平”更像能提供一点 15m 方向信息。**

最值得记的 3 个数：
1. **`ΔKVSI z-score` 顶部 decile** 对应的 **后续 15m 平均 perp return 约 `+2.60 bps`**；底部 decile 约 **`+0.14 bps`**；两者差约 **`+2.46 bps`**。
2. **`KVSI level z-score` 顶部 decile** 的后续 15m 平均 return 约 **`-0.31 bps`**；底部 decile 约 **`-2.65 bps`**；两者差约 **`+2.34 bps`**。
3. 线性相关层面，`ΔKVSI z-score -> next 15m return` 的样本相关大约 **`0.036`**，t-stat 约 **`1.07`**；强度不高，但至少说明 **方向变化** 比 **绝对水平** 更值得下一轮深挖。

翻成人话：
- 这还远远不是“能直接交易的 standalone alpha”；
- 但它已经够说明：**KVSI 类 proxy 至少不是完全空气，而且更可能作为 `gate / veto / sizing` 有用。**

## 3.5 策略拆解（必填）
- 方向属性：shared regime / venue-segmentation gate
- 基础 alpha：无独立 raw alpha；服务对象是 `cross-market momentum / lead-lag / shock-reversal`
- regime：韩国份额抬升、或份额变化显著上冲时，允许 trend / continuation 线提高信号权重
- filter / veto：若已有做空均值回归 / fade 逻辑，遇到 `ΔKVSI` 明显转强时先降权或 veto
- risk / sizing / execution overlay：
  - `gate_on`: 仓位 `1.0x`
  - `soft_on`: 仓位 `0.5x`
  - `gate_off`: 仓位 `0~0.25x`
  - 只改风险预算，不改 base alpha 的 entry 本体

## 4. 和当前项目的直接关系
这条线和当前 desk 是直接相关的，不是泛泛而谈的宏观解释：

1. **它能同时服务至少 3 类已在池中的 alpha**
   - `cross-market momentum`
   - `BTC -> alt / venue-to-venue lead-lag`
   - `shock fade / short-horizon mean reversion`

2. **它补的是目前库里比较缺的东西：venue state variable**
   我们已经有不少“价差/动量/OFI/funding”线索，但还缺一个明确回答：
   **“这根 bar 是谁在主导价格发现？”**

3. **它是可接线、可分钟级更新的外部数据**
   不是日频慢变量，不是只能做宏观背景板；
   它天然可以 forward 到 `1m/3m/5m/15m`，尤其适合做 `5m/15m` gate。

## 5. 外部数据口径（必须写清）
这条线依赖外部公开数据，必须把口径写清：

### 5.1 论文口径
- 指标：**KVSI = 韩国交易所相对全球交易所的交易量份额指标**
- 用途：作为 venue-level state variable，进入策略状态空间
- 公开性：论文摘要未给出私有数据要求，概念上依赖各 venue 的公开成交量
- 更新频率：可做成分钟级 / bar 级

### 5.2 desk 最小可复现实验口径
- 数据源 1：**Upbit `KRW-BTC` 分钟蜡烛 API**
  - 公开性：公开可得
  - 更新频率：分钟级
  - 直接用字段：`trade_price`, `candle_acc_trade_price`, `candle_acc_trade_volume`
- 数据源 2：**Binance Spot `BTCUSDT` klines**
  - 公开性：公开可得
  - 更新频率：`1m/3m/5m/...`
  - 用途：作为 global volume proxy 与 FX 变换参考腿
- 数据源 3：**Binance Futures `BTCUSDT` perp klines**
  - 公开性：公开可得
  - 更新频率：`1m/3m/5m/...`
  - 用途：作为策略交易腿 / 预测目标

### 5.3 最小可复现实验映射
- 若做 `5m`：每根 bar 更新一次 `KVSI_proxy` 与 `ΔKVSI_proxy`
- 若做 `15m`：可将 3 根 `5m` 聚合为
  - `max(ΔKVSI_z)`
  - `close-to-close ΔKVSI`
  - `KVSI level percentile`
- 先只用它做 gate / veto，不要伪装成单独方向信号

## 6. 最小可复现实验（面向 1m / 3m / 5m / 15m）
第一轮建议只做最小、干净、不会把问题做脏的版本：

1. **先固定一个 raw alpha 本体**
   - 方案 A：`5m/15m` BTC continuation
   - 方案 B：`5m/15m` BTC shock fade
   - 方案 C：BTC impulse -> ETH/SOL follower lead-lag

2. **给它挂一个三档 KVSI gate**
   - `gate_off`：`ΔKVSI_z < 0`
   - `gate_mid`：`0 <= ΔKVSI_z < p80`
   - `gate_on`：`ΔKVSI_z >= p80`

3. **先做最小比较**
   - 裸跑
   - 裸跑 + binary gate
   - 裸跑 + ternary sizing

4. **核心指标**
   - post-cost pnl
   - turnover
   - hit-rate / payoff ratio
   - gate-on vs gate-off 的 signal quality split
   - reversal 线被错误逆冲打脸的次数

## 7. 下一步怎么测（必须）
1. **优先测 `ΔKVSI`，不要优先测 level。**
   这次快检已经提示：变化量比绝对份额更有 transfer 价值。

2. **先接两类相反风格 alpha 做 A/B。**
   - `trend / continuation`
   - `short-horizon fade / reversal`
   如果一个明显受益、另一个明显受损，KVSI 的真实角色会比继续堆解释更清楚。

3. **把“韩国腿”从 BTC 扩到 ETH / majors。**
   若 Upbit 上 ETH / XRP / SOL 的本地份额变化也有相似信息，KVSI 才更像 shared gate，而不是 BTC 特例。

4. **把 global proxy 从单一 Binance 扩到多 venue。**
   当前 probe 只是 `Upbit vs Binance`，下一轮应扩成 `Upbit / (Binance + OKX + Bybit)`，否则 global leg 太单薄。

5. **做 time-of-day 分层。**
   韩盘权重的有效性很可能和亚洲时段、欧美交接时段不同；若全天混着测，edge 容易被冲淡。

6. **若后续证据继续成立，再把它升级成 risk budget 组件。**
   到那一步，再讨论它是否应该控制资金杠杆、最大并发仓位或 maker/taker 模式切换。

## 8. 风险与保留意见
- **这不是 standalone raw alpha。** 当前只能排在二梯队 intake，而不是顶级 raw-alpha intake。
- 论文本轮能拿到的是 **DOAJ 摘要 + metadata**，不是全文精读；因此我们只能对其最稳妥的迁移部分发言。  
- 本地快检只是 **public-data portability probe**，样本很短（约 4 天），不能拿来下结论。  
- `Upbit vs Binance` 只是一个很粗的 `Korea vs global` proxy，不等于论文精确定义的 KVSI。  
- 这个主题最容易犯的错，就是把它硬说成“韩盘变强=下一根必涨”；目前证据完全不支持这么强的表述。  

## 9. 来源
1. **Han, D., & Kim, Y. (2026). _Enhancing Reinforcement Learning-Based Crypto Asset Trading: Focusing on the Korean Venue Share Indicator_. Systems.**
   - Venue: *Systems*
   - DOI: `10.3390/systems14010111`
   - Readable URL: `https://doaj.org/article/2a96001897424b6aa1fca527d14ece5f`
   - DOI URL: `https://doi.org/10.3390/systems14010111`
   - Repo URL: N/A

2. **Upbit quotation endpoint (`KRW-BTC` minutes candles).**
   - Endpoint example: `https://api.upbit.com/v1/candles/minutes/5?market=KRW-BTC&count=200`

3. **Binance Spot API – Kline/Candlestick Data.**
   - Endpoint example: `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=1500`

4. **Binance Futures API – Kline/Candlestick Data.**
   - Docs URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - Endpoint example: `https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=5m&limit=1500`

## 10. 本地复现产物
- `reports/artifacts/quant_digests/2026-04-02_kvsi_proxy_probe/summary.json`
- `reports/artifacts/quant_digests/2026-04-02_kvsi_proxy_probe/kvsi_proxy_panel_5m.csv`
- `reports/artifacts/quant_digests/2026-04-02_kvsi_proxy_probe/probe_notes.txt`

## 11. 一句话结论
**这篇 2026 KVSI 论文对 short-cycle desk 最有价值的，不是 RL，而是把“韩国盘口是否正在拿回价格发现权”这件事，变成一个能挂到现有 raw alpha 上的 venue-segmentation gate。第一步该测 `ΔKVSI`，不是复刻 agent。**
