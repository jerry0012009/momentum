# PyTrendline 报告可读性升级：补页面导读、区块提问与统一图注

## Why this was chosen now

当前最近主线仍然是 `A0. pytrendline explainability report`，而且用户刚刚明确要求：
- 不是泛泛优化显示效果；
- 而是要确保页面里“每个部分都能讲明白”；
- 特别要把图表与计算口径的关系讲清楚。

基于这个目标，这轮优先做 `A0-Display` 里最基础、最有杠杆的部分：
- 页面导读
- 区块回答的问题
- 输入到结果的步骤总览
- 统一图下注释
- 图上元素字典
- 更像教学顺序的步骤标题

这些改动不会改变计算逻辑，但能显著降低阅读门槛。

## What changed

### 1) 升级报告页面的“怎么读”能力

文件：
- `scripts/build_pytrendline_report.py`

新增内容：
- `页面导读 / Reading guide`
- `步骤总览：从输入到结果`

作用：
- 告诉读者这页应该按什么顺序看；
- 把 `bars -> pivots -> candidate lines -> filtered lines -> duplicate groups -> best lines + breakout labels` 串成一条更清晰的理解链。

### 2) 给主要区块补“这个区块回答什么问题”

已在这些模块补充说明句：
- 这次落地了什么
- 参数
- 窗口 / 运行边界
- 来源与边界
- 逐步骤操作性定义
- 图上元素字典
- 窗口内数量概览
- 各分步骤图
- 结果表
- 字段解释
- research-only 边界
- pytrendline -> parallel channel 映射
- Artifacts

这样做的好处是：页面不再只是“堆卡片”，而更像一串有因果关系的问题与回答。

### 3) 给图表增加统一图下注释与图例字典

新增：
- 图上元素字典表
- Step1~Step4 与最终总览图的统一图下注释

说明内容包括：
- 绿色/红色 K 线实体代表什么
- support / resistance 线分别是什么颜色
- breakout 为什么用虚线
- pivot 三角标记分别是什么意思
- 每张图应该如何和前后图对照着看

### 4) 把步骤标题改成教学式标题

原先更偏技术编号，当前改成：
- 先看结构锚点：原始 K 线 + pivots
- 再看支撑线如何从锚点长出来
- 再看阻力线如何从锚点长出来
- 最后只看事件线：breakout-only
- 最终总览图：把锚点、代表线与事件线叠在一起

### 5) 回写 TODO 状态

已将以下 TODO 标记为完成：
- 页面导读 / reading guide
- 每个大区块补一句“这个区块回答什么问题”
- 输入 -> 中间结果 -> 最终展示的步骤总览卡片
- 每张图补统一格式的图下注释
- 每张图补图上元素字典
- step1~step4 改成更像教学顺序的标题

## Validation / evidence

### A. 报告重建成功
使用项目虚拟环境重建并发布：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 本地报告已重建
- 站点已重新发布到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 页面结构确实更适合教学阅读
当前首页已经可以直接看到：
- 页面导读
- 步骤总览
- 各模块“这个区块回答什么问题”
- 图上元素字典
- 每张关键图的图下注释
- 教学式步骤标题

这能明显降低“只看到很多图和表，但不知道先看什么”的问题。

## Risks / caveats

- 本轮主要是 explainability / 信息架构优化，没有新增 candidate-before-filter 图或 duplicate before/after 图。
- 目前图和表之间仍然缺少更强的索引级联动（例如 pivot index / line 命中点直接对照）。
- 这轮没有新增计算逻辑说明到“参数为什么这么设”的深层级，只是先把阅读入口整理清楚。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：补“参数为什么这么设”的解释表（`window_bars=96 / min_points_required=3 / all_pts_must_be_pivots=True / ignore_breakouts=False`）；
2. **次优方案**：补 `duplicate grouping before/after` 对照图，让图表和计算口径再往前贴一步。

## Commit hash (if committed)

93017aa7da71c0b5756a30a690d19f50addddd3a

## Commit note

本轮仍有与 interval sweep / quant digest 相关的其他脏文件存在，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
