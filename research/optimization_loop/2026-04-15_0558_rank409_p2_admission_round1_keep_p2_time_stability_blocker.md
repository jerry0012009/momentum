# Rank 409 P2 admission（出口倾向判定轮-1）— keep_P2（唯一剩余 blocker：time-stability）

- 时间：2026-04-15 05:58 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：#1 `Rank 409 / BTC-beta-neutral residual momentum ranking shell（re-scoped to residual sign-fade @1h->24h hold）`

## 本轮执行
1. 对 `1h residual sign-fade` 做 P2 admission 最小闭环，覆盖：
   - effectiveness（费后 net bps / sharpe）
   - cross-asset stability（`BTC` vs `BTC+ETH` market proxy）
   - time stability（test 前后半段拆分）
   - parameter stability（hold `16/24/32h` + cost `4/6/8 bps`）
2. 按要求补 1 项最小 execution realism 检查：
   - canonical `24h hold` 下把执行延迟从 `t+1` 提到 `t+2`；
   - 并把成本上推到 `10/12 bps`，核验 pocket 是否被压回零线。

## 关键工件
- `research/optimization_loop/artifact_rank409_p2_admission_1h_residual_signfade_20260415.csv`
- `research/optimization_loop/artifact_rank409_p2_admission_1h_residual_signfade_20260415.json`

## 关键结果
样本（本轮重跑）：`2026-03-23 03:00 UTC ~ 2026-04-15 05:00 UTC`，test bars=`555`。

### 1) effectiveness + parameter（16/24/32h, 4/6/8bps）
- `BTC proxy`：`24h` 在 `4/6/8bps` 均为正（约 `+0.325 / +0.240 / +0.154 bps/bar`）；`32h` 更高。
- `BTC+ETH proxy`：`24h` 在 `4/6bps` 小幅为正（约 `+0.165 / +0.079 bps/bar`），`8bps` 已接近零线（`-0.006 bps/bar`）。

### 2) cross-asset
- 同一参数下两种 proxy 方向不一致：`BTC` 更稳，`BTC+ETH` 在较高成本下边际消失，跨代理稳健性不足。

### 3) time stability（决定性）
- `24h, 6bps`：
  - `BTC proxy` 前半段 `+0.074`、后半段 `+0.405 bps/bar`（后半显著主导）；
  - `BTC+ETH proxy` 前半段 `-0.223`、后半段 `+0.382 bps/bar`（明显前负后正翻转）。
- 结论：当前费后 pocket 对时间切片高度敏感，尚未形成 admission 出口所需的时段稳定性。

### 4) honesty / execution realism（最小补检）
- `BTC proxy, 24h`：延迟到 `t+2` 后在 `8bps` 起已转负（`-0.063 bps/bar`），对执行延迟敏感。
- `BTC+ETH proxy, 24h`：`t+2` 下仍为正，但同样存在前半段偏弱/为负问题。
- 未见 lookahead / leakage 级别致命违规，但 execution 鲁棒性不足以支持本轮直接 `promote_P3`。

## 结论（改变系统认知）
`Rank 409` 在 `residual sign-fade @1h->24h` 上仍有费后正 pocket，但 **time-stability（前后半段翻转）是当前唯一剩余 decisive blocker**；因此本轮收口为 **`keep_P2`（非开放式拖延）**，下一轮必须围绕“单一时段稳健化 re-scope（如 session/regime gating）或直接退出决策”完成出口判断。
