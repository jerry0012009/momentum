# 别把 YoloBotV2 只读成“大而全 perp bot”：对 short-cycle desk，更该先测的是「crowded-long fragility × liquidation-unwind continuation」这条 raw alpha

- 时间：2026-04-13 19:13 UTC
- 类型：2026 GitHub repo source audit（`backend/core/fragility.py` + `backend/core/cascade_engine.py` + `backend/core/factor_scoring.py`）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题标签：raw-alpha/event-driven/positioning/fragility/liquidation/cascade/crowding/funding/open-interest/top-trader/continuation/exhaustion/bounce/btc/eth/sol/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：源码规则 + 一个月公共数据 portability probe + desk-level strategy reframing

- 主题类型：raw alpha
- 基础 alpha：**当市场处于“拥挤多头且脆弱”的状态时，第一次出现 `15m` 级别的价格下跌 + OI 同步下掉，往往不是普通回撤，而是 forced unwind 开始；其后续 `15m~60m` 更容易沿下行方向继续重定价。repo 里的 exhaustion / bounce 只是第二阶段，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = crowded-long fragility → liquidation-unwind continuation。**

不是“funding 高了就空”。
也不是“OI 高了就危险”。
更不是把 `fragility` 当成一个抽象风险分数挂在看板上。

这份 repo 真正适合 desk 拆出来的，是一条 **事件驱动 raw alpha**：

1. **先识别哪一边拥挤而脆弱；**
2. **再等第一脚 against-crowd move 把 forced unwind 真正打出来；**
3. **Phase B 先做顺着清算方向的 continuation；**
4. **Phase C / D 再考虑 exhaustion 和反打 bounce。**

翻成人话：
- 第一段赚的是 **拥挤仓位被迫平掉时的顺势延续**；
- 第二段才是 **瀑布末端的反抽**；
- 所以对 short-cycle desk，**最值得先测的是 continuation leg**，不是先去赌 knife-catch。

## 2. 这次看了什么

### 主来源（repo）
- **Author / Owner：** GitHub owner `uponly-trades`
- **Year：** 2026
- **Title：** *YoloBotV2*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/uponly-trades/YoloBotV2>
- **Repo URL：** <https://github.com/uponly-trades/YoloBotV2>
- **Repo 描述：** `Autonomous crypto perpetual futures trading bot with Nautilus-inspired strategy filters`
- **本轮观测到的最新提交时间：** `2026-04-14T01:30:22+07:00`（shallow clone 本地可见）

### 本轮直接审的关键文件
- `backend/core/fragility.py`
- `backend/core/cascade_engine.py`
- `backend/core/factor_scoring.py`

