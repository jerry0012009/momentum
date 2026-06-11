# 别把 Fib 回踩确认继续写成“到位就算守住”：`方向 + 强度` 多档标签，更像 15m retest_hold 的 admission / sizing layer
- 时间：2026-03-19 05:25 UTC
- 类型：论文
- 主题标签：fibonacci / retest-hold / confirmation / trend-strength / position-sizing / support-resistance / paper / crypto / 15m
- 证据类型：论文证据

## 1. 这次看了什么
这次看的是 Khattak et al. (2024) 的论文《Profitability trend prediction in crypto financial markets using Fibonacci technical indicator and hybrid CNN model》。它表面上是在做 BTC 1m 的深度学习分类，但对我们更有价值的不是 CNN 本身，而是一个很适合 desk 侧偷出来单测的旁支：**Fibonacci 不一定只该回答“有没有回到位”，也可以回答“这次回到位以后，后续延续的强弱该分几档”**。

## 2. 核心结论
- **一句话核心结论：** Fib 更像该先做成“方向 + 强度”的分档确认层，而不是 `touch 0.618 = 开火` 的二元开关。
- **它怎么证明的：** 论文用 BTC/USDT 的 **1-min 公共 OHLCV**（2022-10-07 至 2022-12-13，**97,929** 条样本），把 Fibonacci retracement 当成额外 support/resistance 特征，比较“有 / 无 Fib”与“binary / 4-class / 6-class / 8-class / 10-class”标签后的测试表现与 ROI。
- 加入 Fibonacci 特征后，作者报告 **44% 的模型配置测试表现改善**，**68% 的模型配置盈利性改善**；说明 Fib 不是只能当图上画线，它确实能给短周期模型补可用信息。
- 更关键的是，作者没有只做二元方向，而是把未来价格变化拆成强弱档。文中给的结论是：**trend-strength prediction** 相比纯 binary，更容易把 ROI 改善体现到交易层；其中 long strategy 的最大改善达到 **+6.89%**，long-short ROI 改善出现在 **17/25** 个配置里。
- 但这不等于“照抄论文模型”。样本很短、周期是 **1m**、而且高阶多分类越细并不稳定——例如文中也出现 8-class / 10-class 配置走坏。真正值得复用的是：**把 Fib 从位置许可层，升级成强弱分层 / 仓位分层。**

## 3. 为什么和当前项目有关
这篇最直接服务的是当前的 `Fibonacci confirmation / retest_hold` 收口线。

我们最近已经反复补了 `0.618 hold / 0.5 fail`、VWAP reclaim、volume、structure reclaim 这些“有没有守住”的确认模块，但还比较少认真问：**守住以后，这次 continuation 到底是弱修复、中等 continuation，还是值得给更高预算的强 continuation？**

这篇论文给的启发，不是让我们把 15m `Fib retest_hold` 改成 ML 分类器，而是提醒：
- `Fib` 负责回答**位置**；
- `trend-strength bucket` 负责回答**这次守住后的延续质量**；
- admission / sizing 不一定非得二元化，可以变成 `deny / half-size / full-size`。

换句话说，它比继续再补一个普通 veto 更值得做，因为它正好能把当前 Fib 线从“是否成立”推进到“成立以后配多大”。

## 4. 可复刻的最小实验
**研究假设：** 对 `BTC / ETH / SOL` 的 `15m` perpetual，`Fib retest_hold` 若改成“位置 + 强度分档”而不是二元确认，能在不过度砍样本的前提下改善 post-cost expectancy，并减少把弱 bounce 误判成可重仓 continuation。

**最小可计算定义：** 先保留现有 base event：`impulse leg -> 回踩 0.5/0.618 -> 0.618 未收破`。然后把 admission 分成三档：
1. `weak`：触及 `0.618` 后，只是守住，但确认 bar 收盘仍在 `0.5` 下方；
2. `medium`：触及 `0.618` 后，确认 bar 收盘重新站回 `0.5` 上方；
3. `strong`：在 `medium` 基础上，再额外满足 `收回 0.382` **或** `突破 retest bar high`。

**最小回测切口：**
- 资产：`BTC / ETH / SOL` perpetual
- 周期：`15m`
- 样本：最近 `180 ~ 365` 天
- 版本：
  - `base_binary`：现有 `hold / fail` 二元版本
  - `strength_filter`：只做 `medium + strong`
  - `strength_sizing`：`weak=0`、`medium=0.5x`、`strong=1.0x`

**最该先看 2 个指标：**
- `2~4 bar fail rate`：分档后，弱 bounce 是否被更诚实地剔掉；
- `post-cost expectancy`：`medium/strong` 或分档 sizing 是否比 binary 更稳。

如果第一轮就看到 `weak` 桶的 fail rate 显著更高，而 `medium/strong` 保住了大部分有效样本，这条线就值得升成 `Fib retest_hold` 的正式 admission / sizing layer。若三档之间没有可分性，就说明论文里的“strength”更依赖 1m + ML 表达，在我们 15m 规则化框架里未必可迁移。

## 5. 风险与保留意见
- 论文样本很短，只覆盖 **2022-10 至 2022-12** 的 BTC 1m；不能把其 ROI 数字直接当成 15m 可复制结论。
- 论文的 strength 标签本质上是**未来价格变化分层**，我们这里把它翻译成“规则化 admission 分档”，属于 desk-friendly 改写，不是原式复刻。
- 这篇证据更像在证明“Fib 值得从二元线位升级为 richer state”，不是在证明某个具体 `0.5 / 0.618 / 0.382` 组合必胜。
- 若交易成本、滑点、确认延迟偏大，`strong` 桶可能改善胜率却损失 R multiple；所以必须看 **post-cost**，不能只看 hit rate。

## 6. 来源
- Bilal Hassan Ahmed Khattak, Imran Shafi, Chaudhary Hamza Rashid, Mejdl Safran, Sultan Alfarhood, Imran Ashraf. (2024). *Profitability trend prediction in crypto financial markets using Fibonacci technical indicator and hybrid CNN model*. Journal of Big Data.
- DOI: `10.1186/s40537-024-00908-7`
- Readable URL: `https://journalofbigdata.springeropen.com/articles/10.1186/s40537-024-00908-7`
- PDF URL: `https://link.springer.com/content/pdf/10.1186/s40537-024-00908-7.pdf`
