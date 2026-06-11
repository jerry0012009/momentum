# Add full-ladder data gap checklist to trendline_event foundation

## Why this was chosen now

这轮继续严格沿当前最近主线推进：补强 `trendline_event_foundation` 的 auditability，而不是硬做一个当前 source 其实不支持的“伪 confirmation ladder 比较”。

上一轮已经把 foundation 页补到了：
- `event_taxonomy_card`
- `source_limitations`
- `sample_coverage_table`
- `event_density_summary`

在检查当前 `trendline_event_slope_audit/trade_detail.csv` 后，确认了一个关键事实：
- 现有 source event buckets 是 `breakout_long / breakout_short / rebound_long / rebound_short`
- `breakout_*` 当前统一对应 `confirm_bars=3`
- `rebound_*` 当前统一对应 `confirm_bars=2`

这意味着：
- 当前 source 还不能直接支持 foundation taxonomy 想要的完整 ladder：
  - `raw_breach`
  - `close_confirm_same_bar`
  - `confirm1`
  - `confirm3`
  - `retest_hold`
- 如果在这种情况下硬去生成 `breakout_confirmation_comparison`，很容易把“当前 source event families”和“完整 ladder 层级”混为一谈。

因此，本轮选择一个更扎实、也更能帮助后续 Agent 的主点：
- **把“要升级到完整 ladder / full event universe 还缺什么数据接口”做成明确 checklist，并同时落到 foundation 页、contract.json 和 artifacts CSV 里。**

这样后续实现就不再停留在“我们知道当前数据不够”，而是进入“我们清楚具体缺什么”。

## What changed

### 1) 升级 `scripts/build_trendline_event_foundation_report.py`

脚本新增：
- `build_data_gap_checklist()`

当前固定导出一张缺口清单，列出为了实现完整 ladder / full event universe，还缺哪些关键数据接口：

1. `event_universe_table`
2. `event_bucket_enum`
3. `line_object_id`
4. `event_timestamp_fields`
5. `state_transition_fields`
6. `symbol_bar_count_by_sample`

每一项都包含：
- `missing_piece`
- `why_needed`
- `what_breaks_without_it`

也就是说，这张表不只是列名，而是把“为什么缺它会卡住 foundation 研究”也一起说清楚了。

### 2) foundation 页新增 `Data gaps to unlock the full ladder`

文件：
- `reports/site/factors/trendline_event_foundation/report.html`

页面新增独立区块：
- `Data gaps to unlock the full ladder`

它明确告诉读者：
- 现在为什么还不能直接比较 `raw_breach → close_confirm → confirm1 → confirm3 → retest_hold`
- 不是因为我们“还没想好”，而是因为当前 source 还缺这些确定的数据接口与事件表。

这一步让 foundation 页从“指出 limitation”进一步升级到“指出缺口与下一步需要补的数据 contract”。

### 3) contract.json 新增 machine-readable gap 信息

文件：
- `reports/site/factors/trendline_event_foundation/contract.json`

新增：
- `data_gaps_to_full_ladder`

也就是说：
- 这些 gap 不再只存在 HTML 说明文字里；
- 后续脚本或 Agent 也能直接从 `contract.json` 中读取当前缺口清单。

### 4) 新增 CSV 导出

新增：
- `reports/artifacts/trendline_event_foundation/data_gap_checklist.csv`

当前 shape：
- `(6, 3)`

这意味着 gap checklist 也成为了一个正式 artifact，而不只是散落在文档里的备注。

### 5) 回写 TODO

已在 `docs/TODO.md` 中新增并勾选：
- `明确“要升级到完整 ladder / full event universe 还缺什么数据接口”`

并写明：
- 当前 checklist 已经落到 foundation 页与 `contract.json`；
- 后续 Agent 可以直接据此知道：为了做完整 ladder，还需要补哪些表和字段。

## Validation / evidence

### A. 最小运行验证

执行：
- `python3 scripts/build_trendline_event_foundation_report.py`
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- 成功生成：
  - `reports/artifacts/trendline_event_foundation/data_gap_checklist.csv`
  - 更新后的 `report.html`
  - 更新后的 `contract.json`
- 成功发布站点

### B. CSV 检查

已确认：
- `data_gap_checklist.csv` → `(6, 3)`
- 前几项包括：
  - `event_universe_table`
  - `event_bucket_enum`
  - `line_object_id`
  - `event_timestamp_fields`
  - `state_transition_fields`
  - `symbol_bar_count_by_sample`

### C. 线上检查

已确认线上 foundation 页可读到：
- `Data gaps to unlock the full ladder`

同时页面中原有：
- `Current source event taxonomy mapping`
- `Current source limitations`

也仍保留，因此页面现在对“当前 source 代表什么 / 缺什么 / 还不能做什么”已经形成一套连续解释。

## Risks / caveats

- 这轮没有新增任何 event-return 统计；它解决的是 **数据 contract 缺口可视化**，不是收益层结果；
- gap checklist 当前是人工定稿的第一版，不排除后续实现时发现还需要再补其它字段；
- 发布脚本会顺手刷新 `reports/site/reading/deep_dives/*` 与 `reports/site/reading/quant_digests/*` 的站点时间戳，这些文件仍保持 dirty，本轮未将它们一并提交。

## Next recommended step

现在 foundation 页已经具备：
- taxonomy mapping
- source limitations
- full-ladder data gap checklist
- sample coverage
- event density

下一轮最自然的主点有两个：

1. **把 gap checklist 进一步转换成“目标数据表 schema 草图”**
   - 例如明确：
     - `event_universe_table.csv` 应该有哪些列
     - `state_transition_fields` 应该如何命名
     - `event_timestamp_fields` 最少需要哪些时间戳

2. **在当前 source 允许的范围内，开始做 best-effort 的 breakout / rebound family comparison**
   - 但必须明确它是 family-level，而不是完整 ladder-level。

如果只选一个，我建议下一轮优先做：
- **目标数据表 schema 草图**

原因：现在“缺什么”已经说清楚了，下一步最值得做的是把“补什么长什么样”也钉住。这样后续 Agent 才能真正开始补数据接口，而不是只知道有缺口。

## Commit hash (if committed)

- 已 selective commit：`95f624a` (`docs(momentum): add full-ladder data gap checklist`)

## Commit note

repo 中仍有与本轮无关的 dirty files（例如 `reports/site/reading/deep_dives/*`、`reports/site/reading/quant_digests/*` 的自动刷新项，以及工作区外层的未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `scripts/build_trendline_event_foundation_report.py`
- `docs/TODO.md`
- `reports/artifacts/trendline_event_foundation/data_gap_checklist.csv`
- `reports/site/factors/trendline_event_foundation/*`
- `reports/site/plans/*` 中受 TODO 更新影响的镜像页

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
