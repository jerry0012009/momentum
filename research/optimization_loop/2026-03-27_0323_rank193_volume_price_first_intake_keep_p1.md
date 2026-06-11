# 2026-03-27 03:23 UTC｜bot3｜Rank 193 fresh intake｜price-first, volume-second volume gate

## 本轮执行对象
- 来源：`research/quant_digests/2026-03-27_0223_volume-is-not-trend-alpha.md`
- 对象：`Rank 193 / price-first, volume-second asymmetric volume gate`
- 类型：`shared gate / filter`
- 执行动作：fresh intake 首判（仅允许 lightweight proxy）

## 为什么这轮不是直接 park
这篇 digest 的结论很明确：**volume 不是 15m 趋势发动机本体**。如果把它硬翻成独立 raw alpha，应该直接 park。

但本轮要回答的不是“volume 本身能不能当 alpha”，而是：**`price-first, volume-second` 这条更窄的 shared-gate 读法，是否值得保留成一个单独的 desk 对象。**

我认为答案是：**值得，先保留到 `P1`。**

原因不是它已经证明能赚钱，而是它已经把一个高频误用点收窄成了一个可诚实验证的最小对象：
1. 方向仍由 price-defined setup 决定，而不是由 volume spike 决定；
2. volume 的职责被压缩为二层 `quality / veto / sizing`；
3. 且这个职责具有**明确的方向不对称**：
   - `up-signal + high volume` 更像质量加分，而不是启动器；
   - `down-signal + high volume` 更像 `panic / no-chase / size-down` 风险提示，而不是 generic continuation blessing。

这已经不是泛化的“volume 有用吗”，而是一个非常具体、可 clean-room 检验的 gate 假说。

## 为什么它不是旧 Rank 87 的重复 reopen
它和 `Rank 87 / volume-clock + CS spread interaction gate` 有亲缘，但不是同一个对象。

- `Rank 87` 的主轴是：真实成交活跃窗口不等于固定时钟，并尝试把 `volume-clock + CS spread` 写成 queue-facing allow/deny gate；
- 本轮 `Rank 193` 的主轴是：**无论什么主策略，volume 都应该被降级到 `price-first` 之后的条件层，而且 long/short 要分开读。**

也就是说：
- `Rank 87` 更像“时钟 / microstructure 角度的 gate”；
- `Rank 193` 更像“volume 在 desk 架构里的正确职责定义”。

前者已经 park；后者仍值得用一次 survivor follow-up 看它能不能在现有 raw alpha 上减少坏单。

## 本轮首判
**verdict：`keep_P1`**

### 一句话结果
`Rank 193 / price-first, volume-second asymmetric volume gate` 值得保留为单一 shared-gate desk 对象：当前证据支持把 volume 明确降级为 price-defined signal 之后的方向不对称 `quality / veto / sizing` 层，而不是独立趋势发动机。

## 进入 survivor 的最小 clean-room 定义
下一轮唯一合法 follow-up 不应再做泛泛 literature 复述，而应直接回答：

> 在一个固定的 price-first 主体（优先选 `15m breakout / retest-hold / EMA-pullback` 之一）上，加入 `asymmetric volume gate` 后，是否能**减少坏单**，而不是只靠大幅砍 retention 让结果“看起来没那么差”。

### 最小对象定义
- `signal_on`：完全由 price-first 主体决定（本轮不改 signal）
- `volume_gate_long`：`up-signal` 下，`vol_z >= 1` 只作为 quality add；`vol_z <= 0` 作为 `size-down or veto`
- `volume_gate_short`：`down-signal` 下，`vol_z >= 1` 默认不是追击 blessing，而是 `maker-first / smaller-size / no-chase`
- 第一轮 survivor 指标只看：
  - `false_break_ratio`
  - `forward_4/8bar expectancy`
  - `trade_retention`
  - `MAE / early-fail`

### survivor 成败门槛
- 若它只能靠极端压缩 retention 才“少亏一点”，则直接 `park_to_background`；
- 若它能在不显著摧毁 retention 的前提下，稳定减少坏单或改善 early-fail / false-break ratio，则可考虑 `promote_P2`。

## 为什么不是直接 promote_P2
因为当前证据还停留在：
- 一篇论文 + 一个很轻的 transfer check；
- 能支持“别把 volume 当发动机”，
- 但还不足以证明这条 gate 在任何一个固定 price-first 主体上已经形成诚实、可迁移的 admission-worthy edge。

所以最诚实的位置是：**`keep_P1`，给它一次且仅一次 survivor follow-up。**

## 本轮允许写回 runtime 的结论
- 新 fresh intake 对象成立；
- 分配正式 `Rank 193`；
- fresh intake 首判：`keep_P1`；
- survivor 槽位应切换到该对象，等待唯一一次 cheap decisive follow-up。
