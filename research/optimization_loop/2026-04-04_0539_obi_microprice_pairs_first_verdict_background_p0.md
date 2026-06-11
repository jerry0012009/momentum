# Rank 325 intake verdict — OBI / microprice pairs shell 收口到 background/P0

- 时间：2026-04-04 05:39 UTC
- 对象：`research/quant_digests/2026-04-04_0416_obi-microprice-pairs-shell-alpha.md`
- 本轮动作：fresh intake first verdict
- 结论：`background/P0`

## 这轮实际回答了什么
这条 intake 不是空壳。repo 主语是清楚的：

1. **base alpha**：`cointegrated spread z-score fade`
2. **执行 veto**：`microprice / OBI`
3. **结构完整度**：有 pair admission、entry/exit、stop、kill switch 和 live execution 原型

也就是说，它确实不是“单纯把盘口指标包装成 alpha”。如果只问“有没有一个能读懂的策略壳”，答案是有。

但 bot3 这轮要回答的不是“能不能写成 digest”，而是“它值不值得占当前前排资源”。这一步的答案是否定的。

## 为什么这轮不记成 keep_P1
### 1) 新信息增量不够大，主要还是“pairs MR + microstructure veto”的旧主题再包装一遍
当前运行态里，pairs / stat-arb 主线已经有前排对象：

- `Rank 322 / cointegrated spread z-score × stop-loss/time-exit` 已经进入 `Active P2`
- 近期研究池里也已经有多条 `OBI / microprice / orderbook veto` 相关 digest

这条 repo 的新增价值主要是把这些部件放进同一套 GitHub repo 壳里，而不是给出一条比现有前排更独特的新 lane。换成人话：

> 它更像“把已有 pairs + veto 思路接成了工程样机”，不是“又发现了一条全新、值得抢占 survivor 槽位的 raw alpha”。

### 2) repo as-is 仍停留在“值得拆件借鉴”，还不到“值得前排继续追”的程度
digest 已经把 repo 的关键脏点写得很清楚：

- research / optimizer / live engine 的 schema 有断裂，要靠 `fix_strategies.py` 补救
- pair universe 含大量噪声腿和 meme/new listing 组合
- `1h admission -> 1m/tick execution` 存在明显频率断层

这些问题不只是实现瑕疵，它们会直接影响我们对“short-cycle desk lane 是否诚实可迁移”的判断。当前 digest 里给出的 desk 化建议，本质上已经是：

- 把 universe 缩到主流腿
- 把信号压回 `15m`
- 把 `1m/5m` 降成 execution veto

一旦做完这一步，真正被留下来的可迁移核心，实际上又回到了：

> `major-coin pairs spread fade` + `orderbook veto`

而这条 lane 的更干净版本，当前已经由 `Rank 322` 在前排承接了。

### 3) 当前没有必要再让它挤占唯一 survivor 槽位
policy 明确要求前排槽位稀缺使用。当前已经有：

- `Surviving candidate slot = Rank 324`
- `Active P2 slot = Rank 322`

在这种情况下，新的 fresh intake 只有在**明显带来新的 raw alpha 主语、或比现有前排更有迁移价值**时，才值得记成 `keep_P1`。这条 OBI / microprice pairs shell 做不到这一点：它更像对现有 pairs 主线的工程化复述，而不是新的主线对象。

## 这轮改变了什么系统认知
这条 repo 仍然有研究价值，但它的价值定位已经可以诚实收口为：

> **它是 `pairs mean reversion + execution veto` 的可拆件 repo 壳，不是需要占用前排资源的新 survivor。**

所以本轮 first verdict 直接记为：

- 正式分配 `Rank 325`
- 结论：`background/P0`
- 原因：主语清楚，但新增信息不足以超过当前前排 pairs 主线；更适合作为 `Rank 322` 一类对象的实现参考/旁证，而不是新的前排候选

## 最终落点
- `Rank 325 / OBI-microprice pairs shell`
- verdict: `background/P0`
- 不进入 `Surviving candidate slot`
- 不改动当前 `Active P2` / `Surviving candidate` 的前排承接关系
