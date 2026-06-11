# 2026-03-16 11:01 UTC｜Scout Rank 3 continuity refresh：共享 15m cache 诚实续到 10:45 completed bar 后复核 third-touch 窄门守卫

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- **Run 1 / Paper Seat**：`EMA` 仍处于 `running paper / waiting_not_due`，当前没有新的 `due-now / overdue` lane。
- **Run 2 / Scout Seat**：上一轮已明确写下，若共享 Binance `15m` cache 出现新的 completed bar，就优先继续 `Rank 3 third_touch_plus_ema_macd` 的 honest continuity。
- 当前实测三个币种共享 cache 都可诚实续到 `2026-03-16 10:45 UTC` completed bar，因此这轮前提成立，合规继续做一刀 `Run 2`；没有回退到 `Run 3 / tiny-live plumbing`。

## 本轮只认领的事项
- **主点**：把共享 Binance `15m` cache 最小增量续写到 `10:45 UTC` completed bar，并对 `Rank 3 third_touch_plus_ema_macd` 做一次 honest continuity refresh。
- **紧邻子点**：把本轮回执同步回 `docs/TODO.md` 顶部 `Scout Seat / Next 3 bot3 runs`，避免下一轮在没有新 bar 时重复同样本 continuity。

## 本轮做了什么
### 1）对共享 Binance 15m cache 做最小增量续写，并剔除未完成 bar
直接复用 `reports/artifacts/scout_tau_band_breakout_15m/cache/*.csv`，只追加当前已完成的新 bar：

- `BTCUSDT` 最新 completed bar：`2026-03-16 10:45 UTC`
- `ETHUSDT` 最新 completed bar：`2026-03-16 10:45 UTC`
- `SOLUSDT` 最新 completed bar：`2026-03-16 10:45 UTC`

因此本轮 `Run 2` 前提成立：
**这次确实有 genuinely new local bar，可合规执行一次 Rank 3 continuity。**

### 2）重跑 Rank 3 continuity
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

### 3）把 desk 回执写回指挥板并刷新站点镜像
更新：
- `docs/TODO.md`
  - `Scout Seat` 最新补充（`2026-03-16 11:01 UTC`）
  - `Next 3 bot3 runs` 最新补充（`2026-03-16 11:01 UTC`）
- `python3 scripts/build_plans_site.py`
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

对应 reader-facing 落点：
- `reports/site/plans/momentum_todo.html`
- `https://jp.jerrypsy.top/momentum/`

## 验证 / 证据
### 最小验证
1. 直接核对共享 cache 末端：三个币种都已诚实续到 `2026-03-16 10:45 UTC` completed bar ✅
2. `python3 scripts/build_third_touch_ema_macd_first_verdict.py` ✅
3. `python3 scripts/build_trendline_alpha_scout_report.py` ✅
4. `python3 scripts/build_plans_site.py` ✅
5. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ✅

### 更新后的 hard verdict
`Rank 3` 最佳版本仍是 `third_touch_plus_ema_macd`：
- 跨资产 `mean_total_return ≈ +0.78%`
- `mean_false_break_ratio = 0.00%`
- `positive_asset_ratio = 1/3`
- `mean_trades ≈ 0.33` 笔 / 资产

成本快检仍保持：
- `10bps`：约 `+0.70%`
- `15bps`：约 `+0.60%`
- `20bps`：约 `+0.50%`

更诚实的读法：

**Rank 3 在新 completed `15m` bar 下继续通过 continuity，没有塌掉；但它仍只是 keep-narrower structure-confirmation challenger，不是 replace-ready / tiny-live ready。**

支持这句话的证据：
- `third_touch_plus_ema_macd` 相比 `raw_breakout` 仍明显更诚实，且新增 completed bar 后结论没有反转；
- 但它仍只有 `1/3` 资产为正收益，交易数仍很稀；
- 因此当前只能维持“可继续轻量 forward 复核的窄门 guard”读法，不能偷升格成可接管 Live Seat 的新主角。

## 风险 / 边界
- 本轮不是新 alpha 主线，也不是 Live Seat replace verdict。
- 本轮只做了基于 genuinely new local bar 的 honest continuity；没有扩成 breakout heavy rerun，也没有重开 EMA 发散。
- 若下一轮之前共享 cache 仍停在 `10:45 UTC` completed bar，就不应继续重跑同样本 Rank 3 continuity，而应回退到 `Run 3 / tiny-live plumbing`。

## 下一步建议
1. 若下一轮前共享 Binance `15m` cache **仍只到 `10:45 UTC` completed bar**，就不要再重跑同样本 Rank 3 continuity；按 desk 规则回退到 `Run 3 / tiny-live plumbing`。
2. 若下一轮前出现新的 completed `15m` bar，再优先核对 `Rank 3` 是否值得继续做 honest continuity。
3. `breakout` 继续按 `bench / recheck-only` 处理；没有 genuinely new blocker reduction 前，不应重新占用默认主资源。

## 网页可见落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`
- 首页：`https://jp.jerrypsy.top/momentum/`

## Commit hash
- HEAD：a9a00d9
- 本轮未提交。

## 如果未提交，原因
当前 worktree 仍有大量与本轮无关的既有脏文件与未跟踪文件；本轮只做 selective cache 续写、Rank 3 continuity 刷新、`TODO/plans` 同步与首页发布，避免混提。
