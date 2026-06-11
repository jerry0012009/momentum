# 别把 breakout-short 想成“前一小时越左偏越能追空”：15m 更像吃 **failed-bounce 的中性/微右偏 skew band**，而不是 waterfall 延续
- 时间：2026-03-20 20:08 UTC
- 类型：论文 + 本地代理快检
- 主题标签：breakout-short/v3/final-verdict/follow-up/skewness/intrahour/5m/15m/confirmation/failure/failed-bounce/filter/paper/crypto
- 证据类型：论文机制启发 + 本地 15m 既有信号快检

## 1) 这次为什么选它
这轮优先继续服务 **`V3 final-verdict / breakout-short follow-up`**，而不是再开一条离题的新线。

原因很简单：
- 我们已经有不少 `breakout-short` 的 **post-break path / failure / confirmation** 读法；
- 但“**信号前 1 小时价格分布长什么样**”这件事，还没有被明确写成一个可秒测的 5m → 15m gate；
- 它非常便宜：直接复用现成 15m signal 样本，再回看过去 12 根 5m 收益就能做最小实验。

更重要的是，这个角度不是硬抄论文 headline alpha，而是从论文里拎一个 **更适合 desk 的旁支变量**：**过去 1 小时的 5m 收益偏度（skewness）**，把它当成 short follow-up 的确认/否决层。

## 2) 看的来源
主来源是较新的 crypto 论文：

### Source A（主）
- Author: **Manisha Yadav**
- Year: **2025**
- Title: **Intraday lottery demands in cryptocurrency market**
- Venue: **Studies in Economics and Finance**
- DOI: **10.1108/SEF-07-2024-0461**
- Readable URL: `https://doi.org/10.1108/SEF-07-2024-0461`
- Repo URL: **N/A**

这篇论文的主问题是 intraday `MAX`，不是给我们现成的 breakout-short 规则；但它有个对 desk 很有用的细节：**作者把过去 1 小时的 5m returns 里 `MAX / IVOL / skewness` 都纳入了同一套高频横截面框架**。对我们来说，最值得偷的不是 `MAX` 本身，而是这套 **“上一小时 5m 分布形状”** 的建模骨架。

### Source B（测度来源）
- Authors: **Turan G. Bali, Nusret Cakici, Robert F. Whitelaw**
- Year: **2011**
- Title: **Maxing out: Stocks as lotteries and the cross-section of expected returns**
- Venue: **Journal of Financial Economics**
- DOI: **10.1016/j.jfineco.2010.08.014**
- Readable URL: `https://doi.org/10.1016/j.jfineco.2010.08.014`
- Repo URL: **N/A**

这篇老论文不是这轮主角，但它是 `MAX / lottery demand` 这条测度传统的上游来源。这里引用它，主要是为了交代：**我们这次偷的是“过去一段短收益分布可当解释变量”这层思路，不是直接搬股票横截面结论。**

## 3) desk 版一句话结论
**对 15m breakout-short 来说，好的 follow-up 不像“前一小时已经左偏到瀑布”；它更像“先有一点 failed-bounce / 微右偏，再向下打穿”。**

更直白一点：
- **太左偏**：很多时候已经走太多，追空性价比反而差；
- **太右偏**：更像 squeeze / 反抽主导，也不适合追空；
- **最好的是中性到微右偏**：像“反抽失败后再破位”，更贴近我们要的 short follow-up 形状。

## 4) 本地最小快检怎么做的
我没有重开大回测，只复用现成样本做一刀最便宜的 yes/no 检查。

### 4.1 信号样本
复用：
- `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/signals_btcusd_breakout_short_raw_trigger.csv`
- `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/signals_ethusd_breakout_short_raw_trigger.csv`
- `reports/artifacts/scout_rank73_psar_close_confirmed_followup_15m/signals_solusd_breakout_short_raw_trigger.csv`

