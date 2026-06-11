# 别把这组 crypto 订单流论文只读成“价格形成解释”：对 short-cycle desk，更该先测的是「small-size taker surge × no-large-flow confirmation」这条 raw alpha

- 时间：2026-04-14 00:06 UTC
- 类型：2024/2025 SSRN 论文元数据（Crossref + OpenAlex）+ Binance USDⓈ-M `aggTrades` size-bucket portability probe
- 主题类型：raw alpha
- 基础 alpha：**当小单主动买卖压力突然单边化、但大单没有同向确认时，这段 move 更像“零售/噪声冲击后的短时失衡”，未来 `1m~5m` 更适合反打；若大小单同向共振，至少在当前 public-data 代理口径下，并没有给出干净 continuation。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/microstructure/order-flow/trade-size-decomposition/retail-proxy/large-trade-confirmation/divergence/fade/binance-perpetual/1m/3m/5m/15m/paper/metadata/public-data/cost/risk
- 证据类型：论文元数据 + 本地 public-data portability probe

## 1. 这次看了什么
这轮主线不是继续做 CVD / OFI 的老读法，而是补一条**更接近“交易对手拆解”**的 microstructure raw alpha。

主参考材料有两篇：

1. **Bozzetto, Christian; Sifat, Imtiaz; Nahidi, Narmin (2024)**  
   - **Title:** *Fee Structure and Order Flow Informativeness in the Cryptocurrency Market*  
   - **Venue:** SSRN Electronic Journal / working paper  
   - **DOI:** `10.2139/ssrn.5051291`  
   - **Readable URL:** <https://doi.org/10.2139/ssrn.5051291>  
   - **Metadata anchor:** <https://api.openalex.org/works?filter=doi:10.2139/ssrn.5051291>  
   - **Repo URL:** 暂未见公开代码仓库

2. **Eom, Chanyoung (2025)**  
   - **Title:** *The Anatomy of Retail Order Flow: Counterparty Decomposition and Price Formation*  
   - **Venue:** SSRN Electronic Journal / working paper  
   - **DOI:** `10.2139/ssrn.5974914`  
   - **Readable URL:** <https://doi.org/10.2139/ssrn.5974914>  
   - **Metadata anchor:** <https://api.crossref.org/works/10.2139/ssrn.5974914>  
   - **Repo URL:** 暂未见公开代码仓库

要先说明清楚：**这轮并没有直接读到 SSRN 全文 PDF**，因为 SSRN 反爬挡住了正文抓取；所以我不假装看过没看到的表格数字。真正用来定题的，是：

- 标题 / 作者 / DOI / venue 等元数据；
- 这两篇都在说的同一件事：**order flow 不能只看总量，应该拆交易对手或交易流类型**；
- 我再用 Binance 公共 `aggTrades` 做一个**可独立复现的 trade-size proxy 最小实验**，回答更适合我们 desk 的问题：

> **如果把“小单主动流”当成 retail-like proxy，把“大单主动流”当成更强确认流，真正值得先测的，是 continuation 还是 divergence fade？**

一句话先定性：

> **更值钱的不是“订单流有信息”这句空话，而是 `small-size taker surge × no-large-flow confirmation -> short-horizon fade` 这条 raw alpha。**

## 2. 核心结论
- **一句话核心结论：** 当前 first-pass 结果更支持“**小单冲、但大单不跟**”是一条可测的短时均值回归 raw alpha，而**不支持**把“大小单同向”直接翻译成短窗 continuation。
- **一句话证明方式：** 我用 Binance USDⓈ-M `BTC/ETH/SOL` 最近 `10` 天 `aggTrades`，按**日内成交额中位数 / 90 分位**把逐笔成交粗分成 `small / mid / large` 三桶；再对每分钟主动买卖金额做 rolling z-score。结果：
  - `divergence_fade`（小单极端单边、大单未确认）共有 **1315** 个事件，后 **5m 平均 +0.646 bps**、中位 **+0.935 bps**、胜率 **51.6%**；
  - 但拉到 **15m** 后只剩 **-0.071 bps**，几乎归零；
  - 相反，`confirmed_cont`（大小单同向）共有 **3344** 个事件，后 **5m 平均 -0.444 bps**、后 **15m 平均 -0.504 bps**，first-pass 反而更差。

最关键的不是绝对数有多大，而是**方向判别已经分出来了**：

> **在当前代理口径下，divergence 比 confirmation 更像 alpha，本体偏 mean reversion，不偏 continuation。**

## 3. 为什么这条线值得单独写，而不是继续并进“泛 order flow”主题
它补的是一个当前池子里还不够密的缺口：

- 我们已经有 OFI、CVD、bar delta、large-trade bias 这类**“看总压力方向”**的材料；
- 但还缺一种更像交易对手拆解的读法：**不是问“有没有买盘”，而是问“是谁在追这笔买盘，谁没来确认”。**

对 short-cycle desk，这个问题很值钱，因为很多分钟级假突破 / 假延续，本质上不是“没有成交”，而是：

