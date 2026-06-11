# Rank 202 survivor follow-up — public feed复验后不升 P2，退回 Background pool

- 时间：2026-03-27 22:24 UTC
- 对象：`Rank 202 / 1s book horizon sweep microstructure drift`
- 来源：`research/optimization_loop/2026-03-27_2028_rank202_1s_book_horizon_sweep_intake_keep_p1.md`
- 本轮动作：用掉 survivor 唯一 follow-up；按 state 指定只做公共 feed 最小复验、long/short 对称版与 `3m/5m/15m` horizon × cost 生存表，回答这条母线是否值得升 `P2`
- 本轮结论：`drop_to_background`

## 本轮新增 artifact
- 脚本：`scripts/build_rank202_public_feed_followup.py`
- 输出目录：`reports/artifacts/rank202_public_feed_followup_20260327/`
- 关键文件：
  - `feature_frame_1s.csv`
  - `summary.csv`
  - `best_by_side.csv`
  - `predictions.csv`
  - `meta.json`

数据口径：
- 交易所：Binance USDⓈ-M Futures 公共日包
- 标的：`BTCUSDT`
- 日期：`2024-01-15`
- 输入：`bookTicker + aggTrades`
- 频率：聚合到 `1s`
- 特征：`microprice_dev`、`depth_imbalance`、`flow_imbalance`、`trade_count_z`、`ret_1s`、`spread_bps`
- 训练/验证：前半天拟合线性 proxy，后半天 OOS 测试
- 对称执行：`pred >= q90` 做多，`pred <= q10` 做空，同时输出 `long / short / combined`
- horizon：`180s / 300s / 900s`
- 成本：`2 / 4 / 8 / 12 / 20 bps round-trip`

## 核心发现
这轮最关键的收口，不是“repo 说 15m/30m 还行”，而是：

> **一旦换成公共 feed 的最小可复验骨架，并且把 short 侧也补上，`3m/5m/15m` 的 gross edge 只剩 `0.15~0.46 bps/event`，远不足以支撑任何合理成本档，因此不值得升入 `P2`。**

### 1) 对称版补完后，short 并没有把这条线救活
`summary.csv` 显示：

- `180s long`: `+0.366 bps/event`
- `180s short`: `+0.348 bps/event`
- `300s long`: `+0.270 bps/event`
- `300s short`: `+0.284 bps/event`
- `900s long`: `+0.154 bps/event`
- `900s short`: `+0.456 bps/event`

也就是说，short 侧确实不像 repo 那样被完全浪费；但它补出来的也只是 **sub-0.5 bps/event** 量级的毛边，不是能把对象推进到前排 admission 的 decisive 证据。

### 2) horizon 拉长后也没有出现可交易 pocket
如果这条线值得升 `P2`，至少应该出现一种比较像样的形态：
- `3m -> 5m -> 15m` gross 随 horizon 拉长明显抬升；或
- 某一侧（long/short）在 `4bps` 左右成本下至少接近 break-even；或
- 对称合并后形成更厚的 combined pocket。

但本轮看到的是：
- `combined 180s = +0.357 bps/event`
- `combined 300s = +0.277 bps/event`
- `combined 900s = +0.305 bps/event`

horizon 并没有把 edge 推到更厚，反而是整体维持在很薄的噪音边缘。

### 3) 成本生存表直接把 survivor 收口
所有口径在最轻的 `2bps rt` 下都已经转负：

- 最好的一档是 `900s short`，也只有 `gross +0.456 bps/event`，对应：
  - `net_2bps_rt = -1.544`
  - `net_4bps_rt = -3.544`
  - `net_8bps_rt = -7.544`

其余组合更弱。换句话说：

> **这条线当前留下的是“能测到一点微结构方向信息”，不是“已经形成值得 bot2/bot3 前排继续 admission 的 desk 级 raw alpha”。**

## 为什么本轮必须直接 drop_to_background
上一轮 survivor follow-up 问的不是抽象的“有没有 edge 影子”，而是很具体的：

> 用公共 feed 最小复验 + long/short 对称版 + horizon/cost 生存表后，这条 `1s 微结构压力 -> 3m~15m 方向漂移` 母线，是否已经值得升 `P2`？

本轮答案已经足够清楚：**不值得。**

- 公共 feed 骨架已经补上；
- short 侧也补上了；
- horizon × cost 生存表也补上了；
- 但所有 pocket 都停留在 `sub-0.5 bps/event gross`；
- 连 `2bps rt` 这种极轻成本都完全穿不过。

因此这不是“再补一点稳定性”的问题，而是 **survivor 预算已经把唯一 decisive blocker 回答完：可交易厚度不成立。**

## runtime 一句话
`Rank 202 / 1s book horizon sweep microstructure drift` 的 survivor 唯一 follow-up 已完成：公共 `bookTicker + aggTrades` 最小复验下，补完 long/short 对称版后的 `3m/5m/15m` gross 仅剩 `0.15~0.46 bps/event`，所有 `2~20 bps` round-trip 成本档均为负，因此这条线不升 `P2`，本轮直接 `drop_to_background`。