### 本轮自建 probe 产物
- 脚本：`reports/artifacts/quant_digests/2026-04-13_yolobot_fragility_cascade_probe.py`
- 汇总：`reports/artifacts/quant_digests/yolobot_fragility_cascade_probe_summary_2026-04-13.json`
- 明细：`reports/artifacts/quant_digests/yolobot_fragility_cascade_probe_detail_2026-04-13.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 表面看像“多策略 perp bot 拼装体”，但真正值得 desk 收下的，是 `fragility score → cascade state machine` 这条两阶段 event-driven raw alpha 壳；第一阶段先做 crowded-side unwind continuation，第二阶段再做 exhaustion bounce。**

### 一句话证明方式
> **证明不靠 README 口号，而靠源码结构本身：`fragility.py` 先把拥挤/脆弱方向状态化，`cascade_engine.py` 再把 Phase A/B/C/D/E 串成完整交易生命周期；我再用 Binance 公共 `funding + OI + top-trader ratio + 15m return` 做一个公开 proxy，得到 BTC/ETH 核心 lane 在近一个月 `12` 个事件里，事件后 `15m` 平均空头收益 `+5.96 bps`、事件后 `60m` 平均空头收益 `+14.29 bps`。**

## 4. 为什么这轮值得写，而不是继续补又一个 pairs / basis / OFI 题

因为它补的是当前池子里相对少的一类：

1. **它不是纯 overlay。**
   - `fragility` 虽然长得像风险分数；
   - 但 repo 实际把它接成了 **可独立交易的 event router**；
   - 真正的交易对象是“拥挤方向被迫 unwind 的后续价格路径”。

2. **它不是 funding alpha 的重复翻版。**
   - funding 在这里只是 crowding 因子之一；
   - alpha 本体不是吃 funding，而是吃 **forced unwind 带来的短时 drift**。

3. **它对 `5m/15m` desk 很自然。**
   - regime / factor 识别可以慢一点；
   - 但真正执行可以落到 `5m` 子腿；
   - 非常适合做 **event admission on 15m, execution on 5m** 的架构。

## 5. repo 真正提供了什么

## 5.1 `fragility.py`：不是温度计，而是“哪边先爆”的 pre-entry gate
`compute_fragility_score()` 把 7 类因子揉成一个 `0~100` 的脆弱度分数，并同时给出 `fragile_direction`：

1. `OI percentile`（最高给 `20` 分）
2. `Funding velocity / squeeze risk`（最高给 `15` 分）
3. `CVD divergence`（最高给 `15` 分）
4. `Bid depth decay`（最高给 `10` 分）
5. `Orderbook imbalance trend`（最高给 `10` 分）
6. `Whale pulse`（最高给 `5` 分）
7. `Volume climax`（最高给 `5` 分）

分层阈值：
- `>= 90`：`EXTREME`
- `>= 70`：`HIGH`
- `>= 50`：`MODERATE`
- `>= 30`：`ELEVATED`

关键不在“分数高低”，而在：
> **repo 明确在问“现在更脆的是多头还是空头”。**

这就已经不是 generic risk overlay 语言了，而是 **交易方向 admission 语言**。

## 5.2 `factor_scoring.py`：fragility 是刻意放在主方向投票之外的
这个文件很重要，因为它明确把系统拆成两层：

- 主方向投票：`MOMENTUM / TREND / VOLUME / STRUCTURE / DERIVATIVES`
- fragility-only 非投票指标：`liq cluster / bid depth decay / OB imbalance trend / volume climax ...`

翻成人话：
- 普通信号负责回答“应该偏多还是偏空”；
- `fragility` 负责回答“哪边会先被爆、有没有必要 override 原方向”。

对 desk 来说，这个拆法非常有价值，因为它允许你：
- 不改已有 trend / MR / OFI 模型；
- 单独新增一条 **crowding unwind 事件腿**。

## 5.3 `cascade_engine.py`：真正有价值的是 5-phase 生命周期，不是一个静态信号
repo 把 cascade 写成了一个状态机：

- **Phase A — PRE_CASCADE**：`fragility >= 90` 时启动
- **Phase B — CASCADE_ACTIVE**：regime 切到 `R5_ANOMALY / R6_CRISIS`
- **Phase C — EXHAUSTION**：`7` 个 exhaustion signal 里满足 `4+`
- **Phase D — BOUNCE**：`Supertrend reclaim` 或 `VWAP reclaim`
- **Phase E — NORMALIZING**：`fragility < 30` 且进入 `R4_REVERSAL`，或超时 `4h`

其中最有用的是 Phase B/C/D：

### Phase B：顺着 forced unwind 做 continuation
repo 注释里直接写了：
- `Cascade active (force-close fragile positions, trail shorts)`

如果脆弱的是多头，Phase B 的第一反应就是：
> **顺着下跌方向继续做。**

这就是本轮认为最该先测的 raw alpha leg。

### Phase C：exhaustion 不是拍脑袋，而是 7 选 4
源码里写的 7 个 exhaustion signal 包括：
1. `CVD reversal`
2. `Volume climax`
3. `Bid depth recovering`
4. `Funding stabilized`
5. `15m RSI extreme`
6. `Price stabilizing`
7. `Minimum cascade duration > 30 min`

这很像 desk 会接受的结构：
- 不要求单指标神奇翻转；
- 而是要求 **多证据拼图**。

### Phase D：bounce 触发比“抄底”严格得多
repo 不是说一看到跌狠了就反手，
而是要求：
- 先到 `EXHAUSTION`
- 再满足 `Supertrend reclaim OR VWAP reclaim`

也就是说：
> **repo 里真正可以迁移的不是“逢暴跌抄底”，而是“先做瀑布延续，再等结构 reclaim 做 bounce”。**

## 6. 我做的 Binance public-data portability probe：先测 continuation leg，不先赌 bounce

## 6.1 为什么只能做 proxy，而不是 1:1 复刻 repo
repo 的完整 `fragility` 需要：
- CVD divergence
- bid depth decay
- orderbook imbalance trend
- whale pulse
- volume climax

这些并不都能用一组简单公共历史接口无损复原。

所以本轮只做一个 **公开、低门槛、最小可复现 proxy**，专门近似 repo 的“多头脆弱并开始被打”这条支路：

- `fundingRate > 0`：多头付费，方向先验偏拥挤多头
- `|funding|` 位于近期高分位（`fund_abs_pct >= 0.6`）
- `openInterestValue` 位于近期高分位（`oi_value_pct >= 0.6`）
- `topLongShortPositionRatio` 位于近期高分位（`tls_pct >= 0.8`）
- 当根 `15m` 收益 `<= -0.20%`
- 当根 `15m` OI 变化 `<= -0.25%`

翻成人话：
> **先要求 crowding 明确存在，再要求“价格跌 + OI 掉”这脚 liquidation-style unwind 已经开始。**

## 6.2 数据与口径
- **数据源：** Binance USDⓈ-M public API
  - `/fapi/v1/klines`
  - `/futures/data/openInterestHist`
  - `/futures/data/topLongShortPositionRatio`
  - `/fapi/v1/fundingRate`
- **公开性：** 完全公开，无需 key
- **更新频率：** `15m` 可稳定更新；funding 为 `8h`
- **样本区间：** 约 `2026-03-13 19:15 UTC` 至 `2026-04-13 19:00 UTC`
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT`
- **最小实验：** 事件出现后，直接测下一根 `15m` 和后四根 `15m`（约 `60m`）空头收益

