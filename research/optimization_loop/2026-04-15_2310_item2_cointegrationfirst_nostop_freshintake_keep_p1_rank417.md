# bot3 optimization loop log — 2026-04-15 23:10 UTC

## 执行小点
- cycle_plan item 2
- target: `research/quant_digests/2026-04-15_2218_cointegrationfirst-nostop-cryptopairs-alpha.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + 分时段 + 最小 execution realism）

## 结果摘要（会改变系统认知）
`cointegration-first pair admission × no-stop intraday spread fade` 在本轮最小可复核口径下未被否决且具备费后存活 pocket，判定 `keep_P1` 并分配正式 `Rank 417`；但存在单一 survivor blocker：`Asia` 分时段在 `4/6/8bps` 下均为负，尚未达到跨时段同向稳健。

## 关键证据
本轮新增 artifact：
- `reports/artifacts/quant_digests/2026-04-15_cointegrationfirst_nostop_t2_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-15_cointegrationfirst_nostop_t2_probe_pairs.csv`
- `reports/artifacts/quant_digests/2026-04-15_cointegrationfirst_nostop_t2_probe_trades.csv`

最小复核口径（Binance USDⓈ-M `15m`，8 大流动性币，`t+2` 入场，`|z|>=2`，no-stop 仅零轴回归平仓，round-trip 成本 `4/6/8bps`）：
- 总体：`n=100`，`gross_mean=+16.89bps`，`net4=+8.89bps`，`net6=+4.89bps`，`net8=+0.89bps`
- 分时段：
  - `Asia`：`net4=-9.80bps`，`net6=-13.80bps`，`net8=-17.80bps`
  - `EU`：`net4=+13.92bps`，`net6=+9.92bps`，`net8=+5.92bps`
  - `US`：`net4=+29.25bps`，`net6=+25.25bps`，`net8=+21.25bps`
- 现实性提示：中位持有 `41` 根 `15m` bar，属于明显资金占用型 no-stop 形态，不适合作为“全时段无差别上线”结论。

## 最小 honesty / execution realism 子检查
- **无前视**：信号、入场、出场按 bar 序列前向计算，统一 `t+2` 延迟。
- **执行现实性（最小）**：统一 round-trip `4/6/8bps`；直接按 entry UTC 小时切分 Asia/EU/US，不混并口径。
- **唯一 survivor blocker**：`Asia` 在三档成本下全负，说明该 alpha 当前是“时段选择性有效”，不是“全时段稳健有效”。

## 本轮执行结论
- verdict: `keep_P1`
- rank_assignment: `Rank 417`
- survivor_slot: `Rank 417 / cointegration-first pair admission × no-stop intraday spread fade`
- status: `done`

## 尾部执行状态（非阻断）
- homepage publish：待本轮尾部命令执行。
- 邮件通知：待本轮尾部命令执行。
