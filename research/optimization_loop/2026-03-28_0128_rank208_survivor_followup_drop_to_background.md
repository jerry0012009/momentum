# 2026-03-28 01:28 UTC · Rank 208 / extreme-return shock percentile survivor follow-up

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 本轮只执行 `cycle_plan` 里当前排在最前且 `status: pending` 的唯一小点：`Rank 208 / extreme-return shock percentile`
- 动作类型：`Surviving candidate` 唯一 follow-up（收口轮）

## 1. 本轮要回答的唯一 decisive 问题
在 `BTC/ETH`（并补看 `SOL`）的 `3m/5m` majors 上，把两支分开：
- `q95/q99 continuation`
- `q10/q5 fade`

并在 `2/4/8/12 bps round-trip` friction ladder 下并排比较：
- `无确认`
- `VWAP 确认`

只回答：**成本后还剩 continuation pocket、fade pocket，还是两边都过不了 friction。**

## 2. 本轮实现与证据口径
- 数据源：Binance UM monthly klines public feed
- 样本：`2025-03` 到 `2026-02`
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT`
- bar：`3m / 5m`
- 事件定义：
  - 正 shock：用滚动 20 天等效 lookback 的正收益尾部分位定义 `q95 / q99`
  - 负 shock：用滚动 20 天等效 lookback 的负收益绝对值尾部分位映射 `q10 / q5`
- 交易解释：
  - `continuation`：正 shock 后继续做多
  - `fade`：负 shock 后做多反转
- 持有：`1 / 2 / 4` 根 bar
- `VWAP 确认`：事件 bar 收盘价必须站上当日累计 VWAP
- artifact：`reports/artifacts/rank208_survivor_followup_20260328/summary.csv`

## 3. 关键结果
先看 policy 指定的主判断口径：**BTC/ETH majors 是否在成本后留下 pocket。**

### 3.1 8 bps round-trip：没有任何 majors pocket 存活
对 `BTCUSDT + ETHUSDT` 的全部组合（`3m/5m × q95/q99 continuation × q10/q5 fade × 无确认/VWAP × hold 1/2/4`）汇总后：

> **`8 bps round-trip` 下，`BTC/ETH` 没有一组组合的平均单笔收益仍为正。**

也就是说，本轮最重要的问题已经被直接回答：
- 不是 continuation 留下了 pocket；
- 也不是 fade 留下了 pocket；
- 而是 **两边都过不了 friction。**

### 3.2 最接近存活的是 ETH fade + VWAP，但只到低摩擦边缘
最强的几组都落在 `ETH` 的 `fade + VWAP` 支上，例如：
- `ETHUSDT 5m q5_fade + VWAP, hold 4`：`gross +7.21 bps`，但到 `8 bps RT` 变成 `-0.79 bps`
- `ETHUSDT 5m q5_fade + VWAP, hold 2`：`gross +5.45 bps`，到 `8 bps RT` 变成 `-2.55 bps`
- `ETHUSDT 3m q5_fade + VWAP, hold 2`：`gross +4.92 bps`，到 `8 bps RT` 变成 `-3.08 bps`

这说明：
- **确实有一点 fade micro-pocket 的影子；**
- 但它只够支撑接近 `4 bps` 的低摩擦环境，**一到 desk 默认更诚实的 `8/12 bps` 就消失。**

### 3.3 continuation 并没有比 fade 更好
- `q95/q99 continuation` 在 `BTC/ETH` 上没有一组能在 `8 bps` 存活；
- 最好的 continuation 也只是在低成本附近勉强接近盈亏平衡，且明显弱于上面的 `ETH fade + VWAP`。

因此，这条线当前留下来的并不是“continuation 比 fade 更稳”的结构性结论；恰好相反，**如果说还有一点影子，也只是在 ETH 的负 shock fade 上，但仍不够穿过 friction cliff。**

## 4. 收口结论
按 survivor follow-up 的 success criterion，这一轮必须在 `升 P2` 与 `移入 Background pool` 之间收口。

本轮正式结论是：

> **`Rank 208 / extreme-return shock percentile` 在 BTC/ETH majors 的 `3m/5m`、`2/4/8/12 bps RT`、`无确认/VWAP` 并排口径下，没有留下成本后可存活的 continuation pocket 或 fade pocket；survivor 唯一 follow-up 用尽后，应直接移入 `Background pool`，不升 `P2`。**

## 5. 为什么不是继续拖一个新的 P1/P2 检查
不继续拖的原因很直接：
1. **本轮补的是唯一高杠杆 blocker**：成本后到底有没有 pocket。
2. 现在答案已经出来：**在 majors + 诚实 friction 下没有。**
3. 若再继续补更多相近维度（更多 quantile、更多确认、更多 hold），很大概率只是围绕同一轴做低杠杆微调，而不会改变层级判断。

所以按照 policy，这里应诚实收口，而不是继续占前排资源。

## 6. Artifact
- 汇总：`reports/artifacts/rank208_survivor_followup_20260328/summary.csv`
- BTC/ETH 全量排序：`reports/artifacts/rank208_survivor_followup_20260328/majors_full.csv`

## 7. 一句话结果
**Rank 208 的 survivor 唯一 follow-up 已把最关键问题补完：ETH 上确有一点低摩擦 fade 影子，但在 BTC/ETH majors 的 `8/12 bps` 诚实成本下，continuation 与 fade 两支都没有留下可存活 pocket，因此这条线本轮不能升 `P2`，应直接从 survivor 收口并移入 `Background pool`。**
