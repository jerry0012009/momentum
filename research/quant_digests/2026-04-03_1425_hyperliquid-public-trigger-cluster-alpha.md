# Hyperliquid public-trigger-cluster cascade alpha

- 主题类型：raw alpha
- 基础 alpha：**公开可见的 whale trigger orders / liquidation prices 会把短线价格“拉”向簇密集区；当价格进入高密度 cluster 邻域并出现同向微冲击时，更值得先做朝 cluster 的 continuation，而不是先猜顶猜底。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

> 一句话先定性：这轮不把 2026 新 repo 的主叙事继续写成“funding + OI + liquidation 老三样”，而是把里面更适合我们 desk 的旁支单独拎出来——**用 Hyperliquid 公共 `frontendOpenOrders` + `clearinghouseState` 做可扫描的 stop / liquidation map，再交易“向 cluster 逼近时的短时级联 continuation”**。

## 1. 为什么这轮值得写

这轮它比再补一篇泛 breakout/filter 更值钱，原因很简单：

1. **base alpha 说得清**：公开 stop / liquidation cluster 不是纯背景噪音，而是短时 liquidity target；当价格已朝它移动时，后续 `1m/3m/5m` 往往先看“打到它”。
2. **数据公开可得**：Hyperliquid 官方 `info` endpoint 公开给出：
   - `frontendOpenOrders`：`isTrigger / orderType / triggerCondition / triggerPx`
   - `clearinghouseState`：持仓、杠杆、`liquidationPx`
   - `allMids` / `trades`：当前中间价与实时成交
3. **不是只能当 filter**：只要把 cluster 密度、距离、方向、时间窗和 cost 壳写清，它本身就是一条独立 event-driven raw alpha。
4. **时间尺度天然匹配 desk**：这不是日频链上慢变量；本质上是秒级/分钟级 stop-sweep 路径问题，天然属于 `1m/3m/5m`，`15m` 更像管理与二次确认层。

这也符合当前 intake 优先级：它不是纯解释，不是纯 overlay，而是一个**能直接下手做最小实验**的 raw alpha 候选。

---

## 2. 本次主源与证据类型

### 主源 A：2026 GitHub 新 repo（旁支想法的核心来源）
- **Author / Maintainer**: `wilsontiger2222`
- **Year**: 2026
- **Title**: *liquidation-hunter*
- **Venue / DOI**: GitHub repo / N.A.
- **Readable URL**: <https://github.com/wilsontiger2222/liquidation-hunter>
- **Repo URL**: <https://github.com/wilsontiger2222/liquidation-hunter>
- **GitHub metadata**:
  - created: `2026-02-08`
  - pushed: `2026-02-08`
  - description: `Liquidation cascade trading strategy for crypto perps`
- **本次重点审阅文件**:
  - `README.md`
  - `config.yaml`
  - `main.py`
  - `src/data/hyperliquid_client.py`
  - `src/data/positions.py`
  - `src/signals/liquidation_map.py`
  - `src/signals/signal_aggregator.py`
  - `tests/test_signal_aggregator.py`

### 主源 B：Hyperliquid 官方 API 文档（证明数据公开可扫）
- **Author**: Hyperliquid Docs
- **Year**: 2026 访问版本
- **Title**: *Info endpoint*
- **Venue / DOI**: Hyperliquid Docs / N.A.
- **Readable URL**: <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint>
- **关键公开字段**:
  - `openOrders`
  - `frontendOpenOrders`
  - `allMids`
- `frontendOpenOrders` 返回 `isTrigger / orderType / triggerCondition / triggerPx / reduceOnly`，足够拼 stop-map

### 主源 C：Hyperliquid 官方 WebSocket 文档（实时触发流入口）
- **Author**: Hyperliquid Docs
- **Year**: 2026 访问版本
- **Title**: *Websocket*
- **Venue / DOI**: Hyperliquid Docs / N.A.
- **Readable URL**: <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket>
- **用途**: 用 `wss://api.hyperliquid.xyz/ws` 订阅 `trades`，给 cluster touch / break / follow-through 做实时触发。

### 微观结构地基（为什么 stop-sweep 这类事件值得先测）
- **Easley, López de Prado, O’Hara (2012)**
- **Title**: *Flow toxicity and liquidity in a high-frequency world*
- **Venue**: *Review of Financial Studies*
- **DOI**: `10.1093/rfs/hhs053`
- **Readable URL**: <https://doi.org/10.1093/rfs/hhs053>

> 这篇不是直接讲 crypto stop-map，但它给了足够硬的地基：**当订单流已带方向性且流动性脆弱时，接下来短时价格并不“中性”，而是容易继续沿冲击方向走。** public stop/liq cluster 可以理解成把“脆弱位置”显式化了。

