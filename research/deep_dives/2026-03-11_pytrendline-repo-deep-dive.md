# Deep Dive — Repo: ednunezg/pytrendline

- 时间：2026-03-11
- 类型：GitHub 仓库拆解
- 主题标签：trendline / breakout / candlestick / support-resistance / confirmation
- 当前相关性：非常高

## 1. 为什么 `pytrendline` 对你当前阶段特别重要

如果你现在的兴趣点是：
- 平行通道
- 支撑阻力位
- 趋势线突破
- breakout 后确认

那么 `pytrendline` 比很多泛技术分析仓库都更贴你现在的问题。

原因是它直接从 **OHLC candlestick chart** 出发，做：
- support / resistance line detection
- pivot points
- breakout-aware trendline evaluation

这比只给“指标值”的库更接近你真正想研究的东西。

## 2. README 里最关键的功能拆解

### 2.1 输入对象是 CandlestickData
README 和 example 说明，它不是吃单一 close 序列，而是吃完整 K 线结构：
- Open
- High
- Low
- Close
- Date / time interval

这点很重要，因为：
**趋势线、阻力位、突破、影线交互，本来就不该只靠 close。**

### 2.2 先识别 pivot points
仓库明确写了：
- pivot points = local maximum / minimum
- 也就是 peaks / troughs

这点和你后面做趋势线、通道都直接相关。

### 2.3 扫描所有 `(i, j)` 点对尝试画线
README 明说：
- 它通过穷举点对去扫描 trendlines
- 复杂度是 **O(N^3)**

这是它最重要的工程特征之一：
- 研究分析很强
- 实时大样本很贵

### 2.4 一条线是否有效，要经过三类检查
#### 检查 1：有多少有效点落在线附近
通过 `max_allowable_error_pt_to_trend` 控制

#### 检查 2：线是否穿过 candle body
README 里很关键的一点是：
- 如果 trendline 在某个位置穿过 candle body，并且超过 `breakout_tolerance`，就被视为 breakout

这和你正在关心的“阻力位突破 / 假突破”是强相关的。

#### 检查 3：pivot 约束
可以要求：
- first point must be pivot
- last point must be pivot
- all points must be pivots

这点非常适合用来做“更严格/更保守”的结构线过滤。

### 2.5 scoring + duplicate grouping
它不是找到线就结束，还会：
- 给 trendlines 打分
- 对相似 slope / last_price 的线做 grouping
- 找每组最优线

这很适合研究阶段，因为实际检测出来的线通常很多、很重复。

## 3. example.py 暴露出的可调参数

从 example 可以看到，这个仓库已经很接近你后续真正要研究的信号要素：

- `trend_type`：BOTH / SUPPORT / RESISTANCE
- `first_pt_must_be_pivot`
- `last_pt_must_be_pivot`
- `all_pts_must_be_pivots`
- `trendline_must_include_global_maxmin_pt`
- `min_points_required`
- `ignore_breakouts`
- `config`（可覆盖默认 scoring 等）

这意味着你后面完全可以围绕这些维度定义研究问题：
- 更严格的线是否更稳？
- breakout line 要不要忽略？
- 至少几次 touch 才算有效？

## 4. 为什么它比 `trendln` 更适合你当前的 breakout 兴趣

我自己的判断是：

- `trendln` 更像结构线识别工具箱
- `pytrendline` 更像 **candlestick 上的 trendline/breakout research engine**

也就是说，如果你现在更关心：
- 压力位突破
- 阻力线突破后确认
- 线有没有穿 candle body
- 假突破/真突破怎么区分

那么 `pytrendline` 的直接相关性更高。

## 5. 它在你项目里已经怎么落地了

这不是纯外部学习，你项目里已经有明确接法。

### 5.1 项目文档：`docs/RESEARCH_PYTRENDLINE.md`
这里已经明确了它的定位：
- `pytrendline` 是研究功能
- 不直接当正式交易信号
- 重点回答：最近窗口里找到了哪些 support / resistance / breakout 线

### 5.2 项目桥接层：`src/momentum/factors/pytrendline_bridge.py`
你项目里现在已经做了一个非常合理的 adapter：

