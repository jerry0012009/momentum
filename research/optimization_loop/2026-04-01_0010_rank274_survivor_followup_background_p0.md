# 2026-04-01 00:10 UTC — Rank 274 survivor follow-up：ETH dual-thrust 更长窗复验后回 background/P0

## 本轮执行的小点
- target: `Rank 274 / ETH dual-thrust SMA200 breakout`
- action: 作为当前唯一合法 survivor，只执行这一次 decisive follow-up，直接回答这条 `ETH / daily adaptive breakout × SMA200 bull gate / 5m execution` 在更长样本、统一成本与最小 falsification 下，是否足以从 `P1` 进入 `P2`
- success_criterion: 若更长样本下 `5m` after-cost pocket 仍成立、且至少能说明它不是纯 execution 偶然或单一窗口幻觉，则升 `P2`；否则 survivor 预算用尽并回 `background/P0`

## 这次实际做了什么
只做这一次 follow-up，不扩新 intake、不改别的 pending 条目：
1. 读取原 digest / keep_P1 记录，锁定主语仍是 **ETH dual-thrust + SMA200 bull gate + intraday breakout execution**；
2. 补读原 repo 公开规则说明，确认 baseline 仍是 `N=3 / K=0.5 / 07:00 open / 16:00 exit / 1% stop / SMA200 gate`；
3. 新写 `scripts/build_rank274_survivor_followup.py`，改走 `data.binance.vision` 公共历史包，避免 Binance API 429；
4. 在更诚实的执行口径下重做长窗复验：
   - `honest execution = first high > trigger 后，下一个 bar open 入场`
   - `one trade/day`
   - `1% stop`
   - `16:00 UTC time exit`
   - 显式扣 `6 / 10 / 14 bps per side`
5. 做最小 falsification：
   - 同一规则比较 `ETH 5m` vs `ETH 15m`
   - 同一规则外推到 `BTCUSDT 5m`、`SOLUSDT 5m`

## Artifact
- `scripts/build_rank274_survivor_followup.py`
- `reports/artifacts/rank274_survivor_followup/decision.json`
- `reports/artifacts/rank274_survivor_followup/summary.csv`
- `reports/artifacts/rank274_survivor_followup/eth_5m_yearly_10bps.csv`
- `reports/artifacts/rank274_survivor_followup/eth_15m_yearly_10bps.csv`
- `reports/artifacts/rank274_survivor_followup/btc_5m_yearly_10bps.csv`
- `reports/artifacts/rank274_survivor_followup/sol_5m_yearly_10bps.csv`
- `reports/artifacts/rank274_survivor_followup/trades_ETHUSDT_5m.csv`
- `reports/artifacts/rank274_survivor_followup/trades_ETHUSDT_15m.csv`
- `reports/artifacts/rank274_survivor_followup/trades_BTCUSDT_5m.csv`
- `reports/artifacts/rank274_survivor_followup/trades_SOLUSDT_5m.csv`

## 冻结规则
- data window: 最近 `900d` execution sample，另加 `260d` daily warmup
- data_end: `2026-04-01 00:00 UTC`
- regime gate: `prev-day close > SMA200(prev-day)`
- range: `max(HH-LC, HC-LL)` over prior 3 completed UTC days
- anchor: 当日 `07:00 UTC` open
- trigger: `anchor_open + 0.5 * range`
- entry: 第一根 `high > trigger` 之后的 **下一根 bar open**
- stop: `entry * 0.99`
- exit: `16:00 UTC` open
- metric: fixed-size return sum / mean net bps

## 核心结果

### 1) ETH 5m：还有 pocket，但厚度不够诚实地升 P2
| cost/side | trades | mean net bps | total net pct | years_positive | first_half | second_half |
|---|---:|---:|---:|---:|---:|---:|
| 6 bps | 55 | +12.99 | +7.14% | 2 | -0.32% | +7.47% |
| 10 bps | 55 | +4.97 | +2.73% | 2 | -2.48% | +5.22% |
| 14 bps | 55 | -3.04 | -1.67% | 1 | -4.64% | +2.97% |

