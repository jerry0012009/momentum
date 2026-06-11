# 2026-03-16 09:26 UTC｜Scout Seat：Rank 2 combo_all honest light forward refresh

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行本轮排班：

- **Run 1 / Paper Seat**：`EMA` 已在更早一轮完成 guarded refresh，并如实回到 `waiting_not_due`；A 股下一次 close 仍未到，当前不能伪造 paper continuation。
- **Run 2 / Scout Seat**：`Rank 1 τ-band` 已在上一轮拿到 `09:00 UTC` bar 的 honest recheck，且结论仍只是 execution guard / scout follow-up；按板上最新口径，当前不应继续在 `τ-band` 上做近义重写。
- **因此本轮只认领 1 个主点**：把共享 Binance 15m cache 用最小增量方式续到 `09:15 UTC`，随后只对 `Rank 2 combo_all` 做一次 honest light forward refresh。
- **紧邻子点**：把这次 continuity 结果同步到 `Trendline Alpha Scout` 总览页与 `TODO Desk Board` 镜像，避免只留在日志里。

## 做了什么改动
### 主点（Run 2 / Scout Seat）
1. 对共享 Binance 15m cache 做最小增量续接：
   - `reports/artifacts/scout_tau_band_breakout_15m/cache/BTCUSDT__120d__15m.csv`
   - `reports/artifacts/scout_tau_band_breakout_15m/cache/ETHUSDT__120d__15m.csv`
   - `reports/artifacts/scout_tau_band_breakout_15m/cache/SOLUSDT__120d__15m.csv`
   
   三个 cache 均从 `2026-03-16 09:00 UTC` 续到 `2026-03-16 09:15 UTC`，只补 1 根新 completed 15m bar，不重拉整段长样本。
2. 基于更新后的共享 cache，重跑：
   - `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. 刷新 Rank 2 相关 artifact / 页面：
   - `reports/artifacts/scout_volume_supportflip_higherlow_15m/{variant_aggregate,asset_summary,trial_meta,cache_meta}.csv`
   - `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`

### 紧邻子点（reader-facing sync）
1. 重跑：
   - `python3 scripts/build_trendline_alpha_scout_report.py`
   - `python3 scripts/build_plans_site.py`
2. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
   - 新增 `2026-03-16 09:26 UTC` 的 Scout Seat 补充；
   - 刷新 `Next 3 bot3 runs` 当前窗口排班，明确：若再无 genuinely new local bar，不要继续在 `Rank 1 / Rank 2` 上做同样本近义续切，应优先看 `Rank 3 continuity`，再退到 `tiny-live plumbing`。
3. 刷新首页索引：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

## 验证 / 证据
执行（最小必要验证）：
1. 通过 Binance API 最小增量抓取最近 15m bar，确认远端已存在 `2026-03-16 09:15 UTC` completed bar；随后仅把 3 个共享 cache 各补 1 行。
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py` ✅
3. `python3 scripts/build_trendline_alpha_scout_report.py` ✅
4. `python3 scripts/build_plans_site.py` ✅
5. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ✅

关键结果（Rank 2 / `combo_all`，`variant_aggregate.csv`）：
- 刷新后跨资产 `mean_total_return` 仍约 `+2.33%`
- `mean_false_break_ratio` 仍约 `6.67%`
- `positive_asset_ratio` 仍为 `2/3`
- `raw_breakout` 仍深负（跨资产 `mean_total_return` 约 `-39.72%`）

换句话说，这根新 bar **没有把 Rank 2 推成更强的新结论**，但也**没有破坏它当前的 keep-narrower 读法**；这正是本轮 honest continuity 的价值：确认它不是靠旧页面停留制造的“假稳定”。

## 本轮 hard verdict
`Rank 2 combo_all` 在共享 cache 续到 `09:15 UTC` 后，结论基本保持不变：它仍是 **值得继续做轻量 forward 复核的 confirmation challenger**，但还不是 `replace-ready / tiny-live ready`。因此当前最诚实的 desk 读法不是升级口径，而是：

**继续保留 Rank 2，但不要在无新 bar 的窗口里重复同样本近义续切。**

## 风险 / 边界
- 本轮只是 **honest light forward refresh**，不是扩样本、不是 live routing、不是 capital cap / kill-switch 真执行验证。
- 新增 bar 数量只有 1 根 completed 15m bar，属于 continuity 检查，不足以单独改变 seat verdict。
- 当前工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件；本轮未做提交，避免混提。

## 下一步建议
1. 若下一轮 `EMA` 仍 `waiting_not_due`，Scout 默认优先检查 `Rank 3 third_touch_plus_ema_macd` 是否出现 genuinely new local bar，可做 honest continuity。
2. 若 `Rank 3` 也没有 genuinely new bar，默认切到 `tiny-live plumbing`，沿 `operator reconciliation sequence` 再补一格，而不是继续在 `Rank 1 / Rank 2` 上做同样本近义续切。
3. `breakout` 继续按 `bench / recheck-only` 处理；没有 genuinely new blocker reduction 前，不应重开 heavy rerun。

## 网站可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页索引：`https://jp.jerrypsy.top/momentum/`

## Commit hash（基线）
- `573439c`

## 如果未提交，原因
当前 repo 存在大量与本轮无关的历史脏文件与未跟踪产物；为避免混提，本轮只做 selective artifact / 页面刷新，不打包提交。
