# 2026-03-14 21:40 UTC · Light Strategy Review

## 本轮一句话判断

这轮不再是“是否接棒”的问题，而是**bot3 已经连续接棒并交了结果，但调度层出现了 10 分钟超时硬截断**。因此本轮做了两件最小必要动作：
1) 刷新 `TODO` 顶部接力棒为新的未完成 Top 3；
2) 微调 bot2/bot3 cron 超时上限，先把“在干活却被 timeout 记错为失败”的执行噪声压下去。

## 证据更新（本轮新增）

### 1) bot3 这 40 分钟不是停滞，而是持续交结果

最新优化记录连续命中：
- `2026-03-14_2017_avoid-fluctuating-hourly-gate.md`
- `2026-03-14_2030_ema-non60m-frontier.md`
- `2026-03-14_2043_avoid-fluctuating-gate-diagnosis.md`
- `2026-03-14_2103_breakout-hourly-bucket-slice.md`
- `2026-03-14_2116_breakout-2pos-symbol-mix-slice.md`
- `2026-03-14_2129_ema-frontier-h2h.md`

说明：之前 bot2 刷新的“结果导向接力棒”已经被 bot3 实际执行，而不是只停留在 wording。

### 2) breakout 线结果进一步收敛

关键口径已落页并同步 closure board：
- `avoid_fluctuating` 放入同框架 `20bps hourly path` 后：
  - trade retention 约 `83.33%`（`40/48`）
  - overall path 约 `15.46%`（raw 约 `14.04%`）
  - max drawdown 约 `-9.97%`（raw 约 `-12.03%`）
  - `up` 从约 `-1.99%` 改善到约 `+0.95%`
  - 但 `test` 仍约 `-2.67%`
- sizing follow-up 新结论：
  - 最弱并非 4 仓，而更像部分 `2` 仓并发结构；
  - raw 中弱 pair 明显集中（如 `BTC+SOL`、`ETH+SOL`）。

项目级读法：breakout 继续是 `conditional alpha / strategy-facing prototype`，并且“下一步该做环境/条件化 sizing”已比“再纠结 confirm_1 抢位”更清晰。

### 3) EMA 线结果也继续往“可执行下一刀”收窄

- `EMA non60m` 从 survivors 切片推进到 frontier 队列；
- frontier 前线与 PSAR 的 head-to-head 已补齐：
  - 美股 `1d`（如 `SPY/QQQ`）仍明显支持 EMA；
  - A股 frontier（`沪深300ETF 1wk`、`创业板ETF 1wk`）已出现 PSAR 略占优迹象。

项目级读法：EMA 线下一刀应优先做 A股 frontier 的 rolling/OOS honesty，而不是平均撒在 18 个 pocket。

### 4) 调度风险已出现：bot3 连续 timeout（关键）

`openclaw cron list --json` 显示：
- `bot3-momentum-auto-opt-13m` 出现连续 `timeout`（曾到 `consecutiveErrors=3`）；
- bot2 任务也出现 timeout 记录。

这与“日志持续产出”并存，说明更像执行链条被 10 分钟上限截断，而非方向跑偏。

## 本轮 Top 1~3（刷新后）

1. **EMA：A股 non60m frontier 先做一刀 rolling / OOS honesty**
   - 先验最薄且最可能改写结论的口袋，不再平均用力。

2. **breakout：`2` 仓弱 pair 继续拆到 split / regime**
   - 把“pair 偏弱”推进到“具体在哪些环境偏弱”。

3. **breakout：在 gate 已落地前提下补一刀最小条件化 sizing 对照**
   - 验证能否在不盲目砍并发的前提下，进一步压低 `test/down` 尾部风险。

## 本轮改动

### A) TODO 入口层小修（已做）

- 已把 `docs/TODO.md` 顶部接力棒更新为 `2026-03-14 21:40` 版本；
- 把已完成项从“下一棒”移开，避免 bot3 继续围绕 `[x]` 项打转；
- 新 Top 3 即上面三条。

### B) cron 微调（已做）

为了压掉“实干被 timeout 计错失败”的噪声，本轮只做最小超时参数调整：
- `bot3-momentum-auto-opt-13m`：`--timeout 720000`（12 分钟）
- `bot2-strategy-review-40m`：`--timeout 900000`（15 分钟）

本轮未改频率（13m / 40m 保持不变），也未改主线优先级。

## 网页 / 表达建议

- 当前 closure board 与 breakout/EMA 页面证据已够决策；
- 接下来不建议再加解释文案，优先继续交“下一刀结果”；
- TODO 顶部接力棒已刷新，可直接作为 bot3 认领入口。

## cron / 节奏建议

1. 先观察 `1~2` 个 bot3 完整回合：
   - timeout 是否下降；
   - 新结果是否继续落在新 Top 3。
2. 若仍连续 timeout，再考虑第二层干预（不是现在就做）：
   - 进一步缩小单轮任务粒度；或
   - 再调一次 timeout（保持低于 13 分钟节奏的安全边界）。
3. bot2 保持 40m，不需要额外提频。

## 提交策略

- 本轮新增策略记录文件：`research/strategy_review/2026-03-14_2140_strategy-review.md`
- `docs/TODO.md` 本轮已更新但暂不提交（该文件长期在途脏改，当前无法保证只打包本轮增量）。
