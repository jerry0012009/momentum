# 别把 USDT depeg 只当 shared overlay：对 short-cycle desk，这篇 2025 JIMF 里更该单独拎出来先测的是「signed depeg × majors/alts 1h directional jump-follow-through」这条 event-driven raw alpha

- 时间：2026-04-10 19:44 UTC
- 类型：2025 *Journal of International Money and Finance* 开放获取全文 PDF + Binance spot / USDⓈ-M `5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**signed stablecoin depeg event alpha：当 USDT 明确跌破锚定（negative depeg）时，BTC/ETH/高流动 alts 在后续 `15m~1h` 更容易出现同向正跳与 follow-through；可先写成 one-sided long event book，而不是双向对称交易。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前只支持 **negative-depeg long sleeve**；`positive depeg -> short` 在公开代理上不成立，不应照抄）
- 主题标签：raw-alpha/event-driven/stablecoin/usdt/depeg/jump-follow-through/directional/asymmetric/btc/eth/sol/xrp/5m/15m/1h/paper/public-data/cost/risk
- 证据类型：论文全文 + public-data portability probe + 非 USDT 计价 sanity check

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = signed USDT depeg shock。**
> 更具体地说，不是“depeg 之后大家都先停机”，而是：
>
> **`USDT negative depeg（跌破 $1） -> majors / liquid alts 下一段更容易同向上跳`**。
>
> 所以这轮不把它读成 shared overlay，而是把论文里此前没单独展开的 **one-sided event-driven raw alpha branch** 拎出来。

## 1. 为什么这轮值得单独写，而不算 3/29 那篇 overlay 的简单重写
`2026-03-29_1458_usdt-depeg-jump-risk-shared-overlay.md` 已经把同一篇 paper 读成了：

- `jump-risk / cojump-risk` 的 shared gate
- 给 pairs / carry / mean reversion / breakout 做 size-down / veto

那条读法没问题，但它默认把 depeg 视为 **风险状态**。

这轮值得重新写，是因为同一篇 paper 其实还藏着一个对当前 desk 更紧迫的分支：

> **不是只有“要不要停”这个 overlay 问题，还有“事件后到底有没有可单独交易的方向性 raw alpha”这个问题。**

而这正好符合本轮优先级：

- 先补 raw alpha 素材池；
- 如果材料里本来同时包含 overlay 与 raw-alpha branch，优先拆 raw alpha 出来。

## 2. 这篇 paper 真正给出的方向信息，比“depeg 很危险”更强
主论文：

> **Baptiste Perez Riaza, Jean‑Yves Gnabo (2025)**  
> **From depegs to jumps: The role of stablecoin instabilities in crypto market dynamics**  
> *Journal of International Money and Finance*  
> DOI：`10.1016/j.jimonfin.2025.103339`  
> DOI URL：<https://doi.org/10.1016/j.jimonfin.2025.103339>  
> OA PDF：<https://researchportal.unamur.be/en/publications/from-depegs-to-jumps-the-role-of-stablecoin-instabilities-in-cryp>  
> 直链 PDF（本地镜像来源可读版本）：<https://pure.unamur.be/ws/files/112887849/Perez_Riaza_and_Gnabo_2025_.pdf>  
> Repo URL：未见官方复现仓库

这篇 paper 最常被摘走的是：

- depeg 后 jump probability 飙升
- depeg 后 cojump probability 飙升
- downward depeg 更危险

但如果把正文再往下看一层，**作者其实给了方向性的频数证据**。

### 2.1 论文里的 sign 线索，不该被忽略
论文 Table 4 直接写到：

- **positive depeg** 后，`5m` 内 BTC 正负跳次数大致均衡；但拉长到 `1h`，更偏向 **negative jumps**；
- **negative depeg** 后，不论看常规 jumps 还是 large jumps，BTC **positive jumps 比 negative jumps 更常见**。

论文原文给出的作者解释也很直白：

> 当 USDT 出现 **negative depeg** 时，可能反映资金从 Tether 向 Bitcoin 这类更 risky 的 crypto-assets 转移，因此既压低 Tether 价格，也抬高 BTC return。

翻成人话：

- **USDT 往下脱锚**，不是只能当“风险来了先别动”；
- 它还可能是 **risk capital 从稳定币挤向主币/山寨的事件触发器**；
- 这条线天然更像 **one-sided long event alpha**，而不是镜像的 long/short 对称系统。

## 3. 论文里最该拿来做 event book 的三组数字
### 3.1 先确认：depeg 后 jump 真的够强
论文 Table 6(b)（BTC jump probability, post-event windows）：

- `5m`：`26.16%` vs control `0.73%`，约 **35.94x**
- `15m`：`34.18%` vs `2.18%`，约 **15.65x**
- `1h`：`50.63%` vs `8.73%`，约 **5.80x**

这说明 event 本身不是弱噪音，而是能把后续 `5m~1h` 直接拉进 jump-prone regime。

### 3.2 再确认：downward / negative depeg 更值得交易
论文 Table 11（downward depeg for USDT）：

- `5m` BTC jump probability：`40.00%` vs `0.73%`，约 **54.87x**
- `1h` BTC jump probability：`65.00%` vs `8.75%`，约 **7.43x**
- `1h` market cojump probability：`42.50%` vs `5.71%`，约 **7.44x**

也就是说，**真正该写进 raw alpha 的，不是“任意 depeg”**，而是：

> **USDT downward / negative depeg 这条支路。**

### 3.3 方向也不是拍脑袋：negative depeg 更常跟着 positive BTC jumps
论文 Table 4：

- `negative depeg -> positive jumps` 的频数 **高于** `negative jumps`
- `positive depeg -> negative jumps` 只在拉长到 `1h` 时才更明显

所以对交易壳来说，更自然的写法不是：

- depeg 来了就猜上下

而是：

- **negative depeg：优先尝试 long sleeve**
- **positive depeg：先别急着 short，先当 overlay / secondary hypothesis**

## 4. 我做的 desk 化 public-data probe：先看这条 raw alpha 能不能独立站住
### 4.1 数据与最小实验口径
我用公开可得的数据做了一个最小 portability probe：

- stablecoin proxy：Binance spot `USDCUSDT`
  - 用 `USDT/USD ≈ 1 / USDCUSDT`
  - 定义 `depeg = 1 / USDCUSDT - 1`
- 事件：**fresh threshold entry**
  - `negative depeg`：`depeg < -10bps`
  - `positive depeg`：`depeg > +10bps`
  - 只在首次越阈时记事件，避免连续条形重复记数
- 执行标的：Binance USDⓈ-M `BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT`
- bar：`5m`
- 持有期：`5m / 15m / 1h`
- 执行：信号 bar 收盘确认，**下一根开盘入场**，持有固定 bars 后退出
- 样本窗：近约 `365d`
- 结果文件：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/stablecoin_depeg_jump_probe_summary_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/stablecoin_depeg_jump_probe_detail_2026-04-10.csv`

