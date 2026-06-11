# 别把 skewness 只当“分布描述符”：对 short-cycle desk，更该先测的是「realized-skewness cross-section fade」这条 raw alpha

- 主题类型：raw alpha
- 基础 alpha：**横截面上，过去一段时间收益分布更“彩票化”（正偏更高）的币，后续更容易跑输；负偏或不那么彩票化的币，后续相对更容易跑赢，因此可做 `long low-skew / short high-skew` 的横截面反转**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-03 02:54 UTC
- 类型：2024 *International Review of Financial Analysis* 元数据 + 2026 GitHub repo source audit（`alpha_05_realized_skewness.py`）+ 2015 JFE 经典 realized-skewness 因子 grounding
- 主题标签：raw-alpha / cross-sectional / mean-reversion / skewness / lottery / realized-moments / distribution-shape / long-short / top-bottom / 15m / 5m / 3m / 1m / paper / repo / public-data / cost
- 证据类型：paper-based（标题/元数据级 crypto grounding）+ repo-based（可直接抄成最小策略壳）

## 1. 这次为什么选它

这轮默认优先补 **raw alpha 素材池**，而不是再做一个纯 gate / overlay。

当前库里已经堆了很多：
- lagged-return reversal / momentum
- pairs / cointegration / basis / funding
- OFI / order-book pressure

但 **“分布形状 → 横截面定价偏差”** 这条线还不算厚，尤其是 **`skewness` 这类比 `MAX` 更平滑、比单根极值更不脆弱** 的 raw alpha 壳，值得补一篇。

一句话说，这次的 base alpha 很清楚：

> **不是追涨跌本身，而是做“彩票偏好”溢价的横截面回吐。**

这比继续再写一篇普通 loser-bounce 更值得，因为它给 desk 新增的是 **另一类原始信号家族**，不是同一类信号换个参数皮肤。

## 2. 这次看的材料

### 2.1 近期 crypto 文献锚点

- **Authors**: Yakun Liu, Yan Chen
- **Year**: 2024
- **Title**: *Skewness risk and the cross-section of cryptocurrency returns*
- **Venue**: *International Review of Financial Analysis*, Volume 96, Article 103626
- **DOI**: `10.1016/j.irfa.2024.103626`
- **Readable URL**: <https://doi.org/10.1016/j.irfa.2024.103626>
- **Repo URL**: 未见作者公开 repo

### 2.2 可直接落地的 repo 壳

- **Repo**: VedantUpasani46 / `Alpha-Research-Discovery`
- **File**: `alpha_05_realized_skewness.py`
- **Readable URL**: <https://github.com/VedantUpasani46/Alpha-Research-Discovery>
- **Direct File URL**: <https://github.com/VedantUpasani46/Alpha-Research-Discovery/blob/master/alpha_05_realized_skewness.py>

### 2.3 经典地基（解释 realized skewness 为什么能当 alpha）

- **Authors**: Diego Amaya, Peter Christoffersen, Kris Jacobs, Aurelio Vasquez
- **Year**: 2015
- **Title**: *Does realized skewness predict the cross-section of equity returns?*
- **Venue**: *Journal of Financial Economics*
- **DOI**: `10.1016/j.jfineco.2015.02.009`
- **Readable URL**: <https://doi.org/10.1016/j.jfineco.2015.02.009>

## 3. 先把 base alpha 说死：它不是 filter，它就是 alpha 本体

这条线最核心的表达很简单：

1. 对每个币，取过去一段时间的 bar return；
2. 计算 realized skewness；
3. 横截面排序；
4. **long 低 skew / short 高 skew**。

翻成人话：

- **高正偏**：更像“平时没啥、偶尔猛拉”的彩票币；
- **低偏 / 负偏**：更像“走势没那么梦幻、但没被彩票偏好抬价”的币。

如果市场里确实存在对“彩票型 payoff”的追捧，那么：

> **高 skew 那一边被买贵，后续更容易回吐；低 skew 那一边相对便宜。**

所以它不是：
- 纯解释型综述；
- 只服务于别的 alpha 的 veto；
- 只能当 risk overlay 的低频变量。

它本身就是一条 **cross-sectional raw alpha**。

## 4. 它和我们已经写过的 `MAX / 极端单根` 不是一回事

这个区别很重要。

我们库里之前已经 intake 过 lottery / MAX 相关东西，但 **MAX 更像“你最近是不是出过一根梦幻长阳”**；
而 **realized skewness 看的是整段 return 分布的偏斜形状**。

差异可以粗暴理解成：

- `MAX`：盯最极端那一根；
- `skewness`：盯整段样本里“右尾是不是系统性更肥”。

