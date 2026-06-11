# 别把 queue pressure 只读成静态 OBI：对 short-cycle desk，更该先测的是「one-sided depth depletion × slow refill → 同向短漂移」这条 microstructure raw alpha

- 时间：2026-04-18 01:46 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/mm_live/signals/imbalance.py` + `src/mm_live/signals/microprice.py`）+ 2026 Preprints 论文 branch read（`Within-Venue Monitoring of BTC/USDT Liquidity and Resiliency on Binance: A Queueing-Theoretic Framework`）+ Binance Spot 公共深度 `1s` live probe（`BTCUSDT` / `ETHUSDT`，top20，约 210s）
- 主题类型：raw alpha
- 基础 alpha：**当买一侧或卖一侧近端深度被明显打薄，而且 2~3 秒内没有快速补回，这往往不是“噪声扫一下就结束”，而更像冲击还没消化完；价格随后几秒更容易继续朝被打薄那一侧漂移。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / microstructure / queue-pressure / depth-depletion / refill / resiliency / continuation / maker-taker / binance / btc / eth / 1m / 3m / 5m
- 证据类型：repo 信号结构 + 论文机制框架 + live public-data sanity probe

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha 不是“OBI 大就追”这种静态厚薄判断，而是更动态的一句：`one-sided queue depletion that does not refill quickly -> same-direction short-horizon drift`。**

翻成人话：
- 如果买盘近端深度突然被打掉一截，说明下方托单被吃掉了；
- 若随后几秒挂单没有迅速补回来，说明这一下冲击没有被市场立刻吸收；
- 这时价格更容易继续往下挪；
- 卖盘侧同理，卖一附近深度被打薄且补得慢，则价格更容易继续往上挪。

这条东西仍然属于 **raw alpha**，不是单纯 filter。因为你可以直接拿它定义方向、进场、持有窗口和退出条件。只是它天然更适合和 maker/taker 执行壳绑在一起。

## 2. 这次看的两份主材料，分别提供了什么

### 2.1 repo：把“静态 queue pressure”拆得很清楚
主仓延续昨天那条高信号 2026 repo：

- **Author / Maintainer：** Aliipou  
- **Year：** 2026  
- **Title：** *mm-live*  
- **Venue：** GitHub repo  
- **Readable URL：** <https://github.com/Aliipou/mm-live>  
- **Repo URL：** <https://github.com/Aliipou/mm-live>

repo 里最核心的是两层：
- `microprice.py`：把买一/卖一队列厚薄翻译成一个更接近“真实短时公允价”的价格；
- `imbalance.py`：把 top-N 深度不平衡做成更平滑的 pressure signal。

昨天那条 digest 已经把它读成：
`microprice deviation × imbalance consensus -> short drift`

但 repo 继续往前推一步，其实会自然得到一个更交易化的问题：

> **如果 queue pressure 不是静态偏移，而是先发生“某一侧被打薄”的瞬时冲击，那么后面最该看的不是 OBI 当下有多大，而是“补单快不快”。**

也就是说，repo 给了 `pressure` 的观测层；而我这轮更想保留的是它的 **动态分叉版**：
- **快速补回**：更像虚惊一场，directional edge 要降级；
- **慢补 / 不补**：更像冲击残留，继续漂移概率更高。

### 2.2 paper：把“补不补得回来”这件事变成可量化的韧性问题
第二份材料是：

- **Authors：** Kyle Braughton, Matthew Bartholomew  
- **Year：** 2026  
- **Title：** *Within-Venue Monitoring of BTC/USDT Liquidity and Resiliency on Binance: A Queueing-Theoretic Framework*  
- **Venue：** Preprints  
- **DOI：** `10.20944/preprints202604.0256.v1`  
- **Readable URL：** `https://www.preprints.org/manuscript/202604.0256/v1`

这篇 paper 上一轮我更偏向把它归到 **regime / router**：它讲的是 venue fragility、impact 强度、resiliency 速度，不直接给你方向。

但如果把它和上面的 repo 接起来，desk 化后会出现一个更具体的分叉：

> **静态 fragility 更像“今天市场脆不脆”；而单次 queue depletion 后的 refill speed，更像“这一脚冲击还会不会延续”。**

换句话说：
- paper 给的是**韧性语言**；
- repo 给的是**微观信号接口**；
- 两者拼起来后，更像一条可直接做 ultra-short entry 的 raw alpha。

## 3. 这条 alpha 怎么落成完整策略壳

