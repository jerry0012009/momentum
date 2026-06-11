# 别把这份 2025 EquiLVN repo 只读成“低成交量节点提示器”：对 short-cycle desk，更该先测的是「midpoint-split dual-LVN range reversion」这条 raw alpha

- 时间：2026-04-13 09:40 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `trade-signal.py`）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题标签：raw-alpha/single-asset/mean-reversion/volume-profile/lvn/support-resistance/midpoint/range-reversion/market-zone/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：工程经验 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**先在 rolling 区间里用 `support / resistance / midpoint` 把价格分成上下两半，再分别找 lower-half 与 upper-half 的最薄成交节点（dual LVN）；当两侧“最薄点”的成交强弱不对称时，只做更占优的一侧，并在价格回到对应 LVN 时进场，赌它从薄区弹回到区间另一侧。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = “rolling range 内的 dual-LVN 条件化反打 / 区间穿越”。** 不是把 LVN 当 breakout 过滤器，也不是把 support/resistance 当静态画线，而是：**在一个近期区间里，先判断哪一侧的薄成交节点更值得信，然后只在价格回到那个薄区时反向押回区间。**

翻成人话：
- 先看最近一段价格活动，把它拆成一个可交易区间；
- 区间下半部找一个“最薄”的价格点，上半部也找一个；
- 两边薄区不一样时，说明市场更像在某一侧留出了更好的回弹/回落 pocket；
- 真正下注的不是“今天会不会突破”，而是**价格回到薄区后，会不会重新弹回区间内部甚至走到对侧边界。**

所以这条线不是 `filter / regime / overlay`。和 `2026-03-18_1048_lvn-poc-acceptance-gate.md` 那篇把 LVN 当 shared gate 的读法不一样，**这里的 LVN 本体就是 entry anchor，本身就是 raw alpha。**

## 2. 这次看了什么

### 主来源（repo）
- **Author：** Aakidul
- **Year：** 2025
- **Title：** *EquiLVN*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/Aakidul/EquiLVN>
- **Repo URL：** <https://github.com/Aakidul/EquiLVN>
- **关键文件：**
  - README：<https://github.com/Aakidul/EquiLVN/blob/main/README.md>
  - 策略脚本：<https://github.com/Aakidul/EquiLVN/blob/main/trade-signal.py>

这个 repo 的有用部分很集中：
- 只用公开 K 线；
- 先取最近窗口的 `support / resistance / midpoint`；
- 再按 `midpoint` 把样本拆成上下两半；
- lower-half 取最低 quote-volume 那根 bar 的高点当 `LVN1`；
- upper-half 取最低 quote-volume 那根 bar 的低点当 `LVN2`；
- 若 `zone1` 的最低成交量 **大于** `zone2` 的最低成交量，则给 `BULLISH`，反之给 `BEARISH`；
- `BULLISH` 就在 `LVN1` 附近做多，止损放 `support`，目标看 `resistance`；
- `BEARISH` 镜像处理。

### 地基参考（paper）
- **Authors：** Chan, Phoong, Cheng, Chen
- **Year：** 2022
- **Title：** *Support Resistance Levels towards Profitability in Intelligent Algorithmic Trading Models*
- **Venue：** *Mathematics*
- **DOI：** <https://doi.org/10.3390/math10203888>
- **Readable URL：** <https://www.mdpi.com/2227-7390/10/20/3888>
- **Repo URL：** N/A

这篇 paper 不是 LVN 论文，但它至少给了一个合理地基：**support / resistance 一类结构，不一定只能当主观画线，也可以被当成可工程化特征。** 对这份 repo 来说，paper 的作用不是“替 repo 背书”，而是提醒我们：**把区间结构写成机器可算对象，本身是值得研究的。**

### 本轮本地 artifacts
- Probe script：`reports/artifacts/quant_digests/2026-04-13_equilvn_probe.py`
- Probe metrics：`reports/artifacts/quant_digests/2026-04-13_equilvn_probe_metrics.csv`

