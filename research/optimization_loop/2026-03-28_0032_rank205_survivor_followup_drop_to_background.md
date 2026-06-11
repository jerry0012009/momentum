# Rank 205 / par-local-drift crossover survivor follow-up → drop_to_background

- Time: 2026-03-28 00:32 UTC
- Target: `Rank 205 / par-local-drift crossover`
- Action type: survivor follow-up (唯一预算)
- Verdict: `drop_to_background`
- Artifact: `reports/artifacts/optimization_loop/rank205_survivor_followup_20260328/summary.csv`

## 本轮要回答的问题
这条 `rolling local drift / prediction line + buffered crossover + opposite flip` 单币方向性母线，放到与简单 trend baseline 相同的窗长、相同成本、相同 BTC/ETH 主币框架里后，是否还能证明自己提供了新增 alpha；如果不能，就必须在 survivor 预算用尽后诚实收口。

## 实验设置
- 标的：`BTCUSDT`、`ETHUSDT`
- 周期：`1m` 与 `5m`
- 样本：本地现成 `90d` perp cache
- 统一成本：`8 bps/side`
- 统一主窗长：
  - `1m`: `61 bars`（约 61 分钟）
  - `5m`: `12 bars`（约 60 分钟）
- local-drift 实现：rolling 二次多项式拟合出的 local prediction line，`±15 bps` buffer，反向信号翻仓
- 对照 baseline：
  1. `EMA crossover`
  2. `Donchian breakout`
  3. `N-bar sign continuation`
- 统一回测口径：信号 `shift(1)`，按仓位变化扣成本，比较成本后 total return / sharpe / max drawdown / trades / avg hold bars / whipsaw rate

## 关键结果
### 1m
- `BTCUSDT`
  - Donchian：`-89.2%`，`1175` 笔，平均持有 `110.3` bars，whipsaw rate `0.09%`
  - Local drift：`-99.2%`，`3224` 笔，平均持有 `40.2` bars，whipsaw rate `1.58%`
- `ETHUSDT`
  - Donchian：`-80.2%`，`1093` 笔，平均持有 `118.5` bars，whipsaw rate `0.18%`
  - Local drift：`-99.9%`，`4261` 笔，平均持有 `30.4` bars，whipsaw rate `3.54%`

### 5m
- `BTCUSDT`
  - Donchian：`-81.5%`，`951` 笔，平均持有 `27.2` bars，whipsaw rate `1.68%`
  - Local drift：`-90.8%`，`1430` 笔，平均持有 `18.1` bars，whipsaw rate `18.11%`
- `ETHUSDT`
  - Donchian：`-78.3%`，`881` 笔，平均持有 `29.4` bars，whipsaw rate `1.36%`
  - Local drift：`-97.2%`，`2182` 笔，平均持有 `11.8` bars，whipsaw rate `20.12%`

## 结论
本轮结论很明确：**Rank 205 没有证明自己比简单 trend baseline 更有新增 alpha。**

更具体地说：
1. 在 `BTC/ETH` 的 `1m` 与 `5m` 四个切片里，`local-drift crossover` 全部落后于简单 `Donchian breakout`；
2. 它的主要特征不是更稳，而是**更高换手、更短持有、更高 whipsaw**；
3. 连 baseline 本身在这组苛刻成本下都偏弱，而 local-drift 又比 baseline 更差，因此当前最诚实的判断不是升 `P2`，而是承认这条线暂时只是一种更复杂的趋势换壳，没有在 desk 当前框架下证明出额外信息含量。

## 改变系统认知的一句话
**Rank 205：survivor 唯一 follow-up 显示它在 BTC/ETH 的 1m 与 5m、统一约 60 分钟窗长与 8 bps/side 成本下都明显落后于简单 Donchian breakout，local-drift 只是更高换手的复杂换壳，未证明新增 alpha，因此预算归零后直接移入 Background pool。**

## Runtime writeback
- `Surviving candidate slot` → `none`
- `followup_budget_remaining` → `0`
- `Rank 205` → `Background pool`

## 备注
- 这一步已经完成 survivor 的唯一允许检查；后续若要重开，必须是用户明确要求或出现新的、更强实现路径，而不是自动继续给这条线续命。
