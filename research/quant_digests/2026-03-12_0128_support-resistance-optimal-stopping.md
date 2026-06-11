# Support / Resistance 不是一句“突破就追”：它也可以被理解成状态切换下的最优买卖问题
- 时间：2026-03-12 01:28 UTC
- 类型：论文
- 主题标签：support-resistance / breakout / pullback / regime / confirmation
- 证据类型：概念地基 / 数学建模论文

## 1. 这次看了什么
这次看的是 **Henderson, Jacka, Liu, Maeda (2021/2025 v2), _The Support and Resistance Line Method: An Analysis via Optimal Stopping_**。这篇不是经验回测文，也不是“又一个自动画线算法”，而是想给传统的 support / resistance 交易法一个更严格的数学解释：**当价格在支撑/阻力附近来回切换、并在真正跌破/突破后发生状态反转时，最优买卖规则长什么样。**

这正好补上当前主线里的一个空缺：前两篇我们已经看了“怎么找线”“怎么把线位变成特征”，但还没正面回答 **support/resistance 交易法本身到底更像什么机制**。这篇给出的答案不是“见线就交易”，而是：**它更像一个 path-dependent regime model 下的最优停时问题。**

## 2. 核心结论
- 论文证据：作者把价格建模成**两种 regime（positive / negative）** 下的过程；在 positive regime 里，某个隐藏固定价位扮演 support，在 negative regime 里同一价位扮演 resistance。**当价格从上向下穿过 `L`，regime 从 positive 切到 negative；当价格从下向上穿过 `H`，regime 从 negative 切到 positive。**
- 论文证据：这不是普通的 exogenous Markov regime-switching。论文明确强调，这里的 regime transition 是**path-dependent** 的：状态切换由价格路径是否击穿关键边界触发，而不是外生马尔可夫链自己跳。
- 论文证据：在这个框架里，作者证明了 value function 的 `C^1` smoothness，并把“什么时候买、什么时候卖”化成**两个相互关联的 free-boundary / optimal stopping 问题**；随后对不同价格动态与不同风险厌恶程度做了数值策略比较，并拿结果去对照传统的 **buy at low / sell at high** 标准规则。
- 对当前项目最重要的启发是：**support / resistance 不是天然等于 breakout-following。** 在某些结构下，它更像“在有效区间内做 buy-low / sell-high；一旦真正击穿边界，再承认状态已变”。也就是说，**反抽确认 / 回踩确认** 不只是经验主义，背后其实对应“先确认 regime 是否真的切换”。

## 3. 为什么和当前项目有关
这篇和你现在的 `channel / support-resistance / breakout confirmation` 偏好非常贴，因为它直接影响系统分层：
- 它支持把 **line touch**、**line break**、**confirmed regime switch** 这三件事分开，而不是把“碰线”“穿线”“入场”混成一个事件。
- 它提醒我们：很多假突破之所以烦人，可能不是线画错了，而是**价格还停留在旧 regime 的区间震荡逻辑里**，你却太早按“新趋势开始”来处理。
- 对 15m Crypto 来说，这篇尤其适合拿来解释为什么 breakout 后常常需要 **1 根确认 / 3 根确认 / 回踩不失守**：这些规则的本质，都是在给“regime 已切换”找更可靠的证据。

## 4. 可复刻的最小实验
- 研究假设：15m Crypto 上，`close` 第一次穿越 support/resistance 时，很多时候仍属于“区间噪音中的暂时越界”；只有当突破后出现额外证据，才更像论文里的**状态反转已完成**。
- 一个可计算定义：
  - 先用当前项目已有的 `trendline_breakout_navigator` 或 `pytrendline` 产出 active support / resistance
  - 对每次穿线事件，区分三层：
    1. `touch_or_cross`：仅触线或首次穿线
    2. `provisional_break`：收盘已在线外，但只持续 1 根以内
    3. `confirmed_switch`：满足以下任一规则
       - **confirm1**：下一根仍收在线外
       - **confirm3**：3 根内至少 2 根收在线外
       - **retest_hold**：突破后回踩原线位不失守，再次转强/转弱
- 最小回测切口：
  - 资产：BTC perpetual、ETH perpetual、SOL perpetual
  - 周期：15m
  - 样本：近 180d~365d
  - 对照：
    1. 第一次穿线即追
    2. `confirm1`
    3. `confirm3`
    4. `retest_hold`
- 最该先看：
  1. `post_cost_return`
  2. `false_break_ratio`（若当前框架还没有，就先补这个统计）

## 5. 风险与保留意见
- 这篇是**数学建模论文**，不是直接用分钟级市场数据做实证 alpha 验证；所以它提供的是“机制视角”，不是现成可搬的胜率数字。
- 论文里的 support/resistance 是**隐藏固定价位 + regime-dependent dynamics**，现实市场比这个复杂得多；Crypto 15m 的支撑阻力通常是移动的、局部的、而且会受流动性和杠杆冲击影响。
- 所以它最适合用来指导**系统分层与确认逻辑**，而不是拿来证明“支撑阻力法一定赚钱”。
- 如果实验结果显示 `confirm1 / confirm3 / retest` 仍然很弱，也不必惊讶：那可能说明当前 active line 定义太粗，或者真正在 Crypto 里有用的不是“静态线位”，而是**线位 + 波动压缩 + 成交量 + funding 时点**的组合。

## 6. 来源
- Henderson, V., Jacka, S., Liu, R., & Maeda, J. (2021; revised 2025). *The Support and Resistance Line Method: An Analysis via Optimal Stopping*. arXiv working paper.
- DOI: https://doi.org/10.48550/arXiv.2103.02331
- Readable URL: https://arxiv.org/abs/2103.02331
- HTML version: https://ar5iv.labs.arxiv.org/html/2103.02331