## 3. 为什么这条分叉值得进当前研究池

它值得写，不是因为“又一个 volume profile 词条”，而是因为它补的是当前池子里比较缺的那一层：

1. **它把 LVN 从 gate 重新拉回 alpha 本体。**
   - 之前 desk 已经有一篇把 `LVN rejection + POC acceptance` 当 shared gate；
   - 但如果一直只把 LVN 当 gate，就会漏掉一个更朴素的问题：**LVN 自己能不能直接变成入场点？**

2. **它是 mean-reversion / range-reversion 候选，不是 trend 续行变体。**
   - 当前地图上 trend / breakout / confirmation 材料很多；
   - 这份 repo 给的是更偏 **range 内反打** 的 raw alpha 壳。

3. **它够便宜，能立刻做 `15m / 5m` 最小实验。**
   - 不需要 order book、链上数据或付费数据；
   - 只用 Binance public klines 就能先回答“有没有 gross pocket”。

4. **它有清楚的可拆解问题。**
   - 到底是 `dual-LVN` 有信息，还是目标设太远？
   - 到底 `15m` 能活，还是 `5m` 一压就碎？
   - 到底该退出到 `midpoint`，还是非要去对侧边界？

## 4. repo 真正提供了什么，哪些地方还不够干净

### 4.1 值得偷的骨架
最值得保留的，是这 4 步：

1. **用 rolling window 定义局部区间**
   - `support = min(low)`
   - `resistance = max(high)`
   - `midpoint = (support + resistance) / 2`

2. **按 `midpoint` 切上下两个 market zone**
   - lower-half：收盘落在 `support ~ midpoint`
   - upper-half：收盘落在 `midpoint ~ resistance`

3. **每边各拿一个“最薄成交点”**
   - `LVN1 = lower-half` 里 quote-volume 最小那根的 `high`
   - `LVN2 = upper-half` 里 quote-volume 最小那根的 `low`

4. **只做占优的一侧**
   - 若 lower-half 的最小成交量反而大于 upper-half 的最小成交量，repo 记为 `BULLISH`；
   - 反之为 `BEARISH`；
   - 然后在对应 LVN 给 entry，止损放区间边界，目标看区间另一端。

这已经足够组成一个最小 raw alpha shell。

### 4.2 目前不够干净的地方
但如果把它直接当“可上线完整策略”，问题很多：

1. **LVN 定义还太粗。**
   - 它不是严格 volume-profile bin；
   - 只是拿一根最低 quote-volume bar 直接当节点；
   - 这在噪声大的 `5m` 上很容易不稳。

2. **entry timing 没写清楚。**
   - 脚本只打印“现在该做多/做空”；
   - 没明确说明是触碰就进、收盘确认再进，还是下一根开盘进。

3. **exit 太贪。**
   - 目标直接看到 `resistance` / `support`；
   - 对短周期来说，这更像“想吃完整个区间”，而不是先吃最有把握的半程。

4. **没有成本与 time-stop。**
   - `15m` 可以勉强先看 gross；
   - `5m` 若没有 maker 优势或更早退出，几乎一定被成本吃掉。

所以对我们来说，正确读法不是“抄 repo 的一键信号”，而是：

> **抄它的 `midpoint-split dual-LVN` 结构，不抄它未经验证的执行细节。**

## 5. public-data portability probe：这条 raw alpha 壳在今天的 Binance `15m/5m` 上像不像真的？

### 5.1 probe 口径
我这轮没有直接宣称完整回测，而是先做一个很轻的 portability probe：

