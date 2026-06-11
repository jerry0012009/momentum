# 2026-04-07 16:50 UTC — Lévy rowscore leader move × follower catch-up basket：fresh intake -> background / P0

- 时间：2026-04-07 16:50 UTC
- 对象：`research/quant_digests/2026-04-07_1549_levy-rowscore-follower-catchup-alpha.md`
- 轮次类型：bot3 auto optimization
- 结论：`fresh intake failed -> background / P0`

## 这轮做了什么
按当前 `cycle_plan` 只执行最前的 pending 小点：判断 `Lévy rowscore leader move × follower catch-up basket` 是否真形成了独立于既有 `major-lead / cross-market ITSM / generic leader-follower` 家族的新 raw alpha 主语，还是只是把熟悉的 lead-lag 排序包装成更复杂的 network-ranking 术语。

本轮只回答三件事：
1. 这份 digest 锁定的 alpha 主语，是否已经明显超出“leaders 先动、followers 下一根补动”的旧 lead-lag 母命题；
2. repo 里的新增信息，是否来自一个新的可交易 pocket，而不是换一种 rowscore / Lévy 语言重述 leader-follower 排序；
3. 与现有库内近邻对象相比，它是否还能保留值得前排占一个 survivor 配额的独立边界。

## 最小证据
### 1) 当前 digest 的可交易翻译仍是标准 lead-lag 骨架
源 digest 自己已经把对象翻译得很直白：
- 先用 rolling lead-lag matrix 给币按 row-score 排序；
- row-score 高的是 leaders、低的是 followers；
- 看 leaders 最新一根收益方向，再去做 follower basket 的同向 catch-up。

这说明 desk 真正拿到手的，不是某个新 microstructure alpha，而仍是 **`leader ranking -> follower basket catch-up`** 这条旧母命题。

### 2) rowscore / Lévy 更像 ranking 技术层，不是新的 raw alpha 主语
这份 repo 的新增主要在于：
- 用 Lévy area / directed network 去估计谁更常先动；
- 用 row-score 做 leader / follower 排名；
- 再配一个组合层与 bot 壳。

但这些增量更接近 **“怎么更花哨地找 leader”**，而不是把 alpha 主语从旧 lead-lag 家族里剥离出来。无论是 digest 中给出的最小实验，还是 repo 的可落地翻译，最后都还是在问：

> leaders 这一根先动后，followers 下一根/下两根会不会补动？

这和我们库里已经存在的 `Rank 171 / volume-ranked theme leader-follower spread`、`Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing`、`major-lead / ITSM` 以及多条 BTC→alt catch-up 线，在 raw alpha 层面是同一家族，而不是一条新的主语。

### 3) 现有库内已经覆盖了“network / routing / follower selection”这类边界
本轮额外对照了库内近邻记录：
- `Rank 249` 已经把 **network follower routing** 单独拿出来审过，保留的核心就是 `leader basket 先动 + selected follower routing 的下一根 spread catch-up`；
- `Rank 171` 已经覆盖了 **ranking-based leader-follower spread** 这一层；
- `major-lead / ITSM` 与多条 `BTC shock -> follower catch-up` 记录，已经覆盖了 **事件驱动/跨市场/跨币种 lead-lag 传导**。

因此，当前对象若想独立成立，必须证明 **rowscore/Lévy 带来了一个旧家族没有的新增 pocket**，例如：
- 明确优于已有 simpler ranking 的 after-cost pocket；
- 或锁定一个只有 directed-network rowscore 才能稳定筛出的 follower 子集。

而当前 digest 并没有把这层增量压清，只说明“可以这样排序、可以这样做篮子、可以接 bot”。这还不够支持独立 `keep_P1`。

### 4) 成本与样本证据反而进一步强化“先别给 survivor”
源 digest 已明确写了两个硬问题：
- 示例回测样本偏短；
- 成本、滑点、冲击处理明显不充分。

也就是说，它既没有证明自己是新主语，也没有给出足够厚的新 pocket；如果现在仍给 survivor 配额，实际上是在为一条旧家族的换壳对象付前排资源。

## 本轮判断
这条线本轮更诚实的记账方式是 `background / P0`，不进入 survivor。原因不是它完全没价值，而是：
1. **alpha 主语不新。** 真正可交易的翻译仍是 `leader ranking -> follower catch-up basket`，属于已存在的 lead-lag / leader-follower 家族；
2. **rowscore/Lévy 目前只是 ranking 技术细化。** 它没有单独压出一个“旧家族做不到、只有它有”的 raw alpha pocket；
3. **证据强度偏弱。** 样本短、成本层薄，连“换个排序法后 edge 更厚”这件事都还没被诚实证明。

因此，本轮不分配新 Rank，不给 `keep_P1`，直接记为 `background / P0`。

## 会改变系统认知的话
`Lévy rowscore leader move × follower catch-up basket` 本轮不成立为新的前排 raw alpha：它给出的可交易主语仍是旧 `leader ranking -> follower catch-up` 家族，rowscore/Lévy 只是在 leader 识别层加了 network-ranking 术语，尚未证明自己压出了独立于 `Rank 171 / Rank 249 / major-lead / ITSM` 的新增 pocket，因此本轮直接记为 `background / P0`。

## 产物
- 源记录：`research/quant_digests/2026-04-07_1549_levy-rowscore-follower-catchup-alpha.md`
- 本轮日志：`research/optimization_loop/2026-04-07_1650_levy_rowscore_follower_catchup_first_verdict_background.md`