> **只有小单在追，真正更有信息量的大单没有继续抬轿。**

这就让它和已有 OFI 线不完全重复：

- OFI / CVD 更像**总失衡**；
- 这条线更像**失衡的成分拆解**；
- 更适合补 `1m/3m/5m` 的 microstructure mean reversion 素材池。

## 4. 本地 public-data portability probe：把“retail-like vs confirmation flow”翻成 Binance `aggTrades` 最小实验
### 4.1 数据与口径
- 市场：**Binance USDⓈ-M perpetual**
- 资产：`BTCUSDT, ETHUSDT, SOLUSDT`
- 数据源：**Binance Data Vision 日频 `aggTrades` 压缩包**
- 样本期：**2026-04-03 ~ 2026-04-12**（10 天）
- 原始字段：`price, quantity, transact_time, is_buyer_maker`
- 主动方向判断：
  - `is_buyer_maker = False` 视作**主动买**
  - `is_buyer_maker = True` 视作**主动卖**
- 交易额：`notional = price * quantity`
- size bucket：按**每币、每天**的成交额分布粗分：
  - `small`：`<=` 当日中位数
  - `large`：`>=` 当日 90 分位
  - 其他归 `mid`
- 每分钟聚合：对 `signed_notional` 求和，形成 `flow_small / flow_large`
- 标准化：`240` 分钟 rolling z-score

这里一定要诚实：

> **small ≠ 真 retail，large ≠ 真机构。**

这只是一个**公开数据可复现**的 proxy；但对 desk 来说，重要的是它能先回答：**trade-size decomposition 到底有没有可交易形状。**

### 4.2 信号定义
我先只测两条最朴素的分支：

1. **divergence_fade**  
   - `flow_small_z >= 1.5` 且 `flow_large_z <= 0` → **short**  
   - `flow_small_z <= -1.5` 且 `flow_large_z >= 0` → **long**

2. **confirmed_cont**  
   - `flow_large_z >= 1.0` 且 `flow_small_z >= 0` → **long**  
   - `flow_large_z <= -1.0` 且 `flow_small_z <= 0` → **short**

本地结果已写入：

- `/root/clawd/jerry/momentum/reports/artifacts/quant_digest_live/smallflow_nolargeconfirm_fade_20260414.json`

## 5. first verdict：当前更像“retail-like push exhaustion fade”，不是“confirmation continuation”
### 5.1 divergence_fade 有 first-pass 正形状，但只活在很短窗
`divergence_fade` 的聚合结果：

- 事件数：**1315**
- 后 `5m`：
  - 平均 **+0.646 bps**
  - 中位 **+0.935 bps**
  - 胜率 **51.6%**
- 后 `15m`：
  - 平均 **-0.071 bps**
  - 中位 **+0.389 bps**
  - 胜率 **50.3%**

翻成人话：

> **这条 edge 不是“拿住就会赚更多”的趋势信号，而更像 1~5 分钟里的短促回吐。**

所以如果真要 desk 化，它的默认落点不是 `15m hold`，而是：

- `1m/3m` 触发；
- `3m/5m` time-box 出场；
- `15m` 更适合拿来当“别硬抱”的反证窗口。

### 5.2 分币后，BTC / ETH 明显比 SOL 更像可交易 lane
按 `5m` 看，`divergence_fade` 分币结果：

- **BTCUSDT**：`143` 个事件，平均 **+1.124 bps**，胜率 **59.4%**
- **ETHUSDT**：`295` 个事件，平均 **+0.977 bps**，胜率 **52.2%**
- **SOLUSDT**：`877` 个事件，平均 **+0.457 bps**，胜率 **50.1%**

这说明：

- **BTC / ETH 更值得先做主实验**；
- SOL 这类更活跃、但噪声也更重的名字，可能需要更严格的过滤层；
- 如果直接把这条线包装成“全市场 microstructure 定律”，就过度了。

### 5.3 “大小单同向 = continuation” 这条直觉，当前反而站不住
`confirmed_cont` 的结果更重要，因为它帮我们排除了一个很常见、但容易想当然的读法：

- 事件数：**3344**
- 后 `5m` 平均：**-0.444 bps**
- 后 `15m` 平均：**-0.504 bps**
- 三个币 `5m` 都没给出正值：
  - BTC：**-0.663 bps**
  - ETH：**-0.181 bps**
  - SOL：**-0.481 bps**

所以这轮最重要的研究结论之一，不是“某个信号赚多少”，而是：

> **别先入为主地把 `large flow confirmation` 当 continuation alpha；至少在这个公开 proxy 里，真正更值得先测的是“未被大单确认的小单冲动”会不会回吐。**

## 6. 这条 raw alpha 的 desk 化读法
### 6.1 它的本体是 mean reversion，不是 overlay
这条线的 base alpha 很清楚：

> **`retail-like one-sided push` 在没有大单确认时，更容易短时回吐。**

所以它不是 filter，不是 regime 说明书；它本身就是一条**单资产、microstructure、短窗均值回归** raw alpha。

### 6.2 但它目前还不是“可以直接一键上线的完整策略”
原因也很清楚：

