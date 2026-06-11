# 别把 Jiang, Kelly, Xiu (2023) 只读成“把 K 线喂给 CNN”：对 short-cycle desk，更该先拆的是「同样跌了 2 小时，但走得更单边、更贴近区间低点的路径，后续更容易继续下滑」这条 raw alpha

- 时间：2026-04-17 20:56 UTC
- 类型：2023 *Journal of Finance* 论文元数据/摘要 audit（Crossref/OpenAlex）+ Binance USDⓈ-M public-data portability probe（`15m` / `5m`）
- 主题类型：raw alpha
- 基础 alpha：不是“过去涨/跌了多少”本身，而是 **`lookback return sign × path efficiency × close-location` 定义的短窗单边趋势路径延续**；当前 public-data first verdict 明显偏向 **downside continuation**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/trend/path-shape/intraday/continuation/path-efficiency/close-location/downside-asymmetry/5m/15m/paper/public-data/cost/risk
- 证据类型：论文摘要级机制启发 + public-data probe

## 1) 这次看了什么
- **Authors**：Jingwen Jiang, Bryan Kelly, Dacheng Xiu
- **Year**：2023
- **Title**：*(Re-)Imag(in)ing Price Trends*
- **Venue**：*Journal of Finance*
- **DOI**：<https://doi.org/10.1111/jofi.13268>
- **Readable URL**：<https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268>
- **Repo URL**：N/A

这篇论文最重要的点，不是“用了图像模型”这么表面，而是它把一个老问题重新写了一遍：

> **市场并不只在乎“这段时间涨了/跌了多少”，还在乎“这段路是怎么走出来的”。**

Crossref 摘要的核心表述很直接：作者不是去验证预定义的 momentum/reversal 规则，而是直接让机器从价格图中找最有预测力的形状模式；这些模式和常见趋势信号并不一样，而且在不同时间尺度上有一定迁移性。

## 2) base alpha 先说清
这篇东西如果翻成当前 desk 最值得先测的版本，base alpha 不是“图像分类”本身，而是：

> **短窗内更“顺滑/单边/贴边”的价格路径，比同收益但更锯齿的路径，更容易在后续数根 bar 延续原方向。**

所以这里我把它归成 `raw alpha`，不是 `filter / overlay`：
- `path shape` 不是给别的 alpha 做风控附属；
- 它本身就在定义“哪一种过去走势才算真正可交易的趋势”。

但要诚实补一句：
- 本轮 public-data first verdict 显示，这条 edge **不是对称地作用在多空两边**；
- 在 crypto perp 的 recent 样本里，它更像一条 **downside continuation pocket**，而不是无脑 long-short 对称趋势信号。

## 3) 我怎么把论文思想翻成 desk 可复现版本
论文是价格图像学习；我先做了一个极简、低过拟合的代理，不硬抄 CNN：

### 路径形状代理（image-lite）
对每个 bar，先看过去一段 lookback：
1. **方向**：lookback return 的正负号；
2. **Path efficiency (ER)**：
   - `|终点-起点| / 路径总长度`
   - 越接近 1，说明这段路越单边、越少来回折返；
3. **Close location value (CLV)**：
   - 当前 close 在 lookback 区间高低点中的相对位置；
   - 对 long，希望 close 更贴近区间高点；
   - 对 short，希望 close 更贴近区间低点。

于是信号不是 plain momentum，而是：
- **long**：过去一段上涨，且 `ER` 高、`CLV` 靠近高点；
- **short**：过去一段下跌，且 `ER` 高、`CLV` 靠近低点。

这就是把“价格图长什么样”压缩成两个最便宜、最容易落地的可解释特征。

## 4) 最小可复现实验（本轮已跑）
### 数据源
- Binance USDⓈ-M public `klines`
- URL：<https://fapi.binance.com/fapi/v1/klines>
- 公开性：公开可得
- 更新频率：按 bar 更新

### 标的
- BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT

### 频率与样本
- `15m`：近 `180d`
- `5m`：近 `90d`

### 规则口径
#### 15m 主实验
- lookback = `8` bars（约 `2h`）
- hold = `4` bars（约 `1h`）
- shape gate：`ER >= 0.65`
- long 还要求 `CLV >= 0.75`
- short 还要求 `CLV <= 0.25`
- 成本：round-trip `6 bps`

#### 5m 快检
- lookback = `12` bars（约 `1h`）
- hold = `6` bars（约 `30m`）
- 其余口径相同

### 对照组
- **baseline_sign**：只看 lookback return 的正负，直接顺着做
- **shape_gated**：加上 `ER + CLV` 路径形状约束

## 5) 关键数据点（先看结论）
### 结论 1：plain intraday momentum 在 recent crypto perp 上基本是成本前后都很差
按四币汇总：
- `15m long baseline`：`34,598` 笔，平均 `-7.18 bps/笔`
- `15m short baseline`：`34,345` 笔，平均 `-5.16 bps/笔`
- `5m long baseline`：`50,963` 笔，平均 `-6.26 bps/笔`
- `5m short baseline`：`52,320` 笔，平均 `-4.87 bps/笔`

人话：
> **“过去涨了/跌了，就继续追” 这件事，在我们关心的 recent short-cycle perp 口径里，几乎可以直接判死。**

### 结论 2：路径形状 gate 并没有普适救活 long side，甚至经常更差
按四币汇总：
- `15m long shape_gated`：`3,543` 笔，平均 `-11.16 bps/笔`
- `5m long shape_gated`：`2,519` 笔，平均 `-8.00 bps/笔`