读法：
- `10bps/side` 下总样本还剩一点正 pocket，但已经薄到只剩 `+4.97 bps/trade`；
- `14bps/side` 直接转负，说明边很薄；
- 更关键的是 **前后半样本不稳**：前半段已经是负的，正值主要靠后半段补回来；
- 按年份看也不是稳定单向：
  - `2023`: `+0.63%`
  - `2024`: `-3.34%`
  - `2025`: `+5.45%`

### 2) ETH 15m：并非完全失效，但更像弱 pocket，不支持“稳定 execution-insensitive alpha”
| cost/side | trades | mean net bps | total net pct | years_positive | first_half | second_half |
|---|---:|---:|---:|---:|---:|---:|
| 6 bps | 54 | +9.02 | +4.87% | 2 | +5.04% | -0.17% |
| 10 bps | 54 | +1.01 | +0.55% | 1 | +2.87% | -2.33% |
| 14 bps | 54 | -6.99 | -3.78% | 1 | +0.71% | -4.49% |

读法：
- `15m` 没有像“完全假信号”那样归零，但在 `10bps/side` 下只剩 `+1.01 bps/trade`、第二半样本转负；
- 这说明 edge 的确对 execution granularity 敏感，但又没有形成足够厚、足够稳的 `5m >> 15m` admission 证据。

### 3) 最小 falsification：BTC / SOL 没有复制 ETH 的结果
| asset | interval | 10bps/side trades | mean net bps | total net pct |
|---|---|---:|---:|---:|
| BTC | 5m | 74 | -15.63 | -11.57% |
| SOL | 5m | 59 | -34.59 | -20.41% |

读法：
- 这条规则没有在同口径 major universe 上迁成普遍 breakout alpha；
- 当前仍更像 **ETH-specific**，而且不是那种厚到足以覆盖更宽 desk execution 假设的口袋。

## 诚实 verdict
**`Rank 274 / ETH dual-thrust SMA200 breakout` 的唯一 survivor follow-up 已完成：不升 `P2`，直接回 `background/P0`。**

原因不是这条线完全没东西，而是更关键的 admission 问题已经被回答：
1. 更长窗口下，`ETH 5m` 的确还留有一点 after-cost pocket，但在 `10bps/side` 只剩 `+4.97 bps/trade`，厚度偏薄；
2. 这条 pocket **跨年份不稳**：`2024` 明确为负，前半样本也为负，不能说它已经摆脱单一窗口依赖；
3. `14bps/side` 直接转负，说明对成本非常敏感；
4. `BTC/SOL` 同规则不复制，表明它当前仍主要是 **ETH-only** 结构；
5. `ETH 15m` 虽未彻底失效，但也只剩极薄正值，不足以把它抬成一个 execution-insensitive、可诚实 admission 的 `P2` 对象。

因此本轮最诚实的层级结论不是再拖一轮 survivor，而是：**唯一 follow-up 预算用尽，回 `background/P0`。**

## 本轮回写要点
- `Surviving candidate slot`：清空，`followup_budget_remaining = 0`
- `Fresh intake slot`：释放前排，改为 `ready_for_new_intake / current_target: none`
- `Background pool.latest_parked`：更新为 `Rank 274`
- `cycle_plan[1]`：
  - `result` = `Rank 274 的唯一 survivor follow-up 已完成：900d 更长窗口下，ETH dual-thrust 在 honest next-bar-open + 10bps/side 口径虽仍有约 +4.97 bps/trade、+2.73% total 的 5m pocket，但 2024 年与前半样本为负、14bps 下转负，且 BTC/SOL 同规则不复制，因此不够诚实地升 P2，预算用尽后回 background/P0。`
  - `status` = `done`

## 一句话结论
`Rank 274` 不是“完全没 alpha”，但它在更长窗、统一成本与最小 falsification 下留下的仍是一个 **ETH-only、成本敏感、跨窗口不够稳** 的薄 pocket；这还不够诚实地占住 `P2 admission`。