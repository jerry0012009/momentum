# Rank 40 clean replication：三 EMA 回调模板如实压回 park

- 时间：2026-03-18 03:14 UTC
- 轮次：bot3 auto optimization / Trading Desk / Run 2 / Scout Seat
- 当前 seat 状态：`Paper Seat / EMA = running paper / waiting_not_due`
- 本轮主点：执行 `Rank 40 / EMA pullback / three-EMA trend continuation` 的那 **1 次最小 clean replication**，给出 hard verdict
- 紧邻子点：把 hard verdict 回写到 `docs/TODO.md`，并落 reader-facing 因子页

## 1. 为什么这轮选这个
先读了 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。

当前 desk 读法：
- `Run 1 / EMA` 仍是 `waiting_not_due`，这轮不能继续在 paper refresh 上空转；
- `Rank 17 / Rank 2 / Rank 29 / Rank 32b` 都已是 `P3 narrow paper lane`，当前没有新的真实 `append/review` 状态变化；
- `Rank 43` 刚在上一轮完成 clean replication 并压回 `park / evidence pool`，不该继续磨；
- `Rank 40` 则是当前 active Scout 候选里边际价值最高的一条，因为它上一轮已经被明确写成：**下一轮默认先给 1 次最小 clean replication**。

所以这轮严格按 `Run 2 / Scout Seat` 执行，不新开多候选，只把 `Rank 40` 从 `admit_to_clean_replication_queue` 推到明确 verdict。

## 2. 做了什么
运行：

```bash
python3 /root/clawd/jerry/momentum/scripts/build_rank40_ema_pullback_clean_replication.py
```

这次冻结的 clean-room 口径：
- 资产：`BTC/ETH/SOL 120d 15m`
- 执行：`signal bar close -> next-bar open -> no-overlap`
- 风险管理：`pullback swing stop + 2.06R target`
- 仅比较 3 组邻近参数：
  - `ema20_100_200`
  - `ema33_165_365`
  - `ema40_200_440`
- 不追新 bar，不扩成完整 stability pack

同时脚本自动完成：
- 写出 `reports/artifacts/scout_rank40_ema_pullback_15m/`
- 生成 reader-facing 页面 `reports/site/factors/scout_rank40_ema_pullback_15m/report.html`
- 将 `docs/TODO.md` 中的 `Rank 40` authoritative 状态从 `admit_to_clean_replication_queue` 回写成最新 hard verdict

## 3. 核心证据
### 主变体（脚本 primary）
- `ema33_165_365 @ 6bps/side`
- 跨资产 `mean_total_return≈-13.32%`
- `positive_asset_ratio≈0/3`
- `mean_trades≈59.0`
- `mean_no_trade_ratio≈83.79%`

### 邻近参数对照
- `ema20_100_200 @ 6bps/side`：`mean_total_return≈-0.19%`，`positive_asset_ratio≈1/3`
- `ema40_200_440 @ 6bps/side`：`mean_total_return≈-8.51%`，`positive_asset_ratio≈1/3`

### time-pocket honesty（主变体 6bps）
- `bucket_1≈-11.47% / positive_asset_ratio≈0.00%`
- `bucket_2≈+6.64% / positive_asset_ratio≈66.67%`
- `bucket_3≈-8.00% / positive_asset_ratio≈33.33%`

更直白地说：
- 这条线不是“完全没出现过正 pocket”；
- 但 pocket 既不够稳，也没通过跨资产和时间切片的最小诚实门；
- 继续给它预算，更像是在替 intake 文案续命，而不是减少真实 gate。

## 4. hard verdict
**`Rank 40 / EMA pullback / three-EMA trend continuation` → `park / evidence pool`**

原因：
- 成本后主证据没有站住；
- 主变体跨资产为 `0/3` 正；
- time-pocket 只有中间桶为正，前后两桶都不诚实；
- 交易数不算稀到没法看，但也没强到足以覆盖上述稳定性问题。

因此这轮最诚实的动作，不是把它抬成 `P1`，而是**直接压回 `park / evidence pool`**。

## 5. 本轮产物
### deployable / reader-facing artifacts
1. `reports/artifacts/scout_rank40_ema_pullback_15m/clean_room_spec.csv`
2. `reports/artifacts/scout_rank40_ema_pullback_15m/overall_summary.csv`
3. `reports/artifacts/scout_rank40_ema_pullback_15m/asset_summary.csv`
4. `reports/artifacts/scout_rank40_ema_pullback_15m/time_bucket_summary.csv`
5. `reports/artifacts/scout_rank40_ema_pullback_15m/all_trades.csv`
6. `reports/artifacts/scout_rank40_ema_pullback_15m/trades_primary_6bps.csv`
7. `reports/site/factors/scout_rank40_ema_pullback_15m/report.html`

### board / write-back
8. `docs/TODO.md`
   - `Rank 40` 已从 `admit_to_clean_replication_queue` 改写为 `park / evidence pool`
   - 顶部 `Next 3 bot3 runs` 补入 `2026-03-18 03:14 UTC` authoritative note

## 6. 验证 / 证据
- 脚本成功退出：`rank40 clean replication done: park / evidence pool`
- 读取 `overall_summary.csv`、`time_bucket_summary.csv`，数值与页面一致
- 读取 `reports/site/factors/scout_rank40_ema_pullback_15m/report.html`，确认 reader-facing 页面已生成
- 读取 `docs/TODO.md`，确认 `Rank 40` 和顶板最新补充已同步写回

额外说明：
- 运行中只出现 pandas `FutureWarning`（`groupby(... observed=...)` 默认值未来会变），不影响这轮 verdict

## 7. 风险 / 边界
- 这轮只做了最小 clean replication，不是完整 `Light Stability Pack`
- 但按当前 desk 规则，这已经足够回答“值不值得继续给预算”
- 由于 verdict 已经是 `park / evidence pool`，默认不应再继续给这条线做 cheap recheck

## 8. 下一步建议
若下一轮 `EMA` 仍是 `waiting_not_due`，默认顺序应是：
1. 先比较是否还有新的合格 `paper / repo based 5m / 15m crypto` source 可做 **fresh intake**；
2. 若 fresh intake 这轮也拿不到合格对象，再诚实回退到 `Run 3 / tiny-live plumbing`；
3. 默认不要继续围着 `Rank 40 / Rank 43` 这两条已 `park` 线打磨近义说明页。

## 9. commit / 邮件
- commit：未提交
- 原因：repo 当前存在大量与本轮无关的既有脏文件 / 未跟踪产物，安全 selective commit 成本过高，避免混提
- 邮件：本轮完成后按要求发送中文摘要
- 当前 commit hash：`5331292`
