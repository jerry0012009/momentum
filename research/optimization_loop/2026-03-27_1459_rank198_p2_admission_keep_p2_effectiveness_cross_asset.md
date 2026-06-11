# Rank 198 P2 admission round 1 — keep_P2 on effectiveness/cross-asset

- Time: 2026-03-27 14:59 UTC
- Target: `Rank 198 / dynamic cointegration pair-basket spread convergence`
- Verdict: `keep_P2`

## 本轮只回答的问题
只执行当前 `cycle_plan` 中排在最前的 pending 小点：

> 这条 dynamic pair-selection / basket-selection + spread convergence 框架，在 `effectiveness / cross-asset` 两个 admission 维度上，是否已经足够接近 `P3 / P1 / P0` 的明确出口？

## 本轮使用的证据
1. `research/optimization_loop/2026-03-27_1450_rank198_survivor_followup_promote_p2.md`
2. `research/quant_digests/2026-03-27_1332_dynamic-cointegration-minute-binned-pairs.md`
3. `reports/artifacts/quant_digests/dynamic_cointegration_pairs_20260327_1332/summary.json`
4. `research/quant_digests/2026-03-23_0958_dynamic-cointegration-pairs-raw-alpha.md`

## 会改变系统认知的结论
### 1) effectiveness：母体 alpha 还活着，但当前只够证明“稀疏 pocket 可做”，不够证明“已接近 paper trade”
- 当前 contemporaneous `15m` transfer check 里，五组 pair 等权后：
  - `net ≈ -0.019 bps/bar`
  - net cumulative `≈ -0.85%`
  - net annualized Sharpe `≈ -0.84`
- 说明这条对象**不能**被理解成“broad equal-weight deployment 已经可上线”。
- 但单 pair 层并非全灭，`TRXUSDT/ADAUSDT` 仍保留：
  - `net ≈ +0.051 bps/bar`
  - net cumulative `≈ +2.12%`
  - net annualized Sharpe `≈ 1.73`
  - `52` trades，active share `≈ 19.7%`
- 所以 effectiveness 的诚实读法不是 `P0`，也不是已到 `P3`，而是：
  - **该框架已经证明“selection-sensitive pocket”存在；**
  - **但还没有证明它在可部署口径下具有足够广度或余量。**

### 2) cross-asset：当前证据更像“少数相关币 pocket”，还不是可迁移的跨资产框架
- 现代映射里，论文历史强 pair 中只有 `TRXUSDT/ADAUSDT` 在当前样本仍明显为正；
- `LTC/ADA`、`XRP/ADA`、`BCH/ADA`、`XRP/TRX` 在相同口径下均为净负；
- 2026-03-23 的独立同主题证据也指向同一件事：naive dynamic spread 直接迁到 `15m` 并不自动过成本，下一步真正该补的是 `pair selection / regime / turnover control`。
- 这意味着 cross-asset 维度目前回答的是：
  - **框架可迁移的“研究对象定义”已经成立；**
  - **但跨资产可迁移的“部署稳定性”还没成立。**

### 3) 因而本轮出口不能是 `promote_P3`，也不该直接退回 `P1/P0`
- 不升 `P3`：因为目前没有证据说明它已经跨出单一 pocket、接近 paper trade / paper launch；
- 不退 `P1`：因为不存在新的 re-scope 方向，本对象当前定义已经明确，继续回到 `P1` 只会变成重复讨论；
- 不退 `P0`：因为母体 alpha 并未被 fatal flaw 否掉，至少已有一条 contemporaneous pocket 和一条独立历史 desk 证据共同支撑。

## 决策
本轮对 `Rank 198` 给出：

> **`keep_P2`**

新的系统读法应更新为：

> `Rank 198 / dynamic cointegration pair-basket spread convergence` 已通过“值得做 admission”的门槛，但在第一轮 admission 中只证明了 **selection-sensitive effectiveness**，尚未证明 **cross-asset deployability**；因此对象继续留在 `Active P2`，但必须把后续 admission 聚焦在剩余真正决定出口的 blocker，而不能再回到泛泛的 pair-pocket 复述。

## 为什么这一步会改变后续动作
- 现在已经明确：`Rank 198` 的主问题不是“有没有 alpha kernel”，也不是“值不值得继续放在 P2”；
- 真正剩余的 admission blocker 收敛为：
  1. `time stability`
  2. `parameter stability`
  3. `honesty / execution realism`
- 同时，`effectiveness / cross-asset` 这一轴已经有了正式结论：
  - **存在 pocket edge；**
  - **但 broad deployment 仍未成立。**

## Runtime writeback
- `Active P2 slot` 保持 `Rank 198`
- `latest_result` 更新为本轮 `keep_P2` admission 结论
- `latest_admission_record` / `latest_result_record` 更新为本日志
- `p2_rounds_since_level_change += 1`
- `p2_consecutive_keep_p2 = 1`
- `p2_last_evidence_axis = effectiveness / cross-asset admission`
- `cycle_plan #2` 标记为 `done`

## Reader-facing takeaway
`Rank 198` 这轮已经把第一层 admission 说清楚了：

**它不是 ready-for-paper 的广谱 pairs 部署，但也不是该被打回去的假 alpha；它目前成立的是“动态选对/选篮子之后，少数 spread convergence pocket 仍能留下净边”，因此对象合法留在 `P2`，后面只该补真正决定出口的剩余 blocker。**
