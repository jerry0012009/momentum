# Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day — intake keep P1

- 时间：2026-03-30 10:33 UTC
- 轮次动作：`cycle_plan` 第 2 项（fresh intake）
- 对象：`intraday hour-pair momentum / reversal within pseudo trading day`
- 结论：`keep_P1`
- 新分配 Rank：`251`

## 本轮只回答什么
只回答这条最新论文 alpha 是否形成独立前排对象，主语严格锁定为：

`同一 pseudo trading day 内 earlier hour return -> later hour return 的 hour-pair continuation / reversal pocket`

不把它偷换成泛 intraday seasonality、generic clock family，或已有的固定单时钟 continuation / reversal。

## intake 结论
`Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day` 值得作为新的独立对象进入前排并给 `keep_P1`：它的最小新意不是“某个 UTC 小时做顺势或反转”，而是把 24/7 crypto 先切成 `pseudo trading day`，再在**同一伪交易日内部**寻找 `earlier hour -> later hour` 的稳定映射，而且允许 `continuation` 与 `reversal` 在不同 `hour-pair` 上同时共存；这比现有 `clock-conditioned mode switch`、`weekday-hour weak schedule`、`open-impulse/pre-close reversal` 更像一套 `hour-pair mining framework`，对象边界独立，且从论文描述到 `BTCUSDT perp × 1h predictor -> 15m/5m execution` 的最小 honest 骨架已经足够清楚。

## 为什么不是旧对象换壳
### 1) 不是 `clock-conditioned mode switch`
已有时钟类近邻更像：
- 固定 `UTC hour` 口袋里，同一 own-past return 要做顺势还是反转；
- 或固定 `weekday × hour` 的稀疏弱时段 schedule；
- 或开段/尾段这种预先写死的双时钟结构。

而这条线的主语是：
- 先定义 `pseudo trading day` 锚点（如 `UTC 00/08/16`）；
- 再在同一伪交易日里枚举 `(predictor_hour i, target_hour j)`；
- 允许不同 pair 分别落在 continuation / reversal；
- 后续 execution 只是在目标小时内下沉到 `15m/5m`。

这不是“某个固定时钟口袋该顺势还是反着做”的同义改写，而是更上层的 `hour-pair mapping` 对象。

### 2) 不是只把 session/open alpha 换个标题
`Rank 250` 锁的是 `pseudo-session 开头 30m dominant leader 自身继续领跑`；
这条新对象不要求 open leader、不要求 cross-section dominant leader，也不把对象锁死在 session opening 30m，而是同一 pseudo-day 内任意 earlier hour 与 later hour 的方向映射。

### 3) 不是单纯 paper wording
该 digest 已把最小实验翻成可执行骨架：
- 先用分钟线聚成 `1h` predictor；
- 默认先测 `UTC 00:00`，再比较 `UTC 08:00/13:00/16:00` 锚点；
- 对 `(i,j)` 做 rolling 训练 / OOS 测试；
- 仅保留符号稳定且目标小时波动能覆盖成本的 pair；
- 执行层转到 `15m/5m`。

所以它不是只有 paper 叙事，没有 desk 化落点。

## 为什么当前只给 keep_P1，不直接升 P2
当前仍缺 1 个便宜但 decisive 的 follow-up：
- 必须先确认这条 `pseudo-day hour-pair` 框架在最近样本里，是否真的能留下**少数稳定 pair**，而不是 24×24 网格挖矿产生的 look-good pockets；
- 还要先看 pseudo-day 锚点（`UTC 00/08/16`）是否只是参数自由度，而不是对象本身的稳健结构。

所以本轮最诚实的层级是：
- **承认对象边界独立，进入前排；**
- **但先停在 `keep_P1`，把唯一 survivor follow-up 留给 rolling / OOS + anchor sensitivity 的 cheap decisive check。**

## 下一轮唯一合法 survivor follow-up 应该问什么
只问一个问题：

> 在 `BTCUSDT perp` 上，把 pseudo-day 锚点限制在 `UTC 00/08/16`，并用 rolling train / OOS test 审查后，是否仍能留下少数对 `15m` 执行成本后有边的稳定 `hour-pair continuation / reversal` pockets？

若答案是肯定的，可升 `P2`；若只剩漂移 pair 或锚点一挪就失真，则按 policy 收口回 background。

## 本轮结果句
`Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day` 完成 fresh intake first verdict：它不是旧时钟效应换壳，而是以 `pseudo trading day × earlier-hour -> later-hour` 映射为核心的独立 `hour-pair mining` 对象；最小 honest 策略骨架已清楚，因此本轮给 `keep_P1`，进入唯一 survivor follow-up。
