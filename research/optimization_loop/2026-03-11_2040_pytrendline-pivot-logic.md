# PyTrendline 报告：补 pivot points 选择逻辑与 bar-by-bar 边界说明

## Why this was chosen now

`pytrendline explainability` 主线里，参数解释之后最自然的一步就是把 pivot points 讲清楚。

因为后面的 trendlines / breakout 全都建立在 pivots 上：
- 如果用户不知道 pivot 是怎么来的，后面的线就会显得像“凭空画出来”；
- 如果不讲清楚 pivot 是否需要看右侧 bar，就很容易误读这页的实时可用性。

所以这轮聚焦 `A0-Calculation` 中最关键的一步：pivot selection logic。

## What changed

### 1) 在报告中新增“Pivot points 是怎么来的”区块

文件：
- `scripts/build_pytrendline_report.py`

新增区块：
- `Pivot points 是怎么来的`

### 2) 报告里明确写出的源码口径

当前已补充这些核心解释：

- **support pivots 看哪里**
  - 在原始 `Low` 序列上找局部低点
  - 不是平滑曲线上的点

- **resistance pivots 看哪里**
  - 在原始 `High` 序列上找局部高点
  - 同样直接来自原始 K 线高点

- **grouping threshold**
  - 源码会把差异很小的相邻高/低点先视作近似连续的一组，再拿更远一点的前后点做比较
  - 这一步是为了避免局部极近邻噪声把 pivot 判断搞得太碎

- **separation threshold**
  - 候选 pivot 需要和前后比较点拉开足够距离
  - 避免把太小的抖动误当成结构点

- **局部极值条件**
  - support 必须比前后更低
  - resistance 必须比前后更高

- **窗口首尾**
  - first / last bar 会被强制纳入 pivots
  - 这样边界上也保留锚点，方便趋势线搜索

### 3) 明确 bar-by-bar 边界

本轮最重要的补充之一是：
- pivot 判断会看右侧若干根 bar；
- 所以当前这页更适合 research inspection / explainability；
- 如果以后要把这些 pivots 用进正式 signal engine，就必须额外审计“何时才算确认”这个问题。

这能避免把当前研究页误读成完全实时可用的信号页。

### 4) 用当前窗口的近似阈值把抽象规则落地

报告里不再只写抽象概念，还把当前窗口下的近似阈值写出来：
- `grouping threshold ≈ avg_candle_range * 0.1`
- `separation threshold ≈ avg_candle_range * 0.2`

这样读者能同时看到：
- 源码规则是什么
- 当前具体窗口下这些规则大概落在什么数量级

### 5) 回写 TODO 状态

已将以下任务标记为完成：
- 单独解释 support pivots / resistance pivots 的选择逻辑
- 在报告里单独解释 pivot points 是怎么来的

## Validation / evidence

### A. 报告成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 页面里已经不再只是“看到 pivots”，而是“知道 pivots 为什么会出现”

新增的 pivot 区块现在可以回答：
- pivots 看的是 High 还是 Low
- 是否来自原始价格还是平滑曲线
- grouping / separation 在做什么
- 首尾点为什么会被纳入
- 为什么这页暂时更适合研究解释而不是直接上实时信号

## Risks / caveats

- 这轮解释了 pivot 规则，但还没有做“pivot index / timestamp 在图上显式打标”的对照图。
- 这轮也还没有展开 candidate lines 是如何从 pivot pairs 枚举出来的。
- 当前给出的阈值是报告窗口下的近似数值，不应误读为跨资产固定阈值。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：单独解释 candidate lines 的生成口径，明确是不是所有 pivot 组合都会尝试，以及哪些组合会被过滤掉；
2. **次优方案**：在 K 线 + pivots 图里补 pivot index 或时间标签，让规则解释和图表对照更直接。

## Commit hash (if committed)

0b5ea605c9b04c595202b1b9fdc037ac069b5c5c

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
