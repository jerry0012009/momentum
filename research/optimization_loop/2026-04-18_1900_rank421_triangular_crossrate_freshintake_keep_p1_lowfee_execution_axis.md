# Rank 421 / triangular cross-rate inconsistency fresh intake -> keep_P1

- 时间：2026-04-18 19:00 UTC
- 对象：`同所同步报价 cross-rate inconsistency`（source: `research/quant_digests/2026-04-18_1048_triangular-crossrate-loop-alpha.md`）
- 本轮动作：fresh intake 最小首判
- 结论：`keep_P1`
- Rank：`421`

## 本轮要回答的唯一问题
公开 top-of-book 下可见的 `positive gross`，在真实 fee / depth / latency 之后，是否还能留下独立可交易 pocket；还是已经退化成只适合做 quote-health / stale-quote 指标。

## 已有最关键证据
digest 已经把 repo 的 `last-price` 探测改成更严格的 Binance Spot `bookTicker` 三腿闭环复算，并给出最小现实口径：

- `fee=0 bps/leg`：`90/90` 样本可找到正 gross，median 约 `+1.50bps`，best 约 `+4.68bps`
- `fee=4 bps/leg`：`0/90` 为正
- `fee=10 bps/leg`：`0/90` 为正
- 最常见 best cycle：`USDT -> ETH -> USDC -> USDT`

这说明：
1. base alpha 不是伪命题，`cross-rate inconsistency` 在公开同步报价中稳定可见；
2. 当前 front-door blocker 不是“是否存在 alpha”，而是非常收敛的 `low-fee + depth-aware execution realism` 单轴问题；
3. 它还没有退化成纯粹 quote-health 指标，因为公开数据已经证明 gross pocket 持续存在，且对象本身是可独立定义的 closed-loop RV alpha。

## 为什么这轮不直接打回 background/P0
按当前 cycle item 的 success criterion，只有当对象在现实口径下已更像 quote-health / stale-quote 指标、没有独立可交易主体时，才应直接 `background/P0`。

但本题当前不是这个状态：
- 信号定义非常干净：`net loop product > fees + slippage + latency buffer`
- repo / public-data probe 已经证明 `gross` 端稳定存在，不是单次 snapshot 幻觉
- 失败点高度集中在 execution side：费率层级、三腿深度、排队/时延、残腿兜底

因此，当前最诚实的首判不是“这题不存在”，而是：**它值得保留成 1 个 P1 front object，只允许再做 1 次 survivor follow-up，去回答唯一剩余 blocker——低费/深度感知执行下是否还能留下 after-cost pocket。**

## 本轮 verdict
`Rank 421`：`同所同步报价 cross-rate inconsistency` fresh intake 首判完成；公开 BBO 已证明三腿闭环 gross pocket 稳定存在，但现实 verdict 目前被单一 `low-fee/depth-aware execution realism` 轴卡住，尚未退化为纯 quote-health 指标，因此本轮给 `keep_P1`，进入 survivor slot 做一次唯一 follow-up。

## 对 runtime 的直接影响
- 分配新正式 Rank：`421`
- `Fresh intake slot` 更新为本对象的首判结果
- `Surviving candidate slot` 切换为 `Rank 421`
- 后续若继续验证，只允许做 1 次最小 follow-up，重点必须收敛在：真实 fee tier / depth aggregation / latency-half-life 是否能把 `gross` 留成正 net

## 尾部执行补记（非阻断）
- `publish_homepage_index.sh` 异步执行收到 `signal SIGKILL`，按 policy 归类为非阻断尾部失败。
- 本轮 verdict / state / rank / 日志结论保持有效，不回滚。