### 4.2 第一眼：真正能站住的是 `negative depeg long sleeve`
perp `1h` 结果最关键：

- `BTCUSDT`：`344` 次事件，平均 **`+0.35bps`**
- `ETHUSDT`：`344` 次事件，平均 **`+1.12bps`**
- `SOLUSDT`：`344` 次事件，平均 **`+5.01bps`**
- `XRPUSDT`：`344` 次事件，平均 **`+5.90bps`**
- **POOL**：`1376` 笔事件，平均 **`+3.09bps`**，胜率 **`52.1%`**

同一个 probe 里，`15m` 也偏正，但明显弱于 `1h`：

- **POOL `15m`**：平均 **`+0.84bps`**

这和论文“event 后 `1h` 方向更清楚”的读法是一致的：

> **它不是 1~2 根 bar 的 ultra-fast micro alpha，更像 `15m~1h` 的事件后续行。**

### 4.3 反过来，`positive depeg -> short` 在公开代理上不成立
同样的脚本里，`positive depeg short sleeve` 结果很差：

- **POOL `1h`**：平均 **`-7.64bps`**
- **POOL `15m`**：平均 **`-5.34bps`**
- **POOL `5m`**：平均 **`-5.07bps`**

也就是说：

> **论文里的“positive depeg 后 1h 更偏 negative jumps”这条，在 Binance 公共代理口径上没有成功迁移成可交易 short sleeve。**

