# 别把 Padyšák, Vojtko (2022) 只读成“BTC 季节性综述”：对 short-cycle crypto desk，更该先测的是「`21:00–23:00 UTC` 固定时间窗 drift」这条 raw alpha

- 时间：2026-04-18 09:40 UTC
- 类型：2022 SSRN working paper 摘要级证据 + PapersWithBacktest 策略镜像 + TradingView 社区实现线索 + Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**BTC 及部分 liquid majors 在每天固定的美股晚段/收盘前后两小时，存在可重复的正向漂移；它不是“全天都涨”，而是收益更集中在一小段 UTC 时间窗里**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（时间触发天然给出 `entry/exit`，desk 版只需再补 `size / cost / veto`）
- 主题标签：raw-alpha / single-asset / time-of-day / seasonality / session / intraday / us-session / btc / eth / sol / bnb / 15m / 5m / paper / abstract-only / public-data / cost / risk
- 证据类型：abstract / mirror summary + community implementation clue + public-data portability probe

先回答一句：**这篇东西的 base alpha 是什么？**

不是“美股开盘会影响币圈”这种泛解释，也不是 regime/filter。它的 base alpha 很直接：

> **每天固定那 2 小时，持有 BTC（以及部分 liquid majors）本身就比随机 2 小时更容易拿到正收益；收益不是均匀分布在 24 小时里，而是明显挤在一个 session pocket。**

所以这轮我把它归成 **raw alpha / 单资产 time-of-day drift**，不是 filter。

---

## 1. 这次看了什么
主来源：
- **Authors：** Matúš Padyšák, Radovan Vojtko
- **Year：** 2022
- **Title：** *Seasonality, Trend-following, and Mean reversion in Bitcoin*
- **Venue：** SSRN working paper
- **DOI：** `10.2139/ssrn.4081000`
- **Readable URL：** <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4081000>
- **Mirror summary：** <https://paperswithbacktest.com/strategies/seasonality-trend-following-and-mean-reversion-in-bitcoin>
- **ResearchGate entry：** <https://www.researchgate.net/publication/367721906_Seasonality_Trend-following_and_Mean_reversion_in_Bitcoin>
- **Community implementation clue：** <https://www.tradingview.com/script/luAYwrT5-Overnight-Effect-High-Volatility-Crypto-AiBitcoinTrend/>
- **Repo URL：** 无官方公开 repo

先说明证据强度：**这轮没拿到 SSRN 全文**，所以不能把论文正文细节编出来；当前可核的是 DOI 元数据、摘要级描述、PapersWithBacktest 的镜像总结，以及一个明确写出 `21:00–23:00 UTC` 的 TradingView 社区实现线索。好处是：这条线非常适合直接用公开 `15m` 数据做最小实验，不需要等全文才能先做 first verdict。

PapersWithBacktest 镜像给出的关键信息很直接：
- 这篇研究看了 seasonality、trend-following、mean reversion 三条支线；
- seasonality 部分最醒目的结论是：**“只在每天两小时持有 BTC”** 也能构成简单策略；
- TradingView 社区实现把这条线具体化成 **`21:00–23:00 UTC`** 的固定窗口，并声称灵感直接来自该 paper。

所以这轮不把它写成“泛季节性背景”，而是直接收口成：
**daily fixed-window drift raw alpha。**

相关 artifact：
- `reports/artifacts/quant_digests/2026-04-18_tod_21_23_utc_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_tod_21_23_utc_probe_events.csv`
- `reports/artifacts/quant_digests/2026-04-18_tod_2h_window_scan.csv`
- `reports/artifacts/quant_digests/2026-04-18_tod_21_23_utc_probe.json`

---

## 2. 一句话核心结论
**如果把这篇 2022 材料 desk 化，当前最值得先测的不是“日内很多窗口都有故事”，而是 `21:00–23:00 UTC` 这一段固定 two-hour pocket；在 Binance USDⓈ-M 近 365 天 `15m` 数据里，它对 `BTC/ETH/SOL/BNB/DOGE` 都给出正向 gross drift，等权组合日均约 `+12.90 bps`，并且在多数币里属于全天 96 个两小时窗口中的前两名。**

