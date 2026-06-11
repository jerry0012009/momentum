# Rankless fresh intake：Savitzky-smoothed depth imbalance × simple-model continuation first verdict = background/P0

- 时间：2026-04-06 03:24 UTC
- 执行动作：只执行 `cycle_plan` 第 2 项（当前最前的 `pending` 小点）：`research/quant_digests/2026-04-06_0040_sg-lob-imbalance-continuation-alpha.md`
- 结论：`Savitzky-smoothed depth imbalance × simple-model continuation` 这条 fresh intake 的 first verdict = `background/P0`

## 为什么这轮直接收口到 background/P0
这份 digest 确实把一个有用结论讲清楚了：**对 LOB directional continuation，先做输入去噪，可能比继续堆更深模型更值钱。** 但按当前 bot2/bot3 policy，这还不够构成一个新的前排 raw alpha 对象，原因有三点。

### 1) 新增的是输入工程证据，不是新的 desk 主语
当前对象的 base alpha 仍是：

- `depth imbalance / weighted-mid / spread / queue state`
- 预测极短期方向 continuation
- 再聚合到 `1m / 3m` 做可交易 conviction

这和我们已经 intake 过的对象仍属于同一母线，而不是新主语：
- `Rank 161` 一类单资产 `OFI + VWAP pressure` taker raw alpha
- `Rank 182 / lob-lgbm-quantile-timing-alpha`
- `Rank 279 / L1 imbalance × VWAP-to-mid × spread gate`
- 以及更广义的 `OBI / OFI / LOB directional continuation` 家族

这轮真正新增的是：
- `Savitzky–Golay / Kalman` 去噪对比
- `simple model > deeper model` 的实务偏好
- `top5/top10/top20/top40` depth portability 提醒

这些都属于**同一家族的 evidence thickening**，不是足够独立到应单开一个正式 Rank 的 raw alpha 本体。

### 2) digest 还没有压出独立于既有 intake 的 `1m/3m after-cost` 新骨架
当前 digest 最强证据仍是：
- Bybit BTC/USDT 单日 `100ms` LOB classification
- `500ms / 1000ms` horizon 上 SG 处理后 accuracy 提升
- 从亚秒信号映射到 `1m/3m` conviction 的 desk blueprint

但它没有给出真正决定 fresh intake 去留的那一步：

> 相对已有 `OBI / OFI / LOB directional continuation` intake，这个“SG-smoothed depth imbalance”是否已经形成**独立的、可命名的、after-cost 更厚的 `1m/3m` 交易骨架**？

目前答案不够成立。现有材料更像是：
- 说明原本那条 LOB continuation 母线，输入清洗方式值得升级；
- 但还没证明“去噪版”已经是一个新对象，而不只是老对象的更好实现件。

### 3) portability 风险仍偏大，不适合凭单日 Bybit 结果升为 keep_P1
digest 自己已经诚实写明：
- 核心展示以单日 Bybit 盘口为主；
- classification accuracy 不等于 after-cost PnL；
- `40-level` 虽然 paper 上更强，但 live 缺失率、带宽、存储与跨 venue 可移植性都还没过；
- `1m/3m` 只是合理转译，还不是已压实的 desk replication。

这意味着它离 `keep_P1` 还差一步关键区分：
- 如果后续真跑出 `raw vs SG vs Kalman` 在统一 `1m/3m`、统一 friction ladder 下，SG 版相对已有 LOB/OBI intake 有**明确净增量**，那可以作为 reopen 或 supporting evidence 使用；
- 但在当前轮，直接把它当一个全新前排对象保留，会和 policy 要求的“distinct raw alpha 主语”冲突。

## 本轮改变了什么系统认知
`Savitzky-smoothed depth imbalance × simple-model continuation` 不应作为新的 front-slot fresh intake 独立推进；它当前更适合作为**既有 microstructure directional continuation 家族的 supporting evidence / implementation upgrade hint**，而不是新的可单独命名 raw alpha。

## runtime 回写
- `Fresh intake slot.current_target`：切到当前 digest
- `Fresh intake slot.latest_result`：写回 `background/P0` first verdict
- `Background pool.latest_parked`：更新为当前对象
- `cycle_plan[2]`：写回 `done`

## 不做的事
- 不分配 Rank：因为本轮 verdict 不是 `keep_P1 / P2 / P3`
- 不改写后续排班：遵循 policy，只执行当前最前的一个 `pending` 小点
- 不自动 reopen 任何旧 microstructure 对象：当前新增只够作为 supporting evidence，不够改变既有层级结论
