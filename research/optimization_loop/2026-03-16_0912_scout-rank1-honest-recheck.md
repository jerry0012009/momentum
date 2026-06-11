# 2026-03-16 09:12 UTC｜Scout Seat Rank 1 τ-band honest recheck

## 为什么这轮做这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：`Paper Seat = EMA` 在 `07:13 UTC` 已如实回到 `waiting_not_due`，所以这一轮不能继续在 Paper 守门空转。
- 当前 `breakout` 仍是 `bench / recheck-only`，没有新的 `pure-test / down-tail` blocker reduction，因此不应回去做 Live Seat heavy rerun。
- `Next 3 bot3 runs` 对当前窗口的首选动作写得很明确：**先检查 `Rank 1 τ-band` 是否终于有 genuinely new local bar 可做 honest recheck**；若有，就先做这件事。

## 本轮认领
- 主点：对 `Scout Rank 1 τ-band / no-trade breakout filter` 做一次基于**真新 15m bar**的 honest recheck。
- 紧邻子点：把 recheck 结果同步到 `trendline_alpha_scout` 总览页与 `TODO` 顶部 Desk Board，避免结果只留在 artifact 目录里。

## 做了什么改动
1. 先单独核对远端 Binance 最新 15m bar，确认三币种（`BTCUSDT / ETHUSDT / SOLUSDT`）都已出现本地 cache 之后的新 bar：
   - 本地旧 cache 末端：`2026-03-16 03:45 UTC`
   - 远端已可见完成 bar：至少到 `2026-03-16 08:45 UTC`，并已有进行中的 `09:00 UTC` bar
2. 因为 `build_tau_band_breakout_scout_report.py` 的 cache freshness 是 `6h`，直接运行会继续复用旧 cache；所以本轮仅把 Rank 1 cache 文件时间戳回拨到过期状态，触发脚本按原逻辑重拉，不改策略逻辑本身。
3. 运行：
   - `python3 scripts/build_tau_band_breakout_scout_report.py`
   - `python3 scripts/build_trendline_alpha_scout_report.py`
4. 同步更新：
   - `docs/TODO.md` 顶部 `Scout Seat` 最新补充
   - `python3 scripts/build_plans_site.py`
   - `bash scripts/publish_homepage_index.sh`

## 验证 / 证据
### 1）新 cache 的真实时间已经前推
`reports/artifacts/scout_tau_band_breakout_15m/cache_meta.csv` 现在显示：
- `BTC / ETH / SOL` 三个 15m cache 的 `last_bar_utc` 都已更新到 `2026-03-16 09:00 UTC`
- 样本窗口相应滚动为 `2025-11-16 09:15 UTC -> 2026-03-16 09:00 UTC`

### 2）Rank 1 最新 aggregate 结果
最新 `variant_aggregate.csv`：
- `confirm2of3_tau_010`：
  - `mean_total_return ≈ -11.16%`
  - `mean_false_break_ratio ≈ 41.03%`
  - `mean_trades ≈ 142.67`
  - `positive_asset_ratio = 0/3`
- 对照 `raw_breakout`：
  - `mean_total_return ≈ -45.37%`
  - `mean_false_break_ratio ≈ 50.17%`

### 3）本轮 hard verdict 没有被新 bar 改写
`trial_meta.csv` 当前口径：
- **`confirm2of3_tau_010` 只是相对 raw 更不差，但绝对 post-cost return 仍为负；保留为 scout follow-up / execution guard 候选，不是 replace-ready winner。`**

## 本轮硬结论（hard verdict）
- `Rank 1 τ-band` 这次终于拿到了 genuinely new local bar，因此这轮 recheck 是合规且有意义的；
- 但新 bar **没有**把它推成 replace-ready challenger：它依旧只是“相对 raw 更不差”的 guard，不能据此抢走当前 Live Seat；
- 因此若后续 `EMA` 继续 `waiting_not_due`，Scout 默认主资源应更偏向 `Rank 2 combo_all` / `Rank 3 third_touch_plus_ema_macd` 的轻量 forward continuity，而不是继续在 `τ-band` 上做近义重写。

## 风险 / 边界
- 本轮虽然是 honest recheck，但样本仍只是一组 `120d / 15m / 3` 币种的本地 scout slice，不是 live-ready 证据。
- 这轮没有改策略逻辑，只是用真新 bar 刷新 Rank 1 现有实验；因此不应把它表述成“发现了新 alpha”。
- `09:00 UTC` 这根 bar 在拉取时已进入 cache 窗口；后续若要继续用它做 forward continuity，应继续保持 completed-bar 口径一致，避免拿进行中 bar 说成已完成 forward。

## 网站可见落点
- `reports/site/factors/scout_tau_band_breakout_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页已通过 `publish_homepage_index.sh` 刷新

## Commit hash
- HEAD：`300b0c2`
- 本轮未提交。

## 如果未提交，原因
- 当前 worktree 存在大量与本轮无关的既有脏文件与未跟踪文件；本轮只做 selective 刷新与同步，避免混提。
