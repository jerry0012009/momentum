# 2026-03-27 05:01 UTC｜bot3｜Rank 194 survivor follow-up｜promote_P2

## 本轮执行对象
- target: `Rank 194 / liquidity-ranked laggard delayed catch-up`
- 来源：`research/optimization_loop/2026-03-27_0422_rank194_liquidity_ranked_laggard_intake_keep_p1.md`
- 动作：作为当前唯一 `Surviving candidate` 执行那一次 follow-up，只回答 rolling `trade_count` + 同分钟 `underreaction score` 分层后，低流动性 laggards 在 BTC `1m` 冲击后的 `1m -> 2m/3m` delayed catch-up 是否仍显著强于高流动性对照
- 运行约束检查：`Rank 194` 已有正式 `Rank`；本轮未改 policy / brief / operating card / auto loop / cron prompt

## 本轮只做了什么
做了一个 cheap but decisive quick admission：
- 数据：Binance Spot 公共 `1m` klines，最近 `7d`
- 标的：`BTCUSDT` + `ETH/XRP/DOGE/ADA/LTC/QKC/CITY/BIFI/PIVX/GNO`
- BTC shock 定义：`abs(ret_BTC_1m)` 高于过去 `1440m` 的 `95%` 分位，且至少 `8 bps`
- liquidity 定义：各币自身 rolling `1440m` `trade_count` 百分位
- underreaction 定义：`dir * (beta * ret_BTC - ret_ALT_current)`，其中 `beta` 用 trailing `720m` rolling beta、并向后移一根 bar 保持因果
- focus bucket：`lowliq_topUR = tc_pct <= 0.3` 且同分钟 cross-sectional `underreaction rank >= 0.7`
- control bucket：`highliq_topUR = tc_pct >= 0.7` 且同分钟 cross-sectional `underreaction rank >= 0.7`
- 评估口径：`1m / 2m / 3m` gross catch-up，以及 `long laggard / short beta·BTC` 的 beta-hedged gross catch-up

产物：
- `reports/artifacts/optimization_loop/rank194_survivor_followup_20260327_0501/summary.csv`
- `reports/artifacts/optimization_loop/rank194_survivor_followup_20260327_0501/lowliq_topUR_by_day.csv`
- `reports/artifacts/optimization_loop/rank194_survivor_followup_20260327_0501/lowliq_topUR_by_symbol.csv`
- `reports/artifacts/optimization_loop/rank194_survivor_followup_20260327_0501/lowliq_topUR_signals.csv`
- `reports/artifacts/optimization_loop/rank194_survivor_followup_20260327_0501/meta.json`

## 关键结果
### 1) 低流动性 + 高欠反应 pocket 明显强于高流动性对照
`lowliq_topUR`：
- `113` 个 BTC shock 事件 / `129` 个信号
- beta-hedged gross catch-up：
  - `1m ≈ +7.36 bps`
  - `2m ≈ +10.05 bps`
  - `3m ≈ +8.84 bps`
- 命中率：
  - `1m = 71.3%`
  - `2m = 69.0%`
  - `3m = 65.9%`

`highliq_topUR` 对照：
- `436` 个事件 / `1037` 个信号
- beta-hedged gross catch-up：
  - `1m ≈ +3.55 bps`
  - `2m ≈ +4.58 bps`
  - `3m ≈ +4.21 bps`
- 命中率：
  - `1m = 56.2%`
  - `2m = 59.1%`
  - `3m = 57.0%`

翻成人话：不是“只要有欠反应就会补动”，而是**同样是 top-underreaction，rolling 低 trade_count 那一档的 delayed catch-up 明显更厚，且 2m 最强。**

### 2) 这不是单天偶然，也不只是 BTC 继续走的 beta 幻觉
`lowliq_topUR` 的 `2m` beta-hedged 结果在最近几天基本持续为正：
- `2026-03-22`: `+9.99 bps`
- `2026-03-23`: `+7.18 bps`
- `2026-03-24`: `+10.63 bps`
- `2026-03-25`: `+5.86 bps`
- `2026-03-26`: `+23.58 bps`

主贡献币种也不止一只：
- `PIVX`: `44` 信号，`2m ≈ +11.80 bps`
- `BIFI`: `37` 信号，`2m ≈ +9.14 bps`
- `GNO`: `19` 信号，`2m ≈ +12.87 bps`
- `CITY`: `19` 信号，`2m ≈ +8.85 bps`

### 3) 信号密度也还够，不是只靠极少数稀薄样本硬撑
- `129` 个信号 / `7d`，约等于每天 `18` 个信号
- 事件数 `113`，说明不是单一极端分钟被重复堆叠
- 这已经够支持它进入 `P2 admission`，再去补成本、跨资产、时间稳定性、参数稳定性与执行诚实性

## survivor verdict
**`promote_P2`**

### 会改变系统认知的一句话
`Rank 194` 的 survivor follow-up 已证明：当 BTC `1m` shock 出现时，rolling 低 `trade_count` 且同分钟 `top underreaction` 的 laggard bucket 在最近 `7d` 上录得 `2m` beta-hedged gross catch-up 约 `+10.05 bps`，明显强于高流动性对照约 `+4.58 bps`，所以它已经不是泛泛“BTC 带 alt”，而是值得进入正式 `P2 admission` 的单一 underreaction alpha。

## 为什么不是 park_to_background
如果结果只是“低流动性更慢”但做不出 gross pocket，我会直接 park。

这轮不是：
- 有明确 bucket 对照；
- 有 beta-hedged 口径；
- 有 `1m/2m/3m` monetization window；
- 有足够的事件与信号密度；
- 并且对象仍保持为单一 `BTC shock -> low-liquidity underreaction laggard catch-up`，没有扩写回泛化 cross-crypto 叙事。

因此最诚实的出口不是继续拖在 survivor，也不是 park，而是进入 `P2`。

## 进入 P2 后的最小 admission 问题
下一轮 `P2` 不该再重问“这个 pocket 存不存在”，而应直接按 policy 的 admission 轴去做：
1. 成本后有效性（maker / taker / impact proxy）
2. 跨资产稳定性（是否只靠 `PIVX/BIFI/GNO/CITY`）
3. 时间稳定性（分时段 / 分日 / 分周）
4. 参数稳定性（shock 分位 / liquidity 分位 / hold window）
5. honesty / execution realism（是否只在最小币上好看、容量是否过薄）
