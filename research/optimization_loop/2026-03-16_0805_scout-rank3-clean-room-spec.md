# 2026-03-16 08:05 UTC｜Scout Rank 3：把 third-touch + EMA/MACD confluence 压成 clean-room spec

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行当前 desk 顺序：

- **Run 1 / Paper Seat**：`EMA` 已明确回到 `waiting_not_due`，当前没有新的 `due-now / overdue` refresh 可写，不能继续重复 paper 守门。
- **Run 2 / Live Seat**：`breakout` 已完成 `bench` 的 reader-facing sync，当前没有 genuinely new `pure-test / down-tail` blocker reduction，不值得继续做同类 rerun。
- 因此本轮自动切到 **Run 3 / Scout Seat 或 tiny-live plumbing**。

在 Run 3 内继续按最新 desk 约束判断：

- `Rank 1 τ-band` 目录最新本地 artifact 仍停在 `03:53 UTC`，没有足够新 bar 可做 honest recheck；
- `Rank 2 combo_all` 已经拿到 `first verdict + friction recheck`，继续对同样本做近义续切的边际价值很低；
- 所以这轮最合理的主点，不是再重读旧样本，而是把 **`Rank 3 third-touch + EMA/MACD confluence`** 冻结成下一轮可直接实现的本地实验 spec。

## 本轮主点 + 紧邻子点
### 主点
新增 Rank 3 的最小 clean-room spec：

- 新脚本：`scripts/build_third_touch_ema_macd_scout_spec.py`
- 新 artifact：`reports/artifacts/scout_third_touch_ema_macd_15m/clean_room_spec_v1.csv`
- 新页面：`reports/site/factors/scout_third_touch_ema_macd_15m/report.html`

本轮冻结的关键口径：
- 市场 / 周期：`BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m`
- 方向层：`EMA20 > EMA50` 只做多 breakout；反之只做空 breakout
- 结构层：用 `2-left/2-right` swing highs/lows 先构造 `candidate boundary`
- 核心确认：`third_touch_confirmation`
- breakout 约束：`2-of-3 closes outside + 0.05 ATR persistence`
- 共识层：`EMA slope` + `MACD histogram / line-signal` 同向
- 首轮对照矩阵：
  - `raw_breakout`
  - `third_touch_only`
  - `third_touch_plus_ema`
  - `third_touch_plus_ema_macd`
- 执行层：`next-bar open entry | 1 ATR stop | 2 ATR target | 8-bar time stop | 6 bps/side`
- 评分板：`post_cost_return / false_break_ratio / persistence_pass_rate / time_to_failure / max_drawdown / positive_asset_ratio / trades_per_asset`
- bench 规则也提前写死：如果 `third_touch_plus_ema_macd` 既不能改善收益，也不能改善假突破率，或者交易数压缩过猛却没有带来更好覆盖，就直接 `bench`

### 紧邻子点（reader-facing sync）
把 Rank 3 spec 同步挂回 reader-facing 页面，而不是只留在单独 factor 页：

- 修改：`scripts/build_trendline_alpha_scout_report.py`
- 更新：`reports/site/reading/trendline_alpha_scout/report.html`
- 更新：`docs/TODO.md`
- 更新：`reports/site/plans/momentum_todo.html`

同步后的外显口径是：

**Rank 3 现在已 implementation-ready，可在后续没有 genuinely new local bar 的窗口里，直接推进 first verdict；但它现在仍只是 spec-ready，不是 replace-ready / tiny-live ready。**

## 做了什么改动
1. 新建 `scripts/build_third_touch_ema_macd_scout_spec.py`
   - 输出 `clean_room_spec_v1.csv` 与 `spec_meta.csv`
   - 生成独立 factor 页面 `scout_third_touch_ema_macd_15m/report.html`
2. 修改 `scripts/build_trendline_alpha_scout_report.py`
   - 新增 `Run 3 fallback（Rank 3 · third-touch + EMA/MACD confluence spec）` 卡片
   - 让 Scout 总览页能直接看到 Rank 3 已进入 implementation-ready 状态
3. 更新 `docs/TODO.md`
   - 在 `Scout Seat` 最新补充中加入 `2026-03-16 08:05 UTC` 这一轮的 spec sync
4. 刷新相关页面
   - `python3 scripts/build_trendline_alpha_scout_report.py`
   - `python3 scripts/build_plans_site.py`
   - `bash scripts/publish_homepage_index.sh`

## 验证 / 证据
执行了最小必要验证：

1. `python3 -m py_compile scripts/build_third_touch_ema_macd_scout_spec.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py` ✅
2. `python3 scripts/build_third_touch_ema_macd_scout_spec.py` ✅
3. `python3 scripts/build_trendline_alpha_scout_report.py` ✅
4. `python3 scripts/build_plans_site.py` ✅
5. `bash scripts/publish_homepage_index.sh` ✅
6. `grep -n "third-touch + EMA/MACD confluence spec\|scout_third_touch_ema_macd_15m\|08:05 UTC" reports/site/reading/trendline_alpha_scout/report.html reports/site/factors/scout_third_touch_ema_macd_15m/report.html reports/site/plans/momentum_todo.html docs/TODO.md` ✅
7. `sed -n '1,8p' reports/artifacts/scout_third_touch_ema_macd_15m/clean_room_spec_v1.csv` ✅

已确认：
- Rank 3 新 artifact 已生成；
- Rank 3 factor 页面可直接阅读；
- Scout 总览页已出现新的 Run 3 fallback 卡片；
- `TODO / plans` 已同步 `08:05 UTC` 的最新补充；
- 首页 index 已刷新并发布到站点首页。

## 本轮 hard verdict
一句话结论：

**这轮最有效的推进，不是继续对没有 genuinely new local bar 的 Rank 1 做近义 recheck，而是把 Rank 3 的 third-touch + EMA/MACD confluence 冻结成 implementation-ready spec，缩短下一轮的 time-to-first-verdict。**

证据如何支持这句话：
- 新 spec artifact 已落地；
- factor 页面与 Scout 总览页都已 reader-facing 可见；
- `TODO / plans` 已同步当前排兵布阵；
- 当前没有把 Rank 3 提前吹成 performance verdict，只如实写成 `spec-ready`。

## 风险 / 边界
- 这轮没有跑 Rank 3 的 performance slice，因此不能把它写成 replace-ready 候选。
- `candidate_boundary` 当前先用 swing-boundary 近似版，而不是完整主观斜趋势线；这是为了先保证因果可实现性。
- `third-touch + EMA/MACD` 很容易出现“看起来更干净，但几乎不交易”的假改善，所以后续 first verdict 必须同时看 `trades_per_asset` 与 `positive_asset_ratio`。

## 下一步建议
1. 若下一轮仍落到 `Run 3` 且没有 genuinely new local bar，优先实现 `raw_breakout + third_touch_only + third_touch_plus_ema_macd` 三档 first slice，而不是继续补解释页。
2. 若 `Rank 1 τ-band` 真出现足够新 bar，再回去做 honest recheck；不要把旧样本硬解释成新进展。
3. 若 tiny-live plumbing 再认领，优先补更接近实际 route/shadow ledger 对账的执行动作，而不是回头重写抽象规则。

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
