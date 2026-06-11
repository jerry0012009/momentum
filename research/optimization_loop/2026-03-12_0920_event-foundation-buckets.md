# Formalize trendline_event foundation 的第一轮 buckets 与 scope

## Why this was chosen now

这轮继续沿着当前已经重排好的主线推进，不再继续打磨 `pytrendline_research` 页面本身，也不新开回测分支。

在上一轮完成 `pytrendline_research` 四段式结构收尾之后，`docs/TODO.md` 中最自然、最邻近、最适合继续往前推进的一步，就是把 `P1-B` 从“概念建议”升级成“可执行 protocol”：
- slope buckets
- quality buckets
- 第一轮 crypto + 少量周期的 scope

这一步的价值很高，因为它直接决定后续 `trendline_event_foundation_report` 能否被不同 Agent 稳定实现：
- 如果不先把 buckets / scope 写清楚，后面每个 Agent 都可能临时定义自己的 slope 阈值、score 分桶和样本要求；
- 那样即使都在“做 event foundation”，结果也会很难横向比较。

因此本轮选择：
- **主点：formalize P1-B（first-round buckets + scope）**
- 紧邻子点：同步把 TODO 中对应三项勾掉，并更新 plans 站点镜像

## What changed

### 1) 在 `docs/RESEARCH_TRENDLINE_EVENT.md` 中把 slope buckets 升级为 operational protocol

已新增更明确的第一轮定稿建议：

#### A. 相对斜率定义
对每条线统一使用：
- `relative_slope_per_bar = (end_price - start_price) / max(abs(start_price), eps) / max(span_bars, 1)`

理由：
- 比直接用原始 `m` 更适合跨资产、跨周期比较；
- 更接近“每根 bar 的相对抬升 / 下压速度”解释。

#### B. sign bucket
在同一 `asset × timeframe × line_side` 宇宙内：
- 先看 `abs(relative_slope_per_bar)` 的分布；
- 用其 20% 分位数定义 `flat_threshold`；
- 再定义：
  - `up`
  - `flat`
  - `down`

#### C. magnitude bucket
- 只对 non-flat 线继续做 magnitude 分桶；
- 用 `abs(relative_slope_per_bar)` 的 tertiles 定义：
  - `low`
  - `mid`
  - `high`
- `flat` 线在 magnitude 维度记为：
  - `flat/na`

#### D. 第一轮建议汇总视角
- `sign only`
- `sign × magnitude`

### 2) 在同一文档中把 quality buckets 升级为 operational protocol

已明确第一轮建议：

#### A. `num_points`
- `3`
- `4`
- `5+`

#### B. `score`
- 在 `asset × timeframe × line_side` 宇宙内做 tertiles：
  - `score_low`
  - `score_mid`
  - `score_high`

#### C. `is_best_from_duplicate_group`
- `representative`
- `non_representative`

并明确：
- 第一轮主表默认用 `representative only`
- 再用 `all valid lines` 做 sensitivity 对照

#### D. `line_side`
- `support`
- `resistance`

并明确第一轮不要把 support / resistance 混成一个大盘结论。

### 3) 在同一文档中补上第一轮 scope 定稿

已明确：
- 资产 universe：BTC / ETH / SOL / DOGE / XRP
- 周期：30m / 60m
- 历史样本长度：默认 180d，样本不足再扩到 365d
- 默认线集合：`representative only`
- sensitivity：`all valid lines`
- 默认事件集合：
  - breakout：`raw_breach / close_confirm_same_bar / confirm1 / retest_hold`
  - rebound：`wick_rejection_only / touch_close_back_inside / touch_next_bar_continuation`

### 4) 新增第一轮样本充分性要求

为了避免 bucket 太细但样本太薄，当前文档已新增：
- `sample_count < 25`：只展示，不下方向性结论
- `25 <= sample_count < 50`：可做弱结论，但必须标记 `low-confidence`
- `sample_count >= 50`：才允许进入第一轮 go / no-go 讨论

这一步能显著减少后面 foundation report 被“很小样本的偶然正收益”误导。

### 5) 回写 TODO

已将 `P1-B` 下这三项标记完成：
- slope buckets
- quality buckets
- first-round crypto + 少量周期 scope

并在 TODO 中补充了文档里已经定稿的 operational protocol 摘要，方便后续 Agent 直接认领实现任务时不用先去猜口径。

## Validation / evidence

### A. 文档镜像更新

执行：
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- 成功重建 plans 页面
- 成功发布站点镜像

### B. 线上检查

已确认线上可读到新的文档内容：
- `relative_slope_per_bar`
- `flat_threshold`
- `representative only / all valid lines`
- `sample_count < 25 / 25~49 / >=50`

对应页面：
- `/momentum/plans/trendline_event_research.html`
- `/momentum/plans/momentum_todo.html`

## Risks / caveats

- 这轮交付的是 **文档级 protocol 定稿**，还没有生成 foundation report 或任何 event-level 统计结果；
- 其中一些阈值（例如 20% 分位数 flat threshold、tertiles 分桶）是为了第一轮研究稳定性和可实现性，后续若证据显示不合理，仍可在 foundation 阶段再调整；
- 当前 scope 故意偏窄，因此它的目标是减少归因复杂度，而不是一开始就追求外推全面性。

## Next recommended step

下一轮最自然的主点有两个：

1. **P1-C：把 confirmation ladder 进一步 formalize 成明确的比较协议**
   - 特别是 breakout 的 `raw_breach / close_confirm_same_bar / confirm1 / confirm3 / retest_hold`
   - 以及 rebound 的确认层级和“confirmed switch vs 暂时越界”的判定

2. **P1-E：把 `trendline_event_foundation_report` 的最小 artifacts 清单写成更明确的页面 blueprint**
   - 例如每张表/图的字段、默认排序、读法顺序

如果只选一个，我建议下一轮优先做：
- **P1-C：formalize confirmation ladder**

因为 buckets / scope 已经定好后，下一步最关键的自由度就是 confirmation 口径；如果这一步不先钉住，后面的 foundation report 还是会漂。

## Commit hash (if committed)

- 已 selective commit：`b242b88` (`docs(momentum): formalize event foundation first-round buckets`)

## Commit note

repo 中仍有与本轮无关的工作区外层脏文件（如 `/root/clawd/memory/2026-03-12.md` 及若干未跟踪目录/文件），因此没有整仓提交；本轮只 selective commit 了：
- `docs/RESEARCH_TRENDLINE_EVENT.md`
- `docs/TODO.md`
- `reports/site/plans/trendline_event_research.html`
- `reports/site/plans/momentum_todo.html`

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
