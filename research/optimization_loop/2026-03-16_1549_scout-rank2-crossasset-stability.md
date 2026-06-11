# 2026-03-16 15:49 UTC｜Scout Seat：Rank 2 combo_all 跨标的稳定性 write-back（paper candidate 保持窄范围）

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 当前属于 `waiting_not_due`，本轮不应空转。
- 因此回退到 `Run 2 / Scout Fast Lane`。
- 当前 Run 2 的优先对象仍是 `Rank 2 combo_all`，且 board 要求优先给出 `paper candidate / one more light check / park` 的硬结论，不做无止境 micro-slicing。

本轮只认领：
- **主点**：补齐 `Light Stability Pack` 的“跨标的稳定性”reader-facing硬卡（复用现有历史样本，不重开重型下载）。
- **紧邻子点**：把 verdict 同步进 scout 汇总页，避免只留日志/邮件不可见。

## 开始前检查
- `git status --short`：仓库存在大量与本轮无关历史脏文件/未跟踪文件；本轮只做 selective 变更，不混提。
- 最近 optimization logs 最新停在：
  - `2026-03-16_1527_run3-rank2-handoff-to-tiny-live-plumbing.md`
  - `2026-03-16_1523_scout-rank2-monitoring-board.md`
- 席位状态沿用 desk board：`Paper=EMA waiting_not_due`、`Live=暂空`、`Scout=默认主资源`。

## 本轮改动
1. 更新 `scripts/build_volume_supportflip_higherlow_first_verdict.py`
   - 新增 artifact 常量：
     - `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_cross_asset_stability_drycheck.csv`
   - 新增函数：
     - `build_cross_asset_stability_drycheck(...)`
     - `derive_cross_asset_stability_verdict(...)`
   - 在 report 中新增卡片：`cross-asset stability dry-check（BTC / ETH / SOL 同框）`
   - 在 `trial_meta.csv` 新增字段：`cross_asset_stability_verdict`

2. 更新 `scripts/build_trendline_alpha_scout_report.py`
   - 在 Rank 2 first-verdict 卡中新增 `cross-asset stability` 行；
   - 同步展示新 artifact 链接，保持 reader-facing 一致。

## 8.1 fallback 记录（本轮执行护栏）
- 本轮出现过 `edit` 的 `exact text` 未命中（模板块精确替换失败）。
- 已按要求立即 fallback：先 `read/定位`，再用更稳健的脚本定点改写方式完成插入，未将整轮判为失败。

## 最小验证（复用缓存）
已执行并通过：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
5. `grep` 命中：
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## 关键结果 / hard verdict
- 新增 deployable artifact：
  - `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_cross_asset_stability_drycheck.csv`
- 新 hard verdict（写入 `trial_meta.csv`）：
  - `cross-asset stability：combo_all 目前仍是 2/3 资产为正的窄范围 paper candidate，但 BTC 这条腿仍偏弱，当前更像 keep-narrower / one-more-light-check，而不是可直接升格。`
- desk 结论不变：
  - `Rank 2` 继续留在 `paper candidate pool（narrow scope）`，不得越级到 Live Seat / tiny-live。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- 首页索引已刷新：`https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 本轮只补跨标的稳定性明牌卡，不新增 forward continuity 证据。
- 仍需继续诚实保留 BTC 弱 pocket 的 watch，不得把“2/3 positive”写成全面稳定。

## Commit hash
- 基线：`76cea75`

## 未提交原因
- 当前 worktree 含大量与本轮无关脏文件；为避免混提，本轮仅完成 selective artifact / 页面刷新 / 日志与邮件交付。