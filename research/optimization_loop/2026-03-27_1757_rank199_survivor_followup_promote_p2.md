# Rank 199 / US cash-session cross-asset lead-lag — survivor follow-up promotes to P2

- Time: 2026-03-27 17:57 UTC
- Target: `Rank 199 / US cash-session cross-asset lead-lag`
- Prior state: `Surviving candidate slot`
- This step verdict: `promote_P2`
- Narrowed working spec: `QQQ+NVDA coordinated downside shock -> short ETH (BTC secondary) 1h follow-through during US cash-session`

## Why this was the legal front-of-queue action
`BOT2_BOT3_STATE.md` 的第 1 个 pending 小点明确要求对 `Rank 199` 做唯一一次 survivor follow-up，并一次性回答：在更稳妥口径、`6~8 bps` 成本与剔除重大宏观事件后，它仍像独立 raw alpha，还是应降级成 event overlay / macro filter。当前 `Paper launch queue` 与 `Active P2` 均为空，因此这一步就是本轮唯一合法主动作。

## What I actually checked
本轮没有重排计划，只补这一个决定性维度：**source/cost/event honesty**。

### Data used
- Leaders: `QQQ`、`NVDA` 近 `60d` 的 Yahoo Chart API `15m` regular-hours bars（`includePrePost=false`，显式限制 `13:30~20:00 UTC`）
- Followers: `BTCUSDT`、`ETHUSDT` 近 `60d` 的 **Binance USDⓈ-M Futures 官方 `15m` klines**
- Hold window: leader bar close 后未来 `4 x 15m = 1h`
- Costs tested: round-trip `6 bps`、`8 bps`
- Macro/event exclusions: `2026-02-06` (NFP), `2026-02-12` (CPI), `2026-02-25` (NVDA earnings), `2026-03-06` (NFP), `2026-03-12` (CPI), `2026-03-18` (FOMC)

### Two signal definitions checked
1. **Same-clock decile**（更严的时钟归一）
   - 结果：edge 基本塌掉；BTC/ETH 在 ex-event 后都不再像可交易 pocket。
2. **Global decile**（更接近原 digest 的极端 bar 读法）
   - 结果：原始 broad thesis 被明显缩窄，但并没有完全失效。

## Key results that changed the system belief
### A. 若用更严的 same-clock decile，原 thesis 站不住
- `BTC`：all-signals `-6.2 bps` raw；剔除事件日后 `-10.7 bps` raw，净后更差
- `ETH`：all-signals `+5.0 bps` raw，但 `6~8 bps` 成本后转负；剔除事件日后也转负

这说明：**如果把 leader shock 严格标准化到 same-clock percentile，原始“QQQ+NVDA broad same-direction shock -> BTC/ETH 1h follow-through”并不是稳定独立 alpha。**

### B. 但在更贴近原 digest 的 global decile 口径下，ETH downside pocket 仍保留可交易净后
剔除上述大事件日后：
- `BTC`：`+3.8 bps` raw，`6~8 bps` 成本后转负
- `ETH`：`+13.2 bps` raw，`6~8 bps` 成本后仍约 `+7.2 / +5.2 bps`

更关键的是方向拆分：
- **upside leader shock（做多 crypto）**：ex-event 后几乎失效，`ETH` 只剩约 `+3.4 bps` raw，`BTC` 转负
- **downside leader shock（做空 crypto）**：ex-event 后仍明显保留
  - `BTC`: 约 `+13.3 bps` raw
  - `ETH`: 约 `+21.6 bps` raw

也就是说，真正留下来的不是“risk-on / risk-off 双边对称 broad basket alpha”，而更像：

> **`QQQ+NVDA` 联合大跌的极端 15m bar，会在接下来 1h 继续向 ETH（BTC 次之）传导出可交易的 downside follow-through；而 risk-on 版本并不稳。**

## Decision
本轮给出正式收口 verdict：**`promote_P2`**。

但升级的不是原始宽口径 thesis，而是下面这条更诚实、也更像 desk 策略骨架的版本：

- **P2 object:** `Rank 199 / US cash-session downside cross-asset lead-lag`
- **Core spec:** `QQQ+NVDA global-bottom-decile coordinated 15m downside shock -> short ETH for next 1h, BTC secondary / optional`
- **Why promote instead of parking:**
  1. 它不是只靠大事件日；剔除 FOMC/CPI/NFP/NVDA earnings 后，ETH 侧仍保留正净值空间；
  2. 这不是“普通 calendar anomaly”，而是有明确 leader、明确时段、明确方向、明确 hold window 的跨资产 raw alpha pocket；
  3. survivor 的唯一 follow-up 已经用完，再继续停在 `P1` 只是拖延；按 policy 应把仍存活的对象直接推进到 `P2 admission`，让下一轮围绕 effectiveness / cross-asset / time / parameter / realism 做正式 admission。

## What did NOT survive
- 不支持继续把它表述成 `BTC+ETH` 对称 basket broad strategy
- 不支持继续把它表述成 `same-direction` 双边都同样有效
- 不支持把它降级成“只在 FOMC / CPI / 财报才成立的 event overlay”——因为 ex-event 后 ETH downside pocket 仍活

## Runtime changes required
- `Surviving candidate slot`: 对 `Rank 199` 的唯一 follow-up 已执行完毕，应退出 survivor
- `Active P2 slot`: 改为 `Rank 199 / US cash-session downside cross-asset lead-lag`
- `p2_rounds_since_level_change = 0`
- `p2_consecutive_keep_p2 = 0`
- `p2_last_evidence_axis = source_cost_event_strip`
- `cycle_plan[1]`: 标记 `done`

## Artifacts
- `reports/artifacts/rank199_survivor_followup_20260327/summary.csv`
- `reports/artifacts/rank199_survivor_followup_20260327/signal_events.csv`
- `reports/artifacts/rank199_survivor_followup_20260327/meta.json`

## One-line result for state writeback
`Rank 199 / US cash-session cross-asset lead-lag` 的唯一 survivor follow-up 已完成：更严 same-clock 口径会把 broad thesis 打散，但在更贴近原 digest 的 global decile + Binance perp + 剔除 FOMC/CPI/NFP/NVDA earnings 后，`QQQ+NVDA` 联合 downside shock -> `short ETH 1h` 仍保留约 `+13.2 bps` raw / `+5.2~7.2 bps` net 的独立 pocket，因此不再留在 survivor，而是缩版升入 `P2`。
