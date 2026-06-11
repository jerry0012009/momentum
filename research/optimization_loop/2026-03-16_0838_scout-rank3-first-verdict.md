# 2026-03-16 08:38 UTC｜Scout Rank 3 first verdict：把 third-touch + EMA/MACD confluence 从 spec 推到本地最小 verdict

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行当前 desk 顺序：

- **Run 1 / Paper Seat**：`EMA` 已在更早轮次完成 guarded refresh，并回到 `waiting_not_due`；当前没有新的 due-now / overdue lane，不该重复守门。
- **Run 2 / Live Seat**：`breakout` 已完成 `bench` 的 reader-facing sync；当前没有 genuinely new blocker reduction，不值得继续同类 rerun。
- **Run 3 / Scout Seat**：`Rank 1 τ-band` 仍缺 genuinely new local bar；`Rank 2 combo_all` 已有 `first verdict + friction recheck`；而 `Rank 3 third-touch + EMA/MACD confluence` 上一轮已经冻结成 implementation-ready spec。

所以本轮不再继续补近义 spec 文案，而是只认领 1 个主点 + 1 个紧邻子点：

- **主点**：把 `Rank 3` 从 `spec-ready` 推到 `15m crypto` 本地 `first verdict`
- **紧邻子点**：把 verdict 同步挂到 `trendline_alpha_scout` / `TODO` / plans，让当前 Run 3 的 desk 读法外显

## 本轮做了什么改动
### 1）新增 Rank 3 first verdict 脚本与 artifacts
新增脚本：
- `scripts/build_third_touch_ema_macd_first_verdict.py`

新增 artifacts：
- `reports/artifacts/scout_third_touch_ema_macd_15m/variant_aggregate.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/asset_summary.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/trial_meta.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/event_sample.csv`

本轮实现口径：
- 继续复用既有 `Binance 120d / 15m / BTC ETH SOL` cache
- 对照矩阵：
  - `raw_breakout`
  - `third_touch_only`
  - `third_touch_plus_ema`
  - `third_touch_plus_ema_macd`
- 执行口径继续沿用：
  - `next-bar open entry`
  - `1 ATR stop`
  - `2 ATR target`
  - `8-bar time stop`
  - `6 bps/side`

### 2）把 Rank 3 页面从 spec-only 改成 verdict page
更新：
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`

当前页面不再只是 clean-room spec，而是已经展示：
- `variant aggregate`
- `per-asset summary`
- `sample events`
- `hard verdict`
- `next step`

### 3）同步 reader-facing 总览与指挥板
更新：
- `scripts/build_trendline_alpha_scout_report.py`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- 首页 index（`bash scripts/publish_homepage_index.sh`）

同步后的 desk 口径改成：
- `Rank 3` 不再只是 `implementation-ready spec`
- 当前更像 **keep-narrower guard / first-verdict-passed**
- 后续若继续落到 `Run 3`，默认优先做更轻量的 `forward / friction` 复核，而不是回头重复 spec-only sync

## 核心结果 / hard verdict
一句话结论：

**`Rank 3 third-touch + EMA/MACD confluence` 已从 spec 推到 first verdict；当前最强版本是 `third_touch_plus_ema_macd`，它明显比深负的 `raw_breakout` 更诚实，但样本太窄、交易太少，所以现在只配当更窄的 structure-confirmation guard，不配写成 replace-ready / tiny-live ready。**

证据：
- `third_touch_plus_ema_macd`
  - `mean_total_return ≈ +0.78%`
  - `mean_false_break_ratio = 0.00%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades ≈ 0.33` 笔/资产
- 对照的 `raw_breakout`
  - `mean_total_return ≈ -45.80%`
  - `mean_false_break_ratio ≈ 49.11%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 500.67` 笔/资产

更诚实的解读是：
- `Rank 3` 的窄门过滤确实切掉了大量噪声；
- 但当前增量高度依赖极少数信号，覆盖面远不够；
- 所以它值得保留为更窄的 confirmation guard 候选，但还不能升级成 Live Seat 替代者，更不能偷渡成 tiny-live 候选。

## 最小验证
本轮只做最小必要验证：

1. `python3 -m py_compile scripts/build_third_touch_ema_macd_first_verdict.py scripts/build_third_touch_ema_macd_scout_spec.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py` ✅
2. `python3 scripts/build_third_touch_ema_macd_first_verdict.py` ✅
3. `python3 scripts/build_trendline_alpha_scout_report.py` ✅
4. `python3 scripts/build_plans_site.py` ✅
5. `bash scripts/publish_homepage_index.sh` ✅
6. `grep -n "08:38 UTC\|third_touch_plus_ema_macd\|Run 3 本地 first verdict" reports/site/plans/momentum_todo.html reports/site/reading/trendline_alpha_scout/report.html reports/site/factors/scout_third_touch_ema_macd_15m/report.html docs/TODO.md` ✅

已确认：
- Rank 3 新 verdict artifacts 已生成；
- factor 页面已从 spec-only 变成 first verdict 页面；
- `trendline_alpha_scout` 已出现新的 Run 3 first verdict 卡；
- `TODO / plans` 已同步 `2026-03-16 08:38 UTC` 的最新 desk 口径；
- 首页 index 已刷新并发布。

## 风险 / 边界
- 当前样本仍只有 `BTC / ETH / SOL | 120d | 15m`，覆盖明显不足。
- `third_touch_plus_ema_macd` 现在看起来最干净，但本质上只在 `SOL` 上留下了极少量有效交易；这更像是“可能有用的更窄 guard”，不是已跨资产成立的稳定候选。
- `raw_breakout` 目前深负，部分原因来自高频高噪声的基线过宽；这说明 Rank 3 的相对改善有意义，但不等于绝对可部署。
- 本轮没有做额外 friction ladder 或 forward continuation，因此当前不能把它写成 next-live challenger。

## 下一步建议
1. 若下一轮仍落到 `Run 3` 且 `Rank 1` 依旧没有 genuinely new local bar，优先只对：
   - `Rank 2 combo_all`
   - 或 `Rank 3 third_touch_plus_ema_macd`
   做更轻量的 `forward / friction` 复核。
2. 若 `Rank 3` 的 full EMA+MACD 版本继续只有极少交易，则应把它收窄成“guard-only 候选”，不要继续往 replace-ready 方向硬吹。
3. 若 `Rank 1 τ-band` 真出现足够新 bar，再把主资源切回 honest recheck，而不是在旧样本上无限续切 Rank 3。

## 网页可见落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页已通过 `publish_homepage_index.sh` 刷新

## Commit hash
- HEAD：`300b0c2`
- 本轮未提交。

## 如果未提交，原因
- 当前工作区仍有大量与本轮无关的既有脏文件与未跟踪文件；本轮继续只做 selective 改动与页面刷新，避免混提。
