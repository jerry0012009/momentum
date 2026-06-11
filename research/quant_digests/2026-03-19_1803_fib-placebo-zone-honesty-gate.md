# 别再把 0.618 当“神位”：在继续收 `Fib confirmation / retest_hold` 之前，更值得先过 `Fib zone vs 非 Fib placebo zone` honesty gate
- 时间：2026-03-19 18:03 UTC
- 类型：论文 + 本地代理快检
- 主题标签：fibonacci / retest-hold / confirmation / placebo / zone / support-resistance / honesty-gate / paper / crypto / 15m
- 证据类型：论文证据 + 本地代理快检

## 1. 这次看了什么
这次看的是 **Prodromos E. Tsinaslanidis、Francisco Guijarro、Nikolaos Voukelatos (2021)** 的论文 **《Automatic identification and evaluation of Fibonacci retracements: Empirical evidence from three equity markets》**。它最值钱的地方，不是又给了一个 Fib 用法，而是把一个我们现在必须先回答的老问题摆到了台面上：**Fib 回撤位到底有没有比“普通回撤区”更特别，还是只是大家习惯拿它当坐标系？**

## 2. 核心结论
- **一句话核心结论：** 在继续给 `Fibonacci confirmation / retest_hold` 叠更多确认层之前，先确认 **Fib 本身是否真有增量信息**；这篇论文给出的答案偏向：**没有显著比非 Fib 区域更特别。**
- **它怎么证明的：** 作者在 **Dow Jones / NASDAQ / DAX** 个股长样本上，先用 **logit** 比较 `Fib zone` 与 `non-Fib zone` 的 bounce probability，再把 **Fib 区域交易规则** 和 **随机 non-Fib 区域**、**buy-and-hold** 做对照。
- 论文最关键的硬结论是：**Fib zone 的 bounce probability 与 non-Fib zone 统计上不可区分**；对应的 **Fib-based trading rule** 也**没有打赢随机 non-Fib zones**，而且整体上**落后于 buy-and-hold**。
- 论文还明确发现：**zone 越宽，检测到“反弹/守住”的概率越高**；但作者把这解释为**主观容差变大、命中自然变多**，不是 Fib 比例本身更神。
- 我这边补的一个 **BTC/ETH/SOL 120d 15m 本地 proxy**，方向也基本一致：把 Fib 容差从 `0 ATR` 放宽到 `0.3 ATR`，`4-bar hold rate` 从 **58.7%** 升到 **64.7%**；但匹配的 **非 Fib 随机回撤区** 也从 **55.8%** 升到 **58.7%**。换句话说，**“zone 放宽更容易守住”不是 Fib 独占结论。**
- 再看一个极简 next-bar-open / hold-8-bars toy backtest：`Fib 0.618` 版本在三资产等权合成上仍只有 **-1.8%**，同时 `4-bar rebreak` 还有 **45.2%**；这更像在提醒我们：**即便 Fib 比随机位稍好，它也远没强到可以单独扛 15m alpha。**

## 3. 为什么和当前项目有关
这篇直接服务当前的 `Fibonacci confirmation / retest_hold` 收口线，而且我觉得它**比继续再补一个普通 veto 更值得先做**。

原因很简单：我们这两天已经连续给 Fib 线补了 `0.618 hold / 0.5 fail`、volume、trend-strength、retest quality 这些层，但还没先问一句更根本的话——**如果把 0.618 换成一堆普通回撤比率，很多“守住”现象是不是一样会发生？**

如果答案是“差不多”，那 desk 更诚实的做法就不是继续神化 `0.618`，而是把 Fib 降级成：
- 一个**结构化坐标系**；
- 一个**候选回踩区**；
- 一个方便交流与执行的 **zone anchor**；
而真正该继续找 edge 的地方，转到 **volume / close quality / asymmetry / trend context / failure path** 这些确认层上。

## 4. 可复刻的最小实验
**研究假设：** 在 `BTC / ETH / SOL perpetual` 的 `15m` 上，当前 Fib 线的大部分有效性，可能来自 **generic retrace geometry + trend context**，而不是 `0.618` 这个比例本身。

**最小实验设计：**
1. `fib_exact`：沿用当前定义，做 `0.618 reclaim + 0.5 fail`；
2. `fib_zone`：保留 Fib 比率，但把触发容差扩成 `0.15 ATR / 0.30 ATR`；
3. `placebo_zone`：把 `0.618` 替换成 `20~50` 个**非 Fib ratio**（排除 `0.236/0.382/0.5/0.618 ± 0.03`），其余规则完全不变，最后看平均结果。

**统一口径：**
- 资产：`BTC / ETH / SOL`
- 周期：`15m`
- 样本：最近 `180~365d`
- 执行：`next-bar open`，`no-overlap`
- 先固定 shared trend/volume context，避免把 state 差异误判成 ratio 差异。

**最该先看 2 个指标：**
- `Δ hold / false_rebreak_4bars`：Fib 是否真的比 placebo 稳定高一截；
- `post-cost expectancy`：Fib 若没有显著高于 placebo，就不该继续被写成“有特殊信息量的 ratio edge”。

**硬判决建议：** 若 Fib 版本在跨资产 / 跨窗口上，既没有稳定高于 placebo 的 hold-rate 差，也没有稳定更好的成本后期望值，就把它**降级为 generic confirmation scaffold**，而不是继续当作 Fib 专属 alpha 收口。

## 5. 风险与保留意见
- 论文样本是**日频股票**，不是 `15m crypto`；它提供的是**评估方法与 honesty gate**，不是可直接照抄的参数。
- 我这轮本地 proxy 只是轻量快检，不是论文级复刻；它更像在验证“zone widening 的机械增益”是否在我们数据上也存在。
- `placebo ratio` 必须批量抽样、固定随机种子、滚动复核，不能只挑几个顺眼比例做 cherry-pick。
- 即便最后证明 Fib 不特殊，它仍然可能保留**表达层 / 执行层 / 仓位层坐标系**价值；被降级的只是“神秘 alpha 地位”，不是它的全部实用性。

## 6. 来源
- Prodromos E. Tsinaslanidis, Francisco Guijarro, Nikolaos Voukelatos. (2021). *Automatic identification and evaluation of Fibonacci retracements: Empirical evidence from three equity markets*. **Expert Systems with Applications**.
- DOI: `10.1016/j.eswa.2021.115893`
- Readable URL: `https://doi.org/10.1016/j.eswa.2021.115893`
- Article URL: `https://www.sciencedirect.com/science/article/pii/S0957417421012495`
- Repo URL: `None found`
