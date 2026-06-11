# 2026-04-17 14:43 UTC — Rank 419 survivor 唯一 follow-up：short-leg cost decisive check 后执行 one-time P1 re-scope（long-only + BTC vol gate），退出前排

## 执行小点
- cycle_plan 第 1 项：`research/quant_digests/2026-04-17_0439_regimeaware-xsmomentum-btcvol-overlay.md`
- 动作：只围绕 `Rank 419` 的唯一 blocker `short-leg cost` 做最小 decisive 检查；并补 1 个最小 honesty / execution realism 子检查

## 本轮最小证据
直接复核 repo 的 constrained-implementation 输出与成本假设：

1. `long top quintile / short BTC-ETH` 收缩 short-leg 版本并没有转成可接受的绝对表现：
   - full sample absolute Sharpe：`-0.475 -> -0.458`（BTC scaling 后仍为负）
   - post-2020 absolute Sharpe：`-0.259 -> -0.111`（改善但仍为负）
2. repo 同时明确写明：当前短腿实现**尚未显式纳入** `perpetual funding rates / borrow scarcity / margin frictions`。
3. 同一份实现报告里，真正更像可落地方向的是 `long-only top quintile + BTC-vol overlay`：
   - full sample absolute Sharpe：`0.241 -> 0.294`
   - post-2020 absolute Sharpe：`0.447 -> 0.478`
   - dispersion overlay 在 long-only 版本里反而变差。
4. honesty / execution realism 子检查结论：既然 `BTC/ETH-only short leg` 在**未完整计入 funding / borrow / margin friction 前**都仍未转正，那么把 short-leg cost 视为唯一剩余 blocker 已经足够 decisive；继续在同一 short-leg 方向追加 rebalance / turnover 细抠，属于低杠杆重复，不应再占 survivor 预算。

## 结论（改变系统认知）
- `Rank 419` 不适合升 `P2 admission`：当前最小 decisive 检查已经表明，收缩到 `BTC/ETH` 的 short-leg 版本在 repo 自身的 constrained implementation 下仍未形成可复制的正绝对边际，而完整 funding/borrow/margin realism 只会让 short side 更差。
- 但它也不该直接打到 `background/P0`：存在唯一明确 re-scope 方向，且方向足够具体——把对象从 `cross-sectional long-short continuation × BTC vol/dispersion overlay` 收敛为 `long-only top quintile relative-strength continuation + BTC realized vol gate`；其中 `dispersion` 不再作为主 overlay 候选。
- 因此本轮执行：`one-time P1 -> P1 re-scope`，并退出 survivor/front slot；后续仅可按**新 spec** 重新作为 fresh intake 进入，不得沿旧 short-leg 路径自动 reopen。

## 回写动作
- `Fresh intake slot`：清空当前对象（本轮已完成其 first verdict + survivor follow-up 收口）
- `Surviving candidate slot`：清空（唯一 follow-up 预算已用完）
- `Background pool`：新增 `Rank 419` 的 `P1 re-scope (long-only top quintile + BTC vol gate)` 停放记录
- `cycle_plan` 第 1 项：写回 `done`

## 尾部动作
- homepage 刷新：待本轮状态写回后单独尝试
- 邮件通知：待日志落盘后单独发送