- `5m` 的 gross edge 仍很薄；
- 双边 taker 成本很可能直接把它吃掉；
- 目前还没把 `1m/3m`、session、spread、funding/OI crowding、maker fill quality 全部分层跑完。

所以这一轮最诚实的定性是：

> **它已经够格进入 raw alpha 素材池，但暂时还不该被写成 production-ready 完整壳。**

### 6.3 更合理的第一版落地形态
如果继续做，不建议上来就：

- 全市场全币跑；
- 每个事件都 taker 反打；
- 持有到 15m。

更像样的第一版应该是：

1. 先只做 `BTC/ETH`；
2. 只保留 `small-flow z` 更极端的事件；
3. 默认 `3m` time-stop，`5m` 最多容忍；
4. maker-first 或者 half-maker 执行优先；
5. funding / OI / liquidation crowding 极端时先 veto，因为那种情况下“看起来像小单冲动”的 move 可能其实是更大级别级联的前奏。

## 7. 策略拆解（必填）
- 方向属性：**single-asset / microstructure / short-horizon mean reversion**
- 基础 alpha：**small-size aggressive flow surge without large-flow confirmation -> short-horizon fade**
- regime：更适合高流动、逐笔成交连续、价差稳定的 majors；极端新闻 / 级联 / funding squeeze 时应降权
- filter / veto：`funding/OI/liquidation crowding`、异常大波动分钟、宽点差、session 交接时段、单边趋势已明显扩散时不做
- risk / sizing / execution overlay：事件强度分层仓位、`3m` 默认 time-stop、`5m` 最长容忍、maker-first、连续亏损 cooldown、每分钟成交次数上限

## 8. 为什么它和当前 desk 直接相关
这条线比继续补一个“泛解释型 order flow 综述”更值得，因为它满足当前优先级：

- **是 raw alpha，不是 overlay；**
- **公开数据可复现；**
- **能映射到 `1m/3m/5m/15m` 的最小实验；**
- **而且与已有 raw alpha 积累直接互补。**

更具体地说：

- 它能和已有 OFI / CVD 线做**正交组合**：一个看总压力，一个看压力成分；
- 它也能给已有 trend / breakout / cascade 书做**execution veto**：如果只是小单在冲、没有大单确认，也许不该追；
- 对 pairs / basis / carry 书，它还能做**短时级别的入场细化**：择更不拥挤的瞬时切点，而不是只看慢状态。

## 9. 风险与保留意见
- **size 不是身份。** 用成交额去 proxy retail / informed flow，很粗糙；只能说是第一层 public proxy。
- **当前 alpha 很薄。** `+0.646 bps / 5m` 这种量级，不足以支持盲目 taker。
- **15m 不该硬抱。** 这条线一旦拖到 15m，优势基本消失。
- **全文未直读。** 这轮主要靠 metadata 定题 + 公共数据复现，不应伪装成“已完整复刻论文主表”。

## 10. 下一步怎么测
1. **先补 `1m/3m/5m/15m` 完整 horizon sweep。** 当前最重要的问题不是再调阈值，而是确认 edge 究竟活多久。
2. **做 friction ladder。** 至少跑 `0 / 2 / 4 / 6 / 8 bps` 单边或 round-trip 口径，别只看 gross。
3. **做 `BTC/ETH` 专项 refine。** 把 `small-flow z` 阈值改成 `1.5 / 2.0 / 2.5`，看看 edge 是否随极端度上升而单调增强。
4. **补 crowding veto。** 把 Binance public funding / OI / top-trader ratio 接进来，检验“看起来像 retail push”的事件里，哪些其实是 crowding continuation，应该禁做 fade。
5. **做 maker-first 版本。** 如果 taker 费后归零，但 maker-rebate 或 passive fill 还能留边际，这条线才值得继续深挖。

## 11. 来源
1. **Bozzetto, C., Sifat, I., & Nahidi, N. (2024). _Fee Structure and Order Flow Informativeness in the Cryptocurrency Market_. SSRN Electronic Journal.**  
   DOI: `10.2139/ssrn.5051291`  
   Readable URL: <https://doi.org/10.2139/ssrn.5051291>  
   Metadata URL: <https://api.openalex.org/works?filter=doi:10.2139/ssrn.5051291>

2. **Eom, C. (2025). _The Anatomy of Retail Order Flow: Counterparty Decomposition and Price Formation_. SSRN Electronic Journal.**  
   DOI: `10.2139/ssrn.5974914`  
   Readable URL: <https://doi.org/10.2139/ssrn.5974914>  
   Metadata URL: <https://api.crossref.org/works/10.2139/ssrn.5974914>

3. **Binance Data Vision — USDⓈ-M Futures Daily AggTrades**  
   URL pattern: <https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2026-04-12.zip>  
   公开性：公开可下载  
   更新频率：日更归档  
   最小可复现实验口径：逐笔成交字段 `price / quantity / transact_time / is_buyer_maker`，按 trade notional 分桶后聚合到 `1m` 做 signed flow z-score
