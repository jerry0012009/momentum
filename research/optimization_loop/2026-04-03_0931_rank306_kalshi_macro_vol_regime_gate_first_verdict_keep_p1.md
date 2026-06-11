# Rank 306 — Kalshi macro vol regime gate first verdict = keep_P1

- Time: 2026-04-03 09:31 UTC
- Target: `research/quant_digests/2026-04-03_0228_kalshi-macro-vol-regime-gate.md`
- Object: `Fed / CPI repricing × shared volatility regime gate`
- Verdict: `keep_P1`
- Rank: `306`

## Why this changes system belief

这条线**不是独立 raw alpha**，但已经足够明确地构成一个可单独 desk 化的 `shared regime / sizing / routing layer`，不应被直接打回 `background/P0`。

关键原因有三点：

1. **asset-channel mapping 已经具体**
   - BTC 侧主通道是 `Fed / recession repricing -> higher future vol state`
   - ETH / SOL / ADA / LINK 侧主通道是 `CPI repricing spike -> lower future vol state`
   - 这不是泛泛的“宏观解释”，而是可直接翻译成不同资产的 daily state map。

2. **daily gate 更新口径已经清楚**
   - 数据源是公开 Kalshi 合约行情 + 公开 crypto K 线
   - 论文锚点和 note 里都已把第一版实现收敛到 `16:00 ET` 的固定 daily snapshot
   - 可先用最笨的 `allow / neutral / veto` 或 `off / half-size / full-size` 三档状态启动，不需要先做复杂连续加权。

3. **它已明确能服务至少两类 sleeve，而不是单一解释材料**
   - breakout / continuation：高波动 state 放行或加大 size，低波动 state veto / half-size
   - mean reversion / stat-arb：高波动 state 下收缩、低波动 state 下 allow / size-up
   - carry / funding：高波动 state 可直接做 gross-down / leverage-down

## Why not P2 yet

还不够直接进 `P2`，因为当前只有论文证据和 clean translation，还没有把它挂到具体底层 sleeve 上做最小 A/B admission。

最小缺口不是“再解释一遍论文”，而是把它接到至少一个具体实验壳：

1. `BTC 15m breakout / continuation × recession-risk high-vol gate`
2. `ETH/SOL 15m breakout × CPI low-vol veto`
3. `ETH/SOL MR / stat-arb × low-vol allow`

在这些 A/B 还没跑之前，最诚实的位置是 `keep_P1`，而不是 `P2`。

## Conclusion

`Rank 306`：`Fed / CPI repricing × shared volatility regime gate` 已具备清楚的 asset-channel mapping、daily gate 更新口径，以及同时服务 breakout 与 MR/stat-arb/carry 的最小实验壳，因此 first verdict = `keep_P1`；它不是新的逐根 raw alpha，但也不是只能停留在宏观解释层的材料。

## Ops note

本轮已尝试执行首页刷新脚本 `scripts/publish_homepage_index.sh`，但脚本中的 `sudo install/chown /var/www/momentum-report/index.html` 在当前 cron 运行环境下无法完成，导致公开首页尚未同步；研究日志与 runtime state 已完成写回。