---

## 3. 这次不跟 repo headline，而是抽它更适合 desk 的旁支

repo headline 是 liquidation cascade strategy；但对我们更值钱的，其实是 README 里一句很关键的话：

- Hyperliquid 的 trigger orders（TP/SL）是**可查询**的
- 没有全市场聚合热力图，需要**按钱包逐个扫**
- 结合 `liquidationPx`、trigger orders、order book depth，可以自己建 map

这意味着：

> **真正可复现的不是“看现成 heatmap 猜方向”，而是自己扫描公开钱包 → 聚合 stop / liq cluster → 交易 cluster 附近的短时 path。**

这就从“可视化看板”升级成了可以编码的 raw alpha。

---

## 4. repo 里能直接迁移成策略骨架的部分

## 4.1 公共数据读取路径已经齐了

`src/data/hyperliquid_client.py` 明确封装了：

```python
{"type": "allMids"}
{"type": "clearinghouseState", "user": user}
{"type": "frontendOpenOrders", "user": user}
```

这三条已经足够做最小 stop-map：

1. `allMids` 给当前价
2. `clearinghouseState` 给仓位与 `liquidationPx`
3. `frontendOpenOrders` 给 trigger orders 的 `triggerPx`

换句话说，**公开 API 本身就支持把“谁会在什么价位被动出手”拼出来**。

## 4.2 liquidation cluster 的构造规则非常适合直接改写到 trigger cluster

`src/signals/liquidation_map.py` 的做法很直接：

- 把每个 `liquidation_price` 按 `bin_pct = 0.5%` 分箱
- 每箱累加 `volume` 与 `count`
- 计算 `distance_pct`
- 按 volume 排序，挑最近且最密的 cluster

信号强度：

```text
strength = 0.6 * distance_factor + 0.4 * volume_factor
```

方向定义也很清楚：

- 当前价下方的 long liquidation cluster → 更像向下 cascade → 做空
- 当前价上方的 short liquidation cluster → 更像向上 cascade → 做多

这个框架直接就能迁到 trigger-order map：

- `triggerPx` 替代 `liquidationPx`
- `origSz` / `sz` / reduceOnly / tpsl 类型做权重
- 同样用 bin、distance、density、direction 去打分

## 4.3 repo 的聚合器也已经给了完整方向壳

`src/signals/signal_aggregator.py`：

```python
WEIGHTS = {
    "funding": 0.35,
    "oi_divergence": 0.30,
    "liquidation": 0.35,
}
```

它把 funding / OI / liquidation 三条线合成一个 `direction + confidence + target_price`。

对我们更有用的不是照抄 35/30/35，而是看到：

> **cluster 本身完全可以做主信号，funding / OI 只负责 admission / veto / sizing。**

这点很重要，因为当前 desk 更需要 raw alpha，不该把所有 crowding 数据都写成 filter。

---

## 5. 这条 raw alpha 应该怎么落成完整策略

下面给一版适合 `1m/3m/5m/15m` 的**最小可交易版本**。

## 5.1 Universe

先只做：
- `BTC`
- `ETH`

原因：
- 公开 wallet / position / trigger 数据足够密
- 滑点相对可控
- cluster 被打穿后的 follow-through 更稳定

`SOL` 可以放二期。

## 5.2 数据与更新频率

### 公共数据源
1. **Hyperliquid Info API**
   - `frontendOpenOrders`
   - `clearinghouseState`
   - `allMids`
2. **Hyperliquid WebSocket**
   - `trades`
3. （可选）repo 原生的 funding / OI 路径

### 更新频率
- `trigger / liq map`：每 `30s` 扫一轮
- `trades`：实时
- bar 化：`1m`

## 5.3 Cluster 构造

### A. Trigger cluster
对每个 wallet 的 `frontendOpenOrders`：
- 仅保留 `isTrigger = true`
- 优先保留 `triggerCondition = sl`
- `tp` 单独记，不和 `sl` 混箱
- `triggerPx` 按 `0.25%` 或 `0.5%` 分箱
- 权重建议：
  - `w_notional = origSz * triggerPx`
  - `reduceOnly = true` 给予更高可信度
  - `sl` 权重大于 `tp`

### B. Liquidation cluster
对每个 wallet 的 `clearinghouseState`：
- 抽 `liquidationPx`
- 用 `marginUsed` 或 `abs(size) * liquidationPx` 近似体量
- 同样按 `0.25%` 或 `0.5%` 分箱

### C. 合成 public stress map
对每个 price bin：

