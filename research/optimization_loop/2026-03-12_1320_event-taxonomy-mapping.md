# Map current source events into foundation taxonomy

## Why this was chosen now

这轮继续严格沿当前最近的 `trendline_event_foundation` 主线推进，不新开方向。

上一轮已经把 foundation 页从 `contract_only` 升级成 `partial_stats`，并真实填入了：
- `sample_coverage_table`
- `event_density_summary`

按原本自然顺序，下一步本来最像是去填 `breakout_confirmation_comparison`。但在真正检查当前数据源之后，发现一个关键边界：
- 当前 `reports/artifacts/trendline_event_slope_audit/trade_detail.csv` 里的 breakout 事件并没有提供完整的 `raw_breach / close_confirm / confirm1 / confirm3` 梯度样本；
- 它当前更像是“已实现策略中的 confirmed breakout / confirmed rebound trade samples”；
- 例如：
  - `breakout_*` 统一对应 `confirm_bars=3`
  - `rebound_*` 统一对应 `confirm_bars=2`

这意味着：
- 现在如果硬做 `breakout_confirmation_comparison`，很容易把“当前 source event types”和“foundation taxonomy 里的完整 ladder”混为一谈；
- 这会直接损害 auditability，也会误导 Jerry 以为 foundation 页已经能比较 raw vs confirmed。

因此这轮选择一个更小、但更扎实的主点：
- **把 current source event buckets 明确映射到 foundation taxonomy，并在页面里公开写出当前 source 的限制。**

这一步不是退步，而是在真正开始更多真实统计之前，先把“当前数据源到底在代表什么”说清楚。

## What changed

### 1) 升级 `scripts/build_trendline_event_foundation_report.py`

脚本新增两块内容：
- `event_taxonomy_card`
- `source_limitations`

#### `event_taxonomy_card`
当前会读取 `trade_detail.csv` 中真实出现的 `event_type`，并映射成一张表，至少包括：
- `source_event_type`
- `source_strategy`
- `foundation_family`
- `mapped_bucket`
- `source_confirm_bars`
- `why_this_mapping_is_not_the_full_ladder`

当前真实导出的 4 个 source event buckets 为：
- `breakout_long`
- `breakout_short`
- `rebound_long`
- `rebound_short`

并明确映射为：
- `confirmed_breakout_long`
- `confirmed_breakout_short`
- `confirmed_rebound_long`
- `confirmed_rebound_short`

也就是说：
- **当前 source 里这些样本更接近“某一层确认后的 trade sample”**；
- **它们不是 foundation 里完整 confirmation ladder 的所有层。**

#### `source_limitations`
页面里新增单独区块，明确写清：
- 当前 source 不暴露完整 confirmation ladder；
- 当前 slope-audit 数据是 trade-sample oriented，而不是 full event-universe oriented；
- 因此 foundation 页当前虽已有真实数据，但还不能直接用来回答 `raw_breach vs confirm1 vs confirm3` 的完整问题。

### 2) 新增 machine-readable 导出

新增：
- `reports/artifacts/trendline_event_foundation/event_taxonomy_card.csv`

当前 shape：
- `(4, 6)`

这张表能帮助后续 Agent 在真正实现 confirmation ladder 比较前，先统一“当前 source bucket 到 foundation event family”的命名桥接。

### 3) foundation 页从“有两块统计”升级成“有两块统计 + 一个 taxonomy bridge + 一个 limitation disclosure”

文件：
- `reports/site/factors/trendline_event_foundation/report.html`
- `reports/site/factors/trendline_event_foundation/contract.json`

当前页面现在多出两个关键区块：
- `Current source event taxonomy mapping`
- `Current source limitations`

这意味着 foundation 页不再只是：
- “有一些看起来不错的表”

而是同时明确：
- “这些表到底是基于什么语义的数据源算出来的”
- “哪些问题当前 source 还回答不了”

### 4) 回写 TODO

已在 `docs/TODO.md` 中增强“先往 foundation skeleton 中填第一批真实统计”的说明：
- 不再只说 sample coverage / event density；
- 现在明确补充了：
  - `event_taxonomy_card`
  - 当前 source 的限制说明

也就是说，TODO 现在已经更准确地反映 foundation 页当前的真实状态，而不是把它误写成“已经准备好比较完整 ladder”。

## Validation / evidence

### A. 最小运行验证

执行：
- `python3 scripts/build_trendline_event_foundation_report.py`
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- 成功生成：
  - `reports/artifacts/trendline_event_foundation/event_taxonomy_card.csv`
  - 更新后的 `report.html`
  - 更新后的 `contract.json`
- 成功发布站点

### B. CSV 形状与样例检查

已确认：
- `event_taxonomy_card.csv` → `(4, 6)`
- 前几行包括：
  - `breakout_long -> confirmed_breakout_long`
  - `breakout_short -> confirmed_breakout_short`
  - `rebound_long -> confirmed_rebound_long`
  - `rebound_short -> confirmed_rebound_short`

并明确附带解释：
- 当前 source 是已确认 trade sample，不是完整 ladder 的所有层。

### C. 线上检查

已确认线上 foundation 页可读到：
- `Current source event taxonomy mapping`
- `Current source limitations`

这两块已经和原有：
- `Sample coverage table`
- `Event density summary`

共同组成 foundation 页当前的真实内容。

## Risks / caveats

- 这轮没有新增 `breakout_confirmation_comparison` 或 `rebound_confirmation_comparison` 的真实统计，因为当前数据源确实不够细；
- 当前 taxonomy mapping 是“从现有 source bucket 映射到 foundation taxonomy”的桥接表，不应误读成完整 taxonomy 已被 fully populated；
- 当前 source limitation 写得越清楚，短期看页面会显得“还没做完”，但长期对 auditability 是正向的，因为它避免了错误归因；
- 发布脚本会顺手刷新 `reading/deep_dives/*` 与 `reading/quant_digests/*` 的站点时间戳，这些文件仍保持 dirty，本轮未将它们一并提交。

## Next recommended step

现在 foundation 页已经具备：
- taxonomy bridge
- limitation disclosure
- sample coverage
- event density

下一轮最自然的主点有两个：

1. **在文档/contract 层明确“当前 source 想升级到完整 ladder 比较，还缺哪些字段/事件表”**
   - 例如：是否需要单独的 event universe 表，而不是只靠 trade_detail。

2. **开始从当前 source 中提炼一版“best-effort breakout confirmation comparison”**
   - 但必须明确这是“current implemented confirmed breakout family”的比较，不是完整 raw→confirmed ladder。

如果只选一个，我建议下一轮优先做：
- **缺口清单 / data contract 增强**

原因：在当前 source 还不支持完整 ladder 时，先把“为了实现完整 foundation 还缺什么数据接口”写清楚，比继续硬拼半成品比较更稳。

## Commit hash (if committed)

- 已 selective commit：`2aa66cc` (`report(momentum): map source events into foundation taxonomy`)

## Commit note

repo 中仍有与本轮无关的 dirty files（例如 `reports/site/reading/deep_dives/*`、`reports/site/reading/quant_digests/*` 的自动刷新项，以及工作区外层的未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `scripts/build_trendline_event_foundation_report.py`
- `docs/TODO.md`
- `reports/artifacts/trendline_event_foundation/event_taxonomy_card.csv`
- `reports/site/factors/trendline_event_foundation/*`
- `reports/site/plans/*` 中受 TODO 更新影响的镜像页

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
