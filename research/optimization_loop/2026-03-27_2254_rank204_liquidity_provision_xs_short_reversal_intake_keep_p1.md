# Rank 204 / liquidity-provision cross-sectional short-reversal intake keep_P1

- 时间：2026-03-27 22:54 UTC
- 对象：`research/quant_digests/2026-03-27_1532_liquidity-provision-xs-short-reversal-alpha.md`
- 动作：fresh intake 首轮 verdict
- 结论：`Rank 204 / liquidity-provision cross-sectional short-reversal` 首轮 intake 完成，正式记 `keep_P1`，进入 survivor 做一次且仅一次便宜 follow-up。

## 为什么这轮不是 `drop`
这条线保留下来的不是“流动性解释文”本身，而是一个可以独立部署、也能继续 desk 化的 raw alpha skeleton：

- 信号本体很清楚：`上一根横截面 relative winner/loser -> 下一根做反向提供流动性`
- 交易结构也很清楚：`long losers / short winners` 的横截面 market-neutral 组合
- 持有周期天然贴当前桌面：`5m -> next 5m` 可往 `15m` desk 化迁移
- 公共 transfer sanity check 已给出还活着的证据：
  - `5m` gross 约 `+1.84 bps/bar`，但 turnover 太高，按 `1 bp/turnover` 扣后转负
  - `15m` gross 约 `+3.83 bps/bar`，turnover 没明显更高，成本后仍约 `+0.94 bps/bar`

换成人话：它不是“只有故事没有交易骨架”的候选，也不是已经被公共数据直接打死的旧逻辑。至少在当前 public Binance spot 最小快检里，**raw alpha 本体还在，问题主要是 5m execution / turnover 太贵，而不是 edge 已经消失。**

## 为什么这轮不直接升 `P2`
还不能直接升 `P2`，因为当前证据只够回答“这是一条值得继续的母策略”，还不够回答“它已经接近 paper trade admission”。

当前缺的不是更多论文解释，而是更贴交易层的唯一 decisive follow-up：

1. `15m` 版本的正 net 是不是只靠这 30 天 pocket；
2. turnover control（`top/bottom quantile`、`entry threshold`、`staggered rebalance`）能不能把这条线从“有 gross、5m 太贵”推进到“成本后更稳”；
3. 它是否保留为一条可迁移的 basket short-reversal 母线，而不是只在 spot top-25 的局部窗口里偶然成立。

所以当前最诚实的首轮 verdict 不是 `promote_P2`，而是：

> **保留这条 `XS short reversal = liquidity provision premium` 母线，但只给它 1 次 survivor follow-up，集中回答“如何把去冲击回归的 raw alpha 变成成本后更可活的 desk 版本”。**

## 当前 runtime 含义
- 正式分配 `Rank 204`
- fresh intake 本轮完成，结果为 `keep_P1`
- survivor 锁定到 `Rank 204`
- 唯一 follow-up 默认应围绕：
  - `15m` cost-aware 版本是否仍稳
  - `top/bottom quantile` / `entry threshold` / `rebalance every 2 bars` 这三类降换手手段里，哪一个最可能把母策略推进到 `P2`
- 在这一步回答前，不升 `P2`

## 一句话结果
**`Rank 204 / liquidity-provision cross-sectional short-reversal` 当前保留下来的是“横截面短反转 = 做流动性 premium”的可独立交易母线；public 数据已证明 15m 版本比 5m 更接近可成本化，因此首轮应记 `keep_P1`，再用 survivor 唯一预算只回答降换手后它能否升 `P2`。**