对 short-cycle desk 来说，后者有两个现实优势：

1. **没那么容易被单根异常 wick 绑架**；
2. 更适合做 **多币横截面排序**，而不是单币图形故事会。

所以这篇值得进池，不是因为“又一个 lottery 概念”，而是因为它提供的是一条 **更平滑、更适合程序化横截面壳** 的 raw alpha。

## 5. repo 里已经给了一个相当完整的策略骨架

`alpha_05_realized_skewness.py` 虽然不是专门为 crypto 短周期写的，但它把策略骨架写得很完整，几乎可以直接压缩到 desk 最小实验：

- **主信号窗口**：`22` 个观测窗口
- **对比窗口**：`5 / 10 / 22 / 63`
- **组合建法**：top/bottom `20%`
- **默认换手节奏**：每 `5` 天再平衡
- **成本假设**：`8 bps`
- **方向**：`alpha = -rank(skew)`，即 **short high-skew / long low-skew**

这些数字虽然原始设定偏日频，但有两个对我们非常有用的点：

### 5.1 它已经把“完整策略”四件套写出来了

不是只说一句“skewness 可能有预测力”，而是把：
- signal
- sorting
- rebalance
- cost

都写进去了。

### 5.2 它天然适合被压缩到 1m / 3m / 5m / 15m

因为 skewness 只是 rolling returns 的函数，不依赖难拿数据。

也就是说，我们完全可以把：
- 日频 `22d` → 替换成 `过去 4h / 8h / 24h` 的 bar-return 分布；
- 每周 rebalance → 替换成 `每 1h / 2h / 4h` 更新横截面；
- 8bps 成本 → 替换成 perp desk 更现实的 `4 / 6 / 8 bps` 单边压力测试。

## 6. 对 short-cycle desk，最合理的 translation 不是照抄论文周期，而是缩成“分布形状的短线横截面 fade”

### 6.1 推荐的最小实验壳

**Universe**
- Binance / OKX / Bybit 主流 USDT perp
- 先取 `24h quote volume` 前 `30~50` 个
- 过滤：近 `N` bars 缺失率过高、价量过低、tick 过粗的币

**Signal**
- 对每个币计算最近窗口的 realized skewness：
  - `5m`：先测 `48 / 96 / 288` bars（4h / 8h / 24h）
  - `15m`：先测 `16 / 32 / 96` bars（4h / 8h / 24h）
- 做横截面 rank
- 信号方向：**long bottom q / short top q**

**Entry / Exit**
- 每 `4` 根 bar 更新一次（1h on 15m；20m on 5m）
- 固定持有 `4 / 8 / 12` bars 三档
- 不做单币 discretionary exit，先做最干净的固定持有回测

**Sizing**
- 先用 dollar-neutral
- 第二轮再试 vol-neutral / ADV-capped
- 单币权重上限先卡 `5%~8%`

**Risk / Cost**
- 单边成本先压 `4 / 6 / 8 bps`
- 做 BTC 单边大波动 veto：若 BTC 最近 `1h` 绝对收益 > 某阈值，则该次 rebalance 缩仓或跳过
- 做 liquidity floor：低于样本中位数的流动性币缩权，而不是直接等权放大尾部垃圾币

## 7. 我更看好的不是“极端尾部”，而是中高流动性里的温和 skew-fade

如果直接照学术直觉，最容易犯的错是：

> “彩票偏好”听起来像长尾小币现象，那我就该去最尾部找最夸张的正 skew 币狠狠干空。

我反而不建议一上来这么做。原因很简单：

1. **最尾部币的 skew 往往和脏数据、上架事件、单根拉盘、极薄盘口混在一起**；
2. 你以为在做 skewness，实际可能是在做 listing/manipulation 噪音；
3. short-cycle 上真正可交易的 edge，未必在最极端分位，反而可能在 **主流 perp universe 的温和右偏币** 上更稳。

所以这条策略第一轮更合理的 desk 版本应该是：

- **只在中高流动性币池里做 skewness 横截面 fade**；
- 不急着碰最尾部；
- 先看是否能在可交易 universe 里拿到稳定 rank IC / spread return。

## 8. 这条 alpha 最可能服务哪类 desk 组合

它比较适合接在这几类组合后面：

### 8.1 作为独立 XS raw alpha sleeve

直接跟：
- lagged-return XS reversal
- lagged-return XS momentum
- PCA residual mean reversion

并列。

好处是来源不同：
- 前几类更看价格路径；
- 这条更看 **路径分布形状**。

### 8.2 作为 trend / breakout 家族的 short basket 候选池

如果某些币刚经历一段“偶发大阳线把分布右尾拉肥”的走势，未来未必继续涨，可能更适合进入 **相对价值空头备选池**。

