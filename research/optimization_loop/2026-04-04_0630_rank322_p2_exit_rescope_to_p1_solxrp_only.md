# Rank 322 — P2 exit decision — one-time P2->P1 re-scope to SOL-XRP-only 15m lane

- 时间：2026-04-04 06:30 UTC
- 对象：`Rank 322 / cointegrated spread z-score × stop-loss/time-exit`
- 轮次角色：bot3 自动执行
- 结论：`one-time P2->P1 re-scope`

## 为什么这一步改变系统认知
`Rank 322` 不再能被诚实地写成“major-pair 15m pairs shell 已足够接近 paper launch”。在更长样本、固定 beta 诚实重检、以及参数扰动之后，原先 survivor 阶段一起存活的 `BTC-XRP / SOL-XRP` 双 lane 已经分叉：**`BTC-XRP` 基本掉出可做范围，只有 `SOL-XRP × 15m` 还保留一条窄而真实的 post-cost pocket。** 这意味着对象不该直接升 `P3`，但也不该直接打回 `P0`；最诚实的出口是做 **一次性 `P2->P1 re-scope`**，把研究对象收窄成 `SOL-XRP-only × 15m`。

## 本轮 admission 口径
只围绕上一轮已锁定的 `BTC-XRP / SOL-XRP × 15m` lane 做最窄 admission，不再重跑泛 pairs 叙事。

### 数据与方法
- 数据：Binance USDⓈ-M 公共 `15m` klines
- 样本：约 `9000` bars（`2025-12-31 12:30 UTC` → `2026-04-04 06:15 UTC`）
- 训练 / 测试：前 `60%` 训练、后 `40%` 测试
- admission 检查：
  1. 更长样本下的 cointegration / half-life
  2. 每周滚动 beta 稳定性
  3. 固定 beta 的 weekly ADF honesty 重检通过率
  4. `entry={1.5,2.0,2.5}` × `exit={0,0.5}` × `cost={4,8,12bps}` 参数扰动
  5. 额外查看 rolling-sigma 口径是否还能留住 8bps 净边

## 关键结果
### 1) `BTC-XRP`：之前的幸存 lane 在更长样本下没有守住
- 训练窗 cointegration `p = 0.0567`，只算勉强擦线；
- `phi = 0.9976`，`half_life ≈ 284.55` bars，约 `71` 小时，明显比 survivor 阶段看到的节奏更慢；
- 每周滚动 beta `cv ≈ 0.417`，固定 beta weekly ADF 通过率只有 `34.5%`；
- 参数扰动下：
  - `entry=1.5 / exit=0` 在 `4bps` 仅约 `+0.0053`，到 `8bps` 已转为 `-0.0011`；
  - `entry>=2.0` 基本没有成交，说明并不存在稳定可迁移的 desk lane；
- 结论：`BTC-XRP` 不能再当作可推进到 paper 的诚实证据。

### 2) `SOL-XRP`：仍保留一条窄 lane，但已经不是“可直接 paper launch”的强度
- 训练窗 cointegration `p = 0.0047`，比 `BTC-XRP` 更干净；
- `phi = 0.9970`，`half_life ≈ 230.33` bars，约 `57.6` 小时，仍偏慢但尚可解释为慢均值回归；
- 每周滚动 beta `cv ≈ 0.381`，固定 beta weekly ADF 通过率约 `46.0%`，说明结构仍会漂移；
- 参数扰动下最稳的一角落在：
  - `entry=1.5 / exit=0.5`
  - `net4 ≈ +0.0858`
  - `net8 ≈ +0.0746`
  - `net12 ≈ +0.0634`
  - `trades = 7`
- 但当 sigma 也改成 rolling 口径后，`8bps` 变成约 `-0.0818`，说明这条 lane 对建模口径仍敏感，离 `paper launch` 还差一层 admission。

### 3) honesty / execution realism 的实际结论
这轮最重要的不是“还能不能找出正数”，而是：
- **固定 beta + weekly ADF 重检** 会多次强制平仓，说明 pair 关系并不稳定到可以放心 paper；
- `SOL-XRP` 虽然还能活，但更像一条 **需要重新定义 scope 的窄 lane**，而不是已经完成 `P2 -> P3` admission 的成熟对象；
- 因此当前不能诚实写成 `promote_P3`。

## 出口判断
按照 policy，本轮必须把 `Active P2` 收口成出口决策：

- **不是 `promote_P3`**：因为更长样本后只剩 `SOL-XRP` 单 lane 勉强存活，且 rolling-sigma / weekly honesty gate 下稳健性不够，不足以支撑 paper launch。
- **也不是 `background/P0`**：因为确实存在一条仍为正的、方向明确的窄 lane，不属于完全失效。
- **因此最诚实的结论是 `one-time P2->P1 re-scope`**：把对象从“major-pair 15m pairs shell”收窄成 **`SOL-XRP-only × 15m`** 的 re-scoped P1，后续若还要继续，只能围绕这条唯一剩余 lane 做一次重新定义后的 cheap check，而不能再把 `BTC-XRP` 一起打包叙述。

## 建议的 re-scope 语义
若后续要继续，新的对象语义应写成：

> `SOL-XRP-only 15m cointegrated spread z-score mean reversion with lower entry threshold, weekly fixed-beta honesty gate, and explicit slow-half-life acceptance`

也就是：
- 放弃“major-pair 普遍可做”的外延；
- 明确承认它是 **单 pair、慢 half-life、低频一些的 15m lane**；
- 后续只值得验证这条窄 lane 在更严格 execution 假设下是否还能保留最小 post-cost pocket。

## 对 runtime 的直接影响
- `Active P2 slot`：本轮出口已收口，释放为 `none`。
- `Rank 322`：执行一次性 `P2->P1 re-scope`，不再以原始 `major-pair dual-lane` 叙事占用 `Active P2`。
- 当前 `Surviving candidate slot` 已被 `Rank 324` 占据，因此 `Rank 322` 的 re-scoped P1 仅作为已定义的新 scope 记录在 runtime，等待 bot2 下轮决定是否显式排入前排。