#### 已做的事
- 用 `PyTrendlineConfig` 包一层本地配置
- 只接受标准 columns：`timestamp/open/high/low/close`
- 自动把数据裁到最近窗口（默认 `96` bars）
- 做 pandas 3 兼容（`DataFrame.append` patch）
- 调用 `pytrendline.detect(...)`
- 返回：
  - `support_pivots`
  - `resistance_pivots`
  - `support_trendlines`
  - `resistance_trendlines`

#### 这层的意义
非常大，因为它已经把外部 repo 从“直接依赖”变成了：
- 可替换
- 可审计
- 可限制运行边界
- 可向上层暴露结构化结果

## 6. 我怎么看它和你当前研究问题的关系

### 问题 1：平行通道能不能从它里头做出来？
能，但要你自己加一层定义。

`pytrendline` 直接给的是：
- support lines
- resistance lines
- breakout-aware trendlines

你需要再定义：
- support slope ≈ resistance slope
- channel width 稳定
- 两侧 touch count 足够

这样才能变成“平行通道候选”。

### 问题 2：它能不能直接回答“突破后几根阳线确认”？
不能直接回答。

它擅长的是：
- 识别线
- 判断线与 candle body 的交互
- 标记 breakout 相关结构

但 “1 根确认 / 2 根确认 / 回踩确认” 这种，是你应该在上层 signal logic 里加的确认层。

### 问题 3：它适合实盘直接跑吗？
不适合直接当高频实时引擎。

原因：
- README 已明说 O(N^3)
- 你项目文档也已经把它定位成 recent window offline analysis

这点判断是对的，不要硬上实时主引擎。

## 7. 你最值得复用的，不是整个 repo，而是这 4 个思想

### 思想 1：先做结构检测，再做交易解释
不要把“线检测”和“交易确认”写成一锅粥。

### 思想 2：用 pivot + line validity 约束提升线质量
你的后续通道研究应该明确：
- 至少几个点
- 哪些点必须是 pivot
- 线与 candle 的误差阈值是多少

### 思想 3：把 breakout 当成“线与 K 线几何关系”
而不是只看：
- `close > resistance`

可以扩展出：
- close breakout
- wick breakout
- body penetration
- retest hold

### 思想 4：结果要以 DataFrame / structured outputs 暴露
这和你自己的 adapter 一致，非常适合后续做：
- report
- filtering
- clustering
- backtest join

## 8. 一个很适合你的最小实验

### 研究目标
验证：

> `pytrendline` 识别的 resistance breakout，是否比裸 rolling-high breakout 更接近“结构型基础 alpha”。

### 实验设计
#### 输入
- BTC / ETH / SOL
- 15m
- 近 60d / 180d
- recent window：`96` bars

#### 触发组
1. 裸 `close > rolling_high(20)`
2. `pytrendline` resistance breakout
3. `pytrendline` breakout + 1 根 close confirmation
4. `pytrendline` breakout + retest confirmation

#### 输出先看
- `post_cost_return`
- `positive_window_ratio`
- `trade_count`
- `false_breakout_rate`（你可以自己定义）

## 9. 它的主要局限

- O(N^3)，不适合粗暴扩大窗口
- 更适合研究窗口，不适合直接在线上高频持续扫描
- 趋势线检测本身很容易对 pivot 参数敏感
- 如果把检测结果直接变成交易信号，容易发生 lookahead / retrospective beautification 风险

## 10. 我对 `pytrendline` 的最终评价

如果你现在只选一个 repo 认真学，我会推荐你先学这个，而不是 `trendln`。

原因不是 `trendln` 不好，而是：

**`pytrendline` 更贴你现在的真实问题：趋势线 / 支撑阻力 / breakout / candle-body 交互 / 假突破。**

同时，你项目里已经有干净的接法了，这意味着它不仅能学，还能马上复用。

## 11. 来源
- Repo: <https://github.com/ednunezg/pytrendline>
- README raw: <https://raw.githubusercontent.com/ednunezg/pytrendline/master/README.md>
- Example raw: <https://raw.githubusercontent.com/ednunezg/pytrendline/master/example.py>
- 项目内研究文档：`docs/RESEARCH_PYTRENDLINE.md`
- 项目内接入代码：`src/momentum/factors/pytrendline_bridge.py`
