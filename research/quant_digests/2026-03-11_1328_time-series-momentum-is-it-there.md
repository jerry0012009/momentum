# Time Series Momentum: Is It There?：别把“策略赚钱”直接当成“简单动量信号已被证明”
- 时间：2026-03-11 13:28 UTC
- 类型：论文
- 主题标签：trend / momentum / alpha / validation
- 证据类型：论文证据 + 工程迁移假设

## 1. 这次看了什么
这次看的是 **Huang, Li, Wang, Zhou (2020), _Time series momentum: Is it there?_**。它非常适合衔接 Jerry 最近那个关键疑问：**简单动量因子是不是太容易、会不会其实并没有我们想的那么“真”。** 这篇论文不是再给 TSMOM 站台，而是回到原始证据链，重新检查“过去 12 个月收益预测未来 1 个月收益”这件事到底有多扎实。

## 2. 核心结论
- 论文证据：作者用与 Moskowitz, Ooi, Pedersen (2012) 相同的 55 个资产样本重做检验，发现**逐资产 time-series 回归的证据很弱**：在 10% 显著性水平下，**55 个资产里有 47 个 t 值低于 1.65**；样本外上，也只有 **3 个资产**给出显著的 OOS `R²`。
- 论文证据：经典 pooled regression 看上去很强，作者也复现出 **t = 4.34**，但用 bootstrap 校正后，5% 临界值约为 **12.53**（parametric wild bootstrap）和 **4.83**（nonparametric pairs bootstrap），所以**这个高 t 值并不够可靠**。换句话说，pooled 显著性可能被高估了。
- 论文证据：TSM 策略虽然能赚钱，但其表现和一个**不要求可预测性**的替代策略非常接近。作者构造了 `TSH (time-series history)`：只按资产历史平均收益的正负做多空。结果显示 **TSM 与 TSH 的平均收益和风险调整收益差异都接近 0**，而且两者的盈利主要都来自 **long leg**，short leg 并不显著。
- 对当前项目最重要的启发是：**一个回测赚钱的“动量策略”，并不自动等于“简单 past-return sign 这个信号本身有稳定 alpha”。** 收益有可能来自长期均值差异、权重设计、波动率缩放，或者别的结构性暴露。

## 3. 为什么和当前项目有关
这篇对 `momentum` 当前阶段很关键，因为你现在正处在“先找基础 alpha”的阶段，最危险的坑之一就是：**把策略收益错认成信号证据。** 它和 15m 主线的关系主要在三点：
- 它直接回应了“**简单动量会不会太容易、会不会其实没那么有效**”这个问题。答案不是简单的“会”或“不会”，而是：必须把**信号层**和**加权/风控层**拆开看。
- 它提醒你不要只看 pooled 或 overall 表现。对 15m Crypto 来说，更该看的是：**逐资产、逐窗口、样本外** 上，裸 `sign(mom_N)` 到底有没有稳定信息。
- 它也说明：如果未来你的 15m 趋势系统主要靠 EMA 方向层、过滤器、仓位缩放、风险控制赚钱，那未必坏；但这代表你找到的是**系统 alpha**，不一定是“最朴素 past-return 动量 alpha”。

## 4. 可复刻的最小实验
- 研究假设：如果 15m 上的简单动量信号真的有信息，它应当在**逐资产 OOS** 上，明显好于“不依赖 serial predictability”的漂移型基线，而不是只在 pooled / vol-scaled 结果里显得漂亮。
- 一个可计算定义：
  - `TSM_N`: `signal_t = sign(close_t / close_{t-N} - 1)`
  - `TSH_like`: `signal_t = sign(expanding_mean(ret_{1:t-1}))`，即只根据历史平均收益方向做多空，不要求最近 N 根存在 serial momentum
  - 先都用**等权**，再各自加一版 **vol-scaling**，防止把仓位层效果误认成信号层效果
- 最小回测切口：
  - 资产：BTC perpetual、ETH perpetual、SOL perpetual；若数据方便，可扩到前 10~20 个高流动 perp
  - 周期：15m
  - 样本：近 365d
  - 对照：
    1. 等权 `TSM_N`
    2. 等权 `TSH_like`
    3. vol-scaled `TSM_N`
    4. vol-scaled `TSH_like`
- 最该先看：
  1. `post_cost_return`
  2. `positive_asset_ratio`（或至少逐资产 OOS 胜出比例）

## 5. 风险与保留意见
- 这篇论文讨论的是**月频跨资产 TSMOM**，不是 15m Crypto；它更像在教你“如何验证一个动量因子是不是被误读”，而不是直接给分钟级信号。
- 论文并没有证明“趋势不存在”，它的更准确结论是：**‘constant 12-month return rule’ 这种简单定义的证据没你想的那么强。**
- 对 Crypto 来说，短周期上真正有信息的可能是：会话切片、结构突破、EMA 方向、量价确认，而不是裸 past-return sign。
- 所以下一步最重要的不是继续争论“动量有没有”，而是把**简单动量、漂移型基线、结构过滤、仓位缩放**拆开做 A/B，对应到不同层级分别验证。

## 6. 来源
- Huang, D., Li, J., Wang, L., & Zhou, G. (2020). *Time series momentum: Is it there?* Journal of Financial Economics, 135(3), 774-794.
- DOI: https://doi.org/10.1016/j.jfineco.2019.08.004
- Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X19301953
- Abstract / working-paper mirror: https://ideas.repec.org/p/cuf/wpaper/717.html