这里要注意：
- 这时 skewness 不是 filter；
- 它是单独的空头打分来源。

### 8.3 作为 lottery/MAX 家族的更平滑替代

已有 MAX 因子太容易被单根 bar 主导时，可以试：
- `MAX`
- `realized skewness`
- `MAX × skewness intersection`

看谁在 short-cycle 下更抗噪。

## 9. 这条线最容易失败在哪里

### 9.1 它可能只是慢频偏好，不一定天然压得进 1m / 3m / 5m

学术上 skewness 溢价常常更慢。

所以这里最该警惕的不是“有没有故事”，而是：

> **短到 1m / 3m 后，你算出来的可能不再是稳定的 distribution-shape premium，而只是 microstructure noise。**

因此建议优先级是：
- 先 `15m`
- 再 `5m`
- 最后才看 `3m / 1m`

### 9.2 skewness 很怕异常点

虽然它比 MAX 平滑，但它仍然是三阶矩，天然对尾部敏感。

所以第一轮一定要做：
- return clip / winsor
- event flag（listing、极端 funding、插针）
- 成交额过滤

### 9.3 它可能和既有 reversal 家族高度重叠

如果最后发现：
- skewness 排名几乎就是 lagged-return 排名的另一种写法；
- 增量 IC 很小；

那它就不该作为独立 sleeve，而应该降级成：
- `lagged-return reversal` 的 companion feature；
- 或用于多因子排序中的次级项。

## 10. 下一步怎么测（直接给实验单）

### 实验 A：先确认它是不是独立 alpha，而不是旧 reversal 换壳

在主流 perp `15m` universe 上：
- `signal_1 = -rank(realized_skew_24h)`
- `signal_2 = -rank(ret_24h)`
- 看两者横截面相关性、独立 IC、双变量回归

**判定标准**：
- 若 `signal_1` 对 `signal_2` 的增量 IC 接近 0，就别单列；
- 若增量 IC 明显为正，再继续。

### 实验 B：找最稳的窗口，而不是先找最猛的极端分位

窗口先测：
- `15m`: `16 / 32 / 96`
- `5m`: `48 / 96 / 288`

分位先测：
- `q = 10% / 20% / 30%`

**目标**：
- 先找成本后还能活的 rank spread；
- 不追求某个样本窗里最漂亮的 gross。

### 实验 C：验证它该不该只在高流动性币池里活

分三层回测：
- top-liquidity 20%
- middle 60%
- bottom 20%

我对这条线的先验是：

> **最可交易的版本，大概率不会出现在最底层流动性。**

如果这条判断对，那么 desk 版 production shell 会更简单、更能下单。

## 11. 最终判断

这篇值得进研究池，而且优先级不低。

原因不是它已经被证明能直接在 `1m/3m/5m/15m` 上赚钱，而是：

1. **base alpha 清楚**：`long low-skew / short high-skew`；
2. **可独立复现**：只要 OHLCV 就能做；
3. **可写成完整策略**：entry / exit / sizing / risk / cost 都很好补齐；
4. **和现有池子有差异化**：它是“分布形状”家族，不是又一个 lagged-return/pairs/funding 变种。

所以我的结论是：

> **把它放进 short-cycle 素材池，先按 `15m 主测、5m 次测、1m/3m 最后看` 的顺序，验证“可交易 universe 中的 realized-skewness cross-section fade”是否有独立增量。**

如果实验 A/B/C 跑出来有增量，再决定它是：
- 独立 raw alpha sleeve，还是
- 进入多因子 XS 排序模型作为一条 distribution-shape feature。

## 12. 来源链接

1. Liu, Y., & Chen, Y. (2024). *Skewness risk and the cross-section of cryptocurrency returns*. *International Review of Financial Analysis*, 96, 103626. DOI: `10.1016/j.irfa.2024.103626`  
   URL: <https://doi.org/10.1016/j.irfa.2024.103626>

2. Amaya, D., Christoffersen, P., Jacobs, K., & Vasquez, A. (2015). *Does realized skewness predict the cross-section of equity returns?* *Journal of Financial Economics*. DOI: `10.1016/j.jfineco.2015.02.009`  
   URL: <https://doi.org/10.1016/j.jfineco.2015.02.009>

3. VedantUpasani46. (2026). *Alpha-Research-Discovery* — `alpha_05_realized_skewness.py`.  
   Repo URL: <https://github.com/VedantUpasani46/Alpha-Research-Discovery>  
   File URL: <https://github.com/VedantUpasani46/Alpha-Research-Discovery/blob/master/alpha_05_realized_skewness.py>
