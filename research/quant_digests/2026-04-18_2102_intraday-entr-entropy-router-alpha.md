# intraday EntR（return / entropy）cross-section：别把它只当组合筛股指标，更该先问它能不能当短周期 raw alpha router

- 时间：2026-04-18 21:02 UTC
- 类型：paper full-text read + Binance public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：过去一段时间里，**近期收益更强、但路径更“有序”而不杂乱**的资产（`return / intraday entropy` 更高）是否会在下一小段时间继续相对跑赢；做法是横截面上 **long high-EntR / short low-EntR**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / momentum / entropy / information-theory / predictability / 5m / 15m / Binance / paper / public-data / cost / risk
- 证据类型：2026 论文全文 + Binance USDⓈ-M `5m/15m` portability probe

## 1. 这次看了什么

这次看的主材料是：

- **David Neděla, Aleš Kresta (2026)**
- **Title:** *Applicability of Intraday Entropy for Trading During Regular Market Hours*
- **Venue:** *Computational Economics*
- **DOI:** `10.1007/s10614-026-11347-2`
- **Readable URL:** `https://link.springer.com/article/10.1007/s10614-026-11347-2`

这篇 paper 的可迁移点，不是它原文里的美股 regular-hours 组合配置外壳，而是里面那个非常适合我们 desk 拆开的核心量：

> `EntR = recent return / normalized intraday Shannon entropy`

翻成人话就是：
**同样都是涨，涨得更干净、更不乱、更像“有方向地走出去”的标的，后面值不值得继续高看一眼？**

所以它对我们不是“又一个组合管理指标”，而更像一个可直接进入短周期研究池的 **cross-sectional raw alpha / router 候选**。

## 2. 一句话核心结论

- **最该记住的话：** 这篇东西真正可迁移的 base alpha 是 `high recent return per unit of intraday entropy`，也就是“**强势，而且强得不乱**”是否继续赢。  
- **它主要怎么证明：** 作者用 `1m` intraday returns 先算 Shannon entropy，再和日收益拼成 `EntR`，做 regular-hours 选股/组合，对比普通基线与统计检验来验证这个比值是否真有用。

## 3. 为什么和当前项目有关

这条线对当前 desk 有三点价值：

1. **它是能独立定义的 raw alpha，不是 filter 假装 alpha。**  
   分数本身就能排序、就能下单，不依赖外部宏观数据。
2. **它天然适合压缩到 `5m / 15m`。**  
   原文是“收益 ÷ intraday entropy”；我们完全可以把它缩成 `过去 1~4h return ÷ 过去 1~4h 1-bar entropy`。
3. **它也能服务已有 raw alpha。**  
   如果裸 alpha 不够强，它至少很像一个 `cross-sectional router / admission score`：决定同一时刻该把预算给谁。

所以这条线的关键，不是抄论文原始投资组合，而是看：
**短周期 crypto 里，“有方向但不乱”的标的，究竟更该追，还是更该反着做。**

## 3.5 策略拆解（必填）

- 方向属性：横截面 / relative-strength
- 基础 alpha：`high recent return ÷ low intraday entropy` 的高分资产随后相对跑赢
- regime：默认无强 regime 假设；可后续叠加 `BTC trend / dispersion / volume` 做分层
- filter / veto：可后续加流动性、成交额、波动率分位、funding 极端 veto
- risk / sizing / execution overlay：横截面 market-neutral、每期只做 top-vs-bottom、强分数时才开仓、成本后再决定是否保留

## 4. 我做的最小 portability probe

### 4.1 实验口径

- 数据源：Binance USDⓈ-M 公共 `5m` klines
- 标的：`BTC / ETH / SOL / BNB / XRP / DOGE`
- 样本：近约 `30d`，每个币约 `9000` 根 `5m` bars
- 定义：
  - `lookback = 24 bars`（约 `2h`）
  - 先把过去 `24` 根 `5m` 单根收益离散成 6 个固定 bins，算 **normalized Shannon entropy**
  - 再算 `EntR = past_2h_return / entropy`
- 组合：每个时点横截面上 **long top2 EntR / short bottom2 EntR**
- 观察窗：
  - next `3 bars`（`15m`）
  - next `12 bars`（`1h`）

### 4.2 快检结果

结果很直接：**paper 的原始“追高 EntR”读法，在 current liquid-major perp 上并没有顺手迁移成功。**