### 4.2 价格数据
复用公开可得 Binance perp K 线缓存：
- 5m：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/exec_cache/*__5m__perp.csv`
- 15m：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/perp_cache/*__15m__perp.csv`

### 4.3 最小实验口径
- 资产：`BTC / ETH / SOL`
- 事件：既有 `breakout_short / raw_trigger`
- 解释变量：**信号触发前 1 小时（12 根 5m）log return 的 realized skewness**
- 入场：`next-bar open`
- 持有：`4 根 15m`（约 1 小时）
- 成本：`6 bps/side`，合计 `12 bps round-trip`
- 样本数：`N = 61`

## 5) 快检结果：不是单调关系，而是“中带最好、两头更差”
### 5.1 全样本 baseline
- 全部 `61` 笔 raw breakout-short 的 `4-bar net expectancy ≈ -11.1 bps`
- `win rate ≈ 47.5%`

也就是说，**raw 追空本来就不够好**。这正适合拿来检验一个确认层到底有没有信息。

### 5.2 先看最简单切法：上半区 vs 下半区
以样本中位数 `skew = -0.503` 分两半：

- **下半区（更负 skew）**：`N=31`
  - `mean net ≈ -26.9 bps`
  - `win rate ≈ 45.2%`
  - `MAE ≈ 137 bps`
- **上半区（没那么负 / 更偏右）**：`N=30`
  - `mean net ≈ +5.3 bps`
  - `win rate ≈ 50.0%`
  - `MAE ≈ 95 bps`

这已经说明一个很关键的事：

**“越左偏越能追空”在我们的 15m breakout-short 样本里并不成立。**

### 5.3 真正最干净的 pocket：`0 <= skew < 0.5`
如果把 skew 分成更细的几档，最好的 pocket 不是最负，也不是极正，而是 **中性到微右偏**：

- **`0 <= skew < 0.5`**：`N=11`
  - `mean net ≈ +66.2 bps`
  - `win rate ≈ 54.5%`
  - `MAE ≈ 65.0 bps`
  - `MFE ≈ 130.6 bps`

对照两个坏 pocket：

- **`skew <= -0.5`**：`N=31`
  - `mean net ≈ -26.9 bps`
- **`skew >= 0.5`**：`N=5`
  - `mean net ≈ -57.1 bps`
  - `win rate ≈ 20.0%`

所以更诚实的读法不是“负 skew = short confirmation”，而是：

> **breakout-short 更像吃 failed-bounce 之后的再下破；如果前一小时已经瀑布式左偏，或者反过来过度右偏，追空都容易吃亏。**

## 6) 这条线怎么帮助 `V3 final-verdict / breakout-short follow-up`
它直接回答的就是当前第一优先线里的一个实际问题：

### 不是问“有没有破”
而是问：
**这次破位前 1 小时，到底是“反抽失败后再打穿”，还是“已经走完一大段下跌才姗姗来迟的信号”？**

对 `V3 final-verdict / breakout-short follow-up`，这意味着：
- 若前一小时 **过度左偏**，更应怀疑这是 `late short / waterfall chase`
- 若前一小时 **中性到微右偏**，更像 `failed-bounce → continuation`
- 若前一小时 **极右偏**，更应防止这是 `squeeze / unstable distribution`

这比再加一个泛泛的“强弱指标”更值钱，因为它直接落在我们正在收的 **post-break path / avoid-chase / follow-up honesty** 上。

## 7) 当前最诚实的 desk 定位
**这不是 standalone short alpha。它更像 breakout-short 专用的 pre-entry shape filter。**

而且当前不要把它 shared 到另外两条线：
- 对 `Fib retest_hold`：暂时没证据说明同一条 skew 口径也应该直接搬过去
- 对 `EMA / PSAR raw alpha`：可能可以测，但当前这轮最值钱的位置仍是 `breakout-short follow-up`

## 8) 下一步怎么测（直接可跑）
### 实验 A（优先）：给 `breakout_short` 加一个双端 veto
在现有 `raw_trigger / close_confirmed_n1 / n2 / n3` 上统一加：
- veto if `skew <= -0.5`
- veto if `skew >= 0.5`
- only allow if `-0.5 < skew < 0.5`

主看：
- `post_cost expectancy`
- `false_break_ratio`
- `MAE after entry`
- `trade_count_retention`

### 实验 B：更激进地只保留 `0 <= skew < 0.5`
这条更像“failed-bounce continuation pocket”。

主看：
- 是否能把 raw breakout-short 从负 expectancy 拉到非负/正值
- retention 会不会低到失去执行意义

### 实验 C：只接到 `V3 final-verdict` 的“继续做 / 不继续做”层
不要改主触发，只在 final-verdict 层追加一条：
- `若 pre-break intrahour skew ∈ sweet spot，则允许 short follow-up verdict 更积极`
- `若 skew 在两端极值，则直接降低 verdict / 降仓 / 放弃`

这样最符合它现在的角色：**不是独立触发器，而是 final-verdict 的 path-quality 补充证据。**

## 9) 风险与边界
- 当前只是 **61 笔** 既有样本快检，样本不大，且资产间并不完全一致。
- 这轮只测了 `raw_trigger`，还没把 `close_confirmed_n1/n2/n3` 一起纳入比较。
- skewness 很容易受极端 bar 影响，所以更适合先当 **band / veto**，不适合当连续打分器直接控仓。
- 这条线来自论文里的 **旁支变量重读**，不是论文 headline alpha 的直接复刻；所以我们必须靠后续 clean replication 来决定去留。

## 10) 本轮产物
- 研究笔记：`research/quant_digests/2026-03-20_2008_breakout-short-failed-bounce-skew-band.md`
- 快检目录：`reports/artifacts/quant_digest_intrahour_skew_breakout_short_2026-03-20/`
- 关键文件：
  - `summary.csv`
  - `aggregate_by_quartile.csv`
  - `aggregate_by_bin.csv`
  - `asset_by_quartile.csv`
  - `signals_with_skew.csv`

---
一句话收口：

**对 15m breakout-short，前一小时不是越“左偏”越该追；更值得测的，是把 `中性/微右偏 = failed-bounce continuation` 作为 final-verdict 的 short-side 确认层。**