### 3.1 方向定义
- **bid-side depletion**：top1 或 top5 bid depth 相对上一个采样点显著下跳，且 ask 侧没有同步被打薄  
  → 看空 / 少接飞刀
- **ask-side depletion**：top1 或 top5 ask depth 显著下跳，且 bid 侧没有同步被打薄  
  → 看多 / 少在上方继续挂空

### 3.2 关键确认：不是“被打薄”本身，而是“补得慢”
可直接用一个很土但很实用的定义：
- 事件时刻记为 `t0`
- 近端深度损失量记为 `lost_depth`
- 看 `t0+1s ~ t0+3s` 内最多补回多少
- `refill_ratio = recovered_depth / lost_depth`

再分三档：
- `slow_refill <= 0.3`
- `mid_refill 0.3~0.7`
- `fast_refill >= 0.7`

我的 desk 读法：
- **slow_refill**：允许做 continuation
- **fast_refill**：不给 directional admission，甚至可当 veto
- **mid_refill**：只减仓做，或者要求 microprice/imbalance 再同向确认

### 3.3 一个最小可执行壳
以 `1s` 事件为底层，聚合到 `1m / 3m` 执行也可以：

**Entry**
- 监控 `top5` depth
- 若某侧深度单秒跌幅 `<= -15%`，且另一侧跌幅 `> -5%`
- 再要求 `refill_ratio_3s <= 0.3`
- 同时 `microprice deviation` 与 depletion 方向一致
- 则在 `t0+3s` 附近入场，做 `3s / 5s / 8s` 超短 continuation，或将事件强度聚合成 `1m` bar 内的 directional pressure 分数

**Exit**
- 固定持有 `5~10s`；
- 或一旦 opposite-side queue 反向 depletion；
- 或 `refill_ratio` 后续跃升到 `> 0.7` 立刻走。

**Sizing**
- 按 `lost_depth / local_depth`、事件前 30s 波动、spread 宽度做分层；
- 单事件只给小仓，允许事件簇叠加，但要设总库存上限。

**Risk / Cost**
- 这类 alpha 天然怕：撮合延迟、排队失败、价差回吐；
- 若不能在亚秒级/几秒级拿到流数据和执行回报，最好先当 **maker-skew bias** 或 **execution veto** 用，而不是纯 taker 追单。

## 4. 我补的 Binance 公共 depth 快检

### 4.1 数据源、公开性、更新频率、最小实验口径
- **数据源：** Binance Spot `api/v3/depth`
- **公开性：** 完全公开可得
- **更新频率：** 本轮按 `1s` 轮询
- **标的：** `BTCUSDT`、`ETHUSDT`
- **深度口径：** `top20` 抓取，计算 `top5 bid/ask qty`
- **样本时长：** 约 `210s`
- **最小事件定义：**
  - 某侧 `top5 depth` 单秒跌幅 `<= -15%`
  - 对侧同秒跌幅 `> -5%`
  - 未来 `3s` 计算 `refill_ratio`
  - 观察未来 `3s / 5s / 8s` 的 signed mid return
- **artifact：**
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_queue_refill_probe_summary.json`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_queue_refill_probe_events.json`

### 4.2 先看最粗结论
总共抓到 **139** 个单侧 depletion 事件。把收益统一按“depletion 指向的 continuation 方向”签名后：
- **全部事件平均 signed return：**
  - `3s`: **+0.25 bps**
  - `5s`: **+0.33 bps**
  - `8s`: **+0.42 bps**

翻成人话：
> **只看“某侧突然变薄”本身，就已经不是完全随机；至少在这轮 live probe 里，它后面几秒更偏向继续往被打薄那边漂。**

### 4.3 更关键：慢补比快补更像 continuation
#### bid-side depletion（买盘被打薄 → 看下）
- `slow_refill`（30 例）
  - `5s`: **+0.68 bps**
  - `8s`: **+0.82 bps**
- `fast_refill`（32 例）
  - `5s`: **+0.33 bps**
  - `8s`: **+0.37 bps**

这组最干净：
> **买盘被打薄后，如果几秒内补不回来，向下 continuation 大约是快补情形的 2 倍。**

#### ask-side depletion（卖盘被打薄 → 看上）
- `slow_refill`（36 例）
  - `5s`: **+0.20 bps**
  - `8s`: **+0.52 bps**
- `fast_refill`（29 例）
  - `5s`: **+0.12 bps**
  - `8s`: **-0.07 bps**

