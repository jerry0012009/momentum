# Rank 366 survivor follow-up — turning-point-confirmed continuation causalization

- 时间：2026-04-09 20:52 UTC
- 对象：`Rank 366 / turning-point-confirmed trend leg × short-horizon continuation`
- 动作：survivor 唯一一次 follow-up（honesty / causalization closeout）
- 结论：`background / P0`，不升 `P2`

## 这轮实际回答的问题
把这条线从前一轮的 `EMA slope flip` 薄近似，收紧成**严格非重绘**的 `confirmed swing -> prior-level exceed` 因果事件后，它还剩不剩一个独立 pocket？

我的结论：**不剩。**
它在 causalized 口径下既没有保住 top-liquid majors 的 after-cost continuation，也明显塌回成现有 `confirmed extremum / breakout confirmation` family 的一种变体，所以本轮应直接收口到 `background / P0`。

## 这轮最小 honesty 子检查
我直接复用了仓库现成的 `120d × 15m` perp 缓存（`BTC/ETH/SOL/XRP/ADA/DOGE/LINK/AVAX`），做了一个最便宜但会改变结论的 causal proxy：

### 事件定义（严格因果）
- 用 `K=2` 的对称 pivot 定义确认 swing；
- pivot 只在右侧 `2` 根 bar 出来后才算“已知”，避免把局部极值当场提前知道；
- **多头事件**：先有 `L0 -> H0 -> L1`，且 `L1 > L0`，随后在 `L1` 已确认后，价格**再次上破** `H0`；
- **空头事件**：镜像处理，即 `H0 -> L0 -> H1`、`H1 < H0`，再向下击穿 `L0`；
- 统计事件后 `1/3/6` 根的同向 forward return。

### 样本结果
跨 `8` 个 top-liquid majors 共得到 `8727` 个事件：

- 全样本平均：
  - `+1 bar`: `-0.33 bps`
  - `+3 bars`: `-0.59 bps`
  - `+6 bars`: `+1.75 bps`
- 若按保守 `8 bps` round-trip 成本：
  - `+1 bar net`: `-8.33 bps`
  - `+3 bars net`: `-8.59 bps`
  - `+6 bars net`: `-6.25 bps`
- `+3 / +6 bars` 胜率约 `45.2% / 45.9%`

资产层也没有出现“多数资产都还稳健为正”的图景：
- `BTC`: `+3 bars ≈ +1.55 bps`、`+6 bars ≈ +2.51 bps`，成本后仍显著为负；
- `AVAX`: `+3 bars ≈ +2.20 bps`、`+6 bars ≈ +3.52 bps`，成本后仍为负；
- `XRP / ADA / DOGE` 到 `+6 bars` 虽有小幅正值，但都远不够覆盖短周期交易成本；
- `ETH / SOL / LINK` 在该 causal 定义下连毛 edge 都不稳。

## 为什么这会改变层级判断
前一轮 `keep_P1` 的前提是：如果把 turning point 因果化后，仍能留下一个不同于 generic breakout 的、可交易的短续行动作，那它值得升 `P2`。

现在关键事实已经变了：

1. **honesty 关掉后，edge 没保住。**
   一旦不再用事后平滑的 turning point，而改成“已确认 swing + 之后再 exceed 前高/前低”的严格因果事件，`15m` top-liquid majors 的 continuation 只剩 very thin / mixed 毛收益，成本后整体转负。

2. **结构上也没有留下独立 pocket。**
   这个 causal 版事件本质上就是：
   - 先等一个已确认的 swing / extremum；
   - 再看后续有没有继续突破前一个 swing level。

   这和 desk 现有的 `confirmed extremum after BMS`、`breakout confirmation / follow-through` 家族已经高度同构。也就是说，turning-point 这层新说法没有额外保住一个与现有 family 可分离的 raw alpha；它更像**同一家族里的一种叙述方式**。

3. **没有明确的单次 re-scope 方向。**
   这里不是“只差一个明确重设 scope 就能保住”；恰恰相反，causal 化之后同时出现了：
   - 独立性下降（被吸收）；
   - 成本后可交易性不足。

   所以它不符合再留一次 `keep_P1` 的条件，也不该勉强升 `P2`。

## 本轮收口 verdict
- 层级：`Surviving candidate -> Background / P0`
- 一句话结果：**`Rank 366` 在严格非重绘的 `confirmed swing -> prior-level exceed` 口径下，15m top-liquid majors 的 continuation 只剩薄且成本后转负的 breakout-style follow-through，未保住独立 pocket，故 survivor follow-up 收口为 `background / P0`。**

## 对 runtime 的直接影响
1. `Surviving candidate slot` 应清空；
2. `Rank 366` 不进入 `P2`；
3. `cycle_plan` 第 1 项应标记为 `done`；
4. 前排默认继续回到下一条已存在的具体 fresh intake（当前仍是 `kimchi premium` 那条）。
