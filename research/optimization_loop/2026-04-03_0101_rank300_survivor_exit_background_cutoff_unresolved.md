# Rank 300 / liquidity-split lagged-return sign-flip alpha — survivor exit = background/P0

- Time: 2026-04-03 01:01 UTC
- Target: `Rank 300 / 24h lagged-return × liquidity-split sign flip alpha`
- Slot: Surviving candidate
- Verdict: `background/P0`

## Why this changes system belief

`Rank 300` 的 survivor follow-up 已经把仅剩的两个 blocker 直接收口：

1. **formation / holding pocket**：在现有公开数据 clean-room 里，high-liquidity `winner-follow` 的确不是完全没生命迹象；`15m` 版本里 `24h formation -> 4h hold` 的 intraday pocket 明显强于 `1h hold`，说明这条 family 更像慢一点的 liquid continuation，而不是立刻失效。
2. **liquidity cutoff**：但到目前为止，证据还没有把“究竟从哪一层 liquidity 开始应该翻成 winner-follow”收成一个可 desk 迁移的单一 cutoff。已有 daily split 证据里，`mom_highliq` 仍未形成足够干净、稳定、能直接写进 governance 的 cutoff 结论；也就是说，我们知道 broad liquid-perp desk 不该再按 loser-bounce 理解它，但还不知道 admission 时应该用哪条明确 bucket 边界来稳定地拿这条 continuation sleeve。

## Evidence used this round

### A. Cutoff axis：还没收成单一可迁移边界

来自 `reports/artifacts/quant_digests/liquidity_regime_daily_reversal_momentum_20260331.csv` 的汇总：

- `ls_all`: mean `-0.267%/day`, annualized Sharpe `-1.69`, cumulative `-52.8%`
- `ls_lowliq`: mean `-0.301%/day`, annualized Sharpe `-1.48`, cumulative `-58.8%`
- `mom_highliq`: mean `-0.050%/day`, annualized Sharpe `-0.22`, cumulative `-25.9%`

这组结果足够说明一件事：**“全市场 yesterday losers 反弹”在当前可交易样本里不是可 admission 主线**。但它也同时说明，现有 high-liquidity 分层证据还**没有**收成一个 reader-facing 的“从这里开始翻正、且能稳定写成 desk bucket rule”的 cutoff 结论。

### B. Holding-pocket axis：4h 明显优于 1h，但还不足以替代 cutoff 治理

来自 `reports/artifacts/quant_digests/liquidity_conditioned_intraday_momentum_15m_20260331.csv` 的汇总：

- `mom1h`: mean `+0.010%/bar`, annualized Sharpe `1.89`, cumulative `+4.6%`
- `mom4h`: mean `+0.116%/bar`, annualized Sharpe `11.47`, cumulative `+138.3%`

因此 survivor follow-up 的新增认知是：

> 对当前 liquid continuation 口袋，**真正活着的是 `24h formation -> 4h hold`，而不是之前更模糊的“也许 1h 就够”**。

但按当前 policy，survivor 只能做 **1 次** decisive follow-up。这个 follow-up 的任务不是继续开新 admission，而是回答：

> 现有 evidence 能不能已经把它收成可 admission 的 `P2`？

答案仍然是否定的，因为 **holding pocket 已收口，cutoff 还没收口**；而 cutoff 正是这条 sign-flip family 能否 desk 化的核心治理轴。

## Exit decision

因此本轮不做 `promote_P2`。

`Rank 300` 的最诚实结论是：

> 它成功证明了 `lagged-return` 在 liquid perp desk 上更该被理解成 **slow liquid continuation family**，并把最佳 pocket 收到 `24h formation -> 4h hold`；但现有证据仍不足以把 high-liquidity 边界写成可 admission 的单一 cutoff rule，所以 survivor budget 用尽后应退回 `background/P0`，而不是带着半收口治理继续占用前排槽位。

## Runtime action taken

- `Rank 300` 从 `Surviving candidate slot` 移出
- survivor follow-up budget 视为用尽，本轮收口为 `background/P0`
- 释放唯一 survivor 槽位
- 因造成前排对象切换，`Fresh intake slot` 的前置阻塞解除；`BB/z-score overshoot × RSI confirm × trend-veto` 重新回到下一合法 fresh intake 头位
