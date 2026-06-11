# Rank 427 / high-volume selloff -> 5m bounce P2 exit promote P3

- 时间：2026-04-19 23:54 UTC
- 对象：`Rank 427 / high-volume selloff -> 5m bounce (ex-ETH core bounce sleeve)`
- 动作：`P2 admission / exit decision`
- 结论：`promote_P3`

## 本轮只回答的 admission 组合
围绕当前已收窄成立的 `ex-ETH core bounce / simple 5m hold12 child-execution sleeve`，只补本轮 policy 允许的最高杠杆组合：
1. `cross-asset + time stability`
2. `最小 execution realism`

目标不是再做开放式 `keep_P2`，而是直接回答它离 `P3 / P1 / P0` 哪个出口最近。

## 使用的最小证据
复用现成 artifact：
- `reports/artifacts/quant_digests/2026-04-19_highvol_selloff_bounce_5m_panel.csv`

口径固定为：
- 仅看 `signal=1`
- 仅看已在 survivor 轮确认过的对象定义：`ex-ETH core bounce sleeve = BTC/SOL/BNB/DOGE`
- 统一按 `8bps` round-trip 成本扣减
- 用 `hold12 / hold24 / hold36` 作为最小参数/退出稳定性近似
- 不再回退到 `strongest-only top1`，因为上一轮已证伪它不是诚实对象定义

## 结果

### 1) cross-asset：不是单一币孤立撑住
`hold12 net8`：
- `SOLUSDT`: `n=29`, `mean≈+9.58bps`, `median≈-0.55bps`
- `DOGEUSDT`: `n=15`, `mean≈+36.98bps`, `median≈+43.64bps`
- `BNBUSDT`: `n=5`, `mean≈+61.85bps`, `median≈+55.15bps`
- `BTCUSDT`: `n=3`, `mean≈+15.73bps`, `median≈+49.59bps`

虽然强度不均，但四个币的 `hold12 mean` 都为正；对象不是只靠某一个 symbol 的单点幻觉存活。

### 2) time stability：历史长度短，但 recent slice 并未塌掉
`hold12 net8` 按月份：
- `2026-03`: `n=2`, `mean≈-10.48bps`
- `2026-04`: `n=50`, `mean≈+24.20bps`, `median≈+19.74bps`

结论：样本明显偏 recent，严格意义上还没有完成长时间稳定性终审；但当前 pocket 的主体样本就来自最近月份，而且 recent slice 明显为正，没有出现“越接近当前越失效”的 fatal pattern。

### 3) parameter / exit stability：短窗成立，拖太久失真
在同一对象定义下：
- `hold12 net8`: `n=52`, `mean≈+22.86bps`, `median≈+15.01bps`
- `hold24 net8`: `n=52`, `mean≈+22.08bps`, `median≈+1.88bps`
- `hold36 net8`: `n=52`, `mean≈-3.69bps`, `median≈-16.16bps`

结论：这条线不是“随便怎么持有都行”的泛 bounce；它明确更像一个 `~1h` 的短窗反弹 sleeve。`hold24` 仍有正均值但中位数明显变薄，`hold36` 已失真转负，因此对象定义应保持 `5m hold12 / short-hold`，而不是拉成长持有壳。

### 4) 最小 execution realism：不要求 top1 极致抢单，top2/全开仍可承接
- survivor 轮已确认：`top1 strongest-only` 在统一 `8bps` 下转负，不是诚实对象定义。
- 本轮补最小可承接性检查：同一时间戳只取 `top2 shock_score` 的事件，仍得到：
  - `top2 hold12 net8`: `n=44`, `mean≈+21.45bps`, `median≈+9.44bps`

这说明对象不需要极端理想化的 “只抓最强那一腿”；保持 `ex-ETH core universe` 内的普通短窗承接/择优执行，就仍有可进入 paper 的 pocket。

## 本轮 verdict
`Rank 427` 已经更接近 `P3 / paper launch queue`，而不是 `P1 re-scope` 或 `background/P0`：
- `cross-asset`：BTC/SOL/BNB/DOGE 四腿都给出正的 `hold12 net8 mean`
- `time`：虽然历史深度不长，但 recent 主体样本显著为正，没有暴露出接近当前即失效的致命模式
- `parameter / execution realism`：edge 明确集中在 `5m hold12` 的短窗 bounce；不依赖已被证伪的 `top1 router`

因此本轮直接执行 `promote_P3`：

> `Rank 427 / high-volume selloff -> 5m bounce` 已通过当前最小 admission，正式升级为 `P3 / Paper launch queue`，对象定义收敛为 **`ex-ETH core bounce / simple 5m hold12 short-hold sleeve`**；后续默认进入 dedicated runner + scheduler + first verified run 的 launch wiring，而不是继续停留在开放式 P2 研究。

## 对 runtime 的影响
- `Paper launch queue.current_target` 切换为 `Rank 427 / high-volume selloff -> 5m bounce (ex-ETH core bounce sleeve)`
- `Paper launch queue.latest_result` 更新为本轮 `promote_P3` verdict
- `Active P2 slot` 清空为 `none`
- `cycle_plan` 第 1 项写回 `done`
