# 2026-03-20 02:20 UTC — Rank 105 body-defined zone re-entry clean replication → park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `4.7h`）
  - 脚本按 `require-due` guard 退出（code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮合法主动作仍是 `Scout Seat`，且只该拿 **`Rank 105 / body-defined zone re-entry honest failure verdict`** 的那唯一一手最小 clean replication。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1631`
- 最近 optimization logs：
  - `2026-03-20_0202_rank105-body-zone-intake.md`
  - `2026-03-20_0149_rank104-clean-replication-park.md`
  - `2026-03-20_0115_rank104-post-break-signflip-intake.md`
  - `2026-03-20_0054_rank103-clean-replication-park.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前的 `Scout Seat` 顺序为：`Rank 105 / body-defined zone re-entry honest failure verdict > elephant candle corridor long-bias gate > MTF CHOP charged-up count > prebreak higher-low pressure ladder context gate`
- `manual_narrow_paper_last_run_summary.json` 近期无新 closed-trade append，不构成 `P3 continuity` 插队理由。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 105 / body-defined zone re-entry honest failure verdict`**
   - 上轮已完成 `source intake + 两条轻量诚实守门`，当前是唯一合法的 queue-facing 下一手。
   - 它直接回答当前 desk 最缺的那件事：失败判决边界到底要不要继续画在 wick 上。
2. **`elephant candle corridor long-bias gate`**
   - 是最新 fresh repo reserve；但在 `Rank 105` 的 clean replication verdict 没收口前，不该抢本轮主资源。
3. **`MTF CHOP charged-up count` / `prebreak higher-low pressure ladder context gate`**
   - 仍是后置 reserve；当前边际价值低于先把 `Rank 105` 直接定生死。
4. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该抢主资源位。

结论：本轮只认领 `Rank 105` 的最小 clean replication，不并开任何第二条候选。

## 本轮认领
- 主点：`Rank 105 / body-defined zone re-entry honest failure verdict`
- 紧邻子点：把 clean replication artifact、reader-facing 页面、`TODO` 顶板与下一轮顺序一次写齐

## Clean replication 口径（strict queue-facing）
- 数据：`BTC/ETH/SOL Binance Futures 180d 15m`
- parent box：`UTC first-4h box`
  - `wick_high / wick_low = 首个 4h box 的高低点`
  - `body_high / body_low = 首个 4h box 的最高/最低收盘价（accepted body zone）`
- breakout / verdict：
  - 先等 `close` 真正突破 `wick_high / wick_low`
  - 三臂只比较：`wick_verdict`、`body_verdict`、`body_verdict_plus_non_doji`
- 统一执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 4/8 bars`
- 关键 honesty 约束：
  - 不把后续路径倒灌回 verdict candle
  - `body+non_doji` 只多一层 `verdict candle body_ratio >= 0.35`
  - `entry-to-stop` 统一近似为 `breakout extreme -> verdict entry` 的 adverse distance，用来衡量“更诚实是否只是更晚”

## 结果摘要
### overall（重点看 8-bar / 6 bps per side）
- `wick_verdict`
  - `events = 620`
  - `mean_net_ret ≈ -14.07bps`
  - `false_follow ≈ 79.03%`
  - `mean_stop_distance ≈ 51.95bps`
- `body_verdict`
  - `events = 525`
  - `trade_count_retention ≈ 84.68%`
  - `mean_net_ret ≈ -6.75bps`
  - `false_follow ≈ 66.48%`
  - `mean_stop_distance ≈ 68.47bps`
  - `stop_distance_inflation_vs_wick ≈ 1.32x`
- `body_verdict_plus_non_doji`
  - `events = 510`
  - `trade_count_retention ≈ 82.26%`
  - `mean_net_ret ≈ -7.56bps`
  - `false_follow ≈ 64.51%`
  - `mean_stop_distance ≈ 69.45bps`
  - `stop_distance_inflation_vs_wick ≈ 1.34x`

### 怎么读
- `body_verdict` 的确比 `wick_verdict` 更诚实：假延续比例明显下降，且样本保留率没有塌到不可用。
- 但它的改善主要来自**更晚的判决**，不是把 expectancy 真正推过门槛：三臂在 `6bps/side` 下仍全部为负。
- `body+non_doji` 继续压了一点假延续，但没有把收益再抬起来，说明这里已经开始进入“更慢但未更好”的区域。
- 这条线因此更像 **shared failure-verdict boundary evidence**，不像值得继续排默认资源的 queue-facing gate。

## 当前硬结论
**`Rank 105 = park / evidence pool`**。

翻成人话：别再把这条线当默认 Scout 主资源了。`body-defined accepted zone` 确实比 `wick` 更少被骗，但 clean replication 下它仍没跨过成本门槛；这不是 `P2 / paper candidate`，也不值得继续占用下一轮预算。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/event_log.csv`
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/side_summary.csv`
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/symbol_summary.csv`
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/stop_inflation_summary.csv`
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/verdict_summary.csv`
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/summary_snapshot.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/report.html`
  - `reports/site/reading/repo_scout/rank105_body_zone_reentry_honest_failure_verdict_clean_replication.html`
- 可复现脚本：
  - `scripts/build_rank105_body_zone_reentry_clean_replication.py`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 默认从 `Rank 105` 切到 **`elephant candle corridor long-bias gate`**
- 当前 active Scout 顺序应改写为：
  1. `elephant candle corridor long-bias gate`
  2. `MTF CHOP charged-up count`
  3. `prebreak higher-low pressure ladder context gate`
  4. `Rank 105 / Rank 104 / Rank 103 / Rank 102 / Rank 101 / Rank 100 / Rank 99 / Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 94 / Rank 92 / regression-channel-width`（`P0 park / evidence pool`）
  5. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used`）
  6. `P3 continuity sidecar`
  7. `tiny-live plumbing`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 elephant candle corridor long-bias gate 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 elephant candle corridor long-bias gate guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 MTF CHOP charged-up count；只有 fresh source 也 exhausted，才允许继续回退到 prebreak ladder > 旧 evidence_pool > P3 continuity > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前仍是 `waiting_not_due`
- `python3 scripts/build_rank105_body_zone_reentry_clean_replication.py`
  - 成功生成 rank105 clean replication artifact 与 reader-facing 页面
- 回读以下文件，确认已写入成功：
  - `reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/verdict_summary.csv`
  - `reports/site/factors/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/report.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 `elephant candle corridor`、`MTF CHOP` 或任何 `P3 continuity`
- 本轮没有整理或覆盖无关脏文件
- 工作区仍有大量历史脏文件；本轮只做 selective write-back
