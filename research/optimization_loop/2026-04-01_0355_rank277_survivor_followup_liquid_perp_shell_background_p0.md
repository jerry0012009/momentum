# 2026-04-01 03:55 UTC · Rank 277 / US session window cross-sectional reversal survivor decisive follow-up

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`
- 本轮只执行 `cycle_plan` 第 1 个 pending 小点
- 目标：只回答一个问题——把 US open / close 的横截面 loser-winner reversal 迁到 liquid perp shell 后，是否至少还有一个 session window 能在现实成本下留下可迁移的 after-cost pocket

## 1. 本轮实验口径
### liquid perp universe
使用 Binance USDⓈ-M perpetual `15m` 公共 K 线，样本区间：`2025-10-01 ~ 2026-04-01 UTC`。

冻结 universe：
- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`
- `BNBUSDT`
- `XRPUSDT`
- `DOGEUSDT`
- `ADAUSDT`
- `LINKUSDT`
- `AVAXUSDT`
- `LTCUSDT`
- `BCHUSDT`
- `DOTUSDT`

这一步的意图很明确：不再停留在 source spot 中小币的 gross/impact 叙事，而是直接换到更液体、更接近可迁移交易壳的 perp majors / upper-mid caps。

### strategy skeleton
- 频率：`15m`
- signal window：
  - `morning = 13:30~14:00 UTC`（对应 US open pocket）
  - `close = 19:30~20:00 UTC`（对应 US close pocket）
- 横截面排序：按 signal window 最近 `30m` 收益做排名
- 组合：`long bottom 20% / short top 20% / dollar-neutral / equal-weight`
- 进场：signal 结束后再延后一个 bar，固定在 `+45m` 时点进场，避免把信号窗最后一根直接当成交价
- 持有：固定扫 `30m / 45m / 60m / 90m`

### 成本口径
统一冻结为 round-trip 成本三档：
- `maker = 4 bps`
- `mixed = 8 bps`
- `taker = 12 bps`

### 产物
- `reports/artifacts/rank277_survivor_followup_20260401/summary.csv`
- `reports/artifacts/rank277_survivor_followup_20260401/daily_returns.csv`
- `reports/artifacts/rank277_survivor_followup_20260401/raw_15m_perp.csv`

## 2. 核心结果
来自 `summary.csv` 的主结论：

### close window
- `30m hold`: gross `-0.39 bps/day`; maker net `-4.39`; mixed `-8.39`; taker `-12.39`
- `45m hold`: gross `-0.21`; maker net `-4.21`; mixed `-8.21`; taker `-12.21`
- `60m hold`: gross `+1.06`; maker net `-2.94`; mixed `-6.94`; taker `-10.94`
- `90m hold`: gross `+0.52`; maker net `-3.48`; mixed `-7.48`; taker `-11.48`

### morning window
- `30m hold`: gross `-1.90 bps/day`; maker net `-5.90`; mixed `-9.90`; taker `-13.90`
- `45m hold`: gross `-0.01`; maker net `-4.01`; mixed `-8.01`; taker `-12.01`
- `60m hold`: gross `-1.03`; maker net `-5.03`; mixed `-9.03`; taker `-13.03`
- `90m hold`: gross `-1.47`; maker net `-5.47`; mixed `-9.47`; taker `-13.47`

## 3. 该怎么读
这次最关键的信息，不是“成本太高所以先 keep_P1”，而是：

1. **更液体 shell 并没有把这条线救活。**
   - close window 最好的 gross 也只有 `60m hold ≈ +1.06 bps/day`；
   - morning window 最好的 gross 接近 `0`；
   - 说明问题已经不再是“impact 太大把中小币 gross 吃掉”，而是换到 liquid perp 之后，alpha 本体就已经非常薄。

2. **两个 session window 都没有留下 after-cost pocket。**
   - maker / mixed / taker 三档全部为负；
   - 没有任何一个 hold 组合达到“至少在 maker 或 mixed 下还明显为正”的门槛。

3. **这不满足 survivor 升 `P2` 的成功条件。**
   cycle plan 已写死：
   - 若至少一个 window 在 liquid perp majors / upper-mid caps、现实成本下保留清晰 after-cost edge，则 `promote_P2`；
   - 否则直接 `drop_to_background/P0`。

本轮结果属于后者，而且证据已经足够 decisive，不需要再拖出第二刀。

## 4. survivor verdict
### 结论
**`Rank 277` 不升 `P2`，直接 `drop_to_background/P0`。**

### 原因
- source 里的 gross alpha 主要建立在 spot 中小币横截面；
- 一旦迁到更诚实、更液体的 perp shell，两个 US session pocket 都只剩接近零或负的 gross；
- 成本后更是全线为负；
- 因此当前不存在“至少一个可迁移 after-cost pocket”这件事。

## 5. 一句话结果
`Rank 277` 的唯一 survivor follow-up 已经诚实收口：**US open / close 横截面 loser-winner reversal 迁到 liquid perp majors / upper-mid shell 后，maker/mixed/taker 三档下都没有留下可迁移的 after-cost pocket，因此本轮直接回 `background/P0`。**