## 6.3 先记最重要的 5 个数

### 数 1：BTC 这条腿是最干净的
`BTCUSDT`：
- 事件数：`5`
- 事件后 `15m` 平均空头收益：`+10.76 bps`
- 事件后 `60m` 平均空头收益：`+21.13 bps`
- `15m / 60m` 胜率：都为 `80%`

这说明：
> **至少在 BTC 上，“crowded long + down bar + OI flush” 更像 cascade 开始，而不是已经跌完。**

### 数 2：ETH 也偏正，但没 BTC 干净
`ETHUSDT`：
- 事件数：`7`
- 事件后 `15m` 平均空头收益：`+2.54 bps`
- 事件后 `60m` 平均空头收益：`+9.40 bps`
- 胜率：`57.1% / 57.1%`

翻成人话：
- ETH 不是完全没用；
- 但它更像 **需要额外过滤** 的第二优先级标的，不能和 BTC 同等看待。

### 数 3：BTC+ETH 核心 lane 合并后仍是正的
把 `BTC + ETH` 合并看：
- 事件数：`12`
- 事件后 `15m` 平均空头收益：`+5.96 bps`
- 事件后 `60m` 平均空头收益：`+14.29 bps`

这很像一个 desk 可接受的第一版结论：
> **先别把它当“全市场全币通用”；但在 BTC/ETH 主流 perp 上，已经值得继续做第二轮更细的分层实验。**

### 数 4：SOL 太 sparse，不能现在就宣布可迁移
`SOLUSDT`：
- 事件数：`2`
- `15m` 空头收益均值是负的（`-10.27 bps`）
- `60m` 空头收益均值是正的（`+32.18 bps`）

这个结果最合理的读法不是“SOL 也行”，而是：
> **SOL 当前样本太少，暂时更像需要单独分 asset behavior 的第二阶段对象。**

### 数 5：这条线更像 `60m` 内 drift，而不是单根秒杀型信号
三资产合并：
- 总事件数：`14`
- 事件后 `15m` 平均空头收益：`+3.64 bps`
- 事件后 `60m` 平均空头收益：`+16.85 bps`

这意味着：
- 它不是那种只赌下一根的超高频点火；
- 更像 **事件触发后 `15m~60m` 的延续漂移**；
- 因此执行层更适合：
  - `15m` admission
  - `5m` child execution
  - `<= 60m` 的 hard time stop

## 7. 这条线对 short-cycle desk 的正确读法

## 7.1 它是 raw alpha，不是 regime/filter/overlay
因为它已经能独立回答：
- 什么时候进？
- 做多还是做空？
- 持有多久？
- 什么时候退出？
- 如何定义无效？

所以它不是“给别的 alpha 加一层 veto”那么简单。
它本身就是：
> **event-driven liquidation-continuation raw alpha**。

## 7.2 但它天然是“两段式”而不是“一把梭”
不要把 repo 读成一个单点信号。
更准确的 desk 拆法是：

1. **Continuation leg（优先）**
   - crowded side 开始 unwind
   - 先顺着做

2. **Bounce leg（次优先）**
   - 只有在 exhaustion + reclaim 后再反打

当前阶段，显然应先做第 1 条。

## 7.3 最像怎样的完整策略壳？
第一版 desk shell 我会这样写：

