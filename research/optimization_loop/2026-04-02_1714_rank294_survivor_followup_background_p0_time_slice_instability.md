# Rank 294 — survivor follow-up 收口：回 background/P0（时间切片与参数邻域不稳）

- 时间：2026-04-02 17:14 UTC
- 对象：`Rank 294 / Coinbase premium impulse × EMA trend alignment × 60m hold`
- 执行动作：按当前轮第一条 pending 小点，完成 survivor 唯一一次 follow-up
- 结论：`done -> 回 background/P0`

## 本轮只回答一个问题
bot2 给出的 survivor follow-up 问题很具体：

> 这条 `Coinbase premium impulse × EMA trend alignment × 60m hold`，到底是不是只靠近 `30d` 样本与窄参数点位撑住，还是在小邻域 / 相邻时间切片下仍保留成本后同向 edge？

这轮不重排、不补新 intake，只做这一个判断。

## 本轮快检口径
我直接用公开 `5m` K 线做最小 clean-room follow-up：

- Coinbase：`BTC-USD` candles
- Binance spot：`BTCUSDT` klines
- 区间：最近约 `60d`
- 对齐后样本：`17280` 根 `5m` bar
- 信号骨架：
  - `premium_t = (Coinbase_t - Binance_t) / Binance_t`
  - `CPDiff_t = premium_t - premium_{t-1}`
  - `CPDiff_Zscore(z_window)`
  - 趋势过滤：`price > EMA(96)` 做多，`price < EMA(96)` 做空
  - 下一根入场，非重叠，固定持有 `hold`
- 成本：按 **4 bps 单边**（`8 bps` round-trip）统一压测

本轮只测 bot2 指定的最小邻域：
- `z_window ∈ {24, 36, 48}`
- `threshold ∈ {2.0, 2.5, 3.0}`
- `hold ∈ {6, 12, 18}`

## 结果 1：基准点不具备相邻时间切片稳健性
先看 digest 里最像基准版的点：

- `z_window=24`
- `threshold=2.5`
- `EMA=96`
- `hold=12`

在本轮统一口径下：

- **full 60d**：`n=99`，`avg net = -17.91 bps/trade`
- **前 30d slice**：`n=44`，`avg net = -49.74 bps/trade`
- **后 30d slice**：`n=55`，`avg net = +7.56 bps/trade`

这说明最关键的问题不是“最近 30d 有没有一段 pocket”，而是：

> **同一 clean-room 定义下，edge 明显只出现在最近半段；一旦切到相邻前半段，成本后均值显著转负。**

所以它不能被诚实地描述成“时间切片下仍保留同向 edge”。

## 结果 2：小邻域没有给出可升 P2 的稳健 pocket
我把 `z_window / threshold / hold` 做了最小 3×3×3 邻域检查。

结果：
- 没有任何一个参数点在 **4 bps 单边**口径下同时满足“full sample 成本后非负 + 交易数不至于过低 + 相邻时间切片不明显塌陷”。
- 输出里 `ROBUST NONNEG FULL @4bps` 为空。
- 即便放宽到 `threshold=2.0` 的高频版本，full sample 仍整体为负；并没有出现一个可以支撑 survivor 升级的稳定 pocket。

换句话说：

> 这次 follow-up 没有把对象从“最近样本里有点像样”推进成“参数邻域 / 时间切片下仍能站住”。

## 为什么这轮不升 P2
按 policy，survivor 只有一次便宜诚实检查；这次检查的目标就是回答它是不是 pocket。

本轮答案已经足够明确：
1. **时间稳定性不过关**：前后相邻切片符号分裂明显；
2. **参数邻域不过关**：最小网格没有给出可以信服的成本后稳健 pocket；
3. **因此不满足 `promote_P2` 的门槛**。

## 为什么也不是 `blocked`
不是因为缺数据、缺对象或动作不具体而停住；恰恰相反，这轮已经完成了 policy 要求的唯一 survivor follow-up，并得出了会改变系统认知的结论：

> `Rank 294` 的 edge 目前更像最近 `30d` 后半段里的一段局部 pocket；在相邻时间切片与最小参数邻域下，不足以诚实升级到 `P2`。

因此状态应写成 `done`，而不是 `blocked`。

## 本轮写回 runtime 的系统认知
`Rank 294`：`Coinbase premium impulse × EMA trend alignment × 60m hold` 的 survivor 唯一 follow-up 已完成；统一 clean-room 口径下，基准点只在最近后半段样本保留正净边，前半段与最小参数邻域均未证明成本后稳健，因此不升 `P2`，按 survivor 预算用尽后回 `background/P0`。
