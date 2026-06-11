# 别把 15m 的触发周期固定死：4H/1H 同向时偷 5m BOS，对不齐时退回 15m 确认，更像三条收口线共用的 execution gate
- 时间：2026-03-18 17:30 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/execution/bos/mtf/alignment/filter/repo/crypto/15m
- 证据类型：仓库源码 + 公开 OHLCV / 可快速复现实验

## 1. 这次看了什么
这次看的是 GitHub 仓库 `Frosty098/smc-bos-strategy`（2026-03）里的 `Second_Adj.pine`。repo 表面上是 SMC 结构交易框架，但对我们当前 desk 最值钱的旁支，不是 OB/FVG 这些名词本身，而是一个更朴素的执行层想法：**别把所有 setup 都固定用同一个触发周期；当 `4H bias` 与 `1H trend` 同向时，可以让 `5m BOS` 提前点火；当两者对不齐时，退回 `15m BOS`，别让 micro 噪声替 15m 做决定。**

## 2. 核心结论
- **一句话核心结论**：这份 repo 最值得先偷的不是整套 SMC 语法，而是 `HTF alignment -> execTF` 这条 shared execution rule：**同向时用更快触发，对不齐时提高确认门槛。**
- **一句话证明方式**：源码把规则写得非常直接：`execTF = (alignedBull or alignedBear) ? "5" : (opposedBull or opposedBear) ? "15" : "15"`；随后只在该执行周期上读取 `bosUpExec / bosDnExec`。也就是说，它不是“多看一个周期更安心”的口号，而是把 **高周期方向一致性** 真的落成了 **触发周期切换**。
- repo 还顺手加了一个很轻的 pressure 条件：`bodyPct >= 0.55` 且 `volume > SMA20` 才算 `buyPressure / sellPressure`。这说明它的真正骨架不是复杂对象，而是三层分工：**HTF 给背景，execTF 给触发速度，pressure 给最后一脚确认。**
- 这题现在比继续给三条线各补一个局部滤镜更值得，因为三条线眼下共同缺的，不是第 N 个新指标，而是：**什么时候 15m setup 可以借 5m 提前进，什么时候必须坚持等 15m 自己站稳。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：最该补的不是更多破位后形状，而是 **follow-up short 是否允许借 5m continuation trigger**。若 `4H/1H` 同向向下，可让 `5m BOS` 负责更快 continuation；若 `1H` 和 `4H` 打架，就必须退回 `15m BOS`，减少假跌破后被反抽打脸。
- 对 `Fibonacci confirmation / retest_hold`：Fib 负责位置，alignment gate 负责决定“回踩后是允许看 `5m reclaim`，还是必须等 `15m reclaim`”。也就是：**不是所有 retest 都值得 micro front-run。**
- 对 `EMA / PSAR raw alpha focus`：EMA/PSAR 继续承担方向层，但 entry 不必永远死守 15m。可以改成：**方向仍看 15m/1H，触发周期随上层同向度切换。** 这比直接再叠一个新指标，更像执行层的真实增量。

## 4. 可复刻的最小实验
- **研究假设**：对当前 `breakout_short`、`fib_retest_hold`、`ema_psar_raw`，把 entry trigger 从“永远 15m”改成“`4H/1H` 同向时 `5m`，不齐时 `15m`”，会比继续堆局部过滤器更有效地改善 continuation 质量，同时保留足够交易数。
- **公开数据源**：Binance perpetual `5m / 15m / 1h / 4h` OHLCV 即可；不需要订单簿、OI、资金费率或收费数据。
- **最小可计算定义**：
  1. `4H bias = close_4h > ema200_4h`（空头反之）；
  2. `1H trend = close_1h > ema200_1h`（空头反之）；
  3. 若 `4H` 与 `1H` 同向，则该 setup 允许用 `5m` 的最近摆点 `BOS` 触发；否则只接受 `15m BOS`；
  4. 可选最后再加 repo 的轻 pressure：`abs(close-open)/(high-low) >= 0.55` 且 `volume > SMA20(volume)`；
  5. 第一轮先不要接完整 OB/FVG/Breaker，只测 `execTF switch` 本身。
- **第一轮 bucket**：`base_15m_only` vs `always_5m_confirm` vs `alignment_switch(5m/15m)`；可再补一档 `alignment_switch + pressure`。
- **最先看 4 个指标**：`post-cost expectancy`、`trade count retention`、`false-break / false-hold rate`、`MFE/MAE after entry`。
- **下一步怎么测**：先固定 `BTC / ETH / SOL` perpetual、最近 `180d`、`next-bar open`、`no-overlap`。只回答一个问题：**`4H/1H` 同向时放宽到 `5m BOS`、其余维持 `15m BOS`，能否在交易数保留 ≥70% 的前提下，同时改善 breakout-short 的 follow-up、Fib 的 retest_hold、以及 EMA/PSAR continuation 的成本后质量？** 若这一步都没有增量，就不要继续把它包装成更复杂的多结构框架。

## 5. 风险与保留意见
- 这份 repo 很新、也几乎没有社区验证；它更像研究启发，不是可直接抄去 paper/live 的成熟模板。
- `5m BOS` 很容易把成交频率和噪声一起放大，所以第一轮必须把 `trade retention` 和成本后指标并排看，不能只看命中率。
- repo 还混了 sweep、OB/FVG/EQ、breaker、pressure 等多层对象；如果不做 ablation，很容易把“触发周期切换有效”和“其它 confluence 有效”混在一起。
- `EMA200 4H/1H` 只是最小起点，不代表最终最优。第一轮目标是验证“**周期切换这件事**值不值得存在”，不是先去炼 EMA 参数。

## 6. 来源
- Frosty098. (2026). *smc-bos-strategy*. GitHub repository.
  - Venue / DOI：GitHub / N/A
  - Repo URL: <https://github.com/Frosty098/smc-bos-strategy>
  - Readable URL: <https://github.com/Frosty098/smc-bos-strategy>
  - README: <https://raw.githubusercontent.com/Frosty098/smc-bos-strategy/main/README.md>
  - Main source (`Second_Adj.pine`): <https://raw.githubusercontent.com/Frosty098/smc-bos-strategy/main/Second_Adj.pine>
  - Baseline source (`Oiabm.pine`): <https://raw.githubusercontent.com/Frosty098/smc-bos-strategy/main/Oiabm.pine>
  - Repo metadata snapshot: created `2026-03-04`, updated `2026-03-05`, `0` stars, `0` forks at fetch time.
- Binance USDⓈ-M Futures. *Kline/Candlestick Data*.
  - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
  - 用途：构造 `5m / 15m / 1h / 4h` 多周期对齐与执行周期切换实验。