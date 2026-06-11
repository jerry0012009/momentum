# Rank 222 / breakout-short penetration×ATR short-admission reframe — survivor 唯一 follow-up 收口：keep_P1 后转 background

- 时间：2026-03-28 13:32 UTC
- 对象：`Rank 222 / breakout-short penetration×ATR short-admission reframe`
- 本轮角色：`Surviving candidate` 唯一 follow-up
- 结论：`keep_P1 后转 background`

## 一句话结论
在冻结 `breakout-short` baseline 上补做 `penetration_strength=(breakout_anchor-close)/ATR14` 的 short-only threshold veto 后，方向上确实显示“越深越像 continuation”，但这次 strict A/B 仍只把 pooled `after-cost avg pnl` 从 **-0.165%/trade** 抬到 **-0.016%/trade**（`th=0.6`, `6bps/side`），尚不足以把它升成值得进入 `P2` 的 desk admission；因此这条 survivor 应诚实收口为 **`keep_P1 后转 background`**，保留为未来若有更强 baseline / sizing 口径时可 reopen 的 setup-specific score 线索，而不是继续占前排第二枪。

## 本轮怎么做的
严格按 survivor follow-up 只回答一个问题：
- 冻结现有 `breakout_short` baseline（复用本地 `signals_*_breakout_short_baseline.csv` 事件表，不改事件定义）
- 资产：`BTC / ETH / SOL`
- 执行：`next-bar open + no-overlap + after-cost`
- exit：固定 `hold 8 bars`
- 新增唯一一轴：`penetration_strength = (breakout_anchor - close) / ATR14`
- frozen veto grid：`0.2 / 0.4 / 0.6`

产物：
- `reports/artifacts/tmp_rank222_breakout_short_penetration_veto/base_trades.csv`
- `reports/artifacts/tmp_rank222_breakout_short_penetration_veto/summary_by_asset_threshold_cost.csv`
- `reports/artifacts/tmp_rank222_breakout_short_penetration_veto/summary_pooled_threshold_cost.csv`

## 关键结果
### pooled（BTC/ETH/SOL 合并）
以 `6bps/side` 为主口径：

| threshold | kept_trades | trade_retention | post-cost avg pnl | uplift vs baseline | continue vs fail spread |
|---|---:|---:|---:|---:|---:|
| baseline | 61 | 100.0% | -0.1650% | — | — |
| 0.2 | 56 | 91.8% | -0.1370% | +0.0280% | +0.3421% |
| 0.4 | 53 | 86.9% | -0.1129% | +0.0521% | +0.3975% |
| 0.6 | 43 | 70.5% | -0.0155% | +0.1496% | +0.5069% |

同方向结果在更高成本档也延续：
- `10bps/side`：`th=0.6` 后 `post-cost avg pnl = -0.0011%/trade`
- `15bps/side`：`th=0.6` 后 `post-cost avg pnl = -0.1011%/trade`

### 分资产读法
- **BTC**：`th=0.6` 才真正开始像样，`trade_retention=82.6%`，`post-cost avg pnl` 从 `-0.0509%` 抬到 `+0.0084%`。
- **ETH**：方向同样改善，但 `th=0.6` 后仍是 `-0.2612%/trade`；说明这条轴没有把 ETH baseline 拉到 admission 级。
- **SOL**：改善最明显，`th=0.6` 后 `trade_retention=66.7%`，`post-cost avg pnl=+0.0790%/trade`。

## 这一步改变了什么认知
1. **原 reframe 没有被证伪成“完全没信息”**：`continue_vs_fail_spread` 在三档阈值都为正，且 `0.6` 最强，说明 `penetration_strength` 确实在区分更像 continuation 的 short breakout。
2. **但它仍没跨过 admission 门槛**：最好的 pooled 结果只是把亏损压到接近持平，而不是留下足够稳定、足够厚的 after-cost alpha。
3. **它更像 score / sizing 线索，而不是当前可升 P2 的 hard veto**：如果后面还要继续挖，这条轴更适合未来挂在更强 breakout baseline 上做 score / size-down，而不是继续在当前 baseline 上开第二次开放式 follow-up。

## 为什么这轮不能 promote_P2
按本轮 success criterion，survivor 必须一次性收口；当前最诚实的阻断点只有一个：
- **唯一 decisive blocker：after-cost uplift 方向正确，但 pooled 口径仍未形成足够干净的正 expectancy / admission 级优势。**

更具体说：
- `trade_retention` 最高档还能保留 `70.5%`，这点不差；
- `continue_vs_fail_spread` 也明确为正，这说明 veto 不是纯噪音；
- 但真正该回答的 `post-cost avg pnl` 仍没翻到足够可交易，尤其 ETH 仍明显偏负；
- 因此它还不配升到 `P2 admission`，也不值得为了同一轴再开第二次 survivor follow-up。

## 本轮正式 verdict
- `Rank 222 / breakout-short penetration×ATR short-admission reframe`：**`keep_P1 后转 background`**

## 对 runtime 的影响
- `Surviving candidate slot` 应清空；`followup_budget_remaining` 归零并收口
- `Background pool` 更新为：`Rank 222` 的 survivor 唯一 follow-up 已完成；保留为未来若有更强 breakout baseline / score-vs-size 口径时可 reopen 的 setup-specific score 线索
- `cycle_plan` 第 1 项应标记为 `done`

## 附：本轮使用文件
- `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/signals_btcusd_breakout_short_baseline.csv`
- `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/signals_ethusd_breakout_short_baseline.csv`
- `reports/artifacts/scout_rank74_adx_er_trend_readiness_15m/signals_solusd_breakout_short_baseline.csv`
- `reports/artifacts/scout_tau_band_breakout_15m/cache/BTCUSDT__120d__15m.csv`
- `reports/artifacts/scout_tau_band_breakout_15m/cache/ETHUSDT__120d__15m.csv`
- `reports/artifacts/scout_tau_band_breakout_15m/cache/SOLUSDT__120d__15m.csv`
