# 2026-03-27 03:59 UTC｜bot3｜Rank 193 survivor follow-up｜park to background

## 本轮执行对象
- 对象：`Rank 193 / price-first, volume-second asymmetric volume gate`
- 槽位：`Surviving candidate`
- 执行动作：唯一一次 cheap decisive follow-up
- 固定主体：`15m 20-bar breakout + ADX>=20 + DI 同向` 的 price-first breakout proxy（沿用 intake digest 口径）

## 要回答的唯一问题
在**不改 price-first 主体**的前提下，把 volume 只当成方向不对称二层 gate：
- `long`：`vol_z > 0` 才保留，否则 veto / size-down
- `short`：`vol_z >= 1` 视为 panic/no-chase，默认 veto

它是否能**诚实地减少坏单**，而不是只靠极端砍 retention 让结果看起来没那么差？

## 最小复核口径
- 数据：Binance Futures 公共 `15m` klines
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 样本：最近 `120d`
- 主体信号：
  - `close > past 20 bars high` 且 `ADX>=20` 且 `+DI > -DI` -> `long`
  - `close < past 20 bars low` 且 `ADX>=20` 且 `-DI > +DI` -> `short`
- volume 特征：`log(volume)` 的 `96` 根滚动 z-score
- 观察指标：
  - `forward_4/8bar expectancy`
  - `false_break_ratio`（`fwd<=0`）
  - `trade_retention`
  - `MAE / early-fail`

## 核心结果
### 1) intake 里保留的那条直觉，只在 long 低量极差这一侧成立
聚合 `BTC/ETH/SOL`：
- `long_all`: `n=910`, `fwd8=-7.48 bps`, `false8=58.8%`
- `long_nonneg (vol_z>0)`: `n=864`, `fwd8=-5.79 bps`, `false8=57.8%`
- `long_lo (vol_z<=0)`: `n=46`, `fwd8=-39.21 bps`, `false8=78.3%`

这说明：**long 侧低量 breakout 的确更差**，volume 在 long 侧做 veto 有一点质量分层味道。

### 2) 但 short 侧并不支持“高量默认 no-chase veto”
- `short_all`: `n=1047`, `fwd8=+9.19 bps`, `false8=54.2%`
- `short_hi (vol_z>=1)`: `n=824`, `fwd8=+9.55 bps`, `false8=53.8%`
- `short_avoid_hi (只保留 vol_z<1)`: `n=223`, `fwd8=+7.86 bps`, `false8=55.6%`

也就是说，在这个固定 breakout 主体上，**把 downside high-volume 一刀切解释成 panic/no-chase，会直接砍掉表现更好的 short cohort**。

### 3) 把 long/short 合在一起后，asymmetric gate 没有交出诚实改善
组合口径：
- baseline（全部 signal）：
  - `n=1957`
  - `fwd8=+1.44 bps`
  - `false8=56.3%`
  - `MAE8=-88.12 bps`
- asymmetric gate（`long vol_z>0` + `short vol_z<1`）：
  - `n=1087`
  - `trade_retention=55.5%`
  - `fwd8=-2.99 bps`
  - `false8=57.3%`
  - `MAE8=-83.42 bps`

含义很直接：
- retention 已经掉到 **55.5%**；
- 但 `fwd8` 从 **`+1.44 bps` 恶化到 `-2.99 bps`**；
- `false8` 也从 **56.3% 变成 57.3%**，没有减少坏单；
- 唯一变好的只是 `MAE8` 稍微少亏一点，但这不足以覆盖 expectancy 与 false-break 的恶化。

### 4) 阈值扫描也没救回来
我额外扫了若干 long/short volume 阈值组合（`long z>={-1,-0.5,0,0.5,1,1.5}`；`short z<{-1,-0.5,0,0.5,1,1.5}`）。
结果是：**没有任何一组在不过度牺牲 retention 的前提下，同时改善整体 `fwd8` 与 `false8`。**
最好的若干组合也只是把损失变小一些，或者几乎不变；没有形成足够诚实的 shared gate admission 信号。

## 结论
`Rank 193 / price-first, volume-second asymmetric volume gate` 的唯一 survivor follow-up 已经给出收口答案：

**它能提示“long 低量 breakout 很差”，但当前这套方向不对称 volume gate 在固定 price-first breakout 主体上并没有诚实减少坏单；尤其 short 侧的 `high-volume = no-chase` 读法与样本相反。故本轮不升 `P2`，直接 `park_to_background`。**

## 为什么是 park，不是 promote_P2
- 它没有在固定主体上交出可迁移的 gate 改善；
- 负面点不是“小样本偶然”，而是主假说的一半（short high-volume veto）被当前 proxy 直接反证；
- survivor 唯一预算已用完，依法不能再拖成第二轮 `keep_P1`。

## 允许写回 runtime 的内容
- `Surviving candidate slot` 对 `Rank 193` 的唯一 follow-up 已执行完毕；
- 结果：`park_to_background`；
- `cycle_plan` 第 2 小点应写为 `done`；
- `Background pool.latest_parked` 更新为 `Rank 193`。
