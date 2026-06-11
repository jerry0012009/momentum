# 别把 EMA/PSAR continuation 继续写成二元开关：`EMA spread/ATR + VWAP distance/ATR + volume + ATR expansion` 更像 15m 的 graded admission score
- 时间：2026-03-18 23:18 UTC
- 类型：GitHub
- 主题标签：ema / psar / breakout-short / continuation / score / vwap / atr / volume / regime / filter / repo / crypto / 15m
- 证据类型：源码证据 + 工程迁移假设
- 证据强度提示：**中等偏弱**（规则清楚，但不是论文，也没有同口径 crypto OOS 绩效）

## 1. 这次看了什么
这次看的是 **bptrades (2026), `0dte-momentum-continuation`**。它不是在卖“神奇入场点”，而是把 continuation 质量拆成一个很朴素的 **0~100 分 admission score**：
- `EMA fast/slow` 是否拉开；
- 价格离 `VWAP` 是否足够远；
- 成交量有没有站上 `SMA20`；
- `ATR` 有没有高于自己的均值。

源码把四块各记 **25 分**，总分 `>=75` 才叫 `A+`，`60~74` 叫 `B`。翻成人话：**不是问“能不能做”，而是先问“这笔 continuation 到底有多像样”。**

## 2. 核心结论
- **一句话核心结论**：对当前 `EMA / PSAR raw alpha focus`，更值得先测的不是再加一个新指标，而是把已有 continuation 条件改写成 **graded admission score**。
- **一句话说明它怎么证明**：不是靠论文，而是源码直接把 `EMA gap / ATR`、`price-VWAP gap / ATR`、`volume > volMA20`、`ATR > ATR-MA14` 叠成 4 个 25 分模块，并用 `>=75` / `60~74` 做分层。
- 最值钱的地方不是 `9/21 EMA` 或 `0.75 ATR` 这些默认参数，而是它把不同确认层统一缩放到 **ATR 口径**，避免“价差大只是因为币价高”。
- repo 默认还带一个可选 **15m HTF EMA bias**，说明作者也在做一件我们很熟的事：把 raw trigger 和 higher-timeframe allow/deny 拆开。
- 这对 desk 的启发是：**EMA/PSAR、breakout-short follow-up、Fib retest_hold 都不一定非得再写一个二元 veto；先给 continuation 质量打分，可能更诚实。**

## 3. 为什么这轮值得先写
如果继续沿今天的节奏往三条收口线里塞“又一个单独 filter”，边际价值已经在下降。我们已经补了不少：VWAP、OI、liquidation、FVG、regime matrix、PSAR close-confirm。当前真正还没收干净的，是 **这些确认条件到底怎么组合，组合后该 binary 还是 graded**。

所以这轮主题没有偏离主线，反而正中 `EMA / PSAR raw alpha focus` 的缺口：
- 对 **EMA/PSAR**：把 raw alpha 从“满足 / 不满足”改成“弱 continuation / 强 continuation”；
- 对 **breakout-short follow-up**：跌破后不再只看某一个 veto，而是看 follow-through score 有没有站上 `60/75`；
- 对 **Fib retest_hold**：不是“守住就一律开”，而是守住后再看 volume、ATR、VWAP、EMA spread 有没有一起配合。

## 4. 可复刻的最小实验
### 研究假设
把当前 lane 的二元 continuation gate 改成 **0~100 admission score**，会比单个 yes/no 过滤器更稳定地提升 `post-cost expectancy`，同时减少 `2~4 bar` 内的假延续。

### 最小可计算定义
先冻结一个现成 trigger（推荐先用最干净的 `EMA / PSAR raw lane`），只改 gate：
- `ema_score = min(25, abs(ema_fast - ema_slow) / atr14 * 25)`
- `vwap_score = min(25, abs(close - vwap_ref) / atr14 * 25)`
- `vol_score = 25 if volume > sma(volume, 20) else 0`
- `atr_score = 25 if atr14 > sma(atr14, 14) else 0`
- `admission_score = ema_score + vwap_score + vol_score + atr_score`

其中：
- long 侧要求 `ema_fast > ema_slow`、`close > ema_fast`、`close > vwap_ref`
- short 侧镜像
- `vwap_ref` 第一轮先用 **session VWAP**；若结果像样，再跟已研究过的 **event-anchored VWAP** 做 head-to-head

### 最小回测切口
- 标的：`BTC / ETH / SOL` perpetual
- 周期：`15m`
- 样本：近 `180~365d`
- 执行：`next-bar open`，`no-overlap`
- 成本：先统一跑 `6 / 10 / 15 / 20 bps per side`

### 最小对照组
1. `baseline`：当前二元 gate
2. `score>=60`
3. `score>=75`
4. `score bucket`：`<60 / 60~74 / >=75` 只做分层观察，不急着先做 hard gate

### 第一轮最该看什么
- `post_cost_expectancy`
- `forward_3bar_median_return`
- `flip_to_fail_rate`（入场后 `2~4` 根内失守 EMA fast / VWAP 的比例）
- `trade_retention`（分数提高后，交易数到底掉了多少）

## 5. 风险与保留意见
- 这是 **0DTE intraday repo**，带明确时段过滤；那部分不适合直接搬到 `24/7 crypto`。
- 四块都给 `25` 分很方便，但也很武断；第一轮先接受它是“便宜 baseline”，不要马上去优化权重。
- `session VWAP` 在 crypto 里天然比美股更弱，所以 `vwap_score` 最后可能需要让位给 `anchored VWAP` 或者 `rolling mean price`。
- 这份材料证明的是“规则可写清”，不是“已经有可信 alpha”。如果 `score>=75` 只是把交易数砍得很少却没改善成本后收益，就该停在 backlog。

## 6. 下一步怎么测
最直接的一步：不要把它当 standalone 新策略，先把它接到 **当前最干净的 `EMA / PSAR raw lane`** 上做 overlay。

如果第一轮结果显示：
- `score>=75` 在 `BTC / ETH / SOL` 三个标的都能压低 `flip_to_fail_rate`；
- 同时 `post_cost_expectancy` 没被交易数塌缩拖死；
- 并且 `score bucket` 呈现出比较单调的质量分层，
那它就值得升成 **EMA/PSAR 的 graded continuation admission overlay**。再下一步，才轮到把它借给 `breakout-short follow-up` 和 `Fib retest_hold` 做 shared scoring layer。

## 7. 来源
1. **bptrades (2026)**, *0dte-momentum-continuation*.
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/bptrades/0dte-momentum-continuation
   - Repo URL: https://github.com/bptrades/0dte-momentum-continuation
2. **Raw source code**: `MomentumContinuationProAlgo.pine`
   - Raw URL: https://raw.githubusercontent.com/bptrades/0dte-momentum-continuation/main/MomentumContinuationProAlgo.pine
   - 关键规则：`trendScore = emaStrength + vwapStrength + volStrength + atrStrength`；`A+ >= 75`；`B = 60~74`
3. **Repo metadata API**
   - URL: https://api.github.com/repos/bptrades/0dte-momentum-continuation
   - 关键元数据：`created_at = 2026-02-06T18:35:25Z`，`pushed_at = 2026-02-06T18:38:46Z`
