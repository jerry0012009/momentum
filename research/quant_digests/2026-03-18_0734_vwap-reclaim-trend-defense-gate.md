# 别把 retest_hold 写成“回到 Fib 就算数”：session VWAP reclaim + above-VWAP breadth，更像 15m 的防守确认层
- 时间：2026-03-18 07:34 UTC
- 类型：GitHub
- 主题标签：fibonacci/retest-hold/confirmation/vwap/ema/psar/breakout-short/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看的是 GitHub 仓库 `JinHwaChiu/vwap-trend-defense`（2026）。它本来是给 ES/MES 做的 **session VWAP pullback + reclaim** 模板：先要求最近一段时间大多数 bar 站在 VWAP 上方，再等价格回踩 VWAP，最后只在重新收回 VWAP 的阳线触发。对我们现在的 desk 来说，最值钱的不是它的美股早盘背景，而是它把 **“回踩到位”** 和 **“真的站稳”** 拆成了两层：`位置触碰` 不够，必须再过 `session VWAP reclaim + side-breadth` 这一关。这正好能补 `Fibonacci confirmation / retest_hold`，也能顺手服务 `EMA / PSAR` 的角色判断。

## 2. 核心结论
- **一句话核心结论**：对 15m 来说，很多假回踩不是“位置错了”，而是**回到位以后并没有重新夺回当日均价重心**；所以比裸 Fib / 裸 EMA 更值得先测的，是 `retest location + session VWAP reclaim + 最近几根 bar 站位占比` 这套防守确认层。
- **一句话证明方式**：这个 repo 不是讲抽象大道理，而是把条件直接写进代码：`trend filter = 最近 N 根里 >50% 收盘在 VWAP 上方`，`setup = 当前或前一根 low 触到 VWAP 容忍带`，`trigger = 绿色 K 线收回 VWAP`，再配 `swing low` 止损和 `R-multiple` 目标；注释里给出的优化结果显示，作者在 5m 上用 `lookback=6 / swing=3 / tol=0.2% / 2.5R`，得到 `55% win rate`、`PF=1.9` 的局部样本表现，而代码也已经预留了 `15m` 参数组（`lookback=4, swing=2, tol=0.2%, 2.5R`）。
- 最值得复用的不是它的收益数字，而是这套**层级分工**：`VWAP` 负责给出当日动态重心，`above-VWAP breadth` 负责回答趋势是否仍站在强侧，`touch + reclaim` 负责回答这次回踩是否被接住，`swing low + R target` 负责把失效线写清楚。
- 这一轮优先认领它也说得通：它不是偏题新玩具，而是能同时帮助三条收口线里的两条——`Fib / retest_hold` 和 `EMA / PSAR raw alpha focus`；甚至对 `breakout-short follow-up` 也能派生出一个更诚实的镜像版本：**跌破后先等反抽到 VWAP 下沿附近，再看能不能重新压回 VWAP 下方**，而不是跌破就追。

## 3. 为什么和当前项目有关
- 对 `Fibonacci confirmation / retest_hold`：Fib 线位更像“价位许可”，VWAP reclaim 才更像“回踩后有没有重新守住场内平均成本”。也就是说，`0.618` 可以继续负责“回到关键区”，但 `session VWAP reclaim` 更适合负责“这次 hold 是真 hold 还是只是路过”。
- 对 `EMA / PSAR raw alpha focus`：它给了一个比“再多加一根均线”更干净的确认思路——让 EMA / PSAR 继续做方向或结构锚，把 **VWAP 重新站回/跌回** 当成 micro confirmation，减少把均线系统写成自我循环确认的风险。
- 对 `V3 breakout-short follow-up`：repo 本身只有 long 侧，不能直接把多头结论镜像成 short 结论；但它提醒我们，short 侧 continuation 更该先测的是 **underground retest + failed reclaim**，而不是“新低出现就默认继续空”。

## 4. 可复刻的最小实验
- **研究假设**：在 `BTC / ETH / SOL` perpetual 的 `15m` 上，给现有 `Fib retest_hold` 或 `EMA/PSAR continuation` setup 叠加 `session VWAP reclaim + side-breadth gate`，会比裸位置触发更能降低假回踩和成本后打脸率。
- **最小定义**：
  1. 先保留原 setup（如 `Fib reclaim`、`EMA 回踩后继续`、`breakout 后 retest`）；
  2. 定义 `session_vwap` 为 **UTC 日内重置 VWAP**；
  3. long 侧加 `vwap_reclaim = close > session_vwap and (low <= session_vwap * 1.002 or prev_low <= prev_vwap * 1.002)`；
  4. 再加 `breadth_gate = 最近 4 或 6 根里 >50% close 在 session_vwap 上方`；short 侧做对称镜像。
- **最小回测切口**：最近 `180~365` 天，`15m`，`next-bar open`，`no-overlap`，成本至少看 `6 / 10 / 15 bps per side`；先做三臂：`base`、`+ vwap_reclaim`、`+ vwap_reclaim + breadth_gate`。
- **最先看的 4 个指标**：`post-cost return`、`false-retest rate`（入场后 4 根内反向穿回 VWAP 或反向超过 `0.75 ATR`）、`trade_count`、`positive_asset_ratio`。
- **下一步怎么测**：先别把它和一堆 volume / funding 条件一起堆满；第一轮只回答一个最值钱的问题——**对当前 `retest_hold`，救命的是“收回 VWAP”本身，还是“最近几根大多数已经站在 VWAP 同侧”这条 breadth gate？** 如果前者就能明显降 `false-retest rate`，它值得进三条收口线的共享确认层；如果必须叠满很多条件才勉强改善，就说明它更像局部美化，不是当前 desk 的高优先级骨架。

## 5. 风险与保留意见
- 这是 **新仓库工程证据**，不是论文或成熟生产证据；repo 目前 `0 stars / 0 forks`，社会证明很弱。
- 源策略是 **ES/MES 美股早盘 long-only**，而 crypto 是 `24/7`；因此最容易过拟合的地方不是 VWAP 本身，而是 **session 定义**。在 crypto 上不能机械照搬 `9:30-12:00 ET`。
- repo 给出的收益数字没有完整 friction ladder、rolling OOS、cross-asset 验证；所以我们最多应该继承它的 **规则骨架**，不应继承它的收益自信。
- 对 `breakout-short`，必须单独做 short mirror 实验。多头的“回踩后收回 VWAP”并不自动推出空头的“反抽后跌回 VWAP”同样成立。
- 如果已有 `EMA / PSAR` 本身就已经暗含类似“均价重夺回”信息，那 VWAP reclaim 可能只是重复确认，需要用 ablation 明确它是否真有独立增量。

## 6. 来源
- JinHwaChiu. (2026). *vwap-trend-defense*.
  - Venue / DOI：无
  - Repo URL: <https://github.com/JinHwaChiu/vwap-trend-defense>
  - Readable URL: <https://github.com/JinHwaChiu/vwap-trend-defense/tree/main/strategies>
  - Raw strategy URL: <https://raw.githubusercontent.com/JinHwaChiu/vwap-trend-defense/main/strategies/vwap_trend_defense.py>
  - Supporting raw URL: <https://raw.githubusercontent.com/JinHwaChiu/vwap-trend-defense/main/strategies/vwap_reversion.py>
  - Repo API: <https://api.github.com/repos/JinHwaChiu/vwap-trend-defense>
  - Repo metadata snapshot: created `2026-01-24`, updated `2026-01-24`, `0` stars, `0` forks.
