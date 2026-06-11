# Rank 309 — survivor-only follow-up 收口为 background/P0

- Time: 2026-04-03 11:42 UTC
- Target: `Rank 309 / crypto spike reversion × binary wrapper`
- Stage: survivor-only decisive follow-up
- Verdict: `background/P0`
- Source basis: `research/quant_digests/2026-04-03_0948_crypto-spike-reversion-binary-alpha.md` + repo source re-check (`README.md`, `backend/services/strategies/crypto_spike_reversion.py`, `backend/services/strategies/reversion_helpers.py`)

## 这轮真正回答了什么
本轮不是再重复“这条规则壳写得清不清楚”。那个问题在 first verdict 已经回答过了。

这轮唯一要回答的是：

> 这条 `5m impulse overshoot -> short-cycle reversion`，是否已经有足够公开证据证明它在更长样本、至少 `BTC/ETH/SOL/XRP` 分层、且显式 taker/spread/slippage 成本后，仍保留稳定的 post-cost expectancy？

答案是否定的。

## 为什么不能升 P2
### 1) 公开证据仍停留在“规则壳存在”，不是“alpha 已被诚实验证”
repo 源码明确给出了：
- `min_abs_move_5m = 1.8%`
- `|move_5m| >= 0.55 * |move_30m|`
- `|move_2h| <= 14%`
- `8% TP / 4% SL / 8m max hold`
- spike up 反做 `NO`、spike down 反做 `YES`

这些信息足够支持 first verdict 的 `keep_P1`，因为它说明主语清楚、实验壳清楚、不是泛平台叙事。

但它们**不等于**更长样本的 after-cost 有效性证据。

### 2) 成本口径仍然过粗，不能当 admission 级证据
源码里对成本的处理仍是：
- `net_edge_percent = max(0.0, edge - 0.25)`

这只是一个粗 fee/slippage deduction，不是：
- taker fee
- spread
- slippage
- 按流动性层分组后的 fill realism
- 不同标的/不同波动状态下的实际成交约束

因此它最多说明作者“承认成本存在”，但还不足以证明策略在成本后真实可行。

### 3) 没有看到 survivor 这一轮要求的关键稳健性证据
当前公开材料里，没有给出：
- 更长样本的汇总表现
- `BTC/ETH/SOL/XRP` 分层后的结果
- 多档成本情景下的 after-cost expectancy
- 证明 edge 不是 prediction-market 容器特有 quote/settlement pocket 的迁移证据

README 主要在讲平台能力与策略目录，并没有给这条策略的历史表现页或分资产统计。
`crypto_spike_reversion.py` 与 `reversion_helpers.py` 也主要是信号筛选/执行壳，不是实证结果。

## 系统认知改变
`Rank 309` 现在的真实状态应当被表述为：

> 它是一条**规则壳清楚、值得 intake 但尚未被公开证据诚实验证的 short-cycle shock-fade raw alpha skeleton**；当前不足以进入 `P2`，因此 survivor-only follow-up 的出口应直接收口为 `background/P0`。

## 为什么不是 keep_P1 / 继续拖
policy 对 survivor 很明确：
- `Surviving candidate` 只能是上一条 fresh intake
- 最多只允许 **1 次** 最小 decisive follow-up
- 这 1 次之后若仍未升级到 `P2`，默认移入 `Background pool`

本轮已经用掉这唯一一次 follow-up，且没有得到足以升级 `P2` 的新证据，所以不能继续开放式停留在前排。

## Final verdict
`Rank 309` 的 survivor-only follow-up 结论是：当前公开证据只证明规则壳存在，未证明其在更长样本、多资产分层与显式 taker/spread/slippage 成本后仍保留稳定的 after-cost expectancy；因此不升 `P2`，直接回到 `background/P0`。
