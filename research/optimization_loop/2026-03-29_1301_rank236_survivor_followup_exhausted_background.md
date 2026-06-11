# 2026-03-29 13:01 UTC — Rank 236 / breakout-short-specific short-side admission score-veto survivor follow-up exhausted

## 为什么这轮做它
- 按 `docs/BOT2_BOT3_STATE.md` 当前 `cycle_plan`，排在最前的 pending 小点是：
  - `Rank 236 / breakout-short-specific short-side admission score-veto`
- 本轮严格只执行这一个小点：
  - 在 frozen `breakout-short` short-side baseline 上做唯一一次最小 clean replication；
  - 直接回答它更接近 `promote_P2` 还是用尽 survivor 预算后回 `background/P0`。

## 本轮读取/使用的权威输入
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. `research/optimization_loop/2026-03-29_1033_rank236_rank86b_distinctness_turn_into_fresh_intake.md`
4. `research/optimization_loop/2026-03-29_1248_rank236_first_verdict_keep_p1.md`
5. `research/quant_digests/2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md`
6. `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/summary_pooled.csv`
7. `reports/artifacts/quant_digests/2026-03-23_donchian_strength_short_admission/summary_by_symbol_side_threshold.csv`
8. `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/trades.csv`

## 这轮只回答一个问题
在统一事件源里，`Rank 236` 的 `short-only penetration/ATR veto/score` 是否还能保留独立、可复现、足以升级到 `P2` 的 post-cost 增量？

## clean replication 口径
### 统一事件源
- 直接使用当前 frozen `breakout-short` baseline：
  - `reports/artifacts/scout_rank151_breakout_short_family_honest_gate_15m/trades.csv`
  - 只取 `variant=baseline`、`event_side=-1`、`cost_bps_per_side=6.0`
- 这样比较的是**同一批已冻结 breakout-short short-side 事件**，而不是重新换一套 proxy 事件源。

### 当根 strength 定义
- 对每个 baseline short 事件，在对应 `signal ts` 当根回算：
  - `donchian_lower = prior 20 bars rolling low`
  - `ATR14 = trailing ATR`
  - `short_strength = (donchian_lower - signal_close) / ATR14`
- 然后只做最小阈值过滤：`strength > 0.2 / 0.4 / 0.6`
- 不改 entry/exit，不改持有期，不叠第二轴。

### 产物
- `reports/artifacts/rank236_breakout_short_survivor_followup/summary.csv`
- `reports/artifacts/rank236_breakout_short_survivor_followup/asset_summary.csv`
- `reports/artifacts/rank236_breakout_short_survivor_followup/events_with_strength.csv`
- `reports/artifacts/rank236_breakout_short_survivor_followup/meta.json`

## 结果
### pooled summary（同一 frozen baseline 上）
| threshold | trades | retention | mean_net_bps | win_rate | positive_asset_ratio |
|---|---:|---:|---:|---:|---:|
| baseline (`>0.0`) | 1727 | 1.000 | -3.47 | 40.36% | 0.33 |
| `>0.2` | 1218 | 0.705 | -4.58 | 40.64% | 0.33 |
| `>0.4` | 839 | 0.486 | -4.26 | 40.41% | 0.33 |
| `>0.6` | 559 | 0.324 | -5.15 | 41.14% | 0.00 |

### 分币读法
- `BTCUSDT`：
  - baseline `-7.25 bps`
  - `>0.2` `-12.25 bps`
  - `>0.4` `-12.30 bps`
  - `>0.6` `-8.04 bps`
- `ETHUSDT`：
  - baseline `+3.61 bps`
  - `>0.2` `+5.39 bps`
  - `>0.4` `+3.50 bps`
  - `>0.6` `-6.76 bps`
- `SOLUSDT`：
  - baseline `-5.85 bps`
  - `>0.2` `-5.80 bps`
  - `>0.4` `-3.10 bps`
  - `>0.6` `-0.56 bps`

## 结论
- **结论：`Rank 236` 在统一 frozen `breakout-short` baseline 上没有保留足够独立的 post-cost admission 增量，不能升 `P2`。**
- digest/proxy 里的“short-side pooled 改善”在当前真正前排的 frozen breakout-short 事件源上没有复现出来：
  - retention 明显下降；
  - pooled `mean_net_bps` 没有变好，反而整体更差；
  - `positive_asset_ratio` 从未提升到值得升级的水平，`>0.6` 时甚至降到 `0.00`。

## 为什么这一步必须收口到 background
根据 policy：
- `Surviving candidate` **只能有 1 次**最小 decisive follow-up；
- 这 1 次之后若仍未升级到 `P2`，默认移入 `Background pool`；
- 不允许继续开放式 `keep_P1`。

本轮 clean replication 已经直接回答：
- 这条线的改善主要停留在旧 proxy/digest 口径；
- 一旦挂到统一 frozen baseline，独立 admission 增量消失；
- 因此 survivor 预算视为**已用尽**，应诚实写成 `background/P0`，而不是再续命。

## hard verdict
- **`Rank 236 / breakout-short-specific short-side admission score-veto`：survivor follow-up exhausted，回 `background/P0`**
- 不是 `promote_P2`
- 也不是继续 `keep_P1`

## 对 runtime 的直接影响
1. `Surviving candidate slot` 清空为 `none`，`followup_budget_remaining` 归零。
2. `Background pool.latest_parked` 改写为本轮结论。
3. `cycle_plan` 第 1 项写成 `done`，并把结果写成：
   - `Rank 236` 在统一 frozen breakout-short baseline 上未复现独立 post-cost admission 增量；唯一 survivor follow-up 用尽后回 `background/P0`。
4. `Active P2 slot`、`Paper launch queue` 本轮不变。

## 备注
- 本轮没有改写 policy / brief / cron prompt。
- 本轮没有重排 `cycle_plan`。
- 本轮 reader-facing 的系统认知变化是：`Rank 236` 从 `Surviving candidate` 诚实收口到 `background/P0`。