```text
cluster_score
= 0.45 * stop_notional_z
+ 0.35 * liquidation_notional_z
+ 0.20 * address_count_z
```

再计算：
- `distance_pct`
- cluster 方向（上方 short-stop / short-liq；下方 long-stop / long-liq）
- 当前价到 cluster 的 gap

## 5.4 Entry：先做“向 cluster 的 continuation”，不先做 post-sweep fade

### Long entry
满足以下条件时开多：
1. 当前价上方 `0.3% ~ 1.2%` 内存在高分 cluster；
2. 该 cluster 方向对应 **shorts/short stops 会被挤爆**；
3. 最近 `3` 根 `1m` bar 至少 `2` 根收涨；
4. 最近 `1m` 主动买成交占优，或最新价重新站上最近 `3m` 局部高点；
5. 预期剩余空间 `gap_to_cluster >= 5 * roundtrip_cost`。

### Short entry
镜像：
1. 当前价下方 `0.3% ~ 1.2%` 内存在高分 cluster；
2. 该 cluster 对应 **longs/long stops 会被挤爆**；
3. 最近 `3` 根 `1m` bar 至少 `2` 根收跌；
4. 最新价跌破最近 `3m` 局部低点；
5. `gap_to_cluster >= 5 * roundtrip_cost`。

### Admission / veto（不是 alpha 本体）
- **Funding 同向加分**：拥挤方向若与 cluster path 一致，则放宽最小 cluster_score
- **OI 同向加分**：价格未大动但 OI 继续累积时，更容易形成脆弱堆积
- 若 funding / OI 明显反向，则降杠杆或跳过

## 5.5 Exit

### 主止盈
- 第一目标：`0.8 ~ 1.0 * gap_to_cluster`
- 若价格已实际触发 cluster（穿越 bin 中心后回到 bin 内），立即减仓 `50%`

### 剩余仓位
- 若触发后 `1m` follow-through 仍强，则剩余仓位改 trailing stop
- 若触发后第一根 `1m` bar 出现长反向 wick + 收回，则全部平仓

### 止损
取更紧者：
- `0.35 * gap_to_cluster`
- `0.8 * ATR(1m, 20)`

### Time stop
- `8~12` 分钟不打到 cluster，平仓
- `15m` 级别最多不超过 `1` 根 bar

## 5.6 Sizing

按 cluster 质量分三档：

- `top decile score`: 风险预算 `1.00R`
- `80~90 pct`: `0.70R`
- `70~80 pct`: `0.40R`

并加两条硬约束：
- 同一方向同一币同时仅 1 笔
- BTC 与 ETH 相关事件同时触发时，总风险不超过 `1.5R`

## 5.7 Cost

这条策略不能忽略 cost，因为它交易的是**剩余 gap**。

最小要求：

```text
expected_gap_bps >= 5 * roundtrip_cost_bps
```

其中 roundtrip cost 应含：
- taker fee
- 预估滑点
- stop-sweep 时段的冲击成本上浮

如果 cluster 离得太近但深度太薄，表面上“马上会打到”，实际上可能是**没有足够 alpha 去覆盖冲击成本**。

---

## 6. 为什么它和当前 short-cycle desk 直接相关

## 6.1 这不是形态派内循环

它服务的不是：
- breakout 图形本身
- RSI 超买超卖
- generic trend filter

而是：
- **公开可扫描的脆弱持仓/止损结构**
- **cluster 邻域的路径依赖**
- **分钟级 event-driven continuation**

所以它确实在扩充 raw alpha 素材池，而不是继续围绕固定形态打转。

## 6.2 1m / 3m / 5m / 15m 怎么用

- `1m`：主触发频率，最适合做 touch / break / follow-through
- `3m`：适合做 admission，减少假触发
- `5m`：适合做持仓管理和 cluster 打到后的确认
- `15m`：更适合风控限时，不适合拿来定义首触发

换句话说：

> **信号在 1m 生成，3m 做去噪，5m 做管理，15m 做 time cap。**

---

## 7. 公开 live probe：这条数据路真的能拉出来吗？

我做了一个极小的公共接口快检。

### Probe 口径
- 时间：`2026-04-03 14:19 UTC`
- 数据源：Hyperliquid 公共 `info` endpoint
- 钱包：repo `config.yaml` 里的 `13` 个示例 whale wallets
- 资产：`BTC / ETH / SOL`
- 拉取内容：
  - `frontendOpenOrders`
  - `clearinghouseState`
  - `allMids`

### 结果摘要
当前价：
- BTC `66,698.5`
- ETH `2,046.45`
- SOL `79.6825`

