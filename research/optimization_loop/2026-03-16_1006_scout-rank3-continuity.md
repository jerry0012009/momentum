# 2026-03-16 10:06 UTC｜Scout Rank 3 honest continuity：shared 15m cache 续到 09:45 后重跑 third-touch 窄门复核

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- **Run 1 / Paper Seat**：`EMA` 早前已完成 guarded refresh，并已如实回到 `waiting_not_due`；当前没有新的 `due-now / overdue` paper 动作。
- **Run 2 / Scout Seat**：上一轮之所以回退到 `Run 3`，是因为共享 Binance `15m` cache 三个币种最新 completed bar 仍只到 `2026-03-16 09:15 UTC`。
- 本轮先做最小核对后发现：共享 cache 已经可以诚实续到 `2026-03-16 09:45 UTC`，因此 `Rank 3 third_touch_plus_ema_macd` 这次确实出现了 genuinely new local bar，可执行一次 honest continuity，而不是继续 tiny-live fallback。

所以本轮只认领 1 个主点 + 1 个紧邻子点：
- **主点**：对 `Rank 3 third_touch_plus_ema_macd` 做一次基于新 completed 15m bar 的 honest continuity refresh
- **紧邻子点**：把 desk 回执同步到 `TODO` 顶部与 Scout 总览页，避免下一轮在没有新 bar 时重复同样本 continuity

## 本轮做了什么改动
### 1）把共享 Binance 15m cache 从 09:15 UTC 续到 09:45 UTC
直接对共享 cache 做最小增量 append，三个币种都新增 `2` 条 completed bars：

- `BTCUSDT`：`09:15 -> 09:45 UTC`
- `ETHUSDT`：`09:15 -> 09:45 UTC`
- `SOLUSDT`：`09:15 -> 09:45 UTC`

这一步的作用不是“刷新一个页面”，而是先确认本轮 Run 2 前提真的成立：
**必须先有 genuinely new local bar，后续 Scout continuity 才是合规动作。**

### 2）基于新 bar 重跑 Rank 3 continuity
执行：
- `python3 scripts/build_third_touch_ema_macd_first_verdict.py`
- `python3 scripts/build_trendline_alpha_scout_report.py`

刷新产物：
- `reports/artifacts/scout_third_touch_ema_macd_15m/variant_aggregate.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/asset_summary.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/trial_meta.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/friction_ladder.csv`

同步页面：
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

### 3）把这次 desk 回执写回 `TODO` 顶部
补充：
- `Scout Seat` 最新补充（`2026-03-16 10:06 UTC`）
- `Next 3 bot3 runs` 最新补充（`2026-03-16 10:06 UTC`）

含义很具体：
- 这轮 Run 2 是合规的，因为已经有新的 completed 15m bar；
- 但更新后结论基本不变，所以**如果下一轮没有新的 completed 15m bar，就不该再重跑同样本的 Rank 3 continuity，而应如实回退到 `Run 3 / tiny-live plumbing`。**

## 验证 / 证据
### 最小验证
1. `python3 -m py_compile scripts/build_third_touch_ema_macd_first_verdict.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py` ✅
2. 共享 cache append 后核对三个币种末端时间：均从 `2026-03-16 09:15 UTC` 续到 `2026-03-16 09:45 UTC` ✅
3. `python3 scripts/build_third_touch_ema_macd_first_verdict.py` ✅
4. `python3 scripts/build_trendline_alpha_scout_report.py` ✅
5. `python3 scripts/build_plans_site.py` ✅
6. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ✅
7. `grep -n "10:06 UTC\|third_touch_plus_ema_macd" docs/TODO.md reports/site/plans/momentum_todo.html reports/site/reading/trendline_alpha_scout/report.html` ✅

### 更新后的 hard verdict
`Rank 3` 最佳版本仍是 `third_touch_plus_ema_macd`：
- 跨资产 `mean_total_return` 约 `+0.78%`
- `mean_false_break_ratio = 0.00%`
- `positive_asset_ratio = 1/3`
- `mean_trades ≈ 0.33` 笔 / 资产

更诚实的读法：

**这次 continuity 说明 Rank 3 在新 completed bar 下没有塌掉，仍比深负的 `raw_breakout` 更像可保留的窄门 structure-confirmation guard；但它的样本仍很窄，交易也很稀，因此还不是 replace-ready / tiny-live ready。**

支持这句话的证据：
- `raw_breakout` 仍深负，跨资产 `mean_total_return` 约 `-45.14%`
- `third_touch_plus_ema_macd` 仍维持正的跨资产平均收益与 `0.00%` false-break ratio
- 但它依旧只在 `1/3` 资产上赚钱，且交易数很少，说明目前更像“有边界的 confirmation guard”，而不是能立即接管 Live Seat 的新主角

## 风险 / 边界
- 这不是新 alpha 主线，也不是 Live Seat replace verdict。
- 本轮只是基于新增 completed 15m bars 做 honest continuity，不代表已经完成 forward 审核、venue 偏差校验或 tiny-live 配套。
- `Rank 3` 交易数仍很稀，读法容易被少量样本左右；因此当前只能维持 `keep-narrower`，不能往前夸成 replace-ready。

## 下一步建议
1. 若下一轮 `EMA` 仍处于 `waiting_not_due`，先再核对 `Scout` 是否有 genuinely new completed 15m bar：
   - **有**：继续做一次 honest Scout continuity
   - **没有**：不要重复这份样本，直接回退到 `Run 3 / tiny-live plumbing`
2. `tiny-live` fallback 默认继续沿 `review ticket / closeout / writeback` 这条执行链往前补，而不是回头补抽象说明页。
3. `breakout` 继续按 `bench / recheck-only` 处理；没有 genuinely new blocker reduction 前，不应重新抢占默认资源。

## 网页可见落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页：`https://jp.jerrypsy.top/momentum/`

## Commit hash
- HEAD：`573439c`
- 本轮未提交。

## 如果未提交，原因
当前 worktree 仍有大量与本轮无关的既有脏文件与未跟踪文件；本轮只做 selective cache append、Scout continuity 刷新、`TODO/plans` 同步与首页发布，避免混提。