- **市场：** Binance USDⓈ-M Perpetual
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT`
- **频率：** `15m` 与 `5m`
- **窗口：** 按 repo 建议，`15m -> 35 bars`，`5m -> 75 bars`
- **入场近似：** 若当前 bar 触到对应 `LVN`，视为该 bar 成交进场
- **出场：**
  - `15m` 最多持有 `12` bars（约 `3h`）
  - `5m` 最多持有 `24` bars（约 `2h`）
  - 期间先 hit `target` / `stop` 就提前退出
  - 否则按 horizon 末尾 close 记 timeout
- **执行：** `no-overlap`，只做最小 gross probe，不含 fee / slippage / funding

这不是为了给出“最终可交易 PnL”，而是先回答：
1. 触发密度够不够？
2. 是不是至少有一个 symbol / timeframe 看起来有 gross pocket？
3. 它更像 `15m` 还是 `5m`？

## 6. 关键结果：`15m ETH` 有 pocket，但 repo 原版“打到区间另一侧” exit 太贪，`5m` 普遍不干净

### 6.1 三个最值得记的数

#### `ETHUSDT 15m`
- **`235` 笔** no-overlap 触发
- 平均 **`+10.76 bps gross / trade`**
- `target hit` **`23.4%`**、`stop hit` **`28.9%`**、`timeout` **`47.7%`**

这说明两件事：
- 这条壳在 `15m ETH` 上**不是完全瞎的**；
- 但近一半单子都 timeout，说明 **“直奔对侧边界”太贪**，更像是信号方向有一点信息，exit 设计却拖后腿。

#### `BTCUSDT 15m`
- **`239` 笔**触发
- 平均 **`+1.82 bps gross / trade`**
- `timeout` **`53.1%`**

这更像：
- 结构上能触发很多次；
- 但 edge 很薄，几乎一压成本就没了。

#### `SOLUSDT 5m`
- **`281` 笔**触发
- 平均 **`-1.19 bps gross / trade`**
- `stop hit` **`35.9%`**

这说明 repo 这套最原始写法，到了更快的 `5m` 噪声层，**已经开始明显碎掉。**

### 6.2 5m 的总体结论
`5m` 三个标的里：
- `BTCUSDT`：**`+2.95 bps gross`**
- `ETHUSDT`：**`+2.64 bps gross`**
- `SOLUSDT`：**`-1.19 bps gross`**

问题在于：
- `target hit` 只有 **`12%~15%`**；
- `timeout` 却高达 **`49%~59%`**；
- 这意味着即使 gross 不是全负，**也完全不够覆盖短周期 taker 成本。**

所以这条线当前更像：
- **`15m` = 先研究 alpha 本体**
- **`5m` = 后续只用来做更细执行，不适合直接照抄 repo 当主信号层**

## 7. 这条线对当前 desk 的真正价值，不是“原版能直接赚钱”，而是它暴露了一个更对的实验方向

我对这条线现在的判断是：

> **dual-LVN 本身可能有一点 range-location 信息，但 repo 原版把 target 设到区间另一侧，导致 hit-rate 太低、timeout 太高，最后把 alpha 本体和 exit 贪婪混在了一起。**

换句话说，当前 probe 更像证明了：
- `entry anchor` 可能是有料的；
- 但 `full-range traversal` 这个出场假设太重；
- 真正下一轮该先测的，不是“再换 20 个 symbol”，而是**先把 exit 和 veto 拆开。**

## 8. 策略拆解（必填）

- 方向属性：single-asset / mean-reversion / range-reversion
- 基础 alpha：`midpoint-split dual-LVN` 的薄区反打
- regime：先限定为 liquid majors / majors-like perp，优先 `15m`
- filter / veto：可加 `range_width / ATR` 过滤、连续单边趋势 veto、极端窄区间 veto
- risk / sizing / execution overlay：固定风险预算；next-bar open 或限价挂回 LVN；必须有 time-stop；成本先压 `6 / 10 / 15 bps per side`

## 9. 跟当前短周期 desk 的关系

这条线最适合放进：
- **raw alpha 素材池**，尤其是 mean-reversion / range-reversion 侧；
- 不是再做一个 shared gate；
- 也不是把外部数据硬塞成方向判断。

更具体地说，它非常适合做成：
- **`15m` 信号层**：决定“这个局部区间值不值得反打”
- **`5m` 执行层**：决定“回到 LVN 后是立刻进，还是等 micro fail / micro reclaim 再进”

这就和当前主线里很多 `15m` trend / breakout 模块形成互补：
- 那些是在追 continuation；
- 这条是在抓 **range 内的薄区反打 pocket**。

## 10. 下一步怎么测（必须项）

下一轮别先扩 universe，先把下面 `4` 个最值钱的问题测清楚：

1. **先拆 exit，不要先换 alpha**
   - 固定同一套 dual-LVN entry；
   - 比较三种退出：
     - `midpoint` 退出
     - `opposite LVN` 退出
     - repo 原版 `full boundary` 退出
   - 先看哪个在 `15m ETH / BTC` 上 post-cost 最诚实。

2. **给它 time-stop 与 range 宽度过滤**
   - 当前 timeout 太高，第一版建议：
     - `15m` time-stop 先测 `4 / 8 / 12` bars
     - `range_width / ATR` 过小不做（没肉），过大也不做（像趋势展开而不是区间）

3. **把 LVN 从“单根最低量 bar”升级成真正的 price-bin 节点**
   - 现在的定义太脆；
   - 下一轮应至少改成 rolling price bins 或简化 volume profile histogram；
   - 这能回答：当前 edge 来自 LVN 概念，还是来自偶然的单根低量 bar。

4. **成本与挂单可达性**
   - 先压 `6 / 10 / 15 bps per side`；
   - 再比较：
     - `touch LVN taker`
     - `pre-place maker near LVN`
     - `触碰后等一根 confirm 再 taker`
   - 这个问题不回答，就没法判断它到底是 alpha 还是 execution 幻觉。

## 11. 风险与保留意见

- repo 本身非常轻量，不能把它误读成成熟 volume-profile 系统；
- 当前 probe 对 entry 做了“当 bar 触到 LVN 就视为成交”的近似，真实可成交性还要单独验证；
- 结果只看 gross，不含费用、滑点、资金费率；
- `ETH 15m` 的 **`+10.76 bps gross / trade`** 看起来有点意思，但 round-trip 一压成本就可能只剩很薄；
- 所以这条线当前更像 **raw alpha 候选**，不是“已经可上线的完整策略”。

## 12. 一句话结论

> 这份 2025 `EquiLVN` repo 真正值得 short-cycle desk 接的，不是“又一个支撑阻力信号器”，而是它把 **LVN 直接当 entry anchor** 的思路：`midpoint-split dual-LVN` 确实有希望形成一条 `15m` 的 range-reversion raw alpha。当前 Binance public probe 里，`ETHUSDT 15m` 有 **`235` 笔**触发、平均约 **`+10.76 bps gross / trade`**，但接近一半单子 timeout，说明真正该优化的是 **exit 与执行层**，而不是继续把 LVN 只当 shared gate。

## 13. 本轮产物

- 研究笔记：`research/quant_digests/2026-04-13_0940_midpoint-split-dual-lvn-range-reversion-alpha.md`
- Probe script：`reports/artifacts/quant_digests/2026-04-13_equilvn_probe.py`
- Probe metrics：`reports/artifacts/quant_digests/2026-04-13_equilvn_probe_metrics.csv`

## 14. 来源

1. **Aakidul (2025). _EquiLVN_. GitHub repository.**
   - Repo URL：<https://github.com/Aakidul/EquiLVN>
   - README：<https://github.com/Aakidul/EquiLVN/blob/main/README.md>
   - Script：<https://github.com/Aakidul/EquiLVN/blob/main/trade-signal.py>

2. **Chan, J. Y.-L., Phoong, S. W., Cheng, W. K., & Chen, Y.-L. (2022). _Support Resistance Levels towards Profitability in Intelligent Algorithmic Trading Models_. Mathematics, 10(20), 3888.**
   - DOI：<https://doi.org/10.3390/math10203888>
   - Readable URL：<https://www.mdpi.com/2227-7390/10/20/3888>

3. **Binance USDⓈ-M Futures Public API**（本轮 portability probe 实际使用）
   - Kline / Candlestick Data：<https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
