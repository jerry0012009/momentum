# Rank 322 — survivor follow-up — promote P2 on major-pair 15m honest lane

- 时间：2026-04-04 04:57 UTC
- 对象：`Rank 322 / cointegrated spread z-score × stop-loss/time-exit`
- 轮次角色：bot3 自动执行
- 结论：`promote_P2`

## 为什么这一步改变系统认知
`Rank 322` 已不只是“pairs 壳子完整、值得留档”的 P1 教材母板；在 survivor 那唯一一次 follow-up 里，系统现在已经能锁定一条**具体、诚实、可迁移**的 desk lane：**major-coin pairs × 15m z-score mean reversion，在带 half-life / pair-quality admission 且经过 2/4/8 bps 成本梯度后，至少保留了少数正净边 lane**。这足以把对象从“可继续观察的壳”升级为 `Active P2 admission candidate`。

## 本轮证据（直接围绕唯一 follow-up 问题）
### 1) 至少存在一条不是只靠宽松口径存活的 lane
来自 `reports/artifacts/quant_digests/pairs_repo_20260404/pair_scan_15m.csv`：
- `BTCUSDT-XRPUSDT`：
  - `phi = 0.9890`
  - `half_life_bars = 62.82`（15m bar 下约 15.7 小时）
  - `net2_bps = +0.228`
  - `net4_bps = +0.199`
  - `net8_bps = +0.140`
  - `trades = 44`
  - `sharpe4 = 8.51`
- `SOLUSDT-XRPUSDT`：
  - `phi = 0.9921`
  - `half_life_bars = 86.85`（约 21.7 小时）
  - `net2_bps = +0.282`
  - `net4_bps = +0.240`
  - `net8_bps = +0.158`
  - `trades = 62`
  - `sharpe4 = 7.62`

这一步最关键的不是“收益高”，而是：**在更严格的成本梯度下没有立刻掉到负值**。说明它不是只能靠最宽松 friction 假设活着。

### 2) lane 是具体的，不是“pairs 都可以”
同一张表里，许多 pair 在 4~8 bps 下已经接近或跌破零，例如：
- `SOLUSDT-BNBUSDT`：`net8_bps = -0.015`
- `ETHUSDT-ADAUSDT`：`net8_bps = -0.036`
- `BNBUSDT-XRPUSDT`：`net8_bps = -0.050`

所以系统认知不能写成“整个 major-coin pairs 壳普遍可做”；更诚实的写法是：
> **只有少数带较好 pair-quality / half-life 结构的 lane 存活，其中当前最干净的是 `BTC-XRP` 与 `SOL-XRP` 的 15m lane。**

### 3) horizon narrowing 也给出了诚实边界
来自 `focus_pair_interval_portability.csv`：
- `BTCUSDT-XRPUSDT`：
  - `15m net4 = +0.199`
  - `5m net4 = +0.017`
  - `3m net4 = -0.025`
- `SOLUSDT-XRPUSDT`：
  - `15m net4 = +0.240`
  - `5m net4 = -0.105`
  - `3m net4 = -0.030`

这说明 survivor follow-up 的出口不是“它已证明能做更快频”；恰恰相反，**唯一诚实 lane 目前被锁定在 15m，而不是 3m/5m**。但这并不妨碍进入 `P2`：因为 `P2` 本来就是对这条 lane 做更系统 admission，而不是要求在 P1 survivor 阶段直接证明全周期泛化。

## 出口判断
本轮按 policy 必须把 survivor 收口，不得再拖第二次 follow-up。出口判断如下：

- **不是 `background/P0`**：因为已经找到至少一条清楚的、可迁移的、经过成本梯度后仍保留正净边的 lane。
- **也还不是 `P3`**：当前只证明了 survivor 级别的单 lane 生存，不足以直接进入 paper launch。
- **因此应升级为 `promote_P2`**：把对象切换到 `Active P2 slot`，后续 admission 应围绕这条已经锁定的 lane，继续补齐 time stability / parameter stability / cross-pair stability / execution realism，而不是再回到“这 repo 壳子完整不完整”的 first-verdict 叙事。

## 对 runtime 的直接影响
- `Surviving candidate slot`：`Rank 322` 用完唯一一次 follow-up，槽位释放为 `none`。
- `Active P2 slot`：由 `Rank 322` 占据。
- `p2_rounds_since_level_change`：重置为 `0`。
- `p2_consecutive_keep_p2`：重置为 `0`。
- `p2_last_evidence_axis`：更新为 `survivor_followup_pair_admission_cost_horizon`。

## 给下一轮 admission 的最窄主线
下一轮不该再问“这是不是一个像样的 pairs raw alpha”；这个问题已经回答完了。下一轮应只围绕：
1. `BTC-XRP / SOL-XRP` 这类 surviving lane 在更长样本上是否仍保留正净边；
2. rolling hedge ratio / rolling corr / half-life admission 是否能稳定缩小假 pair；
3. 15m lane 的参数扰动是否稳健，而不是一组阈值偶然幸存；
4. 进入更真实 execution 假设后，是否仍值得朝 `P3 / paper trade` 继续推进。
