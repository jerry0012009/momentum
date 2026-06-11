# Rank 40 EMA pullback clean replication → park
- 时间：2026-03-17 18:27 UTC
- 轮次：bot3 momentum auto optimization loop
- 席位：Scout Seat
- 主点：`Rank 40 / EMA pullback / three-EMA trend continuation`
- 紧邻子点：authoritative board write-back（`docs/TODO.md`）

## 0. 开场检查
- `Paper Seat / EMA` 仍处于 `waiting_not_due`，没有新的 `due-now / overdue` paper refresh need。
- `Live Seat` 仍为空；没有 bot2 新点名的 promoted candidate。
- 当前 `TRADING DESK BOARD` 的 `Next 3 bot3 runs` 已把 `Rank 40` 指定为当前最该消耗的那 **1 次最小 clean replication**。
- repo 工作区存在大量**与本轮无关**的历史脏文件 / 未跟踪产物，因此本轮只做 selective 产出与 write-back，不混提其他改动。

## 1. 为什么本轮还是落到 Rank 40
按当前 board 的 authoritative 顺序：
1. `Run 1 / Paper Seat` 没有 due-now 动作，不能在 waiting-window 空转；
2. `Run 2 / Scout Fast Lane` 里，上一轮刚把 `Rank 40` 从 source intake 提升到 `admit_to_clean_replication_queue`；
3. 本轮只允许继续消耗它那 **1 次最小 clean replication**，而不是同时再开别的 scout 候选。

因此这轮主资源只给 `Rank 40`，不扩写新大框架，也不回头磨 P3 continuity 文档。

## 2. 本轮固定的 clean-room 口径
本轮严格按最小预算冻结为：
- 样本：`BTC/ETH/SOL 120d 15m` 本地 cache
- 执行：`signal bar close -> next-bar open -> no-overlap`
- 规则：
  - `EMA fast` 与 `EMA trend` 同向；
  - 价格先回抽穿越 `EMA fast`；
  - 回抽极值若深穿 `EMA limit` 则判 fail；
  - 回到 `EMA fast` 正确一侧时触发；
  - `short` 侧镜像。
- 风控：保留 source 原意的 `pullback swing stop + 2.06R target`
- 风险带：保留 source 默认 `0.8% ~ 2.0%` 风险窗口
- 参数预算：只比较 3 组极小邻近参数：
  - `20/100/200`
  - `33/165/365`（主变体）
  - `40/200/440`
- 不做的事：
  - 不追最新 bar
  - 不做大网格搜参
  - 不扩成完整 `Light Stability Pack`
  - 不补 admission / operator packet 类文档

## 3. 产物
### 3.1 新脚本
- `scripts/build_rank40_ema_pullback_clean_replication.py`

### 3.2 新 artifact
- `reports/artifacts/scout_rank40_ema_pullback_15m/clean_room_spec.csv`
- `reports/artifacts/scout_rank40_ema_pullback_15m/overall_summary.csv`
- `reports/artifacts/scout_rank40_ema_pullback_15m/asset_summary.csv`
- `reports/artifacts/scout_rank40_ema_pullback_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank40_ema_pullback_15m/all_trades.csv`
- `reports/artifacts/scout_rank40_ema_pullback_15m/trades_primary_6bps.csv`

### 3.3 网页落点
- `reports/site/factors/scout_rank40_ema_pullback_15m/report.html`

### 3.4 authoritative write-back
- `docs/TODO.md`
  - `Rank 40` 条目已从 `admit_to_clean_replication_queue` 写回为 `park / evidence pool`
  - `Next 3 bot3 runs` 已追加 18:25 UTC 的 authoritative supplement

## 4. 硬结果
### 4.1 主变体（`ema33_165_365`）
在 `6bps/side` 下跨资产：
- `mean_total_return ≈ -13.32%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 59.0`
- `mean_signals_seen ≈ 365.3`
- `mean_no_trade_ratio ≈ 83.79%`

### 4.2 时间口袋诚实性（主变体 / 6bps）
- `bucket_1 ≈ -11.47% / positive_asset_ratio=0/3`
- `bucket_2 ≈ +6.64% / positive_asset_ratio=2/3`
- `bucket_3 ≈ -8.00% / positive_asset_ratio=1/3`

### 4.3 邻近参数也没救回来
- `20/100/200 @ 6bps`：`mean_total_return ≈ -0.19%`，虽然比主变体少亏，但仍只有 `positive_asset_ratio=1/3`
- `40/200/440 @ 6bps`：`mean_total_return ≈ -8.51%`，`positive_asset_ratio=1/3`
- 成本上升到 `10/15/20bps` 后三组参数整体继续恶化，没有出现“只是主参数选错了”的干净救援信号。

## 5. Hard verdict
**`park / evidence pool`**

更直白地说：
- 这条线已经不再只是 `admit_to_clean_replication_queue`；
- 它的最小 clean replication 已经给出足够明确的否定：主变体成本后显著转负、跨资产 `0/3` 为正，而且 `time-pocket honesty` 只剩中间一段勉强为正；
- 因此它不配继续拿默认 Scout 预算，也不进入 `paper candidate pool`。

## 6. 对交易台排班的影响
- `EMA = waiting_not_due` 的前提没变；
- 但 `Rank 40` 这条 scout 线现在也已经完成其唯一允许动作并压回 `park`；
- 所以下一轮若仍处于 `Run 2 / Scout Fast Lane`，默认应先重新比较是否还有新的合格 `paper / repo based 5m / 15m crypto` source 可做 `fresh intake`；
- **只有在这一轮也拿不到合格 source 时，才诚实回退到 `Run 3 / tiny-live plumbing`。**

## 7. 验证 / 执行记录
- 运行：`python3 scripts/build_rank40_ema_pullback_clean_replication.py`
- 结果：成功，退出码 `0`
- 备注：出现 1 条 pandas `FutureWarning (groupby observed)`，不影响本轮结论。

## 8. 本轮没有做的事
- 没有再碰 `Rank 17 / Rank 2 / Rank 29` 的 P3 continuity
- 没有扩成 `Light Stability Pack`
- 没有处理与本轮无关的大量脏文件
- 没有提交 commit

## 9. 下一手建议
默认下一轮继续按 board：
1. 先看 `Run 1` 是否出现真实 `EMA due-now / overdue`；
2. 若仍 `waiting_not_due`，则在 `Run 2` 里优先重新做 **fresh source intake**；
3. 若 fresh source 也暂时拿不到，才回退 `Run 3 / tiny-live plumbing`。
