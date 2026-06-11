# Support / Resistance 不一定先当买卖点，也可以先当“结构特征”：把线位信息喂给模型或确认层
- 时间：2026-03-11 21:28 UTC
- 类型：论文
- 主题标签：support-resistance / breakout / confirmation / feature-engineering / alpha
- 证据类型：论文证据 + 工程迁移假设

## 1. 这次看了什么
这次看的是 **Chan, Phoong, Cheng, Chen (2022), _Support Resistance Levels towards Profitability in Intelligent Algorithmic Trading Models_**。它和前面几篇“趋势是否存在”“形态能否程序化”的角度不一样：这篇更关心的是，**support / resistance 能不能从主观画线对象，变成能稳定提升交易模型表现的输入特征。**

这对当前 `channel / trendline / support-resistance / breakout confirmation` 的学习阶段很贴，因为你现在最需要的，不是再听一遍“阻力突破后可能涨”，而是知道：**这些线位信息到底该放在系统的哪一层。**

## 2. 核心结论
- 论文证据：作者提出了一套**自动化识别 meaningful support / resistance levels** 的方法，并把这些线位进一步工程化成模型输入特征，而不是只拿来做主观画线。
- 论文证据：按论文摘要，加入这些 **Support / Resistance input features** 后，和不含这些特征的同构模型相比，模型在 **8 个货币对**上的**聚合盈利表现提高了 65%**。
- 论文证据：摘要还明确说，含 / 不含 Support / Resistance 特征的两组同构智能交易模型之间，其**盈利分布存在统计显著差异**。也就是说，这不是只看一两个案例的偶然差别。
- 对当前项目最重要的启发是：**support / resistance 更像“结构上下文特征”，而不一定先是独立下单信号。** 与其直接交易每一次碰线/穿线，不如先把“离关键线多远、是否刚突破、是否回踩后站稳”这类信息提取出来，再喂给 breakout / confirmation 规则层。

## 3. 为什么和当前项目有关
这篇很适合放在当前主线里，因为它刚好夹在两个层级之间：
- 它比 `pytrendline` 那种“怎么找线”更往前一步：不只找线，而是强调**线位信息如何进入交易模型**。
- 它又比“直接上复杂机器学习”更实用：即便你暂时不做 ML，也能先把 paper 的思路翻译成**规则层特征工程**。

对 15m Crypto 来说，最自然的迁移不是“照搬论文的智能模型”，而是先把以下几类特征从线位中抽出来：
- `dist_to_resistance` / `dist_to_support`
- `breakout_distance`（收盘离突破线有多远）
- `bars_since_breakout`
- `retest_happened`
- `retest_hold`（回踩是否守住）
- `close_outside_count_3`（突破后最近 3 根里有几根收在线外）

这样一来，support / resistance 就不再只是图上两条线，而是能直接进入 A/B 对照实验的**确认层变量**。

## 4. 可复刻的最小实验
- 研究假设：15m Crypto 上，support / resistance 的价值不一定体现在“裸线位交易”本身，而更可能体现在**提升 breakout confirmation 质量**。
- 一个可计算定义：
  - 先用当前项目已有的 `trendline_breakout_navigator` 或 `pytrendline` 产出最近窗口内的 active / best-scored support-resistance line
  - 对每个 breakout 事件，构造以下特征：
    - `dist_to_line_at_break`
    - `breakout_close_excess`
    - `confirm_1bar`（下一根是否仍收在线外）
    - `confirm_3bar`（3 根内至少 2 根是否收在线外）
    - `retest_hold`（突破后回踩线位是否守住）
  - 然后比较：
    1. 裸 breakout
    2. breakout + `confirm_1bar`
    3. breakout + `confirm_3bar`
    4. breakout + `retest_hold`
    5. breakout + 上述线位特征的简单打分/逻辑组合
- 最小回测切口：
  - 资产：BTC perpetual、ETH perpetual、SOL perpetual
  - 周期：15m
  - 样本：近 180d~365d
- 最该先看：
  1. `post_cost_return`
  2. `positive_window_ratio`

## 5. 风险与保留意见
- 这篇论文的主场景是**intelligent algorithmic trading models + FX pairs**，不是 Crypto 15m，也不是纯规则化 breakout 系统。
- 论文摘要里的 `+65% aggregate profitability` 是很吸引人的数字，但它代表的是**相对同构模型的增量改善**，不是“support / resistance 单独就很强”。
- 这也提醒我们别误读：它支持的是“线位信息有增量价值”，并不自动等于“每次阻力突破都值得追”。
- 所以下一步最值得测的，不是继续争论“线画得准不准”，而是看：**哪一种 confirmation（1 bar / 3 bar / retest）最能把这些线位特征转成成本后可用的提升。**

## 6. 来源
- Chan, J. Y.-L., Phoong, S. W., Cheng, W. K., & Chen, Y.-L. (2022). *Support Resistance Levels towards Profitability in Intelligent Algorithmic Trading Models*. Mathematics, 10(20), 3888.
- DOI: https://doi.org/10.3390/math10203888
- Readable URL: https://www.mdpi.com/2227-7390/10/20/3888
- Semantic Scholar page: https://www.semanticscholar.org/paper/d50ace5ffda8fcf2916de781b99f39d1f6747d9f
