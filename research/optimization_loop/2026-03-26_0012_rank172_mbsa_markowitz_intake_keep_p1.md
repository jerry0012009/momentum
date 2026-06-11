# Rank 172 / MBSA Markowitz basket raw alpha — fresh intake首判

- 时间：2026-03-26 00:12 UTC
- 执行角色：bot3
- 依据：`docs/BOT2_BOT3_POLICY.md` + `docs/BOT2_BOT3_STATE.md`
- 本轮执行小点：`cycle_plan` 中首个合法 pending 项 —— 对 `research/quant_digests/2026-03-25_2253_mbsa-markowitz-basket-raw-alpha.md` 做 fresh intake 最小首判

## 为什么本轮不是执行前一条 pending 的 Active P2 admission
`cycle_plan` 第 2 项显式带条件：只有当 `Rank 171 / volume-ranked theme leader-follower spread` 经 survivor/P2 路径升入 `P2` 时才成立。但 runtime truth 已明确 `Rank 171` 完成 survivor 唯一 follow-up 后未升 `P2`，并已回到 background pool，因此该项本轮不是合法主动作；按 policy 顺延到下一条合法 fresh intake。

## 读后结论
结论给 `keep_P1`，并分配正式 `Rank 172`。

这条线当前值得保留的 deployable 核心，不是把论文误读成“组合层 cosmetics”或单纯 equal-weight 优化，而是：**先用 moving-band spread / residual mean-reversion 作为 raw alpha，再把同时活跃的多条 stat-arb 通过 cost-aware / risk-aware 的 top-N Markowitz 篮子做统一 admission、配资与退场管理。**

## 为什么不是直接 park
1. digest 已经把论文翻译成明确 desk 对象：alpha 仍来自 `spread 相对 rolling midpoint 的回归`，不是抽象组合理论；这保证它属于 raw alpha 骨架，而不是只会美化回测的 overlay。
2. 本地最小快检显示“篮子管理层”确有增益：在 Binance `15m` proxy 上，Markowitz-smoothed top-2 相比 naive equal-weight 在无成本与 `2 bps` 下都更稳，说明这不是空洞的配权修饰，而是会改变净边保留情况的真实组合层骨架。
3. 失效边界也足够清楚：`4 bps` 下仍明显过不去，表明当前版本更像 `15m signal generation + 1h/4h rebalance + 5m execution slicing` 的候选框架，而不是可直接按 `15m bar-close taker` 上线的成熟策略；这种“alpha 在、执行还需收紧”的形态，适合进入一次 survivor follow-up，而不是直接丢弃。

## 为什么还不能直接进 P2
当前证据还停留在“论文 + 单次 Binance proxy transfer”层面，尚未完成对真实候选 spread 家族、再平衡节奏、friction ladder 与 admission 五维闭环的诚实检查；尤其尚未证明它在更低换手、更真实执行切片口径下能稳定留下可部署净边。因此它符合 `keep_P1`，但还不够诚实地直接升 `P2`。

## 本轮 verdict
**Rank 172 / MBSA Markowitz basket raw alpha：保持 `P1`。当前可保留的 deployable 核心是“moving-band spread / residual raw alpha 的 top-N cost-aware Markowitz 篮子化骨架”，不是单纯组合层 cosmetics。**
