# Deep Dive — Repo: GregoryMorse/trendln

- 时间：2026-03-11
- 类型：GitHub 仓库拆解
- 主题标签：support-resistance / trendline / structural-alpha / tooling
- 当前相关性：高

## 1. 这个仓库到底是干什么的

`trendln` 的定位非常直接：

> **程序化计算 support / resistance trend lines**

它不是完整交易系统，不是回测框架，也不是信号工厂。
它最核心的价值是：

- 找局部 extrema
- 在这些 extrema 基础上找 support / resistance trend lines
- 给出可画图、可筛选、可统计分析的趋势线结果

如果你现在最关心的是：
- 平行通道识别
- 支撑阻力位
- 趋势线突破

那 `trendln` 值得看，因为它偏“结构线识别工具”。

## 2. README 暴露出来的核心功能

从仓库 README 可以明确看到这些功能点：

### 2.1 `calc_support_resistance(...)`
这是它的核心入口。

支持输入：
- 单一时间序列
- `(support_series, resistance_series)` 二元组
- 比如 low/high 拆开传入

输出会包含：
- minima / maxima indices
- 价格点集合
- trend lines
- windows / grouping 结果

这说明它不是只给一条线，而是给一整组支持后续分析的结构信息。

### 2.2 extrema detection methods
README 里提到多种 extrema 提取方法，例如：
- `METHOD_NAIVE`
- `METHOD_NAIVECONSEC`
- `METHOD_NUMDIFF`（默认，数值微分）

这很重要，因为：
**支撑阻力线的质量，很大程度取决于 extrema 抽取质量。**

### 2.3 trendline search methods
README 提到多种趋势线搜索方式：
- `METHOD_NCUBED`
- `METHOD_NSQUREDLOGN`（默认，较快）
- `METHOD_HOUGHPOINTS`
- `METHOD_HOUGHLINES`
- `METHOD_PROBHOUGH`

这说明它不只是“画线”，而是提供了不同的几何搜索/近似方法。

### 2.4 tuning knobs
README 里可以看到一些非常值得研究的参数：
- `window`
- `errpct`
- `hough_scale`

这意味着 `trendln` 更像一个**研究平台**，而不是“一键给答案”的黑箱。

## 3. 这个仓库适合你学什么

### A. 支撑阻力线识别的“工程拆法”
它把问题拆成：
1. extrema 怎么提
2. 线怎么搜索
3. 线如何合并/过滤

这套拆法很值得你学，因为后面你做通道也离不开这三步。

### B. 不要把支撑阻力当作单点价格
`trendln` 的思路更接近：
- 支撑阻力是一条结构线
- 不是一个孤立价格标签

这对于你后面研究 breakout confirmation 很关键：
**你要确认的，往往不是单点价位，而是对一条结构边界的有效突破。**

### C. 通道识别可以看成“成对趋势线问题”
虽然 `trendln` 主要讲 trend lines，不直接给你“平行通道策略”，但你完全可以把它扩展为：
- 下轨 support line
- 上轨 resistance line
- 两条线斜率相近时，视作 channel 候选

## 4. 这个仓库不擅长什么

这点也很重要。

### 不擅长 1：逐 bar 交易状态机
它不是专门为“每根 K 线都输出当前 active line / breakout 状态”设计的。

### 不擅长 2：confirmation logic
它本身不直接回答：
- 突破后几根确认
- 回踩确认
- 假突破过滤

### 不擅长 3：高频长样本实时扫描
虽然 README 提到较快算法，但如果你要在超长样本、全市场、短周期上实时跑，仍然要非常小心性能。

## 5. 它和你当前项目怎么结合

目前 `momentum` 项目更偏三类能力：
- 指标/因子模块
- signal state machine
- report / backtest pipeline

`trendln` 最适合作为：

### 角色 1：结构识别层
用于生成：
- support candidate lines
- resistance candidate lines
- slope / line quality / window-level features

### 角色 2：channel 候选生成器
你可以进一步定义：
- 两条近似平行的 support / resistance lines
- 形成 channel
- 再在上层去定义 breakout / confirmation

### 角色 3：研究工具，而不是最终交易引擎
更合理的路线是：
- 用 `trendln` 学会如何找结构线
- 然后在你自己的项目里做轻量、bar-by-bar、可因果的 clean 版本

## 6. 如果你要复用，最值得抽哪些概念

### 概念 1：extrema 先行
先有可靠 extrema，后有可靠线。

### 概念 2：line search 与 line quality 分开
不要只看“有没有线”，还要记录：
- 误差
- 支撑点数
- 斜率稳定性
- 重复线合并后得分

### 概念 3：channel = pair of lines + width stability
平行通道不应该只是“看起来像”，而应明确：
- slope difference 小
- width 在窗口内相对稳定
- 上下轨各自至少有足够 touch points

## 7. 一个适合你项目的最小改造方案

### 目标
把 `trendln` 的思路翻译成你项目里的结构特征，而不是直接依赖它输出买卖点。

### 最小可实现输出
对每个分析窗口输出：
- `support_slope`
- `resistance_slope`
- `channel_width_mean`
- `channel_width_std`
- `support_touch_count`
- `resistance_touch_count`
- `is_parallel_channel`
- `breakout_distance_over_upper`

### 然后上层再做信号
- `close > upper_channel`
- `close_confirm_bars >= 1`
- `retest_hold == True`

## 8. 你现在学它时最该避免的坑

- 不要把趋势线识别结果直接当作交易信号。
- 不要忽略 lookback window 对线的位置与斜率的影响。
- 不要忽略不同 extrema 方法带来的结果跳变。
- 不要一上来就在 15m 全量样本里暴力扫描全市场全参数。

## 9. 我对 `trendln` 的最终评价

如果你问我它对你值不值得学，我会说：

**值得，但它更像“结构线识别教材/工具库”，不是你最终策略的可直接落地内核。**

你最该学的是它怎么把“支撑阻力线”问题拆成：
- extrema
- line search
- line quality
- visualization

## 10. 来源
- Repo: <https://github.com/GregoryMorse/trendln>
- README raw: <https://raw.githubusercontent.com/GregoryMorse/trendln/master/README.md>
- Related article link referenced by README: <https://towardsdatascience.com/programmatic-identification-of-support-resistance-trend-lines-with-python-d797a4a90530>
