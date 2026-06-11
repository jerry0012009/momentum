# 起草 trendline event 研究设计文档

## Why this was chosen now

这轮继续沿着刚刚重排后的主线推进，不再随机扩题。

上一轮已经把 `docs/TODO.md` 的上位方向从“先押注 parallel channel alpha”调整为：
- 先验证 **structure-event alpha**；
- 其中最自然、最接近已有资产的一步，是先做 `trendline_event_foundation_report`。

在这种新主线下，最近最邻近、最高杠杆、也最小步的动作，不是继续补某一张图，而是先把：
- 为什么先做 trendline event foundation；
- 事件怎么分层；
- line lifecycle 和 trade trigger 如何拆层；
- 第一轮验证范围与边界是什么；

这些问题写成正式设计文档，避免后续 Agent 又回到旧的 `parallel channel` 直冲式路径，或者在 breakout / rebound / confirmation 口径上反复漂移。

因此本轮选择：
- **主点：起草 `docs/RESEARCH_TRENDLINE_EVENT.md`**
- 紧邻子点：把 TODO 中与该设计文档直接对应的三项一并勾掉

## What changed

### 1) 新建 `docs/RESEARCH_TRENDLINE_EVENT.md`

已起草第一版文档，核心内容包括：

- 为什么当前不再先押注 `parallel channel`
- 为什么先做 `trendline_event_foundation_report`
- 当前可复用输入资产：
  - `pytrendline_research`
  - `trendline_breakout_navigator`
  - `trendline_segment_backtest` / interval sweep
- 当前研究问题：
  - breakout vs rebound
  - slope 是否重要
  - confirmation 是否重要
  - line quality 是否重要
- 系统分层：
  - line detection
  - line lifecycle / line state
  - event detection
  - confirmation
  - execution
- event taxonomy：
  - touch
  - wick interaction
  - first cross / raw breach
  - provisional break
  - confirmed break
  - rebound
- line lifecycle 与 event 的关系
- slope buckets / quality buckets 的第一轮建议
- confirmation ladder 的第一轮建议
- 第一轮实验范围：
  - BTC / ETH / SOL / DOGE / XRP
  - 30m / 60m
  - 180d 起步
- foundation report 的最小 artifacts 与当前暂不做内容

### 2) 回写 TODO

已将以下三项标记完成：

- `新建 docs/RESEARCH_TRENDLINE_EVENT.md`
- `在设计草案中明确 event taxonomy（事件分层）`
- `在设计草案中明确 事件与 line lifecycle 的关系`

并在每条完成项下补了简短结果说明，便于后续 Agent 继续认领下一批任务。

## Validation / evidence

### A. 文档存在性与关键章节检查

已确认 `docs/RESEARCH_TRENDLINE_EVENT.md` 中包含以下关键章节：
- `Event taxonomy（事件分层）`
- `line lifecycle 与 event 的关系`
- `confirmation ladder（确认阶梯）`
- `第一轮实验范围（先故意收窄）`

### B. TODO 对齐检查

已确认 `docs/TODO.md` 中对应的三项任务已从 `[ ]` 更新为 `[x]`，且说明文字与文档内容一致。

## Risks / caveats

- 这轮交付的是 **设计文档**，不是事件验证脚本或 foundation report 本体；因此它解决的是“研究口径稳定”问题，还没有解决“事件是否真的有 alpha/feature 价值”。
- 其中部分定义（比如 slope magnitude 分桶阈值、false_break_ratio 具体口径）目前仍停留在第一版建议层，后续仍需在实现时进一步细化。
- 这轮没有继续补 `pytrendline_research` 的 `candidate lines before filtering` 图；该项仍保留在 P0，后续可继续认领。

## Next recommended step

下一轮最自然的两个相邻动作是：

1. **补 `candidate lines before filtering` 图**
   - 收掉 `pytrendline_research` explainability baseline v1 的关键遗留项。

2. **开始定义 `trendline_event_foundation_report` 的最小 artifacts 和 event-study 指标口径**
   - 直接承接本轮新文档中的 event taxonomy / confirmation ladder / first-round scope。

如果只选一个，我建议下一轮优先做：
- `candidate lines before filtering` 图

原因是：它仍属于当前 explainability baseline 的收尾项，完成后再切去 foundation report，会更顺。

## Commit hash (if committed)

- 已 selective commit：`8a8f8bc` (`docs(momentum): draft trendline event research plan`)

## Commit note

repo 中仍存在与本轮无关的脏文件（例如 interval sweep / crypto rebound scan / deep dive 索引 / 较早 optimization loop 记录等），因此没有整仓提交；本轮只 selective commit 了：
- `docs/RESEARCH_TRENDLINE_EVENT.md`
- `docs/TODO.md`

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
