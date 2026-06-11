# Rank 296 survivor exit：不升 P2，预算用尽后回 background/P0

- 时间：2026-04-02 20:40 UTC
- 对象：Rank 296 / BTC next-day CIDR curve timing
- 轮次角色：bot3 survivor follow-up（唯一一次 follow-up 收口）
- 依据：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`、`research/quant_digests/2026-04-02_1929_cidr-intraday-curve-timing-alpha.md`

## 本轮要回答的问题
作为当前唯一合法的 survivor follow-up，这条 `predict-next-day intraday curve × buy forecasted low / sell post-low high` 是否已经足够从 `keep_P1` 升到 `P2`，还是应在 survivor 预算用尽后回 background/P0。

## 结论
**本轮结论：不升 `P2`；`Rank 296` survivor 预算用尽后回 `background/P0`。**

一句话版本：
> 这条线的主语是清楚的，但当前 desk 可复核证据仍停留在 **BTC 单币、419 天、15m discovery 的薄 gross edge**，且最关键的 `5m/3m execution refine` 还只是“下一步建议”，尚未形成能把 4~8bps 成本问题诚实救回来的 admission 级证据，所以现在更像一个值得保留的研究 lead，而不是该进入 `P2 admission` 的前排候选。

## 为什么这轮不能升 P2
按 policy，`P2` 至少要值得继续做 admission 级验证，而不是靠一句“可能用更好执行能救回来”硬续命。当前材料还差这一步。

### 1) effectiveness / expected return：有 alpha 痕迹，但现口径太薄
摘要里的最小 portability probe 是：
- Binance BTCUSDT perp
- 2025-02-07 ~ 2026-04-01
- 419 个完整 UTC 日
- 182 天训练窗
- 15m CIDR curve + PCA + serial-correlation gate

结果：
- 全样本：平均单日约 `+3.90bps`，Sharpe `0.65`
- gated 样本：平均单日约 `+8.30bps`，Sharpe `1.21`

这说明 **base alpha 没被立即证伪**，但强度明显不够厚，尤其全样本版本已经非常接近“成本一碰就没”。

### 2) honesty / execution realism：当前最关键的 blocker 就在这里
同一份 digest 自己已经把最关键问题写得很清楚：
- 全样本版本 `4bps` round-trip 后 Sharpe 已接近 `-0.02`
- gated 版本：`4bps` 还有 `0.63`，但 `8bps` 已接近 `0.04`

这代表当前真正成立的口径不是“已证明能交易”，而是：
> **也许在低成本、低频、并且靠更细 execution refine 的条件下还能活。**

问题在于：
- 这轮 survivor follow-up 并没有带来新的 `5m/3m execution refine` 实证；
- 也还没有 reader-facing artifact 证明 `15m discovery + 5m/3m execution` 真能把 post-cost 生命力从“薄 edge”抬到 admission 级；
- 因此当前不能把“尚未验证的执行补救”当成升 `P2` 的已得证据。

### 3) cross-asset stability：目前仍是 BTC 单币故事
这条线当前只有 BTC 单资产版本，且 digest 自己明确写了：
- 不能自动外推到 ETH/SOL；
- 不建议先扩成多币篮子。

这不一定致命，但意味着它现在更像 **单一研究 lead**，不是已准备进入 admission 阶段的较成熟候选。

### 4) time stability：只有近一年多可移植样本，还不足以支撑 admission 前移
当前 public-data probe 只有约 14 个月左右的 Binance perp 样本，论文原始样本也已提示 2017 后存在衰减。换句话说：
- 这条线不是长期稳厚的 time-of-day pocket；
- 而是“路径预测在某些 regime 还活着”。

这种结论适合保留为研究方向，但还不适合在没有更强执行证据前推进到 `P2`。

### 5) parameter stability：gated vs ungated 差异很大，说明它高度依赖 gate
当前最能看的版本依赖 serial-correlation gate；全样本硬做明显变差。说明：
- 不是“壳子一搭就稳”；
- 而是 **对 gate 触发和成本条件都非常敏感**。

这再次支持：它应被视为一个有趣但仍脆弱的路径预测 lead，而不是已经够格进 `P2 admission` 的对象。

## 这轮真正改变系统认知的地方
改变系统认知的话应当写成：

> `Rank 296` 不再作为前排 survivor 继续占资源：它目前最诚实的位置是 `background/P0` 中的“保留研究 lead”，因为现有证据只说明 BTC 次日日内曲线预测有薄弱 gated timing 痕迹，还没证明 `15m discovery + 5m/3m execution` 能把 post-cost 生命力抬到 admission 级。

## runtime 动作
- `Surviving candidate slot`：清空，不再保留 `Rank 296`
- `Background pool`：记录 `Rank 296` 本轮 survivor follow-up 已收口，预算用尽后回 background/P0
- `cycle_plan[1]`：标记 `done`

## 后续口径（仅记录，不作为本轮续做）
如果未来 human 明确 reopen，这条线最值得补的不是再写 functional 术语，而是直接补一份 reader-facing clean-room 实验：
1. `15m discovery + 5m execution refine`
2. 明确 `2 / 4 / 6 / 8 bps` 成本后表现
3. 验证它更适合做独立 timing trade，还是做 BTC directional gate

但在当前 policy 下，这些都属于将来可能的 reopen 方向，不构成这轮继续留在 survivor/P2 的理由。
