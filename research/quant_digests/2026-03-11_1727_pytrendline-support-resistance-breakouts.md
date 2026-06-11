# pytrendline：把 support / resistance / breakout 先做成“可枚举研究对象”，再谈 1~3 根 K 线确认
- 时间：2026-03-11 17:27 UTC
- 类型：GitHub
- 主题标签：trendline / support-resistance / breakout / confirmation / implementation
- 证据类型：代码实现 + 工程经验

## 1. 这次看了什么
这次看的不是论文，而是 **Eduardo Nunez 的 `pytrendline`**。它的价值不在于“直接给你一个买卖策略”，而在于把很多人主观手动画的 support / resistance / 趋势线，拆成一个**可枚举、可打分、可筛选**的研究流程。对当前 `channel / trendline / breakout confirmation` 偏好来说，它是很合适的工程型地基。

## 2. 核心结论
- 代码证据：`pytrendline` 不是随便连两点，而是先识别 pivot，再对 `(i, j)` 组合做**穷举扫描**，检查：这条线能覆盖多少有效触点、误差多大、是否穿过 K 线实体、是否满足 pivot 约束；最后给每条线打分并去重分组。这个流程比“肉眼挑一条最顺眼的线”可审计得多。
- 代码证据：仓库把 **breakout** 明确定义成“趋势线以超过 `breakout_tolerance` 的幅度穿过 candle body”，并允许通过 `ignore_breakouts` 决定是否保留这类线。也就是说，它更适合做**breakout 事件发现器**，而不是直接替你决定要不要追单。
- 工程结论：这个库最大的优点是把支撑/阻力线的候选集、评分、聚类去重都显式产出成 **Pandas DataFrame**；最大的缺点也很明确：因为是**全量穷举，复杂度 O(N^3)**，所以更适合最近窗口的小样本研究，而不适合拿去扫很长的全历史低延迟实盘流。
- 对当前项目最重要的一点是：**趋势线检测层和 breakout confirmation 层应该拆开。** `pytrendline` 更适合前者；而你当前更关心的“突破后 1~3 根阳线确认 / 回踩确认”，应该放在它之后单独建规则，而不是混进同一个 detection 函数里。

## 3. 为什么和当前项目有关
这正好对应 `momentum` 里最近在做的两条线：
- `pytrendline` 适合做 **support / resistance 候选线搜索器**：给你一批可评分的线、breakout line 标记、最近窗口内的结构视图。
- 当前仓库里的 `trendline_breakout_navigator` 更像 **逐 bar 状态机**：跟踪 active support / resistance、区分 provisional line、生成 `tbn_breakout_bull/bear` 与 wick 交互。
- 两者组合起来，刚好形成很清楚的分层：
  1. `pytrendline` 负责“最近这段结构里有哪些值得看的线”
  2. `navigator` 负责“当前这根 bar 相对 active line 发生了什么”
  3. 你自己的确认层负责“突破后要不要等 1~3 根 K / 阳线确认 / 回踩确认再入场”

这比把“画线、判突破、判确认、判入场”全塞在一个黑盒里要健康得多。

## 4. 可复刻的最小实验
- 研究假设：在 15m Crypto 上，**趋势线 breakout 本身可能还不够稳**；但如果把它当作事件触发，再叠加 1~3 根 K 线确认或回踩确认，噪音会明显下降。
- 一个可计算定义：
  - 窗口：最近 `96` 根 15m bar（约 24h）
  - 先用 `pytrendline` 找最近窗口内的 support / resistance 候选线，只保留每个 duplicate group 的 best-scored line
  - 事件：`close` 穿越 best-scored resistance / support line 且超过 `breakout_tolerance`
  - 确认分三组对照：
    1. **confirm1**：突破后下一根仍收在线外
    2. **confirm3**：突破后 3 根内至少 2 根收在线外
    3. **retest**：突破后回踩线位不失守，再二次转强/转弱
- 最小回测切口：
  - 资产：BTC perpetual、ETH perpetual、SOL perpetual
  - 周期：15m
  - 样本：近 180d
  - 对照：裸 breakout vs confirm1 vs confirm3 vs retest
- 最该先看：
  1. `post_cost_return`
  2. `positive_window_ratio`

## 5. 风险与保留意见
- `pytrendline` 的 O(N^3) 决定了它更像**研究工具**，不是随手就能上超长样本或实时大规模扫市场的生产级引擎。
- 它的评分函数是启发式的：高分线不等于高收益线，只说明“更贴线、触点更多、结构上更像一条好线”。
- breakout 在这个库里主要还是**几何事件**，不是完整交易定义；如果直接把“穿线”当入场，仍然很容易被假突破和 wick interaction 打脸。
- 所以最合理的落地顺序不是继续争论“这条线画得准不准”，而是把它固定成**候选线生成器**，然后单独比较 `confirm1 / confirm3 / retest` 哪个最能提升成本后表现。

## 6. 来源
- Nunez, E. (GitHub repository, active by 2021). *pytrendline*.
- Repository: https://github.com/ednunezg/pytrendline
- PyPI metadata in local env: `pytrendline 1.0.1`, Author: Eduardo Nunez, License: MIT
- Local related doc: `/root/clawd/jerry/momentum/docs/SIGNALS_TRENDLINE_BREAKOUT_NAVIGATOR.md`
