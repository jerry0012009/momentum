# Formalize trendline_event foundation 的 event study metrics protocol

## Why this was chosen now

这轮继续严格沿当前最近的主线推进：把 `trendline_event_foundation_report` 从设计文档逐步收紧成可执行 protocol。

上一轮已经把 `P1-C`（confirmation ladder） formalize 掉了；此时 `docs/TODO.md` 中最邻近、最自然的下一步就是：
- 把 `P1-D` 的 event-level validation 从抽象目标升级成清晰的 metrics / comparison / decision rubric。

这一步之所以关键，是因为即使 buckets 与 confirmation 口径都已经定了，如果：
- 看哪些指标
- 先比较什么
- 什么情况算 `go`
- 什么情况只是 `feature`
- 什么情况应 `park`

这些不先钉住，后续 Agent 还是会在 foundation report 里各自挑指标、各自挑结论口径，导致结果很难横向比较。

因此本轮选择：
- **主点：formalize P1-D（event study metrics protocol）**
- 紧邻子点：同步回写 TODO 并更新 plans 镜像

## What changed

### 1) 在 `docs/RESEARCH_TRENDLINE_EVENT.md` 中把 event-level validation 扩写为 operational protocol

原来该部分只列出：
- `sample_count`
- `forward_return_windows`
- `win_rate`
- `MFE / MAE`
- `false_break_ratio`
- `event_density`

本轮已把它扩写成更明确的第一轮 metrics protocol，包括：

#### A. `sample_count`
- 作为所有结论的第一过滤器；
- 明确沿用 scope 里的样本充分性阈值：
  - `<25`：只展示，不下方向性结论
  - `25~49`：可做弱结论，但要标记 `low-confidence`
  - `>=50`：才允许进入 go / no-go 讨论

#### B. `event_density`
- 明确建议同时展示：
  - `events per 1k bars`
  - `avg bars between events`
- 目的：避免把“很稀但好看”的事件和“太高频的噪声事件”混在一起看。

#### C. `forward_return_windows`
- 第一轮定稿为：
  - `+1 bar`
  - `+3 bars`
  - `+6 bars`
  - `+12 bars`
- 暂不在第一轮就引入按 timeframe 自适应窗口，先保证横向可比性。

#### D. `win_rate`
- 明确它的用途不是单独判定 go/no-go，
- 而是帮助判断收益偏移是“稳定偏移”还是“少数大赢驱动”。

#### E. `MFE / MAE`
- 明确建议用固定事件后窗口计算；
- 重点回答：
  - 某类确认是否减少 early adverse move；
  - 某类 event 是否经常先大幅逆行再给利润。

#### F. `false_break_ratio`
- 明确它只对 breakout / confirmed-switch 相关事件计算；
- 第一轮建议定义为：
  - 事件发生后，在短窗口内重新回到原结构侧、且未维持外侧状态的比例。

### 2) 定稿第一轮核心比较顺序

文档中已明确，foundation report 第一轮不应把所有维度一起摊平，而应按以下顺序比较：

1. `breakout vs rebound`
2. `raw vs confirmed`
3. `slope bucket differences`
4. `line quality bucket differences`
5. `support vs resistance`
6. `representative only vs all valid`（作为 sensitivity）

同时也明确了 report 默认阅读顺序：
1. sample coverage
2. event density
3. raw vs confirmed
4. slope buckets
5. quality buckets
6. go / feature / park judgement

### 3) 定稿第一轮 go / feature / park rubric

文档中现已明确：

#### `go`
至少大体满足：
- 样本量足够；
- 多个资产 / 周期 / 相邻 bucket 方向较一致；
- `confirmed` 相比 `raw` 有明显改善；
- slope / quality 分层具有稳定解释力；
- `false_break_ratio` / `MAE` 没暴露明显结构缺陷。

#### `feature`
常见情形：
- 单独做信号不够强；
- 但明显能帮助做 confirmation / filter / feature engineering；
- 例如 `confirm1` 明显优于 `raw_breach`，或某些 slope bucket 明显更稳。

#### `park`
常见情形：
- 样本太薄；
- 不同资产 / 周期方向经常打架；
- `confirmed` 并未明显优于 `raw`；
- slope / quality 分层也没有稳定解释力。

### 4) 回写 TODO

已将 `P1-D` 下这三项标记完成：
- event study 指标集
- 第一轮核心比较问题
- 第一轮结论是 go / no-go（更准确地说是 `go / feature / park`）

并补入文档中已定稿的 protocol 摘要，方便后续 Agent 直接认领 `P1-E` 或实现脚本时不用再猜口径。

## Validation / evidence

### A. 最小同步

执行：
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- plans 镜像页成功重建并发布

### B. 线上检查

已确认线上 `trendline_event_research.html` 中可读到新的 `event-level validation` 扩写内容，包括：
- `event_density` 的两种默认表示
- `+1 / +3 / +6 / +12 bars`
- `go / feature / park rubric`
- foundation report 的默认阅读顺序

也已确认 `momentum_todo.html` 中 `P1-D` 三项均已转为 `[x]`。

## Risks / caveats

- 这轮仍然是 **文档级 protocol 定稿**，没有开始真正计算 event study 统计；
- 某些指标（比如 `false_break_ratio` 的“短窗口”具体多长）后续落到代码时仍需进一步定死；
- 由于发布脚本会顺手刷新 `reading/deep_dives/*` 与 `reading/quant_digests/*` 的站点时间戳，这些文件在工作区仍保持 dirty，本轮未把它们带入提交。

## Next recommended step

现在 `P1-D` 已 formalize，下一轮最自然的主点是：

1. **P1-E：把 foundation report 的最小 artifacts 清单升级成页面 blueprint**
   - 每张表/图应该回答什么问题；
   - 默认字段、排序、说明文字；
   - 默认阅读顺序。

2. **起草 `scripts/build_trendline_event_foundation_report.py` 的输入/输出草图**
   - 先不做完整实现，只定义脚本产物和目录结构。

如果只选一个，我建议下一轮优先做：
- **P1-E：foundation report blueprint**

原因：到这一步，设计文档里“该怎么判断”已经基本定稿，下一步最该推进到“页面长什么样、Agent 该产出什么 artifacts”。

## Commit hash (if committed)

- 已 selective commit：`6dc1b02` (`docs(momentum): formalize event study metrics protocol`)

## Commit note

repo 中仍有与本轮无关的 dirty files（例如 `reports/site/reading/deep_dives/*`、`reports/site/reading/quant_digests/*` 的自动刷新项，以及工作区外层的未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `docs/RESEARCH_TRENDLINE_EVENT.md`
- `docs/TODO.md`
- `reports/site/plans/*`

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
