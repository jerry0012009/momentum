# Lo 形态识别的第三方复现仓库：把 kernel regression → extrema → pattern rules 拆成可读代码
- 时间：2026-03-11 01:28 UTC
- 类型：GitHub
- 主题标签：trend / breakout / pullback / structure / alpha / implementation
- 证据类型：论文证据 + 第三方工程实现

## 1. 这次看了什么
这次不是新论文，而是看一个直接对你更有帮助的第三方复现仓库：`SITONGRUC/FOUNDATIONS_OF_TECHNICAL_ANALYSIS`。它不是 Lo, Mamaysky, Wang (2000) 的官方代码，但它把论文里的核心流程拆成了几本 notebook：`Kernel regression.ipynb`、`Find Min&Max.ipynb`、`pattern count.ipynb`，很适合拿来理解“形态识别到底怎么落到代码里”。

## 2. 核心结论
- 这套复现把 Lo 论文的方法非常直白地拆成三步：**先平滑，再找 extrema，再做规则匹配**。这和论文本身是一致的，也和你现在在 `momentum` 里做的 endpoint smoothing + confirmed extrema 思路是同一路。
- `Kernel regression.ipynb` 里直接用 `statsmodels.nonparametric.kernel_regression.KernelReg` 做高斯核回归，带宽用 `bw='cv_ls'`；然后在每个滚动窗口内生成平滑序列。
- `Find Min&Max.ipynb` 里用 `scipy.signal.argrelextrema` 先在平滑序列上找局部高低点，再把 extrema 映射回原始序列附近的点位；`pattern count.ipynb` 再用 if/else 阈值去匹配 HS / IHS / broadening / triangle 等形态。
- 但它也暴露了一个很重要的问题：**能“看懂论文”不等于能直接拿去做 15m 实盘信号**。这个复现当前更像教学代码——窗口短、路径硬编码、本地 CSV 驱动、而且看起来主要在 `ret` 序列上做，不是为因果、无重绘、在线检测设计的。

## 3. 为什么和当前项目有关
这份仓库最适合当前 `momentum` 主线，因为你现在缺的不是“再多一个玄学图形名词”，而是把结构识别拆成工程步骤。它给你的价值主要有三点：
- 证明 `kernel smoothing -> extrema -> pattern rule` 这条链很容易先做成最小可运行原型；
- 让你能把论文语言翻译成代码骨架，尤其适合对照现有 `confirmed extrema` 设计；
- 反过来也提醒你：当前项目应坚持 **price-level / causal / delayed-confirmation**，不要把教学代码里的非因果细节原样照搬进 15m crypto。

## 4. 可复刻的最小实验
- 研究假设：如果 Lo 风格形态识别对 15m crypto 真的有帮助，那么把“结构条件”显式化后，应当能比裸 breakout 更稳定地筛掉一部分假突破。
- 一个可计算定义：先只做 3 个模式，不贪多：`double_top/bottom`、`head-and-shoulders`、`pullback_recovery_like`。流程固定为：
  1. 对 15m 收盘价做 **causal smoothing**；
  2. 用 **confirmed extrema** 生成局部高低点；
  3. 用 extrema 序列匹配规则，而不是直接在 K 线上硬写 if。
- 最小回测切口：BTC、ETH、SOL；15m；近 180d；对比 `Donchian breakout` 基线 vs `Donchian breakout + 结构过滤`。
- 最该先看：`post_cost_return`、`false_break_ratio`。如果结构过滤没能降低假突破占比，就先别继续堆图形库。

## 5. 风险与保留意见
- 这不是作者官方仓库，只能算**第三方复现参考**，不能当成论文原版实现。
- 复现代码明显更偏研究/教学，不是 production-ready；直接照搬到 15m crypto 很容易引入 look-ahead、窗口依赖和过拟合。
- 这份仓库最该学的是“分层流程”，不是具体 notebook 里的每一个实现细节。

## 6. 来源
- Lo, A. W., Mamaysky, H., & Wang, J. (2000). *Foundations of Technical Analysis: Computational Algorithms, Statistical Inference, and Empirical Implementation*. NBER Working Paper 7613.
- DOI: <https://doi.org/10.3386/w7613>
- Readable URL: <https://www.nber.org/papers/w7613>
- 第三方复现仓库：SITONGRUC. *FOUNDATIONS_OF_TECHNICAL_ANALYSIS*.
- Repo URL: <https://github.com/SITONGRUC/FOUNDATIONS_OF_TECHNICAL_ANALYSIS>
- README / file list 可见：`Kernel regression.ipynb`、`Find Min&Max .ipynb`、`pattern count.ipynb`