这轮最重要的 desk 结论因此非常明确：

- **保留 negative-depeg long**
- **放弃把 positive-depeg short 当对称腿照抄**

## 5. 我又补了一层 sanity check：这不是纯 USDT 计价的机械涨幅
一个必须先排除的误判是：

> “你看到的只是 `BTCUSDT` 因为 USDT 变弱而机械上升，不是底层资产真的有 follow-through。”

所以我又看了 **非 USDT 计价现货对** 的 `1h` forward return：

- `BTCUSDC`：`344` 次事件，平均 **`+0.45bps`**
- `ETHUSDC`：`344` 次事件，平均 **`+1.20bps`**
- `XRPUSDC`：`344` 次事件，平均 **`+5.95bps`**
- `BTCFDUSD`：`344` 次事件，平均 **`+0.08bps`**
- `ETHFDUSD`：`344` 次事件，平均 **`+0.98bps`**
- `SOLFDUSD`：`344` 次事件，平均 **`+4.77bps`**

这说明：

- 事件后上涨 **不完全是 USDT 计价幻觉**；
- 至少在一部分主流币上，USDT negative depeg 的确对应了 broader crypto risk-on / squeeze / bid migration；
- 但强度在 `BTC/ETH` 上不算夸张，**更像 alt sleeve 强于 BTC sleeve**。

## 6. 这条 raw alpha 该怎么诚实地 desk 化
### 6.1 不要写成对称系统
当前证据只支持：

- **主策略：negative depeg -> long**
- **次策略：positive depeg 暂时只做风险层 / 不开反向 short**

所以壳子应该长这样：

1. 观测 `USDCUSDT`
2. 计算 `depeg = 1 / USDCUSDT - 1`
3. 当 `depeg < -threshold` 且是 fresh breach：触发事件
4. 做 `BTC/ETH/SOL/XRP` 中的 liquid sleeve
5. 固定 `15m~1h` time-stop 或 event decay exit

### 6.2 先把它写成 one-sided event shell，而不是全市场 shared gate
更具体的落地模板：

- **entry**：`USDT negative depeg <-10bps` fresh breach
- **execution**：下一根 bar 开盘做多；避免事件 bar 尾端抢价
- **hold**：先测 `3 / 6 / 12` bars（`15m / 30m / 1h`）
- **stop**：
  - 事件反向回 peg
  - 或标的单腿回撤超过 `0.75~1.0 ATR(5m)`
- **exit**：固定 time-stop + re-peg / momentum fail-fast 二选一
- **sizing**：`BTC/ETH` 低权重，`SOL/XRP` 仅在 liquidity pass 时上调
- **cost model**：maker / passive-first 与 taker 分开记账

### 6.3 这条 alpha 和 1m / 3m / 5m / 15m 的关系
- `1m / 3m`：适合做 **event detection 与更细的 execution routing**
- `5m`：适合做 **研究主频与事件定义**
- `15m`：适合做 **持有与再确认**

所以这条线不是“15m 主信号”，而是：

> **`5m` 事件触发 + `15m~1h` 持有的 event-driven directional alpha。**

## 7. 这条线现在的弱点也得写清楚
### 7.1 纯 taker 成本下，pool 级平均收益还不够漂亮
如果粗扣 `8bps` round-trip，当前 public probe 的 pooled `1h` 均值 **`+3.09bps`** 还不够。

这意味着：

- 不能把它写成“无脑每次都打”的独立大仓策略；
- 更像是 **稀疏事件单 + selective universe + 更低执行成本** 的 raw alpha 候选；
- 或者进一步只做 stronger sleeves（当前看更像 `SOL/XRP > ETH > BTC`）。

