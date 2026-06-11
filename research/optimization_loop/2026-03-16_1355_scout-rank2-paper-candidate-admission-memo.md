# 2026-03-16 13:55 UTC｜Scout Seat：Rank 2 combo_all 窄范围 paper candidate admission memo

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 处于 `waiting_not_due`，当前没有 `due-now / overdue` refresh。
- 因此本轮切到 `Run 2 / Scout Fast Lane`。
- `Next 3 bot3 runs` 当前明确要求优先做：`Rank 2 combo_all -> paper-candidate narrow scope / admission memo`。

本轮只认领：
- **主点**：把 Rank 2 从“快筛结论”收紧为可落地的 `paper candidate admission memo`（可部署口径产物）。
- **紧邻子点**：同步更新 reader-facing 页面（factor 页 + scout 汇总页），并发布首页索引。

## 开始前检查
- `git status --short`：仓库存在大量与本轮无关的历史脏文件与未跟踪文件；本轮仅做 selective 修改，不混提。
- 最近 runs：
  - `2026-03-16_1246_scout-rank2-shadow-readiness.md`
  - `2026-03-16_1302_scout-rank2-trade-count-honesty.md`
  - `2026-03-16_1315_scout-rank2-time-stability.md`
  - `2026-03-16_1334_scout-rank2-parameter-stability.md`
- 当前席位：`Paper=EMA waiting_not_due`，`Live=暂空`，`Scout=优先`。

## 本轮做了什么
1. 修改 `scripts/build_volume_supportflip_higherlow_first_verdict.py`：
   - 新增 artifact 路径：
     - `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_admission_memo.csv`
   - 新增 admission memo 生成逻辑：
     - `build_paper_candidate_admission_memo(...)`
     - `derive_paper_candidate_admission_verdict(...)`
   - 将 admission verdict 写入 `trial_meta.csv`（字段 `paper_candidate_admission_verdict`）
   - 在 factor report 新增 `paper candidate admission memo（narrow scope）` 卡片。

2. 修改 `scripts/build_trendline_alpha_scout_report.py`：
   - 在 Rank 2 卡片读取并展示 `paper_candidate_admission_verdict`
   - 同步更新 Rank 2 的 desk role 口径为“窄范围 paper candidate / keep-narrower challenger”。

3. 修复本轮执行中的脚本级错误（非 edit exact-match）：
   - 首次构建时因函数实参误带入未定义变量触发 `UnboundLocalError`；
   - 立即修正调用签名与 `write_report` 参数对齐后重跑通过。

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
5. `grep` 校验网页落点：
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## 关键结果 / hard verdict
新增 admission memo 产物：
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_admission_memo.csv`

核心结论：
- `combo_all` 已满足进入**窄范围** `paper candidate pool` 的最小条件（clean replication + Light Stability Pack 未判死 + 规则/诚实守门可写清）。
- 但必须保留 `one more light check` 标签：
  - `idle_gap_guard=fail`（最大空窗约 58.6 天）
  - `time_false_break_guard=fail`
  - `early bucket` 仍是负 pocket（约 `-1.34%`, `0/3` positive）
- 因此当前**只允许** `paper candidate（narrow scope）`，不得偷升格成 `Live Seat / tiny-live ready`。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 本轮仍是历史样本快筛收紧，不是新的 forward continuity 证据。
- admission memo 属于 `paper candidate` 准入文档，不等于 live 准入。

## Commit hash（基线）
- `76cea75`

## 如果未提交，原因
当前 worktree 有大量与本轮无关脏文件；为避免混提，本轮仅做 selective 构建、网页刷新、日志与邮件交付，不做提交。
