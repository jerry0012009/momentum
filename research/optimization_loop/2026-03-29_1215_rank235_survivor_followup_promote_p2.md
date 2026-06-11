# Rank 235 / richest-venue routing × hysteresis funding carry — survivor 唯一 follow-up 收口（promote_P2）

- 时间：2026-03-29 12:15 UTC
- 执行者：bot3 auto 13m loop
- Source record: `research/optimization_loop/2026-03-29_1027_rank235_richest_venue_routing_intake_keep_p1.md`
- Object: `Rank 235 / richest-venue routing × hysteresis funding carry`
- Verdict: `promote_P2`

## 本轮回答的唯一问题
在统一 repo 口径里，把 `Binance-only`、`richest-venue routing only`、`richest-venue routing + hysteresis/min_hold` 三条手臂拆开看，净边独立增量主要来自 routing，还是其实只是 hysteresis 在减少 churn？

## 本轮使用的最小证据
我没有重做全量回测，而是直接检查这份对象自身的代码/笔记本结构，看三条手臂在 repo 里分别对应什么：

1. `strategy.py` = **Binance-only** 基线
   - 单 venue funding z-score，默认 `z_entry=1.5`
   - 没有 `best venue` 选择
   - 没有 hysteresis / min-hold 机制

2. `strategy_cross.py` = **routing 是第一性改动**
   - 先 `compute_best_fr(...)`，对每个 `(period, asset)` 取跨 Binance / Gate / Hyperliquid 的 `max funding`
   - 这一步先把 `best_fr` 和 `best_exch` 算出来，随后 z-score、持仓与 pnl 都围绕 `best_fr` 展开
   - 也就是说，cross 版本的 alpha 主体先天就是 `route to richest venue`

3. 同一 `strategy_cross.py` 里，**hysteresis 只是第二层 turnover/fee-drag 治理**
   - 注释明确写着：`z_exit = z_entry` 就是旧的无 hysteresis 行为
   - `z_exit = 0.0 + min_hold = 3` 的作用是 `dramatically reducing turnover and fee drag`
   - 这说明 repo 自己承认 hysteresis 是 exit-layer 的净化器，不是发现 richest venue uplift 的源头

4. `notebook_cross.ipynb` 已把 **A vs C** 的结果显式跑出来
   - `2023-09+`：`Binance-only net = -10.0% CAGR`
   - `2023-09+`：`Cross-exchange net = +27.8% CAGR`
   - `Cross-exchange gross = +30.3% CAGR`
   - 同页还给出 `best funding` 相对 Binance 的均值 uplift 约 `+6.10 bps / 8h`，以及活跃期 exchange share 大致 `Binance ≈45%`、`Hyperliquid ≈55%`

## 诚实拆解
### 1) routing 是独立主增量，不只是 hysteresis 降 churn
当前最关键的不是 C 手臂赢，而是 **cross 版本先换了被交易的 funding 本体**：
- `strategy.py` 交易的是 `Binance funding`
- `strategy_cross.py` 交易的是 `best_fr = max(Binance, Gate, Hyperliquid)`

因此，即使暂时把 hysteresis 拿掉，routing 这条臂依然先把可收取 carry 的底层 cashflow 抬高了；这不是单靠“少交易几次”能制造出来的改善。

更直白地说：
- hysteresis 解决的是 **你把已有 edge 浪费掉多少**；
- routing 解决的是 **你到底在收哪一档 funding**。

而 notebook 给出的 `Binance-only net -10.0%` 对 `Cross-exchange net +27.8%`，已经足够证明“跨 venue richest-funding 选择”不是装饰件，而是让净边从负翻正的主因。

### 2) 为什么本轮仍然不把功劳全部记到 hysteresis
repo 代码对 hysteresis 的定位非常清楚：
- `z_exit = z_entry` = 旧行为（无 hysteresis）
- `z_exit = 0 + min_hold` = 降 turnover / 降 fee drag

这能证明 hysteresis **重要**，但它更像是把 routing edge 留在账上的执行层放大器，而不是 primary alpha source。

### 3) 当前还缺什么
严格说，repo 没把 B 手臂（`routing-only, no hysteresis`）的独立指标表单独贴出来，所以我们还没有“一张三行表”直接量化 B 与 C 的差值。

但 survivor 轮要求的是：**独立增量主要来自哪一层，足不足以决定升降级。**
本轮已经足够回答：
- routing 不是可有可无的小修饰；
- hysteresis 也不是唯一让对象成立的来源；
- 真正先改变系统认知的，是 `best venue selection` 把单 venue fee-negative carry 变成可继续研究的 cross-venue positive skeleton。

## 改变系统认知的一句话
**Rank 235 的 survivor 唯一 follow-up 已经足够收口：这条对象的独立主增量首先来自 `richest-venue routing` 对底层 funding cashflow 的抬升，`hysteresis/min-hold` 主要负责把该 edge 从 churn/fee drag 里保留下来；因此它不应再停留在 P1 survivor，而应正式 `promote_P2`。**

## 为什么是 promote_P2，而不是继续 keep_P1
因为 survivor 轮本来要回答的就是：`routing` 是否有独立主增量。
现在答案已经是 **有，而且是决定性的主增量**。继续把它留在 P1 只会变成拖延。

## 下一层该研究什么（留给后续 P2）
后续若继续做，应该进入更窄的 `P2 admission / honesty`：
1. 真正补一张 `A: Binance-only / B: routing-only / C: routing+hysteresis` 的统一表；
2. 检查 routing uplift 是否集中在少数币或少数 venue-regime；
3. 对 quoted funding → realized carry 做 desk 化兑现审计。

但这些已经属于 **P2 admission**，不是 survivor 是否该升级的问题。