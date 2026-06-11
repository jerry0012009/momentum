# 别把 retest_hold 继续写成二元开关：先给回踩质量打分，才像 15m 的 shared confirmation layer
- 时间：2026-03-18 11:51 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/pullback/atr/volume/score/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
这次看的是 GitHub 仓库 `nirujan123/Pullback-Quality-Strategy`（2026），核心脚本叫 **Continuation Quality Index (CQI)**。它原本是一个偏高周期的 long-only pullback 策略，但真正值得我们 desk 借的不是它的 4H / Daily 回测，而是它把“顺势回踩值不值得做”拆成了一个 **0~100 的质量分数**：`EMA 结构`、`ATR 计量的回踩深度`、`回踩时是否缩量`、以及 `reclaim / continuation trigger`，各自占不同分值。对当前三条收口线来说，这比继续给每条线单独补一个新过滤器更像共享确认层。

## 2. 核心结论
- **一句话核心结论**：对 `15m` 来说，`retest_hold` 最值得先测的不是再加一条新线，而是把回踩写成“质量评分题”——趋势、深度、参与度、触发各自记分，分数够才放行。
- **一句话证明方式**：这个 repo 直接把逻辑写进 Pine：`uptrend=30分`、`pullbackInZone=30分`、`lowVolPullback=20分`、`entryTrigger=20分`，默认阈值 `80` 分；其中回踩深度用 `recentHigh - close` 除以 `ATR`，理想区间是 `0.8~2.2 ATR`，缩量定义是 `volume < 0.9 * volMA20`，触发则看 `EMA reclaim` 或 `break previous high`。
- 对 desk 最值钱的启发是：**EMA / PSAR 不该继续单扛 entry**，它们更像 `trendPts`；`Fib / breakout retest` 也不该再被写成“碰到位置就算守住”，而该进入 `zonePts + volPts + triggerPts` 这套记分框架。
- 这比继续围绕某一条线单独补材料更值得，是因为它能同时服务三条收口线：`Fibonacci retest_hold` 需要更诚实的 hold 定义，`breakout-short follow-up` 需要 mirror 版的 rebound-quality score，`EMA / PSAR raw alpha` 则需要被降级成打分卡里的一部分，而不是全部答案。
- repo README 自己也写得很老实：当前结果只是 **modest positive expectancy, regime-dependent performance**。这反而是优点——说明我们该继承的是**评分骨架**，不是作者的周期与绩效口径。

## 3. 为什么和当前项目有关
- 对 `Fibonacci confirmation / retest_hold`：Fib 继续负责“回踩到哪”，CQI 负责“这次回踩质量够不够”。`0.5 / 0.618` 可以映射成 zone，缩量回踩和 reclaim 负责确认。
- 对 `V3 final-verdict / breakout-short follow-up`：可直接写 short mirror：先看跌破后的反抽深度是否仍在可接受 ATR 区间，再看反抽是否缩量，最后看是否重新压回弱侧；这样比“跌破就追”更像 post-break path 过滤。
- 对 `EMA / PSAR raw alpha focus`：EMA / PSAR 最合适的角色，不是生成完整 alpha，而是给 shared score 提供 `trendPts` 或 `biasPts`。这更符合最近几轮对它们角色的降级重估。

## 4. 可复刻的最小实验
- **研究假设**：在 `BTC / ETH / SOL` perpetual `15m` 上，把现有 `Fib retest_hold`、`breakout retest`、`EMA/PSAR continuation` setup 改写为统一 `pullback_quality_score`，会降低假 hold / 假 continuation，同时比简单堆叠二元过滤器更容易做 ablation。
- **最小定义**：
  1. `trendPts(0/30)`：`EMA9 > EMA21` 且斜率同向；若走 `EMA/PSAR` 线，也可改成 `15m EMA aligned + 1h PSAR bias`；
  2. `zonePts(0/30)`：回踩/反抽深度落在 `0.6~1.8 ATR`；long 侧相对最近确认高点或 Fib `0.5~0.618`，short 侧对称；
  3. `volPts(0/20)`：回踩/反抽段成交量 < `0.9 * SMA20(volume)`；
  4. `triggerPts(0/20)`：long 看 reclaim EMA/关键位或突破前一根高点，short 看压回 EMA/关键位下方或跌破前一根低点；
  5. `score = trendPts + zonePts + volPts + triggerPts`，先测 `>=60` 与 `>=80` 两档。
- **最小回测切口**：近 `180~365` 天，`15m`，`next-bar open`，`no-overlap`，成本先看 `6 / 10 / 15 bps per side`；先做 `base`、`base+zone`、`base+zone+vol`、`base+full score` 四臂。
- **最先看的 4 个指标**：`post-cost return`、`false-hold / false-follow-through rate`（入场后 4~8 根内反向穿越 setup 失效线）、`trade_count`、`positive_asset_ratio`。
- **下一步怎么测**：第一轮别急着找最佳阈值，先回答一个更值钱的问题——**增量主要来自“ATR 深度写对了”，还是“缩量 + trigger 组合”写对了？** 如果只有全叠满才有效，这套分数只是包装；如果某一项单独就明显改善 false-hold rate，它才配进入主线。

## 5. 风险与保留意见
- 这是一个 **很新的小仓库**，代码短、证据弱，社会证明几乎没有；当前只能当作规则骨架，不是 validated alpha。
- repo 主要测试 `4H / Daily` 且只有 long 侧；下放到 `15m`、再镜像到 short 侧，都会引入额外噪音与样本偏差。
- `recentHigh - close` 这种回踩定义，在高频 crypto 上可能把结构回踩偷换成短窗波动回撤；需要和 confirmed swing / breakout pivot 版本做对照。
- score 模型很容易变成“每项都看起来合理，但信息彼此重叠”；必须做分项 ablation，防止 EMA、Fib、trigger 实际上在重复表达同一件事。

## 6. 来源
- Nirujan123. (2026). *Pullback-Quality-Strategy / Continuation Quality Index (CQI)*.
  - Venue / DOI：无
  - Repo URL: <https://github.com/nirujan123/Pullback-Quality-Strategy>
  - Readable URL: <https://github.com/nirujan123/Pullback-Quality-Strategy/blob/main/README.md>
  - Raw strategy URL: <https://raw.githubusercontent.com/nirujan123/Pullback-Quality-Strategy/main/src/CQI_v1_3_strategy.pine>
  - Repo API: <https://api.github.com/repos/nirujan123/Pullback-Quality-Strategy>
  - Repo metadata snapshot: created `2026-02-19`, updated `2026-02-19`, `0` stars, `0` forks.