这组更 noisy，但方向上仍能读成：
> **卖盘被打薄后，若补单很快，向上 edge 会明显衰减；到 `8s` 口径甚至被反向吃掉。**

### 4.4 我对这些数字的 desk 解读
这轮快检不能证明“直接上线就能赚钱”，但已经够回答一个更关键的问题：

> **这条东西至少不是空想。队列被打薄以后，‘补不补得回来’这件事，确实在几秒尺度上携带了方向信息。**

而且它比静态 OBI 更像一个能直接交易的事件型信号：
- **静态 OBI**：像“现在书偏哪边”；
- **depletion + refill**：像“刚刚挨了一脚，这脚还没缓过来没”。

对超短执行来说，后者通常更接近真正的 entry trigger。

## 5. 为什么我认为它值得进当前素材池

### 5.1 它直接补的是 raw alpha，不是又写一个解释层
最近很多材料容易滑向：
- regime
- router
- execution caution
- market-quality 注释

这些都重要，但如果本轮目标是补 **raw alpha 素材池**，那么这条更合格，因为它能直接回答：
- **什么时候做多 / 做空？**
- **拿多久？**
- **什么情况下立刻撤退？**

### 5.2 它和已有 microprice / OBI digest 不是一回事
已有 digest 更偏：
- `microprice deviation`
- `top-book imbalance`
- `fair value shift`

而这条强调的是：
- **事件发生时的 queue shock**
- **shock 后的 refill speed**

前者像“静态偏置”，后者像“动态冲击延续”。两者可以一起用，但不是同一条主题的换皮。

### 5.3 它能自然服务 1m / 3m / 5m
虽然底层是秒级事件，但并不意味着只能做 HFT：
- 把 `1s` depletion 事件聚合成 `1m pressure score`，可服务 `1m/3m` directional entry；
- 把它当 `5m` bar 内的 microstructure confirm，也能服务更慢一点的 continuation / breakout sleeve；
- 若连续出现 opposite-side depletion，可以反过来当 **fade veto**。

## 6. 主要保留意见
- **样本很短。** 这轮只有约 `210s` live probe，更多是 sanity check，不是稳定性证明。
- **公开 REST 轮询太粗。** 真要做 production，必须换 WebSocket depth diff，而不是 `1s` HTTP poll。
- **成本门槛还没过。** 这轮看到的是 `0.2~0.8 bps` 级别的超短 edge，若用 taker 追，很容易被手续费和排队失败吃掉。
- **更适合先做 maker/taker 混合壳。** 最现实的第一步不是全 taker directional trade，而是：
  - depletion 慢补时，把顺势那一边 quote 挂近一点；
  - fast refill 时撤掉 directional bias。

## 7. 下一步怎么测

### 7.1 先做一个更像样的最小复现
- 改成 **Binance WebSocket depth diff**，至少拿 `30~60` 分钟连续样本；
- 标的扩到 `BTCUSDT / ETHUSDT / SOLUSDT`；
- 同时记录：
  - top1 / top5 / top10 depletion
  - refill ratio at `1s / 3s / 5s`
  - microprice deviation
  - spread / realized vol

### 7.2 做 3 个最小壳对照
1. **pure taker continuation**：事件后直接追，持有 `3s/5s/8s`
2. **maker-skew shell**：只调整 quote skew，不主动追单
3. **router-only**：给现有 OBI / microprice alpha 做 allow / veto

重点比较：
- gross bps
- fee 后 bps
- adverse selection
- fill ratio

### 7.3 真正决定它能否留下来的，不是 IC，而是成本后生存性
最该先问的不是“它有没有方向性”，而是：

> **在 maker/taker 不同执行假设下，这条事件信号能不能留下正的 fee-after edge？**

如果答案是：
- taker 死、maker 活 → 它应归到 **maker shell alpha**
- 两边都活 → 可升级成独立 ultra-short sleeve
- 两边都死 → 留作 execution veto，不再当主 alpha

## 8. 来源
1. **Aliipou (2026)**, *mm-live*，GitHub repo  
   - Readable URL: <https://github.com/Aliipou/mm-live>
2. **Kyle Braughton, Matthew Bartholomew (2026)**, *Within-Venue Monitoring of BTC/USDT Liquidity and Resiliency on Binance: A Queueing-Theoretic Framework*, Preprints  
   - DOI: `10.20944/preprints202604.0256.v1`  
   - Readable URL: `https://www.preprints.org/manuscript/202604.0256/v1`
