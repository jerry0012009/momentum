# Formalize trendline_event foundation 的 confirmation ladder protocol

## Why this was chosen now

这轮继续严格沿当前最近的研究主线推进：`trendline_event_foundation_report` 的设计定稿，不再回到 `pytrendline_research` 页面细修，也不新开回测分支。

上一轮已经把 `P1-B`（slope buckets / quality buckets / first-round scope）收紧成了可执行 protocol。此时 `docs/TODO.md` 中最邻近、最自然的下一步就是：
- 把 `P1-C` 的 confirmation ladder 从“名字清单”进一步 formalize 成清晰的执行口径。

这一步之所以关键，是因为即使 buckets / scope 已经定好了，如果：
- 什么算 `raw_breach`
- 什么算 `confirm1`
- 什么叫 `retest_hold`
- 什么还只是 `provisional break`
- 什么才算 `confirmed switch`

这些定义不先钉住，后续不同 Agent 还是会在实现时各自漂移，导致 foundation report 很难横向比较。

因此本轮选择：
- **主点：formalize confirmation ladder protocol**
- 紧邻子点：同步回写 TODO，并发布 plans 页镜像

## What changed

### 1) 在 `docs/RESEARCH_TRENDLINE_EVENT.md` 中把 confirmation ladder 升级成可执行 protocol

原来该部分只列了 breakout / rebound 的层级名称；本轮已把它扩写为第一轮建议定稿，包括：

#### breakout ladder
- `raw_breach`
- `close_confirm_same_bar`
- `confirm1`
- `confirm3`
- `retest_hold`

#### rebound ladder
- `wick_rejection_only`
- `touch_close_back_inside`
- `touch_next_bar_continuation`
- `touch_htf_aligned_continuation`

### 2) 明确事件必须绑定到“事件参考线”

文档中现在明确：
- 每个 event 都必须绑定到一条 **已识别 line object**；
- 第一轮默认优先看：
  - `representative only`
  - 且 line 在事件发生时已经进入可用 state，而不是纯 candidate 草稿。

这一步减少了“随便找一条画出来的线就拿来定义事件”的模糊空间。

### 3) 明确 `raw_breach` / `touch` 的几何语义

文档中已将 support / resistance 分开说明：
- support：`touch` 与 `raw_breach` 分别对应 low/close 相对支撑线的位置关系；
- resistance：`touch` 与 `raw_breach` 分别对应 high/close 相对阻力线的位置关系；

并明确：
- 第一轮允许 `raw_breach` 先按几何越线定义；
- 但更强确认必须依赖 close / 持续性 / retest 来提升质量。

### 4) formalize `close_confirm_same_bar / confirm1 / confirm3 / retest_hold`

文档中现已明确：
- `close_confirm_same_bar`：同 bar 越线且收盘在线外；
- `confirm1`：下一根 close 仍在线外；
- `confirm3`：3 根内至少 2 根 close 维持在线外；
- `retest_hold`：越线后回踩原线位不失守，再次沿突破方向离开。

并明确推荐顺序：
- breakout 默认先比较：
  1. `raw_breach` vs `close_confirm_same_bar`
  2. `close_confirm_same_bar` vs `confirm1`
  3. `confirm1` vs `confirm3`
  4. `confirm1` vs `retest_hold`

### 5) formalize rebound ladder 的对应层级

文档中已明确：
- `wick_rejection_only`
- `touch_close_back_inside`
- `touch_next_bar_continuation`
- `touch_htf_aligned_continuation`

并明确第一轮推荐：
- 先实现前三档；
- `HTF aligned continuation` 先保留在文档中，不作为第一批必须落地的复杂度。

### 6) 明确 `provisional break` vs `confirmed switch`

本轮最关键的新增之一，是把这两个状态口径明确写开：

#### provisional break
- 只有 `raw_breach`
- 或只有 `close_confirm_same_bar`
- 但还没有后续持续性证据

#### confirmed switch
- 至少满足：
  - `confirm1`
  - `confirm3`
  - `retest_hold`

这样后续 foundation report 就不会再把：
- “刚越线一下”
- 和 “结构真的切换了”

混成同一类样本。

### 7) 回写 TODO

已将 `P1-C` 下这三项标记完成：
- breakout confirmation ladder
- rebound confirmation
- confirmed switch vs provisional break 区分口径

并在 TODO 中补入已定稿的 protocol 摘要，方便后续 Agent 直接认领实现任务。

## Validation / evidence

### A. 最小同步

执行：
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- plans 镜像页已重建并发布

### B. 线上检查

已确认线上 `trendline_event_research.html` 中出现新的 confirmation ladder protocol 内容，包括：
- `provisional break`
- `confirmed switch`
- `confirm1 / confirm3 / retest_hold`
- rebound ladder 四档说明

已确认 `momentum_todo.html` 中 `P1-C` 三项均已转为 `[x]`。

## Risks / caveats

- 这轮交付的是 **文档级 protocol 定稿**，不是 event-level 统计实现；
- `retest_hold`、`touch_close_back_inside` 等细节后续落到代码时，仍需要再明确“线附近”的 tolerance 与窗口长度；
- 由于发布脚本会顺手刷新 quant digests / deep dives 的站点时间戳，这些文件在工作区仍会显示 dirty；本轮未将它们一并提交。

## Next recommended step

现在 `P1-C` 已定稿，下一轮最自然的主点是：

1. **P1-D：formalize event study 指标集**
   - 把 `sample_count / forward returns / win rate / MFE / MAE / false_break_ratio / event density` 的字段与默认比较口径写成更明确 protocol。

2. **P1-E：定义 foundation report 的最小 artifacts 与读法顺序**
   - 例如每张图/表应该回答什么问题、默认排序是什么。

如果只选一个，我建议下一轮优先做：
- **P1-D：event study metrics protocol**

因为 confirmation ladder 已经定住后，下一步最重要的自由度就是“用什么指标看它值不值得继续”。

## Commit hash (if committed)

- 已 selective commit：`dce58e6` (`docs(momentum): formalize confirmation ladder protocol`)

## Commit note

repo 中仍有与本轮无关的 dirty files（例如 `reports/site/reading/deep_dives/*`、`reports/site/reading/quant_digests/*` 的自动刷新项，以及工作区外层的未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `docs/RESEARCH_TRENDLINE_EVENT.md`
- `docs/TODO.md`
- `reports/site/plans/*`

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
