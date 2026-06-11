# Rank 338 — extreme funding tail carry — survivor follow-up = background / P0

- Time: 2026-04-05 15:27 UTC
- Target: `Rank 338 / extreme funding tail carry`
- Slot: `Surviving candidate`
- Verdict: `drop_to_background / P0`
- Artifact: `reports/artifacts/rank338_survivor_followup/summary.csv`

## What changed
`Rank 338` 的 survivor 唯一一次 follow-up 已经收口：把对象压成 `BTC/ETH` clean-room `extreme positive funding` 事件研究后，`boundary-time extreme-only` 与 `basis-expansion veto` 都没有把样本抬到可 admission 的 after-cost 水平，因此这条对象不升 `P2`，直接回 `background/P0`。

## Method
- 标的：`BTCUSDT`, `ETHUSDT`
- 样本：近 `730d`
- 数据：Binance public funding history + Binance spot/perp `5m` klines
- 事件定义：只保留 `annualized funding APR >= 15%` 的极端正 funding 窗口
- 持有定义：`funding boundary` 前 `30m` 建立 `long spot + short perp`，持有到下一个 funding 窗口结束（`+8h`）
- 成本：沿 repo baseline，开/平各 `14bps`，往返 `28bps`
- veto：若 funding 前最近 `15m` 的 spot-perp basis 仍在扩张，则视为 `basis-expansion veto fail`

## Decisive findings
### 1) continuous threshold carry 本体仍是 fee-dominated
按 digest 里的 baseline 状态机复刻：
- `BTC`：`211` 次 entry，单次平均净值约 `-22.5bps`
- `ETH`：`207` 次 entry，单次平均净值约 `-22.0bps`

这说明问题依旧不是“看错 funding 方向”，而是默认 carry 壳在 liquid majors 上持续被 fees 吃掉。

### 2) extreme-only 没有把净收益翻正
只看 `APR >= 15%` 的极端 funding 尾部：
- `BTC`：`48` 个事件，平均净值 `-25.82bps/event`，正收益事件 `0/48`
- `ETH`：`70` 个事件，平均净值 `-25.84bps/event`，正收益事件 `0/70`
- 合并：`118` 个事件，平均净值 `-25.83bps/event`，正收益事件 `0/118`

换句话说，极端 funding 尾部并没有在 `BTC/ETH` 上留下“funding 足以覆盖 28bps roundtrip fees”的可交易 pocket。

### 3) boundary-time + basis-expansion veto 也不是 decisive blocker-remover
把样本缩到 `boundary-timed extreme-only + basis-expansion veto` 后：
- veto 通过事件只剩 `38/118`
- 合并平均净值仍为 `-25.60bps/event`
- `veto pass` 与 `veto fail` 的平均净值几乎一样：
  - `veto pass`: `-25.60bps/event`
  - `veto fail`: `-25.93bps/event`
- 正收益事件仍然是 `0`

所以 `basis-expansion veto` 最多只是轻微删掉更差的事件，并没有把样本整体从负净值抬到可 admission 的正 pocket，更谈不上成为 survivor follow-up 里唯一 decisive blocker-remover。

## Why this closes the survivor honestly
根据 policy，survivor 只允许这一次最小 decisive follow-up。这里的 follow-up 已经直接回答了唯一关键问题：

> `boundary-time + fee-churn veto` 是否真能把 extreme funding carry 压成一个在 BTC/ETH 上留得下净收益的可 admission 壳？

答案是否定的。既然最关键的 clean-room 问题已经被回答，而且结果没有造成层级上移，就不应该继续拖成长尾 `keep_P1` 或补同维度重复证据。

## Runtime result sentence
`Rank 338`：`BTC/ETH` clean-room survivor follow-up 已确认，`extreme-only` 与 `boundary-time + basis-expansion veto` 都无法把 extreme funding tail carry 提升到 after-cost 可 admission 的 P2 壳，故按 policy 直接 `drop_to_background / P0`。
