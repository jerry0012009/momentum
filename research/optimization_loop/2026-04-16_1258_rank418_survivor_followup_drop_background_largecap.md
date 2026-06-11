# bot3 optimization loop — 2026-04-16 12:58 UTC

## 执行小点
- target: `Rank 418 / funding boundary neg-FR latency short shell`
- action: survivor 唯一 follow-up：仅做“大容量子集去拥挤”最小决策检查（统一 `t+2 + 4/6/8bps` + Asia/EU/US）并补 1 个最小 execution realism（容量收缩后的可成交滑点上界）

## 本轮执行
1. 仅在大容量合约子集（`BTC/ETH/SOL/BNB/XRP/ADA/DOGE`）上复算极端负 funding 事件；阈值使用各 symbol 最近样本内分位（`fundingRate <= q20` 且 `<0`）。
2. 统一执行口径：`t+2` delayed-confirmation 入场，`+15m` 退出，按 1m K 线计算 short-leg return（bps）。
3. 统一成本口径检查 `4/6/8bps`，并按 Asia/EU/US 分时段拆分。

## 关键结果（大容量去拥挤后）
- 样本事件：`247`
- overall：mean `-5.50bps`；`net8=-13.50bps`（`net6=-11.50bps`, `net4=-9.50bps`）
- Asia：mean `-12.03bps`；`net8=-20.03bps`
- EU：mean `-0.17bps`；`net8=-8.17bps`
- US：mean `-5.19bps`；`net8=-13.19bps`
- symbol 级别（`net8`）均未转正：BTC `-11.46`、ETH `-20.05`、SOL `-4.91`、BNB `-17.35`、XRP `-15.63`、ADA `-12.47`、DOGE `-15.78`。

## 最小 honesty / execution realism 结论
上一轮 survivor 的唯一 blocker（“去小币种拥挤后是否仍有费后边际”）已被直接证伪：当样本收敛到可交易容量更可信的大容量子集后，`t+2→+15m` 在统一摩擦口径下整体与分时段均为负，无法支撑继续升档。

## 出口决策（本轮必须收口）
`Rank 418` survivor 唯一 follow-up 已用尽且唯一 decisive blocker 未通过，本轮结论为 `background/P0`（不进入 `P2`）。

## runtime 回写
- `Surviving candidate slot`：`Rank 418` 收口退出（follow-up budget 用尽，结论转 `background/P0`）。
- `Background pool`：追加 `Rank 418 / funding boundary neg-FR latency short shell`（大容量去拥挤后费后不可复制）。
- `cycle_plan` item1：`status=done`，`result` 写入收口结论。