扫描结果：
- 一共拿到 `468` 行公开数据
- 活跃持仓数：`BTC 9 / ETH 7 / SOL 4`
- 带 `liquidationPx` 的持仓：`BTC 2 / ETH 4 / SOL 3`
- 扫到的 trigger orders：仅 `BTC 1` 笔，离现价约 `13.0%`
- 在 `1%` 邻域内：`BTC/ETH/SOL` 都**没有**密集 trigger / liq cluster

### 这说明什么
这不是坏消息，反而把最关键的瓶颈说透了：

1. **公共路径成立**：公开接口确实能取到仓位、清算价、trigger 字段。
2. **静态 13 钱包白名单太稀**：拿 repo 示例 wallet list 直接跑，不足以支撑高频 live alpha。
3. **真正该做的第一步不是“直接交易”，而是扩大 wallet discovery 层**：
   - 动态发现高活跃钱包
   - 滚动更新地址池
   - 再做 cluster 事件研究

对应 artifact：
- `reports/artifacts/quant_digests/hl_trigger_map_probe_20260403_1420/summary.json`
- `reports/artifacts/quant_digests/hl_trigger_map_probe_20260403_1420/wallet_summary.csv`
- `reports/artifacts/quant_digests/hl_trigger_map_probe_20260403_1420/details.csv`

---

## 8. 最小可复现实验（MVE）应该怎么做

这轮最诚实的 MVE 不是直接上实盘，而是先做**事件研究**。

## 8.1 数据面

连续采集 `7~14` 天：
- 每 `30s` 扫一次 `frontendOpenOrders` / `clearinghouseState`
- 实时订阅 `trades`
- 聚合到 `1m` bar

先只做 `BTC / ETH`。

## 8.2 事件定义

对每个 `1m`：
- 找最近的上方/下方 cluster
- 记录：
  - `distance_pct`
  - `cluster_score`
  - `address_count`
  - `stop_share` vs `liq_share`
  - 是否有 funding/OI 同向拥挤

定义 event：
- **approach event**：价格首次进入 cluster `1.0%` 邻域
- **touch event**：价格首次触达 bin 区间
- **breach event**：价格穿越 cluster 中心

## 8.3 评估指标

对每类 event 测：
- forward return：`1m / 3m / 5m / 15m`
- hit ratio：是否在 `N` 分钟内打到 cluster
- MAE / MFE
- 触发后第一根 bar 的 wick reversal 比例
- 按 `cluster_score` 分层后的单调性

## 8.4 先测哪两个版本

### Version A：pre-sweep continuation（主线）
- 交易“向 cluster 打过去”
- 重点看 `1m/3m/5m`

### Version B：post-sweep snapback（支线）
- 交易“打到后第一根失败 bar 的反抽/反弹”
- 重点看 `1m/3m`

我建议先做 A，因为 repo 原始 liquidation logic 本来就是 continuation 语义；B 可以等 A 的 cluster 数据积出来后再做。

---

## 9. 对当前 desk 的结论

这轮我会把它归档为：

- **主题类型**：`raw alpha`
- **alpha 家族**：`event-driven / relative-value-of-path / stress-cluster continuation`
- **更细标签**：`trigger-map / stop-sweep / liquidation / Hyperliquid / public-data`

最关键的判断是：

> **这不是“现成 heatmap 指哪打哪”的主观交易笔记，而是一条公开 API 足以支撑、能编码、能做事件研究、也能落成完整策略壳的 short-cycle raw alpha 候选。**

但也要诚实地补一句：

> **当前 repo 自带的 13 钱包白名单太稀，不能直接拿来 live trade；真正的 alpha 门槛在 wallet discovery，不在 cluster 打分公式本身。**

这个结论本身就很有价值——因为它告诉我们，下一步该把研发时间花在哪。

---

## 10. 下一步怎么测

按优先级只做三步：

1. **先补 wallet discovery**
   - 用 Hyperliquid 公共 `trades` / 排行榜 / 大额成交，动态生成 top active wallets
   - 不再依赖 repo 静态 13 钱包

2. **做 `BTC/ETH` 的 14 天 30s cluster replay**
   - 每 30s 重建 trigger / liq map
   - 产出 approach / touch / breach 事件表

3. **先跑 A 版主实验**
   - `pre-sweep continuation`
   - 频率：`1m` 触发
   - 持有：`1m/3m/5m` 优先，`15m` 仅作上限
   - admission：`cluster_score + distance + short-term impulse`

如果这三步做下来，`hit-to-cluster rate` 和 `forward 3m expectancy` 没有随 `cluster_score` 单调上升，这条线就不要再浪费时间；若单调性成立，再考虑把 funding/OI 接回来做 sizing/veto。
