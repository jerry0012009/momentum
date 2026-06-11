# Rank 198 P2 admission round 2 — keep_P2 on time/parameter/honesty

- Time: 2026-03-27 15:30 UTC
- Target: `Rank 198 / dynamic cointegration pair-basket spread convergence`
- Verdict: `keep_P2`

## 本轮只回答的问题
只执行当前 `cycle_plan` 中排在最前的 pending 小点：

> 对这条 `Active P2` 补第二轮 admission，但必须换轴到 `time stability / parameter stability / honesty-execution realism`；直接回答它现在更接近 `promote_P3`、`one-time P2->P1 re-scope`，还是 `drop_to_background`。

## 本轮使用的证据
1. `research/optimization_loop/2026-03-27_1459_rank198_p2_admission_keep_p2_effectiveness_cross_asset.md`
2. `research/optimization_loop/2026-03-27_1450_rank198_survivor_followup_promote_p2.md`
3. `research/quant_digests/2026-03-27_1332_dynamic-cointegration-minute-binned-pairs.md`
4. `reports/artifacts/quant_digests/dynamic_cointegration_pairs_20260327_1332/summary.json`
5. `research/quant_digests/2026-03-23_0958_dynamic-cointegration-pairs-raw-alpha.md`

## 会改变系统认知的结论
### 1) time stability：alpha 家族没有死，但“广谱 pair/basket deployment”跨时段稳定性没有被证成
- 论文样本（2018~2019 BitMEX）显示 dynamic cointegration pairs / basket 当年非常强；
- 当前 desk 映射（2025Q4~2026Q1 Binance USDⓈ-M `15m`）里，五组 pair 等权组合已经成本后转负：
  - `net ≈ -0.019 bps/bar`
  - net cumulative `≈ -0.85%`
  - net annualized Sharpe `≈ -0.84`
- 但同一 contemporaneous 样本里，`TRXUSDT/ADAUSDT` 仍保留：
  - `net ≈ +0.051 bps/bar`
  - net cumulative `≈ +2.12%`
  - net annualized Sharpe `≈ 1.73`
- 所以时间维度最诚实的读法是：
  - **spread convergence 这类 stat-arb kernel 还活着；**
  - **但它跨时期稳定保留下来的，是稀疏 pocket，不是可以直接 paper launch 的 broad deployment。**

### 2) honesty / execution realism：当前证据口径基本诚实，没有明显 fatal flaw
- 这轮不是只看 paper 里的回测，而是已经做了现实 desk 映射：
  - `60% formation / 40% trading` split；
  - 明确 `entry z=2.0 / exit z=0.5 / max_hold=16 bars`；
  - 明确加入 `6 bps round-trip` 成本；
  - 结果里大多数 pair 被成本打回负值，而不是被选择性忽略。
- `TRXUSDT/ADAUSDT` 的净值保留也不是靠超高换手硬刷出来：
  - `52` trades over `4222` trading bars；
  - average hold `≈ 8.48 bars`；
  - active share `≈ 19.7%`。
- 因而本轮看不到明显的 lookahead / repaint / friction denial 级别 fatal flaw；
- **honesty 维度可以认为通过了“没有明显作弊式成立”的 admission 门槛。**

### 3) parameter stability：这是当前唯一仍未被解决、且足以挡住 `promote_P3` 的 decisive blocker
- 目前仍只有一组主规格被最小映射验证：
  - `entry_z = 2.0`
  - `exit_z = 0.5`
  - `max_hold = 16`
  - `round-trip cost = 6 bps`
- 现存 pocket 的净边并不宽：`TRXUSDT/ADAUSDT` gross cumulative `≈ +5.36%`，扣成本后只剩 net cumulative `≈ +2.12%`；
- 同时组合层已经明确不能部署，因此当前 verdict 几乎完全压在单一 pocket + 单一参数口径上；
- 在这种情况下，**如果不先确认参数扰动后 pocket 仍然活着，就还不能把它升级成 `P3 / paper launch`。**
- 也就是说，本轮剩下的唯一 decisive blocker 已经收敛为：
  - **“这条 surviving pocket 在邻近参数、持有期、执行假设下是否仍然成立？”**

## 决策
本轮对 `Rank 198` 给出：

> **`keep_P2`**

新的系统读法应更新为：

> `Rank 198 / dynamic cointegration pair-basket spread convergence` 在 `time stability / honesty-execution realism` 上已经足够说明它不是伪 alpha，也不是靠不诚实口径成立；但它仍未跨过 `parameter stability` 这一唯一 decisive blocker，因此本轮只能形成**第二次连续 `keep_P2`**，下一步必须直接进入正式出口决策，不能再产出第三次开放式 admission。

## 为什么这一步会改变后续动作
- 现在 `Rank 198` 的 admission blocker 不再是泛泛的“还要再看更多”；
- 剩余问题已被压缩成一个单点：**单一 surviving pocket 的参数稳定性是否足够支撑 paper launch，还是只够支撑一次明确 re-scope / 或直接退出前排**；
- 因此后续合法动作只剩：
  1. `promote_P3`（若认为现有 pocket 已足够值得 paper trade）
  2. `one-time P2->P1 re-scope`（若唯一明确方向是把对象收窄成特定 pocket / execution-aware spec）
  3. `drop_to_background`（若认为参数稳定性不足以支撑继续前排）

## Runtime writeback
- `Active P2 slot` 保持 `Rank 198`
- `latest_result` 更新为本轮第二次 `keep_P2` admission 结论
- `latest_admission_record` / `latest_result_record` 更新为本日志
- `p2_rounds_since_level_change = 2`
- `p2_consecutive_keep_p2 = 2`
- `p2_last_evidence_axis = time stability / parameter stability / honesty-execution realism`
- `cycle_plan #1` 标记为 `done`

## Reader-facing takeaway
`Rank 198` 现在已经不是“要不要继续 admission”的问题，而是**该怎么正式出 P2**的问题：

**这条 dynamic cointegration 框架在诚实口径下确实留下了少数活着的 spread-convergence pocket，但当前仍没有证成参数稳定性；因此它还不能直接升 `P3`，同时下一步也不允许再写第三次开放式 `keep_P2`。**
