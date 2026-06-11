# 2026-03-16 14:23 UTC｜Scout Seat：Rank 3 补齐 trade-count / time stability 轻量诚实守门

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：

- `Run 1 / Paper Seat`：`EMA` 当前处于 `waiting_not_due`，没有新的 due-now / overdue 动作。
- 因此切到 `Run 2 / Scout Fast Lane`。
- `Rank 2 combo_all` 已在上一轮完成 `paper candidate admission memo`，本轮优先推进 `Rank 3` 的 Light Stability Pack 缺口（明确要求优先补 `trade-count / time stability`，而不是继续追新 bar）。

本轮只认领：
- **主点**：为 `Rank 3 third_touch_plus_ema_macd` 增加 `trade-count honesty` 与 `time stability dry-check` 两张轻量守门卡，并给出 hard verdict 边界。
- **紧邻子点**：同步 reader-facing 页面（factor 页 + scout 汇总页 + 首页索引）。

## 开始前检查
- `git status --short`：工作区存在大量与本轮无关脏文件/未跟踪文件，本轮坚持 selective 改动，不混提。
- 最近 runs：
  - `2026-03-16_1355_scout-rank2-paper-candidate-admission-memo.md`
  - `2026-03-16_1334_scout-rank2-parameter-stability.md`
  - `2026-03-16_1315_scout-rank2-time-stability.md`
- 当前席位：`Paper=EMA waiting_not_due`，`Live=暂空`，`Scout=默认主资源`。

## 本轮做了什么
1. 修改 `scripts/build_third_touch_ema_macd_first_verdict.py`：
   - 新增 artifacts：
     - `reports/artifacts/scout_third_touch_ema_macd_15m/trade_detail.csv`
     - `reports/artifacts/scout_third_touch_ema_macd_15m/trade_count_honesty.csv`
     - `reports/artifacts/scout_third_touch_ema_macd_15m/time_stability_drycheck.csv`
   - 新增函数：
     - `build_trade_count_honesty(...)` / `derive_trade_count_honesty_verdict(...)`
     - `build_time_stability_drycheck(...)` / `derive_time_stability_verdict(...)`
   - 将 verdict 写入 `trial_meta.csv`：
     - `trade_count_honesty_verdict`
     - `time_stability_verdict`
     - 对应 bullets 字段
   - 在 Rank 3 factor 页面新增两张卡：
     - `trade-count honesty / cadence dry-check`
     - `time stability dry-check`

2. 修改 `scripts/build_trendline_alpha_scout_report.py`：
   - Rank 3 卡片新增 `trade-count honesty`、`time stability` 两行，避免只展示 friction headline。

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_third_touch_ema_macd_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_third_touch_ema_macd_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `bash scripts/publish_homepage_index.sh`
5. `grep` 校验网页落点：
   - `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## 关键结果 / hard verdict
新增稳定性守门结论：

- `trade-count honesty`：**fail**（样本过薄）
  - `total trades = 1`（门槛 `>=9`）
  - `active assets = 1/3`
  - `min asset trades = 1`
  - `min active months per asset = 1`
- `time stability dry-check`：**fail**（不具备诚实三段切片条件）
  - `three_bucket_sample_floor` fail
  - `bucket_asset_coverage` fail
  - 因样本过薄，`positive_bucket_floor / bucket_trade_floor` 记为 `not attempted + fail`

一句话结论：
- `Rank 3` 当前虽然在 friction 上保留正向迹象，但 `trade-count / time stability` 都明确提示“样本太薄”，因此只能维持 `keep-narrow / one-more-light-check`，不能升格成 `paper candidate` 或 `live challenger`。

## 网页可见落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 本轮严格使用已有历史 cache，不引入新 bar。
- 本轮是 Light Stability Pack 的诚实补门，不是 forward continuity 证据。
- 由于样本极稀疏，当前结论偏保守是预期行为，不应被误读为“策略完全无效”。

## Commit hash（基线）
- `76cea75`

## 如果未提交，原因
当前 worktree 有大量与本轮无关脏文件；为避免混提，本轮只做 selective 构建、网页刷新、日志与邮件交付，不提交。