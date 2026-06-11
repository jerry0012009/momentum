# Rank 6 BTC->COIN/MSTR proxy clean replication — 2026-03-17 15:31 UTC

## 本轮 desk 读取
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- `Run 1 / Paper Seat`：EMA 当前无 `due-now / overdue`，仍是 `waiting_not_due`。
- `Run 2 / Scout Seat`：本地 `paper / repo based 5m / 15m crypto` 快筛池本轮已基本耗尽；`Rank 30~35` 已完成当前允许动作并 park，`Rank 17 / Rank 2 / Rank 29` 的 P3 continuity 已交给专属 cron + 状态页托管。
- 因此按 board 允许的回退，给 `Rank 6 / BTC -> COIN / MSTR proxy` 1 次最小 clean replication 预算；不扩成全美股 proxy 宇宙。

## 认领主点
- 主点：`Rank 6 / BTC -> COIN / MSTR proxy` 最小 clean replication
- 紧邻子点：把 hard verdict 写回 `docs/TODO.md` 并产出 reader-facing 网页落点

## 开工前检查
- repo 有大量既有脏文件，绝大多数与本轮无关；本轮不做混提、不做全局整理。
- 最近新增 run 显示上一轮已完成 `Rank 5 / Rank 6 external-data probe`，结论是 `Rank 6` 值得继续、但只允许 `BTC -> COIN / BTC -> MSTR` 两条窄线。

## 本轮动作
1. 新增脚本：`scripts/build_rank6_btc_equity_proxy_clean_replication.py`
2. 固定数据与执行口径：
   - `BTCUSDT 15m`：Binance spot
   - `COIN / MSTR 15m`：Yahoo Finance chart API
   - 只保留 regular-session overlap
   - 信号只用上一根已完成 overlap bar
   - 交易执行固定为下一根 equity bar `open -> close`
3. 只比较三档最小规则：
   - `btc_large_move_follow_proxy`
   - `btc_two_bar_follow_proxy`
   - `btc_proxy_gap_catchup`
4. 输出 artifact / 网页：
   - `reports/artifacts/scout_rank6_btc_equity_proxy_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank6_btc_equity_proxy_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank6_btc_equity_proxy_15m/primary_trades_6bps.csv`
   - `reports/artifacts/scout_rank6_btc_equity_proxy_15m/time_bucket_summary.csv`
   - `reports/site/factors/scout_rank6_btc_equity_proxy_15m/report.html`
5. 将结论写回 `docs/TODO.md`：
   - external-data scout 备选里的 `Rank 6` 更新为“最小 clean replication 已落地”
   - 顶部当前窗口摘要更新为：`Rank 6` 已完成，当前更诚实口径为 `park / evidence pool`

## 结果
### Hard verdict
- `Rank 6 / BTC -> COIN / MSTR proxy` → **`park / evidence pool`**

### 最关键证据
- 6bps/side 下最不差的规则是 `btc_large_move_follow_proxy`
- 跨资产摘要：
  - `btc_large_move_follow_proxy` → `mean_total_return≈2.39% / positive_asset_ratio≈100.00% / mean_trades≈110.0`
  - `btc_two_bar_follow_proxy` → `mean_total_return≈1.89% / positive_asset_ratio≈50.00% / mean_trades≈124.0`
  - `btc_proxy_gap_catchup` → `mean_total_return≈-22.24% / positive_asset_ratio≈0.00% / mean_trades≈153.5`
- 但更诚实的否决点也很直接：
  - `mean_sign_hit_rate` 只在 `50~52%` 左右，边缘很薄；
  - 一旦把成本从 `6bps/side` 提到 `10bps/side`，三档规则全部转负；
  - time-pocket 不是稳定单边正：
    - `COIN` 三桶里只有中间一桶显著为正；
    - `MSTR` 则是中间一桶转负。

## 为什么这轮不继续升格
- 这条线的最小 replication 已经回答了真正会改 verdict 的问题：
  - “BTC 领先一根 15m bar，能不能在 `COIN / MSTR` 上形成足够干净、成本后仍站得住的可交易 edge？”
- 当前答案是：**有一点同步/滞后味道，但不够干净，也不够抗成本**。
- 所以按当前 desk 纪律，更诚实的动作是压回 `park / evidence pool`，而不是继续给它更多默认预算续命。

## 最小验证
- 实际执行：`python3 scripts/build_rank6_btc_equity_proxy_clean_replication.py`
- 脚本成功落地 artifact、网页与 `TODO` 写回。
- 中途遇到 1 次脚本异常：`build_verdict()` 对空 `time_buckets` 直接取 `symbol` 列报错；已当场修复后重跑成功。

## 对下一轮 desk 的含义
- `EMA = waiting_not_due` 仍成立。
- `Rank 6` 这条 external-data fallback 已用掉本轮允许预算，且结论已回到 `park / evidence pool`。
- 若没有新的本地 `paper / repo based 5m / 15m crypto` source 补进来，下一优先动作应转向 `Run 3 / tiny-live plumbing fallback`，而不是继续磨同一条 external-data 线。