### Admission（15m）
满足以下同时成立时，允许开空：
- 正 funding 且处于相对高位
- OI 高分位
- top-trader position ratio 偏多高分位
- 当前 `15m` 跌幅达到阈值
- 当前 `15m` OI 同时明显下掉

### Entry（5m child）
- 事件 `15m` 收盘后，不直接追最后一秒；
- 在下一根 `5m`：
  - 若价格未明显反抽回事件 K 中位之上，则允许做空；
  - 若反抽过深，则降级或放弃。

### Exit
优先级：
1. `60m` hard timer
2. 价格重新站回事件 VWAP / 事件 K 中位之上
3. OI 停止继续下掉，且下一根出现明显反包

### Sizing
- 第一版建议单笔风险 `25~35 bps NAV`
- `BTC/ETH` 最多同向 `2` 笔
- 暂不把 `SOL` 放进第一批 live paper list

### Cost
- 这条线不是极薄 edge；
- 但 `15m` 端均值也没有豪华到可以无脑 taker 两边乱扫；
- 第一轮回测至少要压：
  - 单边 `2 bps / 4 bps / 6 bps`
  - maker/taker 混合成交

## 8. 这条线现在最大的风险是什么

### 风险 1：公共 proxy 只近似了 repo 的一半
当前 probe 没有复刻：
- CVD divergence
- bid-depth decay
- OB imbalance trend
- whale pulse

所以当前结果更像：
> **证明“这条原理值得测”，还不是证明“repo 全状态机已经可直接照抄上线”。**

### 风险 2：极端暴跌日容易把“已经跌完”混进来
明细里能看到某些 `2026-03-16` 的 BTC/ETH 事件，
事件后下一根并没有继续下，而是直接反抽。

这说明需要再加一层：
- **不要在 vol_z 极端过高且已经进入 panic endgame 时再追。**

换句话说：
- `fragility → cascade` 有用；
- 但 **“已经开始 unwind”** 和 **“已经 unwind 到尾声”** 之间，仍然要做 phase split。

### 风险 3：不同资产的 phase 长度并不一致
- BTC 更干净
- ETH 勉强可做第二梯队
- SOL 太 sparse

所以不要一开始就做“统一阈值全市场广播”。

## 9. 下一步怎么测（必须项）

### 9.1 先把 Phase B continuation 和 Phase D bounce 分开做标签
下一轮不要再把所有事件揉在一起。
至少拆成两套 label：

1. **Continuation label**
   - `t+1 / t+2 / t+4` 空头收益
2. **Exhaustion/bounce label**
   - 事件后是否出现 `VWAP reclaim / 15m RSI extreme / OI 停跌`
   - 再测反手多单收益

### 9.2 用更多公共因子逼近 repo 原版 `fragility`
下一轮建议补进：
- `takerlongshortRatio`
- `globalLongShortAccountRatio`
- `aggTrades` 近似 delta/CVD
- 深度快照的 bid/ask imbalance

目标不是炫技，而是把 repo 里 7 因子中的至少 5 个，用公共接口近似出来。

### 9.3 先只做 BTC/ETH，不急着推全市场
第一轮正式回测建议：
- 资产：`BTCUSDT / ETHUSDT`
- 事件框架：`15m admission + 5m execution`
- 持有：`15m / 30m / 60m` 三档
- 成本：`2/4/6 bps` 三档
- stop：`0.5 x 15m ATR` 与事件 K 高点二选一

### 9.4 加一个“尾声 veto”
最应该马上补的不是更多 fancy features，
而是一个简单 veto：

> **若事件 bar 的 `vol_z` 已经极端高，且下一根出现 OI 不再继续下掉，则不追 continuation，改等 bounce。**

这一步很可能直接决定这条线能不能从“研究有趣”变成“实盘可做”。

## 10. 最后的 desk 结论

如果只问一句“这轮该不该进素材池”，我的答案是：**该，而且优先级不低。**

但要把结论说准：

> **应进入素材池的，不是“YoloBotV2 全家桶”，而是其中 `crowded-side fragility → unwind continuation → exhaustion reclaim` 这条事件状态机。当前最值得先做的 leg 是 BTC/ETH 上的 continuation short；bounce leg 留到第二轮。**

一句话落地：
> **先把它当成 `15m` 事件 admission、`5m` 子执行的 liquidation-continuation raw alpha 去测；不要一上来就把它写成万能风险面板，也不要急着先赌末端反转。**
