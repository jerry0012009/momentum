# 2026-03-18 04:40 UTC — FibTrend-Pro 最小 clean replication 后压回 park

## 本轮为什么选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 后，`Run 1 / EMA` 当前仍是 `running paper / waiting_not_due`：A 股下一次 close 仍在 `2026-03-18 07:00 UTC`，美股在 `2026-03-18 20:00 UTC`，crypto 在 `2026-03-19 00:00 UTC`。
- 当前 `P3` 的 `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 继续由专属 refresh / monitoring 托管，没有新的 `append/review` 状态变化。
- 按顶板默认顺序，上一轮 `FibTrend-Pro` 已完成两条轻量诚实守门，因此这轮唯一允许、也最高边际价值的主点就是它的 **1 次最小 clean replication**；不该回头磨 `P3 continuity`，也不该直接跳去 `Rank 35b`。

## 本轮主点
- **主点**：`FibTrend-Pro / Fib 0.618 reclaim + volume/trend gate` 的唯一那手最小 clean replication
- **紧邻子点**：把 hard verdict 写回 `docs/TODO.md`，并产出 reader-facing report

## 这轮怎么冻结执行口径
为了避免把 TradingView 的 bar-close 判断和同 bar 乐观成交混在一起，这轮故意只做 clean-room 版本：
- 样本：`BTC / ETH / SOL` 本地 Binance `120d 15m` cache
- 执行：`signal close -> next-bar open -> no-overlap`
- 退出：`close < Fib 0.5` 直接判定 setup fail；否则最多持有 `8` 根 bar
- 成本：`6 / 10 / 15 / 20 bps per side`
- 四臂对照：
  1. `fib_touch_raw`
  2. `+volume_gate`
  3. `+trend_gate_shared`
  4. `+ema_confirm(ATR variant)`（主臂）

## 做了什么改动
1. 新增脚本：
   - `scripts/build_repo_fibtrend_clean_replication.py`
2. 生成 artifact：
   - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/clean_room_spec.csv`
   - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/asset_summary.csv`
   - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/overall_summary.csv`
   - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/time_stability.csv`
   - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/cost_trade_stability.csv`
   - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/all_trades.csv`
3. 生成 reader-facing 页面：
   - `reports/site/factors/scout_repo_fibtrend_confirmation_15m/report.html`
4. 将 hard verdict 写回 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
5. 重建 / 发布：
   - `python3 scripts/build_todo_page.py`
   - `bash scripts/publish_homepage_index.sh`

## 硬结果
### 6bps/side 主结果
- `fib_touch_raw`
  - `mean_total_return≈-33.02%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈321.3`
  - `mean_false_retest_rate≈49.09%`
- `+volume_gate`
  - `mean_total_return≈-18.86%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈168.0`
  - `mean_false_retest_rate≈50.83%`
- `+trend_gate_shared`
  - `mean_total_return≈-4.54%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈98.0`
  - `mean_false_retest_rate≈48.19%`
- `+ema_confirm(ATR variant)`
  - `mean_total_return≈-1.14%`
  - `positive_asset_ratio≈33.33%`
  - `mean_trades≈76.0`
  - `mean_false_retest_rate≈47.52%`

### 时间稳定性（主臂 / 6bps）
- `bucket_1 ≈ -0.10% / positive_asset_ratio≈33.33%`
- `bucket_2 ≈ +0.49% / positive_asset_ratio≈66.67%`
- `bucket_3 ≈ -1.58% / positive_asset_ratio≈33.33%`

### 成本斜率（主臂）
- `6bps ≈ -1.14%`
- `10bps ≈ -6.96%`
- `15bps ≈ -13.75%`
- `20bps ≈ -20.05%`

## 这轮的 hard verdict
- **`FibTrend-Pro = park / evidence pool`**
- 更直白地说：
  - 它确实比 `fib_touch_raw` 诚实得多，说明 `volume + trend + EMA confirm` 这套过滤层不是完全没用；
  - 但最小 replication 后仍只有 `1/3` 资产为正，且只有中间时间桶勉强转正；
  - 一上到 `10bps/side` 就重新明显转负，因此当前还不配继续占默认 clean-replication 队列预算。

## 对排班的影响
- `FibTrend-Pro` 这条 fresh repo source 已走完整条允许预算：`source intake -> honesty gate -> minimal clean replication -> hard verdict`
- 因此下一轮若 `EMA` 仍是 `waiting_not_due`，更诚实的默认顺序应回退到：
  - `Rank 47 / EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`
- 这也意味着：不应继续在这条线补 admission wording / 近义说明页。

## 验证 / 证据
- `python3 scripts/build_repo_fibtrend_clean_replication.py` 成功跑完，退出码 `0`
- 已确认生成：
  - `reports/site/factors/scout_repo_fibtrend_confirmation_15m/report.html`
  - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/overall_summary.csv`
  - `reports/artifacts/scout_repo_fibtrend_confirmation_15m/time_stability.csv`
- 已确认 `docs/TODO.md` 顶部当前窗口排班改为 `EMA-ADX-VOL skeleton > Rank 35b > Run 3`
- 已执行：
  - `python3 scripts/build_todo_page.py`
  - `bash scripts/publish_homepage_index.sh`

## 风险 / 边界
- 这轮没有把 `FibTrend-Pro` 升格成 `P1/P2`；只是在允许预算内把它走完并如实压回证据池。
- 这套 clean-room 仍是 `15m + 120d cache` 的最小切口，不代表高周期 `4H/1D/1W` 的原作者口径被完整复现。
- 当前 repo 与上级 workspace 仍有大量与本轮无关的脏文件 / 未跟踪文件，因此不做混合提交。

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