### 7.2 正向 depeg 这条 mirror leg 当前不诚实
尽管 paper 里有“positive depeg 更偏 negative jumps”的频数线索，但在这轮 public proxy 上，short sleeve 没迁移成功。

所以现在最不能做的事是：

> **为了让系统显得完整，就强行把它包装成 long/short 对称事件框架。**

### 7.3 stablecoin proxy 仍是代理，不是论文原始口径
论文用的是更广义 stablecoin USD 价格序列与 70-asset universe；这轮我用的是：

- `USDCUSDT` 作为 `USDT/USD` 代理
- Binance 单交易所标的

它足够回答“有没有可做的 raw branch”，但还不够回答最终 production 参数该怎么定。

## 8. 给当前项目最有价值的读法
这轮不是说“stablecoin depeg 不再是 overlay”，而是说：

- **同一篇材料里同时有 overlay branch 与 raw-alpha branch**；
- 之前已经写过 overlay；
- 当前更缺的是 **能独立复现的 event-driven raw alpha**；
- 而 paper 里最适合 desk 的新提法，其实是：

> **USDT negative depeg -> majors / liquid alts 的 one-sided directional follow-through。**

也因此，这轮主题类型我把它标成 **raw alpha**，而不是再重复写 shared overlay。

## 9. 下一步怎么测
这轮最该继续做的不是再扩写论文摘要，而是直接上 4 组 A/B：

### A. threshold sweep
- `10 / 15 / 20 / 30 bps` negative depeg 阈值
- 看更深 depeg 是否换来更高 `1h` per-event edge

### B. asset-side admission
- `BTC / ETH / SOL / XRP / ADA / DOGE`
- 先别默认全资产做
- 直接做 `asset × threshold × horizon` 排名

### C. execution split
- `signal-close -> next-open`
- `signal-close + maker wait`
- `signal-close + 1m VWAP entry`
- 分离“alpha 有无”与“吃不吃得下”

### D. overlay + alpha 联动
- raw branch：`negative depeg -> long sleeve`
- overlay branch：同一事件下，pairs / MR / carry 仍然 size-down
- 回答：**同一个 stablecoin shock，能不能同时驱动 directional book 和 risk book**

最小实验建议：

- bar：`5m`
- 持有：`15m / 30m / 1h`
- universe：`BTC / ETH / SOL / XRP / ADA / DOGE`
- 数据：Binance spot `USDCUSDT` + USDⓈ-M perp klines
- 成本：`2 / 4 / 8 bps` 三档
- 输出：
  - gross / net bps per event
  - win rate
  - max adverse excursion
  - event clustering sensitivity
  - per-asset contribution

## 10. 这轮一句话结论
**别把 USDT depeg 只留在 shared risk overlay 那层：对当前 short-cycle desk，更值得先落地的是 `USDT negative depeg -> liquid crypto 15m~1h one-sided long follow-through` 这条 event-driven raw alpha；但它现在只诚实支持 long sleeve，不支持对称 short sleeve。**

## 11. 来源
### 论文
1. Perez Riaza, B., & Gnabo, J.-Y. (2025). *From depegs to jumps: The role of stablecoin instabilities in crypto market dynamics*. *Journal of International Money and Finance*, 155, 103339.
   - DOI：`10.1016/j.jimonfin.2025.103339`
   - DOI URL：<https://doi.org/10.1016/j.jimonfin.2025.103339>
   - Readable URL：<https://researchportal.unamur.be/en/publications/from-depegs-to-jumps-the-role-of-stablecoin-instabilities-in-cryp>
   - OA PDF：<https://pure.unamur.be/ws/files/112887849/Perez_Riaza_and_Gnabo_2025_.pdf>
   - Repo URL：未见官方复现仓库

### 本地实验产物
- `/root/clawd/jerry/momentum/reports/artifacts/literature/stablecoin_depeg_jump_probe_summary_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/stablecoin_depeg_jump_probe_detail_2026-04-10.csv`
