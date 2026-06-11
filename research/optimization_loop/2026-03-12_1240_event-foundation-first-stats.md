# Add first real statistics to trendline_event foundation

## Why this was chosen now

这轮继续严格沿当前最近主线推进：把 `trendline_event_foundation_report` 从 skeleton / contract-only 再往前推一步，填入第一批真实统计。

上一轮已经完成了：
- `scripts/build_trendline_event_foundation_report.py`
- `report.html + contract.json` skeleton
- TODO 中相应的 I/O contract 说明

在这个上下文里，最自然、最小步、但最有实质推进意义的一步，不是继续写文档，而是让 foundation 页真正开始吃到真实历史数据。按照此前已经定好的最小读法，最先该填的两块就是：
1. `sample_coverage_table`
2. `event_density_summary`

原因很明确：
- 没有样本覆盖表，后面一切比较都可能建在稀薄样本上；
- 没有事件密度表，后面即使某类事件 forward return 好看，也无法判断它是“稀有好看”还是“可用频率”。

因此本轮选择：
- **主点：把 foundation skeleton 升级成 partial-stats 页面**
- 紧邻子点：导出两个 machine-readable CSV，便于后续 Agent 直接复用

## What changed

### 1) 升级 `scripts/build_trendline_event_foundation_report.py`

脚本不再只是生成一个纯 contract-only 的 HTML，而是开始读取现有真实数据：
- `reports/artifacts/trendline_event_slope_audit/trade_detail.csv`
- `reports/artifacts/trendline_event_slope_audit/sample_meta.csv`

当前第一轮只过滤默认资产 universe：
- BTC-USD
- ETH-USD
- SOL-USD
- DOGE-USD
- XRP-USD

并基于这些现有 slope-audit 产物生成：
- `sample_coverage_table`
- `event_density_summary`

### 2) foundation report 页面从 `contract_only` 升级为 `partial_stats`

文件：
- `reports/site/factors/trendline_event_foundation/report.html`
- `reports/site/factors/trendline_event_foundation/contract.json`

现在页面明确说明：
- 当前状态不再是 contract-only；
- 已有两块真实统计填入；
- 当前真实数据来源是 `trendline_event_slope_audit`。

### 3) 新增 machine-readable 导出

新增：
- `reports/artifacts/trendline_event_foundation/sample_coverage_table.csv`
- `reports/artifacts/trendline_event_foundation/event_density_summary.csv`

#### `sample_coverage_table.csv`
按以下维度聚合样本数：
- `sample_key`
- `timeframe`
- `period`
- `asset`
- `line_side`
- `event_bucket`
- `sample_count`
- `confidence_flag`

其中 `confidence_flag` 按既有第一轮规则生成：
- `<25` → `display-only`
- `25~49` → `low-confidence`
- `>=50` → `ok`

#### `event_density_summary.csv`
当前用 `sample_meta.csv` 的 `rows / symbols` 估算每个 sample 的平均 bars per symbol，再计算：
- `events_per_1k_bars`
- `avg_bars_between_events`

并在表中明确标记：
- `density_note = approx via sample_meta avg rows per symbol`

也就是说，这是一版**近似但有用**的第一轮密度视图，而不是伪装成精准 bar-level density 的黑盒。

### 4) 回写 TODO

已在 `docs/TODO.md` 中新增并勾选：
- `先往 foundation skeleton 中填第一批真实统计`

并明确写入：
- 当前已真实填入 `sample_coverage_table` 与 `event_density_summary`
- 页面状态已从 `contract_only` 升级为 `partial_stats`

## Validation / evidence

### A. 最小运行验证

执行：
- `python3 scripts/build_trendline_event_foundation_report.py`
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- 成功写出：
  - `reports/site/factors/trendline_event_foundation/report.html`
  - `reports/site/factors/trendline_event_foundation/contract.json`
  - `reports/artifacts/trendline_event_foundation/sample_coverage_table.csv`
  - `reports/artifacts/trendline_event_foundation/event_density_summary.csv`
- 成功发布站点

### B. 线上检查

已确认线上可打开：
- `/momentum/factors/trendline_event_foundation/report.html`

页面中已经能看到：
- `Current page status`（状态为 `partial_stats`）
- `Sample coverage table`
- `Event density summary`

### C. CSV 形状检查

本轮生成的两张第一批真实统计表当前形状为：
- `sample_coverage_table.csv` → `(79, 8)`
- `event_density_summary.csv` → `(79, 9)`

这说明当前在默认 5 个 crypto 资产上，已经能形成一个可读的第一批 event foundation 统计视图。

## Risks / caveats

- 当前真实统计来源仍是 `trendline_event_slope_audit`，所以它更接近“现有 slope-audit 产物在 foundation 页中的第一轮复用”，还不是完整 P1 实现；
- `event_density_summary` 目前用 `sample_meta` 的平均 bars per symbol 估算，属于第一轮近似密度，不应被误读成逐 symbol 精确 bars 计数；
- 当前表里仍混有 `breakout_long / breakout_short / rebound_long / rebound_short` 等 event bucket，后续若 foundation 页要更严格贴合 event taxonomy，可能还需要再统一映射命名；
- 发布脚本会顺手刷新 `reports/site/reading/deep_dives/*` 与 `reports/site/reading/quant_digests/*` 的站点时间戳，本轮未将这些自动刷新项一并提交。

## Next recommended step

现在 foundation 页已经从 contract-only 进入 partial-stats。下一轮最自然的主点有两个：

1. **开始填 `breakout_confirmation_comparison`**
   - 这是最符合当前默认阅读顺序的下一块真实统计；
   - 也最直接承接已定稿的 confirmation ladder。

2. **开始填 `rebound_confirmation_comparison`**
   - 与 breakout 对称，能帮助尽快进入“breakout vs rebound”的第一轮核心比较。

如果只选一个，我建议下一轮优先做：
- **`breakout_confirmation_comparison`**

原因：当前 foundation 页已经有了样本覆盖与事件密度，最自然的下一块就是开始回答“raw vs confirmed 到底有没有改善质量”。

## Commit hash (if committed)

- 已 selective commit：`7bb250d` (`feat(momentum): add first event foundation statistics`)

## Commit note

repo 中仍有与本轮无关的 dirty files（例如 `reports/site/reading/deep_dives/*`、`reports/site/reading/quant_digests/*` 的自动刷新项，以及工作区外层的未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `scripts/build_trendline_event_foundation_report.py`
- `docs/TODO.md`
- `reports/site/factors/trendline_event_foundation/*`
- `reports/artifacts/trendline_event_foundation/*`
- `reports/site/plans/*` 中受 TODO 更新影响的镜像页

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