这说明一个很重要的反直觉点：
> **crypto 的“顺滑上涨”不一定更该追，很多时候反而是更接近短线过热。**

### 结论 3：但在 `15m` 的 downside continuation 上，shape gate 明显有信息增益
按四币汇总：
- `15m short baseline`：平均 `-5.16 bps/笔`
- `15m short shape_gated`：平均 `-2.46 bps/笔`

也就是：
- 仍未过成本线；
- 但比 plain short momentum **改善约 `+2.70 bps/笔`**。

### 结论 4：最值得保留的 pocket 是 `SOL 15m short`
- `SOL 15m short baseline`：`8,688` 笔，平均 `-4.35 bps/笔`
- `SOL 15m short shape_gated`：`955` 笔，平均 **`+1.43 bps/笔`**

注意这里是 **已扣 `6 bps` 成本后仍为正**。虽然样本不算巨大，也绝对还不能直接宣判 production-ready，但它已经不是“只剩 paper story”的程度了。

## 6) 这条研究线对当前 desk 的真实价值
一句话：
> **价格路径形状不是 decorative feature；它至少能把“所有下跌都去追空”的烂 baseline，筛成一个更像样的 downside continuation pocket。**

为什么这对 desk 有价值？
1. 它不是又一个泛泛的“加指标看看”；它在回答更底层的问题：**同样的过去收益，哪些路径才值得当趋势看待？**
2. 它和当前 short-cycle 体系兼容：
   - 不需要额外付费数据；
   - 直接从 OHLC 就能做；
   - 能和 breakout / momentum / fragility / OI / order-flow 组合。
3. 它给了一个明确方向：
   - **long side 先别幻想**；
   - **优先把它当 short-side admission / raw alpha pocket 继续深挖**。

## 7) 和 `1m / 3m / 5m / 15m` 的关系
- **15m**：当前最像样。尤其是 downside continuation 这边，已经看到 from bad → less bad → 局部转正 的结构。适合先做主战深挖。  
- **5m**：当前 first verdict 偏差，说明简单 ER/CLV 代理在更快周期上太粗。不是没戏，但不能照抄。  
- **3m / 1m**：若要下钻，更像 execution-aware 版本：
  - 把 `shape` 放在更高一级（如 15m/5m）定义主方向；
  - 1m/3m 用来做 pullback re-entry / maker entry / stop placement，别直接拿 ultra-fast bar 去生啃同一公式。

## 8) 下一步怎么测（最重要）
### A. 先做 asymmetric follow-up，不要再多空对称地浪费时间
优先只测：
- `15m short`
- 标的先聚焦：`SOL / ETH / BNB`
- BTC 只留作对照

### B. 把 image-lite 升级成更像论文精神、但仍便宜的 shape 特征组
至少加三类：
1. **回撤密度 / counter-trend density**：单边下跌里反向小反弹有多少；
2. **bar-body dominance**：实体占比高不高，还是靠影线堆出来；
3. **time-at-low / close-near-low persistence**：不是最后一根突然砸到低点，而是连续多根贴低运行。

### C. 把它和已有 raw alpha 组件做“串联 admission”而不是单独硬跑
优先组合：
1. **fragility / crowded-long / liquidation-unwind** 方向的已有研究；
2. **OI-volume shock / cascade** 类事件；
3. **breakdown 后 retest fail** 这类结构性下破。

一句话就是：
> 让 `path shape` 决定“这次下跌像不像真的会继续”，而不是单独拿它裸奔。

### D. 明确最小实验矩阵
下一轮建议直接跑：
- 周期：`15m signal / 5m execution`
- universe：`BTC/ETH/SOL/BNB` → 先缩到 `ETH/SOL/BNB`
- entry：`ret<0 & ER分位前20% & CLV分位后20%`
- exit：`1h 固定持有` vs `下根反抽止损` vs `ATR trail`
- cost ladder：`2 / 4 / 6 / 8 bps`
- 输出：`trade_count / gross / net / side asymmetry / by-symbol contribution`

## 9) 风险与保留意见
- 当前只是 **image-lite** 代理，不等于复现了论文真正的图像学习框架。  
- 结果显示明显的 **方向不对称**：不能把“图像趋势有预测力”误读成多空都该追。  
- `SOL 15m short` 的正值很可能带有样本期结构性成分，必须做滚动窗和分段验证，不能直接上线。  
- 这条线很适合做 **admission / selection**，但若想单独成为 production alpha，还需要 execution 与风险壳配齐。

## 10) 本轮产物
- `reports/artifacts/quant_digests/2026-04-17_price_shape_intraday_probe.py`
- `reports/artifacts/quant_digests/2026-04-17_price_shape_intraday_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-17_price_shape_intraday_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-17_price_shape_intraday_probe_trades.csv`

## 11) 来源
1. Jiang, J., Kelly, B., & Xiu, D. (2023). *(Re-)Imag(in)ing Price Trends*. *Journal of Finance*, 78(6), 3193–3249. DOI: <https://doi.org/10.1111/jofi.13268>  
   Readable URL: <https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268>
2. Crossref metadata / abstract: <https://api.crossref.org/works/10.1111/jofi.13268>
3. OpenAlex metadata: <https://api.openalex.org/works/https://doi.org/10.1111/jofi.13268>
4. Binance USDⓈ-M Futures Klines API（public）: <https://fapi.binance.com/fapi/v1/klines>