- `15m` 持有：
  - 全样本 `8972` 笔
  - `long high-EntR / short low-EntR` 平均约 **`-0.47 bps`**
  - 胜率约 **`46.8%`**
- `1h` 持有：
  - 全样本 `8963` 笔
  - 平均约 **`-1.96 bps`**
  - 胜率约 **`44.8%`**
- 只保留分数差更大的 `q75` 强信号后，反而更差：
  - `15m` 约 **`-1.03 bps`**
  - `1h` 约 **`-4.36 bps`**

我还顺手看了一个更粗的 `15m` 压缩版，结论也没变：随着持有窗从 `30m` 拉到 `1h`，同向 continuation 不是变强，而是继续变差。

## 5. 这组结果怎么解读

### 5.1 这篇 paper 提供的是好公式，不是现成 crypto 成品

`EntR` 这个想法本身很干净：
- 收益告诉你“方向有没有出去”；
- entropy 告诉你“过程乱不乱”；
- 两者拼起来，就像是在问“这段走势的信息含量高不高”。

这很值得学。

### 5.2 但 current crypto transfer first verdict 偏负

至少在这次 `Binance liquid-major perp 5m` 口径里：
- **高 EntR 继续赢** 这件事没站住；
- 而且不是“弱正被成本吃掉”，而是 **gross 就已经偏负**。

这意味着对 short-cycle crypto 来说，`高 return / 低 entropy` 这类“走得很顺”的短窗强势，未必是更该追，反而可能更接近：
- 短窗拥挤度过高；
- 一段单边推进后，后面先进入均值回复 / 轮动切换；
- liquid majors 上的趋势延续不如论文设定的 regular-hours equity universe 那么稳。

### 5.3 它更像 router feature，而不是现成主策略

所以这条线当前更合理的定位是：

- **一级：raw alpha 候选**（因为 base alpha 可独立复现）
- **二级：shared router / admission score**
  - 给横截面 momentum basket 排序
  - 或者反过来给 mean-reversion basket 做 veto / target selection

我现在不建议把它直接写成“完整策略可上线”，但非常建议把这个特征留在研究池里。

## 6. 下一步怎么测

最值得做的不是继续沿用 paper 原封不动的 `long high / short low`，而是直接做 4 个最小 A/B：

1. **方向翻转测试**  
   比较 `long high EntR / short low EntR` vs `long low EntR / short high EntR`，确认 crypto 上它究竟更像 continuation 还是 fade。

2. **宇宙分层**  
   把 `liquid majors` 和 `mid-cap perp` 分开。论文逻辑更可能在“非最有效、但仍有流动性”的币上更明显。

3. **和已有 alpha 拼成 router**  
   把 `EntR` 接到已有 `cross-sectional momentum / reversal / residual basket`，看它是 admission layer 还是 veto layer。

4. **改 entropy 定义**  
   当前我用了固定 bins 的 Shannon entropy；下一轮可试：
   - sign entropy
   - volatility-normalized bins
   - 只对 `1m` child bars 算 entropy，再映射到 `5m / 15m` 决策

最小优先实验我会选：
**`5m` 上过去 `2h` 的 `EntR` 做横截面排序，对比 continuation 与 fade 两个方向，在 `majors vs mid-caps` 上分别看 next `15m / 1h`。**

## 7. 风险与保留意见

- 原文是 **美股 regular-hours**，不是 crypto 专文；迁移时必须诚实。
- 这次只做了 **6 个 liquid majors**；如果 edge 真存在，可能在更宽 universe 才能露出来。
- entropy 的离散化方式对结果有影响，当前只算 first verdict，不算正式定论。
- 即便后续方向成立，它也更像 **ranking feature**，不一定是单独拿出来就能交易的主信号。

## 8. 来源

- David Neděla, Aleš Kresta. (2026). *Applicability of Intraday Entropy for Trading During Regular Market Hours*. *Computational Economics*.
- DOI: `10.1007/s10614-026-11347-2`
- Readable URL: `https://link.springer.com/article/10.1007/s10614-026-11347-2`
- Crossref metadata: `https://api.crossref.org/works/10.1007/s10614-026-11347-2`

## 9. 相关产物

- Digest：`/root/clawd/jerry/momentum/research/quant_digests/2026-04-18_2102_intraday-entr-entropy-router-alpha.md`
- Probe summary：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_intraday-entropy-entr_xs_summary.csv`
- Probe events：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-18_intraday-entropy-entr_xs_events.csv`
