# 别把大币 lead-lag 继续读成“山寨跟涨”：这篇 2023 JEmpFin 更该先测的是「large-cap shock → alt basket 反向 seesaw」5m raw alpha
- 时间：2026-03-26 15:55 UTC
- 类型：2023 Journal of Empirical Finance 论文（IDEAS/RePEc 摘要 + 搜索结果摘要交叉）+ Binance Futures 公共 `5m/15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**大币先动后，小币不一定“跟着同向补动”，反而更可能出现反向 seesaw。** 对 desk 最可复现的第一版，不是做复杂 LASSO 黑箱，而是做 `BTC+ETH 5m leader shock -> 反向交易高流动性 alt basket`。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/negative-leadlag/seesaw/large-vs-small/alt-basket/market-neutral/5m/15m/binance/perpetual/paper
- 证据类型：摘要级论文证据 + 本地公共数据快检

> 先回答 base alpha：**这不是 filter，也不是“市场结构解释层”。base alpha 就是“大币上一根短周期冲击，对下一根/接下来几根小币收益有反向预测力”，可直接写成 cross-sectional / relative-value raw alpha。**

## 1. 这次看了什么
主来源是：
- **Yuecheng Jia, Yangru Wu, Shu Yan, Yuzheng Liu (2023), _A seesaw effect in the cryptocurrency market: Understanding the return cross predictability of cryptocurrencies_, Journal of Empirical Finance, DOI: `10.1016/j.jempfin.2023.101428`**

从目前能公开抓到的摘要信息看，这篇东西最值钱的不是“又一篇 lead-lag 文献”，而是它明确说：
- crypto 的 intraday cross-predictability **不是股票里常见的正向 lead-lag**；
- 恰恰相反，它更像 **negative lead-lag / seesaw**；
- **large coins negatively predict other coins**，而 small coins 很少反过来预测 large coins；
- 作者用 **LASSO** 做可交易信号，且摘要明确写到：**across major exchanges、在 realistic transaction costs 下仍有显著利润**。

这对当前 desk 的价值非常直接：
- 我们最近 intake 里已经有不少 **正向跟涨 / delayed follow-through** 的 lead-lag；
- 这篇补的是另一面：**leader 冲击后，follower 更适合反着做**；
- 所以它不是重复讲“BTC 先动、alts 后动”，而是在 raw alpha 池里补上一条 **negative propagation / relative-value** 分支。

## 2. 核心结论
### 一句话核心结论
**别默认 BTC/ETH 一冲，alts 下一拍就同向补涨补跌；在这篇 2023 JEmpFin 的读法里，更值得先测的是“大币冲击后的 alt 反向 seesaw”。**

### 一句话它怎么证明
摘要级证据给出的论点很清楚：
1. **大币对小币存在负向 intraday cross-predictability**；
2. small 对 large 的反向预测力弱得多；
3. 用稀疏模型（LASSO）把这种 cross-predictability 落成交易策略，**在主要交易所、含现实交易成本后仍显著**。

### 这轮最该记住的 4 个数字
1. **本地 `5m` follower-only 快检（近 90d，Binance USDⓈ-M，leaders=`BTC+ETH`，followers=`SOL/XRP/DOGE/ADA/LINK`）**：如果每根都做 `followers <- opposite(sign(leader_{t-1}))`，平均只有 **+0.33 bps / rebalance**，不够惊艳，但方向是对的。  
2. **只保留 leader shock top 20% 的 `5m` bars**，下一根 follower basket 反向收益提高到 **+0.53 bps**；若持有 **3 根 5m（=15m）**，升到 **+1.64 bps**，hit rate **53.9%**。  
3. **top 10% 更极端 shock** 没继续变强：`1-bar` **+0.58 bps**、`3-bar` **+1.43 bps**。说明这条线更像“高波动 pocket 里的扩散/回摆”，不是越极端越好。  
4. **`15m` 迁移直接翻负**：top 20% 的 `15m` leader shock 下，followers 反向做法反而是 **-1.45 bps**；top 10% 是 **-1.80 bps**。所以这条线当前应优先归档为 **5m raw alpha**，不是 15m 主策略。

## 3. 为什么和当前 desk 直接相关
- 它是 **raw alpha**，不是解释文。
- 它补的是当前更缺、也更值得持续扩充的 **relative-value / cross-sectional / stat-arb** 素材池。
- 它和最近已有的正向 leader-follower intake 最大区别在于：
  - 不是 `leader up -> follower 也 up`；
  - 而是 `leader shock -> follower 更容易 opposite move`。
- 这点对实盘拆解很重要：
  - 你不必再把所有 leader shock 都接成 trend / continuation；
  - 同一个事件 pocket，可以分成 **follow-through pocket** 和 **seesaw pocket** 两条互斥 raw alpha 线。

更具体地说，这条线最适合服务于：
1. **alt basket 相对值**：long/short followers；
2. **leader-vs-follower spread**：leader 只做 hedge，不必当 alpha 本体；
3. **现有正向 lead-lag 家族的 veto/branch selector**：同样是 BTC/ETH 冲击，哪些场景该追、哪些场景该反，不能永远只押一边。

## 3.5. 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / negative lead-lag
- 基础 alpha：large-cap leader shock 对 follower basket 的未来短周期收益有**反向**预测力
- regime：优先只在 `|leader 5m return|` 处于滚动高分位时开机
- filter / veto：
  - 只做高流动性、可稳定双边交易的 perp
  - 避开上新币、异常 funding、极端事件分钟
  - follower 篮子里剔除过度同质化或单币成交深度不足标的
- risk / sizing / execution overlay：
  - 第一版 followers 等权；第二版再测 inverse-vol
  - 单币权重上限、单侧 notional cap、单次事件最大风险预算
  - 优先 maker/TWAP，避免把本来就偏薄的 edge 全部交给 taker
- entry：
  1. 每根 `5m` 计算 leader composite：`ret_{BTC, t-1}` 与 `ret_{ETH, t-1}` 的等权平均
  2. 若 `|leader_ret|` 落在过去 `30d` 滚动样本 top 20%（首轮建议），生成信号
  3. 对 follower basket 做 `signal = -sign(leader_ret)`
  4. 第一版可直接等权做 basket；第二版再按历史 seesaw 系数排序，挑最强反应者
- exit：
  - 第一优先先测 **持有 3 根 5m（15 分钟）**
  - 对照组：`1 bar / 2 bars / 6 bars`

## 4. 可复刻的最小实验
### 数据源与公开性
- 数据源：Binance USDⓈ-M Futures Klines
- 公开性：公开可得，无需 API key
- 更新频率：`5m / 15m`
- 本轮 transfer-check universe：
  - leaders：`BTCUSDT`, `ETHUSDT`
  - followers：`SOLUSDT`, `XRPUSDT`, `DOGEUSDT`, `ADAUSDT`, `LINKUSDT`

### 第一版最小实验口径
- signal bar：`5m`
- predictor：`leader_prev = mean(ret_BTC, ret_ETH)_{t-1}`
- pocket：只保留 `abs(leader_prev)` 位于滚动样本 **top 20%** 的 bars
- portfolio A：followers 等权、方向为 `-sign(leader_prev)`
- portfolio B：`follower basket - leader basket` 的对冲 spread（用来验证 alpha 是否真的在 follower 腿）
- hold：`1 / 2 / 3 / 6` 根 `5m`
- 先看 4 个指标：
  1. `avg gross bps per rebalance`
  2. `hit rate`
  3. `best holding window`
  4. `follower-only vs spread hedge` 哪个更厚

### 这轮本地快检结果
#### 4.1 follower-only（近 90d, `5m`）
- all bars：**+0.33 bps / 1 bar**，hit rate **51.4%**
- top 20% leader shock：**+0.53 bps / 1 bar**，hit rate **52.9%**
- top 20% leader shock + hold 3 bars：**+1.64 bps / trade**，hit rate **53.9%**
- top 10% leader shock + hold 3 bars：**+1.43 bps / trade**，hit rate **53.5%**

#### 4.2 spread-hedged（`follower basket - leader basket`）
- top 20% leader shock + hold 3 bars：**+0.88 bps**
- 比 follower-only 明显更薄，说明这条 edge 当前更像 **followers 自身的反向 pocket**，而不是简单 leader-follower 配对就能放大。

#### 4.3 单币 follower（top 20% leader shock, hold 3 bars）
- `LINKUSDT`: **+2.13 bps**, hit **53.7%**
- `ADAUSDT`: **+2.04 bps**, hit **52.3%**
- `DOGEUSDT`: **+2.02 bps**, hit **54.2%**
- `XRPUSDT`: **+1.78 bps**, hit **54.6%**
- `SOLUSDT`: **+1.59 bps**, hit **53.0%**

#### 4.4 `15m` 为什么先不做
- all bars：**-0.33 bps / 1 bar**
- top 20% leader shock：**-1.45 bps / 1 bar**
- top 10% leader shock：**-1.80 bps / 1 bar**

这说明同一主题别硬泛化：**当前最诚实的 desk 读法是“5m 上有 pocket；15m 上先别装它活着”。**

## 5. 下一步怎么测
1. **把 equal-weight basket 升级成 ranking 版**：先用过去 `30d/45d` 的滚动回归或 LASSO，估每个 follower 对 leader shock 的 seesaw 系数，只做最强的 2~3 个币。  
2. **把 pocket 从纯 `|leader_ret|` 升级成 `leader shock × market breadth / funding / OI`**：这条线很可能只在“leader 抽血、小币承压”的 crowding 状态才最强。  
3. **分开测正 shock 与负 shock**：`BTC/ETH 大涨后 alt 回落` 与 `BTC/ETH 大跌后 alt 反抽` 很可能不对称，别继续混在一起。  
4. **测 execution honesty**：当前 `+1.64 bps` gross 仍偏薄，必须直接测 maker 参与率、盘口厚度、实际可成交滑点；否则只能先当 research alpha，不该急着升成 taker 策略。  
5. **和已有正向 lead-lag 家族做冲突测试**：同一 leader shock pocket，到底什么时候该做 `follow-through`，什么时候该做 `seesaw`，这是这条线真正的 desk 价值。

## 6. 风险与保留意见
- 论文侧我目前拿到的是 **摘要级证据**，足够确认“negative lead-lag + LASSO 策略 + cost 后仍显著”这三个主结论，但不够支撑更细的样本/参数细节；所以这篇 digest 必须诚实地写成 **摘要级论文 + 本地 transfer check**。  
- 本地快检说明这条线 **不是 taker 圣杯**：`5m top20 pocket + hold 3 bars` 只有 **+1.64 bps gross**，如果执行粗糙，很容易被吃掉。  
- 目前更像 **follower-only edge**，hedged spread 版并没有更强，所以别急着把它过度工程化。  
- `15m` 已经明显翻负，说明这条线不能被偷换成“适用于所有短周期”。当前应先锁定 **5m / 15m持有窗口** 的版本，而不是 `15m signal bar` 版本。

## 7. 来源
1. **Jia, Y., Wu, Y., Yan, S., & Liu, Y. (2023). _A seesaw effect in the cryptocurrency market: Understanding the return cross predictability of cryptocurrencies_. Journal of Empirical Finance, 74, 101428.**  
   - DOI: `10.1016/j.jempfin.2023.101428`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S0927539823000956`  
   - IDEAS/RePEc 摘要页: `https://ideas.repec.org/a/eee/empfin/v74y2023ics0927539823000956.html`  
   - Repo URL: `未见作者官方开源代码`
2. **Binance Developers. USDⓈ-M Futures API – Kline/Candlestick Data.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地产物
- `reports/artifacts/quant_digests/crypto_seesaw_20260326_1548/transfer_summary.csv`
- `reports/artifacts/quant_digests/crypto_seesaw_20260326_1548/per_follower_h3.csv`
- `reports/artifacts/quant_digests/crypto_seesaw_20260326_1548/meta.json`

## 9. 当前 verdict
**值得进研究池，而且应按 raw alpha 记账；但当前最诚实的版本不是“15m 大币带 alt 同向”，而是“5m large-cap shock 之后，优先去找 alt basket 的反向 seesaw pocket”。**