**一句话证明方式：** 论文摘要和镜像页只告诉我们“有一个每天两小时的简单 seasonality 策略”；我再直接把 `21:00–23:00 UTC` 放到 Binance perp 公开 `15m` 数据上，扫了近 `365d`、`6` 个 liquid majors，并和全天所有 rolling `2h` 窗口做横向排名比较。

---

## 3. 为什么这对当前 desk 有意义
这条线的优点不是“学术包装漂亮”，而是它非常适合 short-cycle 研发节奏：

1. **base alpha 够清楚**：固定 UTC 时间窗持有，不需要额外解释成别的 filter；
2. **entry / exit 天然简单**：每天 `21:00 UTC` 入，`23:00 UTC` 出；
3. **很容易下沉到 `15m/5m`**：主信号是 2h session pocket，child execution 可以再拆成 `20:55–21:15` 的 pullback fill、或 `21:00–22:00 / 22:00–23:00` 两段；
4. **和最近素材池互补**：我们最近补了很多 microstructure / pairs / funding / divergence，这条线能补一个**纯时间结构 raw alpha**，不再只围着同一类形态打转。

---

## 3.5 策略拆解（必填）
- 方向属性：**顺势 / 单资产 intraday seasonality drift**
- 基础 alpha：**固定 UTC 时间窗（当前先测 `21:00–23:00 UTC`）内的正向 drift**
- regime：可先不加；进阶版再看高波动/低波动、趋势/震荡分层
- filter / veto：可选 `24h realized vol`、日内 trend sign、事件日黑名单、 funding 结算前后 veto
- risk / sizing / execution overlay：时间止盈/止损、日均波动缩放、`maker-first` 入场、单日一次、节假日/宏观事件 size-down

---

## 4. public-data probe：当前最该记住的 4 个数据点
样本：Binance USDⓈ-M，`BTC/ETH/SOL/BNB/XRP/DOGE`，`15m`，近约 `365d`；定义为每天 `21:00 UTC` 用当根 `open` 入场，`23:00 UTC` 用两小时后 `open` 出场。

### 4.1 组合层：不是只有 BTC，有一篮子可迁移性
六币等权组合 `EW6`：
- 样本数：**365** 天
- 平均 gross：**`+12.90 bps / 日`**
- 胜率：**`58.36%`**
- t-stat：**`2.87`**

粗扣 `8 bps` round-trip 后，组合仍大约剩 **`+4.90 bps / 日`**。这还不算滑点，但至少说明它不是“只有统计显著、完全过不了成本”的那种薄到看不见的边。

### 4.2 BTC 本身就不弱，而且 21–23 UTC 接近全天最强 pocket
`BTCUSDT`：
- 平均 gross：**`+10.10 bps / 日`**
- 胜率：**`54.52%`**
- t-stat：**`3.27`**
- 在全天所有 rolling `2h` 窗口中，`21:00–23:00 UTC` 的 mean rank = **第 2 名 / 96**

更细一点看，BTC 最强的一串窗口其实集中在：
- `20:15–22:15`：**`+10.26 bps`**
- `21:00–23:00`：**`+10.10 bps`**
- `20:30–22:30`：**`+9.08 bps`**

这意味着：**真正的 edge 不是一个孤零零的 timestamp，而是一段美股晚段附近的正 drift 簇。**

### 4.3 不是所有币都一样，但 `ETH / SOL / BNB / DOGE` 也给出同向证据
- `ETHUSDT`：**`+17.43 bps / 日`**，胜率 **`57.81%`**，窗口排名 **第 1 / 96**
- `SOLUSDT`：**`+13.39 bps / 日`**，胜率 **`58.36%`**，窗口排名 **第 2 / 96**
- `BNBUSDT`：**`+12.51 bps / 日`**，胜率 **`59.73%`**，窗口排名 **第 2 / 96**
- `DOGEUSDT`：**`+17.55 bps / 日`**，胜率 **`56.71%`**，窗口排名 **第 1 / 96**

只有 `XRPUSDT` 明显弱一些：
- **`+6.42 bps / 日`**，t-stat **`1.18`**，排名掉到 **第 8 / 96**

所以这条线更像 **liquid-major basket drift**，不是所有币都该一刀切等权上满。

### 4.4 “高波动才更好”这件事，目前并不统一
我额外按过去 `24h` realized vol 的样本中位数，把 `21–23 UTC` 分成高波动 / 低波动两档：
- 组合层 `EW6`：高波动 **`+13.33 bps`** vs 低波动 **`+12.47 bps`**，差别不大；
- `BTC/BNB` 偏向高波动略好；
- `ETH/SOL/XRP` 反而是低波动更稳。

所以别急着把它包装成“必须 high-vol 才做”的 filter；当前更像：
**时间窗 alpha 本体先成立，波动过滤还是第二层优化题。**

---

## 5. 风险与保留意见
1. **论文正文未拿到**：这轮必须诚实标注为 `abstract / mirror based`，不能把原文回测参数说得很确定。
2. **时区 / 夏令时口径要锁死**：`21:00–23:00 UTC` 是当前 mirror + community implementation 给出的可操作口径；若后续拿到全文，可能还要核对是否与 NYSE open/close、DST 调整完全一致。
3. **时间窗 edge 容易被宏观事件污染**：CPI、FOMC、财报夜、大所事故日，可能正好密集落在这段时间，使均值被大事件拉高。
4. **这不是全天趋势预测器**：它更像一个稳定 pocket。把它硬扩展成“只要晚间就做多”很可能会稀释 edge。

---

## 6. 最小可复现实验
### 研究假设
在 liquid majors 上，**每天 `21:00–23:00 UTC` 存在稳定正 drift；若把 `15m` child entry 做得更细，成本后表现有机会优于“21:00 一把梭”。**

### 一个可计算定义
- 主信号：若当前时间到 `21:00 UTC`，则开多；
- 基础版本：`23:00 UTC` 固定平仓；
- 对照组：全天任意 rolling `2h` 窗口、以及相邻窗口 `20:00–22:00 / 22:00–24:00`。

### 最小回测切口
- 标的：`BTC/ETH/SOL/BNB/DOGE`
- 周期：`15m` 主测试，`5m` 做 child execution
- 样本：近 `365d`
- 最先看：
  1. `gross / net bps per day`
  2. `window rank stability`

---

## 7. 下一步怎么测
下一轮别再停留在“21:00 到 23:00 买着看”，直接做这 4 件事：

1. **把固定持有版升级成 child execution 版**  
   比较：
   - `21:00` 直接入场
   - `21:00–21:15` 首次回踩 `VWAP/open` 再入
   - `21:00–22:00` 分两笔 TWAP 入场

2. **做邻域鲁棒性**  
   不只看 `21:00–23:00`，而是同时扫：
   - `20:30–22:30`
   - `20:45–22:45`
   - `21:15–23:15`
   看它到底是单点巧合，还是一整个 session 窗簇都强。

3. **做 friction ladder**  
   这条线日频只开一次，看起来比高频策略更抗费，但也必须明确分：
   - `4 bps`
   - `8 bps`
   - `12 bps`
   三档净值口径，别只报 gross。

4. **做 basket admission**  
   当前 probe 已经提示 `XRP` 弱、`ETH/SOL/BNB/DOGE` 强。下一步该比较：
   - `BTC only`
   - `BTC+ETH`
   - `EW5 majors`
   - `只保留 top-ranked windows 的币`

如果这四步跑完，`15m/5m` child execution 仍能在成本后保住正 net，
那这条线就不只是“seasonality 小知识”，而是值得进 admission 的 **time-of-day raw alpha**。